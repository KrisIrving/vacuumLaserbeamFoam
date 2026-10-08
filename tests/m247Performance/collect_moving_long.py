#!/usr/bin/env python3
"""Copy existing pair evidence into a fresh archive; no compilation or CFD."""
import argparse,json,shutil,os
from pathlib import Path
from moving_completion import completion
from package_results import package
from region_audit import sha

def inventory(previous):
    """Read live resources/progress; no process control or original-case writes."""
    previous=previous.resolve();result=dict(schema=1,read_only=True,processes=[],runs=[])
    usage=shutil.disk_usage(previous)
    result['disk_bytes']=dict(total=usage.total,used=usage.used,free=usage.free)
    if hasattr(os,'statvfs'):
        fs=os.statvfs(previous);result['inodes']=dict(total=fs.f_files,free=fs.f_favail)
    mem=Path('/proc/meminfo')
    if mem.is_file():
        result['memory_kB']={line.split(':')[0]:int(line.split()[1]) for line in mem.read_text().splitlines()
            if line.split(':')[0] in ('MemTotal','MemAvailable','SwapTotal','SwapFree')}
    proc=Path('/proc')
    if proc.is_dir():
        for folder in proc.iterdir():
            if not folder.name.isdigit():continue
            try:
                command=(folder/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
                if str(previous) not in command:continue
                comm=(folder/'comm').read_text().strip()
                status=(folder/'status').read_text().splitlines()
                details={line.split(':')[0]:line.split(':',1)[1].strip() for line in status
                    if line.split(':')[0] in ('State','PPid','VmRSS','VmSwap')}
                result['processes'].append(dict(pid=int(folder.name),command_name=comm,status=details,is_current_collector=int(folder.name)==os.getpid()))
            except (OSError,ValueError):continue
    for ns in ('5ns','10ns'):
        run=previous/(previous.name+'-'+ns);case=run/'movingCFD';ranks=[]
        for rank in range(48):
            folder=case/f'processor{rank}'/'0.00018'
            ranks.append(dict(rank=rank,initial_directory=folder.is_dir(),
                fields_present=[name for name in ('T','U','alpha.metal','epsilon1','phi') if (folder/name).is_file()]))
        result['runs'].append(dict(variant=ns,case=str(case),rank_progress=ranks,
            solver_log_present=(case/'log.vacuumLaserbeamFoam').is_file(),run_metadata_present=(case/'run.json').is_file()))
    result['note']='Point-in-time snapshot. Process absence or free resources now cannot establish historical cause; filenames do not prove complete native decomposition.'
    return result


def collect(previous,work):
    previous,work=previous.resolve(),work.resolve()
    if not previous.is_dir():raise ValueError('Original pair directory missing')
    if work==previous or previous in work.parents or work in previous.parents:raise ValueError('Collection overlaps original')
    work.mkdir(parents=True,exist_ok=False);copied={}
    (work/'movingLongInventory.json').write_text(json.dumps(inventory(previous),indent=2)+'\n')
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
