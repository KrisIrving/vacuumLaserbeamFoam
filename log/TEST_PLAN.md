# Test plan

## T0 — Repository build

Command:
`./Allwmake -j`

Acceptance:
- original LaserbeamFoam applications compile;
- new `vacuumLaserbeamFoam` executable compiles;
- no new compiler error from the copied solver.

## T1 — Original upstream regression

Run at least one existing V3.0 `laserbeamFoam` tutorial unchanged.

Record:
- OpenFOAM version;
- git commit;
- command;
- exit status;
- execution time;
- final continuity error;
- min/max T;
- integrated laser deposition if present.

Acceptance:
- original solver behavior remains unchanged.

## T1b — vacuumLaserbeamFoam smoke test

Case:
`tutorials/vacuumLaserbeamFoam/bootstrapPlate2D`

Purpose:
- ensure the new executable is discoverable;
- initialize all copied fields/models;
- advance the baseline equations without a fatal runtime error.

This is not a 0.6 Pa validation case.

Acceptance:
- CI/tutorial smoke run completes without a solver error.

## T2 — Phase-1 executable equivalence

Use the same prepared case twice:
1. run with `laserbeamFoam`;
2. reset the case;
3. run with `vacuumLaserbeamFoam`.

Recommended first case: a small plate case before LPBF_small, then LPBF_small.

Compare at identical output times:
- `alpha.metal`;
- `T`;
- `U`;
- `p_rgh`;
- `epsilon1`;
- `Qv` where written;
- melt-history fields.

Acceptance:
- results are identical or within a documented floating-point/MPI tolerance.
- no intentional physical difference is allowed in Phase 1.

## T3 — Serial/parallel consistency

After T2:
- run a selected regression case in serial and MPI;
- compare integral and geometric metrics.

Acceptance criteria will be set after the first measured baseline.

## T4 — Evaporation-model unit/curve tests (future)

Before full CFD coupling, sample temperature and pressure ranges and compare:
- `pSat(T)`;
- `mDot(T,pChamber)`;
- `pRecoil(T,pChamber)`;
- `qEvap(T,pChamber)`.

Include limiting cases and dimensional checks.

## T5 — Energy balance (future)

For controlled cases evaluate:
- incident laser power;
- absorbed laser power;
- sensible energy change;
- fusion latent heat;
- radiation;
- evaporation heat loss;
- boundary conduction/fluxes.

## T6 — Pressure sweep (future)

Run identical bare-plate cases while varying only chamber pressure/model input.
Check for stable and physically interpretable trends down to 0.6 Pa.

## T7 — Mesh/time-step sensitivity (future)

At minimum three spatial resolutions and multiple time-step/Courant settings for
the selected validation case.

## Result-recording rule

A planned test belongs here. A measured result belongs in `TEST_RESULTS.md`.
Never mark a test passed based only on code inspection.

## T2b — Legacy evaporation-model API regression

After Phase-2 integration:
- build `libvacuumEvaporationModels` and `vacuumLaserbeamFoam`;
- confirm log reports `Selecting vacuum evaporation model legacyAnisimov`;
- run bootstrapPlate2D successfully;
- compare Phase-2 `vacuumLaserbeamFoam` against the pre-API Phase-1 solver on
  the same case/fields before accepting physical equivalence.

Acceptance:
- no build/runtime failure;
- legacy model selection is explicit in the test case;
- no intentional equation change beyond moving the formulas into the model.

## T2c — Automated byte-level legacy field equivalence

Script:
`tests/legacyEquivalence/Allrun`

Method:
- copy the same bootstrap Plate2D case into two clean directories;
- force both cases to write after the first time step;
- run one with upstream `laserbeamFoam`;
- run one with `vacuumLaserbeamFoam + legacyAnisimov`;
- require the runtime-selection message;
- byte-compare key OpenFOAM field files at the same output time.

