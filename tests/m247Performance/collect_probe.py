#!/usr/bin/env python3
"""Summarise schema-2 MPI timers and compare common-time physical diagnostics."""
import argparse
import csv
import json
import math
from pathlib import Path
import re

SECTIONS = ('controls', 'alpha', 'props', 'laser', 'momentum', 'thermal',
            'pressure', 'history', 'fieldWrite', 'diagnostics', 'rayIO',
            'executionLog', 'other')
METRICS = ('Tmax', 'Umax', 'pVapMax', 'interfacePVapMax', 'QvMax',
           'depositedPower', 'evaporationPower', 'radiationPower',
           'interfaceArea', 'recoilForceX', 'recoilForceY', 'recoilForceZ')

def parse_records(text, prefix):
    records = []
    for line in text.splitlines():
        if line.startswith(prefix+' '):
            record = {k:float(v) for k,v in re.findall(r'(\w+)=([-+0-9.eE]+)', line)}
            if any(not math.isfinite(value) for value in record.values()):
                raise ValueError(f'Non-finite {prefix} value')
            records.append(record)
    return records

def read_probe(case):
    metadata = json.loads((case/'probe.json').read_text())
    run = json.loads((case/'run.json').read_text())
    if not math.isfinite(run['elapsed_wall_s']) or run['elapsed_wall_s'] <= 0:
        raise ValueError('Invalid job wall time')
    text = (case/'log.vacuumLaserbeamFoam').read_text(errors='replace')
    if run['returncode'] != 0 or run.get('wall_budget_stop') or run.get('forced_stop') or not re.search(r'^End\s*$', text, re.M):
        raise ValueError(f'Incomplete probe: {case}')
    perf = parse_records(text, 'PERF_DIAGNOSTICS')
    diag = parse_records(text, 'VACUUM_DIAGNOSTICS')
    if not perf or not diag:
        raise ValueError(f'Missing timing or physical diagnostics: {case}')
    previous = metadata['start_s']
    for row in perf:
        required = ('schema','startTime','time','ranks','steps','stepWall_s',
                    'stepWallMax_s','thermalCorrectors','thermalLimitHits',
                    'maxThermalCorrectors')+tuple(k+'_s' for k in SECTIONS)
        if any(k not in row for k in required) or row['schema'] != 2:
            raise ValueError('Requires rebuilt schema-2 solver, including all timing sections')
        if abs(row['startTime']-previous)>1e-12 or row['time']<=previous or row['ranks'] != metadata['ranks']:
            raise ValueError('Timing intervals overlap, have gaps, or use the wrong rank count')
        if row['steps']<=0 or row['stepWall_s']<=0 or any(row[k+'_s']<0 for k in SECTIONS):
            raise ValueError('Invalid timing totals')
        if not math.isfinite(row['stepWallMax_s']) or row['stepWallMax_s']<=0:
            raise ValueError('Invalid maximum-rank wall time')
        if abs(sum(row[k+'_s'] for k in SECTIONS)-row['stepWall_s']) > max(1e-5, row['stepWall_s']*1e-4):
            raise ValueError('Mean sections do not reconcile to mean step wall time')
        if row['stepWallMax_s'] < row['stepWall_s']*(1-1e-5):
            raise ValueError('Maximum rank time below rank mean')
        previous = row['time']
    if abs(previous-metadata['end_s'])>1e-12 or abs(diag[-1].get('time',-1)-previous)>1e-12:
        raise ValueError('Probe did not cover the requested physical interval')
    if len(diag)<2 or any(any(k not in r for k in ('time',)+METRICS) for r in diag):
        raise ValueError('At least two complete physical diagnostic samples required')
    if any(a['time']>=b['time'] for a,b in zip(diag,diag[1:])):
        raise ValueError('Physical diagnostics are not strictly chronological')
    total = sum(r['stepWall_s'] for r in perf)
    steps = sum(r['steps'] for r in perf)
    summary = dict(case=str(case), variant=metadata['variant'], ranks=metadata['ranks'],
        duration_us=metadata['duration_us'], steps=int(steps),
        mean_rank_step_wall_s=total,
        interval_rank_max_sum_s=sum(r['stepWallMax_s'] for r in perf),
        job_wall_s=run['elapsed_wall_s'],
        thermal_correctors_per_step=sum(r['thermalCorrectors'] for r in perf)/steps,
        max_thermal_correctors=max(r['maxThermalCorrectors'] for r in perf),
        thermal_limit_hits=int(sum(r['thermalLimitHits'] for r in perf)),
        sections={k:dict(mean_s=sum(r[k+'_s'] for r in perf),
                         mean_fraction=sum(r[k+'_s'] for r in perf)/total) for k in SECTIONS})
    summary['wall_s_per_us'] = summary['interval_rank_max_sum_s']/metadata['duration_us']
    return metadata, summary, diag

def compare(reference, candidate, rtol=1e-8, atol=1e-12):
    rm, rs, rd = reference
    cm, cs, cd = candidate
    for key in ('source','checkpoint','start_s','end_s','ranks','source_snapshot_sha256'):
        if rm[key] != cm[key]:
            raise ValueError(f'Unmatched probe input: {key}')
    if len(rd) != len(cd) or any(abs(a['time']-b['time'])>1e-12 for a,b in zip(rd,cd)):
        raise ValueError('Physical sample times differ; no silent nearest-time matching')
    rows = []
    for a,b in zip(rd,cd):
        for metric in METRICS:
            delta=abs(a[metric]-b[metric]); tolerance=atol+rtol*abs(a[metric])
            rows.append(dict(time_s=a['time'], metric=metric, reference=a[metric],
                             candidate=b[metric], absolute_difference=delta,
                             allowed_difference=tolerance, passed=delta<=tolerance))
    summary = dict(reference=rs, candidate=cs,
                   matched_samples=len(rd), diagnostic_pass=all(r['passed'] for r in rows),
                   thermal_limit_gate=rs['thermal_limit_hits']==cs['thermal_limit_hits']==0,
                   solver_loop_speedup=rs['interval_rank_max_sum_s']/cs['interval_rank_max_sum_s'],
                   job_wall_speedup=rs['job_wall_s']/cs['job_wall_s'], rtol=rtol, atol=atol)
    return summary, rows

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args=parser.parse_args()
    try:
        summary, rows=compare(read_probe(args.reference), read_probe(args.candidate))
        if args.output.exists():
            raise ValueError('Comparison output already exists; choose a new directory')
        args.output.mkdir(parents=True)
        (args.output/'comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
        with (args.output/'diagnosticComparison.csv').open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
        for name in ('reference','candidate'):
            data=summary[name]
            print(f"{name}: {data['wall_s_per_us']:.2f} s/us; thermal correctors/step={data['thermal_correctors_per_step']:.2f}; limit hits={data['thermal_limit_hits']}")
            for section, value in sorted(data['sections'].items(),key=lambda item:item[1]['mean_s'],reverse=True):
                print(f"  {section}: {100*value['mean_fraction']:.2f}%")
        print(f"Loop speedup={summary['solver_loop_speedup']:.3f}; job speedup={summary['job_wall_speedup']:.3f}")
        print(f"Diagnostic comparison={'PASS' if summary['diagnostic_pass'] else 'FAIL'}; thermal limit gate={summary['thermal_limit_gate']}")
        if not summary['diagnostic_pass'] or not summary['thermal_limit_gate']:
            parser.exit(2,'Performance candidate has not passed the short regression gates.\n')
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1,f'Collection failed: {error}\n')

if __name__=='__main__':
    main()
