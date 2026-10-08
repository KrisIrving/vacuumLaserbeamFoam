#!/usr/bin/env python3
"""Self-contained native regional interface acceptance; not an LPBF benchmark."""
import argparse
import hashlib
import json
import math
import os
import signal
from pathlib import Path
import re
import subprocess
import time


def save(path,data):
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def foam_header(name,kind='dictionary'):
    return f'FoamFile {{ version 2.0; format ascii; class {kind}; object {name}; }}\n'


def field(name,kind,dimensions,value,boundaries):
    return foam_header(name,kind)+f'dimensions [{dimensions}];\ninternalField uniform {value};\nboundaryField\n{{\n'+boundaries+'\n}\n'


def block_mesh(x0,x1,nx,ny,nz):
    vertices=[(x0,0,0),(x1,0,0),(x1,.001,0),(x0,.001,0),
              (x0,0,.001),(x1,0,.001),(x1,.001,.001),(x0,.001,.001)]
    return foam_header('blockMeshDict')+'scale 1;\nvertices\n(\n'+'\n'.join('(%g %g %g)'%p for p in vertices)+f'\n);\nblocks (hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 1 1));\n'+'''edges ();
boundary
(
 inlet { type patch; faces ((0 4 7 3)); }
 outlet { type patch; faces ((1 2 6 5)); }
 walls { type wall; faces ((0 1 5 4) (3 7 6 2) (0 3 2 1) (4 5 6 7)); }
);
mergePatchPairs ();
'''


def prepare_fixture(case,cooling=False):
    if case.exists():raise ValueError('Fixture must be fresh')
    def write(relative,content):
        p=case/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content,encoding='utf-8')
    write('system/controlDict',foam_header('controlDict')+'''application m247RegionalCouplingAudit;
startFrom startTime; startTime 0; stopAt endTime; endTime 1e-9;
deltaT 1e-9; writeControl timeStep; writeInterval 1; runTimeModifiable false;
''')
    schemes=foam_header('fvSchemes')+'''ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes { default Gauss linear; }
laplacianSchemes { default Gauss linear orthogonal; }
interpolationSchemes { default linear; }
snGradSchemes { default orthogonal; }
'''
    solution=foam_header('fvSolution')+'''solvers
{ pRegionalCorrection { solver PCG; preconditioner DIC; tolerance 1e-14; relTol 0; maxIter 1000; } }
'''
    decomposition=foam_header('decomposeParDict')+'''numberOfSubdomains 2; method simple;
simpleCoeffs { n (1 2 1); delta 0.001; }
'''
    write('constant/regionProperties',foam_header('regionProperties')+'regions (fluid (flowRegion) solid (thermalRegion));\n')
    write('system/decomposeParDict',decomposition)
    for region,bounds in (('thermalRegion',(0,.001,4,2,2)),('flowRegion',(.0002,.0008,5,4,4))):
        write(f'system/{region}/blockMeshDict',block_mesh(*bounds))
        write(f'system/{region}/fvSchemes',schemes)
        write(f'system/{region}/fvSolution',solution)
        write(f'system/{region}/decomposeParDict',decomposition)
    write('constant/regionalTransferDict',foam_header('regionalTransferDict')+'''rho 7950; rhoGas 1; cpGas 520; LatentHeatGas 1;
kappa 29; Tsolidus 1537; Tliquidus 1631; cpSolidus 790; cpLiquidus 860; LatentHeat 150000;
auditDeltaT 1e-9; manufacturedCorrectionDensity 0;
mixtureAudit true; sourceAudit true; globalContainsLocalSources false;
localProjectionAudit true; projectionPasses 2; projectionDivergenceTolerance 1e-5;
''')
    zero='inlet { type zeroGradient; } outlet { type zeroGradient; } walls { type zeroGradient; }'
    for name,dim,value in (('T','0 0 0 1 0 0 0','1580'),('alpha.metal','0 0 0 0 0 0 0','0'),('epsilon1','0 0 0 0 0 0 0','0')):
        write(f'0/thermalRegion/{name}',field(name,'volScalarField',dim,value,zero))
    write('system/thermalRegion/setFieldsDict',foam_header('setFieldsDict')+'''defaultFieldValues (volScalarFieldValue alpha.metal 0 volScalarFieldValue epsilon1 0);
regions (boxToCell { box (-1 -1 -1) (0.0005 1 1); fieldValues
    (volScalarFieldValue alpha.metal 1 volScalarFieldValue epsilon1 1); });
''')
    write('0/flowRegion/U',field('U','volVectorField','0 1 -1 0 0 0 0','(0.2 0 0)',
        'inlet { type fixedValue; value uniform (0.1 0 0); } outlet { type zeroGradient; } walls { type fixedValue; value uniform (0 0 0); }'))
    write('0/flowRegion/rho',field('rho','volScalarField','1 -3 0 0 0 0 0','4000',zero))
    write('0/flowRegion/pRegionalCorrection',field('pRegionalCorrection','volScalarField','1 -1 -2 0 0 0 0','0',
        'inlet { type fixedFluxPressure; value uniform 0; } outlet { type fixedValue; value uniform 0; } walls { type fixedFluxPressure; value uniform 0; }'))
    values=(1e14,4e14,1e14,0,0) if cooling else (1e15,2e14,1e14,-5e13,0)
    for name,value in zip(('regionalLaserGain','regionalEvaporationLoss','regionalRadiationLoss','regionalAdvectionGain','regionalConductionGain'),values):
        write(f'0/flowRegion/{name}',field(name,'volScalarField','1 -1 -3 0 0 0 0',str(value),zero))


