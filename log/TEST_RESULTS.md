# Test results

Record only tests that were actually executed.

## 2026-09-28 — Baseline and Phase-1 bootstrap

### Baseline Git-tree verification

Result: **PASS**

The project `main` tree SHA was verified equal to the public LaserbeamFoam
V3.0 tree:

`a37e12fa6d6828e06bbde60831db2de67dab283a`

This verifies repository-content identity.

### Upstream baseline CI

Commit:
`9cfaddf297830129a2ed248e6fd8e9a66a78d8c6`

GitHub Actions run:
`36404163128`

Environment:
`OpenFOAM-v2506` container used by the repository Build workflow.

Result: **PASS**

Observed:
- `Allwmake`: success;
- `Alltest`: success;
- reported attempted laserbeamFoam-related cases: 11;
- solver failures: 0;
- other command failures: 0.

### Phase-1 source-copy equivalence

Result: **PASS (structural check)**

The new `applications/solvers/vacuumLaserbeamFoam` contains 33 source/build
files. Comparing Git blob identities against V3.0 `laserbeamFoam`:

- 30/33 files are byte-identical;
- 3 intentionally differ:
  - `Make/files` — executable/source name;
  - `createFields.H` — diagnostic source-name string only;
  - `vacuumLaserbeamFoam.C` — application identity and descriptive text.

No equation file differs from the V3.0 reference at this stage.

### Phase-1 build

Commit:
`2ad22fb0930127c9d5ba596a72d37340e3af1d8e`

GitHub Actions run:
`36404707004`

Result: **PASS**

Observed:
- `wmake vacuumLaserbeamFoam` executed;
- `vacuumLaserbeamFoam.C` compiled successfully;
- executable linked successfully;
- overall `Allwmake` succeeded.

A non-fatal wmkdepend warning about `alphaEqn.H` was observed. The same warning
is present when building the untouched baseline `laserbeamFoam`, so it is
recorded as inherited behavior rather than a new Phase-1 regression.

### Phase-1 vacuumLaserbeamFoam smoke test

Case:
`tutorials/vacuumLaserbeamFoam/bootstrapPlate2D`

Result: **PASS**

The CI log explicitly shows:
- `blockMesh` executed;
- `setFields` executed;
- `vacuumLaserbeamFoam` executed on the bootstrap case;
- overall `Alltest` completed successfully;
- solver failures: 0;
- other command failures: 0.

Important:
This proves startup/minimal runtime behavior only. It is not a 0.6 Pa physical
validation.

### Phase-1 full numerical equivalence regression

Result: **PENDING**

Still required:
run the same prepared case with `laserbeamFoam` and
`vacuumLaserbeamFoam`, then quantitatively compare fields/integral metrics at
identical output times.

## 2026-09-28 — Phase-2 first CI attempt

Commit:
`f14f15d34290bb033af99a21407a303dca9e7797`

GitHub Actions run:
`36418680113`

Result: **FAIL (build)**

Failure:
`vacuumEvaporationModelNew.C` used an explicit
`dictionaryConstructorTable::iterator` type that is not accepted by the
OpenFOAM-v2506 runtime-selection API in this build environment.

Consequence:
`libvacuumEvaporationModels` was not created, so the later solver link also
failed with `cannot find -lvacuumEvaporationModels`.

Diagnosis:
the linker failure is cascading, not a separate library-order issue.

Fix:
use C++17 `auto` for the runtime-selection table iterator and re-run CI.
