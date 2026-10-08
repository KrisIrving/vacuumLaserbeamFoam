#!/usr/bin/env python3
"""Project copied four-layer restart flux; gate a 0.2 us/15 minute CFD pilot."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from collect_probe import read_probe,parse_records
from collect_thermal_validation import residual_gate
from local_refinement import moments,run
from restart_audit import case_fingerprint,flux_record
from prepare_probe import set_entry
from region_audit import sha

def projection_gate(after,coarse):
    limits={k:max(floor,1.05*coarse[k]) for k,floor in (('divL1',.05),('divRMS',15),('divMax',15000))}
    return dict(passed=all(after[k]<=limit for k,limit in limits.items()),limits=limits,
                note='Pilot-only screening against coarse continuity; not production tolerances.')

def unchanged_except_phi(before,after):
    changed=sorted(k for k in set(before)|set(after) if before.get(k)!=after.get(k))
    if any(k!='0.00018/phi' for k in changed):raise ValueError('Projection changed a protected field/mesh/system file')
    return changed

def execute(audit_work,work,utility):
    audit_work,work,utility=map(lambda p:Path(p).resolve(),(audit_work,work,utility))
    audit=json.loads((audit_work/'localRestartReview.json').read_text())
    if not audit.get('complete') or not audit.get('geometry_qualification_gate') or audit.get('production_approved'):
        raise ValueError('Completed qualified unpromoted restart audit required')
    preview=Path(audit['inputs']['previous_work']).resolve()
    for parent in (audit_work,preview):
        if work==parent or parent in work.parents or work in parent.parents:raise ValueError('Output overlaps input')
    source=preview/'localRefine4';row=next(r for r in audit['cases'] if r['case']=='localRefine4')
    coarse=next(r for r in audit['cases'] if r['case']=='coarse')['flux']
    if case_fingerprint(source)!=row['files_sha256']:raise ValueError('Source differs from audited restart')
    if (work/'fluxPilotInputs.json').exists():raise ValueError('Choose fresh output')
    work.mkdir(parents=True,exist_ok=True);case=work/'rayTraversalCached';case.mkdir()
    for part in ('constant','system','0.00018'):shutil.copytree(source/part,case/part)
    if case_fingerprint(case)!=row['files_sha256']:raise ValueError('Copy hash mismatch')
    meta=json.loads((preview/'previewInputs.json').read_text())['copied_restart']
    if meta['ranks']!=48:raise ValueError('Expected original48rank controls')
    meta.update(variant='rayTraversalCached',duration_us=.2,start_s=.00018,end_s=.0001802,
        purpose='Experimental localRefine4 projected-flux restart compatibility; not a matched speedup test',
        local_refinement=True,production_approved=False)
    (case/'probe.json').write_text(json.dumps(meta,indent=2)+'\n')
    set_entry(case/'system/fvSolution','solvers/M247FluxPotential',
        '{ solver PCG; preconditioner DIC; tolerance 1e-13; relTol 0; maxIter 10000; }')
    for key,value in (('startFrom','startTime'),('startTime','0.00018'),('endTime','0.0001802'),
        ('stopAt','endTime'),('writeInterval','1e-7'),('writePrecision','17'),('writeCompression','off'),('writeFormat','ascii')):
        set_entry(case/'system/controlDict',key,value)
    inputs=dict(schema=1,audit_sha256=sha(audit_work/'localRestartReview.json'),source_case=str(source),
        source_files_sha256=row['files_sha256'],utility_sha256=sha(utility),duration_us=.2,wall_budget_minutes=15,
        no_source_writes=True,copy_hash_gate=True)
    (work/'fluxPilotInputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
    commands=[];report=dict(schema=1,inputs=inputs,commands=commands,complete=False,
        projection_gate=False,pilot_gate=False,production_approved=False)
    def save():(work/'fluxPilotReview.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    before_hash=case_fingerprint(case)
    commands.append(run(work,[str(utility),'-case',str(case),'-restart'],'localProjected_before'))
    before_text=(work/'localProjected_before.log').read_text()
    if moments(before_text)!=row['moments'] or flux_record(before_text)!=row['flux']:
        raise ValueError('Copied restart metrics differ from audited state')
    commands.append(run(work,[str(utility),'-case',str(case),'-restart','-project'],'localProjected_projection'))
    projection_text=(work/'localProjected_projection.log').read_text()
    markers=parse_records(projection_text,'M247_FLUX_PROJECTION')
    if len(markers)!=1 or any(markers[0].get(k)!=v for k,v in dict(schema=1,passes=5,wrotePhi=1,wroteU=0,advancedTime=0).items()):
        raise ValueError('Missing flux-only projection marker')
    changed=unchanged_except_phi(before_hash,case_fingerprint(case))
    # Audit the written field, not only the in-memory result of projection.
    commands.append(run(work,[str(utility),'-case',str(case),'-restart'],'localProjected_after'))
    after_text=(work/'localProjected_after.log').read_text();after=flux_record(after_text)
    if moments(after_text)!=row['moments']:raise ValueError('Projection altered material moments')
    gate=projection_gate(after,coarse)
    report.update(before=row['flux'],after=after,continuity_screen=gate,changed_files=changed,projection_gate=gate['passed'])
    save()
    if not gate['passed']:raise ValueError('Projection continuity screen failed; CFD not launched')
    commands.append(run(work,['decomposePar','-case',str(case),'-time','0.00018','-noFunctionObjects'],'localProjected_decompose'))
    commands.append(run(work,[sys.executable,str(Path(__file__).with_name('run_probe.py')),'--case',str(case),'--wall-hours','0.25'],'localProjected_pilot'))
    metadata,summary,diagnostics=read_probe(case)
    report.update(pilot=summary,physical_diagnostics=diagnostics,
        thermal_gate=summary['thermal_limit_hits']==0 and residual_gate(case,metadata,summary['steps']))
    save()
    commands.append(run(work,['reconstructPar','-case',str(case),'-time','0.0001802','-noFunctionObjects'],'localProjected_reconstruct'))
    commands.append(run(work,[str(utility),'-case',str(case),'-restart','-auditTime','0.0001802'],'localProjected_final'))
    final_text=(work/'localProjected_final.log').read_text()
    report['final_state']=moments(final_text,expected_time=.0001802)
    report['final_flux']=flux_record(final_text)
    if report['final_state']['cells']!=row['moments']['cells']:raise ValueError('Pilot changed static mesh')
    if case_fingerprint(source)!=row['files_sha256']:raise ValueError('Source changed during pilot')
    report.update(complete=True,pilot_gate=report['thermal_gate'],source_unchanged_gate=True,
        note='Single0.2us local-grid compatibility pilot. No matched coarse interval, mesh convergence, physical equivalence or production approval. Cost extrapolation needs a longer mature-window pilot.')
    save();return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--audit',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--utility',type=Path,required=True);a=p.parse_args()
    try:
        r=execute(a.audit,a.work,a.utility)
        print('Projection:',r['projection_gate'],'short pilot:',r['pilot_gate'],'production approved: False')
        if not r['pilot_gate']:p.exit(2,'Pilot convergence gate failed.\n')
    except (ValueError,KeyError,OSError,StopIteration,subprocess.SubprocessError) as e:p.exit(1,f'Flux pilot failed: {e}\n')

if __name__=='__main__':main()
