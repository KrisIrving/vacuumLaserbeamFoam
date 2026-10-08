#!/usr/bin/env python3
"""Opt-in 0.2us full-solver pilot; no measured speedup claim."""
import argparse,json,math,re,shutil,subprocess,sys,tarfile,time
from pathlib import Path
from collect_probe import read_probe,parse_records
from collect_thermal_validation import residual_gate
from restart_audit import case_fingerprint
from prepare_probe import set_entry
from region_audit import sha
from moving_window import collect,dynamic_dictionary


def mapping_gate(text,end_s=.0001802):
    rows=parse_records(text,'M247_MOVING_CFD')
    if not rows:raise ValueError('Missing rebuilt moving-CFD diagnostics')
    previous=.00018
    for row in rows:
        keys=('schema','time','cells','changed','centreX','centreZ','requested','wakeBefore','wakeAfter','wakeMissed',
              'metalBefore','metalAfter','thermalProxyBefore','thermalProxyAfter')
        if any(k not in row or not math.isfinite(row[k]) for k in keys):raise ValueError('Incomplete/nonfinite moving-CFD record')
        if row['schema']!=1 or not previous<row['time']<=end_s+1e-12:raise ValueError('Wrong moving-CFD time/schema')
        previous=row['time']
        if not 756000<=row['cells']<=2000000 or row['cells']!=int(row['cells']):raise ValueError('Moving-CFD cell budget failed')
        if row['changed'] not in (0,1):raise ValueError('Invalid topology flag')
        if any(row[k]!=int(row[k]) or row[k]<0 for k in ('requested','wakeBefore','wakeAfter','wakeMissed')):raise ValueError('Invalid moving-CFD counts')
        if abs(row['centreX']-(-100e-6+row['time']))>1e-12 or abs(row['centreZ'])>1e-12:raise ValueError('Window differs from original laser table')
        if row['metalBefore']<=0 or row['thermalProxyBefore']<=0:raise ValueError('Invalid pre-mapping integrals')
    errors=[dict(time=r['time'],metal_relative=abs(r['metalAfter']/r['metalBefore']-1),
        thermal_proxy_relative=abs(r['thermalProxyAfter']/r['thermalProxyBefore']-1)) for r in rows]
    return dict(records=rows,mapping_errors=errors,
        coverage_gate=all(r['wakeMissed']==0 and r['wakeAfter']>0 for r in rows),
        topology_gate=any(r['changed']==1 for r in rows),
        mapping_screen=all(e['metal_relative']<=1e-6 and e['thermal_proxy_relative']<=1e-6 for e in errors),
        thermal_proxy_relative_limit=1e-6,production_approved=False)


def state_gate(text,mapping):
    rows=parse_records(text,'M247_MOVING_CFD_STATE')
    if len(rows)!=len(mapping['records']):raise ValueError('Missing final-step moving-CFD state records')
    for row,mesh in zip(rows,mapping['records']):
        keys=('schema','time','alphaMin','alphaMax','epsilonMin','epsilonMax','Tmin','Tmax','Umax','divL1','divMax','invalid')
        if any(k not in row or not math.isfinite(row[k]) for k in keys):raise ValueError('Missing/nonfinite final-step state')
        if row['schema']!=1 or abs(row['time']-mesh['time'])>1e-12:raise ValueError('Wrong final-step state time/schema')
        if row['invalid']!=0 or row['alphaMin']<-1e-8 or row['alphaMax']>1+1e-8 or row['epsilonMin']<-1e-8 or row['epsilonMax']>1+1e-8 or row['Tmin']<=0 or row['Tmax']<row['Tmin'] or row['Umax']<0 or row['divL1']<0 or row['divMax']<row['divL1']:
            raise ValueError('Invalid final-step field bounds/continuity')
    return dict(records=rows,continuity_screen=all(r['divL1']<=.05 and r['divMax']<=15000 for r in rows),
        limits=dict(divL1=.05,divMax=15000),note='Short-pilot continuity screen, not production tolerance.')


