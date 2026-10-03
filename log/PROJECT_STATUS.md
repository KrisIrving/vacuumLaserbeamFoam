# Project status — 2026-10-03

This file is the current-state snapshot of the vacuumLaserbeamFoam project.
Detailed chronology remains in CHANGELOG_DEV.md and measured values remain in
TEST_RESULTS.md.

## Project objective

Develop a reproducible OpenFOAM-v2512 solver workflow for laser melting,
evaporation/recoil and keyhole dynamics under near-vacuum LPBF conditions,
with the present target centred on **304L at 0.6 Pa with a powder bed and a
moving laser**.

The solver lineage is LaserbeamFoam V3.0. The project intentionally preserves
the original solver baseline and introduces new physics through documented,
runtime-selectable additions rather than replacing the entire architecture.

---

## A. Completed and frozen work

### A1. Baseline and solver bootstrap — COMPLETE

- preserved the LaserbeamFoam V3.0 baseline;
- added `vacuumLaserbeamFoam`;
- established the local OpenFOAM-v2512 / 48-core workflow;
- retained legacy behaviour through `legacyAnisimov` regression coverage.

### A2. Evaporation-model architecture — COMPLETE

Implemented runtime-selectable `vacuumEvaporationModels` with:
- `legacyAnisimov`;
- `hertzKnudsen`;
- `knudsenLayerSonic`;
- transition-state relations;
- `nearVacuumWang`.

Analytical and constitutive tests cover saturation pressure, mass flux, recoil
pressure, evaporation heat flux, sonic/transition limits and chamber-pressure
activation.

### A3. Wang near-vacuum model — COMPLETE / FROZEN

The project-relevant Wang, Zhang & Yan (2020) near-vacuum implementation is
frozen as **Wang 304L matched validation v1**.

Completed items:
- Knudsen-layer jump relations;
- common-atmosphere transition solve;
- exact Ma=0 boiling endpoint;
- automatic Tk0/Tk1 thresholds;
- chamber-pressure activation;
- Cr/Ni/Fe multi-component 304L extension;
- mass-fraction to molar-fraction conversion;
- 304L pressure anchor;
- VOF recoil-pressure coupling;
- evaporation heat-loss coupling.

No empirical recoil multiplier was introduced.

### A4. Optical/radiative closure for Wang validation — COMPLETE / FROZEN

Implemented:
- backward-compatible Drude/resistivity optical mode;
- fixed-complex-index Fe Fresnel mode;
- specular multiple reflection;
- grey-body chamber radiation;
- integrated energy/recoil diagnostics.

The Wang benchmark uses the Fe fixed-complex-index route at 1070 nm.

### A5. Wang 304L CFD validation — COMPLETE / FROZEN

Reference configuration:
- 20.265 Pa / 298 K;
- 260 W / 100 um stationary laser;
- 4 um mesh, 80^3 cells;
- 48 MPI ranks;
- 140 us.

Primary validation results:
- connected-3D t32 = 25.7344 us;
- connected-3D t136 = 101.966 us;
- 32-to-136 um growth interval = **76.2318 us**;
- Wang current-model reference = approximately 75 us;
- x-ray reference = approximately 70 us;
- centreline interval = 76.0169 us;
- final 140-us connected-3D depth = 183.433 um;
- surface pressure-load integral at the equivalent paper comparison stage =
  approximately **3.52 mN** versus Wang approximately 4 mN;
- history peak pressure-load integral = 4.70 mN.

The isolated hottest reconstructed recoil-pressure face remains an OPEN
mesh/interpolation sensitivity diagnostic only. It is not a reason to retune
the Wang closure.

### A6. Formal stationary-keyhole post-processing — COMPLETE

Frozen stationary metric:
- atmosphere-connected main `alpha.metal=0.5` 3-D interface;
- disconnected pores/droplets excluded;
- deepest supported interface point;
- centreline extraction retained as an independent cross-check.

### A7. 0.6 Pa constitutive and moving-powder integration — COMPLETE

Passed:
- 304L at 0.6 Pa constitutive regression;
- 13-sphere integration smoke;
- generated-powder integration smoke;
- moving laser;
- 48-rank execution;
- evaporation/recoil/radiation activation.

The validated Wang coefficients remain unchanged.

### A8. Reproducible powder-bed generator — COMPLETE

Implemented deterministic geometric powder generation with:
- versioned configuration;
- fixed seed;
- uniform or truncated-lognormal PSD support;
- sequential vertical deposition;
- layer-thickness rejection;
- overlap check;
- generated `setFieldsDict`;
- exact particle CSV;
- JSON manifest containing PSD and packing statistics.

This is a geometric initial-condition generator, not DEM.

### A9. Long-duration 0.6 Pa moving-track integration — COMPLETE

Engineering T12 case:
- 0.6 Pa;
- 260 W / 100 um laser;
- 2 m/s engineering scan speed;
- 600 um track;
- 300 us;
- 8 um mesh / 160,000 cells;
- 144 generated particles;
- 48 MPI ranks.

