# M247 computational-cost strategy

## Problem statement

The 200-us, 756k-cell M247 powder run required 29.18 h on 48 MPI ranks.
A simple full-domain extension is not viable for the final 1.5-2 mm track.

Approximate naive scaling:
- 2-mm scan plus conservative leading/trailing buffers: about 2.6 mm x-domain,
  roughly 3.1x the current x-length;
- physical scan time: 2 ms, 10x the current time;
- naive estimate: approximately 900 wall-hours (~38 days) on 48 cores.

A 1.5-mm track remains on the order of 500+ wall-hours (~23 days) under the
same assumptions.

Global 4-um production is therefore excluded.

## Immediate 4-um validation policy: under 24 h

The 4-um M247 test will not start from t=0 and will not refine the whole domain.

Planned method:
1. use an evolved 8-um state in the 150-180-us regime;
2. map that state to a hybrid mesh;
3. retain 4 um only in a compact keyhole/melt-pool ROI;
4. keep coarse cells outside the ROI;
5. run approximately 20-30 us;
6. discard an initial adaptation interval and compare the remaining history
   against the 8-um reference.

Acceptance target:
- one 4-um validation job must finish within 24 h on the 48-core Ubuntu host.

This is a transfer-resolution check, not an independent full-track 4-um run.

## Performance work before production

The solver now supports optional PERF_DIAGNOSTICS timing for:
- VOF;
- material-property updates;
- laser/ray deposition;
- momentum;
- nonlinear thermal/phase-change solve;
- pressure;
- unclassified remainder;
- thermal-corrector count.

A 10-us / 756k-cell benchmark case is provided. Optimization will be based on
measured cost fractions rather than guesswork.

Low-risk candidates after profiling:
- pressure-corrector sensitivity;
- thermal-solver tolerance/corrector sensitivity;
- ray discretization and/or controlled ray-update cadence;
- Courant target sensitivity;
- reduced output overhead.

No physics knob is changed without a paired short regression.

## Final-track architecture

The preferred production architecture is a local moving thermal-fluid model:

- a small moving high-fidelity CFD/VOF region around the laser/keyhole;
- a coarser outer region that solves heat conduction / phase thermal history;
- exchange of temperature/heat flux across the interface;
- the trailing solidified track remains in the thermal domain for
  solidification/cooling without paying full VOF/pressure/momentum cost;
- fresh preheated substrate/powder enters the leading side of the moving
  thermal-fluid window.

This directly matches the physical localization of melt-pool fluid flow.

Literature basis:
- Jia et al., CMAME 419 (2024) 116673: local moving thermal-fluid framework,
  thermal-fluid solved only in the local moving zone and heat transfer in the
  remainder; melt-pool-dimension errors below 2.6% versus full thermal-fluid
  references; part-scale example reduced from about three weeks to 62 h.
- Li et al., CMAME (2023): local multi-mesh finite-volume formulation with a
  coarse thermal base mesh and moving fine thermal-fluid overlay mesh;
  reported 16-50x efficiency gains for the demonstrated size ratios.
- Recent meltPoolFoam workflows also demonstrate adaptive moving-frame /
  mesh-refinement single-track strategies in OpenFOAM.

## Development stages

P0 — instrument and profile current solver.
P1 — achieve safe short-case speedups with existing single mesh.
P2 — build <24-h local 4-um transfer validation.
P3 — prototype moving/local thermal-fluid window with thermal outer domain.
P4 — compare hybrid model against the existing full CFD result over 100-200 us.
P5 — run final 1.5-2 mm melting track and trailing solidification.
