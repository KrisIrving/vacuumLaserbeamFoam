# M247 1.5 mm pilot review and pressure restart pair

The 20261012-105416 pilot completed 0--50 us in 10852.47 s (3.0146 h),
4198 steps, 48 ranks, 4,232,448 cells. Manifest file hashes all match.
Mesh OK: nonorthogonality 0, maximum aspect ratio 6.075, no topology errors.

Timing: pressure50.44%, thermal16.51%, momentum9.94%, laser9.90%,
alpha7.42%, properties5.13%. Thermal correctors mean3.13, maximum6,
no150-corrector limit hits. All4198 nonlinear epsilon/phase-temperature
checks satisfy1e-4/0.01K. Pressure performs3 solves/step, average28.27
linear iterations/solve, maximum165. Every final pressure solve satisfies1e-7.

At50us connected solidus melt depth105um, width270um, liquidus envelope
width246um. Minimum fine-zone margin39um; no molten metal outside fine
corridor. About6um cell-centre uncertainty; these are instantaneous molten
dimensions, not keyhole depth or final solidified-track dimensions. The
nearest outer z boundary is231um from molten cell centres. No boundary-
sensitivity or384/full-ray accuracy comparison is established by this run.

Tmax4506.65K (interface), metal3472.25K, gas4484.00K; Umax81.79m/s.
Median dt11.76ns, maximum printed Courant0.1548 despite target0.1.
Adaptive control uses previous-step flow; a transient exceedance is reported,
not concealed or equated with fatal instability. Final cumulative continuity
diagnostic3.19e-8 is an OpenFOAM flux diagnostic, not a measured mass-loss fraction.

Startup exception: at1.200048002ns the first T linear solve reached1000
iterations, final residual7.9338294e-9 versus1e-9 requested. No further T
linear failures appeared. Nonlinear thermal convergence does not prove all
linear solves converged. A mature restart cannot validate this startup.

At observed rate,1500us heating projects90.44h plus cooling; this is not a
reliable full-track ETA. Pressure-only optimisation has an ideal maximum
speedup1/(1-0.5044)=2.02 even if pressure cost vanished, so it alone cannot
establish a24h full-track run. Further mesh/time-step changes would need
their own physical evidence after the principal pressure bottleneck is measured.

Run a matched50--60us pair, retaining the completed pilot:

```bash
git pull --ff-only
bash tests/m247Performance/RunM247PressurePair tests/m247Performance/runs/m247-track1500-pilot-20261012-105416/track1500
```

pressurePCG preserves original PCG/DIC. pressureGAMG changes only the
p_rgh/p_rghFinal dictionaries to standard GAMG/GaussSeidel, cached faceAreaPair
agglomeration,10 coarsest cells, mergeLevels1. Pressure tolerance1e-7,
normal relTol0.05/final0,3 correction loops, Co controls, thermal iteration
and aligned384 rays remain unchanged. This follows standard OpenFOAM
configuration, not a new custom pressure algorithm:
https://doc.openfoam.com/2212/tools/processing/numerics/solvers/multigrid/rtm/GAMG/
https://www.openfoam.com/documentation/user-guide/6-solving/6.3-solution-and-algorithm-control

Two fresh copies use the same saved partition/50us fields; their pre-edit
input snapshot hashes must match. No remeshing, redecomposition, source
modification, deletion, forced stop or timeout. Rebuild/preflight preserves
binary hashes. Each variant writes55/60us states; official reconstructPar
and postProcess export alpha/T/cell centres for exact-time geometry checks.
Parallel checkpoints and large ASCII geometry exports remain on Ubuntu.
Allow additional disk space for two copied mesh/restart sets and exports.

Recommendation requires both samples' melt depth/width differences<=5%,
both runs' nonlinear thermal and linear pressure/T convergence, molten metal
remaining in fine corridor with>=12um margin, and measured job speedup>1.05.
Continuity, temperatures and recoil are reported. No extra temperature/recoil
rejection threshold is introduced. Passing only recommends longer continuation;
it does not approve final1.5mm physical accuracy or guarantee runtime.

Send ONE M247_m247-pressure-pair-TIMESTAMP_review.tar.gz, including on
failure. Manifest distinguishes missing outputs from a completed pair.
Build, preparation, solver and extraction logs are retained per variant.
Collection-only recovery (after geometrySamples.json exists):

```bash
python3 tests/m247Performance/track_pressure_pair.py --work tests/m247Performance/runs/m247-pressure-pair-TIMESTAMP --collect
python3 tests/m247Performance/track_pressure_pair.py --work tests/m247Performance/runs/m247-pressure-pair-TIMESTAMP --package
```
