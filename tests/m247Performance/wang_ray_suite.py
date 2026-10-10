#!/usr/bin/env python3
"""Fresh Wang 304L 4um histories: identical solver/mesh, angular sampling only."""
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import time

from collect_probe import read_probe, parse_records
from collect_thermal_validation import read_field, residual_gate

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT/'tutorials/vacuumLaserbeamFoam/wang2020_304L_nearVacuum'
VARIANTS = ((1536,96),(768,48),(384,24),(192,12))
END = 140e-6
NCELLS = 80**3

def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n', encoding='utf-8')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(case, label, command):
    print(f'Starting {case.name}: {label}', flush=True)
    with (case/('log.'+label)).open('w', encoding='utf-8') as log:
        subprocess.run([str(x) for x in command], cwd=case, stdout=log,
                       stderr=subprocess.STDOUT, check=True)

def setting(case, dictionary, key, value):
    subprocess.run(['foamDictionary',str(case/dictionary),'-entry',key,'-set',str(value)],
                   stdout=subprocess.DEVNULL, check=True)

def crossing(rows, target):
    # First upward crossing, interpolated between written samples; no extrapolation.
    if rows and rows[0][1]==target: return rows[0][0]
    for a,b in zip(rows, rows[1:]):
        if a[1] < target <= b[1]:
            return a[0]+(target-a[1])*(b[0]-a[0])/(b[1]-a[1])
    return None

def interpolate(rows, t):
    for a,b in zip(rows,rows[1:]):
        if a[0] <= t <= b[0]:
            return a[1]+(b[1]-a[1])*(t-a[0])/(b[0]-a[0])
    raise ValueError('Requested time outside measured history')

def relative(a,b):
    return abs(a-b)/abs(a) if abs(a)>1e-30 else None

def scalar_field(path):
    values, components, uniform = read_field(path)
    if components != 1 or (not uniform and len(values)!=NCELLS):
        raise ValueError('Requires original uniform 80^3 scalar mesh: '+str(path))
    return values*NCELLS if uniform else values

def field_metrics(case):
    result=[]
    for state in sorted(case.iterdir(), key=lambda p:p.name):
        try: t=float(state.name)
        except ValueError: continue
        if not state.is_dir() or t<=0: continue
        a=scalar_field(state/'alpha.metal'); e=scalar_field(state/'epsilon1')
        if any(x < -1e-5 or x > 1.00001 for x in a+e):
            raise ValueError('Out-of-range phase field')
        result.append(dict(time_s=t, liquid_metal_volume_m3=sum(x*y for x,y in zip(a,e))*4e-6**3))
    result.sort(key=lambda r:r['time_s'])
    if not result or abs(result[-1]['time_s']-END)>1e-12:
        raise ValueError('Missing final liquid-volume state')
    save(case/'liquidVolume.json',result)
    return result

def summarize(case):
    summary, diag, perf=read_probe(case)
    depth=[(float(r['time_s']),float(r['keyhole_depth_um'])) for r in
           csv.DictReader((case/'keyholeDepthSurface.csv').open())]
    depth.sort()
    if len(depth)<2 or abs(depth[-1][0]-END)>1e-12:
        raise ValueError('Incomplete connected-depth history')
    t32=crossing(depth,32); t136=crossing(depth,136)
    growth=(t136-t32)*1e6 if t32 is not None and t136 is not None and t136>t32 else None
    recoil=list(csv.DictReader((case/'keyholeRecoilSurface.csv').open()))
    if not recoil or abs(float(recoil[-1]['time_s'])-END)>1e-12:
        raise ValueError('Incomplete recoil history')
    axial=[(float(r['time_s']),float(r['full_recoil_force_y_signed_N'])) for r in recoil]
    load=[(float(r['time_s']),float(r['full_scalar_pressure_load_N'])) for r in recoil]
    stage=t32+75e-6 if t32 is not None else None
    stage_metrics=dict(time_s=stage,axial_force_abs_N=abs(interpolate(axial,stage)),scalar_load_N=interpolate(load,stage)) if stage is not None and axial[0][0]<=stage<=axial[-1][0] else None
    text=(case/'log.vacuumLaserbeamFoam').read_text(errors='replace')
    refresh=parse_records(text,'LASER_REFRESH_DIAGNOSTICS')
    if len(refresh)!=summary['steps'] or any(r.get('interval')!=1 or r.get('refreshed')!=1 for r in refresh):
        raise ValueError('Every-step laser refresh not evidenced')
    summary.update(growth_32_136_us=growth,
                   deviation_from_wang_75us=relative(75,growth) if growth else None,
                   deviation_from_xray_70us=relative(70,growth) if growth else None,
                   historical_full_ray_growth_us=76.2318,
                   equivalent_recoil_stage_75us_after_32um=stage_metrics,
                   thermal_gate=summary['thermal_limit_hits']==0 and residual_gate(case,json.loads((case/'probe.json').read_text()),summary['steps']),
                   depth_history=depth, diagnostics=diag,
                   liquid_volume=field_metrics(case),
                   recoil_note='Beam is along -y here: full_recoil_force_y_signed_N is axial; full scalar load is a different quantity',
                   recoil_history=recoil)
    save(case/'summary.json',summary)
    return summary

