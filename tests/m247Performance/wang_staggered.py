#!/usr/bin/env python3
"""One fresh384-ray ring-staggered history against retained Wang references."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import tarfile
import time

from wang_ray_suite import run, setting, digest, save, summarize, compare_histories
from collect_probe import parse_records

def collect(work):
    case=work/'rays384Staggered'
    candidate=summarize(case)
    flags=parse_records((case/'log.vacuumLaserbeamFoam').read_text(errors='replace'),'RAY_ANGULAR_SAMPLING')
    if len(flags)!=candidate['steps'] or any(r.get('staggered')!=1 or r.get('nRadial')!=16 or r.get('nAngular')!=24 for r in flags):
        raise ValueError('Missing/mismatched per-call staggered384-ray evidence')
    comparisons={}
    for name in ('rays1536','rays384'):
        reference=json.loads((work/'reference'/name/'summary.json').read_text())
        comparisons[name]=compare_histories(reference,candidate)
    report=dict(schema=1,complete=True,comparisons=comparisons,production_approved=False,
        note='Reference CFD was already completed using pre-stagger implementation; costs are historical comparisons, not same-binary paired timings. Thermal convergence and full-history user budgets are retained.')
    save(work/'comparison.json',report)
    print(json.dumps(report,indent=2),flush=True)

def execute(source,work):
    source=source.resolve();seed=source/'prepared'
    library=Path(os.environ['FOAM_USER_LIBBIN'])/'liblaserHeatSource.so'
    if b'RAY_ANGULAR_SAMPLING schema=1 staggered=' not in library.read_bytes():
        raise ValueError('Rebuild required: missing staggered sampling marker')
    solver=Path(shutil.which('vacuumLaserbeamFoam')).resolve()
    save(work/'binaries.json',dict(solver=str(solver),solver_sha256=digest(solver),laser_library_sha256=digest(library)))
    expected=json.loads((source/'commonInitialHashes.json').read_text())
    if any(digest(seed/path)!=value for path,value in expected.items()):
        raise ValueError('Retained prepared mesh/initial fields changed')
    case=work/'rays384Staggered';case.mkdir()
    for item in seed.iterdir():
        if item.is_dir() and (item.name in ('constant','system','0','scripts') or item.name.startswith('processor')):
            shutil.copytree(item,case/item.name)
    if any(digest(case/path)!=value for path,value in expected.items()):
        raise ValueError('Copied initial fields/decomposition mismatch')
    meta=json.loads((source/'rays1536/probe.json').read_text())
    meta.update(variant=case.name,nAngular=24,rays=384,staggeredAngularSampling=True)
    save(case/'probe.json',meta)
    setting(case,'constant/LaserProperties','nAngular',24)
    setting(case,'constant/LaserProperties','staggeredAngularSampling','true')
    # Prove all other physical/numerical dictionaries match the retained1536 case.
    def normal(text):
        text=re.sub(r'/\*.*?\*/|//[^\n]*','',text,flags=re.S)
        text=re.sub(r'\bstaggeredAngularSampling\s+(?:true|false)\s*;','',text)
        text=re.sub(r'\bnAngular\s+\d+\s*;','nAngular SAME;',text)
        return re.sub(r'\s+','',text)
    for folder in ('constant','system'):
        for p in (case/folder).iterdir():
            if p.is_file():
                other=source/'rays1536'/folder/p.name
                if not other.is_file() or normal(p.read_text())!=normal(other.read_text()):
                    raise ValueError('Reference settings differ beyond sampling: '+str(p))
    save(work/'initialProvenance.json',dict(source=str(source),initial_hashes=expected,
        scope='Same retained prepared mesh, initial state and partition; only angular count and ring phase differ'))
    for name in ('rays1536','rays384'):
        dest=work/'reference'/name;dest.mkdir(parents=True)
        for p in (source/name).iterdir():
            if p.is_file() and (p.suffix in ('.json','.csv') or p.name=='log.vacuumLaserbeamFoam'):
                shutil.copyfile(p,dest/p.name)
    start=time.perf_counter();code=1
    try:
        run(case,'vacuumLaserbeamFoam',['mpirun','-np','48',solver,'-parallel']);code=0
    finally:
        save(case/'run.json',dict(elapsed_wall_s=time.perf_counter()-start,returncode=code,wall_budget_stop=False,forced_stop=False))
    run(case,'reconstructPar',['reconstructPar','-fields','(alpha.metal epsilon1 T pVap)','-time','2e-6:'])
    for name,fields,dictionary in (('keyholeInterface','(alpha.metal)','keyholeInterfaceDict'),('keyholeRecoil','(alpha.metal pVap T)','keyholeRecoilDict')):
        run(case,'postProcess.'+name,['postProcess','-dict','system/'+dictionary,'-fields',fields,'-time','2e-6:'])
    for script,folder,out in (('extractKeyholeSurfaceDepth.py','keyholeInterface','keyholeDepthSurface.csv'),('extractKeyholeRecoil.py','keyholeRecoilSurface','keyholeRecoilSurface.csv')):
        run(case,script,['python3','scripts/'+script,'--post-processing','postProcessing/'+folder,'--surface-y','200e-6','--surface-band','8e-6','--output',out])
    collect(work)

def package(work,code):
    files=[p for p in work.rglob('*') if p.is_file() and not any(part.startswith('processor') or part in ('polyMesh','postProcessing') for part in p.relative_to(work).parts)
        and (p.suffix in ('.json','.csv','.txt','.log') or p.name.startswith('log.') or p.parent.name in ('constant','system')) and p.name!='manifest.json']
    required=('comparison.json','rays384Staggered/summary.json','rays384Staggered/liquidVolume.json','reference/rays1536/summary.json','reference/rays384/summary.json')
    missing=[p for p in required if not (work/p).is_file()]
    save(work/'manifest.json',dict(schema=1,exit_code=code,complete=code==0 and not missing,missing_files=missing,
        files=[dict(path=p.relative_to(work).as_posix(),size=p.stat().st_size,sha256=digest(p)) for p in files]))
    archive=work.parent/('M247_'+work.name+'_review.tar.gz')
    with tarfile.open(archive,'w:gz') as tar:
        for p in files+[work/'manifest.json']:tar.add(p,arcname=work.name+'/'+p.relative_to(work).as_posix())
    print('Review archive: '+str(archive)+'\nSend this single archive, including on failure.',flush=True)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--source',type=Path);ap.add_argument('--work',type=Path,required=True)
    ap.add_argument('--collect',action='store_true');ap.add_argument('--package',action='store_true');ap.add_argument('--exit-code',type=int,default=0)
    a=ap.parse_args();work=a.work.resolve()
    if a.package:package(work,a.exit_code)
    elif a.collect:collect(work)
    elif a.source:execute(a.source,work)
    else:ap.error('--source required to execute')

if __name__=='__main__':main()
