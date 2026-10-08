#!/usr/bin/env python3
"""Compare existing moving-CFD reports without advancing CFD or matching mesh cells."""
import argparse,json,math
from pathlib import Path
from region_audit import sha

def compare(reference,candidate):
    reports=[json.loads(p.read_text()) for p in (reference,candidate)]
    a,b=reports
    for r in reports:
        if not r.get('complete') or not r.get('pilot_gate'):raise ValueError('Completed passing pilots required')
    for key in ('source_case','source_sha256','original_protected_review_sha256','solver_sha256','duration_us','ranks'):
        if a.get(key) is None or a.get(key)!=b.get(key):raise ValueError('Mismatched pilot provenance: '+key)
    ar,br=a['physical_diagnostics'],b['physical_diagnostics']
    if len(ar)!=len(br) or not ar:raise ValueError('Missing matched physical diagnostics')
    differences=[]
    for x,y in zip(ar,br):
        if abs(x['time']-y['time'])>1e-12:raise ValueError('Unmatched physical times')
        if set(x)!=set(y):raise ValueError('Mismatched diagnostic keys')
        for key in x:
            if key=='time':continue
            if not math.isfinite(x[key]) or not math.isfinite(y[key]):raise ValueError('Nonfinite physical diagnostic')
            differences.append(dict(time=x['time'],metric=key,reference=x[key],candidate=y[key],
                absolute_difference=y[key]-x[key],relative_difference=(y[key]-x[key])/abs(x[key]) if x[key]!=0 else None))
    return dict(schema=1,collection_only=True,no_cfd_advanced=True,production_approved=False,
        reference_sha256=sha(reference),candidate_sha256=sha(candidate),
        job_speedup=a['pilot']['job_wall_s']/b['pilot']['job_wall_s'],
        loop_speedup=a['pilot']['interval_rank_max_sum_s']/b['pilot']['interval_rank_max_sum_s'],
        reference_steps=a['pilot']['steps'],candidate_steps=b['pilot']['steps'],differences=differences,
        note='Diagnostic comparison only: no spatial field equivalence, mesh matching, timestep convergence or long-track approval. Relative values near zero are ill-conditioned.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('reference','candidate','output'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    try:
        r=compare(a.reference,a.candidate)
        with a.output.open('x',encoding='utf-8') as f:json.dump(r,f,indent=2);f.write('\n')
        print('Job speedup:',r['job_speedup'],'production approved: False')
    except (ValueError,KeyError,OSError) as e:p.exit(1,str(e)+'\n')
if __name__=='__main__':main()
