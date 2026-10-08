# Experimental full-solver moving-window pilot

The protected frozen prototype164709 passed. The next stage runs the actual
vacuumLaserbeamFoam isoAdvector, pressure, momentum and thermal equations with
an opt-in m247MovingRefineFvMesh. It tests compatibility, not measured speedup.

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunMovingCFDPilot
```

Default prerequisite: runs/moving-window-protected-20261008-164709. The script
revalidates its raw protected topology log and source hashes, then copies the
ORIGINAL audited coarse180us case. Mesh-only snapshots are not solver restarts.
It rebuilds the solver only; previously built laser/material libraries remain
required. The window follows the existing single laser table, covers full yheight
and192um x/z. One-level refinement and2M global cell cap are retained. Graded
shoulder cells at level1 are not all4um. Static cases do not select this mesh.

Hot metal (alpha>1e-6,T>=1537K or epsilon>=1e-4) activates a mapped/written wake
hold field; cold solid cells release below1487K and epsilon<=1e-6. The50K buffer
is an experimental numerical policy. Releasing cooled material prevents permanent
accumulation of all historic hot cells, but needs later cooling/hysteresis study.

The pilot advances180..180.2us on48ranks. Its first topology change exercises full
registered fields, geometric VOF mapping and phi reconstruction/CorrectPhi.
The laser moves only0.2um: large window translations/coarsening were tested by
the frozen prototype; this pilot cannot establish meaningful transient movement
or cooling behavior. Initial refinement adds startup cost, so it cannot establish
steady moving-window acceleration. A matched fixed/moving CFD pair follows only
once compatibility and state-transfer checks pass.

Every topology call reports material volume and rho*(cp*T+L*epsilon) before/after
RAW field mapping (before isoAdvector subsequently remaps alpha). The latter is
a screening proxy, not integral thermodynamic enthalpy with temperature-dependent
cp. No energy correction is implemented. Relative drift>1e-6 or uncovered held
wake stops the native solver; this does not prove full-step energy conservation.
Final-step records include alpha/epsilon bounds,T/U finiteness and phi divergence.
Collector requires all per-step records and final time, converged thermal iterations
with no limit hits, and divL1<=0.05/s,divMax<=15000/s continuity screens. These are
pilot gates, not production tolerances. No production approval is issued.

Solver budget15minutes plus graceful checkpoint-stop allowance; native command
budget30minutes includes decomposition. Compilation/copying/hashing are extra.
Writes full decomposed fields twice; allow severalGB disk headroom. Reports,
binary hashes, dictionaries, full solver log and failure evidence are bundled:
`tests/m247Performance/runs/M247_moving-cfd-pilot-<timestamp>_review.tar.gz`.
Send that single archive on success or failure.

124Python tests and shell checks do not establish native OpenFOAM runtime:
the changed C++ build and48-rank pilot are pending Ubuntu. Check log/M247_ERROR_REGISTER.md
for closed prototype issues and the separate pending solver integration.

Solver launch reserves240s within the shared command deadline for writeNow/MPI
shutdown; the15minute solver budget is shortened if decomposition consumes most
of the shared budget. No solver starts when that reserve cannot be met. Rebuild
and launched solver hashes must match. Wake hold is initialized at the restart
time before the first time increment, so saved hold state can be read correctly.

Pilot startup deltaT1ns, maxDeltaT5ns and maxCo/maxAlphaCo0.1 avoid taking
a coarse-grid-sized first timestep across the initial refinement. These conservative
compatibility settings are not a production speed benchmark.


## 2026-10-08: completed native moving-CFD pilot; recollect without rerun

Archive moving-cfd-pilot-20261008-172613 confirms native build and all40 steps
completed180-180.2us in384.4038s. Wrapper failure is MW05: missing thermal
metadata in the Python collector, not a solver failure. Original fvSolution
explicitly sets epsilonTolerance1e-5 and phaseTemperatureTolerance0.001K.
Complete collection against the actual diagnostic fixture passes all pilot screens:
no thermal limit hits; wakeMissed0; maximum thermal mapping proxy relative drift
7.383e-14; maximum divL1=0.019312/s. This is not production approval.

After pulling feat/m247-material-port, run:
```bash
./tests/m247Performance/RunMovingCFDPilot --resume
```
Default input is runs/moving-cfd-pilot-20261008-172613. The original run directory,
original automatic review archive and hash-checked original coarse source must
remain available. Resume verifies archived critical input hashes, reads explicit
thermal controls, copies small review inputs into a fresh collection directory,
and does not build/decompose/advance CFD. Send its automatically named
M247_moving-cfd-collection-<timestamp>_review.tar.gz. Never overwrite old evidence.

127Python tests pass, including complete actual40-step collection and end-to-end
read-only resume/package regression; Bash syntax passes. Ubuntu recollection is
pending. Future runs write required tolerances before launching CFD.

Cost remains1922s/us under conservative5ns maximum steps, with40 mesh changes.
Timing shares: thermal32.54%, alpha30.95% (includes mesh update and VOF), laser23.19%,
pressure8.69%. These are not a matched speedup comparison. Next acceleration work
must separately measure mesh-update cost and evaluate amortized refinement with
protected wake/window coverage before equivalent-physics comparisons. No24h
4um or full-track feasibility claim is justified by this short pilot.


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


## 2026-10-08 180928: mesh timing confirmed; optional timestep pilot

Native compile/run and all pilot gates pass.40 steps in380.398s job wall;
loop378.642s. Mesh update rank-max sum59.66194s (15.76% loop), native topology
52.41626s, preparation7.17092s. Stage rank maxima are not additive. Thermal35.36%,
laser22.13%, enclosing alpha29.31%. No justified speedup claim versus prior runs.
Even eliminating measured mesh update alone would ideally yield only1.187x,
ignoring effects on other work; cannot meet the full-track goal alone.

Next bounded experiment after pull:
```bash
./tests/m247Performance/RunMovingCFDPilot --dt10
```
Writes runs/moving-cfd-dt10-<timestamp> and automatically packages
M247_moving-cfd-dt10-<timestamp>_review.tar.gz. Same0.2us, same protected initial
state/physics/48 ranks, startup1ns, maxCo/maxAlphaCo0.1 and full thermal/coverage/
mapping/continuity gates; only maximum timestep changes5ns to10ns. Adaptive CFL
may still keep actual steps below10ns. Default invocation retains5ns; resume is
unchanged.15minute solver budget remains. New-run metadata recordsmax_delta_ns.
This is timestep sensitivity screening, not a matched equivalence or production
approval. Review end states/physical diagnostics against180928 and, if needed,
full spatial fields before accepting larger steps.129 local Python tests pass;
Ubuntu10ns run pending. No native C++ change in this update.
