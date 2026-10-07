# Next speed step: laser internal profiling

Implemented default-off laserPerformanceDiagnostics, additive MPI mean
substage wall times, independent whole-call/stage maxima and workload counters.
Trace searches are sampled at stride128; sampled time is nested in trace and
is not extrapolated into a claimed exact search total. Aggregates all inner
laser calls and reports only at write times. Disabled mode adds no new MPI
reductions. Numerical ray decisions/arithmetic and physics remain unchanged.

RunLaserProfile builds the library and clean solver object, rejects build
failures/old or shadowed loaded libraries, then runs independent profiling
off/on 180–180.2-us tight bounded cases with width zero and ray paths off.
Collector validates provenance, timing/counters, interval coverage, thermal
convergence, physical diagnostics and final fields. Package includes build
failures and named variants/reports. Production approval remains false.

Local validation:42 Python tests, Bash syntax and diff checks. Full C++ library
and solver compilation require Ubuntu; no speedup or measured substage cost
is claimed yet. Details: tests/m247Performance/LASER_PROFILE.md.
