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

## 2026-09-28 — Phase-2 corrected build and regression

### Corrected model API build

Commit:
`ecac408e2da1c40fa5c7848ac8e1bd69a2275f4d`

GitHub Actions run:
`36419254818`

Result: **PASS**

Observed:
- `libvacuumEvaporationModels.so` compiled and linked;
- `vacuumLaserbeamFoam` compiled and linked against the new library;
- repository `Alltest` passed.

### Automated legacy field equivalence

Commit:
`8b1806127c4a6103210e704ac6ca0dc20da7cadb`

GitHub Actions run:
`36419960056`

Result: **PASS**

The regression executed the same prepared Plate2D state with:
1. upstream `laserbeamFoam`;
2. `vacuumLaserbeamFoam` selecting `legacyAnisimov`.

Compared output time:
`1e-05`

The following output files were required to be byte-identical:
- `T`;
- `U`;
- `alpha.metal`;
- `p_rgh`;
- `p`;
- `epsilon1`;
- `Qv`;
- `condition`;
- `meltHistory`.

CI result:
`PASS: legacyAnisimov reproduces laserbeamFoam for fields`

Interpretation:
for this deterministic one-step serial regression case, extracting the V3.0
recoil and evaporation-cooling expressions into the runtime-selectable model
introduces no numerical difference in the compared fields.

This is a regression result, not validation of the physical accuracy of the
legacy Anisimov-style evaporation model.

## 2026-09-28 — Phase-3 first CI attempt

Commit:
`281d10c24f583785401d9e8df0f45022148f07dd`

GitHub Actions run:
`36425725491`

Result: **FAIL (build)**

Failure:
`vacuumEvaporationModelNew.C` used the templated form
`lookup<word>()`, which is not accepted by the OpenFOAM-v2506 dictionary API
in this build.

Consequence:
`libvacuumEvaporationModels` was not produced, and the later
`vacuumLaserbeamFoam` link failure (`cannot find -lvacuumEvaporationModels`)
was cascading rather than a separate linker issue.

Fix:
use the established OpenFOAM dictionary-stream conversion
`word(modelDict.lookup("evaporationModel"))` and rerun CI.

## 2026-09-28 — Phase-3 analytical utility first CI attempt

Commit:
`3fa842ffe8496a14375c19f570967348fc4706ef`

GitHub Actions run:
`36427391669`

Result: **FAIL (build)**

Failure:
the new `vacuumEvaporationModelTest` utility included `fvCFD.H` but its
`Make/options` did not include/link `meshTools`. Compilation therefore
stopped at the indirect AMI header dependency
`cyclicAMIPolyPatch.H: No such file or directory`.

Fix:
add `$(LIB_SRC)/meshTools/lnInclude` and `-lmeshTools`.

This failure is isolated to the diagnostic test utility and does not change the
evaporation-model implementation.

## 2026-09-28 — Phase-3 analytical utility second CI attempt

Commit:
`5d6eaac12787466a434feb75616d285e6661c758`

GitHub Actions run:
`36428017249`

Result: **FAIL (build)**

Failure:
the diagnostic utility attempted `Info.precision(16)`; OpenFOAM-v2506
`Info` is a `messageStream` and does not expose that method.

Fix:
print the machine-readable regression line with standard C++
`std::cout << std::setprecision(16)`.

The failure affects only diagnostic formatting; model equations and solver
coupling are unchanged.

## 2026-09-28 — Phase-3 analytical curve regression third attempt

Commit:
`abc749ca644165e980234263d98520c723517494`

GitHub Actions run:
`36428475347`

Result: **FAIL (test input format)**

Passed before the failure:
- `Allwmake`;
- repository `Alltest`;
- legacy byte-level field regression;
- Hertz-Knudsen 0.6 Pa solver smoke test.

Failure:
`tests/hertzKnudsenCurve/vacuumProperties` had an incomplete OpenFOAM header
comment, so `vacuumEvaporationModelTest` aborted while reading the dictionary
before any analytical comparison was performed.

This is a test-fixture formatting error, not a model-equation failure.

