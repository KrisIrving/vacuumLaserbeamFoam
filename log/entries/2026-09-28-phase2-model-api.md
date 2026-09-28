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