def mesh_cost(text,mapping,required=False):
    rows=parse_records(text,'M247_MOVING_MESH_COST')
    if not rows:
        if required:raise ValueError('Missing native mesh-cost records; rebuild required')
        return dict(available=False,reason='Historical solver has no separate mesh timer')
    if len(rows)!=len(mapping['records']):raise ValueError('Incomplete mesh-cost records')
    keys=('topologyWallMax','preparationWallMax','auditWallMax','updateWallMax')
    for row,step in zip(rows,mapping['records']):
        if row.get('schema')!=1 or abs(row.get('time',float('inf'))-step['time'])>1e-12:
            raise ValueError('Mesh-cost time/schema mismatch')
        if any(k not in row or not math.isfinite(row[k]) or row[k]<0 for k in keys):
            raise ValueError('Invalid mesh-cost timing')
        if any(row[k]>row['updateWallMax']+1e-9 for k in keys[:-1]):
            raise ValueError('Mesh stage exceeds total update time')
    return dict(available=True,records=rows,wall_s={k:sum(r[k] for r in rows) for k in keys},
        note='Per-call rank maxima; stage maxima need not sum to total. Excludes timing reductions/output, isoAdvector remap and external CorrectPhi.')


def thermal_metadata(case,metadata):
    """Read explicit archived controls; never silently substitute a tolerance."""
    text=(case/'system/fvSolution').read_text()
    text=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
    match=re.search(r'\bMELTING\s*\{',text)
    if not match:raise ValueError('Missing MELTING controls')
    start=match.end();depth=1;end=start
    while end<len(text) and depth:
        if text[end]=='{':depth+=1
        elif text[end]=='}':depth-=1
        end+=1
    if depth:raise ValueError('Incomplete MELTING controls')
    block=text[start:end-1];result=dict(metadata)
    for name,key in (('epsilonTolerance','epsilon_tolerance'),('phaseTemperatureTolerance','phase_temperature_tolerance_K')):
        values=re.findall(r'\b'+name+r'\s+([-+0-9.eE]+)\s*;',block)
        if len(values)!=1:raise ValueError('Explicit unique thermal control required: '+name)
        value=float(values[0])
        if not math.isfinite(value) or value<=0:raise ValueError('Invalid thermal control: '+name)
        if key in metadata and not math.isclose(metadata[key],value,rel_tol=1e-12,abs_tol=0):
            raise ValueError('Thermal metadata differs from fvSolution: '+key)
        result[key]=value
    return result


def collect_case(case,solver_sha,require_mesh_cost=False):
    provenance=json.loads((case/'run.json').read_text())
    if provenance.get('solver_sha256')!=solver_sha:raise ValueError('Launched solver binary differs from recorded rebuild')
    meta,summary,diagnostics=read_probe(case)
    meta=thermal_metadata(case,meta)
    text=(case/'log.vacuumLaserbeamFoam').read_text()
    mapping=mapping_gate(text,meta['end_s']);state=state_gate(text,mapping)
    thermal=summary['thermal_limit_hits']==0 and residual_gate(case,meta,summary['steps'])
    if abs(mapping['records'][-1]['time']-meta['end_s'])>1e-12:raise ValueError('Mesh lifecycle did not reach pilot end time')
    if len(mapping['records'])!=summary['steps']:raise ValueError('Missing per-step mesh lifecycle records')
    return dict(complete=True,metadata_used=meta,pilot=summary,physical_diagnostics=diagnostics,
        moving_mapping=mapping,final_step_state=state,mesh_cost=mesh_cost(text,mapping,require_mesh_cost),thermal_gate=thermal,
        pilot_gate=all((thermal,mapping['coverage_gate'],mapping['topology_gate'],mapping['mapping_screen'],state['continuity_screen'])))


def resume(previous,work):
    """Verify immutable archived inputs, recollect only, and write a fresh bundle."""
    previous,work=map(lambda p:Path(p).resolve(),(previous,work))
    if work==previous or previous in work.parents or work in previous.parents:raise ValueError('Resume output overlaps completed run')
    archive=previous.parent/('M247_'+previous.name+'_review.tar.gz')
    with tarfile.open(archive) as stream:
        manifest=json.load(stream.extractfile('manifest.json'))
    files={f['source']:f for f in manifest['files']}
    critical=('movingCFDReview.json','movingCFD/log.vacuumLaserbeamFoam','movingCFD/probe.json','movingCFD/run.json','movingCFD/system/fvSolution')
    for name in critical:
        if name not in files:raise ValueError('Original archive lacks critical resume input: '+name)
        path=previous/name;record=files[name]
        if sha(path)!=record['sha256'] or path.stat().st_size!=record['bytes']:raise ValueError('Archived resume input changed: '+name)
    prior=json.loads((previous/'movingCFDReview.json').read_text())
    source=Path(prior['source_case']).resolve()
    if work==source or source in work.parents or work in source.parents:raise ValueError('Resume output overlaps original source')
    if case_fingerprint(source)!=prior['source_sha256']:raise ValueError('Original coarse source changed')
    if (work/'movingCFDReview.json').exists():raise ValueError('Choose fresh collection work')
    work.mkdir(parents=True,exist_ok=True)
    from package_results import FILES
    case=work/'movingCFD';case.mkdir()
    for name in FILES:
        original=previous/'movingCFD'/name
        if original.is_file():
            target=case/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(original,target)
    report={k:v for k,v in prior.items() if k not in ('error','error_type','commands')}
    report.update(complete=False,pilot_gate=False,commands=[],original_commands=prior.get('commands',[]),
        collection_only=True,no_cfd_advanced=True,resumed_from=str(previous),original_archive_sha256=sha(archive))
    target=work/'movingCFDReview.json'
    def save():target.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        report.update(collect_case(case,prior['solver_sha256']),source_unchanged_gate=True)
        save();return report
    except (ValueError,KeyError,OSError) as error:
        report.update(error_type=type(error).__name__,error=str(error));save();raise


