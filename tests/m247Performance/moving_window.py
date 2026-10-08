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


def smoke(work,utility,protect_wake=False):
    """Persist failure reason even when native execution or collection raises."""
    try:
        return _smoke(work,utility,protect_wake)
    except (ValueError,OSError,subprocess.SubprocessError) as error:
        target=work/'movingWindowSmokeReview.json'
        report=json.loads(target.read_text()) if target.exists() else dict(schema=1,complete=False)
        report.update(passed=False,failure_stage='small_mesh_preflight',
            error_type=type(error).__name__,error=str(error),
            large_case_started=False)
        target.write_text(json.dumps(report,indent=2)+'\n')
        raise


def _smoke(work,utility,protect_wake=False):
    """Exercise the identical native lifecycle on 2400 cells before real-case copying."""
    case=work/'movingWindowSmoke';case.mkdir()
    for name in ('constant','system','0.00018'):(case/name).mkdir()
    def dictionary(name,body):
        return f'FoamFile {{ version 2.0; format ascii; class dictionary; object {name}; }}\n'+body
    (case/'system/blockMeshDict').write_text(dictionary('blockMeshDict','''convertToMeters 1;
vertices
((-320e-6 0 -160e-6) (320e-6 0 -160e-6) (320e-6 960e-6 -160e-6) (-320e-6 960e-6 -160e-6)
 (-320e-6 0 160e-6) (320e-6 0 160e-6) (320e-6 960e-6 160e-6) (-320e-6 960e-6 160e-6));
blocks (hex (0 1 2 3 4 5 6 7) (20 12 10) simpleGrading (1 1 1));
edges ();
boundary (walls { type wall; faces ((0 4 7 3) (1 2 6 5) (0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7)); });
mergePatchPairs ();
'''))
    (case/'system/controlDict').write_text(dictionary('controlDict','''application m247MovingWindowCheck;
startFrom startTime; startTime 0.00018; stopAt endTime; endTime 0.000181;
deltaT 1e-9; writeControl timeStep; writeInterval 1; timePrecision 12; writePrecision 17;
writeFormat ascii; writeCompression off; runTimeModifiable false;
'''))
    (case/'system/fvSchemes').write_text(dictionary('fvSchemes','''ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; } divSchemes { default none; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; } snGradSchemes { default corrected; }
'''))
    (case/'system/fvSolution').write_text(dictionary('fvSolution','solvers {}\n'))
    (case/'constant/dynamicMeshDict').write_text(dynamic_dictionary())
    (case/'system/movingWindowAuditDict').write_text(dictionary('movingWindowAuditDict',
        'halfX 96e-6; halfZ 96e-6; interiorMargin 16e-6; maxCells 2000000; centres (80e-6 160e-6 0 80e-6);\n'+wake_controls(protect_wake)))
    for name,value,dimensions in (('T',1400,'0 0 0 1 0 0 0'),('alpha.metal',.5,'0 0 0 0 0 0 0'),('epsilon1',.25,'0 0 0 0 0 0 0')):
        (case/'0.00018'/name).write_text(f'''FoamFile {{ version 2.0; format ascii; class volScalarField; object {name}; }}
dimensions [{dimensions}]; internalField uniform {value};
boundaryField {{ walls {{ type zeroGradient; }} }}
''')
    if protect_wake:
        # blockMesh i-fastest numbering: a hot column outside every test window.
        values=[1600 if i%20==3 and 3<=i//240<=6 else 1400 for i in range(2400)]
        target=case/'0.00018/T';text=target.read_text()
        target.write_text(text.replace('internalField uniform 1400;',
            'internalField nonuniform List<scalar>\n2400\n(\n'+'\n'.join(map(str,values))+'\n);'))
        target=case/'0.00018/epsilon1'
        target.write_text(target.read_text().replace('internalField uniform 0.25;','internalField uniform 0;'))
    report=dict(schema=1,complete=False,passed=False,base_cells=2400,no_cfd=True,protect_wake=protect_wake)
    target=work/'movingWindowSmokeReview.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    deadline=time.monotonic()+120
    for command,name in ((['blockMesh','-case',str(case),'-noFunctionObjects'],'blockMesh'),
                         ([str(utility),'-case',str(case)],'updates')):
        remaining=deadline-time.monotonic()
        if remaining<=0:raise ValueError('Small-mesh preflight budget exhausted')
        with (work/('movingWindowSmoke_'+name+'.log')).open('x') as stream:
            subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True,timeout=remaining)
    mapping=collect((work/'movingWindowSmoke_updates.log').read_text(),base_cells=2400,require_wake=protect_wake)
    report.update(complete=True,mapping=mapping,passed=all(mapping[k] for k in ('linear_mapping_gate','coverage_gate','coarsening_gate','wake_gate')))
    target.write_text(json.dumps(report,indent=2)+'\n')
    if not report['passed']:raise ValueError('Small-mesh preflight gates failed: '+', '.join(k for k in ('linear_mapping_gate','coverage_gate','coarsening_gate','wake_gate') if not mapping[k])+'; large case not copied')
    return report


