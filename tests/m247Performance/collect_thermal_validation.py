#!/usr/bin/env python3
"""Check nonlinear convergence and report sensitivity to tighter tolerances."""
import argparse
import csv
import gzip
import json
import math
from pathlib import Path
import re
from collect_probe import read_probe, compare, parse_records

FIELDS = ('T', 'epsilon1', 'alpha.metal', 'U', 'p_rgh')
NUMBER = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'

def read_field(path):
    if not path.is_file():
        path = path.with_name(path.name+'.gz')
    text = gzip.open(path,'rt').read() if path.suffix == '.gz' else path.read_text()
    text = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
    if not re.search(r'\bformat\s+ascii\s*;',text):
        raise ValueError(f'ASCII output required for field comparison: {path}')
    match = re.search(r'\binternalField\s+nonuniform\s+List<(scalar|vector)>\s+(\d+)\s*\((.*?)\)\s*;', text, re.S)
    if match:
        components = 3 if match[1] == 'vector' else 1
        body = match[3]
        if re.sub(r'[\s()]', '', re.sub(NUMBER,'',body)):
            raise ValueError(f'Invalid numeric field data: {path}')
        values = [float(x) for x in re.findall(NUMBER,body)]
        if len(values) != int(match[2])*components or not all(math.isfinite(x) for x in values):
            raise ValueError(f'Truncated/non-finite field: {path}')
        return values, components, False
    match = re.search(r'\binternalField\s+uniform\s+(.*?)\s*;',text,re.S)
    if not match or re.sub(r'[\s()]','',re.sub(NUMBER,'',match[1])):
        raise ValueError(f'Unsupported internal field: {path}')
    values = [float(x) for x in re.findall(NUMBER,match[1])]
    if len(values) not in (1,3) or not all(math.isfinite(x) for x in values):
        raise ValueError(f'Invalid uniform field: {path}')
    return values, len(values), True

def final_state(case, rank, time):
    candidates = []
    for child in (case/f'processor{rank}').iterdir():
        if child.is_dir():
            try:
                if abs(float(child.name)-time)<=1e-12: candidates.append(child)
            except ValueError:
                pass
    if len(candidates)!=1:
        raise ValueError(f'Missing or ambiguous final field state: {case}, rank {rank}')
    return candidates[0]