def compare_histories(reference, candidate):
    result={}
    histories={'depth':(reference['depth_history'],candidate['depth_history']),
               'liquid_volume':([(r['time_s'],r['liquid_metal_volume_m3']) for r in reference['liquid_volume']],
                                [(r['time_s'],r['liquid_metal_volume_m3']) for r in candidate['liquid_volume']]),
               'Tmax':([(r['time'],r['Tmax']) for r in reference['diagnostics']],
                       [(r['time'],r['Tmax']) for r in candidate['diagnostics']])}
    for name,(a,b) in histories.items():
        # Compare on reference sample times within common coverage. Early zero values
        # use absolute error and a peak-normalised history error, not division by zero.
        common=[(t,x,interpolate(b,t)) for t,x in a if b[0][0]<=t<=b[-1][0]]
        if len(common)<2: raise ValueError('Insufficient common history')
        peak=max(abs(x) for _,x,_ in common)
        if peak<=0: raise ValueError('No nonzero reference '+name)
        absolute=max(abs(x-y) for _,x,y in common)
        pointwise=[relative(x,y) for _,x,y in common if abs(x)>1e-30]
        result[name]=dict(max_absolute_difference=absolute,
            max_peak_normalized_difference=absolute/peak,
            max_pointwise_relative_difference=max(pointwise),
            reference_zero_candidate_nonzero_samples=sum(abs(x)<=1e-30 and abs(y)>1e-30 for _,x,y in common),
            final_relative_difference=relative(common[-1][1],common[-1][2]),
            samples=len(common))
    result['job_speedup']=reference['job_wall_s']/candidate['job_wall_s']
    result['growth_relative_difference']=relative(reference['growth_32_136_us'],candidate['growth_32_136_us']) if reference['growth_32_136_us'] and candidate['growth_32_136_us'] else None
    # Literal relative-budget comparison at nonzero reference samples. Also
    # report peak-normalised error for interpreting fragile early onset ratios.
    result['macro_history_budget_pass']=all(result[k]['max_pointwise_relative_difference']<=tol and result[k]['reference_zero_candidate_nonzero_samples']==0 for k,tol in (('depth',.05),('liquid_volume',.05),('Tmax',.1)))
    for metric in ('depositedPower','evaporationPower','recoilForceX','recoilForceY','recoilForceZ'):
        a=[(r['time'],r[metric]) for r in reference['diagnostics']]
        b=[(r['time'],r[metric]) for r in candidate['diagnostics']]
        errors=[abs(x-interpolate(b,t)) for t,x in a if b[0][0]<=t<=b[-1][0]]
        peak=max(abs(x) for _,x in a)
        result[metric]=dict(max_absolute_difference=max(errors),max_peak_normalized_difference=max(errors)/peak if peak>0 else None)
    for metric in ('full_recoil_force_y_signed_N','full_scalar_pressure_load_N'):
        a=[(float(r['time_s']),float(r[metric])) for r in reference['recoil_history']]
        b=[(float(r['time_s']),float(r[metric])) for r in candidate['recoil_history']]
        errors=[abs(x-interpolate(b,t)) for t,x in a if b[0][0]<=t<=b[-1][0]]
        peak=max(abs(x) for _,x in a)
        result[metric]=dict(max_absolute_difference=max(errors),max_peak_normalized_difference=max(errors)/peak if peak>0 else None)
    result['eligible_for_M247_confirmation']=result['macro_history_budget_pass'] and candidate['thermal_gate'] and reference['thermal_gate'] and result['growth_relative_difference'] is not None and result['job_speedup']>1
    return result

