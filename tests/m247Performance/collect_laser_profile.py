#!/usr/bin/env python3
"""Validate profiling equivalence and summarise additive laser stages."""
import argparse
import csv
import json
import math
from pathlib import Path
from collect_probe import read_probe, compare, parse_records
from collect_thermal_validation import field_differences, residual_gate, final_state

STAGES=('seedGenerate','seedExchange','seedLocate','ownership','trace','exchange','finalize','other')
COUNTS=('callsMean','initialRaysMean','exchangeRoundsMean','ownershipChecksSum','localSegmentsSum',
        'advancesSum','traceSearchCallsSum','interfaceEventsSum','bulkEventsSum',
        'mergeCallsSum','mergeXRaysSum','mergeYRaysSum','mergeAppendsSum')
DETAILS=('exchangeCopy','gather','broadcast','merge')
RANK_COUNTS={'advances':'advancesSum','segments':'localSegmentsSum','searches':'traceSearchCallsSum',
             'interfaceEvents':'interfaceEventsSum','bulkEvents':'bulkEventsSum','mergeCalls':'mergeCallsSum',
             'mergeXRays':'mergeXRaysSum','mergeYRays':'mergeYRaysSum','mergeAppends':'mergeAppendsSum'}

def summarize(records, times, ranks, steps):
    required=('schema','time','ranks','total_s','totalMax_s','traceSearchSampleSum_s',
              'traceSearchSamplesSum','searchSampleStride')+COUNTS+tuple(k+s for k in STAGES+DETAILS for s in ('_s','Max_s'))
    if not records or sorted(set(r.get('time',-1) for r in records)) != times:
        raise ValueError('Laser profiling samples do not cover diagnostic output times')
    if any(a['time']>b['time'] for a,b in zip(records,records[1:])):
        raise ValueError('Laser profiling records are not chronological')
    for row in records:
        if any(k not in row for k in required) or row['schema']!=2 or row['ranks']!=ranks:
            raise ValueError('Incomplete/mismatched laser profiling record')
        if row['searchSampleStride']!=128 or row['total_s']<=0 or row['callsMean']<=0:
            raise ValueError('Invalid laser profiling totals')
        if any(row[k]<0 for k in required if k not in ('time','schema')):
            raise ValueError('Negative laser profiling values')
        if abs(sum(row[k+'_s'] for k in STAGES)-row['total_s'])>max(1e-5,row['total_s']*1e-4):
            raise ValueError('Laser mean stages do not reconcile')
        if row['totalMax_s']<row['total_s']*(1-1e-5) or any(row[k+'Max_s']<row[k+'_s']*(1-1e-5) for k in STAGES+DETAILS):
            raise ValueError('Laser rank maximum below rank mean')
        if abs(row['traceSearchCallsSum']-row['advancesSum']-row['localSegmentsSum'])>0.5:
            raise ValueError('Laser search/work counters do not reconcile')
        if row['traceSearchSamplesSum']>row['traceSearchCallsSum']:
            raise ValueError('Too many sampled searches')
        if row['traceSearchSampleSum_s']>row['trace_s']*ranks+1e-5:
            raise ValueError('Sampled search time exceeds enclosing trace')
        if sum(row[k+'_s'] for k in DETAILS[:3])>row['exchange_s']+max(1e-5,row['exchange_s']*1e-4):
            raise ValueError('Exchange child times exceed parent')
        if row['merge_s']>row['gather_s']+max(1e-5,row['gather_s']*1e-4):
            raise ValueError('Merge time exceeds enclosing gather')
        if row['mergeAppendsSum']>row['mergeYRaysSum']:
            raise ValueError('Merge work counters do not reconcile')
    counts={k:sum(r[k] for r in records) for k in COUNTS}
    if counts['callsMean']<steps:
        raise ValueError('Laser profile does not cover all solver steps')
    total=sum(r['total_s'] for r in records)
    stages=[dict(stage=k,mean_s=sum(r[k+'_s'] for r in records),
                 mean_fraction=sum(r[k+'_s'] for r in records)/total,
                 interval_rank_max_sum_s=sum(r[k+'Max_s'] for r in records)) for k in STAGES]
    samples=sum(r['traceSearchSamplesSum'] for r in records)
    details=[dict(detail=k,mean_s=sum(r[k+'_s'] for r in records),
                  fraction_of_exchange=sum(r[k+'_s'] for r in records)/sum(r['exchange_s'] for r in records)
                    if sum(r['exchange_s'] for r in records)>0 else None,
                  interval_rank_max_sum_s=sum(r[k+'Max_s'] for r in records)) for k in DETAILS]
    return dict(mean_total_s=total,interval_rank_max_sum_s=sum(r['totalMax_s'] for r in records),
                stages=stages,exchange_details=details,counts=counts,trace_search_sample_sum_s=sum(r['traceSearchSampleSum_s'] for r in records),
                trace_search_samples_sum=samples,
                sampled_search_mean_s=(sum(r['traceSearchSampleSum_s'] for r in records)/samples if samples else None),
                note='Only MPI mean stages add. Exchange copy/gather/broadcast are children of exchange; merge is nested inside gather. Blocking gather/broadcast include waiting, not pure transport. Rank maxima are not additive. Search time is a stride-128 sample inside trace, not a separate stage or an unbiased total estimate. Replicated calls/rays/rounds use means; local work uses sums. Outer field reset/dictionary work and profiling report reductions are outside this inner-call total.')