Fields:
- `T`;
- `U`;
- `alpha.metal`;
- `p_rgh`;
- `p`;
- `epsilon1`;
- `Qv`;
- `condition`;
- `meltHistory`.

Acceptance:
all listed field files are byte-identical for this deterministic serial
regression case.

## T4a — Hertz-Knudsen pressure-aware model smoke test

Script:
`tests/hertzKnudsenReference/Allrun`

Checks:
- explicit selection of `hertzKnudsen` from `vacuumProperties`;
- explicit chamber-pressure configuration;
- one-step solver execution;
- `Qv` output exists and contains no NaN/Inf.

This is a runtime/limit sanity test, not physical validation.

## T4b — Pressure/temperature curve verification

Planned next:
sample prescribed temperatures and chamber pressures and compare
`pSat`, `mDot`, `pRecoil`, and `qEvap` against independently evaluated
reference equations. This test should be in place before Phase 4 changes the
production recoil closure.

## T4c — Hertz-Knudsen analytical curve regression

Utility:
`vacuumEvaporationModelTest`

Script:
`tests/hertzKnudsenCurve/Allrun`

The utility evaluates the actual C++ runtime-selected evaporation model on a
uniform prescribed temperature field without advancing the melt-pool solver.

The test independently evaluates the reference equations using `awk` and
compares:
- saturation pressure;
- net evaporation mass flux;
- recoil reference pressure;
- evaporative heat flux.

Cases:
1. reference temperature, 0.6 Pa chamber pressure;
2. lower surface temperature, 0.6 Pa chamber pressure;
3. back pressure greater than saturation pressure, which must suppress net
   evaporation/recoil to zero.

Acceptance:
relative error <= 1e-9 for the analytical quantities, with the zero-flux limit
also enforced.

## T4d — Sonic Knudsen-layer analytical regression

Script:
`tests/knudsenLayerSonic/Allrun`

Model:
`knudsenLayerSonic`

Checks:
- saturation pressure from Clausius-Clapeyron;
- sonic Knudsen-layer mass-flux coefficient;
- sonic recoil-pressure coefficient;
- chamber-relative recoil limit;
- evaporative heat flux;
- one-step CFD coupling at `chamberPressure = 0.6 Pa`;
- finite `Qv` field and runtime model selection.

Independent reference constants for `gamma=5/3, Ma=1`:
- `T3/Te = 0.6691164507`;
- `P3/Pe = 0.2061848244`;
- Hertz-normalized mass flux = `0.8156806362`;
- absolute recoil coefficient = `0.5498261984`.

Acceptance:
analytical quantities agree within the scripted floating-point tolerance and the
one-step CFD coupling run completes without NaN/Inf.

## T4e — Eq. (16)-(17) transition-state solver regression

Utility:
`knudsenTransitionTest`

Script:
`tests/knudsenTransition/Allrun`

Reference states are independently precomputed for the Phase-3 synthetic
single-component thermodynamic parameters at `Te=3000 K`, `T1=300 K`.

The test checks three known states:
- `Ma=0.05`;
- `Ma=0.5`;
- `Ma=1.0`.

For each state it verifies:
- recovery of Ma from Eq. (16)-(17);
- recovery of the known 3000 K threshold temperature;
- the physical region-II shock Mach number `M2>1`;
- successful bisection/bracketing flags.

This test validates the nonlinear-state infrastructure before it is used by a
full near-vacuum evaporation model.

## T4f — nearVacuumWang constitutive/coupling regression

Script:
`tests/nearVacuumWang/Allrun`

Checks:
1. target-pressure strong-evaporation case reduces to the corrected sonic
   Knudsen-layer limit;
2. an intentionally low-liquidus synthetic case exercises the subsonic
   transition branch and compares against independently precomputed values;
3. temperatures below liquidus return zero liquid-evaporation mass/recoil flux;
4. a one-step `vacuumLaserbeamFoam` coupling run at 0.6 Pa completes with
   finite evaporation heat flux.

