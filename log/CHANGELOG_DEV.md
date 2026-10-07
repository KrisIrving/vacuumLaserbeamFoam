# Development changelog

## 2026-10-07 — Verified laser profiling result

190239 archive passes build/provenance/convergence/instrumentation regression; five saved final fields are identical. Exchange/wait path dominates mean laser time, with strong trace-rank imbalance. Recorded measured evidence and exchange/ownership optimization target; no new solver change or speedup claim in this review. See `entries/2026-10-07-m247-laser-profile-result.md`.

## 2026-10-07 — Refresh laser lnInclude on incremental builds

User compilation exposed a missing new laserPerformance.H link in existing lnInclude. Added explicit refresh/header check in direct profiling build and library Allwmake; failures stop build dispatch. No ray/solver physics changes. Ubuntu rebuild pending. See `entries/2026-10-07-m247-laser-lninclude-fix.md`.

## 2026-10-07 — Default-off laser internal profiler

Added write-time MPI substage means/maxima, work counters and stride128 trace-search sampling without changing ray physics. RunLaserProfile builds/preflights library and solver, compares off/on tight width-zero restarts and packages build/results. Collector gates on unchanged diagnostics/final fields and convergence.42 local Python checks pass; actual OpenFOAM build and measured costs remain pending. See `tests/m247Performance/LASER_PROFILE.md`.

## 2026-10-07 — Phase localization decision

Verified 183545 archive: width response changes interface phase/Darcy state and raw pressure in solid metal despite converged thermal solves. Recorded arithmetic, field and pressure-log evidence; smoothing remains default-off and unapproved. No further width tests requested. Next speed work targets laser substage profiling and equivalent optimization; no new solver change in this review. See `entries/2026-10-07-m247-phase-localization-decision.md`.

## 2026-10-07 — Phase width-response review and offline localization

Valid phase probe converges but large local width differences remain. Added InspectPhaseBlend for existing hard/narrow and narrow/wide final fields, with region/threshold/worst-cell reports and one archive. Checks runtime mode, provenance and fixed mesh; preserves prior outputs. Thirty-seven local tests pass; no new CFD or closure acceptance. See `entries/2026-10-07-m247-phase-blend-result.md`.

## 2026-10-07 — Initialise blend control before createFields property update

Ubuntu build log confirms a missing declaration in both normal and postProcess createFields inclusion. Moved width ownership/initialisation before the first updateProps call; share validation with runtime reload and avoid a shadowed time-loop width. Existing 35 Python checks pass; actual OpenFOAM rebuild remains pending. See `entries/2026-10-07-m247-phase-blend-initialisation-fix.md`.

## 2026-10-07 — Reject stale phase-probe executables

The 170639 archive used the prior binary and failed runtime mode checks. Fixed application build error propagation and argument-parser path; added a direct build/log/archive command and static binary/PATH preflight before phase CFD. MPI launches the verified absolute path. Thirty-five Python tests, Bash syntax and a mocked solver-build failure check pass. Ubuntu build diagnosis pending; no new CFD evidence or closure approval. See `entries/2026-10-07-m247-phase-blend-build-gate.md`.

## 2026-10-07 — Opt-in continuous phase-temperature candidate

Added default-off smooth alpha-phase override, coupled phase/enthalpy diagnostics and a three-way width-sensitivity short probe. Preserves legacy branches outside the transition; numerical closure and restart energy response require validation. Thirty-one local tests pass; Ubuntu compilation/CFD pending. See `entries/2026-10-07-m247-continuous-phase-candidate.md` and `tests/m247Performance/PHASE_BLEND_PROBE.md`.

## 2026-10-07 — Localization diagnosis

Verified existing localization archive. Global large T/U differences are in numerical gas; seven epsilon endpoint flips all cross the hard alpha=0.05 phase-temperature override. Recorded evidence and coupled interface-treatment requirements. No solver changes or new CFD. See `entries/2026-10-07-m247-localization-diagnosis.md`.

