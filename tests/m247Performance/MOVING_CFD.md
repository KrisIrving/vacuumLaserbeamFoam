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


## 2026-10-08 182248: timestep result and development checkpoint

Both verified archives have matching source fingerprints, protected checkpoint,
solver hash and48 ranks.5ns:40steps/380.398s;10ns:33steps/312.321s; job speedup
1.21797 and17.90% lower job wall. All short-pilot stability screens pass; no caps.
At180.1us Umax differs-6.82%; at180.2us-4.43%. FinalTmax+0.220%, depositedpower
-0.0278%, pVap+0.819%. Diagnostic similarity is not spatial/temporal convergence.
Keep5ns default and10ns experimental; no production approval.

Read-only comparison tool compares existing reports, requires matching provenance
and physical times, and packages a fresh named archive without CFD or mesh writes:
```bash
./tests/m247Performance/CompareMovingSteps
```
Send M247_moving-step-comparison-<timestamp>_review.tar.gz. Defaults select180928
and182248.130 Python tests pass and both real reports were compared locally.

Completed evidence:
-8um200us baseline completed29.18h; keyhole deepens~189 to317um over100-200us,
  no plateau, remaining bottom clearance~136um. Fine full-track budget unresolved.
-Thermal bounded enthalpy iteration addressed150-corrector cap; currentpilot
  mean15.7/max18 and no cap. Phase smoothing is not adopted as an acceleration.
-Ray traversal cache coarse matched test~1.08x; optical handoff/termination fixes
  tested separately; seed/partition experiments did not justify adoption.
-Static local refinement/flux projection validated restart machinery; fine optics
  changes deposited power, so coarse/fine optical equivalence remains unresolved.
-Moving topology/sparse-cell selection/protected hot wake/mesh-history corrected
  and native-tested; moving isoAdvector/CorrectPhi full CFD now completes40steps.
-Read-only collector recovery validated onUbuntu; mesh cost measured59.66s of
  378.64s loop; timestep10ns pilot tested but physical equivalence not approved.

Next development priorities:
1. Preserve the passing5ns reference, automate paired reporting (this change).
2. Design spatial comparison on a common physical representation; dynamic meshes
   cannot be compared by cell index. IncludeT/alpha/U/liquid fraction, melt/keyhole
   geometry, material and enthalpy balances. Determine acceptance criteria before
   promoting10ns; use longer paired windows only after short comparison is useful.
3. Quantify and reduce thermal/laser cost; test protected update amortization if
   measured savings justify its complexity. All active hot/liquid wake must stay
   covered; skipping CFD equations outside a region is not implemented.
4. Moving local flow + global coarse heat-only region is the strategic full-track
   route, requiring conservative interface heat/material transfer and pressure/
   flow boundary validation. No implementation or cost guarantee yet.
5. After local-grid and timestep convergence, perform bounded4um validation with
   measured24h wall budget; only then promote1.5-2mm melting and solidification.

24h4um feasibility,2um final accuracy, full-track affordability and long-window
energy/geometry convergence remain unproven. Existing short costs cannot be used
as a validated full-track ETA. Do not request full production reruns now.


## 2026-10-08 183756: paired diagnostics verified; stored-field profile audit

Comparison archive3files, hashes/bytes verified, wrapperexit0, missingfilesnone.
Read-only comparison confirms1.21797 job/1.22141 loop speedup and33vs40steps;
no production approval.10nsUmax differs-6.82%/-4.43% at matched snapshots.

Next after pull and sourcing OpenFOAM:
```bash
./tests/m247Performance/CompareMovingProfiles
```
Builds a separate read-only utility using the existing validated regionAudit include/
link settings; never rebuilds/runs the CFD solver. Reads final180.2us from existing
48-rank5ns180928 and10ns182248 cases. Each native audit has600s wall timeout.
InputT/U/alpha/epsilon and latest stored topology files are hashed before/after.
Outputs automatically named M247_moving-profiles-<timestamp>_review.tar.gz on
success or native audit failure. Compilation is still pending Ubuntu;132Python
tests and Bash syntax pass locally, not proof of native runtime.

153coordinate slabs (53x-direction,60y,40z) report geometric volume,metal/liquid
volumes,metal-weightedT and signedU-component integrals. These are three1D
projections, not1533Dcells. Cell-centroid assignment can produce bin-boundary
bias when grids differ; domain/axis-integral closure checks catch missing evidence,
but passing does not imply conservative geometric overlap or3D field equivalence.
No acceptance tolerance or production approval is invented. This screening locates
whether velocity changes accompany distributed material/thermal shifts before
implementing a more costly conservative3D comparison. No enthalpy field is
estimated fromT; no keyhole geometry claim from these slab profiles.
