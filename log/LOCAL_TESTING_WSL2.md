# Local testing — Windows 11 + WSL2 + Intel Core i9-14900KF

## Purpose

This document defines the primary local validation environment for the current
vacuumLaserbeamFoam development workflow.

User environment reported on 2026-09-29:
- host OS: Windows 11;
- Linux environment: WSL2;
- CPU: Intel Core i9-14900KF;
- repository should be stored in the WSL2 Linux filesystem (for example
  `~/src/vacuumLaserbeamFoam`), not under `/mnt/c/`, to avoid unnecessary
  filesystem and build-performance penalties.

The exact OpenFOAM distribution/version must be recorded from `foamVersion`
before interpreting a build result.

## Development/testing workflow

ChatGPT prepares small commits and pushes them to GitHub. GitHub CI remains a
secondary compatibility check. The user's WSL2 installation is the primary
environment for production-oriented validation.

For each checkpoint:
1. fetch/checkout the requested branch/commit;
2. record environment information;
3. clean and build with output redirected to a log file;
4. run only the requested regression tests first;
5. send the logs/results back before larger CFD runs.

## Current checkpoint — Phase 4c

Branch:
`dev/vacuum-solver`

Expected head when this guide was written:
`c8f99b8283b44169dbbf9a649bdea5697931acf3`

This checkpoint contains:
- Phase 1 solver bootstrap;
- Phase 2 runtime evaporation-model API;
- Phase 3 chamber-pressure-aware Hertz-Knudsen reference model;
- corrected Wang Knudsen-layer relations;
- Phase 4a sonic Knudsen-layer model;
- Phase 4b transition-state solver;
- Phase 4c `nearVacuumWang` production model.

Phase-5 radiation is intentionally kept on the separate
`feat/vacuum-radiation` branch until the Phase-4c checkpoint is verified
locally.

## First local validation commands

Clone into the Linux filesystem:

```bash
mkdir -p ~/src
cd ~/src
git clone -b dev/vacuum-solver https://github.com/KrisIrving/vacuumLaserbeamFoam.git
cd vacuumLaserbeamFoam
git rev-parse HEAD
```

Record environment:

```bash
{
    date
    uname -a
    lscpu | sed -n '1,35p'
    foamVersion
    which wmake
    which mpirun
    nproc
} | tee log.local-environment.txt
```

First clean build. Use 16 compile jobs initially on the 14900KF; increase later
only after a stable baseline is established:

```bash
./Allclean > log.clean.txt 2>&1 || true
./Allwmake -j 16 > log.build.txt 2>&1
echo "build_exit=$?" | tee -a log.build.txt
tail -n 80 log.build.txt
```

Verify expected programs:

```bash
which laserbeamFoam
which vacuumLaserbeamFoam
which vacuumEvaporationModelTest
which knudsenTransitionTest
```

Run the focused regression sequence:

```bash
./tests/legacyEquivalence/Allrun   > log.test.legacy.txt 2>&1

./tests/hertzKnudsenCurve/Allrun   > log.test.hertz.txt 2>&1

./tests/knudsenLayerSonic/Allrun   > log.test.sonic.txt 2>&1

./tests/knudsenTransition/Allrun   > log.test.transition.txt 2>&1

./tests/nearVacuumWang/Allrun   > log.test.nearVacuumWang.txt 2>&1
```

Summarize:

```bash
for f in log.test.*.txt; do
    echo "===== $f ====="
    tail -n 20 "$f"
done
```

## Pass criteria for the first WSL2 checkpoint

Required:
- build exits with code 0;
- `vacuumLaserbeamFoam` is found in the OpenFOAM user application bin;
- all five focused regression scripts exit with code 0;
- no `FOAM FATAL ERROR`, segmentation fault, NaN, or Inf is reported;
- legacy equivalence remains byte-identical for its selected fields;
- nearVacuumWang constitutive/CFD-coupling regression reports PASS.

Do not run large LPBF cases yet. First establish that the WSL2 compiler/runtime
environment reproduces the tested constitutive chain.

## Files to return after testing

Please return:
- `log.local-environment.txt`;
- `log.build.txt` if the build fails, otherwise its final ~80 lines are enough;
- every failed `log.test.*.txt`;
- for successful tests, the final 20 lines of each test log are sufficient.

## After Phase-4c passes locally

Next checkpoint:
`feat/vacuum-radiation`

At that point test:
- radiation-disabled backward compatibility;
- analytical Stefan-Boltzmann flux;
- radiation-enabled one-step CFD case;
- then integrate Phase 5 into `dev/vacuum-solver`.

Only after Phase 5 is locally accepted should the project move to the numerical
void/pseudo-gas sensitivity study and real bare-plate pressure sweeps.