## 2026-10-07 — Two-us result and offline field localization

Both candidate tolerances converge over 2 us, but local field maxima remain unresolved. Added offline region/worst-cell localization and one-archive delivery using saved fields, with no extra CFD. Twenty-seven local tests pass. See `entries/2026-10-07-m247-validation-result-localization.md` and `tests/m247Performance/FIELD_LOCALIZATION.md`.

## 2026-10-07 — Longer candidate convergence validation

Added a 180–182-us standard/tighter candidate test with per-step convergence checks, final all-rank internal-field differences, and automatic review archives. Uses the existing candidate binary; physical production approval remains pending. Twenty-five local tests pass. See `entries/2026-10-07-m247-tolerance-validation-tooling.md` and `tests/m247Performance/THERMAL_VALIDATION.md`.

## 2026-10-07 — Ubuntu thermal result and automatic review archives

The 0.2-us Ubuntu candidate converged in 10–14 correctors/step with zero cap hits and reduced job wall from 127.13 to 35.04 s (3.63x). Longer physical validation remains pending. Both test wrappers now automatically package small review files with run/variant names and a SHA256/missing-file manifest; existing runs can be packaged without rerunning. Nineteen local tests and shell syntax checks pass. See `entries/2026-10-07-m247-thermal-probe-result.md`.

## 2026-10-07 — M247 thermal convergence investigation

Reviewed both full Ubuntu logs: all 25,066 phase corrections per run have max increment 1, while T linear solves take 1–2 iterations. Added default-off residual cell diagnostics and an experimental enthalpy slope correction with an additional phase-temperature gate. Added a 0.2-us legacy/candidate probe. Sixteen local harness/model tests pass; Ubuntu build and CFD validation are pending. See `entries/2026-10-07-m247-thermal-log-review.md` and `tests/m247Performance/THERMAL_PROBE.md`.

## 2026-10-07 — M247 performance phase 1

Added opt-in no-ray-history mode, MPI-aware/I/O-inclusive profiling and an
independent180–182-us comparison harness with a wall budget. Defaults preserve
ray history and thermal residual logging. Local tool tests pass; Ubuntu build,
physical comparison and actual speedup remain pending. See
`entries/2026-10-07-m247-performance-phase1.md` and
`tests/m247Performance/README.md`.

## 2026-09-28 — Phase 0/1 bootstrap

Branch: `dev/vacuum-solver`

Changes:
- preserved `main` as exact LaserbeamFoam V3.0 reference;
- created parallel solver `applications/solvers/vacuumLaserbeamFoam`;
- copied V3.0 laserbeamFoam numerical implementation without intentional
  equation/physics changes;
- changed executable/application identity to `vacuumLaserbeamFoam`;
- added persistent `log/` research/development record.

Physics intentionally **not** changed:
- recoil-pressure equation;
- evaporation cooling;
- laser ray tracing/Fresnel absorption;
- VOF equation;
- phase change/latent heat;
- surface tension and Marangoni force;
- pseudo-gas properties;
- radiation.

Additional Phase-1 test infrastructure:
- added `tutorials/vacuumLaserbeamFoam/bootstrapPlate2D` as a smoke test copied from the upstream Plate2D case;
- the copied case changes only the executable/application name and is explicitly not a vacuum-physics validation case.

Next intended code change:
- only after Phase-1 compilation/regression passes, create the evaporation-model
  runtime-selection architecture.

## 2026-09-28 — Phase-1 CI verification

Commit tested: `2ad22fb0930127c9d5ba596a72d37340e3af1d8e`

- OpenFOAM-v2506 `Allwmake`: PASS.
- `vacuumLaserbeamFoam` executable compiled and linked.
- Added bootstrap Plate2D smoke case was explicitly executed by CI.
- Repository `Alltest`: PASS with zero reported solver/command failures.
- Source comparison confirmed 30/33 solver files are byte-identical to V3.0;
  the only differences are the three intended application-identity changes.
