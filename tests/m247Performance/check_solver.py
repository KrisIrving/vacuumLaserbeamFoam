#!/usr/bin/env python3
"""Reject an old or shadowed executable before spending time on phase probes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import re

MARKERS = (b' phaseBlendHalfWidth=', b' phaseOverrideWeight=')

def inspect_laser_library(executable, libbin):
    if not libbin:
        raise ValueError('FOAM_USER_LIBBIN is unset')
    library=(Path(libbin)/'liblaserHeatSource.so').resolve()
    data=library.read_bytes()
    errors=[]
    if b'LASER_PERF_DIAGNOSTICS schema=2 time=' not in data or b'LASER_RANK_DIAGNOSTICS schema=2 time=' not in data:
        errors.append('Old laser library: missing internal profiling marker')
    result=subprocess.run(['ldd',str(Path(executable).resolve())],capture_output=True,text=True,check=True)
    match=re.search(r'liblaserHeatSource\.so\s+=>\s+(\S+)',result.stdout)
    if not match or Path(match[1]).resolve()!=library:
        errors.append('Runtime loader laser library differs from FOAM_USER_LIBBIN target')
    return dict(laser_library=str(library),laser_library_sha256=hashlib.sha256(data).hexdigest(),
                loaded_laser_library=match[1] if match else None,errors=errors,passed=not errors)

def inspect_solver(executable, appbin):
    executable = Path(executable).resolve()
    data = executable.read_bytes()
    expected = (Path(appbin)/'vacuumLaserbeamFoam').resolve() if appbin else None
    missing = [m.decode().strip() for m in MARKERS if m not in data]
    errors = []
    if expected is None:
        errors.append('FOAM_USER_APPBIN is unset; source the intended OpenFOAM environment')
    elif expected != executable:
        errors.append(f'PATH solver differs from build target: {expected}')
    if missing:
        errors.append('Old/incompatible solver; missing compiled diagnostic markers: '+', '.join(missing))
    return dict(solver=str(executable), solver_sha256=hashlib.sha256(data).hexdigest(),
                expected_solver=str(expected) if expected else None,
                missing_markers=missing, errors=errors, passed=not errors,
                note='Static feature check only; collector must also verify runtime mode diagnostics.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--laser-profile', action='store_true')
    args = parser.parse_args()
    executable = shutil.which('vacuumLaserbeamFoam')
    try:
        if not executable:
            raise ValueError('vacuumLaserbeamFoam missing from PATH')
        result = inspect_solver(executable, os.environ.get('FOAM_USER_APPBIN'))
        if args.laser_profile:
            library=inspect_laser_library(executable,os.environ.get('FOAM_USER_LIBBIN'))
            result['laser_library_check']=library
            result['errors'].extend(library['errors'])
            result['passed']=not result['errors']
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        result = dict(passed=False, errors=[str(error)])
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)
    if not result['passed']:
        parser.exit(1, 'Solver/library preflight failed; no CFD started. Rebuild the intended targets and send the build archive.\n')

if __name__ == '__main__':
    main()
