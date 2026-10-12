#!/usr/bin/env python3
"""Matched 50--60 us M247 restart: PCG versus standard OpenFOAM GAMG."""
import argparse
import json
from pathlib import Path
import re
import shutil
import tarfile
import time

from collect_probe import read_probe, parse_records
from collect_thermal_validation import final_state, residual_gate
from prepare_probe import checkpoint, snapshot_digest
from track1500_pilot import pool_geometry
from wang_ray_suite import run, setting, save, digest

START=50e-6
END=60e-6
SAMPLES=(55e-6,60e-6)
VARIANTS=('pressurePCG','pressureGAMG')
GAMG='''{
    solver GAMG;
    tolerance 1e-7;
    relTol 0.05;
    smoother GaussSeidel;
    cacheAgglomeration true;
    agglomerator faceAreaPair;
    nCellsInCoarsestLevel 10;
    mergeLevels 1;
}'''

def pressure_stats(text, steps):
    rows=[(float(a),float(b),int(c)) for a,b,c in re.findall(
        r'Solving for p_rgh, Initial residual = ([-+0-9.eE]+), Final residual = ([-+0-9.eE]+), No Iterations (\d+)',text)]
    if len(rows)!=3*steps:raise ValueError('Expected three pressure solves per step')
    solver_names=sorted(set(re.findall(r'(\w+):\s+Solving for p_rgh,',text)))
    passed=all(final<=max(1e-7,initial*.05 if i%3!=2 else 0)*(1+1e-8) and n<1000
               for i,(initial,final,n) in enumerate(rows))
    continuity=[tuple(map(float,m)) for m in re.findall(
        r'sum local = ([-+0-9.eE]+), global = ([-+0-9.eE]+), cumulative = ([-+0-9.eE]+)',text)]
    # OpenFOAM prints one zero continuity line while initialising phi, before
    # the first pressure solve. Reject any other mismatch rather than assuming
    # every continuity line belongs to a p_rgh solve.
    if len(continuity)==len(rows)+1 and continuity[0]==(0.0,0.0,0.0):
        continuity=continuity[1:]
    if len(continuity)!=len(rows):raise ValueError('Missing continuity records')
    # Reject nonfinite values even if not represented by the numeric regex.
    if re.search(r'\b(?:nan|inf)\b',text,re.I):raise ValueError('Nonfinite solver output')
    temperatures=[(float(b),int(c)) for a,b,c in re.findall(
        r'Solving for T, Initial residual = ([-+0-9.eE]+), Final residual = ([-+0-9.eE]+), No Iterations (\d+)',text)]
    return dict(passed=passed,solver_names=solver_names,calls=len(rows),mean_iterations=sum(r[2] for r in rows)/len(rows),
        max_iterations=max(r[2] for r in rows),final_pressure_max_residual=max(r[1] for r in rows[2::3]),
        temperature_linear_calls=len(temperatures),
        temperature_linear_gate=bool(temperatures) and all(r<=1e-9*(1+1e-8) and n<1000 for r,n in temperatures),
        temperature_linear_max_iterations=max((n for r,n in temperatures),default=None),
        continuity_max_local=max(abs(r[0]) for r in continuity),
        continuity_max_abs_global=max(abs(r[1]) for r in continuity),
        continuity_final_cumulative=continuity[-1][2])

def geometry_difference(reference,candidate):
    result={}
    for name in ('depth_from_original_surface_um','width_z_um'):
        a,b=[g['solidus_connected_pool'][name] if g['solidus_connected_pool'] else 0 for g in (reference,candidate)]
        result[name]=dict(reference=a,candidate=b,relative_difference=abs(b-a)/a if a>0 else None)
    result['passed']=all(r['relative_difference'] is not None and r['relative_difference']<=.05 for r in result.values())
    return result

def prepare(source,case,variant,source_hash):
    if case.exists():raise ValueError('Never overwrite an existing case')
    case.mkdir()
    for name in ('constant','system'):shutil.copytree(source/name,case/name)
    for i in range(48):
        rank=source/f'processor{i}';dst=case/rank.name;dst.mkdir()
        shutil.copytree(rank/'constant',dst/'constant')
        state=checkpoint(rank,START);shutil.copytree(state,dst/state.name)
    # Hash original copied state BEFORE changing controls, guaranteeing matched inputs.
    copied=snapshot_digest(case)
    for key,value in dict(startFrom='startTime',startTime='50e-6',endTime='60e-6',stopAt='endTime',
        writeControl='adjustableRunTime',writeInterval='5e-6',purgeWrite=0,writeFormat='binary',writeCompression='off').items():
        setting(case,'system/controlDict',key,value)
    if variant=='pressureGAMG':
        setting(case,'system/fvSolution','solvers/p_rgh',GAMG)
        # Write final block explicitly: dictionary tools may expand $p_rgh
        # while reading. Never leave a hidden PCG final solve in this variant.
        setting(case,'system/fvSolution','solvers/p_rghFinal',GAMG.replace('relTol 0.05;','relTol 0;'))
    # p_rghFinal retains relTol=0. No changes to correction count,
    # pressure tolerance, time-step controls, thermal iteration or ray sampling.
    save(case/'probe.json',dict(schema=1,source=str(source),source_snapshot_sha256=copied,
        pilot_report_sha256=source_hash,checkpoint=checkpoint(source/'processor0',START).name,
        variant=variant,start_s=START,end_s=END,duration_us=10,ranks=48,
        epsilon_tolerance=1e-4,phase_temperature_tolerance_K=.01))