Fix:
replace the test dictionary header with a valid OpenFOAM `FoamFile` header and
rerun the full CI gate.

## 2026-09-29 — Phase-3 final CI

Commit:
`be98459e3c00a058d53fa6b08e963afa7dc2ba7e`

GitHub Actions run:
`36512859745`

Result: **PASS**

Passed gates:
- `Allwmake`;
- repository `Alltest`;
- legacy Anisimov byte-level field regression;
- Hertz-Knudsen 0.6 Pa solver smoke test;
- Hertz-Knudsen analytical pressure/temperature curve regression.

The analytical curve regression independently reconstructs the implemented
Clausius-Clapeyron saturation pressure, Hertz-Knudsen net mass flux, reference
recoil closure, and evaporative heat flux at multiple temperature/back-pressure
conditions.

Interpretation:
Phase 3 provides a tested pressure-aware reference model and an explicit
`vacuumProperties` configuration split. The Hertz-Knudsen recoil closure remains
an intermediate reference model; it is not the final near-vacuum Knudsen-layer
model for the 0.6 Pa experiment.

## 2026-09-29 — Phase-4a first CI attempt

Commit:
`a9cd4aa495029063b8d6488384ed6257ecf11b89`

GitHub Actions run:
`36513971338`, attempt 1

Result: **FAIL (new analytical regression only)**

Passed:
- `Allwmake`;
- repository `Alltest`;
- legacy byte-level regression;
- Hertz-Knudsen smoke regression;
- Hertz-Knudsen analytical curve regression.

The new sonic test failed with exit code 13 (mass-flux comparison). Artifact
inspection showed that the production model reported:

- `gamma = 1.66667`;
- `massFluxRatio = 0.8289634046`;

instead of the exact `gamma = 5/3` reference value used to construct the
independent expected coefficient.

Diagnosis:
the test script used `foamDictionary` to change temperature/pressure, which
rewrote the dictionary and rounded the configurable gamma value. The discrepancy
was caused by configuration serialization, not the Knudsen-layer equations.

Resolution:
`knudsenLayerSonic` now fixes `gamma = 5/3` in code, consistent with the
monatomic-vapour assumption of the source model. Gamma is no longer a tunable
dictionary coefficient.

## 2026-09-29 — Phase-4a sonic Knudsen-layer final CI

Commit:
`5520d829e06bf66309dd76a50848659c75be7840`

GitHub Actions run:
`36514885821`

Result: **PASS**

Passed gates:
- `Allwmake`;
- repository `Alltest`;
- legacy Anisimov byte-level field regression;
- Hertz-Knudsen 0.6 Pa smoke regression;
- Hertz-Knudsen analytical curve regression;
- sonic Knudsen-layer analytical regression;
- sonic Knudsen-layer one-step CFD coupling.

The sonic regression explicitly passed:
- reference temperature, `chamberPressure=0.6 Pa`;
- lower surface temperature, `chamberPressure=0.6 Pa`;
- high back-pressure limit for chamber-relative recoil;
- finite `Qv` in the coupled solver run.

Interpretation:
the strong-evaporation `Ma=1` branch is now implemented and regression-tested.
This does not yet validate the complete near-vacuum interpolation procedure or
the final Ti-6Al-4V material dataset.

## 2026-09-29 — Phase-4 equation transcription audit

Status: **CORRECTION IN PROGRESS**

Before coupling the transition solver into a production near-vacuum model, the
Wang et al. Eq. (9)-(13) source was rechecked against the published equation
layout and an independent kinetic-theory formulation.

Finding:
the first Phase-4a implementation parsed the square-root placement in Eq. (10)
incorrectly and consequently used an incorrect normalized mass-flux expression.
The earlier Phase-4a PASS therefore verified implementation consistency with the
then-coded constants, not correctness of that equation transcription.

Correct sonic reference values for gamma=5/3, Ma=1 are now:
- T3/Te = 0.6691164507;
- P3/Pe = 0.2061848244;
- Hertz-normalized mass flux = 0.8156806362;
- absolute recoil coefficient = 0.5498261984.

