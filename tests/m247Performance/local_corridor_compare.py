#!/usr/bin/env python3
"""Compare one local 50us DEM pilot with the completed V2 archive."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import tarfile

NEEDED=('pilotReport.json','inputHashes.json','solverCheck.json',
        'openfoamVersion.txt','track1500/probe.json',
        'track1500/log.vacuumLaserbeamFoam')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def load_archive(path):
    path=Path(path).resolve()
    with tarfile.open(path,'r:gz') as tar:
        matches=[name for name in tar.getnames() if name.endswith('/manifest.json')]
        if len(matches)!=1:
            raise ValueError('Expected exactly one baseline manifest')
        prefix=matches[0][:-len('manifest.json')]
        def read(name):
            member=tar.getmember(prefix+name)
            if not member.isfile():raise ValueError('Non-file baseline member: '+name)
            return tar.extractfile(member).read()
        manifest=json.loads(read('manifest.json'))
        if manifest.get('exit_code')!=0 or not manifest.get('complete') or manifest.get('missing_files'):
            raise ValueError('Baseline pilot archive is incomplete')
        files={item['path']:item['sha256'] for item in manifest['files']}
        if any(name not in files for name in NEEDED):
            raise ValueError('Baseline archive lacks required hashed evidence')
        for name,expected in files.items():
            if digest(read(name))!=expected:
                raise ValueError('Baseline archive hash mismatch: '+name)
        data={name:read(name) for name in NEEDED}
    return parse_data(data),digest(path.read_bytes())


def load_work(path):
    path=Path(path)
    data={name:(path/name).read_bytes() for name in NEEDED}
    return parse_data(data)


def parse_data(data):
    result={name:json.loads(data[name]) for name in NEEDED if name.endswith('.json')}
    result['environment']=dict(line.split('=',1) for line in
        data['openfoamVersion.txt'].decode('utf-8').splitlines() if '=' in line)
    log=data['track1500/log.vacuumLaserbeamFoam'].decode('utf-8',errors='replace')
    powers=re.findall(r'\bdepositedPower=([-+0-9.eE]+)',log)
    if not powers:raise ValueError('Missing deposited-power diagnostic')
    result['depositedPower_W']=float(powers[-1])
    thermal_rows=[(float(residual),int(iterations)) for residual,iterations in
        re.findall(r'Solving for T, Initial residual = [-+0-9.eE]+, Final residual = ([-+0-9.eE]+), No Iterations (\d+)',log)]
    if not thermal_rows:raise ValueError('Missing temperature linear-solver records')
    result['T_linear_cap_count']=sum(n>=1000 for _,n in thermal_rows)
    result['T_linear_above_tolerance_count']=sum(r>1e-9*(1+1e-8) for r,_ in thermal_rows)
    return result


def check_baseline(baseline,dem_archive):
    probe=baseline['track1500/probe.json']
    report=baseline['pilotReport.json']
    env=baseline['environment']
    if (env.get('WM_PROJECT_VERSION') not in ('v2512','2512')
        or not env.get('WM_PROJECT_DIR','').endswith('/OpenFOAM-v2512')
        or not env.get('WMAKE','').endswith('/OpenFOAM-v2512/wmake/wmake')):
        raise ValueError('Baseline did not run in a recorded v2512 environment')
    if (probe.get('variant')!='track1500PilotDEM' or probe.get('cells')!=3814272
        or probe.get('rays')!=384 or probe.get('ranks')!=48
        or probe.get('end_s')!=50e-6 or not report.get('complete')):
        raise ValueError('Baseline is not the completed V2 50us DEM pilot')
    if not baseline['solverCheck.json'].get('passed'):
        raise ValueError('Baseline solver preflight did not pass')
    expected=report.get('demHandoff',{}).get('archiveSha256')
    if not expected or expected!=digest(Path(dem_archive).read_bytes()):
        raise ValueError('DEM archive differs from baseline powder')
    return expected


def relative(reference,candidate):
    if not all(math.isfinite(x) for x in (reference,candidate)) or reference<=0:
        raise ValueError('Positive finite reference metric required')
    return abs(candidate-reference)/reference


def compare(baseline,candidate,baseline_sha):
    a=baseline['track1500/probe.json'];b=candidate['track1500/probe.json']
    for key in ('start_s','end_s','duration_us','ranks','rays',
                'epsilon_tolerance','phase_temperature_tolerance_K','epsilon_relaxation'):
        if a[key]!=b[key]:raise ValueError('Unmatched pilot control: '+key)
    if b.get('variant')!='track1500LocalCorridorDEM' or b.get('cells')!=1929312:
        raise ValueError('Candidate is not the local 6um corridor pilot')
    for item in (baseline,candidate):
        if item['environment'].get('WM_PROJECT_VERSION') not in ('v2512','2512'):
            raise ValueError('Pilot ran under the wrong OpenFOAM version')
        if not item['solverCheck.json'].get('passed') or not item['pilotReport.json'].get('complete'):
            raise ValueError('Incomplete solver or pilot report')
    for key in ('solver_sha256',):
        if baseline['solverCheck.json'][key]!=candidate['solverCheck.json'][key]:
            raise ValueError('Unmatched solver binary')
    if (baseline['solverCheck.json']['laser_library_check']['laser_library_sha256']
        !=candidate['solverCheck.json']['laser_library_check']['laser_library_sha256']):
        raise ValueError('Unmatched laser library')
    if (baseline['pilotReport.json']['demHandoff']['archiveSha256']
        !=candidate['pilotReport.json']['demHandoff']['archiveSha256']):
        raise ValueError('Unmatched DEM powder')
    hashes_a=baseline['inputHashes.json'];hashes_b=candidate['inputHashes.json']
    changed={name for name in set(hashes_a)|set(hashes_b) if hashes_a.get(name)!=hashes_b.get(name)}
    if changed!={'system/blockMeshDict'}:
        raise ValueError(f'Inputs changed beyond the mesh: {sorted(changed)}')
    ref=baseline['pilotReport.json'];can=candidate['pilotReport.json']
    if not can.get('static_local_corridor_only'):
        raise ValueError('Candidate report lacks local-only scope')
    ga=ref['geometry'];gb=can['geometry']
    metrics={
        'melt_depth_um':(ga['solidus_connected_pool']['depth_from_original_surface_um'],
                         gb['solidus_connected_pool']['depth_from_original_surface_um'],.05),
        'melt_width_um':(ga['solidus_connected_pool']['width_z_um'],
                         gb['solidus_connected_pool']['width_z_um'],.05),
        'liquidus_cells_6um':(ga['liquidus_all_metal']['cells'],
                              gb['liquidus_all_metal']['cells'],.05),
        'peak_temperature_K':(max(ga['temperature_maxima_K'].values()),
                               max(gb['temperature_maxima_K'].values()),.10),
    }
    comparisons={key:dict(reference=refval,candidate=canval,
                          relative_difference=relative(refval,canval),screen_limit=limit)
                 for key,(refval,canval,limit) in metrics.items()}
    geometry_screen=all(x['relative_difference']<=x['screen_limit'] for x in comparisons.values())
    fine=(gb['molten_metal_cells_outside_fine']==0 and
          gb['solidus_connected_pool']['fine_margin_um']>=24)
    linear_not_worse=(candidate['T_linear_cap_count']<=baseline['T_linear_cap_count']
        and candidate['T_linear_above_tolerance_count']<=baseline['T_linear_above_tolerance_count'])
    speedup=ref['solver']['job_wall_s']/can['solver']['job_wall_s']
    return dict(schema=1,baseline_archive_sha256=baseline_sha,
        comparison_scope='Matched 0-50us DEM pilot; candidate fine x ends at 300um',
        input_provenance_match=True,metrics=comparisons,
        deposited_power_W=dict(reference=baseline['depositedPower_W'],
                               candidate=candidate['depositedPower_W']),
        stability=dict(reference_thermal_gate=ref['thermal_gate'],
                       candidate_thermal_gate=can['thermal_gate'],
                       reference_T_linear_cap_count=baseline['T_linear_cap_count'],
                       candidate_T_linear_cap_count=candidate['T_linear_cap_count'],
                       reference_T_linear_above_tolerance_count=baseline['T_linear_above_tolerance_count'],
                       candidate_T_linear_above_tolerance_count=candidate['T_linear_above_tolerance_count'],
                       linear_not_worse=linear_not_worse,
                       candidate_fine_margin_um=gb['solidus_connected_pool']['fine_margin_um'],
                       candidate_molten_cells_outside_fine=gb['molten_metal_cells_outside_fine']),
        cost=dict(reference_cells=a['cells'],candidate_cells=b['cells'],
                  reference_wall_s=ref['solver']['job_wall_s'],
                  candidate_wall_s=can['solver']['job_wall_s'],job_speedup=speedup,
                  reference_pressure_s=ref['solver']['sections']['pressure']['mean_s'],
                  candidate_pressure_s=can['solver']['sections']['pressure']['mean_s']),
        local_50us_screen_pass=geometry_screen and fine and linear_not_worse and can['thermal_gate'] and
            can['solver']['thermal_limit_hits']==0,
        useful_for_moving_window_development=geometry_screen and fine and linear_not_worse and
            can['thermal_gate'] and speedup>=1.2,
        keyhole_depth_validated=False,full_track_ready=False,production_approved=False,
        note='Melt depth is not keyhole depth. Equal liquidus-cell volume is only a 6um-cell proxy. Matching input files do not prove equal represented powder after setFields on different meshes. Far-ahead powder is coarsened; moving refinement and global thermal history remain unimplemented.')


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--dem',type=Path)
    p.add_argument('--candidate',type=Path)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    baseline,sha=load_archive(a.baseline)
    if a.dem:
        result=dict(schema=1,baseline_archive_sha256=sha,
                    dem_archive_sha256=check_baseline(baseline,a.dem),
                    environment=baseline['environment'],preflight_pass=True)
    elif a.candidate:
        result=compare(baseline,load_work(a.candidate),sha)
    else:p.error('Provide --dem for preflight or --candidate for comparison')
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2,allow_nan=False),flush=True)


if __name__=='__main__':main()

