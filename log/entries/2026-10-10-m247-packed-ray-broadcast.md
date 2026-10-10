## 2026-10-10: opt-in packed optical broadcast and gated full pair

Next implementation after failed lagged optics and ineffective thermal cache:
packedRayBroadcast(defaultfalse), preserving every-step optical updates.
Only final per-wave Pstream broadcast representation changes; combineGather
and ray ordering, stepping/absorption/handoff/termination are unchanged.
Seven scalar values+three labels+two byte flags copied individually with
memcpy to List<char>, broadcastList and exact reconstruction. No raw copying
of polymorphic compactRay, pointers or padding; no conversion of label to scalar.
Requires recordRayPaths false and rejects nonempty paths. Overflow/truncation/
invalid flag guards. Homogeneous scalar/label ABI as native contiguous MPI
transfers, not a portable file format. Empty arrays explicitly supported.

Native m247RayWireCheck exercises0,1,7,1536ray messages on48ranks including
signed zero/scalar extrema/label limits/flags; checks field and byte roundtrip.
RunPackedRayPair rebuilds changed library/dependent solver/checker with official
wmakeLnInclude/wmake only; no wclean/timeouts/kill. Gates library feature marker
and MPI checker before any optical/CFD work. Both frozen180us optical jobs
finish before BOTH transient jobs; identical input fields, Deposition/rayQ,
deposited power and optical work counts required. No time or T/alpha/epsilon/U
advancement permitted during frozen trace. Failure packages archive and stops.
Then full756k180..190us48rank matched-initial/partition10us pair automatically.
Baseline old stream broadcast vs packed candidate; both every-step optics and
thermal cachefalse. Strict sampled field/physical diagnostic/corrector/optical
work equality required; completion is not a production approval.

Package includes all wire/frozen logs even if incomplete; variant names explicit.
Local40tests(39pass,1Windows symlink skip),Python compilation and Bash syntax
pass. Native OpenFOAM/MPI compilation and performance cannot be checked here.
No measured benefit yet. This does not route rays to owners or balance optical
work; blocking broadcast cost still includes imbalance wait. Serialization
change might save little/nothing; do not claim it solves major scaling cost.
Long-track/local-global coupled solution remains outstanding.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunPackedRayPair
Send one M247_packed-ray-pair-<timestamp>_review.tar.gz, even if failed.
Details: tests/m247Performance/PACKED_RAYS.md.