- Full field-by-field `laserbeamFoam` vs `vacuumLaserbeamFoam` regression
  remains pending and is intentionally not inferred from the smoke test.

## 2026-09-28 — Phase 2 evaporation-model API

Branch: `feat/vacuum-model-api`

Implemented:
- new `libvacuumEvaporationModels` library;
- runtime-selectable `vacuumEvaporationModel` base class;
- `legacyAnisimov` model containing the exact V3.0 recoil-pressure and
  evaporation-cooling expressions;
- `UEqn.H` now obtains recoil pressure from the model;
- `TEqn.H` now obtains evaporation heat flux from the same model;
- original `p0/Tvap/Mm/LatentHeatVap/R` ownership moved out of solver field
  creation and into the legacy model;
- bootstrap tutorial explicitly selects `legacyAnisimov`.

No near-vacuum/chamber-pressure physics has been added in this change.

### Phase-2 regression infrastructure

Added `tests/legacyEquivalence/Allrun` and a GitHub Actions step that runs the
same one-step Plate2D state through upstream `laserbeamFoam` and
`vacuumLaserbeamFoam + legacyAnisimov`, then byte-compares key output fields.
This turns legacy equivalence into an automated regression gate rather than a
manual assumption.

### Phase-2 verification and closeout

- First CI run `36418680113`: FAIL because the explicit runtime-selection
  iterator type was incompatible with OpenFOAM-v2506.
- Fixed the selector by using C++17 `auto`; no physics change.
- Corrected CI run `36419254818`: PASS.
- Added automated legacy-equivalence regression.
- CI run `36419960056`: PASS.
- Critical fields were byte-identical between upstream `laserbeamFoam` and
  `vacuumLaserbeamFoam + legacyAnisimov` at time `1e-05`.
- Phase 2 is closed; no chamber-pressure or near-vacuum physics is present yet.

### Phase-2 integration

Pull request: #3 — `Phase 2: runtime-selectable evaporation model API`

Merged into:
`dev/vacuum-solver`

Merge commit:
`14a54919e6a484d6b187c0dbedbde0f83b468879`

The protected project baseline `main` remains unchanged at the LaserbeamFoam
V3.0 tree.

## 2026-09-28 — Phase 3 pressure-aware reference model started

Branch: `feat/pressure-aware-reference`

Implemented in this commit:
- new required `constant/vacuumProperties` for vacuumLaserbeamFoam cases;
- model selection moved from `transportProperties` to `vacuumProperties`;
- runtime model constructor now receives separate environment/model and material
  dictionaries;
- base evaporation-model API extended with `saturationPressure()` and
  `massFlux()`;
- `legacyAnisimov` extended with the new API while preserving the exact V3.0
  recoil and cooling operation order;
- new pressure-aware `hertzKnudsen` reference model;
- CI smoke test for the new model.

No final near-vacuum/Knudsen-layer physics has been implemented yet.

### Phase-3 first CI correction

CI run `36425725491` exposed an OpenFOAM-v2506 API compatibility issue in the
model selector: templated `lookup<word>()` is not supported here. The selector
was changed to the dictionary-stream form already used throughout OpenFOAM.
No equation or physical-model change was made by this correction.

### Phase-3 analytical model regression infrastructure

Added `vacuumEvaporationModelTest`, a small diagnostic utility that directly
evaluates the runtime-selected model without solving U/T/p. Added an independent
analytical regression for the Hertz-Knudsen reference closure at multiple
temperature/back-pressure states, including the zero-net-evaporation limit.

### Phase-3 analytical utility build correction

CI run `36427391669` showed that the new diagnostic utility needed the
OpenFOAM `meshTools` include path/library because `fvCFD.H` pulls AMI mesh
types transitively. Added the missing build dependency; no physics code changed.

### Phase-3 analytical utility output correction

CI run `36428017249` showed that `messageStream Info` cannot set stream
precision directly in OpenFOAM-v2506. The regression utility now uses
`std::cout` with 16-digit precision for its machine-readable test line.

