#!/usr/bin/env python3
"""Prepare/run/collect the first50us of a full1.5mm M247 static6um corridor."""
import argparse
from collections import deque
import gzip
import itertools
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tarfile
import time
from collect_probe import read_probe
from collect_thermal_validation import residual_gate, final_state
from wang_ray_suite import run, setting, save, digest

ROOT=Path(__file__).resolve().parents[2]
TEMPLATE=ROOT/'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_track1500um6um'
CELLS=4232448
FINE=((-240e-6,1620e-6),(0,720e-6),(-192e-6,192e-6))
SURFACE=600e-6

def field_rows(path,width):
    if not path.exists():path=path.with_name(path.name+'.gz')
    opener=gzip.open if path.suffix=='.gz' else open
    with opener(path,'rt') as handle:
        header=''
        for line in handle:
            header+=line
            uniform=re.search(r'internalField\s+uniform\s+([^;]+);',header)
            nonuniform=re.search(r'internalField\s+nonuniform\s+List<(scalar|vector)>\s+(\d+)\s*\(',header)
            if uniform or nonuniform:break
            if len(header)>65536:raise ValueError('Missing internalField header: '+str(path))
        if not re.search(r'format\s+ascii\s*;',header):raise ValueError('ASCII postprocessing field required')
        if uniform:
            row=tuple(map(float,uniform[1].replace('(',' ').replace(')',' ').split()))
            if len(row)!=width or not all(math.isfinite(x) for x in row):raise ValueError('Invalid uniform field')
            yield from itertools.repeat(row,CELLS);return
        if not nonuniform or int(nonuniform[2])!=CELLS or (3 if nonuniform[1]=='vector' else 1)!=width:
            raise ValueError('Unexpected field count/type: '+str(path))
        count=0;buffer=[]
        for line in itertools.chain([header[nonuniform.end():]],handle):
            for token in line.replace('(',' ').replace(')',' ').split():
                buffer.append(float(token))
                if len(buffer)==width:
                    if not all(math.isfinite(x) for x in buffer):raise ValueError('Nonfinite field')
                    yield tuple(buffer);buffer=[];count+=1
                    if count==CELLS:return
        raise ValueError('Truncated field: '+str(path))

def pool_geometry(state, beam_x=50e-6):
    fine_cells={};all_hot=[];liquid_hot=[];outside=0
    peaks=dict(metal=0,interface=0,gas=0)
    for index,(tr,ar,centre) in enumerate(zip(field_rows(state/'T',1),field_rows(state/'alpha.metal',1),field_rows(state/'C',3))):
        temperature=tr[0];alpha=ar[0]
        region='metal' if alpha>=.99 else 'gas' if alpha<=.01 else 'interface'
        peaks[region]=max(peaks[region],temperature)
        if alpha<.5 or temperature<1537:continue
        all_hot.append(centre)
        if temperature>=1631:liquid_hot.append(centre)
        if not all(lo<x<hi for x,(lo,hi) in zip(centre,FINE)):
            outside+=1;continue
        key=tuple(round((x-lo)/6e-6-.5) for x,(lo,hi) in zip(centre,FINE))
        fine_cells[key]=centre
    def bounds(points):
        if not points:return None
        lo=[min(p[i] for p in points) for i in range(3)];hi=[max(p[i] for p in points) for i in range(3)]
        return dict(cells=len(points),minimum_m=lo,maximum_m=hi,
            depth_from_original_surface_um=max(0,(SURFACE-lo[1])*1e6),width_z_um=(hi[2]-lo[2])*1e6,
            fine_margin_um=min(min(a-l,h-b) for a,b,(l,h) in zip(lo,hi,FINE))*1e6)
    substrate=[k for k,p in fine_cells.items() if p[1]<=SURFACE]
    pool=[]
    if substrate:
        seed=min(substrate,key=lambda k:(fine_cells[k][0]-beam_x)**2+(fine_cells[k][1]-SURFACE)**2+fine_cells[k][2]**2)
        seen={seed};queue=deque([seed])
        while queue:
            k=queue.popleft();pool.append(fine_cells[k])
            for axis in range(3):
                for sign in (-1,1):
                    neighbour=list(k);neighbour[axis]+=sign;neighbour=tuple(neighbour)
                    if neighbour in fine_cells and neighbour not in seen:seen.add(neighbour);queue.append(neighbour)
    return dict(schema=1,solidus_connected_pool=bounds(pool),solidus_all_metal=bounds(all_hot),liquidus_all_metal=bounds(liquid_hot),
        molten_metal_cells_outside_fine=outside,temperature_maxima_K=peaks,
        geometry_note='alpha>=0.5 and T>=1537K; connected6-neighbour cell-centre component near laser/substrate. Width along z; melt depth differs from keyhole depth. Centre extents have about one6um-cell discretisation uncertainty. Disconnected molten particles also reported; fine-zone violation prevents continuation recommendation.')