def digest_case(case):
    # Include all original and processor input files; native audit must not write any.
    return {str(p.relative_to(case)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(case.rglob('*')) if p.is_file()}


def parse_audit(text):
    if re.search(r'FOAM FATAL|Segmentation fault|MPI_ABORT',text) or not re.search(r'^End\s*$',text,re.M):
        raise ValueError('Native audit did not finish cleanly')
    result={}
    for marker in ('M247_LOCAL_PROJECTION','M247_REGIONAL_SOURCES','M247_REGIONAL_MIXTURE_AUDIT'):
        lines=re.findall(r'^'+marker+r'\s+(.+)$',text,re.M)
        if len(lines)!=1:raise ValueError('Missing/duplicate native marker: '+marker)
        data={k:float(v) for k,v in re.findall(r'(\w+)=([-+\d.eE]+)',lines[0])}
        if not data or any(not math.isfinite(v) for v in data.values()):raise ValueError('Invalid audit values')
        result[marker]=data
    projection=result['M247_LOCAL_PROJECTION'];sources=result['M247_REGIONAL_SOURCES'];energy=result['M247_REGIONAL_MIXTURE_AUDIT']
    requirements=((projection,('schema','initialMaxDiv','finalMaxDiv','boundaryNetM3PerS','productionApproved')),
                  (sources,('schema','laserJ','evaporationLossJ','radiationLossJ','advectionGainJ','conductionDeltaJ','totalDeltaJ','globalContainsLocalSources','productionApproved')),
                  (energy,('schema','ranks','beforeJ','afterJ','heatAddedJ','correctionJ','ledgerResidualJ','inverseRelativeError','capacityMomentsMapped','productionApproved','globalCells','localCells','mappedTemperatureDifference','constantError')))
    for data,keys in requirements:
        if any(k not in data for k in keys) or data['productionApproved']!=0:raise ValueError('Audit contract missing/changed')
    if projection['schema']!=1 or sources['schema']!=1 or energy['schema']!=2 or energy['capacityMomentsMapped']!=1 or sources['globalContainsLocalSources']!=0:
        raise ValueError('Rebuild required: native audit schema mismatch')
    if energy['globalCells']!=16 or energy['localCells']!=80 or energy['constantError']>1e-14 or energy['mappedTemperatureDifference']>1e-7:
        raise ValueError('Fixture geometry/constant/uniform temperature remap gate failed')
    if projection['initialMaxDiv']<=1e-5 or projection['finalMaxDiv']>1e-5:
        raise ValueError('Projection did not exercise/remove predictor divergence')
    if energy['inverseRelativeError']<0 or energy['ledgerResidualJ']<0 or energy['inverseRelativeError']>1e-10 or energy['ledgerResidualJ']>1e-10*max(abs(energy['beforeJ'])+abs(energy['correctionJ']),1e-300):
        raise ValueError('Native energy gate failed')
    expected=sources['laserJ']-sources['evaporationLossJ']-sources['radiationLossJ']+sources['advectionGainJ']+sources['conductionDeltaJ']
    if not math.isclose(expected,sources['totalDeltaJ'],rel_tol=1e-9,abs_tol=1e-12):raise ValueError('Source component ledger mismatch')
    if abs(projection['boundaryNetM3PerS'])>6e-15:raise ValueError('Projection physical boundary flux gate failed')
    if not math.isclose(energy['afterJ']-energy['beforeJ'],energy['heatAddedJ']+energy['correctionJ'],rel_tol=1e-7,abs_tol=1e-10):raise ValueError('Energy totals inconsistent with source delta')
    return result


def compare_audits(serial,parallel,expected_delta):
    for report,ranks in ((serial,1),(parallel,2)):
        energy=report['M247_REGIONAL_MIXTURE_AUDIT'];sources=report['M247_REGIONAL_SOURCES']
        if energy['ranks']!=ranks:raise ValueError('Unexpected native MPI size')
        for value in (energy['correctionJ'],sources['totalDeltaJ']):
            if not math.isclose(value,expected_delta,rel_tol=1e-9,abs_tol=1e-12):raise ValueError('Unexpected integrated source correction')
    for marker,keys in (('M247_REGIONAL_MIXTURE_AUDIT',('beforeJ','afterJ','heatAddedJ','correctionJ')),
                        ('M247_REGIONAL_SOURCES',('laserJ','evaporationLossJ','radiationLossJ','advectionGainJ','conductionDeltaJ','totalDeltaJ'))):
        for key in keys:
            if not math.isclose(serial[marker][key],parallel[marker][key],rel_tol=1e-9,abs_tol=1e-12):
                raise ValueError('Serial/MPI disagreement: '+key)



def run_bounded(command,output,remaining):
    """Stop the complete MPI process group on timeout/interruption on Ubuntu."""
    process=subprocess.Popen(command,stdout=output,stderr=subprocess.STDOUT,start_new_session=os.name=='posix')
    try:return process.wait(timeout=remaining)
    except BaseException:
        if process.poll() is None:
            if os.name=='posix':os.killpg(process.pid,signal.SIGTERM)
            else:process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                if os.name=='posix':os.killpg(process.pid,signal.SIGKILL)
                else:process.kill()
                process.wait(timeout=5)
        raise

def execute(work,solver,budget=600):
    if not math.isfinite(budget) or budget<=0:raise ValueError('Positive acceptance time budget required')
    work=Path(work).resolve();solver=Path(solver).resolve()
    if not solver.is_file():raise ValueError('Native audit binary missing')
    state={'schema':1,'complete':False,'production_approved':False,'stages':[],
           'solver':str(solver),'solver_sha256':hashlib.sha256(solver.read_bytes()).hexdigest(),'budget_s':budget}
    start=time.monotonic()
    def stage(name,command):
        remaining=budget-(time.monotonic()-start)
        if remaining<=0:raise TimeoutError('Integrated acceptance wall budget exhausted')
        row={'name':name,'command':list(map(str,command)),'status':'running'};state['stages'].append(row)
        save(work/'regionalAcceptance.json',state)
        print('Starting regional stage:',name,flush=True)
        with (work/(name+'.log')).open('w',encoding='utf-8') as output:
            try:
                returncode=run_bounded(row['command'],output,remaining)
                row.update(returncode=returncode,status='complete' if returncode==0 else 'failed')
                if returncode:raise RuntimeError(f'{name} returned {returncode}')
            except BaseException as error:
                row.update(status='failed',error=f'{type(error).__name__}: {error}');raise
            finally:save(work/'regionalAcceptance.json',state)
    try:
        for variant,cooling in (('regionalGain',False),('regionalLoss',True)):
            case=work/variant;prepare_fixture(case,cooling)
            save(work/(variant+'_fixtureInputs.json'),{str(p.relative_to(case)):p.read_text(encoding='utf-8') for p in sorted(case.rglob('*')) if p.is_file()})
            for region in ('thermalRegion','flowRegion'):
                stage(f'{variant}_{region}_blockMesh',['blockMesh','-case',case,'-region',region])
            stage(f'{variant}_setFields',['setFields','-case',case,'-region','thermalRegion'])
            before=digest_case(case);save(work/(variant+'_inputHashes.json'),before)
            stage(f'{variant}_serial',[solver,'-case',case,'-time','0'])
            if digest_case(case)!=before:raise ValueError('Serial audit modified fixture inputs')
            serial=parse_audit((work/(variant+'_serial.log')).read_text(encoding='utf-8',errors='replace'))
            stage(f'{variant}_decompose',['decomposePar','-case',case,'-allRegions'])
            before=digest_case(case);save(work/(variant+'_parallelInputHashes.json'),before)
            stage(f'{variant}_parallel',['mpirun','-np','2',solver,'-case',case,'-time','0','-parallel'])
            if digest_case(case)!=before:raise ValueError('MPI audit modified fixture inputs')
            parallel=parse_audit((work/(variant+'_parallel.log')).read_text(encoding='utf-8',errors='replace'))
            compare_audits(serial,parallel,-.00024 if cooling else .00039)
            state[variant]={'serial':serial,'parallel':parallel,'inputs_unchanged':True,'serial_parallel_gate':True}
        state['complete']=True
    except BaseException as error:
        state['error']=f'{type(error).__name__}: {error}';raise
    finally:
        state['elapsed_s']=time.monotonic()-start;save(work/'regionalAcceptance.json',state)
    return state


def finalize(work,requested_status):
    path=Path(work)/'regionalAcceptance.json'
    state=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {'schema':1,'complete':False,'error':'Native acceptance did not start'}
    complete=state.get('complete') is True and bool(state.get('stages')) and all(row.get('status')=='complete' and row.get('returncode')==0 for row in state.get('stages',[])) and all(state.get(v,{}).get('serial_parallel_gate') is True for v in ('regionalGain','regionalLoss'))
    status=requested_status if requested_status else (0 if complete else 1)
    save(Path(work)/'regionalAcceptanceStatus.json',{'schema':1,'complete':complete and status==0,'exit_code':status,'production_approved':False})
    return status


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--work',type=Path,required=True)
    parser.add_argument('--solver',type=Path);parser.add_argument('--finalize',action='store_true');parser.add_argument('--requested-status',type=int,default=0)
    args=parser.parse_args()
    if args.finalize:raise SystemExit(finalize(args.work,args.requested_status))
    if not args.solver:parser.error('--solver required')
    try:execute(args.work,args.solver)
    except (OSError,ValueError,RuntimeError,subprocess.TimeoutExpired,TimeoutError) as error:parser.exit(1,f'Regional acceptance failed: {error}\n')
    print('Native regional interface acceptance complete; production approved: False',flush=True)


if __name__=='__main__':main()
