#!/usr/bin/env python3
"""Run one prepared probe, with a wall-time stop that requests a checkpoint."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time
from check_solver import inspect_solver, inspect_laser_library

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', type=Path, required=True)
    parser.add_argument('--wall-hours', type=float, default=2)
    parser.add_argument('--stop-grace-seconds', type=float, default=180)
    args = parser.parse_args()
    if not math.isfinite(args.wall_hours) or args.wall_hours <= 0 or not math.isfinite(args.stop_grace_seconds) or args.stop_grace_seconds <= 0:
        parser.error('Wall limit and stop grace must be finite and positive')
    case = args.case.resolve()
    metadata = json.loads((case/'probe.json').read_text())
    log = case/'log.vacuumLaserbeamFoam'
    if log.exists():
        parser.error('Probe already has a solver log; prepare a fresh directory')
    if os.name != 'posix':
        parser.error('Run this on the Ubuntu OpenFOAM host')
    for command in ('mpirun', 'vacuumLaserbeamFoam', 'foamDictionary'):
        if not shutil.which(command):
            parser.error(f'{command} missing; source OpenFOAM and rebuild first')
    executable = Path(shutil.which('vacuumLaserbeamFoam')).resolve()
    if metadata.get('variant') in ('phaseBlendNarrow', 'phaseBlendWide'):
        check = inspect_solver(executable, os.environ.get('FOAM_USER_APPBIN'))
        (case/'solverCheck.json').write_text(json.dumps(check, indent=2)+'\n')
        if not check['passed']:
            parser.error('; '.join(check['errors']))
    if metadata.get('variant') in ('laserProfileOff','laserProfileOn'):
        check=inspect_laser_library(executable,os.environ.get('FOAM_USER_LIBBIN'))
        (case/'solverCheck.json').write_text(json.dumps(check,indent=2)+'\n')
        if not check['passed']: parser.error('; '.join(check['errors']))
    provenance = dict(solver=str(executable), solver_sha256=hashlib.sha256(executable.read_bytes()).hexdigest())
    library = Path(os.environ.get('FOAM_USER_LIBBIN', '/nonexistent'))/'liblaserHeatSource.so'
    if library.is_file():
        provenance['laser_library_sha256'] = hashlib.sha256(library.read_bytes()).hexdigest()
    command = ['mpirun', '-np', str(metadata['ranks']), str(executable), '-parallel']
    started = time.monotonic()
    stopped = None
    forced = False
    with log.open('x') as stream:
        process = subprocess.Popen(command, cwd=case, stdout=stream,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while process.poll() is None:
                elapsed = time.monotonic()-started
                if stopped is None and elapsed >= args.wall_hours*3600:
                    subprocess.run(['foamDictionary', 'system/controlDict', '-entry', 'stopAt', '-set', 'writeNow'],
                                   cwd=case, check=True, stdout=subprocess.DEVNULL)
                    stopped = time.monotonic()
                    print('Wall budget reached: requested writeNow; awaiting checkpoint.', flush=True)
                if stopped is not None and time.monotonic()-stopped >= args.stop_grace_seconds:
                    os.killpg(process.pid, signal.SIGTERM)
                    forced = True
                    try:
                        process.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                    break
                time.sleep(1)
        except BaseException:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
            raise
        process.wait()
    result = dict(provenance, command=command, elapsed_wall_s=time.monotonic()-started,
                  returncode=process.returncode, wall_budget_stop=stopped is not None,
                  forced_stop=forced, wall_budget_hours=args.wall_hours)
    (case/'run.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))
    if process.returncode != 0 or stopped is not None:
        parser.exit(1, 'Probe did not complete its requested interval; inspect log and saved times.\n')

if __name__ == '__main__':
    main()
