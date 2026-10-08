#!/usr/bin/env python3
"""Three frozen optical updates to isolate local-mesh input/traversal sensitivity."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from frozen_laser import INPUTS,read_trace
from local_refinement import run
from restart_audit import case_fingerprint
from prepare_probe import set_entry
from collect_probe import parse_records
from region_audit import sha

NAMES=('localOpticsCoarse','localOpticsFine','localOpticsMapped')

def material_hashes(case):
    return {n:sha(case/'0.00018'/n) for n in ('T','U','alpha.metal','epsilon1')}

def check_capture(text):
    if (parse_records(text,'FROZEN_LASER_CAPTURE')!=[dict(schema=1,time=.00018,calls=0)]
        or not re.search(r'^End\s*$',text,re.M) or re.search(r'^Time\s*=',text,re.M)
        or parse_records(text,'PERF_DIAGNOSTICS')):raise ValueError('Invalid frozen capture')

def mapping_guard(before,after):
    allowed={'0.00018/'+n for n in INPUTS}
    changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
    if any(k not in allowed for k in changed):raise ValueError('Optical mapping changed non-optical fields/mesh')
    return changed

def contrasts(powers):
    return [dict(comparison=label,reference_W=powers[a],candidate_W=powers[b],
        difference_W=powers[b]-powers[a],relative_difference=(powers[b]-powers[a])/powers[a])
        for label,a,b in (('fresh_grid_inputs',0,1),('mapped_coarse_inputs_on_fine',0,2),('fine_input_reconstruction',2,1))]

def execute(audit_work,work):
    audit_work,work=Path(audit_work).resolve(),Path(work).resolve()
    audit=json.loads((audit_work/'localRestartReview.json').read_text())
    if not audit.get('complete') or not audit.get('geometry_qualification_gate'):
        raise ValueError('Completed local restart audit required')
    preview=Path(audit['inputs']['previous_work']).resolve()
    for parent in (audit_work,preview):
        if parent==work or parent in work.parents or work in parent.parents:raise ValueError('Output overlaps input')
    if (work/'localOpticsInputs.json').exists():raise ValueError('Choose fresh output')
    work.mkdir(parents=True,exist_ok=True)
    sources=[preview/'coarse',preview/'localRefine4']
    source_hashes=[next(r['files_sha256'] for r in audit['cases'] if r['case']==name) for name in ('coarse','localRefine4')]
    if any(case_fingerprint(s)!=h for s,h in zip(sources,source_hashes)):raise ValueError('Audited sources changed')
    base=json.loads((preview/'previewInputs.json').read_text())['copied_restart']
    commands=[];report=dict(schema=1,audit_sha256=sha(audit_work/'localRestartReview.json'),
        commands=commands,cases=[],complete=False,production_approved=False,
        note='Same180us material snapshot, separate grid-derived optical inputs. Mapped variant is diagnostic only; it is not a production optical model or mesh-convergence approval. No CFD time advance.')
    (work/'localOpticsInputs.json').write_text(json.dumps(dict(schema=1,source_cases=list(map(str,sources)),
        source_hashes=source_hashes,roles=dict(zip(NAMES,('coarse own inputs','fine own inputs','fine mapped coarse optical inputs')))),indent=2)+'\n')
    def save():(work/'localOpticsReview.json').write_text(json.dumps(report,indent=2)+'\n')
    save();captures=[];outputs=[]
    for i,name in enumerate(NAMES):
        case=work/name;case.mkdir();origin=sources[min(i,1)] if i<2 else work/NAMES[1]
        for part in ('constant','system','0.00018'):shutil.copytree(origin/part,case/part)
        if i<2 and case_fingerprint(case)!=source_hashes[i]:raise ValueError('Copy hash mismatch')
        meta=dict(base,variant=name,frozen_optics=True,frozen_time_s=.00018,
            purpose=report['note'],cached_ray_traversal=True,cartesian_ray_seed_search=False,
            laser_performance_diagnostics=True,preserve_ray_handoff_sample=True,consistent_ray_termination=True)
        (case/'probe.json').write_text(json.dumps(meta,indent=2)+'\n')
        physics_hashes=material_hashes(case)
        if i<2:
            set_entry(case/'system/controlDict','frozenLaserProbe','capture')
            commands.append(run(work,['decomposePar','-case',str(case),'-time','0.00018','-noFunctionObjects'],name+'_decompose'))
            commands.append(run(work,[sys.executable,str(Path(__file__).with_name('run_probe.py')),'--case',str(case),'--wall-hours',str(5/60)],name+'_captureJob'))
            check_capture((case/'log.vacuumLaserbeamFoam').read_text())
            capture=json.loads((case/'run.json').read_text())
            if capture['returncode'] or capture.get('wall_budget_stop') or capture.get('forced_stop'):raise ValueError('Capture did not finish')
            captures.append(capture)
            (case/'log.vacuumLaserbeamFoam').rename(case/'capture.log');(case/'run.json').rename(case/'captureRun.json')
            commands.append(run(work,['reconstructPar','-case',str(case),'-time','0.00018','-fields','('+' '.join(INPUTS)+')','-noFunctionObjects'],name+'_captureReconstruct'))
        else:
            before=case_fingerprint(case)
            commands.append(run(work,['mapFieldsPar','-case',str(case),str(work/NAMES[0]),'-consistent',
                '-sourceTime','0.00018','-mapMethod','cellVolumeWeight','-fields','('+' '.join(INPUTS)+')','-no-lagrangian'],name+'_mapping'))
            report['mapped_changed_files']=mapping_guard(before,case_fingerprint(case))
            report['mapped_inputs_changed']=bool(report['mapped_changed_files'])
            # Native fields are deliberately mapped, not claimed equal across meshes.
            commands.append(run(work,['decomposePar','-case',str(case),'-time','0.00018','-noFunctionObjects'],name+'_decompose'))
            partition_hashes=[]
            for rank in range(48):
                relative=f'processor{rank}/constant/polyMesh/cellProcAddressing'
                paths=[c/relative for c in (work/NAMES[1],case)]
                paths=[p if p.is_file() else p.with_name(p.name+'.gz') for p in paths]
                digests=[sha(p) for p in paths]
                if digests[0]!=digests[1]:raise ValueError('Fine optical variants use different rank cell ownership')
                partition_hashes.append(digests[0])
            report['fine_partition_sha256']=partition_hashes
        set_entry(case/'system/controlDict','frozenLaserProbe','trace')
        for rank in range(48):
            for field in INPUTS:
                if not (case/f'processor{rank}/0.00018'/field).is_file():raise ValueError('Missing frozen rank input')
        commands.append(run(work,[sys.executable,str(Path(__file__).with_name('run_probe.py')),'--case',str(case),'--wall-hours',str(5/60)],name+'_traceJob'))
        trace=read_trace(case,name)
        if material_hashes(case)!=physics_hashes:raise ValueError('Frozen job changed serial material fields')
        outputs.append(trace)
        report['cases'].append(dict(variant=name,diagnostics=trace[2],profile=trace[3],run=trace[1],
            material_unchanged_gate=True,optical_input_sha256={n:sha(case/'0.00018'/n) for n in INPUTS}))
        save()
    jobs=captures+[o[1] for o in outputs]
    for key in ('solver_sha256','laser_library_sha256'):
        if not jobs[0].get(key) or len({j.get(key) for j in jobs})!=1:raise ValueError('Frozen binary provenance differs')
    if any(case_fingerprint(s)!=h for s,h in zip(sources,source_hashes)):raise ValueError('Source changed during optical probe')
    report.update(complete=True,source_unchanged_gate=True,
        contrasts=contrasts([o[2]['depositedPower'] for o in outputs]))
    save();return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit',type=Path,required=True);p.add_argument('--work',type=Path,required=True);a=p.parse_args()
    try:
        r=execute(a.audit,a.work)
        for c in r['cases']:print(c['variant'],'depositedPower W:',c['diagnostics']['depositedPower'])
        print('Frozen optical probe complete; no CFD advanced; production approved: False')
    except (ValueError,KeyError,OSError,StopIteration,subprocess.SubprocessError) as e:p.exit(1,f'Local optics probe failed: {e}\n')

if __name__=='__main__':main()
