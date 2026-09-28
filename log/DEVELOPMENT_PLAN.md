# Development plan

## Goal

Develop `vacuumLaserbeamFoam` from LaserbeamFoam V3.0 for LPBF melt-pool and
keyhole simulation in a nominal 0.6 Pa vacuum environment.

## Phase 0 — Baseline and reproducibility

- Preserve exact V3.0 baseline.
- Confirm repository build in the supported OpenFOAM environment.
- Run at least one original laserbeamFoam tutorial and retain logs/metrics.
- Define numerical comparison quantities for later regression.

Acceptance:
- `./Allwmake` succeeds.
- Original solver tutorial completes.
- Baseline metrics are archived.

## Phase 1 — Solver bootstrap (completed)

- Add `applications/solvers/vacuumLaserbeamFoam`.
- Keep equations and physics identical to V3.0 `laserbeamFoam`.
- Rename only application/build identity and diagnostic references.
- Build both solvers from the same repository.

Acceptance:
- Both executables compile.
- Running the same case with either executable gives equivalent fields within
  numerical/restart tolerance.

## Phase 2 — Vacuum evaporation model API (completed)

Create a runtime-selectable library, planned name
`vacuumEvaporationModels`, so `UEqn.H` and `TEqn.H` no longer contain
hard-coded evaporation/recoil correlations.

Phase-2 API outputs:
- recoil pressure from temperature;
- evaporative heat flux from temperature.

First model: `legacyAnisimov`, reproducing V3.0 exactly.

The API will be extended with saturation pressure, mass flux, and explicit
chamber-pressure inputs when the pressure-aware models are introduced in the
next phases.

Acceptance:
- legacy model reproduces the Phase-1 reference result. **PASS** using the
  automated byte-level field regression at output time 1e-05.

## Phase 3 — Pressure-aware reference model

- Add `constant/vacuumProperties`.
- Introduce explicit `chamberPressure` and `chamberTemperature`.
- Add a Hertz-Knudsen-type reference model for controlled unit/curve tests.
- Keep `pRef`, `pChamber`, and CFD pressure conceptually and numerically separate.

## Phase 4 — Near-vacuum evaporation/recoil

- Implement literature-grounded near-vacuum/Knudsen-layer closure.
- Derive evaporation cooling and recoil pressure from one consistent mass/momentum
  transfer model.
- Validate model curves before coupling to full melt-pool simulations.

## Phase 5 — Vacuum radiation

- Add free-surface radiation to chamber walls.
- No conventional gas convective heat-transfer coefficient at 0.6 Pa.
- Verify radiation independently using prescribed-temperature tests.

## Phase 6 — Numerical void phase study

- Treat VOF outer phase as a numerical void/pseudo-gas rather than a physical
  continuum representation of 0.6 Pa argon.
- Perform sensitivity studies against pseudo-gas density/viscosity and density ratio.
- Identify a numerically stable range with negligible influence on melt-pool metrics.

## Phase 7 — Bare-plate pressure sweep

Planned pressures include atmospheric/low-pressure anchors and the experiment,
with emphasis on monotonic/physically interpretable trends down to 0.6 Pa.

Metrics:
- peak temperature;
- melt-pool length/width/depth;
- depression/keyhole depth;
- recoil pressure;
- evaporation mass/energy flux;
- absorbed laser power.

## Phase 8 — 0.6 Pa experimental validation

Calibrate only parameters with defensible experimental/optical uncertainty.
Avoid using arbitrary recoil multipliers as a catch-all fit parameter.

## Phase 9 — Powder-bed LPBF

- Start from static powder-bed geometry/DEM initialization.
- Validate single-track morphology before multi-track cases.

## Phase 10 — Evaporation-induced mass removal

Use the existing phase-fraction source interfaces to add surface recession.
Mass and energy conservation must be explicitly tested.

## Phase 11 — Multi-component evaporation

Only if required by experiment, add preferential Ti/Al/V evaporation and
composition evolution, with particular attention to Al loss.

## Phase 12 — Multi-track LPBF

Study hatch spacing, remelting, thermal accumulation, and track interaction.

## Phase 13 — Optional rarefied plume / DSMC coupling

This is outside the initial melt-pool solver scope and should only be developed
if plume/denudation physics becomes a primary experimental observable.