def collect(work):
    case=work/'track1500';meta,summary,diag=read_probe(case)
    geometry=pool_geometry(final_state(case,None,50e-6))
    save(case/'meltGeometry.json',geometry)
    thermal=summary['thermal_limit_hits']==0 and residual_gate(case,meta,summary['steps'])
    pool=geometry['solidus_connected_pool']
    static_local=bool(globals().get('STATIC_LOCAL_CORRIDOR',False))
    report=dict(schema=1,complete=True,solver=summary,thermal_gate=thermal,geometry=geometry,
        simulated_scan_um=50,planned_scan_um=1500,
        rough_heating_wall_hours_at_pilot_rate=None if static_local else summary['job_wall_s']/3600*30,
        projection_note=('Static local fine zone ends after the first 50us; no full-track time projection or continuation is valid.' if static_local
            else 'Startup50us rate is not a full-track ETA; thermal/ray work and timestep can change. Cooling cost excluded.'),
        static_local_corridor_only=static_local,
        ready_for_next_stage_review=(not static_local) and thermal and geometry['molten_metal_cells_outside_fine']==0 and pool is not None and pool['fine_margin_um']>=24 and geometry['solidus_all_metal']['fine_margin_um']>=12,
        production_approved=False)
    handoff=case/'demHandoff.json'
    if handoff.is_file():report['demHandoff']=json.loads(handoff.read_text())
    save(work/'pilotReport.json',report);print(json.dumps(report,indent=2),flush=True)

def execute(work):
    case=work/'track1500';shutil.copytree(TEMPLATE,case)
    prepare_case=globals().get('PREPARE_CASE')
    if prepare_case:prepare_case(case,work)
    shutil.copytree(case/'initial',case/'0')
    manifest=json.loads((case/'constant/powderManifest.json').read_text())
    powder_gate=globals().get('POWDER_GATE')
    if powder_gate:powder_gate(manifest)
    elif manifest['minimumInterparticleGap_m'] < -1e-12:
        raise ValueError('Powder overlap preflight failed')
    save(case/'probe.json',dict(schema=1,variant=globals().get('PILOT_VARIANT','track1500Pilot'),start_s=0,end_s=50e-6,duration_us=50,ranks=48,
        epsilon_tolerance=1e-4,phase_temperature_tolerance_K=.01,epsilon_relaxation=1,planned_scan_s=.0015,
        cooling_end_s=.002,rays=384,cells=CELLS))
    for tool in ('blockMesh','setFields','checkMesh'):run(case,tool,[tool])
    meshlog=(case/'log.checkMesh').read_text(errors='replace')
    if 'Mesh OK' not in meshlog or not re.search(r'cells:\s*'+str(CELLS)+r'\b',meshlog):
        raise ValueError('Mesh topology/count gate failed; no CFD launched')
    run(case,'decomposePar',['decomposePar'])
    solver=Path(shutil.which('vacuumLaserbeamFoam')).resolve()
    save(work/'inputHashes.json',{p.relative_to(case).as_posix():digest(p) for directory in ('constant','system','initial') for p in (case/directory).rglob('*') if p.is_file() and 'polyMesh' not in p.parts})
    start=time.perf_counter();code=1
    try:run(case,'vacuumLaserbeamFoam',['mpirun','-np','48',solver,'-parallel']);code=0
    finally:save(case/'run.json',dict(elapsed_wall_s=time.perf_counter()-start,returncode=code,wall_budget_stop=False,forced_stop=False))
    # Keep solver writes compact; official reconstruction exports only final
    # fields in ASCII for streaming geometry collection, not five full copies.
    setting(case,'system/controlDict','writeFormat','ascii')
    try:
        run(case,'reconstructPar',['reconstructPar','-fields','(alpha.metal T)','-latestTime'])
        run(case,'writeCellCentres',['postProcess','-func','writeCellCentres','-latestTime'])
        collect(work)
    finally:setting(case,'system/controlDict','writeFormat','binary')

def package(work,code):
    files=[p for p in work.rglob('*') if p.is_file() and not any(part.startswith('processor') or part in ('polyMesh','postProcessing') for part in p.relative_to(work).parts)
        and (p.suffix in ('.json','.csv','.txt','.log','.md') or p.name.startswith('log.') or p.parent.name in ('constant','system')) and p.name!='manifest.json']
    missing=[p for p in ('pilotReport.json','track1500/meltGeometry.json','track1500/run.json') if not (work/p).exists()]
    save(work/'manifest.json',dict(schema=1,exit_code=code,missing_files=missing,complete=code==0 and not missing,
        files=[dict(path=p.relative_to(work).as_posix(),size=p.stat().st_size,sha256=digest(p)) for p in files]))
    archive=work.parent/('M247_'+work.name+'_review.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for p in files+[work/'manifest.json']:tar.add(p,arcname=work.name+'/'+p.relative_to(work).as_posix())
    print('Review archive: '+str(archive)+'\nSend this single archive, including on failure.',flush=True)

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--work',type=Path,required=True);p.add_argument('--collect',action='store_true');p.add_argument('--package',action='store_true');p.add_argument('--exit-code',type=int,default=0)
    a=p.parse_args();work=a.work.resolve()
    if a.package:package(work,a.exit_code)
    elif a.collect:collect(work)
    else:execute(work)

if __name__=='__main__':main()

