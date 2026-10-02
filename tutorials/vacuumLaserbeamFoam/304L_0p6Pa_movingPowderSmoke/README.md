# 304L / 0.6 Pa moving-laser powder integration smoke

This case is the first integration gate after freezing the Wang-304L matched
validation v1.

It deliberately changes only the new-stage ingredients:

- chamber pressure: **0.6 Pa**;
- moving laser: **2 m/s in +x** for the smoke path;
- deterministic single-layer powder fixture;
- 48 MPI ranks.

It retains the validated 304L material, nearVacuumWang evaporation closure,
260 W / 100 um laser, Fe fixed-complex-index Fresnel optics and epsilon=0.4
radiation model.

## Important scope

This case is **not** a physical 0.6 Pa LPBF validation case yet.

The 2 m/s scan speed and 20 um monodisperse powder radius are engineering
smoke parameters chosen to exercise moving-source + powder + low-pressure
coupling on the existing 8 um mesh. They must not be reported as experimental
inputs.

The legacy LaserbeamFoam `PowderSim` switch is not used for physics here.
Current source inspection shows it is read into `powderSim_` but not consumed
later. Powder interaction is instead represented by the actual
`alpha.metal` geometry initialized with `sphereToCell`, which the existing
ray tracer sees directly.

## Geometry

- domain: 320 x 320 x 320 um;
- substrate top: y=200 um;
- powder sphere radius: 20 um;
- powder centres: y=220 um;
- 13 deterministic spheres in three staggered rows;
- smoke mesh: 8 um, 40^3 = 64,000 cells.

## Laser path

The laser travels from x=-40 um to x=0 over 20 us, corresponding to 2 m/s,
with y=319.5 um and z=0.

## Run

```bash
./Allclean
./Allrun
```

Acceptance is numerical/integration only:
- OpenFOAM-v2512 accepts the sphereToCell powder setup;
- 48-rank solver reaches 20 us;
- multiple laser positions appear in the log;
- deposited power remains finite and non-zero;
- 0.6 Pa nearVacuumWang recoil/evaporation activates;
- no Fatal/NaN/Inf occurs.
