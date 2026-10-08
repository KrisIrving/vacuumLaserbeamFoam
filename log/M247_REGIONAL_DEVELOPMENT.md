# M247 structural acceleration checkpoint — 2026-10-08

The user requests ending small parameter screens and accelerating development.
Freeze the dt/cadence/halo sweeps. No new Ubuntu test requested in this checkpoint.

## Latest evidence

210010 native halo pair completed with all pilot screens. Baseline371.384s/40steps;
halo514.530s/48steps; speedup0.72179 (38.54% more wall time).11topology skips did
not compensate for the added refined cells/steps. Do not adopt halo1 or extend it.
Default halo0,interval1,5ns retained. Existing options preserved for reproducibility.
All archives remain evidence; passing screens are not production approval.

## Development objective

Replace whole-domain coupled CFD with global coarse conduction and moving local
VOF/flow/laser physics. Merely adding AMR leaves equations solved everywhere and
cannot supply the needed order-of-magnitude cost reduction. Regional solver is
NOT implemented yet; this change starts its conservative transfer reference.

## Implemented now

regional_transfer.py provides exact axis-aligned box overlap weights, coarse-to-local
volume-average density gathering and local-to-coarse integrated correction scatter.
Sparse weights reuse a spatial bucket index. Source/target overlaps, incomplete
coverage and invalid inputs reject. Corrections conserve integrated quantity and
must be DELTAS from the coarse prediction, not absolute local energy. Global cells
outside the local overlap receive zero correction.147Python tests pass, including
crossing-cell weights, negative corrections, gaps/overlap and finite-data rejection.
This is an offline correctness reference, not an OpenFOAM runtime implementation
or a general polyhedral mapper. No runtime speedup or full thermodynamic validation
is claimed. No existing solver equations/defaults changed.

## Next coherent implementation milestone

1. Native global/local meshes and fields with separate ownership: global conduction
   prediction, local isoAdvector/momentum/pressure/thermal/laser correction. Retain
   material model and validated optics; avoid replacing fine optics with coarse normals.
2. Port overlap transfer to native parallel code with cached addressing and ownership
   across ranks. Validate box-volume equality for the current orthogonal hex geometry;
   reject deformed/non-box cells until general overlap is available.
3. Use true material enthalpy with reference and temperature-dependent cp/latent
   state; rho*(cp*T+L*epsilon) remains a proxy and is NOT the conserved-energy contract.
   Solve enthalpy-to-T/liquid inversion consistently with current M247 physics.
4. Local-core ownership of laser/evaporation/radiation/recoil and advective transport;
   global prediction must not count the same local heat source twice. Match interface
   conductive flux with opposite signs. Scatter integrated local corrections only.
5. Move the region using laser position plus active liquid/hot/fast wake; preserve old
   and new overlap fields, history and cold powder entry. Do not discard active flow
   or material at a region boundary. Boundary criteria must be validated, not relaxed
   to force a small region. Pressure/free-surface outlet treatment remains unresolved.
6. Package native build, transfer/energy/interface checks, matched physics and cost
   into ONE integrated driver. User runs one bounded acceptance job, not individual
   small parameter screens. Report numerical budget stop/failure, conserved energy,
   mass, molten/keyhole geometry, optical power and total wall cost together.

## Acceptance and production promotion

First integrated milestone is a functioning coupled regional solver with an auditable
energy/material ledger, not a promise of24h full-track execution. Then compare a
meaningful melting/solidification interval against the protected full-CFD reference.
Region and mesh/timestep errors must be separated. Proceed to a24h-budget4um
verification and1.5-2mm full track only after physical/cost evidence supports it.
2um accuracy and full-track affordability remain unproven.

Do not ask the user to run more dt/cadence/halo combinations. Continue implementation
locally until the integrated native milestone is concrete enough to test.
