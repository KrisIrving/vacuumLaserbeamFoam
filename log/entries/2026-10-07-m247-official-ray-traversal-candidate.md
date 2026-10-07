# Official ray-tracing review and equivalent traversal candidate

Official sources checked on 2026-10-07:

- V3.0 release notes: https://github.com/laserbeamfoam/LaserbeamFoam/releases/tag/V3.0
- V3.0 implementation: https://github.com/laserbeamfoam/LaserbeamFoam/blob/V3.0/src/laserHeatSource/laserHeatSource.C
- V3.1 release notes: https://github.com/laserbeamfoam/LaserbeamFoam/releases/tag/V3.1
- Reviewed/merged particle implementation PR: https://github.com/laserbeamfoam/LaserbeamFoam/pull/113
- V3.1 implementation: https://github.com/laserbeamfoam/LaserbeamFoam/blob/V3.1/src/laserHeatSource/laserHeatSource.C
- Website overview: https://laserbeamfoam.com/solvers/laserbeamFoam/documentation.html

V3.0 documents radial/polar discretization independent of mesh resolution and
batched MPI ray exchange using compactRay. Our inherited implementation is
consistent with that architecture. V3.1 and PR113 replace compactRay tracing
with laserRayParticle/cloud machinery. This upstream work is a useful larger
upgrade path, but its reported gains are not M247-specific benchmarks and do
not establish our achievable speedup. Website overview material is less specific
than tagged source for distinguishing versions; use tagged implementations.

The current M247 fork additionally contains fixedComplexIndex/Drude optical
choices and vacuum/thermal diagnostics. A particle-backend port needs explicit
comparison of sampled ray positions, absorbed power, reflection, termination,
process transfer and source accumulation, plus compatibility with v2512.
It is not a drop-in proven replacement for the validated checkpoint.

The next implemented candidate is default-off cachedRayTraversal: lazily cache
the existing per-cell iterator distance for each update, and replace temporary
linked-list search queues with a reusable FIFO and checked set. The same
containment calls occur in the same order, including duplicate queue entries,
limit off-by-one behavior and fallback. The original function remains available
as reference and for debug logging. Cell ownership, sampling, physics and MPI
exchange are unchanged. This targets repeated tracing work; it does not resolve
spatial imbalance by itself, and its net benefit is unmeasured.

RunRayTraversal builds and runs a real-mesh old/new lookup comparison before
the paired CFD benchmark. Cases rayTraversalReference/rayTraversalCached differ
only in cache mode and run 180–180.2 us on the original decomposed checkpoint.
The collector compares eight final fields including local laser deposition and
ray diagnostics, identical ray-work counters, thermal convergence and physical
diagnostics. Profiles on both sides show any change to trace and collective
waiting. Performance threshold is >=5% improvement in both job and loop; no
production approval is inferred. No ray-count or update-frequency reduction.

51 local Python tests and Bash syntax pass. Actual OpenFOAM build, real-mesh
parity and paired CFD/cost results remain pending Ubuntu. See
tests/m247Performance/RAY_TRAVERSAL.md for the one-command test and archive.

After review, retain a candidate only if equivalent and useful. If the cost gain
is small, prioritize tracing-aware partitioning or a separately benchmarked
V3.1 particle backend rather than more profiling-only runs.
