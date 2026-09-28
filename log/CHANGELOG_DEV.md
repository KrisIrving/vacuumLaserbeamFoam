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
