# Laser internal cost probe

Run from the Ubuntu repository root after pulling feat/m247-material-port:

```bash
./tests/m247Performance/RunLaserProfile
```

This command builds liblaserHeatSource and cleanly recompiles vacuumLaserbeamFoam
because the laser class layout changed. Build failures stop the pipeline before
CFD. The laser lnInclude directory is explicitly refreshed and the new
laserPerformance.H link checked before compilation, including on incremental
builds with an existing lnInclude directory. Build failures and
logs/environment are automatically packaged. Static preflight verifies
solver markers, both schema-2 profiling markers, and ldd's resolved laser library
against FOAM_USER_LIBBIN. The source case is copied and never edited.

Two fresh 180–180.2-us/48-rank cases differ only in
LaserProperties/laserPerformanceDiagnostics. Both disable ray-path recording
and phase blending, use bounded enthalpy, tight epsilon1/phase residual limits
1e-5/0.001 K, and matched ASCII outputs. Each solver job has a 15-minute wall
budget; build and copy time are additional. The automatic review archive holds
logs, dictionaries, build/preflight reports, laserProfileReview.json,
laserExchangeDetails.csv and laserRankWork.csv. Default archives are named
M247_laser-exchange-YYYYMMDD-HHMMSS_review.tar.gz to distinguish this stage.

The regression gate checks identical binary/library/source provenance,
complete time coverage, thermal convergence, common-time physical diagnostics
(rtol1e-8/atol1e-12) and final T/epsilon1/alpha/U/p_rgh fields (max norm tolerance
1e-12+1e-8 times reference field maximum). It records profiling overhead.
This validates instrumentation equivalence, not physical production acceptance.

## Timing and counters

* seedGenerate: local ray starting points and powers.
* seedExchange: initial gather and broadcast.
* seedLocate: concatenation, ray construction and initial mesh.findCell calls.
* ownership: replicated global-ray checks, findLocalCell and local list creation.
* trace: local advances, searches, absorption/reflection and deposition.
* exchange: outgoing list copy, combineGather and broadcast.
* finalize: deposited-power integration and output.
* other: remaining inner-call work, including setup and optional path history.

The profiler covers inner per-laser calls and aggregates all lasers since the
last report. It excludes outer field reset/dictionary work and its own report
reductions; the existing solver's laser timer includes these. Reductions occur
only at write times. MPI mean stages are additive; independent rank maxima
must never be added to estimate a critical path. Report maxima of whole inner
calls separately. Waiting can contribute to exchange/ownership timing.

Schema 2 adds exchangeCopy, gather and broadcast timings inside exchange.
Merge timing wraps the existing combineRayLists hash/append operation, including
hash-set destruction, and is a subset of gather: do not add merge to the three
exchange children. Blocking gather and broadcast include waiting; they cannot
be interpreted as pure transport or removable overhead. Merge counters record
invocations, input X/Y list lengths and appended rays, not transmitted bytes.

At each report a small collective gathers per-rank trace/ownership/exchange
and nested timings plus trace/merge work counters. The master emits one
LASER_RANK_DIAGNOSTICS row per rank. The collector checks complete rank groups,
mean/max agreement and counter sums before writing reports, including multiple
reports at the same physical time. Logs retain intervals; laserRankWork.csv
contains totals per rank. No per-ray-round profiling collective is added.
Counters use 15 significant digits; normal log precision is restored afterward.

Counts distinguish replicated calls/initial rays/exchange rounds (rank means)
from local ownership checks, trace segments, advances, interface/bulk events
and searches (rank sums). Repeated initial rays across updates are counted
again, not unique trajectories or transmitted bytes.

One in every 128 local trace searches is timed, starting with the first on each
rank/report interval. This sample is part of trace time. It is neither a separate
additive stage nor an unbiased full-search estimate. Cheap counter/timer work
still incurs overhead; compare the two jobs before interpreting fractions.
No ray count, path, absorption, search algorithm, update cadence or physics
coefficient is changed. The earlier schema-1 pair passed equivalence, but Ubuntu
compilation and regression/cost results for schema 2 remain pending.
Next optimization will be selected from these measurements.
