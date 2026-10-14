#!/usr/bin/env python3
"""Read existing DEM pilot histories in fresh reconstruction cases; no CFD."""
import argparse
from collections import deque
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import tarfile
import time

import track1500_pilot as pilot
from collect_thermal_validation import final_state
from local_corridor_compare import compare, load_work
from wang_ray_suite import digest, run, save, setting

ROI=((-240e-6,300e-6),(180e-6,720e-6),(-192e-6,192e-6))
DX=6e-6
SHAPE=(90,90,64)
TIMES=(0.,10e-6,20e-6,30e-6,40e-6,50e-6)


def environment():
    project=Path(os.environ.get('WM_PROJECT_DIR','/missing')).resolve()
    appbin=Path(os.environ.get('FOAM_APPBIN','/missing')).resolve()
    wmake=shutil.which('wmake')
    if (os.environ.get('WM_PROJECT_VERSION') not in ('2512','v2512')
        or project.name!='OpenFOAM-v2512' or not project.is_dir() or not wmake
        or Path(wmake).resolve()!=(project/'wmake/wmake').resolve()):
        raise ValueError('Load OpenFOAM-v2512/etc/bashrc; version, project and wmake must all match')
    if not appbin.is_relative_to(project):
        raise ValueError('FOAM_APPBIN must belong to the active OpenFOAM-v2512 project')
    commands={}
    for tool in ('foamDictionary','reconstructPar','postProcess'):
        command=shutil.which(tool)
        if not command or Path(command).resolve()!=(appbin/tool).resolve():
            raise ValueError('Missing or mismatched v2512 OpenFOAM command: '+tool)
        commands[tool]=str(Path(command).resolve())
    return dict(WM_PROJECT_VERSION=os.environ['WM_PROJECT_VERSION'],
                WM_PROJECT_DIR=str(project),WMAKE=str(Path(wmake).resolve()),
                FOAM_APPBIN=str(appbin),commands=commands)


def source_inventory(source):
    """Fail before reconstruction if either existing history is incomplete."""
    paths=[source/'system/controlDict',source.parent/'pilotReport.json',
           source.parent/'inputHashes.json',source.parent/'solverCheck.json']
    ranks=sorted(p for p in source.glob('processor*') if p.is_dir())
    if {p.name for p in ranks}!={f'processor{i}' for i in range(48)}:
        raise ValueError('Expected exactly 48 processor directories: '+str(source))
    for rank in ranks:
        paths.extend(p for p in (rank/'constant/polyMesh').iterdir() if p.is_file())
        for stamp in TIMES:
            state=final_state(rank,None,stamp)
            for name in (('alpha.metal','T') if stamp==0 else ('alpha.metal','T','epsilon1')):
                path=state/name
                if not path.is_file():path=path.with_name(path.name+'.gz')
                if not path.is_file():raise ValueError('Missing saved field: '+str(path))
                paths.append(path)
    paths.extend(p for p in (source/'constant/polyMesh').iterdir() if p.is_file())
    return {str(p.resolve()):dict(size=p.stat().st_size,mtime_ns=p.stat().st_mtime_ns)
            for p in paths}


def unchanged(inventory):
    return all(Path(name).is_file() and Path(name).stat().st_size==value['size']
               and Path(name).stat().st_mtime_ns==value['mtime_ns']
               for name,value in inventory.items())


def shadow_case(source,target):
    # Native commands read processor links and write reconstructed fields only
    # into this fresh case. Resolve /media and ~/OpenFOAM aliases before linking.
    target.mkdir()
    shutil.copytree(source/'system',target/'system')
    shutil.copytree(source/'constant',target/'constant')
    for rank in source.glob('processor*'):
        if rank.is_dir():(target/rank.name).symlink_to(rank.resolve(),target_is_directory=True)
    setting(target,'system/controlDict','writeFormat','ascii')
    run(target,'reconstructHistory',['reconstructPar','-time','0:0.00005',
                                    '-fields','(alpha.metal T epsilon1)'])
    run(target,'writeCellCentres',['postProcess','-func','writeCellCentres','-time','0'])