def collect(work):
    summaries={}; errors={}
    for count,_ in VARIANTS:
        name=f'rays{count}'
        try: summaries[name]=summarize(work/name)
        except Exception as exc: errors[name]=str(exc)
    comparisons={}
    if 'rays1536' in summaries:
        for name,summary in summaries.items():
            if name!='rays1536': comparisons[name]=compare_histories(summaries['rays1536'],summary)
    eligible=[name for name,c in comparisons.items() if c['eligible_for_M247_confirmation']]
    report=dict(schema=1, complete=len(summaries)==4, errors=errors,
        comparisons=comparisons, recommended_for_M247_confirmation=max(eligible,key=lambda n:comparisons[n]['job_speedup']) if eligible else None,
        production_approved=False,
        note='Wang acceptance requires reviewing the full curves and axial recoil against literature; M247 transfer still requires its own longer paired test.')
    save(work/'comparison.json',report)
    with (work/'comparison.csv').open('w',newline='',encoding='utf-8') as handle:
        writer=csv.writer(handle)
        writer.writerow(('variant','job_wall_s','speedup','growth_32_136_us','thermal_gate','depth_max_relative','volume_max_relative','Tmax_max_relative','macro_budget_pass'))
        for name,summary in summaries.items():
            c=comparisons.get(name,{})
            writer.writerow((name,summary['job_wall_s'],c.get('job_speedup',1),summary['growth_32_136_us'],summary['thermal_gate'],*[c.get(k,{}).get('max_pointwise_relative_difference') for k in ('depth','liquid_volume','Tmax')],c.get('macro_history_budget_pass')))
    print(json.dumps(report,indent=2),flush=True)
    if errors: raise ValueError('Incomplete suite; see comparison.json')

