#!/usr/bin/env python3
"""Build two static local-refinement previews from copied 180-us fields, no CFD."""
import argparse
import json
from pathlib import Path
import re
import shutil
import subprocess
import time
from collect_probe import parse_records
from prepare_probe import prepare
from region_audit import sha

def selection_dictionary(layers):
    if layers not in (4,10): raise ValueError('Only 4/10-layer sizing previews supported')
    return '''FoamFile { version 2.0; format ascii; class dictionary; object topoSetDict; }
actions
(
    { name refineCells; type cellSet; action new; source fieldToCell;
      field alpha.metal; min 0.001; max 0.999; }
    { name refineCells; type cellSet; action add; source fieldToCell;
      field T; min 1368.15; max 1e30; }
    { name refineCells; type cellSet; action add; source haloToCell;
      steps LAYERS; }
);
'''.replace('LAYERS',str(layers))

def moments(text):
    records=parse_records(text,'M247_MESH_MOMENTS')
    if len(records)!=1 or not re.search(r'^End\s*$',text,re.M):raise ValueError('Incomplete moment check')
    r=records[0]
    required=('schema','time','cells','volume','metalVolume','liquidVolume','metalTemperatureMoment','alphaMin','alphaMax','epsilonMin','epsilonMax','Tmin','Tmax')
    if any(k not in r for k in required) or r['schema']!=1 or abs(r['time']-.00018)>1e-12:
        raise ValueError('Wrong moment schema/time')
    if (r['cells']!=int(r['cells']) or r['cells']<=0 or r['volume']<=0
        or any(r[k]<0 for k in ('metalVolume','liquidVolume','metalTemperatureMoment'))
        or r['alphaMin'] < -1e-8 or r['alphaMax'] > 1+1e-8
        or r['epsilonMin'] < -1e-8 or r['epsilonMax'] > 1+1e-8
        or r['Tmin']<=0 or r['Tmax']<r['Tmin']):
        raise ValueError('Invalid mapped state')
    return r

def compare_moments(before,after):
    rows=[]
    for key in ('volume','metalVolume','liquidVolume','metalTemperatureMoment'):
        delta=abs(after[key]-before[key]);allowed=1e-20+1e-9*abs(before[key])
        rows.append(dict(quantity=key,before=before[key],after=after[key],difference=delta,
                         allowed_difference=allowed,passed=delta<=allowed))
    return rows

def selected_count(text):
    if not re.search(r'^End\s*$',text,re.M):raise ValueError('Incomplete topoSet')
    sizes=re.findall(r'cellSet\s+refineCells\s+now size\s+(\d+)',text)
    if len(sizes)!=3:raise ValueError('Expected three completed selection actions')
    counts=list(map(int,sizes))
    if not 0<counts[0]<=counts[1]<=counts[2]<=756000:raise ValueError('Invalid selection counts')
    return counts

def mesh_ok(text):
    if not re.search(r'^\s*Mesh OK\.\s*$',text,re.M) or not re.search(r'^End\s*$',text,re.M):
        raise ValueError('checkMesh did not certify mesh quality')

def mesh_summary(text):
    if not re.search(r'^End\s*$',text,re.M):raise ValueError('Incomplete checkMesh')
    failed=re.findall(r'^Failed (\d+) mesh checks?\.',text,re.M)
    passed=bool(re.search(r'^\s*Mesh OK\.\s*$',text,re.M))
    if passed == bool(failed) or len(failed)>1:raise ValueError('Ambiguous checkMesh result')
    concave=re.findall(r'Concave cells .*?number of cells:\s*(\d+)',text)
    return dict(passed=passed,failed_checks=int(failed[0]) if failed else 0,
                concave_cells=int(concave[0]) if concave else 0)

def concavity_summary(text,expected_count):
    rows=parse_records(text,'M247_MESH_CONCAVITY')
    required=('schema','count','worstPlaneDistance','maxRelativePlaneDistance','aboveRelative1e9',
              'xmin','xmax','ymin','ymax','zmin','zmax')
    if len(rows)!=1 or not re.search(r'^End\s*$',text,re.M):raise ValueError('Incomplete concavity diagnostic')
    r=rows[0]
    if any(k not in r for k in required) or r['schema']!=1 or r['count']!=expected_count:
        raise ValueError('Concavity set/count mismatch')
    if (r['worstPlaneDistance']<0 or r['maxRelativePlaneDistance']<0
        or r['aboveRelative1e9']!=int(r['aboveRelative1e9']) or not 0<=r['aboveRelative1e9']<=r['count']
        or any(r[c+'min']>r[c+'max'] for c in 'xyz')):raise ValueError('Invalid concavity diagnostic')
    return r