def validate_rank_rows(rows, records, ranks):
    if not records or ranks<1 or len(rows)!=len(records)*ranks:
        raise ValueError('Incomplete laser rank records')
    groups=[]
    # Preserve output-group order to support multiple PIMPLE calls at one time.
    for index,record in enumerate(records):
        group=rows[index*ranks:(index+1)*ranks]
        if sorted(r.get('rank',-1) for r in group)!=list(range(ranks)):
            raise ValueError('Duplicate/missing laser rank IDs')
        required=('schema','time','rank','calls','rounds')+tuple(k+'_s' for k in ('trace','ownership','exchange')+DETAILS)+tuple(RANK_COUNTS)
        for row in group:
            if any(k not in row for k in required) or row['schema']!=2 or abs(row['time']-record['time'])>1e-12:
                raise ValueError('Mismatched laser rank record')
            if any(row[k]<0 for k in required if k!='time'):
                raise ValueError('Negative laser rank record')
            if abs(row['searches']-row['segments']-row['advances'])>0.5:
                raise ValueError('Rank search counters do not reconcile')
            if row['mergeAppends']>row['mergeYRays']:
                raise ValueError('Rank merge counters do not reconcile')
            if sum(row[k+'_s'] for k in DETAILS[:3])>row['exchange_s']+max(1e-5,row['exchange_s']*1e-4) or row['merge_s']>row['gather_s']+max(1e-5,row['gather_s']*1e-4):
                raise ValueError('Rank nested exchange times do not reconcile')
        for k in ('trace','ownership','exchange')+DETAILS:
            average=sum(r[k+'_s'] for r in group)/ranks
            if abs(average-record[k+'_s'])>max(1e-5,record[k+'_s']*1e-4):
                raise ValueError('Rank times disagree with reported mean')
            if abs(max(r[k+'_s'] for r in group)-record[k+'Max_s'])>max(1e-5,record[k+'Max_s']*1e-4):
                raise ValueError('Rank times disagree with reported maximum')
        for k,aggregate in RANK_COUNTS.items():
            if abs(sum(r[k] for r in group)-record[aggregate])>0.5:
                raise ValueError('Rank counters disagree with sums')
        for local,aggregate in (('calls','callsMean'),('rounds','exchangeRoundsMean')):
            if any(abs(r[local]-record[aggregate])>0.5 for r in group):
                raise ValueError('Replicated rank counters disagree')
        groups.append(sorted(group,key=lambda r:r['rank']))
    return [dict(rank=rank,**{k:sum(group[rank][k] for group in groups)
                for k in required if k not in ('schema','time','rank')}) for rank in range(ranks)]