Result:
- completed normally in 6.68 h wall time;
- no Fatal/NaN/Inf;
- stable CFL/interface-CFL behaviour;
- moving keyhole formed and entered a quasi-steady stage.

Initial moving-depth observations:
- >10 um by 25 us;
- >20 um by 35 us;
- >30 um by 45 us;
- >40 um by 70 us;
- peak depth 50.94 um at 140 us;
- 75-210 us mean depth approximately 48.8 um;
- 220-300 us mean depth approximately 42.6 um.

The shallower late stage is not caused by collapse of evaporation/recoil:
deposited power and connected interface area decrease, while evaporation power
remains similar and recoil/interface pressure remains comparable or slightly
higher.

### A10. Formal moving-keyhole metric — COMPLETE / FROZEN

Trailing-window sensitivity was tested at 80/100/120/160/200 um.

Results:
- 120, 160 and 200 um histories are pointwise identical;
- 100 um is nearly converged but can differ by up to 2.26 um;
- 80 um can differ by up to 5.07 um.

Frozen moving-keyhole window:
- trailing = **120 um**;
- forward = 60 um;
- transverse half-width = 75 um;
- reference surface y = 200 um;
- atmosphere-connected main alpha=0.5 interface only.

---

## B. Work currently running

### B1. T13b strict 8 um versus 4 um resolution pair — RUNNING

Both cases use:
- identical 320 x 320 x 320 um domain;
- identical seed-304006 56-particle bed;
- identical particle geometry;
- 0.6 Pa;
- frozen Wang evaporation model;
- 260 W / 100 um Fe-Fresnel laser;
- 2 m/s engineering scan speed;
- x=-100 to +100 um;
- 100 us;
- 48 MPI ranks;
- 5 us output cadence;
- frozen 120-um moving-keyhole metric.

Only the spatial resolution is intentionally changed:
- 8 um: 40^3 = 64,000 cells;
- 4 um: 80^3 = 512,000 cells.

Primary outputs:
- moving-keyhole depth difference;
- bottom-lag difference;
- deposited-power difference;
- Tmax/Umax;
- interfacePVapMax;
- evaporation power;
- recoil force;
- time-step/Courant behaviour.

Decision to be made after T13b:
1. whether 8 um is acceptable for broad parameter studies;
2. whether 4 um is required for publication-quality key cases;
3. whether another intermediate/finer grid is justified.

---

## C. Next technical work, in priority order

### C1. Close the mesh-policy decision

After T13b:
- quantify mean and maximum 4-um minus 8-um keyhole-depth differences;
- compare time histories, not only final values;
- compare optical/evaporation/recoil diagnostics;
- record a formal production-mesh policy.

Tentative interpretation bands:
- mean absolute depth difference <4 um: 8 um likely suitable for broad sweeps;
- 4-8 um: use 8 um for screening and 4 um for key results;
- >8 um: moving powder/keyhole results are strongly mesh-sensitive and require
  a revised production resolution strategy.

These are engineering decision bands, not universal convergence criteria.

### C2. Freeze the engineering numerical baseline

Before switching to experimental parameters, perform only the numerical checks
that can materially change the interpretation:
- resolution pair;
- selected time-step/Courant sensitivity if the resolution pair indicates it;
- numerical pseudo-gas density/viscosity sensitivity;
- domain/boundary sensitivity if keyhole or flow approaches boundaries.

Avoid adding more physics until these numerical effects are bounded.

### C3. Build the experiment-matched single-track input set

Replace engineering placeholders with explicit target inputs:
- chamber pressure;
- laser power;
- scan speed;
- spot size / beam profile;
- wavelength;
- powder PSD;
- powder layer thickness;
- packing/solid fraction;
- substrate thickness represented in the computational domain;
- material-property source set;
- initial/preheat temperature where applicable.

Every production input must have:
- source;
- value;
- units;
- uncertainty or plausible range when known;
- code/config location.

### C4. Production powder-bed ensemble

A single random seed is insufficient for powder-bed conclusions.

After final PSD/packing inputs are known:
- freeze a small seed set;
- quantify seed-to-seed variability;
- distinguish deterministic numerical error from powder-geometry variability.

A practical first ensemble is 3 seeds for screening, expanding only if the
response variance requires it.

### C5. Experiment-matched 0.6 Pa single-track simulations

Suggested workflow:
1. 8 um screening runs if T13b permits;
2. select representative/important cases;
3. rerun publication cases at 4 um;
4. compare track/keyhole/melt-pool observables to experiment;
5. do not retune the frozen Wang evaporation coefficients merely to fit one
   powder-bed observable.

Primary observables:
- moving keyhole depth;
- keyhole lag behind laser;
- melt-pool dimensions;
- track cross-section;
- deposited power;
- evaporation heat loss;
- recoil load;
- surface/interface area;
- velocity/temperature extrema;
- morphology after laser passage.

### C6. Numerical pseudo-gas sensitivity

