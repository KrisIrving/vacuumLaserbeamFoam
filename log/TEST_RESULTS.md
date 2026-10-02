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

## 2026-09-30 — 4 um reference interrupted at Wang boiling endpoint

The first 4 um / 48-rank reference attempt advanced to approximately
`54.0337 us` before stopping with:

`Could not solve the Wang transition state at T=2009.503556 K`

The failure occurred essentially at the 304L chamber-pressure boiling
activation temperature. This identified a numerical endpoint defect in the
step-(4) Mach solve: the implementation bracketed the low-Mach branch from
`Ma=1e-8` instead of admitting the regular `Ma=0` limit.

Fix implemented:
- permit `Ma=0` in the Knudsen jump relations;
- use `MaMin=0` for the subcritical common-atmosphere branch;
- add a constitutive regression at `T=2009.503556 K`;
- make the reference control dictionary restart from `latestTime`;
- add `Resume_background` so the existing decomposed checkpoint can continue;
- make `Status` report FOAM/MPI fatal exits explicitly.

This fix is **pending local rebuild/regression/restart confirmation** and is not
yet marked as a completed reference validation.

## 2026-09-30 — 4 um Wang 304L reference reached 120 us

Result: **numerically complete to 120 us; physical validation interval incomplete**

The restarted 4 um / 48-rank case reached 120 us and ended normally.

Measured centerline keyhole depth:
- first 32 um crossing: approximately 36.07 us;
- depth at 120 us: 127.78 um;
- 136 um target not yet reached.

The Wang paper compares the 32-to-136 um growth interval. Therefore the
reference endpoint is extended to 140 us so that the actual t136 can be
measured instead of extrapolated.

Solver diagnostics at 120 us:
- Tmax = 5696.03 K;
- Umax = 51.70 m/s;
- global pVapMax = 7.91 MPa;
- global QvMax = 3.18e10 W/m2;
- deposited laser power = 210.42 W.

The global pVapMax is not yet treated as directly comparable to the paper's
keyhole-surface recoil maximum because pVap is evaluated throughout the field
whereas its momentum contribution is localized by the VOF interface gradient.
A dedicated interface-recoil diagnostic is required before making that
comparison.

## 2026-10-01 — 140 us Wang 304L keyhole-depth checkpoint

The 4 um / 48-rank reference reached 140 us and ended normally.

Current centreline alpha=0.5 metric:
- depth at 140 us: 147.52 um;
- interpolated t32: 36.07 us;
- interpolated t136: 130.13 us;
- 32-to-136 um growth interval: 94.06 us.

The same interval obtained by using the first saved output time at or above each
threshold is 38-to-132 us = 94 us, so the interval is not an artefact of linear
time interpolation.

However, this remains a **provisional centreline metric**. The Wang paper
describes keyhole depth below the substrate surface but does not prescribe a
centreline-alpha extraction algorithm. A single x=z=0 line can underestimate
the geometric depth if the keyhole bottom bends or shifts laterally, and it can
become ambiguous after bridge closure or multiple alpha=0.5 crossings.

The post-processing workflow therefore now provides two independent metrics:
1. atmosphere-connected centreline crossing, with crossing-count diagnostics;
2. deepest point on the connected 3-D alpha.metal=0.5 main free-surface
   component, excluding disconnected pore/droplet components.

The 3-D surface metric must be checked before treating the 94 us interval as
the formal Wang-validation depth result.

## 2026-10-01 — 140 us dual-metric keyhole-depth validation

The 4 um Wang 304L reference was post-processed with two independent metrics:

1. centreline atmosphere-connected `alpha.metal=0.5` crossing;
2. deepest point on the surface-connected 3-D `alpha.metal=0.5` main interface component.

Measured results:

| Metric | t32 (us) | t136 (us) | 32-to-136 us interval | depth at 140 us |
| --- | ---: | ---: | ---: | ---: |
| Centreline | 36.0676 | 130.126 | 94.0584 us | 147.522 um |
| 3-D connected surface | 33.4462 | 127.328 | 93.8816 us | 147.370 um |

Agreement between the two growth-time metrics is 0.1768 us, about 0.19%.
Across all 71 saved times, the median 3-D-minus-centreline depth is 0.667 um
and the maximum absolute difference is 3.675 um, less than one 4 um mesh cell.

After the 3-D metric first reaches 32 um:
- mean absolute depth difference between metrics is about 1.00 um;
- median bottom lateral offset from the laser axis is 8.0 um;
- maximum bottom lateral offset is 14.42 um;
- bottom support is 11 to 24 nearby interface vertices (median 18);
- the selected main interface is always identified as surface connected.

The full interface contains 2 connected components at many late times and 3
components at 84 us. The depth extractor deliberately selects the broad
surface-connected main component, so disconnected pores/droplets are excluded
from the formal keyhole depth.

Conclusion:
the approximately 94 us 32-to-136 um growth interval is robust to the depth
definition and is not a centreline post-processing artefact. The formal
validation metric should use the 3-D connected-surface result:
**93.88 us**.

For comparison, Wang et al. report about 70 us in the near-vacuum x-ray
experiment and 75 us for their current evaporation model. Therefore the
current vacuumLaserbeamFoam case is about 34% slower than the experiment and
25% slower than the Wang-model result over the same nominal depth interval.

This is a multiphysics validation discrepancy, not a constitutive-regression
failure. The next investigation should prioritize the remaining model
differences (optical absorption/ray interaction and surface heat-loss closure)
and add interface-local recoil diagnostics before altering the Wang
evaporation equations.

## 2026-10-01 — Wang matched-physics precheck

Local primary-machine results reported from the 48-core Ubuntu/OpenFOAM-v2512
workstation:

