# 2026-10-03 — Project review and forward plan

## Purpose

Pause feature expansion while the 8 um / 4 um resolution pair runs and review
what is genuinely complete, what is currently being tested, and what should be
done next.

## Completed physics chain

The following chain is considered complete and regression-backed:

LaserbeamFoam V3 baseline
-> vacuumLaserbeamFoam bootstrap
-> runtime evaporation-model API
-> pressure-aware Hertz-Knudsen reference
-> sonic Knudsen-layer relations
-> Wang common-atmosphere transition
-> Ma=0 endpoint
-> multi-component 304L
-> Fe fixed-complex-index Fresnel optics
-> grey-body radiation
-> Wang 304L full CFD validation
-> 0.6 Pa constitutive transfer
-> explicit 3-D powder
-> deterministic powder generator
-> moving laser
-> 300-us moving-track integration.

The Wang validation physics is frozen. Downstream cases must not silently
retune those coefficients.

## Most important validated Wang result

The connected-3D 32-to-136 um keyhole-growth interval is 76.23 us, compared
with approximately 75 us in Wang's current model. The original Drude-optics
baseline was 93.88 us.

This strongly supports the conclusion that the earlier keyhole-growth mismatch
was primarily an optical-closure mismatch rather than a failure of the Wang
evaporation constitutive law.

## Most important 0.6 Pa engineering result so far

The 300-us / 600-um / 144-particle moving-track case completed on 48 ranks in
6.68 h and produced a stable moving depression/keyhole.

A quasi-steady depth around 49 um was observed in the middle portion of the
track, followed by a shallower approximately 43-um stage. Window-sensitivity
analysis confirms that the late-stage shallowing is not an artefact of the
moving-depth trailing window.

The stage change coincides more strongly with reduced deposited power and
reduced connected interface area than with reduced evaporation/recoil.
Evaporation power remains similar and recoil/interface pressure does not
collapse.

This motivates studying numerical resolution and optical/geometric evolution
before modifying the evaporation model.

## Moving-keyhole metric decision

Trailing-window sensitivity:
- 80 um: not converged;
- 100 um: nearly converged but can clip;
- 120 um: converged;
- 160 um: identical to 120 um;
- 200 um: identical to 120 um.

Formal metric:
- 120 um trailing;
- 60 um forward;
- +/-75 um transverse;
- atmosphere-connected alpha.metal=0.5 main interface;
- original y=200 um substrate plane as depth zero.

## Current running test

Strict resolution pair:
- 8 um / 64k cells;
- 4 um / 512k cells;
- same domain;
- same powder seed and exact geometry;
- same laser path;
- same physics and numerical controls where resolution permits;
- 100 us;
- 48 ranks.

This pair decides the production-mesh strategy.

## Decision tree after the resolution pair

### If 8 um and 4 um agree closely

Use:
- 8 um for broad screening/parameter sweeps;
- 4 um for selected publication-quality cases and final verification.

Then proceed to:
- pseudo-gas sensitivity;
- experiment-input freeze;
- multi-seed experiment-matched single-track study.

### If the difference is moderate

Use:
- 8 um for qualitative screening only;
- 4 um for quantitative keyhole/morphology results.

Consider an intermediate 6 um case only if it materially clarifies the trend.

### If the difference is large

Do not start a large parameter sweep.

Instead:
- inspect interface/powder representation;
- determine whether 4 um itself is approaching convergence;
- consider a targeted finer-grid or local-refinement strategy;
- revise the production mesh policy before experiment fitting.

## Physics intentionally deferred

### Evaporation mass removal / recession

Wang's validation did not require an explicit VOF mass sink for the matched
keyhole-growth benchmark. Adding one now would confound the already validated
closure with a new physical mechanism.

Revisit only if:
- long 0.6 Pa tracks show mass-loss/morphology disagreement;
- experimental mass loss is a target observable;
- conservation analysis shows the omission is unacceptable.

### Preferential composition evolution

Not yet justified because the current project has no validated composition-loss
observable driving it.

Revisit if experimental Cr/Ni/Fe loss or material-property changes become
important.

### Rarefied plume / DSMC coupling

Out of the core scope while the validation targets are melt/keyhole/track
observables. Revisit only if plume, denudation or gas-phase flow becomes a
primary research target.

## Documentation/paper work is now a formal workstream

The Wang paper package is not considered optional cleanup.

Required outputs include:
- Methods text;
- model-assumption table;
- validation table;
- constitutive and keyhole plots;
- recoil/energy plots;
- plotting scripts;
- small derived CSVs;
- figure captions;
- git/case provenance;
- limitation statements.

The 0.6 Pa moving-powder stage will use the same reproducibility pattern.

## Next checkpoint

Wait for the resolution pair to complete, then:
1. postprocess both cases;
2. freeze mesh policy;
3. update PROJECT_STATUS.md;
4. update TEST_RESULTS.md;
5. create the numerical-resolution paper table/figure;
6. begin experiment-input freeze and provenance table.
