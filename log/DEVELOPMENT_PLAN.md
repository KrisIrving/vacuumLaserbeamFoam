# Development plan — current roadmap

## Goal

Develop and validate `vacuumLaserbeamFoam` for near-vacuum LPBF with the
current target of 304L at 0.6 Pa, including evaporation/recoil, powder-bed
geometry and a moving laser.

For current measured status, see `PROJECT_STATUS.md`.
For writing/figure deliverables, see `PAPER_AND_REPORTING_PLAN.md`.

---

## Milestone 1 — Baseline and solver bootstrap

**Status: COMPLETE**

- preserve LaserbeamFoam V3.0 baseline;
- add `vacuumLaserbeamFoam`;
- establish build/test workflow;
- maintain legacy regression.

## Milestone 2 — Evaporation-model API and reference models

**Status: COMPLETE**

- runtime-selectable evaporation library;
- legacy Anisimov path;
- pressure-aware Hertz-Knudsen reference;
- sonic Knudsen-layer branch;
- transition-state relations.

## Milestone 3 — Wang near-vacuum production closure

**Status: COMPLETE / FROZEN**

- common-atmosphere transition;
- exact Ma=0 endpoint;
- automatic Tk0/Tk1;
- chamber-pressure activation;
- multi-component alloy path;
- 304L Cr/Ni/Fe implementation.

## Milestone 4 — Wang optical/radiative alignment

**Status: COMPLETE / FROZEN**

- fixed-complex-index Fe Fresnel mode;
- multiple specular reflection;
- grey-body radiation;
- energy/recoil diagnostics.

## Milestone 5 — Wang 304L validation

**Status: COMPLETE / FROZEN**

Primary result:
- 32-to-136 um connected-3D growth = 76.23 us versus Wang approximately 75 us.

Recoil-load comparison is close without empirical coefficient tuning.

This milestone is closed except for optional publication-oriented
mesh/interpolation sensitivity of the isolated hottest recoil-pressure face.

## Milestone 6 — 0.6 Pa moving-powder integration

**Status: COMPLETE**

Passed:
- 0.6 Pa constitutive gate;
- moving-laser CFD;
- explicit powder geometry;
- deterministic powder generator;
- 20-us generated-bed smoke;
- 300-us / 600-um long-track integration.

## Milestone 7 — Moving-keyhole metric

**Status: COMPLETE / FROZEN**

Formal laser-following window:
- 120 um trailing;
- 60 um forward;
- +/-75 um transverse.

The window is based on explicit convergence against 160/200 um alternatives.

## Milestone 8 — Moving-powder numerical resolution

**Status: RUNNING**

Strict paired cases:
- 8 um / 64k cells;
- 4 um / 512k cells.

Everything except spatial resolution is matched.

Decision output:
- production mesh policy for screening versus publication cases.

## Milestone 9 — Numerical robustness for production

**Status: PLANNED**

Priority:
1. conclude spatial-resolution policy;
2. pseudo-gas density/viscosity sensitivity;
3. timestep/Courant sensitivity only if needed;
4. boundary/domain sensitivity only if indicated by results.

The purpose is to bound numerical artefacts before experimental calibration.

## Milestone 10 — Experiment-input freeze

**Status: PLANNED**

Create a versioned input/provenance table for:
- pressure;
- power;
- scan speed;
- spot size/profile;
- wavelength;
- PSD;
- layer thickness;
- packing fraction;
- material properties;
- preheat/initial conditions.

Engineering fixture values must not silently become final experimental inputs.

## Milestone 11 — Experiment-matched single-track study

**Status: PLANNED**

- use 8 um for broad screening only if Milestone 8 permits;
- rerun key cases at 4 um;
- use a small deterministic seed ensemble;
- compare moving-keyhole, melt-pool and track morphology to experiment.

No arbitrary recoil multiplier is permitted as a catch-all calibration.

## Milestone 12 — Model extensions driven by discrepancies

**Status: CONDITIONAL**

Potential:
- evaporation mass removal/interface recession;
- preferential multi-component evaporation and composition evolution;
- temperature-dependent optical properties;
- rarefied plume/DSMC coupling.

Implement only when a specific observable or discrepancy justifies the added
physics.

## Milestone 13 — Multi-track / process studies

**Status: FUTURE**

After single-track validation:
- hatch spacing;
- remelting;
- thermal accumulation;
- track interaction.

---

## Parallel workstream — paper and reproducibility

**Status: ACTIVE**

This workstream runs in parallel with Milestones 8-13.

Deliverables:
- Wang model Methods/Validation summary;
- publication tables;
- versioned plotting scripts;
- small derived data products;
- figure captions and provenance;
- numerical-resolution subsection;
- 0.6 Pa moving-powder figure set;
- final reproduction index.

See `PAPER_AND_REPORTING_PLAN.md`.