The production sonic model, generic transition relations, and independent
regression references are being corrected in the same commit. A new full CI
result is required before Phase 4c proceeds.

## 2026-09-29 — Phase-4c near-vacuum production model CI

Commit:
`90cdcc9799300054d1bb6ab962d74e2c8f272cfa`

GitHub Actions run:
`36519951799`

Result: **PASS**

Passed gates:
- `Allwmake`;
- repository `Alltest`;
- legacy Anisimov byte-level field regression;
- Hertz-Knudsen smoke regression;
- Hertz-Knudsen analytical curve regression;
- corrected sonic Knudsen-layer regression;
- corrected transition-relation regression;
- new `nearVacuumWang` constitutive and CFD-coupling regression.

The new regression covered:
1. the 0.6 Pa strong-evaporation branch reducing to the corrected sonic
   Knudsen-layer state;
2. a synthetic subsonic transition state;
3. zero liquid-evaporation source below liquidus;
4. one-step coupled `vacuumLaserbeamFoam` execution with finite `Qv`.

Interpretation:
the Phase-4c implementation is numerically regression-tested for the selected
single-component Wang near-vacuum closure. This is **not** yet validation
against Ti-6Al-4V material data or the user's 0.6 Pa experiment.

## 2026-09-30 — OpenFOAM-v2512 Ubuntu fast-track checkpoint

Commit tested:
`d64af0eaa77184991da3b0ae40008cdab0b9f787`

Machine:
- Ubuntu 22.04;
- dual-socket / 48-core workstation;
- OpenFOAM `v2512`;
- GCC/G++ `11.4.0`.

Result: **PASS**

Build:
- repository `./Allwmake` completed successfully;
- the build log ended with
  `There were no build errors: enjoy laserbeamFoam!`;
- `libvacuumEvaporationModels.so`, `vacuumLaserbeamFoam`,
  `knudsenTransitionTest`, and `vacuumEvaporationModelTest` all compiled
  and linked under OpenFOAM-v2512.

Focused regression results:
- `tests/knudsenLayerSonic/Allrun`: PASS;
- `tests/knudsenTransition/Allrun`: PASS;
- `tests/nearVacuumWang/Allrun`: PASS;
- `tests/wangAlloyMixture/Allrun`: PASS;
- `tests/legacyEquivalence/Allrun`: PASS.

Observed sonic constitutive reference values at `T=3000 K`,
`chamberPressure=0.6 Pa`:
- `pSat = 84212.46708506653 Pa`;
- `mDot = 38.79948612505068 kg m^-2 s^-1`;
- net recoil `= 46301.62063810318 Pa`;
- evaporation heat flux `= 23279691.67503041 W m^-2`.

Transition solver round trips recovered:
- `Ma=0.05`, `T=3000 K`, `M2=1.109778263033771`;
- `Ma≈0.5`, `T=3000 K`, `M2=2.334163368386289`;
- `Ma=1`, `T=3000 K`, `M2=3.717937692983043`.

The multi-component Wang Eqs. (18)-(20) regression passed at both
`2500 K` and `3000 K`.

The legacy-equivalence gate also remained byte-identical at output time
`1e-05` for:
`T`, `U`, `alpha.metal`, `p_rgh`, `p`, `epsilon1`, `Qv`,
`condition`, and `meltHistory`.

Interpretation:
the fast-track Wang implementation is now confirmed on the project's primary
OpenFOAM-v2512 Ubuntu workstation, not only on the repository's v2506 CI
container. This clears the constitutive/build checkpoint for the 304L
near-vacuum validation case.

## 2026-09-30 — 304L OpenFOAM-v2512 local checkpoint

Primary machine:
- Ubuntu 22.04;
- OpenFOAM v2512;
- GCC/G++ 11.4.0;
- 48-core workstation.

Uploaded local logs confirm:

### Build after 304L production changes

Result: **PASS**

`./Allwmake -j 16` rebuilt:
- `libvacuumEvaporationModels.so`;
- `vacuumLaserbeamFoam`;
- `knudsenTransitionTest`;
- `vacuumEvaporationModelTest`.

The inherited non-fatal `wmkdepend: could not open alphaEqn.H` warning was
observed again. The build completed with:

