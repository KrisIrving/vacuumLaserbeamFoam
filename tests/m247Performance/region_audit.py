#!/usr/bin/env python3
"""Read-only spatial audit and explicit cost scenarios for the M247 checkpoint."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
from collect_probe import parse_records, read_probe, compare
from collect_thermal_validation import residual_gate
from package_results import FILES

NAMES=('mesh','moltenMetal','activeCFDProxy','warmMetal','hotGas','fastMaterial')
SOURCE_TIMES=[u*1e-6 for u in (100,120,140,160,180,200)]
PAIR_TIMES=[u*1e-6 for u in (180,181,182)]
AXES='xyz'

def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()

def completed(path):
    # The original long thermal log can be large; End is in its final tail.
    with Path(path).open('rb') as stream:
        stream.seek(0,2);size=stream.tell();stream.seek(max(0,size-65536))
        return bool(re.search(r'^End\s*$',stream.read().decode(errors='replace'),re.M))

def read_regions(text, expected_times):
    configs=parse_records(text,'M247_REGION_CONFIG')
    expected=dict(schema=1,liquidus=1631,solidus=1537,alphaMin=0.01,
                  metalMin=0.5,epsilonMin=0.01,fastSpeed=1,thermalThreshold=1368.15)
    if configs!=[expected] or not re.search(r'^End\s*$',text,re.M):
        raise ValueError('Incomplete audit or unsupported M247 material/configuration')
    states=parse_records(text,'M247_REGION_STATE')
    regions=parse_records(text,'M247_REGION')
    if len(states)!=len(expected_times) or len(regions)!=6*len(states):
        raise ValueError('Missing/duplicate audit snapshots or regions')
    result=[]
    for i,(state,time) in enumerate(zip(states,expected_times)):
        if (state.get('schema')!=1 or abs(state.get('time',-1)-time)>1e-12
            or state.get('ranks')!=48 or state.get('invalid')!=0):
            raise ValueError('Wrong audit time/ranks or invalid cells')
        if any(k not in state for k in ('alphaBounds','epsilonBounds','metalTmax','Tmax','Umax','liquidVolume')):
            raise ValueError('Missing audit state values')
        if any(state[k]<0 or state[k]!=int(state[k]) for k in ('alphaBounds','epsilonBounds')):
            raise ValueError('Invalid boundedness counts')
        rows=regions[i*6:(i+1)*6]
        if [r.get('region') for r in rows]!=list(range(6)):
            raise ValueError('Region ordering/IDs changed')
        mesh=rows[0]
        for r in rows:
            if (r.get('schema')!=1 or abs(r.get('time',-1)-time)>1e-12
                or r.get('cells',-1)!=int(r.get('cells',-1)) or r.get('cells',-1)<0
                or r.get('volume',-1)<0):
                raise ValueError('Invalid region counts/volume/time')
            for axis in AXES:
                lo,hi=r.get(axis+'min'),r.get(axis+'max')
                if lo is None or hi is None or lo>hi:
                    raise ValueError('Invalid region bounds')
                if r['cells'] and (lo<mesh[axis+'min']-1e-12 or hi>mesh[axis+'max']+1e-12):
                    raise ValueError('Region escapes mesh')
            if r['cells']>mesh['cells'] or r['volume']>mesh['volume']+1e-18:
                raise ValueError('Region exceeds mesh')
            if bool(r['cells'])!=bool(r['volume']):
                raise ValueError('Empty region has nonzero volume or vice versa')
        if mesh['cells']!=756000 or mesh['volume']<=0:
            raise ValueError('Expected original 756000-cell mesh')
        geometric_volume=math.prod(mesh[a+'max']-mesh[a+'min'] for a in AXES)
        if abs(mesh['volume']-geometric_volume)>1e-6*geometric_volume:
            raise ValueError('Mesh volume does not reconcile to the rectangular domain')
        for axis,lo,hi in (('x',-520e-6,320e-6),('y',0,960e-6),('z',-320e-6,320e-6)):
            if abs(mesh[axis+'min']-lo)>1e-12 or abs(mesh[axis+'max']-hi)>1e-12:
                raise ValueError('Unexpected original mesh envelope')
        if result and any(mesh[k]!=result[0]['regions'][0][k] for k in ('cells',)+tuple(a+s for a in AXES for s in ('min','max'))):
            raise ValueError('Mesh changed between snapshots')
        result.append(dict(state=state,regions=rows))
    return result

def read_pair(directory):
    directory=Path(directory)
    variants=('rayImpactLegacy','rayImpactCorrected')
    probes=[read_probe(directory/n) for n in variants]
    compare(*probes)
    for index,(name,p) in enumerate(zip(variants,probes)):
        m=p[0]
        if (m['variant']!=name or m['ranks']!=48 or abs(m['start_s']-0.00018)>1e-12
            or abs(m['end_s']-0.000182)>1e-12 or abs(m['duration_us']-2)>1e-9
            or m.get('cached_ray_traversal') is not True
            or any(m.get(k) is not bool(index) for k in ('preserve_ray_handoff_sample','consistent_ray_termination'))):
            raise ValueError('Wrong impact pair modes/interval/ranks')
        if not residual_gate(directory/name,m,p[1]['steps']):
            raise ValueError('Impact pair did not converge')
    runs=[json.loads((directory/n/'run.json').read_text()) for n in variants]
    for key in ('solver_sha256','laser_library_sha256'):
        if not runs[0].get(key) or runs[0][key]!=runs[1].get(key):
            raise ValueError('Unmatched impact solver/library provenance')
    return probes

def trend(path):
    with Path(path).open(newline='') as stream: rows=list(csv.DictReader(stream))
    selected=[]
    for row in rows:
        time=float(row['time_s'])*1e6
        if 100-1e-6<=time<=200+1e-6:
            if row['surface_connected']!='yes' or int(row['bottom_support_vertices'])<=0:
                raise ValueError('Disconnected/unsupported keyhole sample')
            depth=float(row['keyhole_depth_um'])
            if not math.isfinite(depth) or depth<0: raise ValueError('Invalid depth')
            selected.append((time,depth))
    if (len(selected)!=11 or abs(selected[0][0]-100)>1e-6 or abs(selected[-1][0]-200)>1e-6
        or any(abs(t-(100+10*i))>1e-6 for i,(t,_) in enumerate(selected))):
        raise ValueError('Requires every 10-us keyhole sample from 100 to 200 us')
    def slope(data):
        tx=sum(t for t,d in data)/len(data);dy=sum(d for t,d in data)/len(data)
        return sum((t-tx)*(d-dy) for t,d in data)/sum((t-tx)**2 for t,d in data)
    return dict(start_depth_um=selected[0][1],end_depth_um=selected[-1][1],
        growth_um=selected[-1][1]-selected[0][1],ols_100_200_um_per_us=slope(selected),
        ols_150_200_um_per_us=slope(selected[5:]),
        end_180_200_um_per_us=(selected[-1][1]-selected[-3][1])/20,
        plateau_approved=False,
        note='Existing alpha-interface OBJ extraction and moving ROI; not a new corrected-physics depth series. No plateau tolerance is invented.')

def cost_scenarios(summary):
    rate=summary['job_wall_s']/summary['duration_us']
    if not math.isfinite(rate) or rate<=0: raise ValueError('Invalid measured cost')
    fractions={k:v['mean_fraction'] for k,v in summary['sections'].items()}
    flow=sum(fractions[k] for k in ('alpha','momentum','pressure'))
    return dict(measured_job_s_per_us=rate,measured_ranks=summary['ranks'],
        flow_only_elimination_ceiling=1/(1-flow),laser_elimination_ceiling=1/(1-fractions['laser']),
        central_spacing_scenarios=[dict(spacing_um=h,cell_multiplier=r**3,
            assumed_step_multiplier=r,assumed_work_multiplier=r**4,
            pilot_2us_hours=rate*2*r**4/3600,
            max_us_in_19p2_hours=19.2*3600/(rate*r**4),
            fixed_workload_1500us_hours=rate*1500*r**4/3600,
            fixed_workload_2000us_hours=rate*2000*r**4/3600)
            for h,r in ((8,1),(4,2),(2,4))],
        note='Scenarios, not measured finer-grid forecasts: halve all existing edges, cells scale r^3, steps scale r. Constant per-cell and MPI cost assumed. Full-track rows hold the short-window workload fixed despite domain/path expansion and omit cooling/build/mapping; cannot approve a production budget. 19.2 h reserves 20% of 24 h.')

def prepare(source,impact,work):
    source,impact,work=map(lambda p:Path(p).resolve(),(source,impact,work))
    if any(p==work or p in work.parents or work in p.parents for p in (source,impact)):
        raise ValueError('Audit output must be separate from source')
    probes=read_pair(impact)
    for p in probes:
        if Path(p[0]['source']).resolve()!=source or p[0]['ranks']!=48:
            raise ValueError('Impact pair belongs to another source or rank count')
    if probes[0][0]['source_snapshot_sha256']!=probes[1][0]['source_snapshot_sha256']:
        raise ValueError('Unmatched impact restart')
    for field in ('movingKeyholeDepth.csv','moltenExtent.csv'):
        if not (source/field).is_file(): raise ValueError(f'Missing existing postprocessing: {source/field}')
    if not completed(source/'log.vacuumLaserbeamFoam'):
        raise ValueError('Original case is incomplete')
    work.mkdir(parents=True,exist_ok=True)
    hashes={}
    for field,name in (('movingKeyholeDepth.csv','sourceKeyholeDepth.csv'),('moltenExtent.csv','sourceMoltenExtent.csv')):
        shutil.copyfile(source/field,work/name);hashes[name]=sha(work/name)
    for variant in ('rayImpactLegacy','rayImpactCorrected'):
        for relative in FILES:
            if relative in ('capture.log','captureRun.json'): continue
            p=impact/variant/relative
            if not p.is_file(): raise ValueError(f'Missing impact reference: {p}')
            target=work/variant/relative
            if target.exists(): raise ValueError('Audit references already exist')
            target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,target)
            hashes[f'{variant}/{relative}']=sha(target)
    provenance=dict(schema=1,source=str(source),impact=str(impact),
        source_solver_log_sha256=sha(source/'log.vacuumLaserbeamFoam'),
        source_times_s=SOURCE_TIMES,pair_times_s=PAIR_TIMES,reference_sha256=hashes,
        read_only=True,production_approved=False)
    (work/'auditInputs.json').write_text(json.dumps(provenance,indent=2)+'\n')

def collect(work):
    work=Path(work);inputs=json.loads((work/'auditInputs.json').read_text())
    if (inputs.get('schema')!=1 or inputs.get('read_only') is not True
        or inputs.get('source_times_s')!=SOURCE_TIMES or inputs.get('pair_times_s')!=PAIR_TIMES):
        raise ValueError('Unexpected audit input provenance')
    required={'sourceKeyholeDepth.csv','sourceMoltenExtent.csv'} | {
        f'{v}/{relative}' for v in ('rayImpactLegacy','rayImpactCorrected') for relative in FILES
        if relative not in ('capture.log','captureRun.json')}
    if set(inputs['reference_sha256'])!=required:
        raise ValueError('Incomplete audit reference hashes')
    for relative,digest in inputs['reference_sha256'].items():
        if sha(work/relative)!=digest: raise ValueError('Audit reference changed')
    audits={name:read_regions((work/log).read_text(),times) for name,log,times in (
        ('source','sourceRegionAudit.log',SOURCE_TIMES),
        ('legacy','legacyRegionAudit.log',PAIR_TIMES),
        ('corrected','correctedRegionAudit.log',PAIR_TIMES))}
    probes=read_pair(work)
    # Envelopes use full vertices of selected cells, not an unmasked gas isotherm.
    rows=[]
    for name,snapshots in audits.items():
        for snapshot in snapshots:
            mesh=snapshot['regions'][0]
            for r in snapshot['regions'][1:]:
                row=dict(case=name,time_us=r['time']*1e6,region=NAMES[int(r['region'])],
                    cells=int(r['cells']),cell_fraction=r['cells']/mesh['cells'],volume_m3=r['volume'])
                for a in AXES:
                    row[a+'min_um']=r[a+'min']*1e6 if r['cells'] else None
                    row[a+'max_um']=r[a+'max']*1e6 if r['cells'] else None
                    row[a+'minus_clearance_um']=(r[a+'min']-mesh[a+'min'])*1e6 if r['cells'] else None
                    row[a+'plus_clearance_um']=(mesh[a+'max']-r[a+'max'])*1e6 if r['cells'] else None
                rows.append(row)
    active=[r for snapshots in audits.values() for s in snapshots for r in [s['regions'][2]] if r['cells']]
    if not active: raise ValueError('No active CFD proxy cells')
    mesh=audits['source'][0]['regions'][0]
    box={};clipped=[]
    for a in AXES:
        lo=min(r[a+'min'] for r in active)-80e-6;hi=max(r[a+'max'] for r in active)+80e-6
        if lo<mesh[a+'min'] or hi>mesh[a+'max']: clipped.append(a)
        box[a+'min']=max(lo,mesh[a+'min']);box[a+'max']=min(hi,mesh[a+'max'])
    box_volume=math.prod(box[a+'max']-box[a+'min'] for a in AXES)
    bounded=all(s['state']['alphaBounds']==s['state']['epsilonBounds']==0 for snapshots in audits.values() for s in snapshots)
    molten=[r for r in rows if r['region']=='moltenMetal']
    molten_boundary_gate=all(r['cells']>0 and min(r[a+side+'_clearance_um'] for a in AXES for side in ('minus','plus'))>=80 for r in molten)
    result=dict(schema=1,execution_gate=True,bounded_snapshot_gate=bounded,production_approved=False,
        molten_snapshot_boundary_gate_80um=molten_boundary_gate,
        provenance=inputs,audits=audits,keyhole_legacy_trend=trend(work/'sourceKeyholeDepth.csv'),
        cost=cost_scenarios(probes[1][1]),
        fine_box_candidate=dict(bounds_m=box,padding_um=80,clipped_axes=clipped,
            domain_volume_fraction=box_volume/mesh['volume'],
            uniform_4um_box_cells=math.prod(math.ceil((box[a+'max']-box[a+'min'])/4e-6) for a in AXES),
            note='Union of snapshot active-material proxies plus80um, a sizing envelope only. Does not cover future growth, cold powder geometry, optical paths or gas-flow requirements; not a mesh/coupling approval.'),
        note='No CFD advancement or field writes. Region thresholds are diagnostics. Alpha masks separate hot gas from molten metal. Spatial split still requires conservative heat coupling, pressure/VOF treatment and boundary sensitivity. Snapshot boundedness is not a full-history stability gate.')
    (work/'regionAuditReview.json').write_text(json.dumps(result,indent=2)+'\n')
    with (work/'regionEnvelopes.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--work',type=Path,required=True);p.add_argument('--source',type=Path)
    p.add_argument('--impact',type=Path);p.add_argument('--prepare',action='store_true')
    args=p.parse_args()
    try:
        if args.prepare:
            if args.source is None or args.impact is None: raise ValueError('Source and impact pair required')
            prepare(args.source,args.impact,args.work)
        else:
            r=collect(args.work)
            print('Read-only audit complete; bounded snapshots:',r['bounded_snapshot_gate'])
            print('Legacy late keyhole slope um/us:',r['keyhole_legacy_trend']['ols_150_200_um_per_us'])
            print('Measured corrected cost s/us:',r['cost']['measured_job_s_per_us'])
            print('Fine-box sizing fraction:',r['fine_box_candidate']['domain_volume_fraction'])
    except (ValueError,OSError,KeyError) as e: p.exit(1,f'Region audit failed: {e}\n')

if __name__=='__main__':main()
