# 2026-10-07 — M247 performance phase 1

User priority: make full-track cost affordable before committing to another
expensive mesh study. Development/upload is performed here; OpenFOAM compilation
and runtime validation will be performed by the user on Ubuntu.

Base checkpoint: f91222cad956a5f02a5720ed0e3571ddcbaf1b37.
Original 200-us result: 6e61eba527a19a37cdb647487a040f062154f1c4.

The result archive confirms 13816 steps and true ClockTime105132 s=29.2033 h.
100–200 us alone costs18.3986 h; the last10 us costs2.1611 h. The original
Status wall figure105042.4 s is ExecutionTime, a small0.085% discrepancy.

Implemented:
- default-compatible recordRayPaths option, removing optional trajectory
  allocation/copy/MPI history payload and VTK output when explicitly disabled;
- schema-2 profiling with MPI mean/max, I/O and diagnostic sections, thermal
  corrector totals and cap hits; clocks/reductions disabled when profiling off;
- independent mature-state180–182 us baseline/noRayPaths pair with source
  snapshot hash, budget-controlled runner and strict common-time diagnostics;
- optional thermal residual-log suppression, independently testable;
- Allwmake pipeline failures now propagate; v2512 is listed as supported.

Known interpretation limits:
- ray equality includes path history, so the disabled-history mode needs the
  paired numerical regression, not just a claim that visualization is harmless;
- timing section maxima are not additive; sum of interval rank-max totals is
  a loop-time proxy, actual job wall time is recorded separately;
- short diagnostic equivalence does not replace full-field/morphology checks;
- two1-us field output intervals expose I/O costs but differ from10-us
  production output frequency;
- no speedup is measured or claimed yet; physical equations/tolerances are
  not intentionally retuned, and optimization remains opt-in.

Verified locally:14 Python tests cover positive/negative comparisons, timing
accounting, incomplete/budget-stopped runs, phase-state requirements, source
preservation, no overwrite, and laser-table bounds. Bash syntax and diff checks
pass. OpenFOAM/MPI build/run remains unverified in this Windows environment.

Next action: follow tests/m247Performance/README.md on Ubuntu; send comparison
JSON/CSV and both logs. Use measured fractions to select the next optimization.
