
## 2026-10-08 175027: native collection confirmed; mesh-cost profile next

User collection archive has12 files with verified sizes/SHA256, wrapper exit0,
no missing files. complete/pilot/thermal/source-unchanged gates pass.
collection_only and no_cfd_advanced are true. MW05 collection repair is confirmed
on Ubuntu; no original CFD rerun occurred. Production approval remains false.

Next command after pulling feat/m247-material-port:
```bash
./tests/m247Performance/RunMovingCFDPilot
```
This rebuilds the solver and repeats the bounded0.2us pilot from protected164709
source with independent mesh-cost timing. It does not change refinement frequency,
physics, convergence tolerances or timestep controls. Send the automatically named
M247_moving-cfd-pilot-<timestamp>_review.tar.gz. Fifteen-minute solver budget still
applies; build/copy/hash/decomposition time is additional.

M247_MOVING_MESH_COST measures preparation, native dynamicRefineFvMesh update
(including its topology/mapping), post-update audits and total, taking per-call
maximum wall time across MPI ranks. Separate rank maxima need not sum. Timing
excludes its own reductions/output and external isoAdvector remap/CorrectPhi.
The enclosing alpha timer continues to include VOF. Collector requires a complete,
finite, nonnegative cost record for each step in new runs; old read-only resume
accepts historical absence explicitly.128 Python tests pass; new native timer build
and runtime require Ubuntu validation. No acceleration claim yet. Use measured
cost to decide whether update amortization is worthwhile, then require coverage
and matched-physics gates before accepting it.