def copy_serial_restart(previous,work):
    previous,work=Path(previous).resolve(),Path(work).resolve()
    if previous==work or previous in work.parents or work in previous.parents:
        raise ValueError('Resume output overlaps previous work')
    inputs=json.loads((previous/'previewInputs.json').read_text())
    meta=inputs['copied_restart']
    if inputs.get('schema')!=1 or not inputs.get('preview_only') or meta.get('ranks')!=48 or meta.get('checkpoint')!='0.00018':
        raise ValueError('Wrong resume preview/restart')
    before=moments((previous/'coarseMoments.log').read_text())
    if before['cells']!=756000:raise ValueError('Wrong resume mesh size')
    mesh_ok((previous/'coarseCheckMesh.log').read_text())
    coarse=work/'coarse';coarse.mkdir()
    hashes={}
    for relative in ('constant','system',meta['checkpoint']):
        origin=previous/'coarse'/relative
        for p in origin.rglob('*'):
            if p.is_symlink():raise ValueError('Resume symlink not permitted')
            if p.is_file():hashes[str(p.relative_to(previous/'coarse'))]=sha(p)
        shutil.copytree(origin,coarse/relative)
    if not hashes or any(sha(coarse/p)!=h for p,h in hashes.items()):raise ValueError('Resume copy hash mismatch')
    for name in ('coarseMoments.log','coarseCheckMesh.log'):
        shutil.copyfile(previous/name,work/('resume'+name[0].upper()+name[1:]))
    evidence=dict(schema=1,previous_work=str(previous),previous_inputs=inputs,
                  previous_inputs_sha256=sha(previous/'previewInputs.json'),copied_files_sha256=hashes,
                  before=before,copy_hash_gate=True)
    (work/'resumeInputs.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return meta,before

def run(work,command,name):
    with (work/(name+'.log')).open('x') as log:
        started=time.monotonic()
        subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=1200)
    return dict(command=command,elapsed_wall_s=time.monotonic()-started,log=name+'.log')