### Phase-3 analytical test fixture correction

CI run `36428475347` reached and passed build, tutorials, legacy regression,
and the pressure-aware solver smoke test. The analytical curve regression then
failed before model evaluation because its copied `vacuumProperties` fixture
had an invalid OpenFOAM header. The fixture header was corrected; no production
model code changed in this commit.

### Phase-3 verification complete

Final CI run `36512859745`: PASS.

All Phase-3 gates pass, including the analytical curve regression. The
pressure-aware reference implementation is ready to integrate into
`dev/vacuum-solver`.

Next development target:
Phase 4 will add a literature-derived Knudsen-layer/near-vacuum model in
incremental, analytically tested steps rather than replacing the reference model
in one change.

### Phase-3 integration

Pull request: #4 — `Phase 3: pressure-aware evaporation reference model`

Merged into:
`dev/vacuum-solver`

Merge commit:
`7d1fed9a61ada6add5fc8c177a8f7fdc2e8a531e`

Final verification before merge:
GitHub Actions run `36512859745` — PASS.

The protected project baseline `main` remains unchanged at the LaserbeamFoam
V3.0 tree.

## 2026-09-29 — Phase 4a sonic Knudsen-layer model

Branch: `feat/knudsen-layer-sonic`

Implemented:
- new runtime-selectable `knudsenLayerSonic` evaporation model;
- Wang et al. (2020) Knudsen-layer jump relations evaluated at `Ma=1`;
- a mass flux and recoil pressure derived from the same sonic jump state;
- chamber-relative net recoil traction for the current pseudo-gas solver;
- evaporative heat flux from `mDot * latentHeatVap`;
- analytical constitutive regression plus one-step CFD coupling smoke test;
- literature-to-code notes in `log/LITERATURE_NOTES.md`.

Scope:
this commit intentionally implements only the strong-evaporation sonic branch.
The full near-vacuum transition/interpolation logic is deferred to Phase 4b.

### Phase-4a first regression correction

CI attempt 1 compiled and passed all pre-existing gates, but the new sonic
analytical comparison exposed a configuration-rounding issue: `foamDictionary`
rewrote a user-configurable gamma to `1.66667`.

The sonic model now fixes `gamma=5/3` in code, matching the monatomic-vapour
assumption of the literature model and eliminating an inappropriate calibration
degree of freedom. No empirical tolerance widening was used.

### Phase-4a verification complete

Final CI run `36514885821`: PASS.

The `knudsenLayerSonic` implementation now passes analytical constitutive
checks and one-step CFD coupling while preserving every Phase 0-3 regression.

Phase 4 remains open: the next sub-phase is the common-atmosphere/transition
solver required to determine the `Ma=0.05` and `Ma=1` temperature thresholds
and implement the source paper's near-vacuum interpolation logic.

### Phase-4a integration

Pull request: #5 — `Phase 4a: sonic Knudsen-layer evaporation model`

Merged into:
`dev/vacuum-solver`

Merge commit:
`6ed0a047f920a583824e484e8427bf3387eec968`

Final verification before merge:
GitHub Actions run `36514885821` — PASS.

The protected `main` branch remains the exact LaserbeamFoam V3.0 baseline.

## 2026-09-29 — Phase 4b transition-state solver started

Branch: `feat/near-vacuum-transition`

Added:
- reusable `knudsenTransitionRelations` scalar constitutive helper;
- exact Knudsen-layer jump-state evaluation for arbitrary `0 < Ma <= 1`;
- analytical reduction of Eq. (17) to the physical shock Mach number;
- logarithmic Eq. (16) residual;
- bounded bisection for `Ma(Te)`;
- bounded bisection for threshold temperature at target Ma;
- dedicated `knudsenTransitionTest` utility;
- round-trip regression at Ma = 0.05, 0.5, and 1.0.

This is transition-state infrastructure only. It does not yet change the
production evaporation model selected by the solver.

### Phase-4 literature equation correction

