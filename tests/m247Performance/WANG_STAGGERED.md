#384-ray radial-ring angular staggering candidate

Wang hotspot archive(2) is complete; worst global temperatures are in the VOF
interface, not safely dismissible pseudo-gas maxima.384-ray at54us has6366.4K
versus4975.0K, alpha0.170 vs reference hottest alpha0.665.768 at124us
has4849.0K versus5967.5K, both interface. Largest pointwise differences often
include alpha/geometry changes, so they are not solely temperature errors on
the same material point. No user criterion is relaxed; thermal cap failures
also remain unresolved. Hotspot data does not prove a cause of these errors.

Existing polar sampling aligns all16 radial rings on the same angular spokes.
New optional staggeredAngularSampling rotates ring iR by
deltaTheta*(iR+0.5)/nRadial. Each ring retains its original radius, Gaussian
power/area weights and evenly spaced nAngular rays. No temporal rotation,
source hold, altered Fresnel/reflection/termination, or spatial deposition
smoothing. Hypothesis: better spatial coverage may reduce coherent sampling
hotspots at low counts. This is not an accuracy claim or a256/384/768 sweep.
Default false retains the original theta expression and no extra sampling log.
Only laserHeatSource.C changes; no header/class ABI change or extra include.

One complete384-ray0..140us4um48-rank candidate reuses the existing suite's
prepared mesh/partition/initial hashes and all numerical/physical dictionaries.
Compares with retained1536 and aligned384 full histories. Reference simulation
costs are historical, not a simultaneous/same-binary performance pair; the
default-off implementation preserves prior physical operations.
No full reference rerun or OpenFOAM cleanup. Existing thermal tolerances/cap
and agreed5/5/10% full-history gates remain unchanged. Even if macro errors
improve, nonconverged steps prevent production approval.

```bash
git pull --ff-only origin feat/m247-material-port
bash tests/m247Performance/RunWangStaggered
```

Optional first argument is the existing suite directory; default is
tests/m247Performance/runs/wang-ray-suite-20261011-000847. Physical paths
resolve symlinks. Wrapper runs official wmake libso in src/laserHeatSource,
verifies runtime loading, then runs one mpirun job with48 ranks. Do not run
alongside another48-rank simulation. Previous384 job took3.73h; this is a
rough planning reference, not a guaranteed new runtime.

One M247_wang-staggered-TIMESTAMP_review.tar.gz includes build/preflight,
current candidate logs/dictionaries/CSV/volume/summary/comparison, retained
reference1536/384 logs/summaries, hashes and a manifest. Build or runtime
failure also packages. Ubuntu native build/CFD still pending; mathematical
quadrature invariants and Python collector/failure packaging tests pass locally.

If collection alone fails, preserve fields and reuse offline:

```bash
python3 tests/m247Performance/wang_staggered.py --collect --work tests/m247Performance/runs/wang-staggered-TIMESTAMP
python3 tests/m247Performance/wang_staggered.py --package --work tests/m247Performance/runs/wang-staggered-TIMESTAMP
```
