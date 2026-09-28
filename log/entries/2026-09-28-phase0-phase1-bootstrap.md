# 2026-09-28 — Phase 0/1 bootstrap session

## Objective

Begin code development without mixing structural changes with vacuum-physics
changes.

## Work performed

1. Confirmed the project baseline is the exact public LaserbeamFoam V3.0 tree.
2. Created `dev/vacuum-solver` from the baseline commit.
3. Added a parallel solver directory derived from V3.0 `laserbeamFoam`.
4. Renamed only the application/build identity and one diagnostic source-name
   reference.
5. Created the persistent `log/` research/development record.

## Scientific intent

This commit is deliberately boring from a physics perspective. That is useful:
if it fails to compile or produces different results, the issue is structural
rather than caused by a new vacuum model.

## Next checks

- GitHub Actions build.
- Local build in the experimental workstation OpenFOAM environment.
- Same-case equivalence test between `laserbeamFoam` and
  `vacuumLaserbeamFoam`.

## Next implementation idea after tests pass

Extract the hard-coded V3.0 recoil and evaporation-cooling expressions into a
runtime-selectable model with a `legacyAnisimov` implementation that must
reproduce the original fields before any pressure-aware model is introduced.
