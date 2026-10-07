# Cached traversal candidate

Run from the Ubuntu repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunRayTraversal
```

The wrapper refreshes lnInclude, builds the laser library, clean solver and
real-mesh search test. It prepares an independent reference checkpoint copy and
runs m247CachedSearchTest on every rank before CFD. That test compares legacy
and cached lookups at cell centres, exact face centres, outside points and
valid/invalid seeds, with search limits 0, 1 and 100. FIFO storage is reused
across calls. It has a 120-second wall limit and must report zero mismatches.
Build or test failures stop the pipeline and are automatically archived.

The two fresh 180–180.2-us cases differ only in cachedRayTraversal, a default-off
LaserProperties switch. Both retain 1536 rays per call from the source setup,
profile timing, tight bounded enthalpy, phase blend width zero and ray paths
off. Each CFD job has a 15-minute wall budget; builds, copying and the search
test are additional. MPI count is read from the copied checkpoint metadata.

The candidate caches the original (0.5/pi)*pow(V,1/3) expression on first use
per cell per laser update. It neither substitutes cbrt nor changes step size.
Caches are discarded every update, avoiding stale geometry between calls.
A DynamicList FIFO and checked set reuse storage for neighbour searches.
Predicate order, duplicate queue entries, maxLocalSearch cutoff and mesh.findCell
fallback remain unchanged. Debug mode retains the original search/logging path.
Ray generation, initial location, optics, MPI routing and deposition order stay
the same. This is an experimental equivalent optimization, not a V3.1 port.

The collector requires successful search parity, expected runtime mode, matched
source/binary controls and profiles, identical global interval and rank work
counters, per-step thermal convergence and common-time physical diagnostics.
Final mandatory all-rank fields are T, epsilon1, alpha.metal, U, p_rgh, Deposition
and rayQ. The inherited rayNumber visual ID is NO_WRITE without debug; compare
it only when both cases and all ranks have saved it, otherwise explicitly report
not_written. Partially present rayNumber outputs are rejected. Do not turn on
debug to obtain it: debug selects the original lookup path. The norm tolerance
is 1e-12 + 1e-8 times the reference field
maximum. The separate performance gate requires at least 5% improvement in
both loop and job times; a single short pair cannot establish statistical or
full-track speedup. Failure of equivalence stops collection with a failure
archive; failure of the performance threshold is reported without promoting
the candidate. Production approval remains false.

Send the single printed M247_ray-traversal-YYYYMMDD-HHMMSS_review.tar.gz. It
includes build and real-mesh test logs, both variant logs/dictionaries/provenance,
rayTraversalReview.json, field comparison, stage/exchange and rank reports.
The large saved fields remain on Ubuntu. No source-case modification occurs.

Local validation: 53 Python harness tests and Bash syntax checks pass.
The 195231 archive verifies compilation, 50688 real-mesh parity checks with zero
mismatches, identical logged diagnostics/work and shorter cached runtime.
Its initial collector failed because rayNumber was incorrectly mandatory.
The subsequent collection-200224 archive passes saved physical/deposition field
regression: all seven mandatory fields have exactly zero differences over756k
cells; optional rayNumber is explicitly not_written. Both regression and5%
performance gates pass (job1.125x, loop1.1385x). Retain the opt-in candidate;
default remains off and broader validation/production approval remain pending.

The recovery command below has already completed successfully for195231; no
repeat is needed. It remains available for another failed collection without
rebuilding or rerunning CFD:

```bash
./tests/m247Performance/InspectRayTraversal tests/m247Performance/runs/ray-traversal-20261007-195231
```

This reads existing fields, creates comparison reports and a fresh
M247_ray-traversal-20261007-195231_collection-TIMESTAMP_review.tar.gz. Collection
stdout/stderr is archived as collection.log, including errors. Existing
comparison reports are never overwritten.
