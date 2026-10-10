"""Real full-solver fixed crop versus full domain, same 180..190us checkpoint.

Held checkpoint cut BCs are an explicit approximation, not global/local coupling.
No new thermal closure or physical source model is substituted.
"""
import argparse
import csv
import json
import math
import os
import re
from pathlib import Path
import shutil
import subprocess
import time
from collect_probe import parse_records, read_probe, METRICS
from collect_thermal_validation import residual_gate
from prepare_probe import prepare, set_entry, checkpoint, snapshot_digest
from region_audit import sha
from local_refinement import mesh_ok

ROOT=Path(__file__).resolve().parents[2]
FIELDS=('T','alpha','epsilon','Ux','Uy','Uz','p_rgh')


def save(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')


def rows(path):
    with Path(path).open(encoding='utf-8',newline='') as f:
        if f.readline().strip()!='x,y,z,volume,T,alpha,epsilon,Ux,Uy,Uz,p_rgh':
            raise ValueError('Native snapshot CSV schema mismatch')
        f.seek(0)
        for row in csv.DictReader(f):
            r={k:float(v) for k,v in row.items()}
            if any(not math.isfinite(v) for v in r.values()) or r['volume']<=0 or r['T']<=0:
                raise ValueError('Invalid native snapshot values')
            if not -1e-8<=r['alpha']<=1+1e-8 or not -1e-8<=r['epsilon']<=1+1e-8:
                raise ValueError('Native snapshot phase bounds failed')
            yield r


def key(r):return tuple(round(r[d]*1e12) for d in ('x','y','z'))


def inside(r,b):return all(b[d+'min']<=r[d]<=b[d+'max'] for d in ('x','y','z'))


def active(r):
    speed=math.sqrt(sum(r[d]**2 for d in ('Ux','Uy','Uz')))
    return (r['alpha']>=.05 and (r['T']>=1487 or r['epsilon']>=1e-6)) or (r['alpha']>=.01 and speed>=1) or speed>=10


def plan_window(path,snapshot,positions,halo=96e-6,details=None):
    # Preserve atmosphere and every active seed; the cold lower reservoir may be cropped.
    if not math.isfinite(halo) or halo<=0:raise ValueError('Positive metric buffer required')
    bounds={d+s:snapshot[d+s] for d in ('x','y','z') for s in ('min','max')}
    lo={d:math.inf for d in ('x','y','z')};hi={d:-math.inf for d in lo};count=0
    reasons={name:dict(cells=0,bounds={d+s:None for d in lo for s in ('min','max')}) for name in ('thermal_phase','metal_flow','fast_any_phase')}
    for r in rows(path):
        speed=math.sqrt(sum(r[d]**2 for d in ('Ux','Uy','Uz')))
        flags=(r['alpha']>=.05 and (r['T']>=1487 or r['epsilon']>=1e-6),r['alpha']>=.01 and speed>=1,speed>=10)
        for name,flag in zip(reasons,flags):
            if flag:
                q=reasons[name];q['cells']+=1
                for d in lo:
                    for side,op in (('min',min),('max',max)):
                        old=q['bounds'][d+side];q['bounds'][d+side]=r[d] if old is None else op(old,r[d])
        if any(flags):
            count+=1
            for d in lo:lo[d]=min(lo[d],r[d]);hi[d]=max(hi[d],r[d])
    if not count:raise ValueError('No active real melt-pool state found')
    for p in positions:
        for d,index in (('x',0),('y',1),('z',2)):
            lo[d]=min(lo[d],p[index]);hi[d]=max(hi[d],p[index])
    for d in lo:
        bounds[d+'min']=max(bounds[d+'min'],lo[d]-halo)
        if d!='y':bounds[d+'max']=min(bounds[d+'max'],hi[d]+halo)
    selected=sum(inside(r,bounds) for r in rows(path))
    result=dict(bounds=bounds,active_seed_cells=count,selected_cells=selected,
        full_cells=int(snapshot['cells']),halo_m=halo,cell_fraction=selected/snapshot['cells'],
        seed_categories=reasons,original_bounds={d+s:snapshot[d+s] for d in lo for s in ('min','max')},
        preserved_original_boundaries=[d+s for d in lo for s in ('min','max') if bounds[d+s]==snapshot[d+s]],
        policy='all active material/gas-jet seeds plus laser path and96um metric padding; preserve original atmosphere; permit cold lower-reservoir cut',
        note='No seed discarded and no buffer reduced. Extrema are cell centres; native cut-face audit is still required.')
    if details is not None:details.update(result)
    if not 48<selected<snapshot['cells']:raise ValueError('Safe active envelope does not reduce the mesh; no claimed acceleration')
    return result


def compare_fields(reference,candidate,bounds,initial=False):
    local={}
    for r in rows(candidate):
        k=key(r)
        if k in local:raise ValueError('Duplicate local coordinate key')
        local[k]=r
    if not local:raise ValueError('Empty local snapshot')
    count=len(local);volume=0;stats={f:dict(max_abs=0,squared_volume=0,reference_squared_volume=0) for f in FIELDS}
    inventories={which:dict(metal_volume_m3=0,liquid_volume_m3=0,molten_cells=0,
        molten_bounds={d+s:None for d in ('x','y','z') for s in ('min','max')}) for which in ('reference','candidate')}
    for a in rows(reference):
        if not inside(a,bounds):continue
        k=key(a)
        if k not in local:raise ValueError('Crop missing a selected reference cell')
        b=local.pop(k);v=a['volume'];volume+=v
        if not math.isclose(v,b['volume'],rel_tol=1e-10,abs_tol=1e-30):raise ValueError('Matched cell volume changed')
        for f,s in stats.items():
            delta=b[f]-a[f];s['max_abs']=max(s['max_abs'],abs(delta));s['squared_volume']+=v*delta*delta;s['reference_squared_volume']+=v*a[f]*a[f]
            if initial and abs(delta)>1e-10*max(abs(a[f]),1):raise ValueError('Crop changed initial internal field: '+f)
        for name,r in (('reference',a),('candidate',b)):
            q=inventories[name];q['metal_volume_m3']+=v*r['alpha'];q['liquid_volume_m3']+=v*r['alpha']*r['epsilon']
            if r['alpha']>=.5 and r['T']>=1631:
                q['molten_cells']+=1
                for d in ('x','y','z'):
                    for side,op in (('min',min),('max',max)):
                        old=q['molten_bounds'][d+side];q['molten_bounds'][d+side]=r[d] if old is None else op(old,r[d])
    if local:raise ValueError('Candidate has cells outside the selected reference geometry')
    for s in stats.values():
        s['volume_weighted_rms']=math.sqrt(s.pop('squared_volume')/volume)
        scale=math.sqrt(s.pop('reference_squared_volume')/volume)
        s['relative_rms']=s['volume_weighted_rms']/scale if scale else None
    return dict(cells=count,volume_m3=volume,fields=stats,inventories=inventories,
                note='Identical retained cells matched by1pm coordinate key and volume. Molten bounds are cell-centre envelopes, not iso-interface dimensions.')


def native_snapshot(text,expected):
    r=parse_records(text,'M247_LOCAL_MELT_SNAPSHOT')
    required=('schema','time','cells','xmin','xmax','ymin','ymax','zmin','zmax','cutFaces','activeCutFaces','cutMetalTmax','cutMetalEpsilonMax','cutUmax','productionApproved')
    if len(r)!=1 or any(k not in r[0] for k in required) or 'End' not in text or r[0]['schema']!=1 or abs(r[0]['time']-expected)>1e-12:
        raise ValueError('Incomplete native snapshot audit')
    return r[0]


def source_digest(source):
    # Hash only copied inputs and selected180us restart, not every historical time.
    entries={}
    for name in ('constant','system'):
        entries[name]=snapshot_digest(source/name)
    if (source/'0.00018').is_dir():entries['serial/checkpoint']=snapshot_digest(source/'0.00018')
    ranks=sorted(p for p in source.iterdir() if p.is_dir() and p.name.startswith('processor') and p.name[9:].isdigit())
    for rank in ranks:
        entries[rank.name+'/checkpoint']=snapshot_digest(checkpoint(rank,.00018))
        if (rank/'constant').is_dir():entries[rank.name+'/constant']=snapshot_digest(rank/'constant')
    return entries


def subset_command(case, checkpoint_name, help_text, start_from, start_time):
    # subsetMesh reads the controlDict start time; v2512 has no -time option.
    # -resultTime controls output only and must not select the input checkpoint.
    for option in ('-case', '-patch', '-overwrite'):
        if not re.search(r'(?<![\w-])'+re.escape(option)+r'(?![\w-])', help_text):
            raise ValueError('subsetMesh lacks required option: '+option)
    if start_from.strip().rstrip(';') != 'startTime':
        raise ValueError('subsetMesh requires explicit startFrom startTime')
    value=float(start_time.strip().rstrip(';'))
    expected=float(checkpoint_name)
    if not math.isfinite(value) or abs(value-expected)>1e-14:
        raise ValueError('subsetMesh controlDict startTime differs from checkpoint')
    return ['subsetMesh','localMeltCells','-case',str(case),'-patch','localCut','-overwrite']


def resolved_case_paths(source,work):
    source,work=Path(source).resolve(),Path(work).resolve()
    if source==work or source in work.parents or work in source.parents:
        raise ValueError('Output overlaps source after resolving directory links')
    return source,work


def cut_initialization_gate(text,faces):
    records=parse_records(text,'M247_LOCAL_CUT_INITIALIZED')
    if 'End' not in text or len(records)!=1 or records[0].get('schema')!=1 or records[0].get('fields')!=5 or records[0].get('faces')!=faces or records[0].get('internalFieldsChanged')!=0:
        raise ValueError('Missing or incomplete native cut initialization')
    for field,kind in [('T','fixedValue'),('alpha.metal','fixedValue'),('epsilon1','fixedValue'),('U','fixedValue'),('p_rgh','fixedFluxPressure')]:
        if f'field={field} type={kind} faces={faces} source=checkpointOwnerCells' not in text:
            raise ValueError('Missing cut field initialization: '+field)
    return records[0]


def cache_equivalence_gate(report):
    return (report['measurement_quality_gate']
        and all(v['max_abs']==0 for snapshot in report['field_comparisons'].values() for v in snapshot['fields'].values())
        and all(x['absolute_difference']==0 for x in report['diagnostic_differences'])
        and report['fullMelt']['performance']['steps']==report['localMelt']['performance']['steps']
        and report['fullMelt']['performance']['thermal_correctors_per_step']==report['localMelt']['performance']['thermal_correctors_per_step'])


def execute(source,work,solver,audit,wall_hours=2,prepared_local=None,refresh_pair=False,thermal_cache_pair=False,packed_pair=False,sampling_pair=False,sampling_long=False):
    if os.name!="posix":raise ValueError("Run real native pair on Ubuntu")
    if sum((refresh_pair,thermal_cache_pair,packed_pair,sampling_pair))>1:raise ValueError("Select only one full-domain experiment")
    full_domain_pair=refresh_pair or thermal_cache_pair or packed_pair or sampling_pair
    if sampling_long and not sampling_pair:raise ValueError('Long sampling schedule requires sampling experiment')
    end_s=.0002 if sampling_long else .00019
    sample_times=(.00019,.0002) if sampling_long else (.000185,.00019)
    sample_arg=','.join(f'{t:.12g}' for t in sample_times)
    if full_domain_pair:prepared_local=source
    source_alias,work_alias=str(source),str(work)
    source,work=resolved_case_paths(source,work)
    solver,audit=Path(solver).resolve(),Path(audit).resolve()
    if prepared_local is not None:
        prepared_local,_=resolved_case_paths(prepared_local,work)
        if prepared_local==source and not full_domain_pair:raise ValueError("Full and local input paths resolve to the same case")
    if not math.isfinite(wall_hours) or not 0<wall_hours<=4:raise ValueError('Per-case wall hours must be in(0,4]')
    if (work/'localMeltPairReview.json').exists():raise ValueError('Fresh work required')
    work.mkdir(parents=True,exist_ok=True)
    report=dict(schema=1,complete=False,production_approved=False,commands=[],source=str(source),
        solver_sha256=sha(solver),audit_sha256=sha(audit),start_s=.00018,end_s=end_s,sample_times_s=sample_times,ranks=48,
        input_paths=dict(source_argument=source_alias,source_resolved=str(source),work_argument=work_alias,work_resolved=str(work)),
        approximation='Fixed crop; T/alpha/epsilon/U cut values held from native checkpoint owner cells, fixedFluxPressure p_rgh. No advancing global thermal reservoir or moving handoff.',
        wall_hours_per_case=None,process_policy="Foreground normal completion; no automatic timeout or kill")
    if refresh_pair:
        report['comparison_kind']='same full mesh/partition; bounded laser refresh vs every-call optics'
        report['approximation']='Candidate holds deposition between guarded updates(interval2,age25ns,alphaChange0.1,motion0.25cells); all CFD/thermal steps retained. Default baseline interval1.'
    if thermal_cache_pair:
        report['comparison_kind']='same full mesh/partition; invariant thermal coefficient cache'
        report['approximation']='None intended: every-step laser, original thermal residuals/cap; only fixed explicit coefficient reused within each TEqn call.'
    if packed_pair:
        report['comparison_kind']='same full mesh/partition; packed ray broadcast'
        report['approximation']='None intended: unchanged gather/order/tracing/deposition/termination, every-step optics; only final broadcast payload representation differs.'
    if sampling_pair:
        report['comparison_kind']='same full mesh/partition; 1536 vs384 angularly coarsened rays'
        report['approximation']='Radial16 retained, angular96->24, every-step optics; unchanged ray stepping/handoff/absorption/cutoff/CFD. Reduced angular coverage explicitly sacrifices optical sampling accuracy.'
    def persist():save(work/'localMeltPairReview.json',report)
    def stage(name,command,timeout=1800):
        command=list(map(str,command));row=dict(name=name,command=command,status='running');report['commands'].append(row);persist()
        print('Starting real melt stage:',name,flush=True);start=time.monotonic()
        try:
            with (work/(name+'.log')).open('x',encoding='utf-8') as stream:
                code=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=False).returncode
            row.update(returncode=code,status='complete' if code==0 else 'failed')
            if code:raise RuntimeError(f'{name} returned{code}')
        except BaseException as error:
            row.update(status='failed',error=f'{type(error).__name__}: {error}');raise
        finally:row['elapsed_s']=time.monotonic()-start;persist()
        return row
    def export(case,name,t,initialize=False,verify=False):
        command=[audit,'-case',case,'-time',f'{t:.12g}','-output',work/(name+'.csv')]
        if initialize:command.append('-initializeCut')
        if verify:command.append('-verifyCut')
        row=stage(name,command)
        return native_snapshot((work/(name+'.log')).read_text(encoding='utf-8'),t)
    persist()
    try:
        if prepared_local is not None:
            before=source_digest(source);local_before=source_digest(prepared_local)
            save(work/'localMeltSourceHashes.json',dict(full=before,local=local_before))
            full=work/'fullMelt';local=work/'localMelt'
            meta=json.loads((source/'probe.json').read_text(encoding='utf-8'))
            if meta.get('ranks')!=48 or abs(meta.get('start_s',0)-.00018)>1e-14 or abs(meta.get('end_s',0)-.00019)>1e-14:
                raise ValueError('Prepared full-case metadata must describe180..190us/48ranks')
            meta=dict(meta,end_s=end_s,duration_us=20 if sampling_long else 10)
            for src,dst in ((source,full),(prepared_local,local)):
                dst.mkdir()
                for item in ('constant','system','0.00018'):
                    shutil.copytree(src/item,dst/item)
                if (dst/'constant/dynamicMeshDict').exists():raise ValueError('Fixed prepared mesh required')
                for k,v in dict(startFrom='startTime',startTime='.00018',stopAt='endTime',endTime=f'{end_s:.12g}',writeControl='adjustableRunTime',writeInterval='10e-6' if sampling_long else '5e-6',purgeWrite=0,writePrecision=17,writeCompression='off',writeFormat='ascii',localMeltBoundaryAudit='true').items():
                    set_entry(dst/'system/controlDict',k,v)
                if full_domain_pair:
                    set_entry(dst/'system/controlDict','thermalInvariantCache','true' if thermal_cache_pair and dst==local else 'false')
                    for k,v in dict(laserRefreshIntervalSteps=2 if refresh_pair and dst==local else 1,laserRefreshMaxAge='25e-9',laserRefreshMaxAlphaChange='.1',laserRefreshMaxCellDisplacement='.25').items():
                        set_entry(dst/'system/controlDict',k,v)
                if packed_pair:
                    set_entry(dst/'constant/LaserProperties','recordRayPaths','false')
                    set_entry(dst/'constant/LaserProperties','packedRayBroadcast','true' if dst==local else 'false')
                    set_entry(dst/'system/controlDict','frozenLaserProbe','off')
                if sampling_pair:
                    optical=dst/'constant/LaserProperties'
                    for name,wanted in (('nRadial',16),('nAngular',96)):
                        value=subprocess.run(['foamDictionary',str(optical),'-entry',name,'-value'],capture_output=True,text=True,check=True).stdout.strip().rstrip(';')
                        if value!=str(wanted):raise ValueError('Sampling baseline requires nRadial16/nAngular96')
                    for name,value in dict(nAngular=96 if dst==full else 24,recordRayPaths='false',packedRayBroadcast='false').items():
                        set_entry(optical,name,value)
                    set_entry(dst/'system/controlDict','frozenLaserProbe','off')
            # Require identical physics/numerical input settings, allowing only
            # additional preparation dictionaries in the local system directory.
            for path in (full/'constant').iterdir():
                if path.is_file() and (not (local/'constant'/path.name).is_file() or sha(path)!=sha(local/'constant'/path.name)):
                    if packed_pair and path.name=='LaserProperties':
                        from packed_broadcast_review import normalized_optical_settings
                        if normalized_optical_settings(path.read_text())!=normalized_optical_settings((local/'constant'/path.name).read_text()):
                            raise ValueError('Optical physics settings differ beyond payload switch')
                    elif sampling_pair and path.name=='LaserProperties':
                        from ray_sampling_review import normalized_settings
                        if normalized_settings(path.read_text())!=normalized_settings((local/'constant'/path.name).read_text()):
                            raise ValueError('Sampling pair changed other optical settings')
                    else:raise ValueError('Prepared constant settings differ: '+path.name)
            for name in ('fvSolution','fvSchemes'):
                if sha(full/'system'/name)!=sha(local/'system'/name):raise ValueError('Prepared numerical settings differ: '+name)
            initial=export(full,'fullMelt_initial',.00018)
            mapped=export(local,'localMelt_initial',.00018,verify=not full_domain_pair)
            if initial['cells']!=756000 or mapped['cells']!=(756000 if full_domain_pair else 604800) or mapped['cutFaces']!=(0 if full_domain_pair else 6300) or mapped['activeCutFaces']:
                raise ValueError('Prepared full/local mesh or cold-cut mismatch')
            b={k:mapped[k] for k in ('xmin','xmax','ymin','ymax','zmin','zmax')}
            report['window']=dict(bounds=b,selected_cells=mapped['cells'],prepared_input=str(prepared_local))
            report['initial_field_match']=compare_fields(work/'fullMelt_initial.csv',work/'localMelt_initial.csv',b,initial=True)
            import importlib.util
            script=ROOT/'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_powderTrack200us8um/scripts/extractMovingKeyholeDepth.py'
            persist()
        else:
            stage('subsetMesh_help',['subsetMesh','-help-full'],60)
            subset_help=(work/'subsetMesh_help.log').read_text(encoding='utf-8')
            stage('localMeltAudit_help',[audit,'-help-full'],60)
            audit_help=(work/'localMeltAudit_help.log').read_text(encoding='utf-8')
            if any(not re.search(r'(?<![\w-])'+re.escape(option)+r'(?![\w-])',audit_help) for option in ('-initializeCut','-verifyCut')):raise ValueError('Rebuild required: native cut initialization/verification missing')
            before=source_digest(source);save(work/'localMeltSourceHashes.json',before)
            full=work/'fullMelt';local=work/'localMelt'
            meta=prepare(source,full,180,10,'rayTraversalCached',corrected_rays=True)
            if meta['ranks']!=48 or (full/'constant/dynamicMeshDict').exists():raise ValueError('Requires fixed original48-rank8um checkpoint')
            set_entry(full/'system/controlDict','writePrecision',17)
            set_entry(full/'system/controlDict','localMeltBoundaryAudit','true')
            set_entry(full/'system/controlDict','writeCompression','off')
            set_entry(full/'system/controlDict','writeFormat','ascii')
            stage('fullMelt_reconstructInitial',['reconstructPar','-case',full,'-time','0.00018','-noFunctionObjects'])
            initial=export(full,'fullMelt_initial',.00018)
            if initial['cells']!=756000:raise ValueError('Requires original756000-cell mesh')
            # Use the established case path parser; require actual un-clamped path coverage.
            import importlib.util
            script=ROOT/'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_powderTrack200us8um/scripts/extractMovingKeyholeDepth.py'
            spec=importlib.util.spec_from_file_location('m247_keyhole',script);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
            path=module.read_path_table(full/'constant/timeVsLaserPosition')
            positions=[module.laser_position(path,t) for t in (.00018,.000185,.00019)]+[r[1:] for r in path if .00018<=r[0]<=.00019]
            report['window']={}
            try:plan=plan_window(work/'fullMelt_initial.csv',initial,positions,details=report['window'])
            finally:persist()
            local.mkdir()
            for name in ('constant','system',meta['checkpoint']):shutil.copytree(full/name,local/name)
            b=plan['bounds'];box='('+ ' '.join(f'{b[d+"min"]:.17g}' for d in ('x','y','z'))+') ('+' '.join(f'{b[d+"max"]:.17g}' for d in ('x','y','z'))+')'
            selection='FoamFile {version 2.0; format ascii; class dictionary; object topoSetDict;}\nactions ({name localMeltCells; type cellSet; action new; source boxToCell; box '+box+';});\n'
            (local/'system/topoSetDict').write_text(selection,encoding='utf-8',newline='\n');(work/'localMelt_selectionDict').write_text(selection,encoding='utf-8',newline='\n')
            stage('localMelt_select',['topoSet','-case',local,'-time','0.00018','-noFunctionObjects'])
            control=local/'system/controlDict'
            start_values=[subprocess.run(['foamDictionary',str(control),'-entry',entry,'-value'],capture_output=True,text=True,check=True).stdout for entry in ('startFrom','startTime')]
            command=subset_command(local,meta['checkpoint'],subset_help,*start_values)
            report['subset_input_time']=dict(startFrom=start_values[0].strip(),startTime=start_values[1].strip(),checkpoint=meta['checkpoint']);persist()
            stage('localMelt_subset',command)
            initialized=export(local,'localMelt_initializeCut',.00018,initialize=True)
            report['cut_initialization']=cut_initialization_gate((work/'localMelt_initializeCut.log').read_text(encoding='utf-8'),initialized['cutFaces']);persist()
            mapped=export(local,'localMelt_initial',.00018,verify=True)
            verified=parse_records((work/'localMelt_initial.log').read_text(encoding='utf-8'),'M247_LOCAL_CUT_VERIFIED')
            if len(verified)!=1 or verified[0].get('schema')!=1 or verified[0].get('fields')!=5 or verified[0].get('faces')!=mapped['cutFaces']:raise ValueError('Missing serialized cut verification')
            report['cut_serialized_verification']=verified[0]
            report['cut_initialization_internal_match']=compare_fields(work/'localMelt_initializeCut.csv',work/'localMelt_initial.csv',b,initial=True);persist()
            if mapped['cells']!=plan['selected_cells'] or not mapped['cutFaces']:raise ValueError('Subset geometry/count mismatch')
            if mapped['activeCutFaces']:raise ValueError('Initial crop cuts active metal; safe window rejected before CFD')
            report['initial_field_match']=compare_fields(work/'fullMelt_initial.csv',work/'localMelt_initial.csv',b,initial=True);persist()
        if packed_pair:
            from collect_thermal_validation import field_differences
            from packed_broadcast_review import frozen_trace,require_exact_fields,validate_mode,require_same_work
            inputs=('frozenAlphaInput','frozenNormalInput','frozenResistivityInput')
            for variant,case in (('fullMelt',full),('localMelt',local)):
                set_entry(case/'system/controlDict','frozenLaserProbe','capture')
                stage(variant+'_frozenCapture',[solver,'-case',case])
                set_entry(case/'system/controlDict','frozenLaserProbe','trace')
            frozen_inputs=field_differences(full,local,None,.00018,field_names=inputs,vector_fields=('frozenNormalInput',))
            require_exact_fields(frozen_inputs)
            report['frozen_broadcast_preflight']=dict(inputs=frozen_inputs,traces={},passed=False);persist()
        def decompose_case(variant,case):
            stage(variant+'_checkMesh',['checkMesh','-case',case,'-time','0.00018','-allTopology','-allGeometry','-noFunctionObjects'])
            mesh_text=(work/(variant+'_checkMesh.log')).read_text(encoding='utf-8')
            mesh_ok(mesh_text)
            if any(x not in mesh_text for x in ('3 geometric (non-empty/wedge) directions (1 1 1)','3 solution (non-empty) directions (1 1 1)')) or 'Total number of faces on empty patches' in mesh_text:
                raise ValueError('Real local melt comparison requires verified3D mesh')
            # Regenerate both decompositions with the same algorithm, on copies only.
            for p in list(case.iterdir()):
                if p.is_dir() and p.name.startswith('processor') and p.name[9:].isdigit():shutil.rmtree(p)
            set_entry(case/'system/decomposeParDict','numberOfSubdomains','48');set_entry(case/'system/decomposeParDict','method','scotch')
            stage(variant+'_decompose',['decomposePar','-case',case,'-time','0.00018','-noFunctionObjects'])
            if full_domain_pair and variant=='localMelt':
                addresses=[]
                for rank in range(48):
                    name=f'processor{rank}/constant/polyMesh/cellProcAddressing'
                    if sha(full/name)!=sha(local/name):raise ValueError('Full-domain pair decomposition differs on rank'+str(rank))
                    addresses.append(sha(full/name))
                report['identical_cell_partition_sha256']=addresses
                persist()
        if packed_pair:
            for variant,case in (('fullMelt',full),('localMelt',local)):
                decompose_case(variant,case)
                cmd=['mpirun','-np','48',solver,'-case',case,'-parallel']
                if packed_pair:
                    stage(variant+'_frozenTrace',cmd)
                    report['frozen_broadcast_preflight']['traces'][variant]=frozen_trace((work/(variant+'_frozenTrace.log')).read_text(),variant=='localMelt')
                    stage(variant+'_frozenReconstruct',['reconstructPar','-case',case,'-time','0.00018','-fields','(Deposition rayQ)','-noFunctionObjects'])
                    set_entry(case/'system/controlDict','frozenLaserProbe','off')
                    if variant=='localMelt':
                        outputs=field_differences(full,local,None,.00018,field_names=('Deposition','rayQ'),vector_fields=())
                        require_exact_fields(outputs)
                        traces=report['frozen_broadcast_preflight']['traces']
                        require_same_work(traces['fullMelt']['profile'],traces['localMelt']['profile'])
                        if traces['fullMelt']['diagnostics']['depositedPower']!=traces['localMelt']['diagnostics']['depositedPower']:
                            raise ValueError('Frozen deposited powers differ')
                        report['frozen_broadcast_preflight'].update(outputs=outputs,passed=True)
                    persist()
        for variant,case in (('fullMelt',full),('localMelt',local)):
            if not packed_pair:decompose_case(variant,case)
            md=dict(meta,variant=variant,window_bounds=b,cut_boundary_policy=report['approximation']);save(case/'probe.json',md)
            cmd=['mpirun','-np','48',solver,'-case',case,'-parallel']
            started=time.monotonic()
            try:
                row=stage(variant+'_solver',cmd,wall_hours*3600);code=row['returncode']
            finally:
                last=report['commands'][-1]
                save(case/'run.json',dict(solver=str(solver),solver_sha256=sha(solver),laser_library_sha256=sha(Path(__import__('os').environ['FOAM_USER_LIBBIN'])/'liblaserHeatSource.so'),elapsed_wall_s=time.monotonic()-started,
                     command=list(map(str,cmd)),returncode=last.get('returncode',-1),forced_stop=False,wall_budget_stop=False))
                shutil.copyfile(work/(variant+'_solver.log'),case/'log.vacuumLaserbeamFoam')
            _,summary,diagnostics=read_probe(case)
            report[variant]=dict(performance=summary,diagnostics=diagnostics,thermal_gate=summary['thermal_limit_hits']==0 and residual_gate(case,md,summary['steps']))
            if full_domain_pair:
                from laser_refresh_review import collect_refresh
                report[variant]['laser_refresh']=collect_refresh(case,md,summary,2 if refresh_pair and variant=='localMelt' else 1)
            if sampling_pair:
                from ray_sampling_review import validate_ray_count
                validate_ray_count(report[variant]['laser_refresh']['optics'],report[variant]['laser_refresh']['updates'],1536 if variant=='fullMelt' else 384)
            if packed_pair:
                validate_mode((case/'log.vacuumLaserbeamFoam').read_text(),variant=='localMelt')
            if thermal_cache_pair:
                cached=parse_records((case/'log.vacuumLaserbeamFoam').read_text(encoding='utf-8'),'THERMAL_INVARIANT_CACHE')
                expected=int(variant=='localMelt')
                if len(cached)!=summary['steps'] or any(x.get('schema')!=1 or x.get('enabled')!=expected for x in cached):
                    raise ValueError('Missing/mismatched thermal cache diagnostics')
                report[variant]['thermal_cache_records']=len(cached)
            persist()
            stage(variant+'_reconstructFinal',['reconstructPar','-case',case,'-time',sample_arg,'-noFunctionObjects'])
            report[variant]['snapshots']=[export(case,variant+'_'+label,t) for label,t in zip(('mid','final'),sample_times)]
            stage(variant+'_interface',['postProcess','-case',case,'-fields','(alpha.metal)','-dict',ROOT/'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_powderTrack200us8um/system/movingKeyholeInterfaceDict','-time',sample_arg])
            stage(variant+'_keyhole',['python3',script,'--post-processing',case/'postProcessing/movingKeyholeInterface','--laser-path',case/'constant/timeVsLaserPosition','--surface-y','600e-6','--surface-band','8e-6','--trailing-window','160e-6','--forward-window','80e-6','--half-width-z','100e-6','--output',work/(variant+'_keyhole.csv')])
            persist()
        report['field_comparisons']={label:compare_fields(work/('fullMelt_'+label+'.csv'),work/('localMelt_'+label+'.csv'),b) for label in ('mid','final')}
        a,c=report['fullMelt'],report['localMelt'];ad,cd=a['diagnostics'],c['diagnostics']
        if len(ad)!=len(cd) or any(abs(x['time']-y['time'])>1e-12 for x,y in zip(ad,cd)):raise ValueError('Physical sample times differ')
        report['diagnostic_scope_note']=('All diagnostics compare identical full domains.' if full_domain_pair else 'Tmax/Umax/powers are whole respective domains; interface area and other integrated quantities change with crop extent. Same-ROI field/inventory comparisons are authoritative for retained material.')
        report['diagnostic_differences']=[dict(time=x['time'],metric=k,reference=x[k],candidate=y[k],absolute_difference=abs(y[k]-x[k]),relative_difference=abs(y[k]-x[k])/abs(x[k]) if x[k] else None) for x,y in zip(ad,cd) for k in METRICS]
        report['cost']=dict(solver_wall_speedup=a['performance']['job_wall_s']/c['performance']['job_wall_s'],
            loop_speedup=a['performance']['interval_rank_max_sum_s']/c['performance']['interval_rank_max_sum_s'],
            note='Same48ranks/resolution/physical duration; solver wall includes initialization and writes. Prep/build/postprocess separately timed. No global-thermal/moving cost measured.')
        boundary=parse_records((local/'log.vacuumLaserbeamFoam').read_text(encoding='utf-8'),'M247_LOCAL_MELT_BOUNDARY')
        required=('schema','time','cutFaces','activeCutFaces','cutMetalTmax','cutMetalEpsilonMax','cutUmax','cutNetFluxM3PerS','productionApproved')
        if full_domain_pair:
            report['boundary']=dict(active_material_clear=True,note='No cut boundary: identical full domains; no regional acceptance claim')
        else:
            if len(boundary)!=c['performance']['steps'] or any(any(k not in r for k in required) or r['schema']!=1 or r['cutFaces']<=0 for r in boundary):raise ValueError('Missing per-step cut-boundary audit')
            report['boundary']=dict(records=boundary,active_material_clear=all(r['activeCutFaces']==0 for r in boundary),
                maximum_cut_gas_or_metal_speed=max(r['cutUmax'] for r in boundary),note='No active metal contact is necessary but not sufficient for pressure/optical boundary independence; held reservoir cannot support long tracks.')
        keyhole=[]
        for variant in ('fullMelt','localMelt'):
            with (work/(variant+'_keyhole.csv')).open(encoding='utf-8',newline='') as f:
                samples=list(csv.DictReader(f))
            if len(samples)!=2 or any(abs(float(r['time_s'])-t)>1e-12 for r,t in zip(samples,sample_times)):raise ValueError('Incomplete keyhole sample times')
            keyhole.append(samples)
        report['keyhole_comparisons']=[dict(time_s=float(a['time_s']),reference_depth_um=float(a['keyhole_depth_um']),candidate_depth_um=float(c['keyhole_depth_um']),
            depth_difference_um=float(c['keyhole_depth_um'])-float(a['keyhole_depth_um']),reference_connected=a['surface_connected'],candidate_connected=c['surface_connected'],
            reference_bottom_support=int(a['bottom_support_vertices']),candidate_bottom_support=int(c['bottom_support_vertices'])) for a,c in zip(*keyhole)]
        report['measurement_quality_gate']=report['fullMelt']['thermal_gate'] and report['localMelt']['thermal_gate'] and report['boundary']['active_material_clear'] and all(r['reference_connected']==r['candidate_connected']=='yes' and r['reference_bottom_support']>0 and r['candidate_bottom_support']>0 for r in report['keyhole_comparisons'])
        if thermal_cache_pair:
            report['thermal_cache_equivalence_gate']=cache_equivalence_gate(report)
        if packed_pair:
            report['packed_broadcast_equivalence_gate']=(cache_equivalence_gate(report) and report['frozen_broadcast_preflight']['passed']
                and report['fullMelt']['laser_refresh']['optics']['counts']==report['localMelt']['laser_refresh']['optics']['counts'])
        if sampling_pair:
            from ray_sampling_review import error_summary
            from local_melt_localization import localize
            report['ray_sampling_error_review']=error_summary(report)
            location_bounds=dict(b,_has_cut=False)
            locations={label:localize(work/('fullMelt_'+label+'.csv'),work/('localMelt_'+label+'.csv'),location_bounds) for label in ('mid','final')}
            save(work/'localMeltLocalization.json',dict(schema=1,complete=True,production_approved=False,comparison_kind=report['comparison_kind'],localization=locations))
        report['source_unchanged']=source_digest(source)==before and (prepared_local is None or source_digest(prepared_local)==local_before)
        if not report['source_unchanged']:raise ValueError('Source inputs changed')
        report['complete']=True
        report['interpretation']='Completed measurement, not production acceptance. Evaluate field/keyhole/power differences against measured speed; no arbitrary physical error tolerance silently approves it.'
        persist();return report
    except BaseException as error:
        if 'before' in locals():
            try:report['source_unchanged']=source_digest(source)==before and (prepared_local is None or source_digest(prepared_local)==local_before)
            except Exception as check:report['source_verification_error']=str(check)
        report['error']=f'{type(error).__name__}: {error}';persist();raise


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--solver',type=Path,required=True);p.add_argument('--audit',type=Path,required=True);p.add_argument('--wall-hours',type=float,default=2);p.add_argument('--prepared-local',type=Path);p.add_argument('--laser-refresh-pair',action='store_true');p.add_argument('--thermal-cache-pair',action='store_true');p.add_argument('--packed-ray-pair',action='store_true');p.add_argument('--ray-sampling-pair',action='store_true');p.add_argument('--ray-sampling-long-pair',action='store_true')
    a=p.parse_args()
    try:execute(a.source,a.work,a.solver,a.audit,a.wall_hours,a.prepared_local,a.laser_refresh_pair,a.thermal_cache_pair,a.packed_ray_pair,a.ray_sampling_pair or a.ray_sampling_long_pair,a.ray_sampling_long_pair)
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError) as e:p.exit(1,f'Real local melt pair failed: {e}\n')
    print('Real local/full melt measurements complete; production approved: False',flush=True)


if __name__=='__main__':main()