### Radiation analytical regression

Command:
`./tests/vacuumRadiation/Allrun`

Result: **PASS**

Reported states:
- 2000 K, solid emissivity 0.4: Qrad = 362720.2426848244 W/m2;
- 2000 K, liquid emissivity 0.1: Qrad = 90680.06067120608 W/m2;
- 1200 K, liquid fraction 0.5, emissivity 0.25:
  Qrad = 29280.39590611125 W/m2.

The standalone radiation model and its solid/liquid interpolation therefore
match the analytical regression.

### Wang 304L constitutive reference

Command:
`./tests/wang304LReference/Allrun`

Result: **PASS**

The anchored Cr/Ni/Fe near-vacuum constitutive reference remains intact after
the optical/radiation changes.

### 48-rank matched-physics smoke

Command:
`./tests/wang304LMatchedSmoke/Allrun`

The script launched blockMesh, setFields, decomposePar and
`vacuumLaserbeamFoam (48 processes)`. After the solver command returned, the
post-run shell checker failed to parse because the generated test script had a
malformed quoted `grep '^End$'` line, causing the following awk block to be
parsed as shell syntax.

This is a **test-harness failure**, not evidence of a CFD failure. The existing
run output is intentionally preserved and should be checked with the new
`tests/wang304LMatchedSmoke/Check` helper before rerunning the CFD.

Matched-physics smoke status: **pending post-check of the already completed
run output**.

## 2026-10-01 — Wang matched-physics 8 um / 10 us smoke

Result: **PASS** on the primary 48-core OpenFOAM-v2512 workstation.

Selected optics:
- opticalModel = fixedComplexIndex;
- n = 2.961346154;
- k = 4.013269231;
- reported normal absorptivity = 0.3725128503.

At 1 us:
- Tmax = 925.90 K;
- depositedPower = 97.1236 W;
- recoil/evaporation inactive;
- radiationPower = 1.74e-5 W.

The 1-us deposited power agrees closely with the flat-surface Fresnel expectation
260 W * 0.37251285 = approximately 96.85 W, supporting correct activation of
the fixed-complex-index optical path.

At 10 us:
- Tmax = 4322.50 K;
- Umax = 16.98 m/s;
- pVapMax = interfacePVapMax = 838550.9 Pa;
- QvMax = 3.5072e9 W/m2;
- depositedPower = 100.655 W;
- evaporationPower = 1.20784 W;
- radiationPower = 0.007856 W;
- interfaceArea = 1.02679e-7 m2;
- recoilForceY = -2.22140e-4 N.

Compared with the earlier Drude 10-us smoke (about 72.61 W deposited,
3571.6 K Tmax, 4.33 m/s Umax and 86.9 kPa pVapMax), the Wang-matched optical
closure produces substantially stronger heating, flow and recoil at the same
time.

Radiative loss is negligible relative to absorbed laser power and evaporation
loss at 10 us; it is retained for paper consistency but is not expected to be
the mechanism that closes the faster-keyhole discrepancy.

Gate T9c is accepted. Proceed to an independent 4 um / 140 us matched-physics
reference from t=0 and compare the same connected-3D 32-to-136 um metric.

## 2026-10-02 — 4 um Wang matched-physics reference completed

Result: **keyhole-growth validation aligned with Wang current model**

The independent 4 um / 48-rank / 140 us matched-physics reference completed
normally with no reported Fatal/NaN/Inf.

Formal connected-3D alpha.metal=0.5 metric:
- t32 = 25.7344 us;
- t136 = 101.966 us;
- 32-to-136 um growth interval = 76.2318 us;
- depth at 140 us = 183.433 um.

Centreline cross-check:
- t32 = 26.1044 us;
- t136 = 102.121 us;
- interval = 76.0169 us;
- depth at 140 us = 183.545 um.

The two independent depth metrics differ by only 0.2149 us in growth time.
Across the time series the median 3-D-minus-centreline depth difference is
0.775 um. After t32 the selected 3-D main surface remains surface-connected,
the bottom-support count stays 11-24 vertices, and the maximum bottom lateral
offset is 11.31 um.

Compared with the first Drude-optics baseline:
- baseline 3-D interval = 93.8816 us;
- matched 3-D interval = 76.2318 us;
- reduction = 17.6498 us = 18.8%.

Wang et al. report about 75 us for the current evaporation model and 70 us for
the x-ray experiment over the same nominal 32-to-136 um interval. The matched
case is therefore about 1.64% slower than Wang's simulation and 8.90% slower
than the experiment.

During the formal t32-to-t136 window:
- mean deposited power = 212.96 W (81.9% of 260 W);
- deposited-power range = 183.42-237.77 W;
- mean evaporation loss = 7.76 W;
- mean radiation loss = 0.0737 W;
- maximum Tmax = 5866.9 K;
- maximum Umax = 73.77 m/s.

At the nearest saved state to t136 (102 us):
- interfacePVapMax (cell-based diagnostic) = 4.294 MPa;
- recoilForceY (whole-interface volume-CSF diagnostic) = -1.326e-3 N.

These recoil quantities are **not yet accepted as direct Fig. 10/11
comparisons**. The paper reports recoil on the reconstructed keyhole surface,
whereas the current maximum is a mixed-cell value and the current force
integrates the complete free surface. A dedicated alpha=0.5 keyhole-surface
pressure/force post-process is required before changing evaporation physics.

Conclusion:
the prior 25% growth-rate discrepancy was primarily caused by the inherited
optical closure. The Fe fixed-complex-index Fresnel path closes the keyhole
growth discrepancy without fitting the Wang evaporation constitutive model.
