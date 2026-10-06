# M247 10-us performance probe — 8 um

Purpose: measure where wall time is spent before changing numerical algorithms.

This case uses the same 756k-cell geometry, M247 properties, powder generator,
48-rank decomposition, laser power, speed and optical model as the 200-us
extension case, but runs only 10 us.

The solver prints one PERF_DIAGNOSTICS record at 10 us with accumulated wall
time for:

- alpha / VOF;
- property updates;
- laser ray/deposition update;
- momentum equation;
- nonlinear thermal/phase-change equation;
- pressure correctors;
- other time;
- total thermal-corrector count.

This is a performance benchmark, not a physics-validation result.

Run after rebuilding the instrumented solver:

    ./Preflight
    ./Allrun

Then extract:

    grep '^PERF_DIAGNOSTICS ' log.vacuumLaserbeamFoam

The result decides which optimization is implemented first. Do not retune
physics solely to improve runtime.