def execute(previous,work,solver,max_delta_ns=5,duration_us=.2):
    if max_delta_ns not in (5,10):raise ValueError("Pilot max delta must be 5 or 10 ns")
    if duration_us not in (.2,.4):raise ValueError("Pilot duration must be 0.2 or 0.4 us")
    end_s=.00018+duration_us*1e-6
    previous,work,solver=map(lambda p:Path(p).resolve(),(previous,work,solver))
    prior=json.loads((previous/'movingWindowReview.json').read_text())
    if not prior.get('complete') or not prior.get('prototype_gate') or not prior.get('protect_wake'):
        raise ValueError('Completed protected native prototype required')
    verified=collect((previous/'movingWindow_updates.log').read_text(),require_wake=True)
    if not all(verified[k] for k in ('wake_gate','linear_mapping_gate','coverage_gate','coarsening_gate')):
        raise ValueError('Protected topology prerequisites failed')
    source=Path(prior['source_case']).resolve();expected=prior['source_sha256']
    for parent in (previous,source):
        if work==parent or parent in work.parents or work in parent.parents:raise ValueError('Output overlaps original data')
    if case_fingerprint(source)!=expected:raise ValueError('Original coarse source changed')
    if (work/'movingCFDReview.json').exists():raise ValueError('Choose fresh work')
    located=shutil.which('vacuumLaserbeamFoam')
    if not located or Path(located).resolve()!=solver:raise ValueError('PATH solver differs from rebuilt binary')
    if b'M247_MOVING_CFD' not in solver.read_bytes() or b'M247_MOVING_MESH_COST' not in solver.read_bytes():raise ValueError('Solver rebuild required: missing moving-CFD marker')
    work.mkdir(parents=True,exist_ok=True);case=work/'movingCFD';case.mkdir()
    report=dict(schema=1,complete=False,production_approved=False,pilot_gate=False,
        original_protected_review_sha256=sha(previous/'movingWindowReview.json'),source_case=str(source),
        source_sha256=expected,solver_sha256=sha(solver),duration_us=duration_us,ranks=48,max_delta_ns=max_delta_ns,commands=[],
        note='Actual isoAdvector/CorrectPhi/thermal solver pilot. No equivalent-grid speedup pair; rho*(cp*T+L*epsilon) is a screening proxy, not thermodynamic enthalpy.')
    target=work/'movingCFDReview.json'
    def save():target.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        for part in ('constant','system','0.00018'):shutil.copytree(source/part,case/part)
        if case_fingerprint(case)!=expected:raise ValueError('Copied initial state hash mismatch')
        interface=subprocess.check_output(['foamDictionary',str(case/'constant/transportProperties'),'-entry','interfaceTrackingScheme','-value'],text=True).strip()
        ranks=subprocess.check_output(['foamDictionary',str(case/'system/decomposeParDict'),'-entry','numberOfSubdomains','-value'],text=True).strip()
        if interface!='isoAdvector' or ranks!='48':raise ValueError('Pilot requires audited isoAdvector/48-rank settings')
        import re
        numbers=[float(x) for x in re.findall(r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?',(case/'constant/timeVsLaserPosition').read_text())]
        if numbers!=[0,-100e-6,959.5e-6,0,200e-6,100e-6,959.5e-6,0]:raise ValueError('Pilot requires original M247 trajectory')
        dictionary=dynamic_dictionary().replace('dynamicFvMesh dynamicRefineFvMesh;',
            'dynamicFvMesh m247MovingRefineFvMesh;').replace('field movingRefineMask;','field m247RefineMask;').replace('correctFluxes ();','correctFluxes ((phi U));')
        (case/'constant/dynamicMeshDict').write_text(dictionary)
        (case/'system/m247MovingWindowDict').write_text('FoamFile { version 2.0; format ascii; class dictionary; object m247MovingWindowDict; }\nhalfX 96e-6; halfZ 96e-6; hotTemperature 1537; releaseTemperature 1487;\nliquidThreshold 1e-4; solidThreshold 1e-6; metalThreshold 1e-6;\n')
        shutil.copy2(case/'constant/dynamicMeshDict',work/'movingCFD_dynamicMeshDict')
        shutil.copy2(case/'system/m247MovingWindowDict',work/'movingCFD_windowDict')
        for key,value in (('startFrom','startTime'),('startTime','0.00018'),('endTime',format(end_s,'.12g')),
                          ('stopAt','endTime'),('writeInterval','1e-7'),('timePrecision','12'),
                          ('deltaT','1e-9'),('maxDeltaT',str(max_delta_ns*1e-9)),('adjustTimeStep','true'),
                          ('maxCo','0.1'),('maxAlphaCo','0.1'),
                          ('writePrecision','17'),('writeFormat','ascii'),('writeCompression','off'),
                          ('performanceDiagnostics','true'),('writeDiagnostics','true'),
                          ('thermalCorrectorLogging','true'),('runTimeModifiable','true'),('functions','{}')):
            set_entry(case/'system/controlDict',key,value)
        set_entry(case/'system/fvSolution','PIMPLE/correctPhi','true')
        set_entry(case/'system/fvSolution','PIMPLE/moveMeshOuterCorrectors','false')
        metadata=dict(schema=1,source=str(source),variant='movingCFD',start_s=.00018,end_s=end_s,
            duration_us=duration_us,ranks=48,max_delta_ns=max_delta_ns,checkpoint='0.00018',source_snapshot_sha256=sha(previous/'movingWindowReview.json'),
            purpose='Experimental moving fine-window full-solver pilot; no measured speedup claim')
        metadata=thermal_metadata(case,metadata)
        (case/'probe.json').write_text(json.dumps(metadata,indent=2)+'\n')
        deadline=time.monotonic()+1800
        def launch(command,name):
            remaining=deadline-time.monotonic()
            if remaining<=0:raise ValueError('30 minute command budget exhausted')
            started=time.monotonic()
            with (work/(name+'.log')).open('x') as stream:
                subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=remaining)
            report['commands'].append(dict(command=command,elapsed_wall_s=time.monotonic()-started,log=name+'.log'));save()
        launch(['decomposePar','-case',str(case),'-time','0.00018','-noFunctionObjects'],'movingCFD_decompose')
        remaining=deadline-time.monotonic()
        if remaining<=240:raise ValueError('Insufficient command budget for solver and graceful MPI stop')
        wall_seconds=min(900,remaining-240)
        report['solver_wall_budget_s']=wall_seconds;save()
        launch([sys.executable,str(Path(__file__).with_name('run_probe.py')),'--case',str(case),'--wall-hours',str(wall_seconds/3600)],'movingCFD_pilot')
        collected=collect_case(case,report['solver_sha256'],require_mesh_cost=True)
        if case_fingerprint(source)!=expected:raise ValueError('Original source changed')
        report.update(collected,source_unchanged_gate=True)
        save();return report
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as error:
        report.update(error_type=type(error).__name__,error=str(error));save();raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous','work'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--solver',type=Path)
    p.add_argument('--resume',action='store_true')
    p.add_argument('--max-delta-ns',type=int,choices=(5,10),default=5)
    p.add_argument('--duration-us',type=float,choices=(.2,.4),default=.2)
    a=p.parse_args()
    try:
        if not a.resume and a.solver is None:raise ValueError('--solver is required for a new CFD run')
        r=resume(a.previous,a.work) if a.resume else execute(a.previous,a.work,a.solver,a.max_delta_ns,a.duration_us)
        print('Moving CFD compatibility pilot gate:',r['pilot_gate'],'production approved: False')
        if not r['pilot_gate']:p.exit(2,'Pilot screen failed; send review archive.\n')
    except (ValueError,KeyError,OSError,subprocess.SubprocessError,tarfile.TarError) as e:p.exit(1,f'Moving CFD pilot failed: {e}\n')
if __name__=='__main__':main()
