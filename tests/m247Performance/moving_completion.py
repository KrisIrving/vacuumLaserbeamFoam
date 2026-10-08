#!/usr/bin/env python3
"""Never mark an interrupted/missing pilot or pair complete from shell status alone."""
import argparse,json
from pathlib import Path
from compare_moving_steps import compare

def completion(work,requested=0,pilot=False):
    errors=[]
    names=('movingCFDReview.json',) if pilot else ('movingStepReference.json','movingStepCandidate.json','movingStepComparison.json')
    for name in names:
        try:
            r=json.loads((work/name).read_text())
            if name!='movingStepComparison.json' and (not r.get('complete') or not r.get('pilot_gate') or not r.get('source_unchanged_gate')):errors.append(name+': incomplete/failed pilot')
        except (OSError,ValueError):errors.append(name+': absent/unreadable')
    if not pilot and not errors:
        try:
            result=compare(work/names[0],work/names[1])
            saved=json.loads((work/names[2]).read_text())
            if result!=saved:errors.append('Comparison differs from paired reports')
            for name in names[:2]:
                if json.loads((work/name).read_text()).get('duration_us')!=.4:errors.append('Wrong longer-pair duration')
        except (ValueError,KeyError,OSError) as e:errors.append(str(e))
    status=requested if requested else (1 if errors else 0)
    report=dict(schema=1,complete=not errors and status==0,requested_exit_code=requested,
        wrapper_exit_code=status,errors=errors,production_approved=False)
    (work/('movingPilotStatus.json' if pilot else 'movingLongPairStatus.json')).write_text(json.dumps(report,indent=2)+'\n')
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--requested-status',type=int,default=0);p.add_argument('--pilot',action='store_true');a=p.parse_args()
    r=completion(a.work,a.requested_status,a.pilot)
    print('Complete:',r['complete'],'exit:',r['wrapper_exit_code'])
    p.exit(r['wrapper_exit_code'])
if __name__=='__main__':main()
