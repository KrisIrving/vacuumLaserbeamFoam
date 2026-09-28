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
