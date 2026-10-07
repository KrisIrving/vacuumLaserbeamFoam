#!/usr/bin/env python3
"""One optical update on shared frozen inputs; original vs weighted partition."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from prepare_probe import prepare, set_entry
from ray_partition import native, mesh_digest, write_weights, require_initial_equal
from collect_thermal_validation import field_differences, final_state
from collect_probe import parse_records
from collect_laser_profile import summarize, validate_rank_rows

NAMES=('frozenLaserReference','frozenLaserWeighted')
INPUTS=('frozenAlphaInput','frozenNormalInput','frozenResistivityInput')
OUTPUTS=('Deposition','rayQ')
TIME=.00018

def input_digest(case):
    state=final_state(case,None,TIME)
    h=hashlib.sha256()
    for name in INPUTS:
        h.update(name.encode());h.update((state/name).read_bytes())
    return h.hexdigest()

def check_inputs(reference,candidate):
    if mesh_digest(reference)!=mesh_digest(candidate): raise ValueError('Global mesh changed')
    fields=field_differences(reference,candidate,None,TIME,field_names=INPUTS,vector_fields=('frozenNormalInput',))
    if any(f['max_abs_difference']!=0 for f in fields):
        raise ValueError('Frozen optical inputs changed during repartition')
    return dict(passed=True,fields=fields,mesh_sha256=mesh_digest(reference),
        shared_input_sha256=input_digest(reference))

def read_trace(case,expected):
    meta=json.loads((case/'probe.json').read_text())
    run=json.loads((case/'run.json').read_text())
    if (meta['variant']!=expected or meta['ranks']!=48 or meta.get('frozen_optics') is not True
        or abs(meta.get('frozen_time_s',-1)-TIME)>1e-12
        or not meta.get('cached_ray_traversal') or meta.get('cartesian_ray_seed_search')
        or not meta.get('laser_performance_diagnostics')):
        raise ValueError('Wrong fixed-state controls')
    if (run['returncode']!=0 or run.get('wall_budget_stop') or run.get('forced_stop')
        or not math.isfinite(run['elapsed_wall_s']) or run['elapsed_wall_s']<=0):
        raise ValueError('Incomplete fixed-state job')
    text=(case/'log.vacuumLaserbeamFoam').read_text()
    if not re.search(r'^End\s*$',text,re.M) or re.search(r'^Time\s*=',text,re.M):
        raise ValueError('Missing end or unexpected time advancement')
    for prefix in ('PERF_DIAGNOSTICS','THERMAL_RESIDUAL_DIAGNOSTICS','FROZEN_LASER_CAPTURE'):
        if parse_records(text,prefix): raise ValueError('Unexpected transient/capture records')
    if parse_records(text,'RAY_TRAVERSAL_DIAGNOSTICS')!=[dict(schema=1,cached=1)] or parse_records(text,'CARTESIAN_SEED_DIAGNOSTICS')!=[dict(schema=1,enabled=0)]:
        raise ValueError('Wrong runtime ray mode')
    if meta.get('preserve_ray_handoff_sample'):
        if parse_records(text,'RAY_HANDOFF_DIAGNOSTICS')!=[dict(schema=1,enabled=1)]:
            raise ValueError('Missing handoff correction mode')
        handoffs=parse_records(text,'RAY_HANDOFF_WORK')
        if (len(handoffs)!=1 or handoffs[0].get('schema')!=1
            or abs(handoffs[0].get('time',-1)-TIME)>1e-12
            or not 0<handoffs[0].get('resumed',-1)<=handoffs[0].get('crossings',-1)):
            raise ValueError('Missing/invalid handoff work')
    rows=parse_records(text,'FROZEN_LASER_DIAGNOSTICS')
    if len(rows)!=1: raise ValueError('Exactly one frozen update required')
    row=rows[0]
    if row.get('schema')!=1 or abs(row.get('time',-1)-TIME)>1e-12 or row.get('calls')!=1:
        raise ValueError('Wrong frozen diagnostic')
    if any(row.get(k)!=0 for k in ('advancedTime','Tchange','alphaChange','epsilonChange','Uchange')):
        raise ValueError('Frozen state evolved')
    if not math.isfinite(row.get('depositedPower',float('nan'))) or row['depositedPower']<=0:
        raise ValueError('Invalid deposited power')
    records=parse_records(text,'LASER_PERF_DIAGNOSTICS')
    if len(records)!=1: raise ValueError('Exactly one laser profile required')
    profile=summarize(records,[TIME],48,1)
    profile['rank_totals']=validate_rank_rows(parse_records(text,'LASER_RANK_DIAGNOSTICS'),records,48)
    if profile['counts']['callsMean']!=1 or profile['counts']['initialRaysMean']!=1536:
        raise ValueError('Frozen ray sampling changed')
    return meta,run,row,profile

def collect(work):
    cases=[work/n for n in NAMES]
    initial=json.loads((work/'initialPartitionCheck.json').read_text())
    inputs=json.loads((work/'frozenInputCheck.json').read_text())
    if not initial.get('passed') or not inputs.get('passed'): raise ValueError('Missing initial/input gate')
    data=[read_trace(c,n) for c,n in zip(cases,NAMES)]
    capture=json.loads((cases[0]/'captureRun.json').read_text())
    capture_text=(cases[0]/'capture.log').read_text()
    if (capture['returncode']!=0 or capture.get('wall_budget_stop') or capture.get('forced_stop')
        or parse_records(capture_text,'FROZEN_LASER_CAPTURE')!=[dict(schema=1,time=TIME,calls=0)]
        or parse_records(capture_text,'LASER_PERF_DIAGNOSTICS')
        or not re.search(r'^End\s*$',capture_text,re.M) or re.search(r'^Time\s*=',capture_text,re.M)):
        raise ValueError('Invalid optical input capture')
    for key in ('source_snapshot_sha256','source','checkpoint'):
        if data[0][0][key]!=data[1][0][key]: raise ValueError('Input provenance mismatch')
    modes=[bool(d[0].get('preserve_ray_handoff_sample')) for d in data]
    if modes[0]!=modes[1]: raise ValueError('Handoff controls differ')
    if modes[0] and parse_records((work/'partition.log').read_text(),'RAY_PACKET_TEST')!=[dict(schema=1,failures=0)]:
        raise ValueError('Missing MPI ray packet check')
    for key in ('solver_sha256','laser_library_sha256'):
        if not data[0][1].get(key) or data[0][1][key]!=data[1][1].get(key): raise ValueError('Binary mismatch')
        if capture.get(key)!=data[0][1][key]: raise ValueError('Capture binary mismatch')
    for case in cases:
        if mesh_digest(case)!=inputs['mesh_sha256']: raise ValueError('Mesh changed after tracing')
    after=check_inputs(*cases)
    if after['shared_input_sha256']!=inputs['shared_input_sha256']: raise ValueError('Reference inputs modified')
    fields=field_differences(*cases,None,TIME,field_names=OUTPUTS)
    for f in fields:
        f['allowed_difference']=1e-12+1e-8*f['reference_max_abs']
        f['passed']=f['max_abs_difference']<=f['allowed_difference']
    powers=[d[2]['depositedPower'] for d in data]
    delta=abs(powers[1]-powers[0]);allowed=1e-12+1e-8*abs(powers[0])
    result=dict(schema=1,frozen_time_s=TIME,transient_steps=0,production_approved=False,
        preserve_ray_handoff_sample=modes[0],
        handoff_work=[parse_records((c/'log.vacuumLaserbeamFoam').read_text(),'RAY_HANDOFF_WORK') for c in cases],
        optical_partition_gate=all(f['passed'] for f in fields) and delta<=allowed,
        fields=fields,deposited_power_W=powers,power_absolute_difference_W=delta,
        power_allowed_difference_W=allowed,initial_partition_check=initial,frozen_input_check=inputs,
        reference_laser_profile=data[0][3],laser_profile=data[1][3],
        job_wall_s=[d[1]['elapsed_wall_s'] for d in data],capture_run=capture,
        note='Diagnostic only. Identical shared internal optical inputs; no flow, thermal or time advancement. Strict spatial/energy gates retained. Timing includes startup and is not full-CFD speedup.')
    output=work/'comparison';output.mkdir()
    (output/'frozenLaserReview.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Frozen optical partition gate:',result['optical_partition_gate'],flush=True)
    print('Deposited power W:',*powers,'difference:',delta,flush=True)
    return result

def job(case,mode):
    set_entry(case/'system/controlDict','frozenLaserProbe',mode)
    subprocess.run([sys.executable,str(Path(__file__).with_name('run_probe.py')),
        '--case',str(case),'--wall-hours',str(5/60)],check=True)

def run(work,source,preserve_samples=False):
    if os.name!='posix': raise ValueError('Run on Ubuntu OpenFOAM host')
    cases=[]
    for name in NAMES:
        case=work/name;meta=prepare(source,case,180,2,name)
        if meta['ranks']!=48 or (case/'constant/dynamicMeshDict').exists():
            raise ValueError('Original fixed mesh and 48 ranks required')
        meta.update(frozen_optics=True,frozen_time_s=TIME,
            preserve_ray_handoff_sample=preserve_samples,
            purpose='Fixed-state optical comparison; duration/end metadata are copy-helper bounds, not simulated interval')
        (case/'probe.json').write_text(json.dumps(meta,indent=2)+'\n')
        set_entry(case/'system/controlDict','writePrecision',17)
        set_entry(case/'system/controlDict','writeCompression','off')
        mesh_digest(case)
        native(work,['reconstructPar','-case',str(case),'-time','0.00018'])
        cases.append(case)
    if preserve_samples:
        native(work,['timeout','--kill-after=30s','240s','mpirun','-np','48',str(Path(os.environ['FOAM_USER_APPBIN'])/'m247CachedSearchTest'),
            '-parallel','-case',str(cases[0])])
    for case in cases:
        set_entry(case/'constant/LaserProperties','preserveRayHandoffSample','true' if preserve_samples else 'false')
    # Use the checkpoint rayQ before overwriting any optical outputs.
    stats=write_weights(cases[1],TIME)
    (work/'partitionWeight.json').write_text(json.dumps(stats,indent=2)+'\n')
    job(cases[0],'capture')
    for old,new in (('log.vacuumLaserbeamFoam','capture.log'),('run.json','captureRun.json')):
        (cases[0]/old).rename(cases[0]/new)
    native(work,['reconstructPar','-case',str(cases[0]),'-time','0.00018','-fields','('+' '.join(INPUTS)+')'])
    for name in INPUTS:
        shutil.copy2(final_state(cases[0],None,TIME)/name,final_state(cases[1],None,TIME)/name)
    dictionary=cases[1]/'system/decomposeParDict'
    set_entry(dictionary,'method','scotch');set_entry(dictionary,'numberOfSubdomains',48)
    set_entry(dictionary,'weightField','rayWorkWeight')
    native(work,['decomposePar','-case',str(cases[1]),'-force','-time','0.00018'])
    native(work,['reconstructPar','-case',str(cases[1]),'-time','0.00018'])
    (work/'initialPartitionCheck.json').write_text(json.dumps(require_initial_equal(*cases),indent=2)+'\n')
    (work/'frozenInputCheck.json').write_text(json.dumps(check_inputs(*cases),indent=2)+'\n')
    for case in cases:
        print('One frozen laser update:',case.name,'at 180 us; five-minute job budget',flush=True)
        job(case,'trace')
        native(work,['reconstructPar','-case',str(case),'-time','0.00018','-fields','('+' '.join(INPUTS+OUTPUTS)+')'])
    collect(work)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--preserve-samples',action='store_true')
    args=parser.parse_args()
    try: run(args.work.resolve(),args.source.resolve(),args.preserve_samples)
    except (ValueError,OSError,KeyError,OverflowError,subprocess.SubprocessError) as error:
        parser.exit(1,f'Frozen optical diagnostic failed: {error}\n')
if __name__=='__main__': main()