This is a constitutive regression using synthetic properties, not Ti-6Al-4V
experimental validation.

## T8 — Primary WSL2 checkpoint validation

Environment:
- Windows 11 host;
- WSL2 Linux runtime;
- Intel Core i9-14900KF.

The exact OpenFOAM version is recorded at test time rather than assumed.

The first local checkpoint is Phase 4c on `dev/vacuum-solver`. Required
focused regressions are:
- legacy equivalence;
- Hertz-Knudsen analytical curve;
- corrected sonic Knudsen-layer model;
- corrected transition relations;
- nearVacuumWang constitutive/coupled smoke test.

The full command sequence and return-log requirements are maintained in
`log/LOCAL_TESTING_WSL2.md`.

Phase-5 radiation remains unmerged until this local checkpoint is accepted.

## T4g — Wang Eqs. (18)-(20) alloy-mixture regression

Script:
`tests/wangAlloyMixture/Allrun`

Purpose:
verify the new multi-component path independently of full CFD.

The synthetic two-component fixture checks two temperatures. Expected values are
calculated independently from component mass fractions, conversion to molar
fractions, component Clausius-Clapeyron curves, Wang Eq. (18) mixture
saturation pressure, Eq. (19) vapor molar mass, and the corrected `Ma=1`
Knudsen-layer coefficients.

Acceptance:
- original single-component `nearVacuumWang` regression still passes;
- component mass fractions convert to the expected molar fractions;
- mixture `Pe`, mass flux, recoil pressure, and evaporation heat flux agree
  with independent constants at both temperatures;
- CI build and all pre-existing regression gates remain green.

This test establishes constitutive correctness only. A 304L / near-vacuum CFD
benchmark is the next validation stage.

## T4h — 304L Wang near-vacuum reference regression

Script:
`tests/wang304LReference/Allrun`

Configuration:
- Cr/Ni/Fe = 18/8/74 wt%;
- chamber = 20.265 Pa, 298 K;
- alloy saturation-pressure anchor = 20.16 Pa at 2009 K;
- pure-component Cr/Ni/Fe curves from the documented NIST/Chase references.

Checks:
1. 2009 K reproduces the Table-II alloy pressure anchor and remains below the
   chamber-pressure boiling activation;
2. 2020 K exercises Wang near-vacuum step (4), with 0 < Ma < 0.05;
3. 2300 K exercises the normal transition branch;
4. 3000 K exercises the sonic branch;
5. all existing single-component and synthetic-alloy regressions remain green.

## T9 — Wang 304L near-vacuum CFD validation

Case:
`tutorials/vacuumLaserbeamFoam/wang2020_304L_nearVacuum`

Gate A — 8 um smoke:
- blockMesh and setFields succeed;
- the solver selects `nearVacuumWang`;
- log reports `common-to-sonic (Wang step 4)`;
- no NaN/Inf/fatal error through 10 us;
- laser deposition is non-zero and temperature rises from 298 K;
- the model crosses the ~2009.5 K activation threshold with finite non-zero
  recoil pressure and evaporation heat flux;
- the interface and pressure solution remain stable long enough to justify the
  4 um reference run.

Gate B — 4 um reference:
- run with the paper-resolution 4 um mesh;
- extract atmosphere-connected centerline keyhole depth from alpha.metal=0.5;
- compare the growth interval from approximately 32 to 136 um against the
  experimental 70 us and paper-model 75 us reference;
- compare peak recoil-pressure order of magnitude against the paper's
  approximately 5-atm keyhole-bottom value;
- document deviations attributable to the currently different optical and
  surface-loss closures.

The 8 um smoke is a numerical setup test, not a physical validation result.

## Primary-machine parallel execution policy

From 2026-09-30 onward, the Ubuntu 48-core workstation is the primary
development/validation machine.