`There were no build errors: enjoy laserbeamFoam!`

### Wang 304L constitutive reference

Script:
`tests/wang304LReference/Allrun`

Result: **PASS**

Observed:
`PASS: Wang 304L Table-I/II anchored constitutive reference`

This clears the anchored 304L multicomponent constitutive checkpoint on the
target OpenFOAM-v2512 environment, including the Wang low-Mach step-(4) path.

### Wang 304L one-step CFD case smoke

Script:
`tests/wang304LCaseSmoke/Allrun`

Result: **PASS**

Observed:
`PASS: Wang 304L 8-um one-step CFD case smoke`

This confirms the 304L case can pass mesh setup and one full
`vacuumLaserbeamFoam` coupled time step on OpenFOAM-v2512.

Next gate:
run the 8 um, 16-rank, 5 us local smoke and inspect thermal/recoil/evaporation
diagnostics before committing compute time to the 4 um paper-reference run.

## 2026-09-30 — 304L 8 um / 5 us local thermal smoke

Machine:
- Ubuntu workstation;
- OpenFOAM v2512;
- 48 MPI ranks.

Result: **PASS for the pre-activation thermal/stability checkpoint**

The run reached `5e-6 s` and finalised normally.

Output-time diagnostics:

| time (us) | Tmax (K) | Umax (m/s) | pVapMax (Pa) | QvMax (W/m2) | deposited power (W) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 769.275 | 4.47e-8 | 0 | 0 | 72.6109 |
| 2 | 1207.750 | 5.17e-8 | 0 | 0 | 72.6109 |
| 3 | 1617.725 | 4.63e-8 | 0 | 0 | 72.6109 |
| 4 | 1720.647 | 9.75e-8 | 0 | 0 | 72.6109 |
| 5 | 1980.192 | 9.48e-2 | 0 | 0 | 72.6109 |

Additional observations:
- the run used 48 MPI ranks;
- the final maximum Courant number was below 5e-4;
- alpha.metal remained bounded to numerical roundoff;
- deposited power remained stable at 72.6109 W, about 27.9% of the 260 W
  incident beam in the initial flat-surface optical state;
- Tmax exceeded the 1727 K liquidus;
- the production model's 304L activation temperature is 2009.50 K, so the
  zero recoil and zero evaporation heat flux at 5 us are expected rather than
  a coupling failure.

Next gate:
extend the same 8 um case to 10 us and require finite non-zero pVap/Qv after
the activation threshold is crossed, while retaining stable alpha, pressure,
and Courant behaviour.

## 2026-09-30 — 304L 8 um / 10 us evaporation-activation smoke

Machine:
- Ubuntu workstation;
- OpenFOAM v2512;
- 48 MPI ranks.

Result: **PASS**

The local run reached the 10 us target and ended normally.

Output-time diagnostics show the evaporation/recoil closure activating between
5 and 6 us:

| time (us) | Tmax (K) | Umax (m/s) | pVapMax (Pa) | QvMax (W/m2) | deposited power (W) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 5 | 1980.192 | 0.0948 | 0 | 0 | 72.6109 |
| 6 | 2287.109 | 0.7602 | 99.78 | 7.994e5 | 72.6109 |
| 7 | 2590.888 | 1.5113 | 947.31 | 7.021e6 | 72.6108 |
| 8 | 2899.477 | 2.1012 | 5549.37 | 3.692e7 | 72.6107 |
| 9 | 3220.584 | 2.8365 | 23960.69 | 1.476e8 | 72.6106 |
| 10 | 3571.579 | 4.3331 | 86870.39 | 5.026e8 | 72.6116 |

At the 10 us target:
- maximum Courant number remained about 0.025;
- alpha.metal remained bounded to roundoff;
- the solver wrote `End` and finalised the parallel run;
- deposited optical power remained essentially constant while recoil pressure,
  evaporation cooling, and melt velocity increased smoothly after activation.

Interpretation:
this clears the 8 um short-time activation/stability gate. The next physical
validation stage is the 4 um reference-resolution Wang 304L case.

