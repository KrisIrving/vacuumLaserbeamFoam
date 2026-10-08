#!/usr/bin/env python3
"""Copy existing pair evidence into a fresh archive; no compilation or CFD."""
import argparse,json,shutil
from pathlib import Path
from moving_completion import completion
from package_results import package
from region_audit import sha

def collect(previous,work):
    previous,work=previous.resolve(),work.resolve()
    if not previous.is_dir():raise ValueError('Original pair directory missing')
    if work==previous or previous in work.parents or work in previous.parents:raise ValueError('Collection overlaps original')
    work.mkdir(parents=True,exist_ok=False);copied={}
    suffixes={'log.vacuumLaserbeamFoam':'Solver.log','run.json':'Run.json','probe.json':'Probe.json'}
    for name,ns in (('reference','5ns'),('candidate','10ns')):
        run=previous/(previous.name+'-'+ns)
        sources={run/'build.log':name+'LongBuild.log',run/'collection.log':name+'LongCollection.log',
            run/'movingCFD_decompose.log':name+'LongDecompose.log',run/'movingCFD_pilot.log':name+'LongPilot.log',
            run/'movingCFDReview.json':'movingStepReference.json' if name=='reference' else 'movingStepCandidate.json'}
        sources.update({run/'movingCFD'/s:name+'Long'+t for s,t in suffixes.items()})
        for source,target in sources.items():
            if source.is_file():
                before=sha(source);shutil.copy2(source,work/target)
                if sha(source)!=before or sha(work/target)!=before:raise ValueError('Input changing during collection: '+str(source))
                copied[str(source)]=before
    for name in ('movingStepComparison.json',):
        if (previous/name).is_file():shutil.copy2(previous/name,work/name)
    (work/'movingLongCollectionInputs.json').write_text(json.dumps(dict(previous=str(previous),no_cfd_advanced=True,
        collection_only=True,copied_sha256=copied,note='Frozen copies only. Missing/incomplete results remain incomplete; no CFD rerun or reconstruction.'),indent=2)+'\n')
    result=completion(work);archive,_=package(work,exit_code=result['wrapper_exit_code'])
    return archive,result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('previous','work'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();fresh=not a.work.exists()
    try:
        archive,result=collect(a.previous,a.work)
        print('Review archive:',archive,'complete:',result['complete'])
        print('Send this archive even if incomplete. No CFD advanced.')
    except (ValueError,OSError) as e:
        if fresh and a.work.is_dir():
            (a.work/'movingLongCollectionInputs.json').write_text(json.dumps(dict(error=str(e),complete=False,no_cfd_advanced=True),indent=2)+'\n')
            archive,_=package(a.work,exit_code=1)
            print('Incomplete review archive:',archive)
        p.exit(1,str(e)+'\n')
if __name__=='__main__':main()
