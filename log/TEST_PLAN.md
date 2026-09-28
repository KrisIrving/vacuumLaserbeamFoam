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