def corrected_work(text,meta,calls):
    if any(meta.get(k) is not True for k in ('preserve_ray_handoff_sample','consistent_ray_termination')):
        raise ValueError('Corrected ray metadata missing')
    for prefix in ('RAY_HANDOFF_DIAGNOSTICS','RAY_TERMINATION_DIAGNOSTICS'):
        if parse_records(text,prefix)!=[dict(schema=1,enabled=1)]:
            raise ValueError('Corrected ray runtime mode missing')
    handoff=parse_records(text,'RAY_HANDOFF_WORK');termination=parse_records(text,'RAY_TERMINATION_WORK')
    if len(handoff)!=calls or len(termination)!=calls or calls<=0:
        raise ValueError('Corrected ray work does not cover all laser calls')
    for index,(h,t) in enumerate(zip(handoff,termination)):
        if (h.get('schema')!=1 or t.get('schema')!=1 or h.get('time')!=t.get('time')
            or not meta['start_s']<h.get('time',-1)<=meta['end_s']+1e-12
            or (index and h['time']<=handoff[index-1]['time'])
            or not 0<=h.get('resumed',-1)<=h.get('crossings',-1)):
            raise ValueError('Invalid corrected work time or handoff counts')
        threshold=t.get('threshold',float('nan'));count=t.get('cutoffRays',float('nan'));power=t.get('discardedPower',float('nan'))
        if (not all(math.isfinite(v) for v in (threshold,count,power)) or threshold<=0
            or count!=int(count) or not 0<=count<=1536 or not 0<=power<=count*threshold+1e-12):
            raise ValueError('Invalid corrected discarded-power accounting')
    if abs(handoff[-1]['time']-meta['end_s'])>1e-12 or sum(h['resumed'] for h in handoff)<=0:
        raise ValueError('Corrected work interval incomplete')
    return dict(handoff=handoff,termination=termination)