def wake_controls(enabled):
    return ('protectWake '+str(enabled).lower()+';\n'
            'hotTemperature 1537; liquidThreshold 1e-4; metalThreshold 1e-6;\n')


def collect(text,base_cells=BASE_CELLS,require_wake=False):
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
        if not base_cells<=row['cells']<=MAX_CELLS or row['cells']!=int(row['cells']):raise ValueError('Cell budget/count failed')
        if any(row[k]!=int(row[k]) or row[k]<0 for k in ('fineCells','protectedCells','interiorCells','coveredCells')):
            raise ValueError('Invalid coverage counts')
        if not 0<=row['coveredCells']<=row['interiorCells']<=row['cells'] or row['updateWall_s']<0 or row['volume']<=0:
            raise ValueError('Invalid coverage/timing/volume')
        if row['alphaMin'] < -1e-8 or row['alphaMax']>1+1e-8 or row['epsilonMin'] < -1e-8 or row['epsilonMax']>1+1e-8 or row['Tmin']<=0 or row['Tmax']<row['Tmin']:
            raise ValueError('Invalid mapped material bounds')
        expected=CENTRES[0] if i==0 else CENTRES[(i-1)//2]
        if abs(row['centreX']-expected)>1e-12:raise ValueError('Wrong window path')
    if rows[0]['cells']!=base_cells or rows[0]['fineCells']!=0:raise ValueError('Expected unrefined coarse initial state')
    history=parse_records(text,'M247_MOVING_V0')
    if len(history)!=8:raise ValueError('Missing old-volume initialization evidence')
    for i,row in enumerate(history):
        if any(row.get(k)!=v for k,v in dict(schema=1,step=i+1,cells=rows[i]['cells'],ready=1,maxDifference=0).items()):
            raise ValueError('Old-volume initialization count/state failed')
        previous,current=row.get('previousIndex'),row.get('currentIndex')
        if previous is None or current is None or current<=previous or current!=int(current) or previous!=int(previous):
            raise ValueError('Old-volume time index did not advance')
        if i and previous!=history[i-1]['currentIndex']:
            raise ValueError('Old-volume history indices are discontinuous')
    wake_gate=True
    selections=parse_records(text,'M247_MOVING_CANDIDATES')
    if require_wake:
        if len(selections)!=8:raise ValueError('Missing direct cell selection evidence')
        for i,selection in enumerate(selections):
            if any(selection.get(k)!=v for k,v in dict(schema=1,timeIndex=history[i]['currentIndex'],
                cells=rows[i]['cells'],directCellSelection=1).items()):
                raise ValueError('Direct selection index/count mismatch')
            requested,selected=selection.get('requested'),selection.get('selected')
            if requested is None or not math.isfinite(requested) or requested!=int(requested) or not 0<requested<=rows[i]['cells'] or selected!=requested:
                raise ValueError('Direct selection lost marked cells')
        for row in rows:
            if row.get('protectWake')!=1 or row.get('directCellSelection')!=1:raise ValueError('Direct wake protection not enabled')
            for key in ('wakeCells','wakeCoveredCells','outsideWakeCells'):
                value=row.get(key)
                if value is None or not math.isfinite(value) or value!=int(value) or not 0<=value<=row['cells']:
                    raise ValueError('Missing/invalid wake coverage evidence')
            if row['wakeCoveredCells']>row['wakeCells'] or row['outsideWakeCells']>row['wakeCells']:
                raise ValueError('Invalid wake coverage counts')
            value=row.get('mappedWakeVolume')
            if value is None or not math.isfinite(value) or value<0 or value>row['volume']*(1+1e-8):
                raise ValueError('Invalid mapped wake volume')
        initial=rows[0]['mappedWakeVolume']
        wake_gate=(initial>0 and all(r['wakeCells']>0 and r['wakeCoveredCells']==r['wakeCells'] for r in rows[2::2])
            and any(r['outsideWakeCells']>0 for r in rows[2::2])
            and all(abs(r['mappedWakeVolume']-initial)<=1e-20+1e-9*initial for r in rows[1:]))
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
    return dict(records=rows,old_volume_history=history,linear_mapping=linear,nonlinear_product_drift=nonlinear,
        wake_gate=wake_gate,wake_protection_required=require_wake,direct_cell_selections=selections,
        linear_mapping_gate=all(r['passed'] for r in linear),coverage_gate=coverage,
        coarsened_cell_reductions=coarsened,coarsening_gate=coarsened>0,
        maximum_cells=max(r['cells'] for r in rows),update_wall_s=sum(r['updateWall_s'] for r in rows))


def execute(audit_work,work,utility,mesh_utility,protect_wake=False):
    audit_work,work,utility,mesh_utility=map(lambda p:Path(p).resolve(),(audit_work,work,utility,mesh_utility))
    audit=json.loads((audit_work/'localRestartReview.json').read_text())
    if not audit.get('complete') or not audit.get('geometry_qualification_gate'):raise ValueError('Completed original restart audit required')
    preview=Path(audit['inputs']['previous_work']).resolve();source=preview/'coarse'
    if any(p==work or p in work.parents or work in p.parents for p in (audit_work,preview)):
        raise ValueError('Output overlaps original data')
    work.mkdir(parents=True,exist_ok=True)
    if (work/'movingWindowSmokeReview.json').exists():raise ValueError('Choose fresh output')
    smoke_report=smoke(work,utility,protect_wake)
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
    (case/'system/movingWindowAuditDict').write_text(dictionary+wake_controls(protect_wake))
    for key,value in (('startFrom','startTime'),('startTime','0.00018'),('timePrecision','12')):
        set_entry(case/'system/controlDict',key,value)
    shutil.copy2(case/'constant/dynamicMeshDict',work/'movingWindow_dynamicMeshDict')
    shutil.copy2(case/'system/movingWindowAuditDict',work/'movingWindow_auditDict')
    report=dict(schema=1,complete=False,production_approved=False,no_cfd=True,
        small_mesh_preflight=smoke_report,protect_wake=protect_wake,
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
    report['mapping']=collect((work/'movingWindow_updates.log').read_text(),require_wake=protect_wake);save()
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
        report['mapping']['coarsening_gate'],report['mapping']['wake_gate'],all(q['qualification']['qualified'] for q in report['quality']))))
    save();return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for key in ('audit','work','utility','mesh-utility'):p.add_argument('--'+key,type=Path,required=True)
    p.add_argument('--protect-wake',action='store_true')
    a=p.parse_args()
    try:
        r=execute(a.audit,a.work,a.utility,a.mesh_utility,a.protect_wake)
        print('Moving window prototype gate:',r['prototype_gate'],'maximum cells:',r['mapping']['maximum_cells'])
        print('Mesh update wall seconds:',r['mapping']['update_wall_s'],'no CFD advanced')
        if a.protect_wake:print('Frozen hot/molten wake coverage gate:',r['mapping']['wake_gate'])
        if not r['prototype_gate']:p.exit(2,'Prototype gate failed; send review archive.\n')
    except (ValueError,KeyError,OSError,StopIteration,subprocess.SubprocessError) as e:p.exit(1,f'Moving window probe failed: {e}\n')


if __name__=='__main__':main()
