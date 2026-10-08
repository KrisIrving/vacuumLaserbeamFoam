#!/usr/bin/env python3
"""Opt-in 0.2us full-solver pilot; no measured speedup claim."""
import argparse,json,math,shutil,subprocess,sys,time
from pathlib import Path
from collect_probe import read_probe,parse_records
from collect_thermal_validation import residual_gate
from restart_audit import case_fingerprint
from prepare_probe import set_entry
from region_audit import sha
from moving_window import collect,dynamic_dictionary


def mapping_gate(text):
    rows=parse_records(text,'M247_MOVING_CFD')
    if not rows:raise ValueError('Missing rebuilt moving-CFD diagnostics')
    previous=.00018
    for row in rows:
        keys=('schema','time','cells','changed','centreX','centreZ','requested','wakeBefore','wakeAfter','wakeMissed',
              'metalBefore','metalAfter','thermalProxyBefore','thermalProxyAfter')
        if any(k not in row or not math.isfinite(row[k]) for k in keys):raise ValueError('Incomplete/nonfinite moving-CFD record')
        if row['schema']!=1 or not previous<row['time']<=.0001802+1e-12:raise ValueError('Wrong moving-CFD time/schema')
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


def execute(previous,work,solver):
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
    if b'M247_MOVING_CFD' not in solver.read_bytes():raise ValueError('Solver rebuild required: missing moving-CFD marker')
    work.mkdir(parents=True,exist_ok=True);case=work/'movingCFD';case.mkdir()
    report=dict(schema=1,complete=False,production_approved=False,pilot_gate=False,
        original_protected_review_sha256=sha(previous/'movingWindowReview.json'),source_case=str(source),
        source_sha256=expected,solver_sha256=sha(solver),duration_us=.2,ranks=48,commands=[],
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
        for key,value in (('startFrom','startTime'),('startTime','0.00018'),('endTime','0.0001802'),
                          ('stopAt','endTime'),('writeInterval','1e-7'),('timePrecision','12'),
                          ('deltaT','1e-9'),('maxDeltaT','5e-9'),('adjustTimeStep','true'),
                          ('maxCo','0.1'),('maxAlphaCo','0.1'),
                          ('writePrecision','17'),('writeFormat','ascii'),('writeCompression','off'),
                          ('performanceDiagnostics','true'),('writeDiagnostics','true'),
                          ('thermalCorrectorLogging','true'),('runTimeModifiable','true'),('functions','{}')):
            set_entry(case/'system/controlDict',key,value)
        set_entry(case/'system/fvSolution','PIMPLE/correctPhi','true')
        set_entry(case/'system/fvSolution','PIMPLE/moveMeshOuterCorrectors','false')
        metadata=dict(schema=1,source=str(source),variant='movingCFD',start_s=.00018,end_s=.0001802,
            duration_us=.2,ranks=48,checkpoint='0.00018',source_snapshot_sha256=sha(previous/'movingWindowReview.json'),
            purpose='Experimental moving fine-window full-solver pilot; no measured speedup claim')
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
        provenance=json.loads((case/'run.json').read_text())
        if provenance.get('solver_sha256')!=report['solver_sha256']:raise ValueError('Launched solver binary differs from recorded rebuild')
        meta,summary,diagnostics=read_probe(case)
        text=(case/'log.vacuumLaserbeamFoam').read_text()
        mapping=mapping_gate(text);state=state_gate(text,mapping)
        report.update(pilot=summary,physical_diagnostics=diagnostics,moving_mapping=mapping,final_step_state=state,
            thermal_gate=summary['thermal_limit_hits']==0 and residual_gate(case,meta,summary['steps']))
        if abs(mapping['records'][-1]['time']-.0001802)>1e-12:raise ValueError('Mesh lifecycle did not reach pilot end time')
        if len(mapping['records'])!=summary['steps']:raise ValueError('Missing per-step mesh lifecycle records')
        if case_fingerprint(source)!=expected:raise ValueError('Original source changed')
        report.update(complete=True,source_unchanged_gate=True,pilot_gate=all((report['thermal_gate'],
            mapping['coverage_gate'],mapping['topology_gate'],mapping['mapping_screen'],state['continuity_screen'])))
        save();return report
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as error:
        report.update(error_type=type(error).__name__,error=str(error));save();raise


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous','work','solver'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    try:
        r=execute(a.previous,a.work,a.solver)
        print('Moving CFD compatibility pilot gate:',r['pilot_gate'],'production approved: False')
        if not r['pilot_gate']:p.exit(2,'Pilot screen failed; send review archive.\n')
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as e:p.exit(1,f'Moving CFD pilot failed: {e}\n')
if __name__=='__main__':main()