A pre-Phase-4c source audit identified an Eq. (10) transcription error in the
initial sonic/transition implementation. The correction changes the
`sqrt(T3/Te)` evaluation and the normalized mass-flux expression, and updates
all independent regression constants. This is a physics correction, not a
tolerance adjustment. The prior successful Phase-4a regression remains in the
record as evidence of the original implementation state.

## 2026-09-29 — Phase 4c near-vacuum production model

Branch: `feat/near-vacuum-model`

Added:
- runtime-selectable `nearVacuumWang` model;
- pressure-dependent boiling temperature;
- automatic `Tk0`/`Tk1` determination;
- cell-wise transition `Ma(T)` solution between the active temperature and
  the sonic threshold;
- sonic branch above `Tk1`;
- explicit refusal of unsupported `Ma<0.05` weak-evaporation configurations;
- synthetic constitutive regression covering sonic, transition, inactive, and
  coupled-CFD paths.

The 0.6 Pa production path now has an explicit near-vacuum model architecture,
but final Ti-6Al-4V material data and experiment validation remain separate
future stages.

### Phase-4c verification complete

GitHub Actions run `36519951799`: PASS.

Every pre-existing regression gate and the new `nearVacuumWang` regression
passed. The branch is ready for integration into `dev/vacuum-solver`.

The corrected Wang Eq. (9)-(13) constants, transition-state infrastructure and
production near-vacuum model are now treated as one verified Phase-4 chain.

## 2026-09-29 — Wang 2020 fast-track alloy extension

Branch: `feat/wang2020-fasttrack`

Implemented:
- generalized the transition residual so callers can supply an arbitrary
  saturation pressure `Pe(T)`;
- extended `nearVacuumWang` with optional multi-component alloy input;
- converted configured mass fractions to the molar fractions required by Wang
  Eq. (18);
- implemented Eqs. (18)-(20) for mixture saturation pressure and
  temperature-dependent vapor molar mass;
- added alloy boiling-temperature and `Tk0/Tk1` bisection using the mixture
  saturation curve;
- retained the previous single-component path unchanged when no component list
  is configured;
- added the two-temperature `wangAlloyMixture` analytical regression and a CI
  gate.

Not yet claimed:
- OpenFOAM-v2512 local validation;
- 304L paper benchmark;
- Ti-6Al-4V production material coefficients;
- composition transport / preferential elemental depletion.

Those items require the subsequent local and CFD validation checkpoints.

## 2026-09-30 — 304L near-vacuum validation implementation

Branch: `feat/wang2020-fasttrack`

Production changes:
- added optional `alloyReferencePressure/alloyReferenceTemperature` scaling for
  multi-component saturation curves while preserving relative vapor composition;
- completed the Wang near-vacuum step-(4) low-Mach branch below `Tk0`;
- added optional clamped-linear metal `cp(T)` and `k(T)` from
  solidus/liquidus tabulated values without changing the default legacy path.

Verification infrastructure:
- added `tests/wang304LReference` with 304L Cr/Ni/Fe composition and
  Table-II saturation-pressure anchor;
- added `tests/wang304LCaseSmoke` for a one-step end-to-end CFD gate;
- added an 8 um setup mesh and 4 um paper-resolution validation mesh;
- added atmosphere-connected centerline keyhole-depth extraction.

A first CI attempt of `wang304LReference` exposed a test-fixture precision
problem: `foamDictionary` rewrote high-precision component latent heats with
reduced output precision. All pre-existing gates passed in that run. The 304L
test was corrected to replace only `testTemperature` with `sed`, preserving
the original thermodynamic constants. This correction changes no production
physics.

## 2026-09-30 — 5 us local-smoke diagnostics

After the local OpenFOAM-v2512 304L constitutive and one-step CFD gates passed,
the validation case was advanced to the 8 um / 5 us short-time physics gate.

Changes:
- `pVap` is now written as an output field;
- added optional `writeDiagnostics` in `vacuumProperties`, defaulting to
  `false` so existing cases and regressions are unchanged;
