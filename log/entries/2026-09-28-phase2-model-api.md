# 2026-09-28 — Phase 2 model API

## Objective

Separate V3.0 evaporation/recoil constitutive equations from the solver equation
files without changing their mathematical form.

## Implementation

A new runtime-selectable library, `libvacuumEvaporationModels`, owns the legacy
parameters and returns:
- recoil pressure field from temperature;
- evaporation heat-flux field from temperature.

The first derived model is `legacyAnisimov`. It intentionally copies the exact
V3.0 formula coefficients (0.54 and 0.82) and thermodynamic expression.

## Compatibility

Existing V3.0 cases do not need an `evaporationModel` entry; the selector
falls back to `legacyAnisimov`. The dedicated bootstrap vacuum tutorial selects
it explicitly to exercise the runtime-selection path.

## Not implemented in this phase

- chamber pressure;
- saturation-pressure API;
- Hertz-Knudsen mass flux;
- Knudsen-layer correction;
- radiation;
- evaporation-induced VOF mass removal.

## Required validation

1. library + solver compilation;
2. runtime model-selection message;
3. bootstrap smoke test;
4. numerical regression against the Phase-1 solver before claiming complete
   equivalence.

## First CI attempt

Run `36418680113`: **FAIL** during library compilation.

Root cause:
the explicit runtime-selection iterator type used in the selector was not
compatible with the OpenFOAM-v2506 API exposed by the CI environment.

The subsequent missing-library linker error was a cascade from this compilation
failure.

Action:
replace the explicit iterator type with `auto` and re-test. This change does
not affect any physical equation.

## Corrected CI result

Run `36419254818`: **PASS**.

The runtime-selection iterator fix allowed:
- `libvacuumEvaporationModels.so` to build;
- `vacuumLaserbeamFoam` to link against it;
- the repository tutorial suite to pass.

## Automated equivalence result

Run `36419960056`: **PASS**.

The automated regression compared upstream `laserbeamFoam` with
`vacuumLaserbeamFoam + legacyAnisimov` at output time `1e-05`.

Byte-identical fields:
- T;
- U;
- alpha.metal;
- p_rgh;
- p;
- epsilon1;
- Qv;
- condition;
- meltHistory.

Conclusion:
Phase 2 successfully changes software architecture without changing the
numerical result of the tested legacy physics case.

## Phase-2 closeout

Phase 2 is considered complete. The next scientific change is Phase 3:
introduce an explicit vacuum environment configuration and a pressure-aware
reference evaporation model. That future change must not reinterpret CFD
`p_rgh` as chamber absolute pressure.