def preview(source,work,utility,max_cells=3000000,resume=None):
    source,work,utility=map(lambda p:Path(p).resolve(),(source,work,utility))
    if source==work or source in work.parents or work in source.parents:raise ValueError('Output overlaps source')
    if max_cells<756000 or max_cells>6048000:raise ValueError('Invalid preview cell budget')
    if (work/'previewInputs.json').exists():raise ValueError('Preview already prepared')
    work.mkdir(parents=True,exist_ok=True)
    coarse=work/'coarse'
    if resume:
        meta,resumed_before=copy_serial_restart(resume,work)
        source=Path(meta['source']).resolve()
    else:
        meta=prepare(source,coarse,180,.2,'rayTraversalCached',corrected_rays=True)
    if meta['ranks']!=48:raise ValueError('Expected48ranks')
    if not (coarse/'constant/polyMesh').is_dir():raise ValueError('Original serial mesh required')
    if (coarse/'constant/dynamicMeshDict').exists():raise ValueError('Expected fixed original mesh')
    inputs=dict(schema=1,source=str(source),copied_restart=meta,utility_sha256=sha(utility),
        max_cells=max_cells,preview_only=True,production_approved=False)
    (work/'previewInputs.json').write_text(json.dumps(inputs,indent=2)+'\n')
    commands=[]
    # Reconstruct all native restart objects, including surface fields, on copies.
    if not resume:
        commands.append(run(work,['reconstructPar','-case',str(coarse),'-time','0.00018','-noFunctionObjects'],'reconstructPreview'))
    commands.append(run(work,[str(utility),'-case',str(coarse)],'coarseMoments'))
    before=moments((work/'coarseMoments.log').read_text())
    if before['cells']!=756000:raise ValueError('Unexpected original serial cell count')
    if resume and (before!=resumed_before):raise ValueError('Copied restart moments changed')
    commands.append(run(work,['checkMesh','-case',str(coarse),'-allGeometry','-allTopology','-noFunctionObjects'],'coarseCheckMesh'))
    mesh_ok((work/'coarseCheckMesh.log').read_text())
    results=[]
    report=dict(schema=2,inputs=inputs,before=before,variants=results,commands=commands,
        complete=False,geometry_mapping_gate=False,production_approved=False,
        note='Static180us mesh sizing only. Quality failure is retained, never waived; both variants are evaluated. Mapping moments are not enthalpy/flux or isoAdvector reconstruction checks. Graph halos do not guarantee metric distance. No CFD, future coverage or speedup established. Cost ratios assume twice as many timesteps and equal per-cell/MPI work.')
    def save_report():
        report['geometry_mapping_gate']=bool(report['complete']) and len(results)==2 and all(r['geometry_mapping_gate'] for r in results)
        (work/'localRefinementReview.json').write_text(json.dumps(report,indent=2)+'\n')
    save_report()
    for layers in (4,10):
        name=f'localRefine{layers}';case=work/name
        case.mkdir()
        for relative in ('constant','system',meta['checkpoint']):
            shutil.copytree(coarse/relative,case/relative)
        dictionary=selection_dictionary(layers)
        (case/'system/topoSetDict').write_text(dictionary)
        (work/(name+'_topoSetDict')).write_text(dictionary)
        commands.append(run(work,['topoSet','-case',str(case),'-time','0.00018','-noFunctionObjects'],name+'_selection'))
        counts=selected_count((work/(name+'_selection.log')).read_text())
        proposed=756000+7*counts[-1]
        result=dict(variant=name,halo_layers=layers,interface_seed_cells=counts[0],
            thermal_union_cells=counts[1],selected_cells=counts[2],proposed_cells=proposed,
            cell_budget=max_cells,production_approved=False)
        if proposed>max_cells:
            result.update(status='skipped_cell_budget',geometry_mapping_gate=False)
            results.append(result);save_report();continue
        commands.append(run(work,['refineHexMesh','-case',str(case),'refineCells','-overwrite','-noFunctionObjects'],name+'_refinement'))
        commands.append(run(work,[str(utility),'-case',str(case)],name+'_moments'))
        after=moments((work/(name+'_moments.log')).read_text())
        result['actual_cells']=int(after['cells']);result['moments']=after
        result['mapping_moments']=compare_moments(before,after)
        if after['cells']<proposed or after['cells']>max_cells:raise ValueError('Actual refinement exceeds budget or omits selected cells')
        commands.append(run(work,['checkMesh','-case',str(case),'-allGeometry','-allTopology','-noFunctionObjects'],name+'_checkMesh'))
        quality=mesh_summary((work/(name+'_checkMesh.log')).read_text())
        result.update(status='completed' if quality['passed'] else 'failed_mesh_quality',mesh_quality=quality,
            geometry_mapping_gate=quality['passed'] and all(r['passed'] for r in result['mapping_moments']),
            cell_multiplier=after['cells']/before['cells'],
            assumed_work_vs_original=2*after['cells']/before['cells'],
            assumed_work_vs_global_edge_halving=after['cells']/(8*before['cells']))
        results.append(result)
        save_report()
        if quality['concave_cells']:
            commands.append(run(work,[str(utility),'-case',str(case),'-concavity'],name+'_concavity'))
            result['concavity_diagnostic']=concavity_summary((work/(name+'_concavity.log')).read_text(),quality['concave_cells'])
            save_report()
    report['complete']=True
    save_report()
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    p.add_argument('--utility',type=Path,required=True)
    p.add_argument('--resume',type=Path,help='Reuse verified serial coarse restart from a previous preview')
    a=p.parse_args()
    try:
        r=preview(a.source,a.work,a.utility,resume=a.resume)
        for v in r['variants']:print(v['variant'],v['status'],'proposed cells',v['proposed_cells'],'actual',v.get('actual_cells'))
        print('Geometry/mapping moment gate:',r['geometry_mapping_gate'],'No CFD advanced.')
        if not r['geometry_mapping_gate']:p.exit(2,'Preview skipped budget or failed mapping gates; not approved.\n')
    except (ValueError,OSError,subprocess.SubprocessError) as e:p.exit(1,f'Local refinement preview failed: {e}\n')

if __name__=='__main__':main()