- when enabled, output times report one compact line containing:
  `Tmax`, `Umax`, `pVapMax`, `QvMax`, and integrated deposited laser
  power;
- the 304L validation case enables these diagnostics;
- `Allrun.smoke` runs 16 MPI ranks to 5 us, collects
  `smokeDiagnostics.log`, and reconstructs the final
  `T/U/alpha.metal/pVap/Qv/Deposition` fields.

The 5 us run is explicitly assigned to the local Ubuntu workstation. No GitHub
CI result is required to advance the project.

## 2026-09-30 — 48-core local-test policy

Per the primary-machine workflow, all current and future full-CFD validation
runs are now configured for 48 MPI ranks.

Updated:
- 304L one-step CFD smoke;
- 304L 8 um / 5 us smoke;
- 304L 4 um paper-reference run;
- smoke/reference decomposition dictionaries;
- validation documentation.

Future local rebuild commands should use `./Allwmake -j 48`.
Pure constitutive utilities remain serial because MPI adds only startup
overhead to those non-CFD checks.

## 2026-09-30 — Wang Ma=0 endpoint/restart fix

A 4 um reference run exposed a low-Mach endpoint failure at
`T=2009.503556 K`, essentially the chamber-pressure boiling point.

The step-(4) solver now includes the exact `Ma=0` endpoint. Wang's jump
relations are regular there:
`T3/Te -> 1`, `P3/Pe -> 1`, mass-flux ratio -> 0, and recoil coefficient -> 1.

The 4 um reference case is now restartable from its latest write, and a
dedicated `Resume_background` helper was added.

## 2026-10-01 — Wang matched-physics gap-closure pass

Implemented after the first 4 um reference produced a robust
32-to-136 um growth interval of 93.88 us versus about 75 us in Wang's current
model.

### Optical closure
- preserved the original LaserbeamFoam Drude/resistivity Fresnel path as
  `opticalModel drudeResistivity`;
- added `opticalModel fixedComplexIndex`;
- the fixed-index path evaluates standard unpolarised complex Fresnel
  reflectivity and specular reflection;
- interface-normal sign is removed from the incidence angle instead of using
  the historical 50% absorption fallback;
- the Wang 304L case now uses Johnson-Christy Fe values interpolated to
  1070 nm: n=2.961346153846154, k=4.013269230769231;
- the corresponding normal-incidence single-hit absorptivity is about 0.3725.

### Surface radiation
- ported the separately developed `vacuumRadiationModel` into the active
  fast-track branch;
- kept radiation distinct from evaporation heat loss;
- coupled it semi-implicitly in the temperature equation;
- enabled epsilon=0.4 for the Wang 304L validation case.

### Diagnostics
Added output-time quantities for direct physical comparison:
- `interfacePVapMax`;
- integrated recoil-force x/y/z components;
- evaporation heat-loss power;
- radiation heat-loss power;
- VOF interface area;
- existing absorbed/deposited laser power remains reported.

### Test isolation
- added a serial analytical radiation regression;
- added a dedicated 48-rank 8 um / 10 us matched-physics smoke test;
- froze explicit smoke control/mesh dictionaries so the smoke test cannot
  accidentally inherit a locally overwritten 4 um / 140 us reference state;
- the matched smoke copies only `initial`, `constant`, and `system`, so it
  does not copy large local processor/output directories.

Status: **implementation complete, pending local build and smoke validation.**

## 2026-10-02 — Begin 0.6 Pa / powder / moving-laser stage

Created branch `feat/0p6Pa-powder-movingLaser` from the frozen Wang validation
line.

Added:
- 3-D 304L 0.6 Pa moving-powder smoke tutorial;
- 13-sphere deterministic single-layer powder fixture;
- 2 m/s tabulated moving-laser smoke path;
- 20 us / 8 um / 48-rank integration configuration;
- isolated automated smoke gate and status helper.

No evaporation-model coefficients were changed.

Status: **implementation ready for local integration test; not yet PASS.**