The outer VOF phase remains a numerical pseudo-gas, not a physical 0.6 Pa
continuum gas.

Required before strong production claims:
- vary pseudo-gas density/viscosity over controlled ranges;
- monitor keyhole depth, recoil coupling, parasitic currents, interface
  topology and timestep restrictions;
- define a numerically stable range with small influence on metal observables.

### C7. Physics extensions — only when justified by experiment

Do not automatically expand the model.

Candidate extensions:
- explicit evaporation mass sink / interface recession;
- composition transport and preferential Cr/Ni/Fe evaporation;
- improved temperature-dependent optical properties;
- plume or rarefied-gas coupling.

Each extension should be triggered by a documented discrepancy or research
question, not by model complexity for its own sake.

Rarefied plume/DSMC remains outside the current core scope unless plume,
denudation or gas-phase observables become primary validation targets.

---

## D. Paper, figures and research-record workstream

Documentation is a first-class project deliverable and proceeds in parallel
with CFD development.

### D1. Wang-model paper package — ACTIVE, physics content essentially complete

Required final package:
- concise model derivation/implementation summary;
- exact assumptions and solver coupling;
- 304L material/optical parameter table;
- constitutive-regression summary;
- keyhole-growth validation table;
- recoil-load validation table;
- limitations;
- references;
- reproducible plotting scripts.

Recommended Wang figures:
1. constitutive curves: pSat / mass flux / recoil / qEvap versus temperature;
2. optical-closure comparison;
3. baseline versus matched keyhole-depth history;
4. 32-to-136 um growth comparison;
5. recoil-pressure/recoil-load history;
6. energy-budget history;
7. selected 3-D interface snapshots if publication space allows.

The paper narrative should emphasise that the original approximately 93.88-us
growth interval was closed to 76.23 us primarily by aligning the optical
closure, not by empirically tuning evaporation coefficients.

### D2. 0.6 Pa moving-powder paper package — IN PROGRESS

As target-stage results mature, retain scripts/data for:
- powder manifest/PSD figure;
- moving-keyhole depth versus time/distance;
- keyhole lag versus time/distance;
- deposited-power history;
- recoil/evaporation history;
- interface-area history;
- 8/4 um resolution comparison;
- seed-to-seed variability;
- final single-track morphology/cross-sections.

Do not wait until manuscript writing to reconstruct these quantities.

### D3. Figure/data provenance rule

Every publication figure should be reproducible from:
- a versioned script;
- a small CSV/manifest or an explicitly named solver log/output source;
- a recorded git commit;
- a caption draft stating metric definitions.

Avoid figures that depend only on manual ParaView operations without a saved
state/script and source-output record.

### D4. Writing milestones

1. **Now:** Wang Methods + Validation skeleton and figure list.
2. **After T13b:** numerical-methods / mesh-resolution subsection.
3. **After experimental inputs are frozen:** target-case Methods table.
4. **After first experiment-matched runs:** Results figure set and discrepancy
   log.
5. **After sensitivity/seed runs:** Discussion and limitations.
6. **Before submission:** one-command reproduction index for all paper figures
   and tables.

---

## E. Items intentionally not claimed yet

The project does **not** yet claim:
- experiment-matched 0.6 Pa powder-bed prediction;
- grid independence of moving-powder results;
- powder-seed independence;
- physical simulation of rarefied chamber gas/plume;
- evaporation-driven interface mass recession;
- preferential alloy composition evolution;
- denudation driven by a resolved gas/vapour plume.

These remain separate future questions.

---

## Immediate checkpoint

Current action:
**wait for the strict 8 um / 4 um pair to complete.**

When complete:
1. run pair post-processing;
2. record T13b;
3. freeze production mesh policy;
4. update this status file;
5. continue the paper/figure package in parallel with the next CFD stage.

## 2026-10-03 clarification — final material and validation direction

### Pressure trend before M247 transfer

Although the Wang 304L benchmark is complete, one additional robustness test is
now planned before material transfer:
- 0.6 Pa;
- 20.265 Pa;
- 1 atm.

The purpose is to confirm the expected pressure trend of the frozen Wang
implementation, not to recalibrate it.

A serial constitutive sweep has been added as T14a. A same-material bare-plate
CFD sweep is planned after the currently running 8/4 um resolution pair.

### Final target material

The intended production target is now explicitly recorded as **M247 powder
bed with an approximately 2 mm melt track**.

The solver architecture is ready for powder-bed M247, but the M247 material
parameterization is not yet complete.

See:
`M247_MATERIAL_PORT_PLAN.md`.

The production 2-mm computational strategy will be chosen after T13b determines
whether 8 um can be used for full-track studies and 4 um reserved for key
verification cases.

### Publication-figure direction

The previous development-oriented plotting style is not accepted as the final
manuscript style.

All publication figures will be regenerated using the restrained Acta-like
materials-science style defined in:
- `paper/FIGURE_STYLE_GUIDE.md`;
- `paper/styles/acta_materialia.mplstyle`.