Execution policy:
- repository rebuilds: use `./Allwmake -j 48`;
- every test that advances `vacuumLaserbeamFoam` or another full CFD solver:
  decompose and run on **48 MPI ranks**;
- 8 um 304L smoke: 48 MPI ranks;
- 4 um 304L paper-reference run: 48 MPI ranks;
- future 0.6 Pa powder/single-track CFD tests: 48 MPI ranks.

Small constitutive/analytical utilities such as
`vacuumEvaporationModelTest` and `knudsenTransitionTest` remain serial
because they do not advance a CFD domain and complete essentially
instantaneously; wrapping them in 48 MPI ranks would add launch overhead
without testing additional solver behavior.

Already accepted historical regressions are not retroactively rewritten solely
to change execution topology.

## T9c — Wang matched-physics closure gate

Purpose:
close the known model-form differences before another expensive 4 um reference
run.

Changes under test:
- Johnson-Christy Fe fixed complex refractive index at 1070 nm;
- standard complex Fresnel/specular reflection for that optical mode;
- Wang Table-II grey-body radiation, emissivity 0.4;
- interface-local recoil and integrated heat/force diagnostics.

Fast gates:
1. build with `./Allwmake -j 48`;
2. serial `tests/vacuumRadiation/Allrun`;
3. 48-rank `tests/wang304LMatchedSmoke/Allrun`.

Smoke acceptance:
- `fixedComplexIndex` is selected and reported;
- radiation is enabled;
- run reaches 10 us without Fatal/NaN/Inf;
- deposited power is finite and non-zero;
- interface recoil, evaporation-power, radiation-power and recoil-force
  diagnostics are finite;
- evaporation/recoil activates after the chamber-pressure boiling threshold.

Only after this gate passes should the 4 um / 140 us Wang reference be rerun
from t=0. The formal comparison metric remains the connected 3-D
alpha.metal=0.5 keyhole depth.

## T10 — 0.6 Pa moving-laser powder integration smoke

Branch:
`feat/0p6Pa-powder-movingLaser`

Case:
`tutorials/vacuumLaserbeamFoam/304L_0p6Pa_movingPowderSmoke`

Execution:
- OpenFOAM v2512;
- primary 48-core workstation;
- 8 um mesh, 40^3 = 64,000 cells;
- 48 MPI ranks;
- end time 20 us.

Engineering smoke fixture:
- chamber pressure = 0.6 Pa;
- 304L material/evaporation/optics inherited from frozen Wang v1;
- deterministic 20 um-radius powder spheres;
- laser moves +x at 2 m/s from x=-40 um to x=0 over the 20 us run.

The sphere radius and scan speed are **not physical validation inputs**.

Acceptance:
1. blockMesh/setFields/decomposePar succeed;
2. v2512 accepts all sphereToCell powder regions;
3. solver reaches 20 us on 48 ranks without Fatal/NaN/Inf;
4. first and last logged laser positions differ;
5. deposited power remains finite/non-zero;
6. interface recoil and evaporation heat loss become non-zero at 0.6 Pa;
7. the solver reaches `End`.

Script:
`tests/304L0p6PaMovingPowderSmoke/Allrun`

If this gate passes, the next step is to replace the synthetic powder fixture
with a reproducible packing/PSD definition and then extend the moving track,
without changing the already validated evaporation coefficients.

### T10a — 304L at 0.6 Pa constitutive gate

Script:
`tests/wang304L0p6PaReference/Allrun`

Checks before the CFD smoke:
- below-liquidus state remains non-evaporating;
- at 0.6 Pa the chamber-pressure boiling point lies below the 1727 K
  liquidus, so the liquidus is the activation floor;
- evaporation/recoil is active at 1727 K on the liquid side;
- the 3000 K sonic state preserves the validated saturation pressure,
  mass flux and evaporation heat flux;
- chamber-relative recoil changes only by the absolute background-pressure
  subtraction.

This is a serial constitutive test; the full CFD integration gate remains
48-rank.

