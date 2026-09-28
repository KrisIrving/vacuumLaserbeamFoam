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

Primary future change:
Replace the hard-coded recoil correlation with
`vacuumEvaporationModel::pRecoil()` after a legacy-equivalent model is tested.

## Energy equation

### `applications/solvers/vacuumLaserbeamFoam/TEqn.H`

Current V3.0 physics:
- transient/advection/conduction;
- fusion latent heat correction;
- ray-tracing deposition;
- hard-coded evaporation cooling `Qv`.

Primary future changes:
- route evaporation heat loss through the same evaporation model used for recoil;
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
