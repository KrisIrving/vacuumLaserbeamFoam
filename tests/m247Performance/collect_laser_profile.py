#!/usr/bin/env python3
"""Validate profiling equivalence and summarise additive laser stages."""
import argparse
import csv
import json
from pathlib import Path
from collect_probe import read_probe, compare, parse_records
from collect_thermal_validation import field_differences, residual_gate

STAGES=('seedGenerate','seedExchange','seedLocate','ownership','trace','exchange','finalize','other')
COUNTS=('callsMean','initialRaysMean','exchangeRoundsMean','ownershipChecksSum','localSegmentsSum',
        'advancesSum','traceSearchCallsSum','interfaceEventsSum','bulkEventsSum')

def summarize(records, times, ranks, steps):
    required=('schema','time','ranks','total_s','totalMax_s','traceSearchSampleSum_s',
              'traceSearchSamplesSum','searchSampleStride')+COUNTS+tuple(k+s for k in STAGES for s in ('_s','Max_s'))
    if not records or sorted(set(r.get('time',-1) for r in records)) != times:
        raise ValueError('Laser profiling samples do not cover diagnostic output times')
    if any(a['time']>b['time'] for a,b in zip(records,records[1:])):
        raise ValueError('Laser profiling records are not chronological')
    for row in records:
        if any(k not in row for k in required) or row['schema']!=1 or row['ranks']!=ranks:
            raise ValueError('Incomplete/mismatched laser profiling record')
        if row['searchSampleStride']!=128 or row['total_s']<=0 or row['callsMean']<=0:
            raise ValueError('Invalid laser profiling totals')
        if any(row[k]<0 for k in required if k not in ('time','schema')):
            raise ValueError('Negative laser profiling values')
        if abs(sum(row[k+'_s'] for k in STAGES)-row['total_s'])>max(1e-5,row['total_s']*1e-4):
            raise ValueError('Laser mean stages do not reconcile')
        if row['totalMax_s']<row['total_s']*(1-1e-5) or any(row[k+'Max_s']<row[k+'_s']*(1-1e-5) for k in STAGES):
            raise ValueError('Laser rank maximum below rank mean')
        if abs(row['traceSearchCallsSum']-row['advancesSum']-row['localSegmentsSum'])>0.5:
            raise ValueError('Laser search/work counters do not reconcile')
        if row['traceSearchSamplesSum']>row['traceSearchCallsSum']:
            raise ValueError('Too many sampled searches')
        if row['traceSearchSampleSum_s']>row['trace_s']*ranks+1e-5:
            raise ValueError('Sampled search time exceeds enclosing trace')
    counts={k:sum(r[k] for r in records) for k in COUNTS}
    if counts['callsMean']<steps:
        raise ValueError('Laser profile does not cover all solver steps')
    total=sum(r['total_s'] for r in records)
    stages=[dict(stage=k,mean_s=sum(r[k+'_s'] for r in records),
                 mean_fraction=sum(r[k+'_s'] for r in records)/total,
                 interval_rank_max_sum_s=sum(r[k+'Max_s'] for r in records)) for k in STAGES]
    samples=sum(r['traceSearchSamplesSum'] for r in records)
    return dict(mean_total_s=total,interval_rank_max_sum_s=sum(r['totalMax_s'] for r in records),
                stages=stages,counts=counts,trace_search_sample_sum_s=sum(r['traceSearchSampleSum_s'] for r in records),
                trace_search_samples_sum=samples,
                sampled_search_mean_s=(sum(r['traceSearchSampleSum_s'] for r in records)/samples if samples else None),
                note='Only MPI mean stages add. Rank maxima are not additive. Search time is a stride-128 sample inside trace, not a separate stage or an unbiased total estimate. Replicated calls/rays/rounds use means; local work uses sums. Outer field reset/dictionary work and profiling report reductions are outside this inner-call total.')

def collect(work):
    work=Path(work)
    cases=[work/v for v in ('laserProfileOff','laserProfileOn')]
    probes=[read_probe(c) for c in cases]
    comparison,diagnostics=compare(*probes)
    runs=[json.loads((c/'run.json').read_text()) for c in cases]
    for key in ('solver_sha256','laser_library_sha256'):
        if not runs[0].get(key) or runs[0][key]!=runs[1].get(key):
            raise ValueError('Unmatched solver/library provenance')
    converged=True
    for case,probe,enabled in zip(cases,probes,(False,True)):
        meta=probe[0]
        if (meta.get('laser_performance_diagnostics') is not enabled
            or meta.get('phase_temperature_blend_half_width')!=0
            or meta.get('epsilon_tolerance')!=1e-5 or meta.get('phase_temperature_tolerance_K')!=0.001):
            raise ValueError('Laser probe requires matched tight controls, width zero and expected profile switch')
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
    if parse_records((cases[0]/'log.vacuumLaserbeamFoam').read_text(),'LASER_PERF_DIAGNOSTICS'):
        raise ValueError('Profiling-off case emitted laser profiling records')
    profile=summarize(parse_records((cases[1]/'log.vacuumLaserbeamFoam').read_text(),'LASER_PERF_DIAGNOSTICS'),
                      [r['time'] for r in probes[1][2]],probes[1][0]['ranks'],probes[1][1]['steps'])
    fields=field_differences(*cases,probes[0][0]['ranks'],probes[0][0]['end_s'])
    for row in fields:
        row['allowed_difference']=1e-12+1e-8*row['reference_max_abs']
        row['passed']=row['max_abs_difference']<=row['allowed_difference']
    result=dict(schema=1,regression_gate=converged and comparison['thermal_limit_gate']
                and comparison['diagnostic_pass'] and all(f['passed'] for f in fields),
                production_approved=False,comparison=comparison,laser_profile=profile,fields=fields,
                profiling_job_overhead_ratio=runs[1]['elapsed_wall_s']/runs[0]['elapsed_wall_s'],
                note='Instrumentation equivalence only; no speedup or physical closure approval is implied.')
    output=work/'comparison'
    if output.exists(): raise ValueError('Comparison directory already exists')
    output.mkdir()
    (output/'laserProfileReview.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,rows in (('laserProfileStages.csv',profile['stages']),('laserProfileFields.csv',fields),('diagnosticComparison.csv',diagnostics)):
        with (output/name).open('x',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    try: result=collect(args.work)
    except (ValueError,OSError,KeyError) as error: parser.exit(1,f'Laser profile collection failed: {error}\n')
    print(f"Profiling equivalence gate: {result['regression_gate']}")
    print(f"Profiling job overhead ratio: {result['profiling_job_overhead_ratio']:.3f}")
    for row in sorted(result['laser_profile']['stages'],key=lambda r:r['mean_s'],reverse=True):
        print(f"  {row['stage']}: {row['mean_s']:.3f} s, {100*row['mean_fraction']:.2f}%")
    if not result['regression_gate']: parser.exit(2,'Instrumentation regression gate failed.\n')

if __name__=='__main__': main()