def common_indices(case,cells):
    pilot.CELLS=cells
    state=final_state(case,None,0.)
    indices={};keys=set()
    for index,centre in enumerate(pilot.field_rows(state/'C',3)):
        if not all(lo<x<hi for x,(lo,hi) in zip(centre,ROI)):continue
        raw=[(x-lo)/DX-.5 for x,(lo,hi) in zip(centre,ROI)]
        key=tuple(round(x) for x in raw)
        if any(abs(x-k)>1e-6 for x,k in zip(raw,key)) or key in keys:
            raise ValueError('Common ROI is not a unique 6um cell-centre lattice')
        keys.add(key);indices[index]=key
    if len(keys)!=math.prod(SHAPE):raise ValueError('Incomplete common 6um ROI')
    return indices


def gas_cavity_depth(alpha):
    """Cell-centre depth of alpha<0.5 gas connected to the ROI top by faces."""
    gas={key for key,value in alpha.items() if value<.5}
    seen={key for key in gas if key[1]==SHAPE[1]-1}
    queue=deque(seen);lowest=600e-6
    while queue:
        key=queue.popleft()
        lowest=min(lowest,ROI[1][0]+(key[1]+.5)*DX)
        for axis in range(3):
            for sign in (-1,1):
                neighbour=list(key);neighbour[axis]+=sign;neighbour=tuple(neighbour)
                if neighbour in gas and neighbour not in seen:
                    seen.add(neighbour);queue.append(neighbour)
    return max(0.,(600e-6-lowest)*1e6)


def snapshot(case,stamp,cells,indices):
    pilot.CELLS=cells
    state=final_state(case,None,stamp)
    epsilon=(itertools.repeat((0.,),cells) if stamp==0 else pilot.field_rows(state/'epsilon1',1))
    alpha={};initial={};peaks=dict(metal=0.,interface=0.,gas=0.)
    liquid_volume=metal_volume=0.;solidus=[]
    for index,(ar,tr,er) in enumerate(zip(pilot.field_rows(state/'alpha.metal',1),
                                         pilot.field_rows(state/'T',1),epsilon)):
        a,t,e=ar[0],tr[0],er[0]
        if not (-1e-8<=a<=1+1e-8 and -1e-8<=e<=1+1e-8):
            raise ValueError('Unbounded alpha/epsilon in saved field')
        if stamp==0 and a>.5 and t>=1537:
            raise ValueError('Initial metal is molten; cannot assume missing initial epsilon=0')
        if index not in indices:continue
        key=indices[index];alpha[key]=a
        region='metal' if a>=.99 else 'gas' if a<=.01 else 'interface'
        peaks[region]=max(peaks[region],t)
        liquid_volume+=max(0.,a)*max(0.,e)*DX**3
        metal_volume+=max(0.,a)*DX**3
        if stamp==0:initial[key]=(a,t)
        if a>=.5 and t>=1537:solidus.append(key)
    if len(alpha)!=len(indices):raise ValueError('Truncated common ROI fields')
    depth=max((600e-6-(ROI[1][0]+(k[1]+.5)*DX))*1e6 for k in solidus) if solidus else 0.
    width=(max(k[2] for k in solidus)-min(k[2] for k in solidus))*6 if solidus else 0.
    return dict(time_s=stamp,roi_metal_volume_m3=metal_volume,
                roi_liquid_fraction_volume_m3=liquid_volume,
                roi_solidus_depth_um=max(0.,depth),roi_solidus_width_um=width,
                top_connected_gas_cavity_depth_um=gas_cavity_depth(alpha),
                roi_temperature_maxima_K=peaks),initial


def initial_difference(reference,candidate):
    if reference.keys()!=candidate.keys():raise ValueError('Initial ROI cell sets differ')
    return dict(cells=len(reference),max_alpha_difference=max(abs(v[0]-candidate[k][0]) for k,v in reference.items()),
                max_temperature_difference_K=max(abs(v[1]-candidate[k][1]) for k,v in reference.items()))


def relative(reference,candidate):
    if reference==0:return 0. if candidate==0 else None
    return abs(candidate-reference)/abs(reference)


