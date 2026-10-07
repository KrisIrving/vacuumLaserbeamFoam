# M247 mature-state performance pair

Ubuntu result: the first ray pair measured 1.120x job speedup, but both modes hit the thermal cap in all 166 steps. The next priority is the short nonlinear thermal investigation described in [THERMAL_PROBE.md](THERMAL_PROBE.md), using `RunThermalProbe`. The ray pair below remains available; earlier pending-execution statements describe its original delivery status.

This first performance change targets optional visual ray history. In the
original tracer every ray appends points while travelling; the entire history
is serialized in `compactRay` and carried through MPI gather/broadcast. A
deeper keyhole can therefore increase both history allocation and message
payload. This is a concrete candidate, not a measured bottleneck yet.

`constant/LaserProperties` now accepts `recordRayPaths false`. The default is
`true`, preserving the original trajectory recording and VTK output. The false
mode omits initial/path point appends, master history copies, VTKs and their
series file. It retains ray count, search, position, direction, power, reflection
and deposition calculations and the same gather/broadcast operations.

One subtlety requires an actual CFD comparison: `compactRay` equality includes
the history. Removing history also changes that auxiliary part of duplicate-ray
comparison during list combination. A shared ray ID still participates in
equality, but numerical equivalence must be tested rather than asserted.

## First Ubuntu test

Use the completed original 756k-cell case with all 48 uncollated `processorN`
directories and the complete 180 us state, including `epsilon1`. The source
log must have `End`. The summary tarball is not a restart case.

From your Ubuntu repository root, with OpenFOAM v2512 sourced:

```bash
git pull --ff-only origin feat/m247-material-port
./Allwmake -j 48
python3 -m unittest discover -s tests/m247Performance -p test_tools.py -v
./tests/m247Performance/RunPair
```

If the reference lives in another checkout, pass its absolute case directory:

```bash
./tests/m247Performance/RunPair \
  /home/kris/OpenFOAM/kris-v2512/vacuumLaserbeamFoam-m247/tutorials/vacuumLaserbeamFoam/M247_0p6Pa_powderTrack200us8um
```

`RunPair` creates two fresh independent case copies outside the reference:
baseline followed by noRayPaths, both 180–182 us and 48 ranks. It copies only
constant/system and the required processor mesh/state, including all restart
fields. It does not clean, modify, hard-link, or run inside the original case.
It refuses an existing destination or an interval outside the original laser
tables. Preparation failure leaves a partial directory for inspection; choose
a fresh destination for a retry. The source must remain unchanged during the
pair. A SHA256 of the copied source snapshot is compared between cases.

The two cases keep Co, thermal/pressure settings, optics, material parameters,
particles and output cadence equal. Each writes at 181 and 182 us. This cadence
is more frequent than the original 10-us field cadence; interpret I/O fractions
accordingly. At the measured late reference rate, each 2-us run costs roughly
25–30 minutes, plus restart/copy/write overhead; the pair is expected around
one hour, not guaranteed. Each job has a 2-hour wall budget. A budget stop
requests `stopAt writeNow`, waits up to 180 s, then terminates the process group
if the solver does not respond. A forced stop is not a guaranteed checkpoint.
Any budget stop fails the pair; it is never reported as a passed run.

For a detached launch, capture the printed work directory in the pair log:

```bash
nohup ./tests/m247Performance/RunPair > m247-performance-pair.log 2>&1 &
tail -f m247-performance-pair.log
```

Read/send:
- `runs/<timestamp>/comparison/comparison.json`;
- `runs/<timestamp>/comparison/diagnosticComparison.csv`;
- both `log.vacuumLaserbeamFoam`, `run.json` and `probe.json` files;
- build errors, if compilation fails before the pair starts.

The collector requires a completed requested interval, schema-2 timings, at
least two matching physical samples and equal source snapshots. It checks the
12 existing physical diagnostics with `atol=1e-12`, `rtol=1e-8`, and flags
thermal iteration cap hits. Diagnostic PASS is a short regression gate, not
full-field/grid/long-track validation. Retain the written alpha/T/U fields for
interface/field inspection. Before production, repeat over 10–20 us, examine
keyhole depth/topology and compare the final fields. A speed improvement with a
failed physical comparison must not be adopted.

## Timing schema 2

With `performanceDiagnostics true` in vacuumProperties, timers measure controls,
VOF, properties, laser, momentum, thermal, pressure, history, field writes,
physical diagnostics, ray output, execution logging and residual other time.
Disabled timers do not call the clock or perform MPI reductions.

`<section>_s` is the MPI mean accumulated wall time; the means add to
`stepWall_s`. `<section>Max_s` is an independently reduced maximum over ranks.
Do not sum section maxima: their maxima can occur on different ranks.
`stepWallMax_s` is the maximum accumulated rank time for one reporting interval.
The collector sums these interval maxima, an upper-bound proxy for the loop
time if the slowest rank changes, and also reports the actual subprocess wall
time. The step timers exclude profiler reporting/reductions themselves,
startup, final VTK-series write and shutdown; subprocess wall time includes
those. Section totals can contain MPI waits and are not pure kernel CPU time.

Thermal totals include correctors per step, largest per-equation corrector
count, and equations ending above epsilonTolerance at the existing cap. The
thermal stopping rule and original operation order are retained, including
the existing do/while counter convention.

`MELTING/thermalCorrectorLogging false` is a separate optional output-only
candidate, default true. It suppresses per-corrector residual printing while
retaining calculations and schema-2 counts. Prepare `--variant quietThermal`
to test it against baseline; this variant retains visual ray history so that
only one candidate is tested at a time. It is not part of the default pair.

## Next decision

After Ubuntu measurements, rank the mean section fractions and compare speed
and physical differences. If visual histories dominate, validate noRayPaths
over a longer window. Otherwise work on the measured pressure/thermal/VOF
component, one numerical setting at a time. Full 1.5–2 mm acceleration still
requires a separately validated local-flow/global-thermal architecture;
this patch does not implement that architecture or promise a speed multiplier.

Local verification for this patch covers 14 Python tests, shell syntax and diff
checks. OpenFOAM compilation, MPI execution and physical regression are pending
on the Ubuntu host.
