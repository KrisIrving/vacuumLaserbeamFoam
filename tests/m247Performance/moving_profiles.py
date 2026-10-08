#!/usr/bin/env python3
"""Compare physical-coordinate slab profiles of stored moving-CFD snapshots."""
import argparse,json,math,re,subprocess
from pathlib import Path
from collect_probe import parse_records
from compare_moving_steps import compare
from region_audit import sha
from collect_thermal_validation import final_state

KEYS=('volume','metal','liquid','metalT','metalUx','metalUy','metalUz')

def collect(text):
    state=parse_records(text,'M247_PROFILE_STATE');rows=parse_records(text,'M247_PROFILE')
    if len(state)!=1 or state[0].get('schema')!=1 or state[0].get('invalid')!=0 or state[0].get('ranks')!=48 or abs(state[0].get('time',0)-.0001802)>1e-12 or not re.search(r'^End\s*$',text,re.M):raise ValueError('Incomplete profile snapshot')
    if len(rows)!=153:raise ValueError('Missing coordinate slabs')
    for d,n in enumerate((53,60,40)):
        selected=[r for r in rows if r.get('axis')==d]
        if [r.get('bin') for r in selected]!=list(range(n)):raise ValueError('Wrong slab IDs')
        lo,hi=((-520e-6,320e-6),(0,960e-6),(-320e-6,320e-6))[d]
        for j,r in enumerate(selected):
            if r.get('schema')!=1 or abs(r.get('time',0)-.0001802)>1e-12:raise ValueError('Wrong profile time/schema')
            if abs(r.get('low',1)-(lo+(hi-lo)*j/n))>1e-12 or abs(r.get('high',1)-(lo+(hi-lo)*(j+1)/n))>1e-12:raise ValueError('Wrong coordinate slab')
            if any(k not in r or not math.isfinite(r[k]) for k in KEYS):raise ValueError('Nonfinite profile')
            if r['volume']<=0 or r['metal']<-1e-18 or r['liquid']<-1e-18 or r['metal']>r['volume']+1e-18 or r['liquid']>r['metal']+1e-18 or r['metalT']<0:raise ValueError('Invalid profile integrals')
        if not math.isclose(sum(r['volume'] for r in selected),(840e-6)*(960e-6)*(640e-6),rel_tol=1e-8):raise ValueError('Domain volume mismatch')
    totals=[{k:sum(r[k] for r in rows if r['axis']==d) for k in KEYS} for d in range(3)]
    for k in KEYS:
        if any(abs(t[k]-totals[0][k])>1e-8*max(sum(abs(r[k]) for r in rows if r['axis']==0),1e-30) for t in totals[1:]):raise ValueError('Axis totals mismatch')
    return dict(state=state[0],rows=rows,totals=totals[0])

def fingerprint(case):
    result={}
    for rank in range(48):
        folder=final_state(case,rank,.0001802)
        for name in ('T','U','alpha.metal','epsilon1'):result[str(folder/name)]=sha(folder/name)
        base=case/f'processor{rank}'
        choices=[]
        for path in base.iterdir():
            try:value=float(path.name)
            except ValueError:continue
            if value<=.0001802+1e-12 and (path/'polyMesh').is_dir():choices.append((value,path/'polyMesh'))
        mesh=max(choices,key=lambda x:x[0])[1] if choices else base/'constant/polyMesh'
        if not mesh.is_dir():raise ValueError('Missing stored mesh')
        for path in mesh.rglob('*'):
            if path.is_symlink():raise ValueError('Mesh symlink unsupported')
            if path.is_file():result[str(path)]=sha(path)
    return result

def execute(reference,candidate,work,utility):
    for source in (reference,candidate):
        if work==source or source in work.parents or work in source.parents:raise ValueError("Audit output overlaps input run")
    work.mkdir(parents=True,exist_ok=False)
    report=dict(schema=1,complete=False,production_approved=False,no_cfd_advanced=True)
    target=work/'movingProfileComparison.json'
    def save():target.write_text(json.dumps(report,indent=2)+'\n')
    save()
    try:
        report['diagnostics']=compare(reference/'movingCFDReview.json',candidate/'movingCFDReview.json')
        report['utility_sha256']=sha(utility);profiles=[]
        for name,run in (('reference',reference),('candidate',candidate)):
            case=run/'movingCFD';before=fingerprint(case)
            with (work/(name+'Profiles.log')).open('x') as f:
                subprocess.run(['mpirun','-np','48',str(utility),'-case',str(case),'-parallel','-time','0.0001802'],stdout=f,stderr=subprocess.STDOUT,check=True,timeout=600)
            if fingerprint(case)!=before:raise ValueError('Stored fields/mesh changed during audit')
            report[name+'_inputs_sha256']=before
            profiles.append(collect((work/(name+'Profiles.log')).read_text()))
        a,b=profiles;differences=[]
        for x,y in zip(a['rows'],b['rows']):
            differences.append(dict(axis=x['axis'],bin=x['bin'],low=x['low'],high=x['high'],
                differences={k:y[k]-x[k] for k in KEYS}))
        report.update(complete=True,profiles=profiles,differences=differences,
            note='Centroid-assigned slabs: directional screening only, not a conservative 3D overlap map, enthalpy audit or geometry convergence. Different cell sizes can affect slab assignment; no production approval.')
        save();return report
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as e:
        report.update(error=str(e),error_type=type(e).__name__);save();raise

def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('reference','candidate','work','utility'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    try:execute(a.reference.resolve(),a.candidate.resolve(),a.work.resolve(),a.utility.resolve());print('Profile screening collected; production approved: False')
    except (ValueError,KeyError,OSError,subprocess.SubprocessError) as e:p.exit(1,str(e)+'\n')
if __name__=='__main__':main()
