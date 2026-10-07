# Cartesian seed-cell shortcut

The previous180–182-us cache pair passed:29manifest entries verified,
seven756000-cell fields have zero differences in the Ubuntu comparison report,
166steps,14.319thermal correctors/step,max18,no caps. Independently rechecked
global/rank ray work and thermal/physical diagnostics match. Job400.4065s vs
334.3467s,1.19758x; loop1.19772x. Tracing max/mean remains13.53.

Next Ubuntu command from repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunRaySeedSearch
```

Automatic library/clean solver/search-test build, runtime-loaded library marker
preflight, real-mesh legacy/cached/shortcut search parity, then two independent
180–182-us checkpoint copies. Both variants retain validated cachedRayTraversal,
tight bounded enthalpy,width zero,original ray resolution and ray paths off.
Only raySeedCached enables cartesianRaySeedSearch.30-minute budget per job;
build/copy and saved-stop/termination grace are extra. Original case is unchanged.

Send the printed M247_ray-seed-search-..._review.tar.gz, also on failure.
It includes build/preflight/search/collection logs and both variant reports.
Seven final fields, identical interval and rank ray counts, physical/thermal
diagnostics and>=5% loop/job gain remain required. Production remains unapproved.

Algorithm: per laser update identify cells with exactly six face-area vectors
aligned with coordinate axes (one positive and one negative per axis). Cache
their face-plane lower/upper coordinates and a precomputed roundoff margin.
Strict interior points in the original seed return that seed directly. Exact
faces/vertices,near-boundary points,invalid seeds and every unqualified cell
fall back to existing cached search. No face-crossing shortcut,changed step,
different neighbour order or reduced ray resolution. Debug uses legacy search.
Rebuild geometry each call; no cross-update cache lifetime assumption.

Real-mesh parity now samples cell centres,wrong/invalid seeds,outside points,
face centres,vertices and offsets to both sides of faces under limits0,1,100.
Collector requires positive Cartesian checks,eligible cells and fast accepts,
so a test that never exercises the shortcut cannot pass this candidate review.
Binary preflight and runtime modes reject old libraries before acceptance.

59 Python harness tests and Bash syntax checks pass locally. No local OpenFOAM
compiler is available; C++ compilation,mesh parity and speed are pending Ubuntu.
This targets seed-containment work on the busiest ranks. It does not remove
tracing imbalance or establish full-track/fine-grid affordability. In parallel
with subsequent architecture work, retain the planned fixed local4-um mesh,
then fixed thermal/fluid coupling prototype before a moving full-track window.