def collect(work, traversal=False, validation=False, seed_search=False, corrected_rays=False):
    if corrected_rays and (not traversal or not validation or seed_search):
        raise ValueError('Corrected ray pair requires broader traversal validation')
    if seed_search and not traversal:
        raise ValueError('Seed search requires paired traversal collection')
    if validation and not traversal:
        raise ValueError('Validation mode requires the paired traversal cases')
    work=Path(work)
    names=('raySeedReference','raySeedCached') if seed_search else ('rayTraversalReference','rayTraversalCached') if traversal else ('laserProfileOff','laserProfileOn')
    cases=[work/v for v in names]
    probes=[read_probe(c) for c in cases]
    if corrected_rays and any(p[0]['ranks']!=48 for p in probes):
        raise ValueError('Corrected transient validation requires 48 ranks')
    if validation:
        for meta,_,_ in probes:
            if (abs(meta['start_s']-0.00018)>1e-12 or abs(meta['end_s']-0.000182)>1e-12
                or abs(meta['duration_us']-2)>1e-9):
                raise ValueError('Broader validation requires exactly 180–182 us (2 us)')
    comparison,diagnostics=compare(*probes)
    runs=[json.loads((c/'run.json').read_text()) for c in cases]
    for key in ('solver_sha256','laser_library_sha256'):
        if not runs[0].get(key) or runs[0][key]!=runs[1].get(key):
            raise ValueError('Unmatched solver/library provenance')
    converged=True
    for index,(case,probe,enabled) in enumerate(zip(cases,probes,(True,True) if traversal else (False,True))):
        meta=probe[0]
        if (meta.get('laser_performance_diagnostics') is not enabled
            or meta.get('phase_temperature_blend_half_width')!=0
            or meta.get('epsilon_tolerance')!=1e-5 or meta.get('phase_temperature_tolerance_K')!=0.001):
            raise ValueError('Laser probe requires matched tight controls, width zero and expected profile switch')
        if traversal:
            mode=parse_records((case/'log.vacuumLaserbeamFoam').read_text(),'RAY_TRAVERSAL_DIAGNOSTICS')
            cached=True if seed_search else bool(index)
            if meta.get('cached_ray_traversal') is not cached or len(mode)!=1 or mode[0].get('schema')!=1 or mode[0].get('cached')!=int(cached):
                raise ValueError('Missing/mismatched runtime cached traversal mode')
            seed_mode=parse_records((case/'log.vacuumLaserbeamFoam').read_text(),'CARTESIAN_SEED_DIAGNOSTICS')
            if seed_search:
                if (meta.get('cartesian_ray_seed_search') is not bool(index) or len(seed_mode)!=1
                    or seed_mode[0].get('schema')!=1 or seed_mode[0].get('enabled')!=index):
                    raise ValueError('Missing/mismatched Cartesian seed search mode')
            elif meta.get('cartesian_ray_seed_search',False) or any(r.get('enabled')!=0 for r in seed_mode):
                raise ValueError('Unexpected Cartesian seed search in traversal pair')
        if (case/'constant/dynamicMeshDict').exists(): raise ValueError('Only fixed M247 mesh supported')
        for rank in range(meta['ranks']):
            for folder in (case/f'processor{rank}').iterdir():
                if (folder/'polyMesh').is_dir():
                    try: time=float(folder.name)
                    except ValueError: continue
                    if time>meta['start_s']+1e-12: raise ValueError('Mesh changed in laser probe')
        converged=residual_gate(case,meta,probe[1]['steps']) and converged
        thermal=parse_records((case/'log.vacuumLaserbeamFoam').read_text(),'THERMAL_RESIDUAL_DIAGNOSTICS')
        if any('phaseBlendHalfWidth' not in r or abs(r['phaseBlendHalfWidth'])>1e-12 for r in thermal):
            raise ValueError('Laser profiling requires runtime phase width zero')
    off_text=(cases[0]/'log.vacuumLaserbeamFoam').read_text()
    if not traversal and any(parse_records(off_text,prefix) for prefix in ('LASER_PERF_DIAGNOSTICS','LASER_RANK_DIAGNOSTICS')):
        raise ValueError('Profiling-off case emitted laser profiling records')
    text=(cases[1]/'log.vacuumLaserbeamFoam').read_text()
    records=parse_records(text,'LASER_PERF_DIAGNOSTICS')
    profile=summarize(records,
                      [r['time'] for r in probes[1][2]],probes[1][0]['ranks'],probes[1][1]['steps'])
    rank_rows=validate_rank_rows(parse_records(text,'LASER_RANK_DIAGNOSTICS'),records,probes[1][0]['ranks'])
    profile['rank_totals']=rank_rows
    extra={}
    work_gate=True
    if traversal:
        parity=parse_records((work/'cachedSearchTest.log').read_text(),'CACHED_SEARCH_TEST')
        if len(parity)!=1 or parity[0].get('checks',0)<=0 or parity[0].get('mismatches',-1)!=0:
            raise ValueError('Cached search parity test missing or failed')
        if seed_search and (parity[0].get('cartesianChecks',0)<=0 or parity[0].get('fastAccepts',0)<=0 or parity[0].get('eligibleCells',0)<=0):
            raise ValueError('Cartesian seed shortcut not exercised by mesh parity test')
        ref_records=parse_records(off_text,'LASER_PERF_DIAGNOSTICS')
        reference_profile=summarize(ref_records,[r['time'] for r in probes[0][2]],probes[0][0]['ranks'],probes[0][1]['steps'])
        reference_profile['rank_totals']=validate_rank_rows(parse_records(off_text,'LASER_RANK_DIAGNOSTICS'),ref_records,probes[0][0]['ranks'])
        work_gate=(len(ref_records)==len(records) and all(a['time']==b['time'] and all(a[k]==b[k] for k in COUNTS) for a,b in zip(ref_records,records))
                   and all(all(a[k]==b[k] for k in RANK_COUNTS) for a,b in zip(reference_profile['rank_totals'],rank_rows)))
        extra=dict(reference_laser_profile=reference_profile,work_counter_gate=work_gate,search_parity_test=parity[0])
    selected_fields=('T','epsilon1','alpha.metal','U','p_rgh','Deposition','rayQ') if traversal else ('T','epsilon1','alpha.metal','U','p_rgh')
    if traversal:
        # The inherited rayNumber visualisation is NO_WRITE unless debug is on.
        # Never enable debug here: it changes the candidate lookup path.
        present=[]
        for case in cases:
            for rank in range(probes[0][0]['ranks']):
                state=final_state(case,rank,probes[0][0]['end_s'])
                present.append((state/'rayNumber').is_file() or (state/'rayNumber.gz').is_file())
        if any(present) and not all(present):
            raise ValueError('Partially available rayNumber outputs: require both cases and all ranks')
        if all(present): selected_fields+=('rayNumber',)
        extra['ray_number_comparison']=dict(status='compared' if all(present) else 'not_written',
            reason='Optional visual ray ID field; inherited solver uses NO_WRITE without debug. Seven physical/deposition fields remain mandatory.')
    fields=field_differences(*cases,probes[0][0]['ranks'],probes[0][0]['end_s'],field_names=selected_fields)
    for row in fields:
        row['allowed_difference']=1e-12+1e-8*row['reference_max_abs']
        row['passed']=row['max_abs_difference']<=row['allowed_difference']
    result=dict(schema=1,regression_gate=converged and comparison['thermal_limit_gate']
                and comparison['diagnostic_pass'] and work_gate and all(f['passed'] for f in fields),
                production_approved=False,comparison=comparison,laser_profile=profile,fields=fields,
                profiling_job_overhead_ratio=runs[1]['elapsed_wall_s']/runs[0]['elapsed_wall_s'],
                note='Instrumentation equivalence only; no speedup or physical closure approval is implied.')
    result.update(extra)
    if corrected_rays:
        packet=parse_records((work/'cachedSearchTest.log').read_text(),'RAY_PACKET_TEST')
        if packet!=[dict(schema=1,failures=0)]: raise ValueError('MPI ray packet check missing or failed')
        corrected=[]
        for case,probe in zip(cases,probes):
            txt=(case/'log.vacuumLaserbeamFoam').read_text()
            rows=parse_records(txt,'LASER_PERF_DIAGNOSTICS')
            if any(r['initialRaysMean']!=1536*r['callsMean'] for r in rows): raise ValueError('Corrected ray sampling changed')
            calls=sum(r['callsMean'] for r in rows)
            if calls!=probe[1]['steps']: raise ValueError('Requires one laser call per step')
            corrected.append(corrected_work(txt,probe[0],calls))
        result['corrected_ray_work']=corrected
        result['corrected_ray_work_gate']=corrected[0]==corrected[1]
        result['regression_gate']=result['regression_gate'] and result['corrected_ray_work_gate']
        result['corrected_rays']=True
    if traversal:
        result['validation_scope']='180-182us' if validation else 'paired traversal'
        result['optimization']='cartesian seed interior' if seed_search else 'cached traversal'
        result['performance_gate']=(result['regression_gate'] and comparison['solver_loop_speedup']>=1.05 and comparison['job_wall_speedup']>=1.05)
        result['note']='Cached traversal candidate: require identical ray work, field/diagnostic regression and measured speedup. One short pair does not establish long-track performance or physical approval.'
        if corrected_rays:
            result['note']+=' Both cases enable sample handoff and consistent termination on the original partition. This compares cache off/on within corrected physics; it does not validate the correction against legacy physics or promote weighted partitioning.'
    output=work/'comparison'
    if output.exists(): raise ValueError('Comparison directory already exists')
    output.mkdir()
    (output/('rayTraversalReview.json' if traversal else 'laserProfileReview.json')).write_text(json.dumps(result,indent=2)+'\n')
    for name,rows in (('laserProfileStages.csv',profile['stages']),('laserExchangeDetails.csv',profile['exchange_details']),
                      ('laserRankWork.csv',rank_rows),('laserProfileFields.csv',fields),('diagnosticComparison.csv',diagnostics)):
        with (output/name).open('x',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--ray-traversal',action='store_true')
    parser.add_argument('--validation',action='store_true',help='Require the broader 180–182-us traversal pair')
    parser.add_argument('--seed-search',action='store_true')
    parser.add_argument('--corrected-rays',action='store_true')
    args=parser.parse_args()
    try: result=collect(args.work,args.ray_traversal,args.validation,args.seed_search,args.corrected_rays)
    except (ValueError,OSError,KeyError) as error: parser.exit(1,f'Laser profile collection failed: {error}\n')
    print(f"Profiling equivalence gate: {result['regression_gate']}")
    if args.ray_traversal:
        print(f"Loop/job speedup: {result['comparison']['solver_loop_speedup']:.3f}/{result['comparison']['job_wall_speedup']:.3f}")
        print(f"Matched ray work: {result['work_counter_gate']}; performance gate (>=5%): {result['performance_gate']}")
    else: print(f"Profiling job overhead ratio: {result['profiling_job_overhead_ratio']:.3f}")
    for row in sorted(result['laser_profile']['stages'],key=lambda r:r['mean_s'],reverse=True):
        print(f"  {row['stage']}: {row['mean_s']:.3f} s, {100*row['mean_fraction']:.2f}%")
    for row in result['laser_profile']['exchange_details']:
        print(f"  exchange/{row['detail']}: {row['mean_s']:.3f} s")
    print('Merge is nested inside gather; blocking gather/broadcast include waiting.')
    if not result['regression_gate']: parser.exit(2,'Instrumentation regression gate failed.\n')

if __name__=='__main__': main()
