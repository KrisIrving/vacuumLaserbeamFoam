#!/usr/bin/env python3
"""Locate tolerance-sensitive internal cells in an existing validation pair."""
import argparse
import csv
import heapq
import json
import math
from pathlib import Path
from collect_probe import read_probe, compare
from collect_thermal_validation import FIELDS, read_field, final_state, residual_gate

THRESHOLDS = {'T':(1,10,100), 'U':(0.1,1,10), 'epsilon1':(0.001,0.01,0.1,0.5,0.99),
              'alpha.metal':(1e-4,1e-3,0.01), 'p_rgh':(100,1000,10000)}
UNITS = {'T':'K','U':'m/s','epsilon1':'1','alpha.metal':'1','p_rgh':'Pa'}

def region(a,b):
    # Disjoint bins based on BOTH states; shifted interfaces stay in interface.
    if max(a,b)<=0.01: return 'gasBoth'
    if min(a,b)>=0.99: return 'metalBoth'
    return 'interfaceOrChanged'

def localize(work, top=10):
    if top<1: raise ValueError('Top-cell count must be positive')
    reference,candidate = work/'enthalpyTight',work/'enthalpyStandard'
    tight,normal = read_probe(reference),read_probe(candidate)
    compare(tight,normal)  # validates source snapshot, time, ranks and sample times
    if tight[0]['variant']!='enthalpyTight' or normal[0]['variant']!='enthalpyStandard':
        raise ValueError('Unexpected validation variants')
    for key in ('solver_sha256','laser_library_sha256'):
        hashes=[json.loads((p/'run.json').read_text()).get(key) for p in (reference,candidate)]
        if hashes[0]!=hashes[1] or (key=='solver_sha256' and not hashes[0]):
            raise ValueError('Solver/library provenance does not match')
    for case in (reference,candidate):
        if (case/'constant/dynamicMeshDict').exists():
            raise ValueError('Only the fixed M247 mesh is supported')
        for rank in range(tight[0]['ranks']):
            for folder in (case/f'processor{rank}').iterdir():
                if (folder/'polyMesh').is_dir():
                    try: value=float(folder.name)
                    except ValueError: continue
                    if value>tight[0]['start_s']+1e-12:
                        raise ValueError('Mesh changed in validation interval')
    groups=('all','gasBoth','interfaceOrChanged','metalBoth')
    stats={(group,field):dict(cells=0,sum_squared=0.0,max_abs_difference=0.0,
        threshold_counts={str(t):0 for t in THRESHOLDS[field]}) for group in groups for field in FIELDS}
    heaps={field:[] for field in FIELDS}
    crossed_phase_override = 0
    crossed_and_large_epsilon = 0
    for rank in range(tight[0]['ranks']):
        folders=[final_state(case,rank,tight[0]['end_s']) for case in (reference,candidate)]
        raw=[{f:read_field(p/f) for f in FIELDS} for p in folders]
        counts={len(v)//c for fields in raw for v,c,u in fields.values() if not u}
        if len(counts)!=1: raise ValueError('Inconsistent/missing cell counts')
        cells=counts.pop()
        data=[]
        for fields in raw:
            expanded={}
            for field,(values,components,uniform) in fields.items():
                if components!=(3 if field=='U' else 1): raise ValueError('Field type mismatch')
                expanded[field]=values*cells if uniform else values
            data.append(expanded)
        for cell in range(cells):
            a,b=[d['alpha.metal'][cell] for d in data]
            group=region(a,b)
            if (a>0.05)!=(b>0.05):
                crossed_phase_override += 1
                if abs(data[0]['epsilon1'][cell]-data[1]['epsilon1'][cell])>0.99:
                    crossed_and_large_epsilon += 1
            for field in FIELDS:
                components=3 if field=='U' else 1
                values=[d[field][cell*components:(cell+1)*components] for d in data]
                squared=sum((y-x)**2 for x,y in zip(*values))
                difference=math.sqrt(squared)
                for g in ('all',group):
                    s=stats[g,field];s['cells']+=1;s['sum_squared']+=squared
                    s['max_abs_difference']=max(s['max_abs_difference'],difference)
                    for threshold in THRESHOLDS[field]:
                        if difference>threshold: s['threshold_counts'][str(threshold)]+=1
                heap=heaps[field]
                if len(heap)<top or (difference,rank,cell)>heap[0][:3]:
                    context=dict(field=field,unit=UNITS[field],absolute_difference=difference,
                        rank=rank,local_cell=cell,region=group,
                        crosses_alpha_0p05=(a>0.05)!=(b>0.05),
                        reference_value=values[0][0] if components==1 else values[0],
                        candidate_value=values[1][0] if components==1 else values[1],
                        reference_T=data[0]['T'][cell],candidate_T=data[1]['T'][cell],
                        reference_alpha=a,candidate_alpha=b,
                        reference_epsilon=data[0]['epsilon1'][cell],candidate_epsilon=data[1]['epsilon1'][cell],
                        reference_U=data[0]['U'][cell*3:(cell+1)*3],candidate_U=data[1]['U'][cell*3:(cell+1)*3],
                        reference_p_rgh=data[0]['p_rgh'][cell],candidate_p_rgh=data[1]['p_rgh'][cell])
                    item=(difference,rank,cell,context)
                    if len(heap)<top: heapq.heappush(heap,item)
                    else: heapq.heapreplace(heap,item)
    summaries=[]
    for (group,field),s in stats.items():
        summaries.append(dict(region=group,field=field,unit=UNITS[field],cells=s['cells'],
            max_abs_difference=s['max_abs_difference'] if s['cells'] else None,
            cell_unweighted_rms_difference=math.sqrt(s['sum_squared']/s['cells']) if s['cells'] else None,
            threshold_counts=s['threshold_counts']))
    worst=[item[3] for field in FIELDS for item in sorted(heaps[field],reverse=True)]
    convergence = tight[1]['thermal_limit_hits']==normal[1]['thermal_limit_hits']==0
    convergence = convergence and residual_gate(reference,tight[0],tight[1]['steps']) and residual_gate(candidate,normal[0],normal[1]['steps'])
    return dict(reference=str(reference),candidate=str(candidate),time_s=tight[0]['end_s'],
        cells=stats['all','T']['cells'],convergence_gate=convergence,production_approved=False,
        alpha_0p05_crossing_cells=crossed_phase_override,
        alpha_0p05_crossing_with_epsilon_difference_above_0p99=crossed_and_large_epsilon,
        note='Same fixed mesh/local cell ordering; internal cells only; RMS is not volume weighted. Positions are not inferred from local cell indices. Alpha bins classify both states. Threshold counts are diagnostic, not acceptance limits.',
        regions=summaries,worst_cells=worst)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    output=args.work/'comparison'
    names=('fieldLocalization.json','fieldRegions.csv','worstCells.csv')
    try:
        if any((output/n).exists() for n in names):
            raise ValueError('Localization outputs already exist; preserve them rather than overwrite')
        result=localize(args.work)
        output.mkdir(exist_ok=True)
        (output/names[0]).write_text(json.dumps(result,indent=2)+'\n')
        for name,rows in ((names[1],result['regions']),(names[2],result['worst_cells'])):
            with (output/name).open('x',newline='') as stream:
                writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
        print(f"Localized {result['cells']} cells. No CFD was run.")
        for row in result['regions']:
            if row['field'] in ('T','U','epsilon1'):
                print(f"{row['region']} {row['field']}: max={row['max_abs_difference']}, RMS={row['cell_unweighted_rms_difference']}, counts={row['threshold_counts']}")
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,f'Localization failed: {error}\n')

if __name__=='__main__':
    main()