def field_differences(reference, candidate, ranks, time):
    totals = {name:dict(cells=0,max_abs_difference=0.0,sum_squared_difference=0.0,
        reference_max_abs=0.0,components=3 if name=='U' else 1) for name in FIELDS}
    for rank in range(ranks):
        folders = [final_state(p,rank,time) for p in (reference,candidate)]
        data = [{name:read_field(folder/name) for name in FIELDS} for folder in folders]
        counts = {len(values)//components for fields in data for values,components,uniform in fields.values() if not uniform}
        if len(counts)!=1:
            raise ValueError('Nonuniform fields have inconsistent or missing cell counts')
        cells = counts.pop()
        for name in FIELDS:
            expanded = []
            for fields in data:
                values, components, uniform = fields[name]
                if components != totals[name]['components']:
                    raise ValueError(f'Wrong field type for {name}')
                expanded.append(values*cells if uniform else values)
            stats = totals[name]
            stats['cells'] += cells
            components = stats['components']
            for i in range(cells):
                diffs = [expanded[1][i*components+j]-expanded[0][i*components+j] for j in range(components)]
                reference_values = expanded[0][i*components:(i+1)*components]
                squared = sum(v*v for v in diffs)
                stats['sum_squared_difference'] += squared
                stats['max_abs_difference'] = max(stats['max_abs_difference'], math.sqrt(squared))
                stats['reference_max_abs'] = max(stats['reference_max_abs'], math.sqrt(sum(v*v for v in reference_values)))
    result = []
    for name, stats in totals.items():
        if not stats['cells']: raise ValueError('Empty field comparison')
        stats['field'] = name
        stats['cell_unweighted_rms_difference'] = math.sqrt(stats.pop('sum_squared_difference')/stats['cells'])
        stats['max_difference_over_reference_max'] = stats['max_abs_difference']/stats['reference_max_abs'] if stats['reference_max_abs'] else None
        result.append(stats)
    return result

def residual_gate(case, metadata, steps):
    records = parse_records((case/'log.vacuumLaserbeamFoam').read_text(), 'THERMAL_RESIDUAL_DIAGNOSTICS')
    required = ('time','boundedEnthalpy','phaseTemperatureChecked','maxResidual','phaseTemperatureResidual_K','aboveTolerance')
    if len(records)!=steps or any(any(k not in r for k in required) for r in records):
        raise ValueError('Incomplete per-step thermal diagnostics')
    if any(a['time']>=b['time'] for a,b in zip(records,records[1:])) or abs(records[-1]['time']-metadata['end_s'])>1e-12:
        raise ValueError('Invalid thermal sample times')
    return all(r['boundedEnthalpy']==1 and r['phaseTemperatureChecked']==1
        and r['maxResidual']<=metadata['epsilon_tolerance']*(1+1e-8)
        and r['phaseTemperatureResidual_K']<=metadata['phase_temperature_tolerance_K']*(1+1e-8)
        and r['aboveTolerance']==0 for r in records)

def collect(work):
    reference, candidate = work/'enthalpyTight', work/'enthalpyStandard'
    tight, normal = read_probe(reference), read_probe(candidate)
    if tight[0]['variant']!='enthalpyTight' or normal[0]['variant']!='enthalpyStandard':
        raise ValueError('Unexpected validation variants')
    for case in (reference,candidate):
        if (case/'constant/dynamicMeshDict').exists():
            raise ValueError('This field comparison supports the fixed M247 mesh only')
        for rank in range(tight[0]['ranks']):
            for child in (case/f'processor{rank}').iterdir():
                if (child/'polyMesh').is_dir():
                    try:
                        mesh_time = float(child.name)
                    except ValueError:
                        continue
                    if mesh_time>tight[0]['start_s']+1e-12:
                        raise ValueError('Mesh changed during the validation interval')
    for key in ('solver_sha256','laser_library_sha256'):
        a,b = [json.loads((p/'run.json').read_text()).get(key) for p in (reference,candidate)]
        if a!=b or (key=='solver_sha256' and not a):
            raise ValueError('Solver/library provenance differs or is missing')
    summary, rows = compare(tight,normal)
    for row in rows:
        row['relative_difference'] = row['absolute_difference']/abs(row['reference']) if row['reference'] else None
    summary['diagnostic_pass_note'] = 'Original strict diagnostic comparison only; differences here measure tolerance sensitivity.'
    summary['convergence_gate'] = summary['thermal_limit_gate'] and residual_gate(reference,tight[0],tight[1]['steps']) and residual_gate(candidate,normal[0],normal[1]['steps'])
    summary['production_approved'] = False
    summary['field_difference_note'] = 'Final internal cells only; RMS is not volume weighted; U differences use vector magnitude. No physical acceptance threshold is assigned.'
    summary['fields'] = field_differences(reference,candidate,tight[0]['ranks'],tight[0]['end_s'])
    output = work/'comparison'
    if output.exists(): raise ValueError('Comparison directory already exists')
    output.mkdir()
    (output/'thermalValidation.json').write_text(json.dumps(summary,indent=2)+'\n')
    for name, records in (('diagnosticComparison.csv',rows),('fieldComparison.csv',summary['fields'])):
        with (output/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(records[0]));writer.writeheader();writer.writerows(records)
    return summary

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    args = parser.parse_args()
    try:
        summary = collect(args.work)
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,f'Validation collection failed: {error}\n')
    print(f"Both runs converged: {summary['convergence_gate']}")
    print(f"Normal/tight job speed ratio (tight time / normal time): {summary['job_wall_speedup']:.3f}")
    for field in summary['fields']:
        print(f"{field['field']}: max difference={field['max_abs_difference']:.6g}; cell RMS={field['cell_unweighted_rms_difference']:.6g}")
    print('Convergence and tolerance sensitivity reported; field/energy/long-track approval still requires review.')
    if not summary['convergence_gate']: parser.exit(2,'Nonlinear convergence gate failed.\n')

if __name__=='__main__':
    main()
