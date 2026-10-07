# Broader cache validation passes; add Cartesian seed interior candidate

Reviewed M247_ray-traversal-validation-20261007-201432_review.tar.gz. All29
manifest hashes/sizes verify,exit0,no missing entries. Both jobs complete166
steps across180–182us;14.319277correctors/step,max18,no cap. Independent parsing
reconciles thermal convergence,two diagnostic times,interval profiling and
96rank rows,with identical global and per-rank work. Seven final fields over
756000cells have zero max/RMS differences in the archived Ubuntu norm report;
raw fields are not archived,so this is not local field recomputation.

Reference/cached job times400.406486/334.346662seconds,1.197579x. Loop sums
398.868081/333.022396seconds,1.197721x. Candidate laser54.77%,thermal30.54%,
pressure8.12%,momentum2.89%,alpha2.40%. Trace max/mean13.5319 remains imbalanced.
Opt-in cache is validated at this8-um mature state; defaults and physical/full
track approval remain unchanged. Do not rerun this completed pair.

Added default-off cartesianRaySeedSearch,requiring cachedRayTraversal. Bounds
derived from six exactly axis-aligned face-area vectors replace only affirmative
strict-interior seed checks. Ambiguous/unsupported points fall back unchanged.
Geometry and margins rebuild each laser call; no changed optics,step sequence,
deposition or MPI routing. Expanded real-mesh search parity before CFD,including
vertices and both face sides; require eligible cells and actual shortcut usage.

RunRaySeedSearch compares validated cache vs cache+seed shortcut for2us with
30-minute/job budget,automatic compile/checks and one tagged review archive.
59 Python tests pass,including variant isolation,runtime modes,unexercised
shortcut rejection and stale library markers. Bash syntax passes. OpenFOAM
build/parity/CFD and actual new gain remain pending Ubuntu. No local compiler.

Next broader architecture remains fixed local fine mesh and a separately
validated fixed thermal/fluid coupling prototype,then moving window. This
candidate can provide near-term gain but is not a replacement for domain-size
reduction needed by1.5–2mm tracks.
