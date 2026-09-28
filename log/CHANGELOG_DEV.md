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
