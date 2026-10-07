# Broader cached traversal validation

The completed0.2-us pair passes field/work/thermal regression and measured
performance gates (job1.125x, loop1.1385x). It is insufficient evidence for
full-track or fine-grid approval. Extend the matched interval to180–182 us
before changing parallel tracing or porting the upstream particle backend.

Run `./tests/m247Performance/ValidateRayTraversal` after pulling the feature
branch on Ubuntu. It reuses RunRayTraversal with an explicit validation mode:
2-us duration,30-minute wall budget per variant, and a distinct
ray-traversal-validation timestamp directory/archive. Existing source checkpoint
is copied separately for reference and candidate. Build, binary preflight,
real-mesh parity and all existing regression/performance gates remain active.
Budget expiry retains saved-stop/termination grace; build/copy time is extra.
The collector checks both metadata intervals before emitting a validation report.

56 Python tests pass, including accepted2-us data, rejected0.2-us metadata and
rejected non-traversal validation mode. Both shell entrypoints pass Bash syntax
checks. No solver/C++ changes; broader execution and timing remain pending
Ubuntu. Cache remains default-off and production_approved remains false.

The next decision depends on whether seven mandatory fields and ray work stay
matched across2 us, thermal convergence stays within controls, and loop/job
speedup remains at least5%. A pass supports retaining this optimization and
then addressing the observed roughly13x tracing max/mean imbalance. It does
not by itself establish physical model closure or a24-hour4-um cost guarantee.
