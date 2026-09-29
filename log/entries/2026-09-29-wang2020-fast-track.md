# 2026-09-29 Wang-2020 fast-track

## Objective

Compress the project scope to a 2-3 day path from LaserbeamFoam V3.0 to a
validated implementation of the Wang, Zhang & Yan (2020) evaporation model
suitable for near-vacuum keyhole and subsequent 2 um powder-track simulations.

## Starting point

The branch was created from `dev/vacuum-solver`, which already contained:
- the isolated `vacuumLaserbeamFoam` solver;
- runtime-selectable evaporation models;
- exact legacy regression;
- Hertz-Knudsen reference closure;
- corrected sonic Knudsen-layer relations;
- Eq. (16)-(17) transition solver;
- the single-component `nearVacuumWang` production model;
- constitutive and one-step CFD regressions.

## Change set 1 — alloy composition

The first fast-track change closes the main model gap relative to the paper:
Wang Eqs. (18)-(20).

Implementation decisions:
1. `componentNames` activates alloy mode.
2. Individual component dictionaries provide mass fraction, molar mass,
   saturation-pressure reference state, and latent heat.
3. Input mass fractions are converted to molar fractions before Eq. (18).
4. Component Clausius-Clapeyron curves produce `Pi(T)`.
5. `Pe(T)` and vapor `M(T)` are recomputed at every evaluated temperature.
6. The common-atmosphere Eq. (16) residual receives the mixture `Pe(T)`.
7. Mass flux uses `R=Rmol/M(T)` as required by Eq. (20).
8. Thermal evaporation loss stays `mLoss*Lv` with alloy-level `Lv`, matching
   the thermal boundary form in Eq. (32).
9. The old single-component input remains valid and remains regression-tested.

## Validation added

`tests/wangAlloyMixture/Allrun` uses a synthetic two-component alloy with
different molar masses and component vapor-pressure curves.

It checks two temperatures against independent constants for:
- mixture saturation pressure;
- mass flux;
- recoil pressure;
- evaporation heat flux;
- mass-to-molar fraction conversion reported by the model.

The test is wired into GitHub Actions after all existing Phase-0-to-4c gates.

## Immediate next checkpoints

1. Resolve any CI/compiler issue without changing the model equations.
2. Run the branch on OpenFOAM-v2512 under WSL2.
3. Add a literature-traceable 304L material dictionary.
4. Build a short 304L / 0.0002 atm stationary-laser validation case.
5. After the short validation is stable, begin the 2 um powder single-track
   case in parallel on the 48-core workstation.

## Scope held back deliberately

The fast-track does not yet add:
- liquid-composition transport;
- vapor plume CFD/DSMC;
- evaporation mass sink in the VOF equation;
- powder-gas momentum coupling;
- multi-track scanning.

These are deferred so they cannot block the near-vacuum keyhole model needed
for the immediate simulations.