def execute(work):
    solver=Path(shutil.which('vacuumLaserbeamFoam')).resolve()
    if b'LASER_REFRESH_DIAGNOSTICS schema=1 time=' not in solver.read_bytes():
        raise ValueError('Old solver: missing every-step refresh diagnostics; rebuild first')
    library=Path(os.environ['FOAM_USER_LIBBIN'])/'liblaserHeatSource.so'
    save(work/'binaries.json',dict(solver=str(solver),solver_sha256=digest(solver),laser_library_sha256=digest(library)))
    source_hashes={str(p.relative_to(SOURCE)):digest(p) for p in SOURCE.rglob('*') if p.is_file() and p.relative_to(SOURCE).parts[0] in ('constant','system','initial','scripts')}
    save(work/'sourceHashes.json',source_hashes)
    seed=work/'prepared'; seed.mkdir()
    for folder in ('constant','system','initial','scripts'):
        shutil.copytree(SOURCE/folder,seed/folder)
    shutil.copyfile(seed/'system/blockMeshDict.reference4um',seed/'system/blockMeshDict')
    shutil.copyfile(seed/'system/controlDict.reference',seed/'system/controlDict')
    shutil.copytree(seed/'initial',seed/'0')
    for key,val in dict(startFrom='startTime',startTime=0,writeFormat='ascii',writePrecision=17,laserRefreshIntervalSteps=1,frozenLaserProbe='off',thermalInvariantCache='false').items():
        setting(seed,'system/controlDict',key,val)
    for key in ('performanceDiagnostics','writeDiagnostics'):
        setting(seed,'constant/vacuumProperties',key,'true')
    for key,val in dict(boundedEnthalpyCorrection='true',epsilonTolerance='1e-5',phaseTemperatureTolerance='.001',phaseTemperatureBlendHalfWidth=0,thermalCorrectorLogging='true',thermalResidualDiagnostics='true').items():
        setting(seed,'system/fvSolution','MELTING/'+key,val)
    for key,val in dict(nRadial=16,nAngular=96,recordRayPaths='false',laserPerformanceDiagnostics='true',cachedRayTraversal='true',preserveRayHandoffSample='true',consistentRayTermination='true',cartesianRaySeedSearch='false',packedRayBroadcast='false').items():
        setting(seed,'constant/LaserProperties',key,val)
    setting(seed,'system/decomposeParDict','numberOfSubdomains',48)
    for tool in ('blockMesh','setFields','checkMesh','decomposePar'): run(seed,tool,[tool])
    initial_hashes={p.relative_to(seed).as_posix():digest(p) for p in seed.rglob('*')
        if p.is_file() and (p.relative_to(seed).parts[0]=='0' or p.relative_to(seed).parts[0].startswith('processor'))}
    save(work/'commonInitialHashes.json',initial_hashes)
    failures={}
    for count,angular in VARIANTS:
        case=work/f'rays{count}'; case.mkdir()
        for item in seed.iterdir():
            if item.is_dir() and (item.name in ('constant','system','0','scripts') or item.name.startswith('processor')):
                shutil.copytree(item,case/item.name)
        # Same decomposition and initial state; only angular seed count differs.
        setting(case,'constant/LaserProperties','nAngular',angular)
        if any(digest(case/path)!=expected for path,expected in initial_hashes.items()):
            raise ValueError('Copied initial fields/decomposition differ: '+case.name)
        save(case/'probe.json',dict(schema=1,variant=case.name,start_s=0,end_s=END,duration_us=140,ranks=48,nRadial=16,nAngular=angular,rays=count,epsilon_tolerance=1e-5,phase_temperature_tolerance_K=.001))
        try:
            started=time.perf_counter(); code=0
            try: run(case,'vacuumLaserbeamFoam',['mpirun','-np','48',solver,'-parallel'])
            except subprocess.CalledProcessError as exc: code=exc.returncode; raise
            finally: save(case/'run.json',dict(elapsed_wall_s=time.perf_counter()-started,returncode=code,wall_budget_stop=False,forced_stop=False))
            run(case,'reconstructPar',['reconstructPar','-fields','(alpha.metal epsilon1 T pVap)','-time','2e-6:'])
            for name,fields in (('keyholeInterface','(alpha.metal)'),('keyholeRecoil','(alpha.metal pVap T)')):
                dictionary='system/keyholeInterfaceDict' if name=='keyholeInterface' else 'system/keyholeRecoilDict'
                run(case,'postProcess.'+name,['postProcess','-dict',dictionary,'-fields',fields,'-time','2e-6:'])
            for script,folder,output in (('extractKeyholeSurfaceDepth.py','keyholeInterface','keyholeDepthSurface.csv'),('extractKeyholeRecoil.py','keyholeRecoilSurface','keyholeRecoilSurface.csv')):
                run(case,script,['python3','scripts/'+script,'--post-processing','postProcessing/'+folder,'--surface-y','200e-6','--surface-band','8e-6','--output',output])
        except Exception as exc:
            failures[case.name]=str(exc); save(case/'failure.json',dict(error=str(exc)))
    save(work/'executionFailures.json',failures)
    if source_hashes!={str(p.relative_to(SOURCE)):digest(p) for p in SOURCE.rglob('*') if p.is_file() and p.relative_to(SOURCE).parts[0] in ('constant','system','initial','scripts')}:
        raise ValueError('Source dictionaries changed during suite')
    collect(work)

def package(work, code):
    files=[p for p in work.rglob('*') if p.is_file() and ('processor' not in '/'.join(p.relative_to(work).parts)) and
           (p.suffix in ('.json','.csv','.txt') or p.name.startswith('log.') or p.parent.name in ('constant','system')) and 'postProcessing' not in p.parts and 'polyMesh' not in p.parts]
    files=[p for p in files if p.name!='manifest.json']
    required=['comparison.json','solverCheck.json','binaries.json','commonInitialHashes.json']+[f'rays{count}/{name}' for count,_ in VARIANTS for name in ('run.json','summary.json','keyholeDepthSurface.csv','keyholeRecoilSurface.csv','liquidVolume.json')]
    missing=[name for name in required if not (work/name).is_file()]
    save(work/'manifest.json',dict(schema=1,exit_code=code,missing_files=missing,complete=not missing and code==0,files=[dict(path=p.relative_to(work).as_posix(),sha256=digest(p),size=p.stat().st_size) for p in files]))
    archive=work.parent/('M247_'+work.name+'_review.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for p in files+[work/'manifest.json']: tar.add(p,arcname=work.name+'/'+p.relative_to(work).as_posix())
    print('Review archive: '+str(archive)+'\nSend this single archive, including on failure.',flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--collect',action='store_true')
    parser.add_argument('--package',action='store_true')
    parser.add_argument('--exit-code',type=int,default=0)
    a=parser.parse_args(); work=a.work.resolve()
    if a.package: package(work,a.exit_code)
    elif a.collect: collect(work)
    else: execute(work)

if __name__=='__main__': main()