def execute(a,work):
    save(work/'environment.json',environment())
    sources=[a.baseline_case.resolve(),a.candidate_case.resolve()]
    if sources[0]==sources[1] or any(not p.is_dir() for p in sources):
        raise ValueError('Two distinct existing completed case directories required')
    if any(work==p or p in work.parents or work in p.parents for p in sources):
        raise ValueError('Collection work must be separate from both source cases')
    evidence=[load_work(p.parent) for p in sources]
    original_comparison=compare(evidence[0],evidence[1],None)
    original_comparison['evidence_source']='Existing completed work directories; no baseline archive hash is asserted by this collector'
    save(work/'originalComparison.json',original_comparison)
    inventories=[source_inventory(p) for p in sources]
    save(work/'sourceInventory.json',dict(zip(('baseline','candidate'),inventories)))
    histories=[];initial=[];collection_start=time.perf_counter()
    try:
        for label,source,data in zip(('baseline','candidate'),sources,evidence):
            target=work/label;shadow_case(source,target)
            cells=data['track1500/probe.json']['cells']
            indices=common_indices(target,cells);rows=[]
            for stamp in TIMES:
                print(f'Collecting {label} {stamp*1e6:.0f} us; no CFD advanced',flush=True)
                row,start=snapshot(target,stamp,cells,indices);rows.append(row)
                if stamp==0:initial.append(start)
            histories.append(rows);save(work/(label+'History.json'),rows)
        difference=initial_difference(*initial)
        comparisons=[]
        for ref,can in zip(*histories):
            comparisons.append(dict(time_s=ref['time_s'],relative_differences={
                key:relative(ref[key],can[key]) for key in ('roi_liquid_fraction_volume_m3',
                'roi_solidus_depth_um','roi_solidus_width_um','top_connected_gas_cavity_depth_um')},
                temperature_relative_differences={key:relative(ref['roi_temperature_maxima_K'][key],
                    can['roi_temperature_maxima_K'][key]) for key in ('metal','interface','gas')}))
        save(work/'historyComparison.json',dict(schema=1,complete=True,
            source_cases=[str(p) for p in sources],common_roi_m=ROI,cell_spacing_m=DX,
            initial_common_roi=difference,initial_mapping_match=difference['max_alpha_difference']<=1e-12
                and difference['max_temperature_difference_K']<=1e-9,
            comparisons=comparisons,collection_wall_s=time.perf_counter()-collection_start,
            cfd_advanced=False,production_approved=False,
            note='Liquid volume integrates alpha*epsilon over identical 6um cells in the common ROI, not the whole domain. Cavity depth uses face-connected gas alpha<0.5 from ROI top; cell-centre uncertainty is about 3um and literature/keyhole validation remains pending. Original failed peak-temperature screen is retained; these histories do not override it.'))
    finally:
        intact=[unchanged(item) for item in inventories]
        save(work/'sourceUnchanged.json',dict(baseline=intact[0],candidate=intact[1],
             verification='size and nanosecond mtime of saved fields and mesh/control metadata; not content hashes'))
        if not all(intact):raise ValueError('Source file metadata changed during read-only collection')


def package(work,code):
    files=[p for p in work.iterdir() if p.is_file() and p.name!='manifest.json']
    for label in ('baseline','candidate'):
        files.extend(p for p in (work/label).glob('log.*') if p.is_file())
    required=('historyComparison.json','sourceUnchanged.json','baselineHistory.json','candidateHistory.json')
    missing=[name for name in required if not (work/name).is_file()]
    save(work/'manifest.json',dict(schema=1,exit_code=code,complete=code==0 and not missing,
        missing_files=missing,files=[dict(path=p.relative_to(work).as_posix(),
        size=p.stat().st_size,sha256=digest(p)) for p in files]))
    archive=work.parent/('M247_'+work.name+'_review.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for p in files+[work/'manifest.json']:tar.add(p,arcname=work.name+'/'+p.relative_to(work).as_posix())
    print('Review archive: '+str(archive)+'\nSend this single archive, including on failure. No CFD advanced.',flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('baseline_case',type=Path);parser.add_argument('candidate_case',type=Path)
    parser.add_argument('--work',type=Path)
    a=parser.parse_args()
    work=(a.work or Path(__file__).resolve().parent/'runs'/('m247-local-corridor-history-'+time.strftime('%Y%m%d-%H%M%S'))).resolve()
    work.mkdir(parents=True,exist_ok=False);code=1
    try:execute(a,work);code=0
    finally:package(work,code)


if __name__=='__main__':main()
