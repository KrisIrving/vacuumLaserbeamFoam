#!/usr/bin/env python3
"""Reject an old or shadowed executable before spending time on phase probes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil

MARKERS = (b' phaseBlendHalfWidth=', b' phaseOverrideWeight=')

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
    args = parser.parse_args()
    executable = shutil.which('vacuumLaserbeamFoam')
    try:
        if not executable:
            raise ValueError('vacuumLaserbeamFoam missing from PATH')
        result = inspect_solver(executable, os.environ.get('FOAM_USER_APPBIN'))
    except (ValueError, OSError) as error:
        result = dict(passed=False, errors=[str(error)])
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)
    if not result['passed']:
        parser.exit(1, 'Solver preflight failed; no CFD started. Run BuildPhaseBlend and send its archive.\n')

if __name__ == '__main__':
    main()
