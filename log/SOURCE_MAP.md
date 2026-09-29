# Source map for vacuumLaserbeamFoam development

This file records where each major physical mechanism lives in the V3.0 code
and where future vacuum-specific changes should be made.

## Main solver control flow

### `applications/solvers/vacuumLaserbeamFoam/vacuumLaserbeamFoam.C`

Current role:
- time loop;
- interface tracking selection (MULES or isoAdvector);
- property update;
- ray-tracing deposition update;
- U/T/p PIMPLE sequence;
- melt-history update.

Development rule:
Keep detailed vacuum constitutive physics out of this file. New physics should
be exposed through model interfaces and called from the equation files.

## Field/material initialization

### `applications/solvers/vacuumLaserbeamFoam/createFields.H`

Current relevant quantities:
- `p0`, `Tvap`, `Mm`, `LatentHeatVap`;
- `pVap` recoil field;
- `Qv` evaporation-cooling field;
- thermal/material fields;
- laser heat-source object.

Planned change:
Introduce a separate vacuum-model dictionary/object. Do not repurpose `p_rgh`
as chamber absolute pressure.

## Momentum equation

### `applications/solvers/vacuumLaserbeamFoam/UEqn.H`

Current V3.0 physics:
- mushy/solidification Darcy damping;
- Marangoni force;
- phenomenological recoil pressure:
  `pVap = 0.54*p0*exp(...)`;
- surface tension and buoyancy terms.

Phase-2 change:
The hard-coded recoil correlation is replaced by
`vacuumEvaporationModel::recoilPressure(T)`. The first implementation,
`legacyAnisimov`, contains the exact V3.0 expression.

## Energy equation

### `applications/solvers/vacuumLaserbeamFoam/TEqn.H`

Current V3.0 physics:
- transient/advection/conduction;
- fusion latent heat correction;
- ray-tracing deposition;
- hard-coded evaporation cooling `Qv`.

Phase-2 change:
Evaporation heat loss is routed through
`vacuumEvaporationModel::evaporationHeatFlux(T)`, using the same selected model
as recoil.

Future change:
- add validated free-surface radiation to chamber surroundings.

## Pressure equation

### `applications/solvers/vacuumLaserbeamFoam/pEqn.H`

Current role:
- pressure-velocity coupling;
- application of surface-tension/recoil/buoyancy contributions through face fluxes.

Design constraint:
CFD pressure must remain conceptually separate from experimental
`chamberPressure`.

## Interface equation hooks

### `applications/solvers/vacuumLaserbeamFoam/isoAdvector/alphaSuSp.H`
### `applications/solvers/vacuumLaserbeamFoam/MULES/alphaSuSp.H`

Current state:
- `Su`, `Sp`, and `divU` are zero.

Future use:
These are candidate hooks for evaporation-induced interface recession/mass
removal after the heat/recoil model has been validated.

## Optical heat source

### `src/laserHeatSource/`

Current role:
- ray creation/propagation;
- interface detection;
- Fresnel absorption;
- multiple reflection;
- laser deposition field.

Current decision:
Do not modify in early vacuum phases. Optical uncertainty/calibration should be
treated separately from vacuum evaporation/recoil model development.

## Explicit vapour reference implementation

### `applications/solvers/compressibleLaserbeamFoam/`
### `applications/solvers/compressibleLaserbeamFoam/multiphaseMixtureThermo/`

Useful reference features:
- explicit condensed/vapour phases;
- saturation-pressure calculation;
- liquid-vapour source terms;
- compressible pressure coupling.

Current decision:
Use this code as a source of implementation ideas for later mass transfer, not
as the first 0.6 Pa production solver framework.

## Regression reference

### `applications/solvers/laserbeamFoam/`

Must remain unmodified while early vacuum development proceeds. It provides the
same-repository numerical reference for `legacyAnisimov` and Phase-1
equivalence testing.

## Vacuum evaporation model library

### `src/vacuumEvaporationModels/`

Current structure:
- `vacuumEvaporationModel/` — abstract runtime-selection interface;
- `legacyAnisimov/` — V3.0-equivalent recoil/cooling closure.

Planned derived models:
- Hertz-Knudsen reference model;
- near-vacuum/Knudsen-layer model.

## Phase-3 additions

### `constant/vacuumProperties`

Owns vacuum-environment/model configuration:
- `evaporationModel`;
- `chamberPressure`;
- `chamberTemperature`;
- model-specific coefficient sub-dictionaries.

### `src/vacuumEvaporationModels/hertzKnudsen/`

Pressure-aware reference implementation. Provides:
- `saturationPressure(T)`;
- `massFlux(T)`;
- `recoilPressure(T)`;
- `evaporationHeatFlux(T)`.

It is an intermediate benchmark only; Phase 4 will introduce the final
near-vacuum/Knudsen-layer closure.

### `applications/utilities/vacuumEvaporationModelTest/`

Diagnostic utility used to evaluate evaporation-model outputs at a prescribed
uniform temperature without running the full melt-pool solver. This separates
constitutive-model verification from CFD coupling and is intended to remain
useful for Phase 4 and later model development.

## Phase-4a additions

### `src/vacuumEvaporationModels/knudsenLayerSonic/`

Implements the strong-evaporation `Ma=1` Knudsen-layer branch of the
literature model used for Phase 4.

Outputs:
- Clausius-Clapeyron saturation pressure;
- sonic Knudsen-layer mass flux;
- chamber-relative recoil traction;
- evaporative heat flux.

This directory does not yet contain the complete near-vacuum interpolation
algorithm; that will be added as a separate model/change in Phase 4b.