def validate_source(source):
    if not re.search(r'^End\s*$',(source/'log.vacuumLaserbeamFoam').read_text(errors='replace'),re.M):
        raise ValueError('Pilot must have completed')
    meta,summary,_=read_probe(source)
    if meta['ranks']!=48 or abs(meta['end_s']-START)>1e-12 or not residual_gate(source,meta,summary['steps']):
        raise ValueError('Requires completed, thermally converged 48-rank 50us pilot')
    if summary['thermal_limit_hits']:raise ValueError('Pilot thermal cap hits')
    ranks=sorted(p.name for p in source.glob('processor*') if p.is_dir())
    if set(ranks)!={f'processor{i}' for i in range(48)}:raise ValueError('Require original uncollated 48-rank partition')
    for i in range(48):
        rank=source/f'processor{i}';state=checkpoint(rank,START)
        if not (rank/'constant/polyMesh').is_dir():raise ValueError('Static processor mesh missing')
        for name in ('alpha.metal','T','U','p_rgh','epsilon1'):
            if not (state/name).exists() and not (state/(name+'.gz')).exists():raise ValueError('Restart field missing: '+str(state/name))
    if (source/'constant/dynamicMeshDict').exists():raise ValueError('Static mesh only')
    # Read through official foamDictionary; reject accidental variants or relaxed
    # controls rather than overwriting them silently.
    import subprocess
    expected=[('constant/LaserProperties','nRadial','16'),('constant/LaserProperties','nAngular','24'),
        ('constant/LaserProperties','staggeredAngularSampling','false'),
        ('system/fvSolution','solvers/p_rgh/solver','PCG'),('system/fvSolution','solvers/p_rgh/tolerance','1e-7'),
        ('system/fvSolution','solvers/p_rgh/relTol','.05'),('system/fvSolution','solvers/p_rghFinal/relTol','0'),
        ('system/fvSolution','PIMPLE/nCorrectors','3'),('system/fvSolution','MELTING/epsilonRelaxation','1'),
        ('system/fvSolution','PIMPLE/nOuterCorrectors','1'),('system/fvSolution','PIMPLE/nNonOrthogonalCorrectors','0'),
        ('system/fvSolution','MELTING/epsilonTolerance','1e-4'),('system/fvSolution','MELTING/phaseTemperatureTolerance','.01')]
    for dictionary,key,value in expected:
        actual=subprocess.check_output(['foamDictionary',str(source/dictionary),'-entry',key,'-value'],text=True).strip()
        try:equal=float(actual)==float(value)
        except ValueError:equal=actual==value
        if not equal:raise ValueError(f'Source setting mismatch: {key}={actual}, expected {value}')

def collect(work):
    results={};metadata={}
    for variant in VARIANTS:
        case=work/variant;meta,summary,diag=read_probe(case);metadata[variant]=meta
        thermal=summary['thermal_limit_hits']==0 and residual_gate(case,meta,summary['steps'])
        text=(case/'log.vacuumLaserbeamFoam').read_text(errors='replace')
        pressure=pressure_stats(text,summary['steps'])
        expected_solver='DICPCG' if variant=='pressurePCG' else 'GAMG'
        if pressure['solver_names']!=[expected_solver]:raise ValueError('Pressure method did not match variant: '+variant)
        geometries=json.loads((case/'geometrySamples.json').read_text())
        if set(geometries)!={f'{t:.12g}' for t in SAMPLES}:raise ValueError('Missing exact-time geometry samples')
        fine=all(g['molten_metal_cells_outside_fine']==0 and g['solidus_connected_pool'] is not None
            and g['solidus_all_metal']['fine_margin_um']>=12 for g in geometries.values())
        results[variant]=dict(summary=summary,thermal_gate=thermal,pressure=pressure,fine_grid_gate=fine,
            geometry=geometries,diagnostics=diag,binary=json.loads((case/'run.json').read_text()))
    a,b=[metadata[v] for v in VARIANTS]
    for key in ('source','source_snapshot_sha256','checkpoint','start_s','end_s','ranks'):
        if a[key]!=b[key]:raise ValueError('Unmatched restart: '+key)
    ref,can=[results[v] for v in VARIANTS]
    for key in ('solver_sha256','laser_library_sha256'):
        if not ref['binary'].get(key) or ref['binary'][key]!=can['binary'].get(key):raise ValueError('Binary provenance differs')
    geometry={key:geometry_difference(ref['geometry'][key],can['geometry'][key]) for key in ref['geometry']}
    speedup=ref['summary']['job_wall_s']/can['summary']['job_wall_s']
    passed=all(r['thermal_gate'] and r['pressure']['passed'] and r['pressure']['temperature_linear_gate'] and r['fine_grid_gate'] for r in results.values()) and all(g['passed'] for g in geometry.values())
    report=dict(schema=1,complete=True,results=results,geometry_comparison=geometry,job_speedup=speedup,
        pressure_section_speedup=ref['summary']['sections']['pressure']['mean_s']/can['summary']['sections']['pressure']['mean_s'],
        recommended_for_longer_continuation=passed and speedup>1.05,production_approved=False,
        note='Matched 50--60us restart. Melt depth/width differences <=5% at both55/60us; thermal and pressure convergence retained. No proof of 1.5mm evolution or final solidification. Continuity/Tmax/recoil are reported; no extra temperature/recoil rejection budget.')
    save(work/'comparison.json',report);print(json.dumps(report,indent=2),flush=True)

