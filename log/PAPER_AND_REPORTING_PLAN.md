# Paper and research-output plan

This file tracks writing, figure, table and reproducibility work as a formal
project stream. It is not postponed until the CFD development is finished.

## 1. Intended paper structure

### 1. Introduction
- LPBF/keyhole evaporation under low pressure;
- need for a pressure-aware evaporation/recoil closure;
- limitation of using conventional atmospheric empirical recoil forms at
  near-vacuum pressure;
- project objective and scope.

### 2. Numerical model

#### 2.1 Base VOF thermal-fluid solver
- LaserbeamFoam lineage;
- incompressible two-phase VOF;
- phase change and Darcy treatment;
- Marangoni and surface tension.

#### 2.2 Laser/ray-tracing model
- Gaussian source;
- multiple specular reflection;
- fixed-complex-index Fresnel mode;
- distinction from the retained legacy Drude path.

#### 2.3 Near-vacuum evaporation model
- saturation-pressure relation;
- Knudsen-layer jump relations;
- common-atmosphere transition;
- Ma=0 endpoint;
- Tk0/Tk1;
- mass flux;
- recoil pressure;
- evaporation heat flux;
- chamber-pressure role.

#### 2.4 Multi-component 304L treatment
- Cr/Ni/Fe mass fractions;
- conversion to molar fractions;
- mixture pressure;
- vapor molar mass;
- alloy anchor.

#### 2.5 CFD coupling
- recoil-pressure localization;
- evaporation heat-flux localization;
- radiation;
- distinction between chamber pressure and CFD pressure;
- pseudo-gas limitation.

#### 2.6 Powder-bed initialization
- deterministic seed;
- PSD;
- sequential vertical deposition;
- setFields geometry;
- manifest/provenance.

#### 2.7 Moving-keyhole metric
- connected alpha=0.5 surface;
- laser-following local window;
- frozen 120/60/+/-75 um definition;
- distinction from stationary global-depth metric.

### 3. Verification and validation

#### 3.1 Constitutive regression
- analytical unit/curve tests;
- sonic and transition relations;
- alloy mixture;
- Ma=0 endpoint.

#### 3.2 Wang 304L benchmark
- case definition;
- Fe-Fresnel optical check;
- connected-3D depth;
- growth interval;
- recoil-load comparison;
- energy budget.

#### 3.3 Numerical resolution for moving powder
- T13b 8 um versus 4 um pair;
- production-mesh decision.

#### 3.4 Additional numerical sensitivity
- pseudo-gas;
- timestep/Courant if required;
- seed variability when production PSD is available.

### 4. 0.6 Pa powder-bed moving-track results
To be populated after experimental inputs are frozen.

### 5. Discussion
- role of low-pressure recoil;
- role of evolving optical geometry;
- moving-keyhole lag;
- powder stochasticity;
- limitations.

### 6. Conclusions

---

## 2. Wang validation figure list

Priority A — main-text candidates:
1. model-regime / constitutive-curve figure;
2. optical closure check;
3. keyhole-depth history and 32-to-136 um comparison;
4. recoil-load validation;
5. energy-budget history.

Priority B — supplementary candidates:
6. centreline versus connected-3D depth cross-check;
7. surface p99 versus hottest-face recoil pressure;
8. moving/interface post-processing definition schematic;
9. constitutive regression table/curve details.

## 3. Target 0.6 Pa figure list

Planned:
1. generated powder bed + PSD/manifest summary;
2. moving-keyhole depth versus laser position;
3. bottom lag behind laser;
4. deposited power / evaporation / recoil history;
5. interface-area history;
6. 8 versus 4 um resolution;
7. powder-seed ensemble;
8. final morphology and cross-sections;
9. experiment-versus-simulation comparison.

---

## 4. Tables to maintain

### Table A — model assumptions
Columns:
- mechanism;
- implemented treatment;
- source;
- solver file;
- limitation.

### Table B — 304L/Wang validation parameters
Include:
- chamber pressure/temperature;
- laser power/diameter/wavelength;
- optical n,k;
- material properties;
- emissivity;
- mesh/time settings.

### Table C — Wang validation results
Include:
- t32;
- t136;
- growth interval;
- final depth;
- recoil-load comparison;
- energy-budget metrics.

### Table D — production 0.6 Pa inputs
Do not fill engineering placeholders into the final paper table.
Populate only after experimental target values are explicitly frozen.

### Table E — numerical sensitivity
Include:
- 8/4 um;
- timestep/Courant if run;
- pseudo-gas sensitivity;
- random-seed sensitivity.

---

## 5. Reproducibility artifacts

For each paper figure/table retain:
- source case;
- git commit;
- raw CSV/log or manifest;
- post-processing script;
- final plotting script;
- figure caption;
- units and metric definition.

Recommended repository structure:

`paper/`
- `wang2020_validation/`
- `moving_powder_0p6Pa/`
- `scripts/`
- `data/`
- `figures/`
- `tables/`
- `captions/`

Large raw OpenFOAM processor directories should not be committed. Store only
small derived data and scripts in git, with the original case/output location
recorded in the metadata.

---

## 6. Current writing status

### Completed in substance
- Wang model development narrative;
- Wang 304L validation numbers;
- optical-gap diagnosis;
- recoil-load definition;
- main limitations;
- initial Chinese paper-oriented summary;
- initial English Methods/Results draft;
- initial compact validation-figure concepts/scripts.

### Still to finalize
- regenerate all figures from the authoritative local completed outputs;
- put figure scripts/data into the repository in a stable paper directory;
- produce publication-quality vector figures;
- create one parameter/source table directly from versioned case dictionaries;
- add exact commit/case provenance to each figure;
- prepare a concise supplementary validation table;
- align terminology across Chinese notes, code and manuscript;
- decide final journal/manuscript formatting later.

---

## 7. Immediate documentation tasks while CFD runs

1. Keep PROJECT_STATUS.md current after each major gate.
2. Update TEST_RESULTS.md only from measured runs.
3. Add the final T13b resolution table when the pair completes.
4. Freeze a paper-data CSV for the Wang validation.
5. Re-run the full-history plotting scripts on the local authoritative outputs.
6. Commit plot scripts and small derived CSVs, not raw processor directories.
7. Start a formal model-assumption/limitation table.
8. Start the 0.6 Pa experiment-input provenance table before production runs.

Documentation is considered part of completion, not optional cleanup.
