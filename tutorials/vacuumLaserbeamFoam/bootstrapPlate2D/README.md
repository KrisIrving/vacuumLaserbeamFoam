# bootstrapPlate2D

This is a Phase-1 smoke-test case for `vacuumLaserbeamFoam`.

It is copied from the LaserbeamFoam V3.0 `laserbeamFoam/Plate2D` tutorial and
changes only the solver executable/application name.

**Important:** this case does not yet represent 0.6 Pa vacuum physics. Its role
is to prove that the new parallel solver can run the same baseline equations
before vacuum-specific models are introduced.

For a full run:

```bash
./Allclean
./Allrun
```

In repository CI, `tutorials/Alltest` shortens tutorials to a minimal smoke
run, so this case also verifies that `vacuumLaserbeamFoam` can start and
advance the baseline problem.
