#!/usr/bin/env python3
"""Read-only localization of a stopped optical mapping; never launch OpenFOAM."""
import argparse
import json
from pathlib import Path
import re
import shutil
from local_optics import NAMES, mapping_guard
from frozen_laser import INPUTS, read_trace
from restart_audit import case_fingerprint
from region_audit import sha


def differences(before, after):
    rows=[]
    for name in sorted(set(before)|set(after)):
        if before.get(name)==after.get(name):
            continue
        rows.append(dict(path=name, before_sha256=before.get(name),
                         after_sha256=after.get(name),
                         status='added' if name not in before else 'removed' if name not in after else 'modified'))
    # Equal hashes identify byte-preserving rename candidates, not permission to restore.
    pairs=[dict(source=a['path'], target=b['path'], sha256=a['before_sha256'])
           for a in rows if a['status']=='removed'
           for b in rows if b['status']=='added' and a['before_sha256']==b['after_sha256']]
    return rows,pairs


def audit(previous, work):
    previous,work=Path(previous).resolve(),Path(work).resolve()
    if previous==work or previous in work.parents or work in previous.parents:
        raise ValueError('Output must not overlap the stopped run')
    if (work/'opticalMappingAudit.json').exists():
        raise ValueError('Choose fresh output')
    work.mkdir(parents=True,exist_ok=True)
    review=json.loads((previous/'localOpticsReview.json').read_text())
    if review.get('complete') or [r['variant'] for r in review['cases']]!=list(NAMES[:2]):
        raise ValueError('Expected a run stopped after the two own-input traces')
    for name,row in zip(NAMES[:2],review['cases']):
        trace=read_trace(previous/name,name)
        if trace[2]!=row['diagnostics']:
            raise ValueError('Saved diagnostic differs from solver log')
        for field,digest in row['optical_input_sha256'].items():
            if sha(previous/name/'0.00018'/field)!=digest:
                raise ValueError('Completed optical inputs changed')
    mapping_log=previous/(NAMES[2]+'_mapping.log')
    if not re.search(r'^End\s*$',mapping_log.read_text(),re.M):
        raise ValueError('Native mapping did not finish')
    before=case_fingerprint(previous/NAMES[1])
    after=case_fingerprint(previous/NAMES[2])
    # The old runner copied constant/system/0.00018 directly from this fine case.
    # This reconstruction is explicitly labelled; it is not a saved pre-map digest.
    rows,pairs=differences(before,after)
    inputs=json.loads((previous/'localOpticsInputs.json').read_text())
    source_gates=[case_fingerprint(Path(c))==h for c,h in
                  zip(inputs['source_cases'],inputs['source_hashes'])]
    allowed={'0.00018/'+f for f in INPUTS}
    gate_error=None
    try:
        mapping_guard(before,after)
    except ValueError as e:
        gate_error=str(e)
    report=dict(schema=1,previous_work=str(previous),complete=True,
        production_approved=False,no_cfd=True,read_only=True,
        baseline='Current completed fine case from which the mapped case was copied; reconstructed, not a historical pre-map fingerprint',
        previous_review_sha256=sha(previous/'localOpticsReview.json'),
        mapping_log_sha256=sha(mapping_log),source_unchanged_gates=source_gates,
        before=before,after=after,changes=rows,byte_identical_rename_candidates=pairs,
        unexpected_changes=[r for r in rows if r['path'] not in allowed],
        strict_mapping_gate=gate_error is None,strict_mapping_error=gate_error)
    (work/'opticalMappingAudit.json').write_text(json.dumps(report,indent=2)+'\n')
    for name in ('localOpticsInputs.json','localOpticsReview.json',NAMES[2]+'_mapping.log'):
        shutil.copy2(previous/name,work/name)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    a=p.parse_args()
    try:
        r=audit(a.previous,a.work)
    except (ValueError,KeyError,OSError) as e:
        p.exit(1,f'Optical mapping audit failed: {e}\n')
    for row in r['changes']:
        print(row['status'],row['path'])
    print('Read-only collection complete; original mapping gate:',r['strict_mapping_gate'])


if __name__=='__main__':
    main()