def execute(source,work):
    source=source.resolve();validate_source(source)
    source_hash=digest(source.parent/'pilotReport.json')
    source_meta,source_summary,_=read_probe(source)
    source_audit=pressure_stats((source/'log.vacuumLaserbeamFoam').read_text(errors='replace'),source_summary['steps'])
    save(work/'source.json',dict(case=str(source),pilot_report_sha256=source_hash,start_s=START,end_s=END,
        initial_pilot_linear_audit=source_audit,
        note='Mature restart pair does not repair or validate the initial pilot startup T linear-solver cap.'))
    for variant in VARIANTS:prepare(source,work/variant,variant,source_hash)
    metas=[json.loads((work/v/'probe.json').read_text()) for v in VARIANTS]
    if metas[0]['source_snapshot_sha256']!=metas[1]['source_snapshot_sha256']:raise ValueError('Copied inputs differ; no CFD advanced')
    check=json.loads((work/'solverCheck.json').read_text())
    solver=Path(shutil.which('vacuumLaserbeamFoam')).resolve()
    if digest(solver)!=check['solver_sha256']:raise ValueError('Solver changed after preflight')
    for variant in VARIANTS:
        case=work/variant;code=1;start=time.perf_counter()
        try:run(case,'vacuumLaserbeamFoam',['mpirun','-np','48',solver,'-parallel']);code=0
        finally:save(case/'run.json',dict(elapsed_wall_s=time.perf_counter()-start,returncode=code,wall_budget_stop=False,forced_stop=False,
            solver_sha256=check['solver_sha256'],laser_library_sha256=check['laser_library_check']['laser_library_sha256']))
        setting(case,'system/controlDict','writeFormat','ascii')
        try:
            geometry={}
            for sample in SAMPLES:
                sample_text=f'{sample:.12g}'
                run(case,'reconstructPar_'+sample_text,['reconstructPar','-fields','(alpha.metal T)','-time',sample_text])
                run(case,'writeCellCentres_'+sample_text,['postProcess','-func','writeCellCentres','-time',sample_text])
                geometry[sample_text]=pool_geometry(final_state(case,None,sample),beam_x=sample)
            save(case/'geometrySamples.json',geometry)
        finally:setting(case,'system/controlDict','writeFormat','binary')
    collect(work)

def package(work,code):
    files=[p for p in work.rglob('*') if p.is_file() and not any(part.startswith('processor') or part in ('polyMesh','postProcessing') for part in p.relative_to(work).parts)
        and (p.suffix in ('.json','.csv','.txt','.log','.md') or p.name.startswith('log.') or p.parent.name in ('constant','system')) and p.name!='manifest.json']
    missing=[name for name in ['comparison.json']+[v+'/'+f for v in VARIANTS for f in ('run.json','geometrySamples.json','log.vacuumLaserbeamFoam')] if not (work/name).exists()]
    save(work/'manifest.json',dict(schema=1,exit_code=code,complete=code==0 and not missing,missing_files=missing,
        files=[dict(path=p.relative_to(work).as_posix(),size=p.stat().st_size,sha256=digest(p)) for p in files]))
    archive=work.parent/('M247_'+work.name+'_review.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for p in files+[work/'manifest.json']:tar.add(p,arcname=work.name+'/'+p.relative_to(work).as_posix())
    print('Review archive: '+str(archive)+'\nSend this single archive, including on failure.',flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path);parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--collect',action='store_true');parser.add_argument('--package',action='store_true');parser.add_argument('--exit-code',type=int,default=0)
    a=parser.parse_args();work=a.work.resolve()
    if a.package:package(work,a.exit_code)
    elif a.collect:collect(work)
    elif a.source:execute(a.source,work)
    else:parser.error('--source required to execute')

if __name__=='__main__':main()
