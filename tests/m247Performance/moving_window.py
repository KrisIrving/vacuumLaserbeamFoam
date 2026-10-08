#!/usr/bin/env python3
"""Bounded moving fine-window topology/field-mapping prototype on real M247 data."""
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import time
from collect_probe import parse_records
from local_refinement import mesh_summary,concavity_summary
from restart_audit import case_fingerprint,geometry_qualification
from prepare_probe import set_entry
from region_audit import sha

CENTRES=(80e-6,160e-6,0.,80e-6)
BASE_CELLS=756000
MAX_CELLS=2000000


def dynamic_dictionary():
    return '''FoamFile { version 2.0; format ascii; class dictionary; object dynamicMeshDict; }
dynamicFvMesh dynamicRefineFvMesh;
dynamicRefineFvMeshCoeffs
{
    refineInterval 1;
    field movingRefineMask;
    lowerRefineLevel 0.5;
    upperRefineLevel 1.5;
    unrefineLevel 0.1;
    nBufferLayers 1;
    maxRefinement 1;
    maxCells 2000000;
    correctFluxes ();
    dumpLevel true;
}
'''


def collect(text):
    rows=parse_records(text,'M247_MOVING_WINDOW')
    endings=parse_records(text,'M247_MOVING_WINDOW_END')
    if len(rows)!=9 or endings!=[dict(schema=1,updates=8,advancedPhysics=0)] or not re.search(r'^End\s*$',text,re.M):
        raise ValueError('Incomplete moving-window native run')
    keys=('schema','step','physicalTime','auditTime','centreX','cells','fineCells','protectedCells',
        'interiorCells','coveredCells','updateWall_s','volume','metalVolume',
        'mappedMetalTemperature','mappedLiquidVolume','directMetalTemperature',
        'directLiquidVolume','alphaMin','alphaMax','epsilonMin','epsilonMax','Tmin','Tmax')
    for i,row in enumerate(rows):
        if any(k not in row or not math.isfinite(row[k]) for k in keys):raise ValueError('Missing/nonfinite moving record')
        if row['schema']!=1 or row['step']!=i or abs(row['physicalTime']-.00018)>1e-12 or abs(row['auditTime']-(.00018+i*1e-9))>1e-12:
            raise ValueError('Wrong moving record index/time')
        if not BASE_CELLS<=row['cells']<=MAX_CELLS or row['cells']!=int(row['cells']):raise ValueError('Cell budget/count failed')
        if any(row[k]!=int(row[k]) or row[k]<0 for k in ('fineCells','protectedCells','interiorCells','coveredCells')):
            raise ValueError('Invalid coverage counts')
        if not 0<=row['coveredCells']<=row['interiorCells']<=row['cells'] or row['updateWall_s']<0 or row['volume']<=0:
            raise ValueError('Invalid coverage/timing/volume')
        if row['alphaMin'] < -1e-8 or row['alphaMax']>1+1e-8 or row['epsilonMin'] < -1e-8 or row['epsilonMax']>1+1e-8 or row['Tmin']<=0 or row['Tmax']<row['Tmin']:
            raise ValueError('Invalid mapped material bounds')
        expected=CENTRES[0] if i==0 else CENTRES[(i-1)//2]
        if abs(row['centreX']-expected)>1e-12:raise ValueError('Wrong window path')
    if rows[0]['cells']!=BASE_CELLS or rows[0]['fineCells']!=0:raise ValueError('Expected unrefined coarse initial state')
    baseline=rows[0];linear=[];nonlinear=[]
    for row in rows[1:]:
        for key in ('volume','metalVolume','mappedMetalTemperature','mappedLiquidVolume'):
            delta=abs(row[key]-baseline[key]);limit=1e-20+1e-9*abs(baseline[key])
            linear.append(dict(step=int(row['step']),quantity=key,difference=delta,limit=limit,passed=delta<=limit))
        for key in ('directMetalTemperature','directLiquidVolume'):
            nonlinear.append(dict(step=int(row['step']),quantity=key,value=row[key],
                difference_from_initial=row[key]-baseline[key],
                relative_difference=(row[key]-baseline[key])/max(abs(baseline[key]),1e-30)))
    # Every second update is the settled state at that path position.
    settled=rows[2::2]
    coverage=all(r['interiorCells']>0 and r['coveredCells']==r['interiorCells'] for r in settled)
    unrefined=re.findall(r'Unrefined from\s+(\d+)\s+to\s+(\d+)\s+cells',text)
    coarsened=sum(int(a)-int(b) for a,b in unrefined if int(a)>int(b))
    return dict(records=rows,linear_mapping=linear,nonlinear_product_drift=nonlinear,
        linear_mapping_gate=all(r['passed'] for r in linear),coverage_gate=coverage,
        coarsened_cell_reductions=coarsened,coarsening_gate=coarsened>0,
        maximum_cells=max(r['cells'] for r in rows),update_wall_s=sum(r['updateWall_s'] for r in rows))


def execute(audit_work,work,utility,mesh_utility):
    audit_work,work,utility,mesh_utility=map(lambda p:Path(p).resolve(),(audit_work,work,utility,mesh_utility))
    audit=json.loads((audit_work/'localRestartReview.json').read_text())
    if not audit.get('complete') or not audit.get('geometry_qualification_gate'):raise ValueError('Completed original restart audit required')
    preview=Path(audit['inputs']['previous_work']).resolve();source=preview/'coarse'
    if any(p==work or p in work.parents or work in p.parents for p in (audit_work,preview)):
        raise ValueError('Output overlaps original data')
    expected=next(c['files_sha256'] for c in audit['cases'] if c['case']=='coarse')
    if case_fingerprint(source)!=expected:raise ValueError('Original coarse audited files changed')
    if (source/'constant/dynamicMeshDict').exists():raise ValueError('Expected static coarse source')
    work.mkdir(parents=True,exist_ok=True)
    if (work/'movingWindowReview.json').exists():raise ValueError('Choose fresh output')
    case=work/'movingWindow';case.mkdir()
    for part in ('constant','system','0.00018'):shutil.copytree(source/part,case/part)
    if case_fingerprint(case)!=expected:raise ValueError('Serial copy hash mismatch')
    (case/'constant/dynamicMeshDict').write_text(dynamic_dictionary())
    dictionary='''FoamFile { version 2.0; format ascii; class dictionary; object movingWindowAuditDict; }
halfX 96e-6;
halfZ 96e-6;
interiorMargin 16e-6;
maxCells 2000000;
centres (80e-6 160e-6 0 80e-6);
'''
    (case/'system/movingWindowAuditDict').write_text(dictionary)
    for key,value in (('startFrom','startTime'),('startTime','0.00018'),('timePrecision','12')):
        set_entry(case/'system/controlDict',key,value)
    shutil.copy2(case/'constant/dynamicMeshDict',work/'movingWindow_dynamicMeshDict')
    shutil.copy2(case/'system/movingWindowAuditDict',work/'movingWindow_auditDict')
    report=dict(schema=1,complete=False,production_approved=False,no_cfd=True,
        source_case=str(source),source_sha256=expected,original_audit_sha256=sha(audit_work/'localRestartReview.json'),
        utility_sha256=sha(utility),commands=[],quality=[],
        note='Mechanical refinement/coarsening path on frozen180us fields; synthetic snapshot times. Only T/alpha/epsilon and two product proxies registered. Saved cases are NOT valid solver restarts. No enthalpy, flux, isoAdvector or speedup approval.')
    def save():(work/'movingWindowReview.json').write_text(json.dumps(report,indent=2)+'\n')
    save();deadline=time.monotonic()+1800
    def launch(command,name):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise ValueError('30 minute native-run budget exhausted')
        started=time.monotonic()
        with (work/(name+'.log')).open('x') as stream:
            subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=min(1200,remaining))
        report['commands'].append(dict(command=command,elapsed_wall_s=time.monotonic()-started,log=name+'.log'));save()
    launch([str(utility),'-case',str(case)],'movingWindow_updates')
    report['mapping']=collect((work/'movingWindow_updates.log').read_text());save()
    for step in range(1,9):
        slot=format(.00018+step*1e-9,'.12g');name=f'movingWindow_step{step}'
        launch(['checkMesh','-case',str(case),'-time',slot,'-allGeometry','-allTopology','-noFunctionObjects'],name+'_quality')
        text=(work/(name+'_quality.log')).read_text();q=mesh_summary(text);diag=None
        if q['concave_cells']:
            launch([str(mesh_utility),'-case',str(case),'-auditTime',slot,'-geometryOnly','-concavity'],name+'_concavity')
            diag=concavity_summary((work/(name+'_concavity.log')).read_text(),q['concave_cells'])
        report['quality'].append(dict(step=step,auditTime=slot,qualification=geometry_qualification(text,diag)));save()
    if case_fingerprint(source)!=expected:raise ValueError('Original coarse source changed')
    report.update(complete=True,source_unchanged_gate=True,prototype_gate=all((
        report['mapping']['linear_mapping_gate'],report['mapping']['coverage_gate'],
        report['mapping']['coarsening_gate'],all(q['qualification']['qualified'] for q in report['quality']))))
    save();return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('audit','work','utility','mesh-utility'):p.add_argument('--'+key,type=Path,required=True)
    a=p.parse_args()
    try:
        r=execute(a.audit,a.work,a.utility,a.mesh_utility)
        print('Moving window prototype gate:',r['prototype_gate'],'maximum cells:',r['mapping']['maximum_cells'])
        print('Mesh update wall seconds:',r['mapping']['update_wall_s'],'no CFD advanced')
        if not r['prototype_gate']:p.exit(2,'Prototype gate failed; send review archive.\n')
    except (ValueError,KeyError,OSError,StopIteration,subprocess.SubprocessError) as e:p.exit(1,f'Moving window probe failed: {e}\n')


if __name__=='__main__':main()
