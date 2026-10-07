#!/usr/bin/env python3
"""Matched fixed-mesh ray-weighted Scotch experiment; no solver modification."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from prepare_probe import prepare, set_entry
from collect_probe import read_probe, compare, parse_records
from collect_thermal_validation import field_differences, read_field, final_state, residual_gate
from collect_laser_profile import summarize, validate_rank_rows

NAMES=('rayPartitionReference','rayPartitionWeighted')
FIELDS=('T','epsilon1','alpha.metal','U','p_rgh','Deposition','rayQ')

def weights(values):
    if not values or any(not math.isfinite(q) or q<0 for q in values):
        raise ValueError('rayQ must have finite non-negative cell values')
    mean=math.fsum(values)/len(values)
    if not math.isfinite(mean) or mean<=0:
        raise ValueError('Checkpoint rayQ contains no usable ray work')
    result=[1+q/mean for q in values]
    if any(not math.isfinite(w) for w in result): raise ValueError('Invalid decomposition weight')
    return result,dict(cells=len(values),active_cells=sum(q>0 for q in values),
        rayQ_mean=mean,min_weight=min(result),max_weight=max(result),mean_weight=math.fsum(result)/len(result),
        formula='1 + rayQ / mean(rayQ)',note='Power-weighted path proxy, not measured cell search cost. Base cell work and ray proxy have equal total weight.')

def mesh_digest(case):
    mesh=case/'constant/polyMesh'
    h=hashlib.sha256()
    for name in ('points','faces','owner','neighbour','boundary'):
        p=mesh/name
        if not p.is_file(): p=p.with_name(name+'.gz')
        h.update(name.encode());h.update(p.read_bytes())
    return h.hexdigest()

def write_weights(case, time):
    field=final_state(case,None,time)/'rayQ'
    values,components,uniform=read_field(field)
    if components!=1 or uniform: raise ValueError('Nonuniform scalar checkpoint rayQ required')
    result,stats=weights(values)
    if not field.is_file():
        import gzip
        text=gzip.open(field.with_name('rayQ.gz'),'rt').read()
    else: text=field.read_text()
    text=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
    boundary=re.search(r'\bboundaryField\s*\{',text)
    if boundary is None: raise ValueError('Checkpoint rayQ boundary dictionary missing')
    output=field.with_name('rayWorkWeight')
    output.write_text('FoamFile { version 2.0; format ascii; class volScalarField; object rayWorkWeight; }\n'
        'dimensions [0 0 0 0 0 0 0];\ninternalField nonuniform List<scalar>\n'
        +str(len(result))+'\n(\n'+'\n'.join(format(w,'.17g') for w in result)+'\n);\n'+text[boundary.start():])
    stats['weight_sha256']=hashlib.sha256(output.read_bytes()).hexdigest()
    return stats

def native(work, command):
    with (work/'partition.log').open('a') as log:
        log.write('\nCOMMAND '+json.dumps(command)+'\n');log.flush()
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=300)

def require_initial_equal(reference,candidate):
    if mesh_digest(reference)!=mesh_digest(candidate): raise ValueError('Global mesh/order changed')
    fields=field_differences(reference,candidate,None,.00018,field_names=FIELDS)
    if any(f['max_abs_difference']!=0 for f in fields):
        raise ValueError('Repartition changed initial fields; refuse CFD')
    return dict(passed=True,mesh_sha256=mesh_digest(reference),fields=fields,
        note='Reconstructed initial internal fields; original global mesh/order retained. All native restart fields were reconstructed/decomposed.')

def collect(work):
    cases=[work/n for n in NAMES];probes=[read_probe(c) for c in cases]
    comparison,diagnostics=compare(*probes)
    initial=json.loads((work/'initialPartitionCheck.json').read_text())
    if initial.get('passed') is not True: raise ValueError('Initial partition verification missing')
    runs=[json.loads((c/'run.json').read_text()) for c in cases]
    for key in ('solver_sha256','laser_library_sha256'):
        if not runs[0].get(key) or runs[0][key]!=runs[1].get(key): raise ValueError('Unmatched binaries')
    profiles=[];thermal=True
    for name,case,probe in zip(NAMES,cases,probes):
        meta=probe[0]
        if (meta['variant']!=name or meta['ranks']!=48 or abs(meta['start_s']-.00018)>1e-12
            or abs(meta['end_s']-.000182)>1e-12 or meta['cached_ray_traversal'] is not True
            or meta['cartesian_ray_seed_search'] is not False or meta['laser_performance_diagnostics'] is not True
            or meta['epsilon_tolerance']!=1e-5 or meta['phase_temperature_tolerance_K']!=.001
            or meta['phase_temperature_blend_half_width']!=0): raise ValueError('Unmatched partition controls')
        if (case/'constant/dynamicMeshDict').exists() or mesh_digest(case)!=initial['mesh_sha256']:
            raise ValueError('Only unchanged global fixed mesh supported')
        text=(case/'log.vacuumLaserbeamFoam').read_text()
        if parse_records(text,'RAY_TRAVERSAL_DIAGNOSTICS')!=[dict(schema=1,cached=1)] or parse_records(text,'CARTESIAN_SEED_DIAGNOSTICS')!=[dict(schema=1,enabled=0)]:
            raise ValueError('Unexpected runtime ray mode')
        thermal=residual_gate(case,meta,probe[1]['steps']) and thermal
        if any(r.get('phaseBlendHalfWidth')!=0 for r in parse_records(text,'THERMAL_RESIDUAL_DIAGNOSTICS')):
            raise ValueError('Runtime phase width changed')
        records=parse_records(text,'LASER_PERF_DIAGNOSTICS')
        profile=summarize(records,[r['time'] for r in probe[2]],48,probe[1]['steps'])
        profile['rank_totals']=validate_rank_rows(parse_records(text,'LASER_RANK_DIAGNOSTICS'),records,48)
        rows=profile['rank_totals'];mean=sum(r['trace_s'] for r in rows)/48
        profile['trace_max_over_mean']=max(r['trace_s'] for r in rows)/mean if mean else None
        profile['inactive_search_ranks']=sum(r['searches']==0 for r in rows)
        profiles.append(profile)
    rays=[p['counts']['initialRaysMean']/p['counts']['callsMean'] for p in profiles]
    if any(abs(n-1536)>1e-9 for n in rays): raise ValueError('Ray sampling changed')
    fields=field_differences(*cases,None,.000182,field_names=FIELDS)
    for row in fields:
        row['allowed_difference']=1e-12+1e-8*row['reference_max_abs']
        row['passed']=row['max_abs_difference']<=row['allowed_difference']
    regression=thermal and comparison['thermal_limit_gate'] and comparison['diagnostic_pass'] and all(f['passed'] for f in fields)
    result=dict(schema=1,regression_gate=regression,production_approved=False,comparison=comparison,
        performance_gate=regression and comparison['job_wall_speedup']>=1.05 and comparison['solver_loop_speedup']>=1.05,
        reference_laser_profile=profiles[0],laser_profile=profiles[1],fields=fields,initial_partition_check=initial,
        note='Repartition sensitivity: compare on original global mesh, not processor-local indices. Per-rank/advance/exchange work may change. Strict cache-scale field/diagnostic tolerances retained; no physical approximation approval.')
    output=work/'comparison';output.mkdir()
    (output/'rayPartitionReview.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Partition regression:',regression,'performance:',result['performance_gate'],flush=True)
    print('Loop/job speedup:',comparison['solver_loop_speedup'],comparison['job_wall_speedup'],flush=True)
    print('Trace max/mean:',*[p['trace_max_over_mean'] for p in profiles],flush=True)
    return result

def run(work,source):
    if os.name!='posix': raise ValueError('Run this on the Ubuntu OpenFOAM host')
    cases=[]
    for name in NAMES:
        case=work/name;meta=prepare(source,case,180,2,name)
        if meta['ranks']!=48: raise ValueError('This matched benchmark requires 48 ranks')
        if (case/'constant/dynamicMeshDict').exists(): raise ValueError('Fixed mesh required')
        set_entry(case/'system/controlDict','writePrecision',17)
        set_entry(case/'system/controlDict','writeCompression','off')
        mesh_digest(case)  # Require original serial mesh/address ordering.
        native(work,['reconstructPar','-case',str(case),'-time','0.00018'])
        cases.append(case)
    stats=write_weights(cases[1],.00018)
    (work/'partitionWeight.json').write_text(json.dumps(stats,indent=2)+'\n')
    dictionary=cases[1]/'system/decomposeParDict'
    set_entry(dictionary,'method','scotch');set_entry(dictionary,'numberOfSubdomains',48)
    set_entry(dictionary,'weightField','rayWorkWeight')
    native(work,['decomposePar','-case',str(cases[1]),'-force','-time','0.00018'])
    native(work,['reconstructPar','-case',str(cases[1]),'-time','0.00018'])
    initial=require_initial_equal(*cases)
    (work/'initialPartitionCheck.json').write_text(json.dumps(initial,indent=2)+'\n')
    for case in cases:
        print('Running',case.name,'180–182 us; 30-minute CFD budget',flush=True)
        subprocess.run([sys.executable,str(Path(__file__).with_name('run_probe.py')),
            '--case',str(case),'--wall-hours','.5'],check=True)
        native(work,['reconstructPar','-case',str(case),'-time','0.000182','-fields','('+' '.join(FIELDS)+')'])
    collect(work)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True);parser.add_argument('--source',type=Path,required=True)
    args=parser.parse_args()
    try: run(args.work.resolve(),args.source.resolve())
    except (ValueError,OSError,KeyError,OverflowError,subprocess.SubprocessError) as error:
        parser.exit(1,f'Ray partition experiment failed: {error}\n')
if __name__=='__main__': main()