## 2026-10-02 — 0.6 Pa moving-powder integration gate passed

The first target-stage integration gate is complete:
- 0.6 Pa constitutive regression PASS;
- explicit 3-D powder geometry PASS;
- moving laser PASS;
- 48-rank CFD PASS through 20 us;
- recoil/evaporation/radiation diagnostics active.

Next stage:
replace the hand-authored 13-sphere fixture with a deterministic,
configuration-driven powder-bed generator that records seed, particle-size
statistics, packing fraction and generated setFields geometry. Then extend the
domain/path into a reproducible moving single-track case.

No validated Wang evaporation coefficients are changed.

## 2026-10-02 — Add reproducible powder-bed infrastructure

Added `tools/powderBed/generatePowderBed.py` with:
- seeded deterministic generation;
- uniform or truncated-lognormal diameter sampling;
- vertical contact settling;
- overlap validation;
- layer-thickness rejection;
- exact particle CSV;
- powder manifest with PSD/packing statistics;
- generated OpenFOAM setFields geometry.

Added a frozen generator regression and a second 48-rank 0.6 Pa
moving-laser smoke using a generated 56-particle bed.

Status: implementation complete; local T11a/T11b validation pending.

## 2026-10-02 — Wang validation line closed for paper documentation

Project decision:
the Wang-type near-vacuum evaporation-model development and the 304L
0.0002-atm stationary-laser validation are complete and frozen as
`Wang 304L matched validation v1`.

Scope of this closure:
- constitutive Wang/Knudsen transition implementation;
- Cr/Ni/Fe alloy extension and 304L anchor;
- Ma=0 boiling-endpoint handling;
- VOF recoil/evaporation coupling;
- Fe fixed-complex-index Fresnel alignment;
- grey-body radiation;
- 4 um / 48-rank / 140 us benchmark;
- connected-3D keyhole-depth validation;
- reconstructed keyhole-surface recoil/load diagnostics.

Primary final metrics:
- 32-to-136 um connected-3D growth interval: 76.23 us;
- Wang current-model reference: about 75 us;
- x-ray reference: about 70 us;
- full surface pressure-load integral at the equivalent comparison stage:
  about 3.52 mN versus Wang about 4 mN;
- time-history peak full pressure-load integral: 4.70 mN.

The single hottest reconstructed recoil-pressure face remains an OPEN
mesh/interpolation sensitivity metric and is not a reason to retune the model.

This closure validates the project-relevant 304L near-vacuum case. It is not a
claim that every Ti-6Al-4V/common-atmosphere/scanning case in Wang et al. has
been independently reproduced.

A paper-oriented summary/figure package is maintained separately from the
production physics code.

## 2026-10-03 — Project review, moving-metric freeze and roadmap reset

The project was reviewed while the strict 8 um / 4 um moving-powder resolution
pair was running.

Completed since the previous roadmap snapshot:
- Wang 304L matched validation v1 frozen;
- 0.6 Pa constitutive gate passed;
- explicit moving-powder integration passed;
- deterministic powder generator passed;
- 300-us / 600-um / 48-rank engineering long-track completed;
- moving-keyhole trailing-window sensitivity completed;
- 120-um trailing window frozen as the formal moving-keyhole metric.

The original DEVELOPMENT_PLAN had become stale because it still described the
Wang near-vacuum and radiation phases as incomplete. It was replaced with a
milestone-based roadmap aligned with the actual project state.

Added:
- PROJECT_STATUS.md for a concise current-state snapshot;
- PAPER_AND_REPORTING_PLAN.md to treat manuscript/figure/reproducibility work as
  a formal parallel workstream;
- updated log/README.md navigation.

Current running milestone:
- strict matched 8 um versus 4 um moving-powder resolution pair.

Immediate decision after that pair:
- define production mesh policy before further experimental-parameter runs.

Physics extensions such as explicit evaporation mass removal, preferential
composition evolution and rarefied plume coupling remain conditional. They are
not introduced simply because the base solver can support more complexity.
