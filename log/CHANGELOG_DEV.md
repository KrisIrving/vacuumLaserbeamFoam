# Development changelog

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
