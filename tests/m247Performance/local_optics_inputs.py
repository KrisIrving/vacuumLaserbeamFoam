#!/usr/bin/env python3
"""Single-input frozen optical substitutions on the same fine mesh."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from local_optics import (NAMES,INPUTS,read_trace,case_fingerprint,mapping_guard,
    material_hashes,sha,run)

ROLES=dict(localOpticsAlphaMapped='frozenAlphaInput',
           localOpticsNormalMapped='frozenNormalInput',
           localOpticsResistivityMapped='frozenResistivityInput')


def contrast(name,field,power,own,mapped):
    return dict(variant=name,replaced_input=field,depositedPower_W=power,
        fine_own_W=own,fine_all_mapped_W=mapped,difference_from_fine_own_W=power-own,
        relative_difference_from_fine_own=(power-own)/own,
        note='Single substitution on the fine mesh; nonlinear interaction and mapped-input artifacts remain possible')


def execute(previous,work):
    previous,work=Path(previous).resolve(),Path(work).resolve()
    review=json.loads((previous/'localOpticsReview.json').read_text())
    if not review.get('complete') or not review.get('source_unchanged_gate'):
        raise ValueError('Completed resumed three-role comparison required')
    if [r['variant'] for r in review['cases']]!=list(NAMES):
        raise ValueError('Wrong optical reference roles')
    original=Path(review['resumed_from']).resolve()
    fine=original/NAMES[1];mapped=previous/NAMES[2]
    inputs=json.loads((previous/'localOpticsInputs.json').read_text())
    roots=[previous,original]+[Path(p).resolve() for p in inputs['source_cases']]
    if any(p==work or p in work.parents or work in p.parents for p in roots):
        raise ValueError('Output overlaps input')
    before={str(c):case_fingerprint(c) for c in (fine,mapped)}
    mapping_guard(before[str(fine)],before[str(mapped)])
    references=[]
    for i,name in enumerate(NAMES):
        case=previous/name;trace=read_trace(case,name);row=review['cases'][i]
        if trace[2]!=row['diagnostics'] or trace[3]!=row['profile']:
            raise ValueError('Reference trace differs from report')
        if i>0:
            origin=fine if i==1 else mapped
            if {n:sha(origin/'0.00018'/n) for n in INPUTS}!=row['optical_input_sha256']:
                raise ValueError('Reference inputs changed')
        references.append(trace)
    for c,h in zip(inputs['source_cases'],inputs['source_hashes']):
        if case_fingerprint(Path(c))!=h:raise ValueError('Original source changed')
    if (work/'localOpticsInputReview.json').exists():raise ValueError('Choose fresh output')
    work.mkdir(parents=True,exist_ok=True)
    report=dict(schema=1,complete=False,production_approved=False,no_cfd=True,
        previous_work=str(previous),previous_review_sha256=sha(previous/'localOpticsReview.json'),
        reference_cases=review['cases'],cases=[],commands=[],source_fingerprints=before)
    def save():(work/'localOpticsInputReview.json').write_text(json.dumps(report,indent=2)+'\n')
    save();jobs=[r[1] for r in references]
    for name,field in ROLES.items():
        case=work/name;case.mkdir()
        for part in ('constant','system','0.00018'):shutil.copytree(fine/part,case/part)
        if case_fingerprint(case)!=before[str(fine)]:raise ValueError('Fine copy mismatch')
        shutil.copy2(mapped/'0.00018'/field,case/'0.00018'/field)
        changed=mapping_guard(before[str(fine)],case_fingerprint(case))
        if any(p!='0.00018/'+field for p in changed):raise ValueError('More than one optical input replaced')
        meta=dict(references[1][0],variant=name,purpose='Single optical input substitution; no CFD')
        (case/'probe.json').write_text(json.dumps(meta,indent=2)+'\n')
        physics=material_hashes(case)
        optical={n:sha(case/'0.00018'/n) for n in INPUTS}
        report['commands'].append(run(work,['decomposePar','-case',str(case),'-time','0.00018','-noFunctionObjects'],name+'_decompose'))
        partitions=[]
        for rank in range(48):
            relative=f'processor{rank}/constant/polyMesh/cellProcAddressing'
            hashes=[sha(p if p.is_file() else p.with_name(p.name+'.gz')) for p in (fine/relative,case/relative)]
            if hashes[0]!=hashes[1]:raise ValueError('Rank cell ownership differs')
            partitions.append(hashes[0])
            for n in INPUTS:
                if not (case/f'processor{rank}/0.00018'/n).is_file():raise ValueError('Missing rank optical input')
        report['commands'].append(run(work,[sys.executable,str(Path(__file__).with_name('run_probe.py')),
            '--case',str(case),'--wall-hours',str(5/60)],name+'_traceJob'))
        trace=read_trace(case,name);jobs.append(trace[1])
        if material_hashes(case)!=physics or {n:sha(case/'0.00018'/n) for n in INPUTS}!=optical:
            raise ValueError('Frozen serial inputs changed')
        report['cases'].append(dict(variant=name,replaced_input=field,changed_files=changed,
            optical_input_sha256=optical,fine_partition_sha256=partitions,
            diagnostics=trace[2],profile=trace[3],run=trace[1],material_unchanged_gate=True,
            contrast=contrast(name,field,trace[2]['depositedPower'],references[1][2]['depositedPower'],references[2][2]['depositedPower'])))
        save()
    for key in ('solver_sha256','laser_library_sha256'):
        if not jobs[0].get(key) or len({j.get(key) for j in jobs})!=1:
            raise ValueError('Reference/candidate binary provenance differs')
    for c in (fine,mapped):
        if case_fingerprint(c)!=before[str(c)]:raise ValueError('Reference case changed')
    for c,h in zip(inputs['source_cases'],inputs['source_hashes']):
        if case_fingerprint(Path(c))!=h:raise ValueError('Original source changed')
    report.update(complete=True,source_unchanged_gate=True);save()
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args()
    try:r=execute(a.previous,a.work)
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as e:p.exit(1,f'Optical input probe failed: {e}\n')
    for c in r['cases']:print(c['variant'],'depositedPower W:',c['diagnostics']['depositedPower'])
    print('Single-input frozen probes complete; production approved: False')


if __name__=='__main__':main()
