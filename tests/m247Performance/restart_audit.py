#!/usr/bin/env python3
"""Audit existing static local meshes and mapped restart fluxes; never run CFD."""
import argparse
import json
from pathlib import Path
import re
import subprocess
from collect_probe import parse_records
from local_refinement import moments,compare_moments,mesh_summary,concavity_summary,run
from region_audit import sha

def geometry_qualification(text,diagnostic=None):
    native=mesh_summary(text)
    if native['passed']:
        return dict(native=native,qualified=True,basis='native_mesh_ok')
    # All native failures must be exclusively the coplanar/concave-cell test.
    flags=re.findall(r'^\s*\*\*\*(.*)$',text,re.M)
    flat=re.search(r'Face flatness .*?min\s*=\s*([0-9.eE+-]+)',text)
    qualified=bool(native['failed_checks']==1 and native['concave_cells']>0 and len(flags)==1
        and flags[0].startswith('Concave cells (using face planes) found') and flat
        and float(flat[1])>=1-1e-12 and diagnostic and diagnostic['count']==native['concave_cells']
        and diagnostic['worstPlaneDistance']<=1e-15 and diagnostic['maxRelativePlaneDistance']<=1e-10
        and diagnostic['aboveRelative1e9']==0)
    return dict(native=native,qualified=qualified,
        basis='coplanar_transition_with_roundoff_only_outward_distance' if qualified else 'rejected',
        absolute_limit_m=1e-15,relative_limit=1e-10,minimum_face_flatness=1-1e-12)

def flux_record(text):
    rows=parse_records(text,'M247_RESTART_FLUX')
    required=('schema','cells','divL1','divRMS','divMax','netFlux','Umax',
              'velocityFluxDifference','velocityFluxAbs','alphaFluxAbs','internalFaces','zeroInternalFluxFaces')
    if len(rows)!=1 or not re.search(r'^End\s*$',text,re.M):raise ValueError('Incomplete restart flux audit')
    r=rows[0]
    if any(k not in r for k in required) or r['schema']!=1:raise ValueError('Wrong restart flux schema')
    for key in required:
        if key not in ('netFlux','schema') and r[key]<0:raise ValueError('Negative restart flux metric')
    for key in ('cells','internalFaces','zeroInternalFluxFaces'):
        if r[key]!=int(r[key]):raise ValueError('Noninteger restart mesh count')
    if r['cells']<=0 or r['zeroInternalFluxFaces']>r['internalFaces']:raise ValueError('Invalid restart mesh counts')
    return r

def case_fingerprint(case):
    files=[]
    for relative in ('constant','system','0.00018'):
        for p in (case/relative).rglob('*'):
            if 'sets' in p.relative_to(case).parts:continue # checkMesh writes diagnostic sets only
            if p.is_symlink():raise ValueError('Case symlinks unsupported')
            if p.is_file():files.append((p.relative_to(case).as_posix(),sha(p)))
    if not files:raise ValueError('Empty case fingerprint')
    return dict(sorted(files))

def audit(previous,work,utility):
    previous,work,utility=map(lambda p:Path(p).resolve(),(previous,work,utility))
    if previous==work or previous in work.parents or work in previous.parents:raise ValueError('Output overlaps preview')
    report=json.loads((previous/'localRefinementReview.json').read_text())
    if report.get('schema')!=2 or not report.get('complete') or report.get('production_approved'):
        raise ValueError('Complete unpromoted sizing preview required')
    if [v['variant'] for v in report['variants']]!=['localRefine4','localRefine10']:
        raise ValueError('Both sizing previews required')
    if (work/'restartAuditInputs.json').exists():raise ValueError('Choose fresh audit output')
    work.mkdir(parents=True,exist_ok=True)
    inputs=dict(schema=1,previous_work=str(previous),preview_report_sha256=sha(previous/'localRefinementReview.json'),
        utility_sha256=sha(utility),read_only_fields=True,no_cfd=True)
    (work/'restartAuditInputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
    results=[];commands=[]
    review=dict(schema=1,inputs=inputs,cases=results,commands=commands,complete=False,
        geometry_qualification_gate=False,restart_ready=False,production_approved=False,
        note='Native mesh failures retained. Scoped qualification only covers coplanar transition faces with bounded plane excursions and no other native failures. Flux metrics are observations, not continuity/enthalpy/interface approval. No field writes, pressure projection or CFD.')
    def save():
        (work/'localRestartReview.json').write_text(json.dumps(review,indent=2)+'\n')
    save()
    for name in ('coarse','localRefine4','localRefine10'):
        case=previous/name;fingerprint=case_fingerprint(case)
        commands.append(run(work,['checkMesh','-case',str(case),'-allGeometry','-allTopology','-noFunctionObjects'],name+'_restartCheckMesh'))
        quality_text=(work/(name+'_restartCheckMesh.log')).read_text();native=mesh_summary(quality_text)
        command=[str(utility),'-case',str(case),'-restart']
        if native['concave_cells']:command+=['-concavity']
        commands.append(run(work,command,name+'_restart'))
        text=(work/(name+'_restart.log')).read_text();state=moments(text);flux=flux_record(text)
        expected=report['before'] if name=='coarse' else next(v['moments'] for v in report['variants'] if v['variant']==name)
        if state!=expected or flux['cells']!=state['cells']:raise ValueError('Restart state differs from preview')
        if fingerprint!=case_fingerprint(case):raise ValueError('Case fields/mesh changed during read-only audit')
        diagnostic=concavity_summary(text,native['concave_cells']) if native['concave_cells'] else None
        row=dict(case=name,moments=state,flux=flux,geometry=geometry_qualification(quality_text,diagnostic),
            concavity=diagnostic,files_sha256=fingerprint,unchanged_files_gate=True)
        if name!='coarse':
            base=results[0]['flux']
            row['continuity_change']={k:dict(coarse=base[k],refined=flux[k],
                ratio=flux[k]/base[k] if base[k] else None) for k in ('divL1','divRMS','divMax','velocityFluxDifference')}
            row['mapping_moments']=compare_moments(results[0]['moments'],state)
        results.append(row);save()
    review['complete']=True
    review['geometry_qualification_gate']=all(r['geometry']['qualified'] for r in results)
    save();return review

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--previous',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--utility',type=Path,required=True);a=p.parse_args()
    try:
        r=audit(a.previous,a.work,a.utility)
        for c in r['cases']:print(c['case'],'geometry qualified:',c['geometry']['qualified'],'divL1/RMS/max:',c['flux']['divL1'],c['flux']['divRMS'],c['flux']['divMax'])
        print('Audit complete. Restart ready: False; no CFD advanced.')
        if not r['geometry_qualification_gate']:p.exit(2,'Geometry qualification rejected.\n')
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as e:p.exit(1,f'Restart audit failed: {e}\n')

if __name__=='__main__':main()
