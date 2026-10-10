# Packed optical broadcast experiment

Run from repository root after sourcing OpenFOAM:

```bash
git pull --ff-only origin feat/m247-material-port
bash tests/m247Performance/RunPackedRayPair
```

Default source is the prepared serial full case at
`tests/m247Performance/runs/local-melt-pair-20261009-164947/fullMelt`.
An optional first argument selects another compatible prepared full case;
second argument is wmake jobs(default8). Inputs are copied to a fresh run.
Physical /media and ~/OpenFOAM aliases are resolved before overlap checks.

This replaces only the final per-wave broadcast payload. The combineGather,
ray order, tracing steps, source update frequency, deposition, handoff and
cutoff rules stay on the baseline route. `packedRayBroadcast` is opt-in in
constant/LaserProperties and defaults false. It requires recordRayPaths false;
visual path payloads are never silently discarded. Both test cases disable
visual paths. It is not owner-directed transport or optical load balancing.
Blocking gather/broadcast measurements include wait for imbalanced tracing;
reduced serialization may give a small benefit or none. No speedup claimed.

The native payload consists of seven scalar values(position,direction,power),
three labels(cell,bounces,global ID) and two explicit byte flags. memcpy keeps
scalar/label bits without floating conversion or polymorphic object padding.
Native representation assumes the same homogeneous MPI scalar/label ABI as
OpenFOAM contiguous transfers. This is not a portable persisted file format.
Header rejects non-empty paths, truncated records, invalid flags and overflow.

The wrapper uses official wmakeLnInclude -u and wmake for changed optics,
dependent solver and a native wire checker. No wclean, timeout or forced kill.
The checker exercises empty,1,7,1536ray arrays on48ranks, including signed zero,
large scalar values, label limits and mixed flags; checks bytes and ray fields.
Then two frozen180us jobs compare identical optical inputs, Deposition/rayQ,
positive equal deposited power and equal optical work counts, without CFD.
BOTH frozen checks finish before either transient solver is launched.
If passed, the script automatically runs two180..190us48rank full-domain jobs
with identical initial fields and exact cellProcAddressing hashes. Both use
laserRefreshIntervalSteps1 and thermalInvariantCachefalse. Mid/final fields,
physical diagnostics, thermal iteration counts and optical work counts must
match exactly at sampled times for packed_broadcast_equivalence_gate.
Directory labels fullMelt/localMelt are compatibility names; both are full756k
meshes. No production approval follows simply from completing a run.

Return the single `M247_packed-ray-pair-<timestamp>_review.tar.gz`, including
failures. It contains build/wire/frozen/transient logs and comparison reports.
Expected pair cost roughly one hour from current48rank benchmarks, plus build
and preprocessing; timings are not a guarantee. Native compilation, MPI wire
roundtrip, frozen equivalence and benefit remain Ubuntu checks.

API reference: https://api.openfoam.com/2512/classFoam_1_1Pstream.html
The library already uses Pstream::broadcastList for initial ray arrays. No
custom MPI calls or global communicator/schedule modifications were added.
