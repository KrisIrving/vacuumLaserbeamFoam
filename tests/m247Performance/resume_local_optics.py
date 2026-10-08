#!/usr/bin/env python3
"""Reuse audited optical mapping and run only the missing frozen trace."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from local_optics import (NAMES,INPUTS,read_trace,check_capture,case_fingerprint,
    material_hashes,restore_unmapped_fluxes,mapping_guard,contrasts,run,sha)
from package_results import FILES


def execute(audit_work,work):
    audit_work,work=Path(audit_work).resolve(),Path(work).resolve()
    audit=json.loads((audit_work/'opticalMappingAudit.json').read_text())
    previous=Path(audit['previous_work']).resolve()
    inputs=json.loads((previous/'localOpticsInputs.json').read_text())
    parents=[audit_work,previous]+[Path(p).resolve() for p in inputs['source_cases']]
    if any(p==work or p in work.parents or work in p.parents for p in parents):
        raise ValueError('Output overlaps input')
    if not audit.get('complete') or audit.get('source_unchanged_gates')!=[True,True]:
        raise ValueError('Completed read-only source audit required')
    if sha(previous/'localOpticsReview.json')!=audit['previous_review_sha256']:
        raise ValueError('Prior review changed')
    if sha(previous/(NAMES[2]+'_mapping.log'))!=audit['mapping_log_sha256']:
        raise ValueError('Mapping log changed')
    if case_fingerprint(previous/NAMES[1])!=audit['before'] or case_fingerprint(previous/NAMES[2])!=audit['after']:
        raise ValueError('Audited fine/mapped files changed')
    for source,digest in zip(inputs['source_cases'],inputs['source_hashes']):
        if case_fingerprint(Path(source))!=digest:raise ValueError('Original source changed')
    work.mkdir(parents=True,exist_ok=True)
    if (work/'localOpticsInputs.json').exists():raise ValueError('Choose fresh output')
    shutil.copy2(previous/'localOpticsInputs.json',work/'localOpticsInputs.json')
    shutil.copy2(audit_work/'opticalMappingAudit.json',work/'opticalMappingAudit.json')
    prior=json.loads((previous/'localOpticsReview.json').read_text())
    if prior.get('complete') or [r['variant'] for r in prior['cases']]!=list(NAMES[:2]):
        raise ValueError('Expected two completed prior traces')
    report=dict(schema=1,complete=False,production_approved=False,cases=[],commands=[],
        resumed_from=str(previous),audit_sha256=sha(audit_work/'opticalMappingAudit.json'),
        no_mapping_rerun=True,no_cfd=True)
    def save():(work/'localOpticsReview.json').write_text(json.dumps(report,indent=2)+'\n')
    save();jobs=[];powers=[]
    for name,row in zip(NAMES[:2],prior['cases']):
        origin=previous/name;trace=read_trace(origin,name)
        check_capture((origin/'capture.log').read_text())
        capture=json.loads((origin/'captureRun.json').read_text())
        if capture['returncode'] or capture.get('wall_budget_stop') or capture.get('forced_stop'):
            raise ValueError('Invalid prior capture')
        if trace[2]!=row['diagnostics'] or trace[3]!=row['profile']:
            raise ValueError('Prior trace no longer matches review')
        if {n:sha(origin/'0.00018'/n) for n in INPUTS}!=row['optical_input_sha256']:
            raise ValueError('Prior optical inputs changed')
        # These are labelled evidence-only directories, not runnable CFD copies.
        for relative in FILES:
            src=origin/relative;dst=work/name/relative
            dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
        jobs.extend([capture,trace[1]]);powers.append(trace[2]['depositedPower'])
        report['cases'].append(dict(row,reused=True,evidence_only=True));save()
    case=work/NAMES[2];case.mkdir()
    for part in ('constant','system','0.00018'):
        shutil.copytree(previous/NAMES[2]/part,case/part)
    shutil.copy2(previous/NAMES[2]/'probe.json',case/'probe.json')
    if case_fingerprint(case)!=audit['after']:raise ValueError('Mapped copy hash mismatch')
    report['restored_flux_names']=restore_unmapped_fluxes(case,audit['before'])
    report['mapped_changed_files']=mapping_guard(audit['before'],case_fingerprint(case))
    physics=material_hashes(case);save()
    report['commands'].append(run(work,['decomposePar','-case',str(case),'-time','0.00018','-noFunctionObjects'],NAMES[2]+'_decompose'))
    partition=[]
    for rank in range(48):
        relative=f'processor{rank}/constant/polyMesh/cellProcAddressing'
        paths=[root/relative for root in (previous/NAMES[1],case)]
        digests=[sha(p if p.is_file() else p.with_name(p.name+'.gz')) for p in paths]
        if digests[0]!=digests[1]:raise ValueError('Fine rank cell ownership differs')
        partition.append(digests[0])
        for field in INPUTS:
            if not (case/f'processor{rank}/0.00018'/field).is_file():raise ValueError('Missing frozen input')
    report['fine_partition_sha256']=partition;save()
    report['commands'].append(run(work,[sys.executable,str(Path(__file__).with_name('run_probe.py')),
        '--case',str(case),'--wall-hours',str(5/60)],NAMES[2]+'_traceJob'))
    trace=read_trace(case,NAMES[2]);jobs.append(trace[1]);powers.append(trace[2]['depositedPower'])
    for key in ('solver_sha256','laser_library_sha256'):
        if not jobs[0].get(key) or len({j.get(key) for j in jobs})!=1:
            raise ValueError('Reused/new binary provenance differs')
    if material_hashes(case)!=physics:raise ValueError('Frozen material changed')
    if case_fingerprint(previous/NAMES[1])!=audit['before'] or case_fingerprint(previous/NAMES[2])!=audit['after']:
        raise ValueError('Retained cases changed')
    for source,digest in zip(inputs['source_cases'],inputs['source_hashes']):
        if case_fingerprint(Path(source))!=digest:raise ValueError('Original source changed')
    report['cases'].append(dict(variant=NAMES[2],diagnostics=trace[2],profile=trace[3],run=trace[1],
        material_unchanged_gate=True,optical_input_sha256={n:sha(case/'0.00018'/n) for n in INPUTS}))
    report.update(complete=True,source_unchanged_gate=True,contrasts=contrasts(powers));save()
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args()
    try:r=execute(a.audit,a.work)
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as e:p.exit(1,f'Optical resume failed: {e}\n')
    for c in r['cases']:print(c['variant'],'depositedPower W:',c['diagnostics']['depositedPower'])
    print('Frozen comparison complete; no CFD advanced; production approved: False')


if __name__=='__main__':main()
