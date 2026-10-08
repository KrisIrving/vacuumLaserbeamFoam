
## 2026-10-09: native mixed-state regional handoff

Implemented m247MixtureEnthalpy and m247RegionalState: separate energy density,
metal volume fraction and latent-energy inventory; reconstruct T at fixed phase
inventory. Native regional audit has optional mixtureAudit branch, reads T,
alpha.metal and epsilon1 from thermalRegion, predicts conduction, gathers state,
returns only local delta energy and checks global ledger. Default solver untouched.

Actual material coefficients: rhoMetal7950,rhoGas1,cpGas520,latentGas1;
metal cp790/860,Ts1537,Tl1631,latent150000. Uses solver alpha-weighted cp and
legacy alpha_filtered latent thresholds (<.01,>.99). h reference0K is explicit.
This diagnostic closure does NOT establish advective TEqn equivalence; mapped
states remain nonequilibrium until local phase equations reconcile them.

Error prevented: averaging energy or temperature while recomputing equilibrium
liquid fraction loses phase inventory. Map latent ENERGY density independently;
alpha averaging may reduce its capacity. Such inadmissible states stop with a
specific error, not clipping. Conservative bounded inventory redistribution is
still required before production motion across such interfaces.

155 Python tests pass. Native C++ build/MPI still unverified in this Windows
environment. No local VOF/pressure/laser solve yet; no speedup or production claim.
Next: conservative admissibility handling, local flow/pressure boundary and source
ownership; build one integrated acceptance driver. No new Ubuntu micro-screen.


## Native regional stage: transfer/enthalpy/FV wiring implemented, LPBF coupling pending

Added src/m247RegionalCoupling/m247RegionalTransfer.H:owned MPI geometry/data
exchange,sparse rectangular overlap,cache invalidation,integrated correction ledger.
Added pure-metal exactclamped cp/latent enthalpy and inversion,checked with actual
M247790/860cp,150kJ/kg latent parameters in independent Python analytic tests.
Added two-region FV conduction/correction wiring utility with explicitdiffusion guard;
no sourcefield writes.150Python tests pass. Native compilation/MPI runtime unverified.
This is not yet local CFD:mixtureenthalpy,pressure/VOF/laser subdomain boundary,
moving field migration and matched physical/cost acceptance remain outstanding.
No new user-run small test in this checkpoint; preserve old validated solver.
Next development connects region ownership and actual local equations before one
combined user acceptance command. See src/m247RegionalCoupling/README.md.


## 2026-10-08 210010: stop micro screens; structural regional acceleration

Halo candidate failed performance (514.530s vs371.384s,11skips but48vs40steps).
User requests faster development and no more small screens. Freeze these branches;
defaults unchanged. Implemented conservative axis-aligned overlap transfer reference
with147passing Python tests; true regional OpenFOAM solver remains pending.
Next milestone is native global-conduction/local-CFD coupling and one combined
acceptance driver. No new Ubuntu command in this update. See M247_REGIONAL_DEVELOPMENT.md.


## 2026-10-08 203504: cadence native-valid but no skips; opt-in refinement halo

Verified paired archive: both nativebuild/run,gates pass,40steps,zero thermalcaps.
Reference370.380s,candidate377.393s,speedup0.98142; physicaldiagnostics identical.
Interval4 attempted40updates,skipped0,30coverage overrides. Native protection did
its job; cadence alone provides no acceleration. Do not adopt interval4alone or
weaken coverage. First-stepneeded87687cells,step2needed2610,then485/408/313...
new corewindow/hotwake cells require refinement eachstep. Split cause betweenwindow
andwake not recorded, so do not assert thermal-only cause.

Develop opt-in one face-neighbour refinementhalo around unionwindow/heldwake on
attempted updates. Uses official2512protectedextendMarkedCells(bitSet&) method:
https://api.openfoam.com/2512/dynamicRefineFvMesh_8H_source.html
Default halo0/interval1 unchanged. Candidatehalo1/interval4 may pre-refine cells
before coverage demands them. CoverageRequired still counts unrefined CORE cells
before halo; first/scheduled/required updates remain enforced; window/wake checks,
2Mcellcap,V0,mapping/thermal/continuity gates retained. No halo guarantee is assumed.
Halo growth on attempted update only; no dilation on skippedstep. New nativecadence
records prove haloLayers/haloAdded; metadata/dictionary/binary markers validated.
Larger cellcount can outweigh fewerupdates; require measured netcost,not claim
speedup from skipcount. Changesmesh/opticalinput,so physicalequivalence pending.

Next after pull:
```bash
./tests/m247Performance/RunMovingHaloPair
```
Same rebuiltbinary,5nsceiling,48ranks,0.2us each: baselineinterval1/halo0 versus
candidateinterval4/halo1.15minute solver cap each;prepare/build/decomposeextra.
Send ONE M247_moving-halo-pair-<timestamp>_review.tar.gz on successorfailure.
144Python tests/Bash syntax/pycompilepass; newC++compile/runtime pendingUbuntu.
If halo still cannot skip or netcost worsens, stop this cadence branch rather than
adding more layers without region/cost evidence.10ns remains experimental.


## 2026-10-08 193354: longer pair succeeds; guarded topology cadence pilot

Both native builds/decompositions/CFD complete180-180.4us,all gates pass,source
unchanged,no thermalcaps.5ns87steps839.855s;10ns80steps776.799s (1.08117job speedup,
7.51% wall saving). Late actualdt~3.94ns forboth; adaptive/write scheduling reduce
ceiling benefit. FinalTmax differs+0.385%,Umax-4.047%,depositedpower+1.131%;
max sampledpVap difference2.667% at180.3us.10ns remains experimental.
Measured mesh-update wall totals139.10/125.90s (~16.6/16.2% loop). MW06 pipeline
repair now confirmed native; original190128 interruption cause still unknown.

Next after pull:
```bash
./tests/m247Performance/RunMovingMeshPair
```
Matched rebuilt binary, same5ns timestep ceiling, same48ranks and initial coarse
checkpoint,0.2us each. Compare every-step topology interval1 vs opt-ininterval4.
Every step still updates wake/mask and checks cell-centre window/wake refinement.
Firstcycle updates;scheduledcycles update; any required cell withlevel!=1forces
immediate update on all MPI ranks, overriding cadence. Skip only whencoverage is
complete. ExistingV0,rawmapping,full-stepthermal/continuity checks retained.
Skipped topology clears topoChanging/moving flags to avoid stale isoAdvector
mapping; supported only for fixed meshpoints,not additional motion solvers.
Native post-updatewindow coverage fatalcheck applies; no deferral silently allowed
if window/wake incomplete. Coverage criteria are same centroid window/sparse hold
semantics, not geometric intersection of entirecell withwindow.

Per-step cadence records prove attempts/skips/coverage overrides. Collector rejects
missing/mismatched records,newbinary marker required. Timer topology stage now
also includes collective guard decision,not exclusively baseupdate. Actualsavings
may be small/zero if coverage frequently forces updates; no speedup claim before
native test. Passing short screens alone does not approve physicalequivalence.

142Python tests and Bash syntax pass; nativechangedC++ compilation/runtime pending.
Send ONE M247_moving-mesh-pair-<timestamp>_review.tar.gz,including bothsolver/stage
logs,reports/comparison,status.15minute solver cap perrun,build/copy/decomposeextra.
Default interval remains1; defaulttimestep5ns. Do not run anotherlongpair now.

Official2512polyMesh interfaces confirm topoChanging(bool)/moving(bool):
https://api.openfoam.com/2512/classFoam_1_1polyMesh.html
Official2506dynamicRefineFvMesh source shows updateTopology sets state flags and
baseupdate also dispatches motion solver. Full2512implementation fetchwas403;
therefore native2512build/runtime are explicitlypending,not claimedfromdocs.
https://api.openfoam.com/2506/dynamicRefineFvMesh_8C_source.html


## 2026-10-08 192925: long job inactive and partial; clean bounded retry

Resource inventory/archive hashes verified: no matching task processes;5ns ranks
0-17initialT/U/alpha/epsilon/phi present,18-47absent; no solver log/run.json;10ns
not started. Current disk free3.176TB,MemAvailable82.85GiB,inodesample. This rules
out currently active matching task/current resource exhaustion, not historicalOOM/
manual interruption/signal/IO cause. Previous saveddecompose tail endsProcessor18.
No physical0.4us result exists. Stop repeating read-only collection now.

Add explicit decomposition prerequisite: successful native subprocess exit AND
native End marker,exact48processor directories,nonempty5initialcorefieldfiles per
rank. Presence is not full mesh/field correctness; native solver validates content.
Failure cannot advance solver. Recorded launcher independently tested for process
nonzeroexit,timeout,KeyboardInterrupt; running entry saved beforelaunch, failure
state/elapsed/returncode saved afterward. SIGKILL remains untrappable.

After pull run once in a NEW automatically named directory:
```bash
./tests/m247Performance/RunMovingCFDLongPair
```
Preserves190128partialrun. Does not resume incompleteprocessor folders or delete
any originaldata. No CFD work is lost from190128 because none was started.
Two0.4us runs5ns/10ns;15minute solver budget each; build/preparation timeextra.
Terminal now announces each decomposition/solver stage and its log path.
Send ONE new M247_moving-long-pair-<timestamp>_review.tar.gz on successor failure.
139Python tests and pycompile pass; unchanged Bash wrappers previously checked.
No C++/physicschanges; native retry and decomposition gate pendingUbuntu.


## 2026-10-08 191618: incomplete decomposition confirmed; live resource inventory

Archive hashes/bytes verified,manifestexit1 correctly denotes incomplete pair.
Native build succeeded. Reference decompose log stops during Processor18field
transfer, no End; no solver/run.json/candidate. Initial commands[] does not mean
no launch: old launcher recorded commands only AFTER success. Cause is unknown:
no native fatal/OOM/disk/error exit evidence in saved logs. User supplied successful
collection output only, not original interrupted-run output. Do not diagnose solver
instability or restart originalcase based on this archive.

Collector now writes movingLongInventory.json before copying: disk/inode free
space, Linux MemAvailable/SwapFree, matching processnames/PIDs/states (own collector
flagged),48rank initialfield progress and solver/run metadata existence. No kill,
cleanup, build,decompose or CFD launch. Point-in-time resources cannot prove a
historical cause. Run same fast read-only collector after pull, send fresh
M247_moving-long-collection-<timestamp>_review.tar.gz. Source stays untouched.

Future native launches persist running stage BEFORE subprocess starts, then
completed/failed-or-interrupted,elapsed wall,error type/returncode. SIGKILL cannot
be trapped; a running record is therefore not proof process is still alive.
137Python tests pass (resource inventory/partial18field preservation), previous
Bash wrapper unchanged. Live Ubuntu inventory pending; no solver physics change.


## 2026-10-08 190128: incomplete long pair; completion gate and read-only recovery

Verified archive contains only reference initialreport/build/collectionlog. Report
complete=false,pilot_gate=false,commands=[]; no solver log/candidate/comparison.
Manifest wrapperexit0 is inconsistent with completion. Cannot infer whether native
job stopped, is still running, or failed in decompose stage from this evidence.
Do not rerun or claim0.4us outcome. Source protection/CFD failures are not proven.

MW06: parent wrapper trusted shellstatus and omitted decomposition/pilot logs.
Fix explicit pilot/pair completion checks,signal exit130/143 handling, archived
status report and stage logs/run/probe metadata. Missing/incomplete reports force
nonzero wrapper status even if incomingstatus0. Existing package manifests remain
historical evidence; incomplete archives are never upgraded without actual reports.

Next after pull:
```bash
./tests/m247Performance/CollectMovingLongPair
```
Default originaldirectory runs/moving-long-pair-20261008-190128. Copies existing
child stage logs/reports into a fresh timestamp directory; no build/decompose/CFD.
Send M247_moving-long-collection-<timestamp>_review.tar.gz even when incomplete.
Changing input during copy is rejected and partial evidence packaged. Do not
interrupt an active job just to collect it. Collection success means evidence was
copied, not simulation completion; manifest status records actual completion.

136Python tests/Bash syntax pass, including initial-only false-zero regression,
130/143 status retention and read-only partial-decompose evidence packaging.
Ubuntu recovery pending. No native solver changes;5ns remains default and10ns
experimental. Physical optimization resumes after actual long-run state is known.


## 2026-10-08 185039: native stored-field profiles pass; bounded longer pair

Native utility compiled and read both final180.2us snapshots successfully. Archive
hashes/sizes verified,wrapperexit0,missingfilesnone. Input fields/topology hashes
unchanged. Final total metal volume difference-4.406e-9%, liquid volume+0.004549%,
metal-weightedT integral-4.904e-6%. Across three centroid slab projections relative
L1 differences:metal0.0000258-0.0001247%,liquid0.0050-0.00751%,signedmetalU
components0.0252-0.1977%. Signed slab averaging may cancel local velocity changes;
these values do not prove pointwise3D equivalence or keyhole convergence.

Next after pull:
```bash
./tests/m247Performance/RunMovingCFDLongPair
```
Automatically runs matched5ns and10ns ceilings from protected164709original
checkpoint over180-180.4us (0.4us each). Startup1ns,48ranks,CFL0.1,thermal and
coverage/mapping/continuity screens remain.15minute solver cap applies per run;
build/copy/hash/decomposition add time. Approximate prior-rate estimate~25minutes
combined CFD is planning only; adaptive CFL and later state may change cost.
If baseline fails/stops at budget, candidate does not launch and failure evidence
is packaged. No limit bypass or retry loop. Send ONE parent archive:
M247_moving-long-pair-<timestamp>_review.tar.gz. Parent includes both available
solver/build/collection logs and reports plus diagnostic comparison if completed;
child archives remain for recovery. Existing shorter runs are preserved.

134local Python tests pass, including variable mapping horizon and invalid-duration
prelaunch rejection. Bash syntax passes; longer native pair pending Ubuntu.
Default short pilot and5ns settings are unchanged. Optional --long changes only
endTime/duration and metadata; --dt10 --long is experimental. No C++ modification.
The previous profile tool intentionally remains scoped to final180.2us snapshots;
do not apply it to new180.4us cases until its horizon/coordinate provenance is
extended. Subsequent work: compare growth of velocity differences and conservation,
then common3D geometry/field validation before accepting10ns or full-track work.


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

# M247 protected native pass and full-solver pilot

Reviewed protected164709:27 archive SHA256/size checks valid; wrapper0,
missing_files empty. Independently reconstructed small and real native mapping
reports (timing sums tolerance1e-12) and all eight geometry qualifications.
48 small hot cells become384 children and remain covered at every position.
Real initial25631 hot cells become205048 children; wake coverage stays complete
including105384..184312 fine cells outside the moving box. Peak1428574 cells;
8updates57.067949519s; all native commands339.735414s; coarsening720664 cumulative
cells. Maximum relative linear proxy error4.95407e-11; maximum nonlinear direct
product drift6.65122e-12. Native checkMesh still reports one concavity failure
per snapshot (25471 cells in step1); all scoped coplanar-roundoff qualifications
pass. This closes MW04 sparse-selector runtime failure, not production CFD.

Added opt-in m247MovingRefineFvMesh runtime mesh inside vacuumLaserbeamFoam.
Both IOobject and doInit constructor tables registered; constructor defers base
initialization exactly as verified in the native prototype. The2512 official
header confirms both tables and virtual selection signature;2506 source confirms
base coefficient dictionary behavior; full2512 source retrieval was unavailable.
Static cases retain their selected mesh and equations. Custom mask follows the
single original laser interpolation table, keeps full height and192um x/z span,
uses direct binary candidates and one-level/2M cap. Hot/mushy metal activates
m247WakeHold, released only below1487K and epsilon<=1e-6 (50K hysteresis below
1537K solidus); hold state is mapped and saved. This is an experimental policy,
not validated wake length or cooling physics. The solver uses its existing
isoAdvector reconstruction/mapAlphaField and CorrectPhi/pressure/energy path.
No new flow/thermal equations or energy correction are introduced.

New RunMovingCFDPilot rebuilds solver only and advances copied original coarse
180..180.2us on48ranks, requiring the completed protected prototype, raw logs,
source hashes, isoAdvector/rank/table/binary checks before launching. Existing
laser/model libraries must already be built. Solver budget15minutes plus stop
checkpoint grace; decompose/run subprocesses share30minute command budget;
build/copy/hashing extra. Errors/partial logs/reports automatically packaged with
movingCFD names. No production restart from mesh-only prototype snapshots.

M247_MOVING_CFD records actual topology/wake and pre/post raw-field mapping
integrals before isoAdvector remaps alpha. rho*(cp*T+L*epsilon) is a stored-field
screening proxy, not integral thermodynamic enthalpy; native stops on relative
metal/proxy drift>1e-6 or missed wake. Final-step records check bounded alpha/eps,
finite T/U and phi divergence after the full solve. Collector requires one mesh
and state record per step, exact final time, thermal residual convergence/no caps,
and continuity divL1<=0.05/s,divMax<=15000/s (pilot screens only). No speedup pair,
physical equivalence, long-wake release or enthalpy conservation claim.

124 Python tests pass; py_compile and Bash syntax pass. Changed solver native
compilation and48-rank runtime pending Ubuntu. Next pull and
./tests/m247Performance/RunMovingCFDPilot; send automatic
M247_moving-cfd-pilot-..._review.tar.gz. After compatibility passes: matched
fixed/moving-grid CFD comparison with energy/flux audit, meaningful longer
movement/cooling interval, then resolution/cost assessment. Do not extrapolate
24h feasibility from frozen mesh timing or this0.2us interval alone.

# Protected moving-window sparse-mask failure (162215)

## Evidence and status

Archive M247_moving-window-protected-20261008-162215_review.tar.gz:7 file
SHA256/size checks valid, wrapper exit1, no missing files. buildEnvironment
records6f541e68966ebc30c9ab932fa302dfd5f1d8354b. Native program compiles and
completes all8 small-mesh updates. Raw-log reconstruction matches smoke report.
Only wake_gate fails: initial48 hot cells remain48 cells with0 covered through
all updates. Linear mapping/window coverage/cold coarsening pass. Large case
was not copied and no CFD or production result exists for this run.

## Root cause and previous verification gap

The cell mask is Boolean, but base selectRefineCandidates averages it to points
before thresholding. A one-cell-wide hot column can reach at most0.5 at its
points; with lowerRefineLevel0.5 this yields zero error, not a positive candidate.
The archived behavior is consistent with this mechanism. Official OpenCFD2506
source confirms average/error/positive-selection chain, and2512 header confirms
protected virtual hook signature. Direct2512 C source retrieval was blocked403;
no claim that its full implementation was locally compiled/inspected.
Sources:
https://api.openfoam.com/2506/dynamicRefineFvMesh_8C_source.html
https://api.openfoam.com/2512/dynamicRefineFvMesh_8H_source.html

Prior Python tests proved input generation and rejection logic, not native sparse
refinement behavior. Reporting their pass count as native confidence was
insufficient. The new native preflight caught this before expensive real work.

## Fix and checks

Protected mode overrides ONLY selectRefineCandidates in diagnostic subclass,
selecting exact1-valued cells directly. It uses override to enforce the2512
signature at compile time, checks binary input/control interval/counts and emits
8 native candidate records. Base selectRefineCells, budgets, topology restrictions,
2:1 consistency, coarsening and mapping remain responsible for actual updates.
Unprotected mode delegates to the original selector. No threshold lowering or
coverage-gate bypass. Collector requires mode and8matching candidate records;
requested/selected counts must agree. Existing wake coverage/marked-volume,
cold coarsening/geometry/original-source gates stay enabled. Failure message names
failed gates. Smoke report also persists error type, reason, failure stage and
large_case_started=false for native/collection exceptions. Archive exact diagnostic records retained as regression fixture.

121 Python tests pass, including archived failure rejection and missing/lost/
wrong-index selection evidence. Python compilation passes. Wrapper unchanged;
previous Bash syntax check applies. Modified native C++ build/runtime PENDING
Ubuntu. Only an actual protected small+real native pass may close this issue.
Next pull and RunMovingWindow --protect-wake; use automatic protected archive.

# M247 moving window: first native pass and frozen wake retention

Reviewed M247_moving-window-20261008-160259_review.tar.gz:27 file hashes/sizes
verified; wrapper0,missing_files empty. Reconstructed raw mapping log agrees
with report. Small preflight passed. Real eight topology updates completed:
756000 initial -> peak1320480 cells; update sum58.397611577s; native commands
sum324.090973s. Window coverage and positive coarsening873600 cumulative cells
passed. Max relative linear proxy error4.23985e-11; nonlinear direct alpha*T
max7.86513e-12 and alpha*epsilon max2.98639e-13. Eight checkMesh snapshots have
native concavity failure only; scoped coplanar-roundoff qualification passes.
No full CFD, enthalpy/flux/isoAdvector mapping or measured speedup established.

Added opt-in RunMovingWindow --protect-wake (named protected review archive),
mask union with hot/molten metal and conservatively mapped initial-wake marker.
Use case solidus1537K, epsilon1>=1e-4, alpha>1e-6. Strict settled level1 wake
coverage, external-wake presence, marker-volume conservation, original source
and existing cold coarsening/geometry/budget gates. Small preflight includes48
hot cells outside all windows to check retention before large case copying.
No clipping, enthalpy surrogate correction or physical equations changed.
Permanent marker is frozen-audit-only: transient release after cooling and
conservative energy/flow/VOF transfer remain required for production integration.

118 Python tests pass including protected coverage, absent evidence, marker
loss, external coverage and small-case input generation. Native changed C++
compilation/execution requires Ubuntu. Next one protected run; do not repeat
the already-passed unprotected run or expand optical matrices.

Reviewed moving-window154937:8archive files SHA256/size valid,exit1,no missing.
Stagedconstructor works and step0 initialstate records756000cells; V0() still
aborts inside prepareOldVolumes before topologyupdate. storeOldVol isconditional
on new timeindex exceedingcurTimeIndex; driverresetindices1..8 can be behind
restart's currenthistoryindex. Fix syntheticindices to max(currentTimeIndex,
meshhistoryIndex)+step. Emit previous/current indices andcheckstrictadvance,
continuity andpreupdateV0size/finite/exactvalues; noprivatepointer/geometryhack.
Addedautomatic2400cell blockMesh preflight exercisingidentical8nativeupdates,
linearproxy/coverage/coarsening checks beforelargecasehash/copy.120secondpreflight
budget, failurelogs/report bundled; actual2400cell count validatedseparately.
Realnative30minute budget andsource/cell/geometry gates unchanged. NoCFD or
production/speedupapproval.116Python tests passed includingindexfailure and
smallpreflight failurepackaging; py_compile/whitespacepass. Nativefix/small+large
runs require Ubuntu. Nextpull andsameRunMovingWindow freshdefaultwork;
sendautomaticM247_moving-window-...review.tar.gz on success orfailure.

Reviewed moving-window154023:8archive SHA256/size valid,exit1,no missing;
both tools compile, native exits before initial-state/mesh updates with missing
motionSolver. PriorV0fix introduced default directconstructor path which eagerly
initializes dynamicMotionSolverListFvMesh withmandatory motion solver, before
refinement class can allowzero motion. Fixeddiagnosticsubclass constructor via
dynamicRefineFvMesh(io,false) followed by dynamicRefineFvMesh::init(true), matching
staged runtimefactory and refinement's optional-motion initialization. Keep
storeOldVol(V) checks/eightmarkers unchanged. No motion solver added, no model
change, no disabled gate. Existing114 Python tests unaffected; native C++compile
and correctedinitialization/runtimependingUbuntu. Rerun RunMovingWindow on new
copiedwork afterpull; standardarchive includes failure evidence automatically.

Reviewed moving-window153230:8archive SHA256/size valid,exit1,no missing.
Both tools compile; native initial756000cell state valid/protected0. First
refinement selects69120 cells, produces1239840, then SIGABRT at
fvMesh::V0 through dynamicRefineFvMesh::mapFields. No completed update snapshot,
coarsening/mapping quality or physics gate established. Cause: synthetic Time
setTime alone does not seed old cell-volume storage in mesh-only driver.
Fix diagnostic-only dynamicRefineFvMesh subclass exposing protectedstoreOldVol(V)
before every update at the new index, without point motion or privatepointer
manipulation. Check V0 count/finite/positive/exactpreupdateV match andemit8
M247_MOVING_V0 records; collector requires everyrecord count/order/zero delta.
114 Python tests pass, py_compile pass; native repairedcompile/runpendingUbuntu.
Existing wrapper/Bash unchanged, budget/celllimit/sourceprotections retained.
Next pull and rerun ./tests/m247Performance/RunMovingWindow in fresh timestamped
output. Send M247_moving-window-..._review.tar.gz on success orfailure.
Official v2512 fvMesh.H confirmsprotectedstoreOldVol andpublicconstructors;
setV0 isonlyaccessor, not aninitializer, so simplycallingitwouldstillabort.

Prioritize moving local-region development per user instruction. Reviewed145738
single-input archive37hashes/sizes valid,exit0,no missing; independently parsed
all3full logs/profiles andfineownership. Own/alpha-only/resistivity-only288.999073W;
normal-only332.355845W equalsallmapped. Normal sensitivity in this snapshot is
localized, not a correctness/convergence verdict. Stop expanding optical matrix.
Implemented native moving fine-window refinement/coarsening prototype,8updates
on original756000cell frozen180us case, fourcentres80/160/0/80um,192um x/z span,
full yheight,onelevel,1buffer,2millioncellcap. Direct/nonlinear product drift is
reported separately from conserved passive proxies. Saved snapshots NOT solver
restarts. Auditall8meshes andscopednativecoplanarqualification, interiorcoverage,
positivecoarsening andlinearproxyintegrals. No CFD/flowmask/enthalpy approval.
30min sharednativebudget,20min cappercommand; build/copy/hash outsidebudget.
Added geometryOnly nativeaudit avoiding nonexistentmappedfields, default old
moment/flux behavior retained. Automatic namedpartial/finalarchive.
Next pull and ./tests/m247Performance/RunMovingWindow. Builds diagnostictools only;
send M247_moving-window-..._review.tar.gz. Nextstepafterevidence: conservative
solverstate/normalhandling,protectedhot/moltenwake maskintegration,matchedCFDpair;
thermal-onlyoutercoupling later. Nativecompile/runtimependingUbuntu.

Reviewed local-optics-resume144915:39 archive hashes/sizes valid,exit0,no missing.
Three same180us frozen traces complete, zero time/T/alpha/epsilon/U changes;
coarse326.667535W,fine-own288.999073W,fine-mapped332.355845W.
Fine-own/coarse -11.5311%; mapped/coarse +1.7413%; own/mapped -13.0453%.
Fine mesh identical48rankownership verified; binary provenance equal; original
source gate true. Byte-identical fluxname restoration and optical-only changes pass.
Mapped inputs change absorption materially on the same fine mesh, but traversal,
interpolation and nonlinear interactions remain; no individual cause/convergence
or production approval. Added RunLocalOpticsInputs: three single substitutions
(alpha_filtered/n_filtered/electrical resistivity), using retained fine-own and
mapped input bytes without another mapping/rebuild/CFD. Static fine mesh48ranks,
exact input/source guards, frozen runtime/ray flags and binary digest checks,
5min/job plus grace, native utilities20min timeouts; copy/hash cost extra.
Next pull and ./tests/m247Performance/RunLocalOpticsInputs; send single
M247_local-optics-inputs-..._review.tar.gz. Native jobs pending Ubuntu.

Reviewed mapping-audit144301:6 archive files pass SHA256/size checks; exit0,
no missing. Independently recomputed before/after differences: only three optical
inputs modified, plus phi and alphaPhi0.metal renamed to .unmapped with exactly
identical hashes. Original source gates true. This explains strict path guard
failure without evidence of material or mesh modification. Baseline remains
reconstructed from the retained fine case, not a historical pre-map digest.
Added narrowly validated byte-identical flux-name restoration in disposable
optical cases; unrelated changes/bad bytes/collisions still fail before any rename.
Added ResumeLocalOptics: verify144301 evidence/retained hashes, reuse two traces
and already mapped data, copy mapped serial case, restore names, decompose48,
verify identical fine rank ownership, run only one5-minute-budget frozen trace,
check same five-job binary provenance and unchanged material/source fields.
Restored flux is for frozen startup only; no CFD restart approval or projection.
Next pull and ./tests/m247Performance/ResumeLocalOptics; send one automatic
M247_local-optics-resume-..._review.tar.gz. No rebuild or mapping rerun.

Reviewed local-optics-124829: all43 archive hashes/sizes valid; wrapper1,
only mapped trace solver/run missing because guard stopped before launch.
Independently parsed both completed frozen logs: coarse326.667535W,
fine288.999073W (-11.53%), one1536-ray update, no time/material evolution.
Native mapFieldsPar ended normally after553s. Actual offending file changes were
not included by old wrapper; do not infer exact cause or bypass strict gate.
Added read-only AuditLocalOpticsMapping comparing retained mapped/fine file hashes,
reporting rename candidates and original-source hash gates. Future mapping failures
preserve before/after fingerprints and explicit changed paths. No CFD/rebuild/re-map.
Next: pull and ./tests/m247Performance/AuditLocalOpticsMapping; send its one archive.
Python tests and Bash syntax verified locally; native data localization pendingUbuntu.

# NEXT ACTION — M247 fast-track checkpoint

Updated: 2026-10-08

## Freeze coarse/fine optics before extending local CFD

110422pilot passes:23archivehashes valid,22converged steps,no caps,133.14s job,
bounded fields, projectedflux and finalcontinuity good. GlobalTmax4448K and
power~288W differ from earliercoarse window; no matchedphysics verdict.
Pull and `./tests/m247Performance/RunLocalOptics`: existingcoarse/fine180us
snapshots, own opticalinputs plusfine-mapped coarseinputs, threefrozen updates,
noCFD advancement/rebuild. Onlythreeopticalfields maymap; sourcehashes protected,
binary/ray/rank/zerochange gates. Send M247_local-optics-..._review.tar.gz.
103Python tests/Bash pass; native newmapping execution pendingUbuntu. See
LOCAL_OPTICS.md. No longerCFD or repeatedfluxpilot yet; older actions superseded.

## Project copied local flux, then gated0.2us compatibility pilot

104821audit complete12hashes valid; mapped fine phi has divL1~88759/93422 per
second versus coarse0.02664. Scalar mapping/geometry screens cannot approve
restart. Pull and run `./tests/m247Performance/RunLocalFluxPilot`. It copies
auditedlocalRefine4, reconstructs/projects phi only, verifies protected fields
and rereads continuity. Only if this passes does48rank CFD run180-180.2us,
15minute CFD budget plusstopgrace. Automatic M247_local-flux-pilot archive on
success/failure.100Python tests/Bash pass; nativeprojection/time option pending.
No original changes/full-track/production approval. See LOCAL_FLUX_PILOT.md;
no need to repeat sizing or restart audit. Earlier actions below superseded.

## Audit mapped fluxes on the existing local meshes

101101 both previews complete;23archive hashes verified;2.284/2.889million cells,
all mapped moments pass. Native concave flags retain strict failure, but outward
plane excursions only1.02e-13relative. Official OpenCFD test includes planar
face pairs. Scoped coplanar qualification accepts only this evidence pattern,
not other failures or real concavity; no native threshold change.
Pull and run `./tests/m247Performance/AuditLocalRestart`. It reuses101101 meshes,
builds only the checker, verifies unchanged hashes and reports U/phi/alphaPhi
mapping/continuity on coarse/four/ten-layer cases. No CFD or field writes.
Send M247_local-restart-..._review.tar.gz.96Python tests/Bash pass; new native flux
mode pendingUbuntu. See tests/m247Performance/LOCAL_RESTART.md. No further mesh
sizing rerun; restart_ready and production remainfalse. Earlier steps superseded.

## Recover local sizing and diagnose concavity without CFD

003900 four-layer refinement has2,283,911cells and preserved moments, but
15,101concave cells fail native mesh quality. Ten layers did not run. Pull and
run `./tests/m247Performance/PreviewLocalRefinement --resume tests/m247Performance/runs/local-refinement-20261008-003900`.
The update saves failed-quality reports, evaluates both variants, and records
native concavity magnitude/bounds. It hash-copies only verified serial coarse
data, skipping48-rank copy/reconstruction; previous cases retained. No CFD.
Send the new M247_local-refinement-..._review.tar.gz even if status2 (quality
or budget rejection).92Python tests/Bash syntax pass; native diagnostic pending.
See entries/2026-10-08-m247-local-refinement-concavity.md and LOCAL_REFINEMENT.md.
This action supersedes earlier checkpoint steps below.

## Preview local fine mesh after successful region audit

002346 region audit completes: 30 archive hashes valid, 12 bounded snapshots,
136 um minimum molten clearance. Active occupancy is small, but its padded
bounding box covers 77.5% of the domain. Use field-driven selection instead.
Pull and run `./tests/m247Performance/PreviewLocalRefinement`; it builds only
a mesh-check utility and compares four/ten-layer static refinement previews
on copied 180 us fields, with three-million-cell budgets. No CFD advances.
Send the automatic M247_local-refinement-..._review.tar.gz archive. Native
build/refinement pending Ubuntu; 88 Python tests and Bash syntax pass.
Do not repeat InspectRegionBudget. See tests/m247Performance/LOCAL_REFINEMENT.md
and entries/2026-10-08-m247-region-budget-local-refinement.md. Older sections
below are checkpoint history, superseded by this action.

## Repair region-audit build and rerun read-only inspection

Ubuntu v2512 compilation failed on cyclicAMIPolyPatch.H: regionAudit lacked
meshTools include/link dependencies. Added both and clean only this utility
before rebuilding. Pull and rerun `./tests/m247Performance/InspectRegionBudget`;
no solver rebuild or CFD rerun. Send the new automatic region-budget archive.
Current compiler output is sufficient; the old failure archive need not be
sent separately. Bash/static checks pass; native build pending Ubuntu. See
entries/2026-10-08-m247-region-audit-meshTools-build-fix.md. Earlier sections are
checkpoint history.

## Read existing regional geometry/cost; no further CFD pair now

233712 impact review completes successfully but strict legacy equality fails.
Localized metal maxT50.631K/maxU0.08873m/s, alpha difference0.015813 and no0.05
crossings; no production promotion. Laser still50% of loop; removing all flow
stages can only yield1.19x in this window. Original late keyhole grows0.87um/us.
Next pull and run `./tests/m247Performance/InspectRegionBudget`. It builds only
a read-only parallel utility, reads original100–200us and existing impact fields,
and packages material-filtered envelopes/occupancy/boundary/cost data. No CFD
solver, reconstruction or field writes. Send M247_region-budget-..._review.tar.gz.
This supplies sizing for fixed local fine mesh/coarse thermal coupling; actual
4um cost starts with a bounded2us pilot after mapping is checked. See
tests/m247Performance/REGION_BUDGET.md and entries/2026-10-08-m247-ray-impact-region-budget.md.
Earlier sections below are checkpoint history.

## Run legacy/corrected physics-impact pair

231038 corrected transient cache pair passes all strict gates:166 converged steps/no caps, seven final norms zero, identical correction/ray work;377.372 to349.341s,1.08024x job speedup. Next pull and run `./tests/m247Performance/RunRayTraversal --physics-impact`. Both cases use cache on original partition; only ray corrections differ, with automatic metal/gas/interface localization. Same180–182us and30-minute/job budgets. Send `M247_ray-physics-impact-..._review.tar.gz`. This measures intentional physical changes and does not approve them or relabel policy timing as equivalent acceleration. See tests/m247Performance/RAY_PHYSICS_IMPACT.md. Earlier sections are checkpoint history.

## Run corrected transient cache validation

225102 frozen optical regression passes strict gates (power delta 1.7e-13 W, relative spatial differences about 1e-14; matching physical ray events and cutoff tail). Pull and run `./tests/m247Performance/RunRayTraversal --corrected`. Two 48-rank original-partition cases solve 180–182 us with both corrections enabled; only traversal caching differs. Each job has a 30-minute budget. Send the automatic `M247_ray-corrected-validation-..._review.tar.gz`. Collector checks full coupled physics/convergence, fields, cache work and per-step correction accounting. No weighted partition or legacy-physics/full-track approval implied. See tests/m247Performance/CORRECTED_RAYS.md. Earlier sections are checkpoint history.

## Run consistent-cutoff optical candidate

223500 handoff review passes packet/input checks and greatly reduces partition differences, but strict optical gates still fail (power delta 2.563e-5 W). Local weak rays currently continue until rank exits, making threshold application partition-dependent. Added default-off consistentRayTermination, requiring the sample fix, with discarded-power accounting. Pull and run `./tests/m247Performance/RunFrozenLaser --termination`; send `M247_frozen-termination-..._review.tar.gz`. Same frozen inputs and strict gates; no transient or full-track test yet. See log/entries/2026-10-07-m247-handoff-result-termination.md. Earlier instructions are checkpoint history.

## Run pending-sample optical candidate

221754 frozen review verifies identical optical inputs but optical regression fails (2.346 W absorbed-power difference; spatial outputs fail). A moved-to ray sample is skipped on transfer by the current loop. Added a default-off pending-sample correction candidate and MPI packet check. Pull and run `./tests/m247Performance/RunFrozenLaser --handoff`; send `M247_frozen-handoff-..._review.tar.gz`. Only copied diagnostic cases enable the candidate. No transient/full-track test or promotion yet. See log/entries/2026-10-07-m247-frozen-result-handoff.md and tests/m247Performance/FROZEN_LASER.md. Earlier instructions below are checkpoint history.

## Run fixed-state optical comparison

Pull feat/m247-material-port and run `./tests/m247Performance/RunFrozenLaser`. It automatically rebuilds the laser library and solver, captures shared optical inputs from the original partition, then executes one fixed-time laser update per partition at 180 us. No flow/thermal/time advancement. Exact input gates precede tracing; reconstructed spatial outputs and total power are checked separately. Five-minute budget per solver launch plus utility/build/shutdown time. Send the single `M247_frozen-laser-..._review.tar.gz`, including failures. This implements the next diagnostic; it is not another transient partition pair. See tests/m247Performance/FROZEN_LASER.md. Earlier instructions below are retained checkpoint history.

## Decision after 213305 partition review

The weighted partition is rejected: job 323.333 to 451.468 s (0.71618x), seven final fields and physical diagnostics fail. Tracing becomes more balanced but exchange rounds rise 2.27x and thermal cost rises 74.7%; cell counts range 155–31568/rank. Keep the original partition, validated traversal cache and seed off. No repeat pair or user CFD run is needed now. Next implement a fixed-state optical comparison across decompositions to isolate ray transport sensitivity before exchanging backends or sweeping weights. See log/entries/2026-10-07-m247-ray-partition-result.md. The instructions below describe the completed experiment, not the next requested run.

## Run the ray-weighted partition experiment

Pull feat/m247-material-port and run `./tests/m247Performance/RunRayPartition` on Ubuntu. No C++ rebuild is needed. Two copied 48-rank cases compare the original partition against checkpoint-rayQ-weighted Scotch over 180–182 us, with a 30-minute CFD budget per case. Initial global mesh/field checks precede both jobs; final fields are compared on the original global mesh after reconstruction. Send the automatically generated `M247_ray-partition-..._review.tar.gz`, including on failure. Weighting is a proxy, so speedup is unverified and strict regression gates remain unchanged. See tests/m247Performance/RAY_PARTITION.md.

## Decision after210403recovery: stop seed shortcut, target tracing distribution

Recovery complete:27hashes verified,both full logs/provenance present. Independent
timing/thermal/physics/global and rank-work checks pass. Seven Ubuntu field norms
zero; raw fields not archived. Job0.984922x/loop0.985554x,so seed switch remains
off; validated cache retained. No more Ubuntu runs or collection for204122.
21/48ranks search nothing;44/46carry58.314% of searches;trace max/mean13.32.
Next development: tracing-aware partition/backend comparison,with appropriate
global physics/ownership checks rather than identical per-rank work after a
partition change. Continue fixed local fine mesh/thermal-fluid coupling roadmap.
See entries/2026-10-07-m247-seed-recovery-verified.md. Older actions superseded.

## Immediate action: recover204122logs; stop seed shortcut experiments

Seed candidate report passes regression but fails performance:327.3→332.3s.
Real-mesh parity322560/0; exact-axis eligibility only244/756000cells. Keep
cartesianRaySeedSearch off and retain validated cachedRayTraversal. No CFD rerun.
Archive11hashes verify,but variants=[] because packaging omitted new names;
full solver logs/provenance are absent,so report gates are not independently
log-verified yet. Shared variant catalog fixes this;60Python tests pass.
Pull and run
`./tests/m247Performance/RepackageReview tests/m247Performance/runs/ray-seed-search-20261007-204122`.
Send printed collection archive. Next development targets tracing load
distribution/particle backend and local fine mesh/domain coupling rather than
further strict-axis seed optimization. See
entries/2026-10-07-m247-seed-search-result.md. Older actions superseded.

## Immediate action: validated cache plus seed-cell shortcut

201432broader cache validation passes:29hashes verified,seven fields exactly
equal,166steps/no caps,matched logged physics/ray work; job1.19758x and
loop1.19772x. Retain validated opt-in cache; no repeat of completed pair.
Pull feature branch and run `./tests/m247Performance/RunRaySeedSearch`.
This builds/checks real-mesh parity and compares cache vs cache+default-off
Cartesian seed interior shortcut over180–182us with30-minute budget per job.
Send printed M247_ray-seed-search-..._review.tar.gz,including failure.
59local Python tests and Bash syntax pass; new C++/CFD/gain pending Ubuntu.
See tests/m247Performance/RAY_SEED_SEARCH.md and
entries/2026-10-07-m247-seed-search-candidate.md. Older actions superseded.
Long-track architecture: fixed local fine mesh,then fixed thermal/fluid coupling
prototype,then moving window; seed optimization does not establish24h affordability.

## Immediate action: 180–182-us cached traversal validation

Pull feat/m247-material-port and run
`./tests/m247Performance/ValidateRayTraversal` on Ubuntu. It automatically builds,
checks real-mesh search parity, and runs independent reference/cached cases
from the same 180-us checkpoint to182 us with a30-minute wall budget per job.
Build/copy time and termination grace are additional. Seven physical/deposition
fields, common-time diagnostics, thermal convergence and identical global/rank
ray work remain required; performance needs at least5% loop and job improvement.
Send the single printed M247_ray-traversal-validation-..._review.tar.gz, including
on failure.56 local tests pass; actual broader CFD is pending Ubuntu.
No new solver algorithm or default change. The completed0.2-us pair need not be
repeated. If this passes, next development targets tracing imbalance before
fine-grid/full-track cost estimates. Older actions below are superseded.
See entries/2026-10-07-m247-traversal-broader-validation.md.

## Decision after collection-200224: keep validated cache candidate

Archive integrity and all short regression/performance gates pass. Seven final
fields over756k cells differ exactly zero; rayNumber explicitly not_written.
Search parity50688/0 mismatches, identical logged physics/work and zero thermal
caps. Job36.0399/32.0343 s (1.125x), loop1.1385x; inner laser cost falls21.29%.
Retain opt-in cachedRayTraversal, keep default false. Tracing imbalance remains
about13x max/mean. Next development prepares a matched180–182-us broader
validation before partitioning/particle-backend optimization. No additional
Ubuntu command or upload is needed for this completed review; do not repeat
the short pair/collection. See entries/2026-10-07-m247-cached-traversal-validated.md.
Older actions are superseded.

## Immediate action: collect existing 195231 fields, no CFD rerun

The cached candidate builds, passes 50688 search parity checks and completes
both jobs. Job36.0399/32.0343 s, speedup1.125; loop1.1385; logged physics and
ray work match, thermal convergence passes. Field collection was incompatible
with inherited non-debug rayNumber NO_WRITE. It now requires seven physical/
deposition fields and explicitly reports absent optional rayNumber. Pull and
run `./tests/m247Performance/InspectRayTraversal tests/m247Performance/runs/ray-traversal-20261007-195231`.
Send its printed collection review archive. No rebuild or CFD is needed.
Candidate remains default off; saved-field regression is pending. See
entries/2026-10-07-m247-traversal-195231-collection-fix.md. Older actions below
are superseded.

## Immediate action: equivalent cached ray traversal

Official V3.0 compactRay and V3.1 particle-tracing sources reviewed. Added a
default-off cachedRayTraversal candidate, preserving legacy lookup predicates,
FIFO order, sampling and optics while caching step lengths and search storage.
Pull and run `./tests/m247Performance/RunRayTraversal`. It builds all targets,
runs an old/new real-mesh search parity test first, then fresh matched 180–180.2-us
reference/cached cases with a 15-minute budget per CFD job. Send the single
printed `M247_ray-traversal-..._review.tar.gz`, including on failure. Regression
includes eight final fields, per-rank work and thermal/physical diagnostics.
51 local harness tests pass; actual OpenFOAM build/CFD and speedup are pending.
See tests/m247Performance/RAY_TRAVERSAL.md and
entries/2026-10-07-m247-official-ray-traversal-candidate.md. Older actions are
superseded.

## Decision after exchange-profile-193145

Compilation, schema-2 statistics and instrumentation regression pass. Five
saved-field norms are exactly zero; all 16 thermal steps converge, no caps.
Jobs 36.0385/36.0376 s. Exchange mean 17.9614 s, dominated by blocking broadcast
but nested merge only 0.00177 s. Tracing max/mean 12.91; two ranks carry 59.20%
of searches and 21 ranks carry none. Prioritize equivalent tracing/cell-search
optimization and then tracing-aware partitioning, rather than merge tuning or
assuming broadcast time is pure transport. Existing evidence is sufficient;
no additional Ubuntu run/upload is needed now. See
entries/2026-10-07-m247-exchange-profile-result.md. Older actions are superseded.

## Build repair: exchange-profiler logging precision

The 192743 compiler output identifies an invalid precision() call on Info,
which is a messageStream. The profiler now obtains its Ostream via Info(),
sets precision there and restores it after reporting. Pull and rerun
`./tests/m247Performance/RunLaserProfile`; the command rebuilds automatically
and prints a fresh review archive. Existing failure logs suffice for diagnosis;
actual Ubuntu compilation and CFD remain pending. See
entries/2026-10-07-m247-exchange-stream-fix.md.

## Immediate Ubuntu action: exchange details and rank work

Pull feat/m247-material-port and run `./tests/m247Performance/RunLaserProfile`.
The command rebuilds the library and clean solver, rejects schema-1 libraries,
and runs fresh matched profiling off/on 180–180.2-us cases (15-minute budget
per job, build/copy additional). Send the printed
`M247_laser-exchange-..._review.tar.gz`. It includes nested copy/gather/broadcast/
merge timing and rank work CSVs. Ray algorithm and physics settings are unchanged;
this evidence selects the next equivalent acceleration. Compilation and CFD
remain pending Ubuntu. See entries/2026-10-07-m247-laser-exchange-profiler.md.
Older actions below are superseded.

## Current measured target after laser-profile-190239

Build/library checks and profiling equivalence pass; all five final fields differ exactly0. Job36.04/37.04 s, observed profiling overhead2.78%. Round exchange consumes94.47% of inner laser mean time, but includes blocking waits; tracing max/mean12.82 indicates strong imbalance. Next development splits copy/gather/broadcast and rank tracing/merge costs before selecting equivalent exchange/ownership acceleration. Do not infer removable94.5% or change ray counts/physics. No additional Ubuntu action is needed for this review. See entries/2026-10-07-m247-laser-profile-result.md. Older actions below are superseded.

## Build repair for laser-profile-185645

The solver cannot find the new laserPerformance.H through an existing lnInclude directory. Both RunLaserProfile and the library Allwmake now refresh it explicitly with wmakeLnInclude -u and check the header before compilation. Pull and rerun `./tests/m247Performance/RunLaserProfile`; send its new timestamped archive whether build succeeds or fails. No manual cleanup is needed. No new CFD or cost result exists yet. See entries/2026-10-07-m247-laser-lninclude-fix.md.

## Immediate Ubuntu action: measured laser substage costs

Pull and run `./tests/m247Performance/RunLaserProfile`. It builds the laser library and clean solver object, preflights the loaded library, runs profiling off/on independent 180–180.2-us tight bounded cases with phase width zero, and auto-packages one archive. Each solver job has a 15-minute budget; build/copy time is additional. Send the printed M247_laser-profile-..._review.tar.gz. Profiling overhead and unchanged diagnostic/field results must pass before selecting an equivalent optimization. No speedup claim or new physical acceptance. See tests/m247Performance/LASER_PROFILE.md. Older actions below are superseded.

## Current decision after 183545 localization

Both-state metal T sensitivity is small (max0.575/0.314 K), but raw metal pressure differences reach1.67/1.93 MPa and interface phase differences exceed0.99 in1498/537 cells. Width itself changes the mixture phase curve and Darcy state; do not promote smoothing or request another width test. Existing localization is sufficient. Next speed-development step: opt-in laser internal timing/counters with width zero, then measured equivalent optimization under matched regression. Phase closure/enthalpy/flow semantics need a separate physical design; 4-um/full-track production remains pending. No additional Ubuntu command is required for this review. See entries/2026-10-07-m247-phase-localization-decision.md. Older actions below are superseded.

## Current action: offline phase width-response localization

182533 phase probe is valid: new binary/modes, all 16 steps converge, zero caps, 36–38 s. Width sensitivity remains unresolved: narrow/wide max T21.9 K, U5.56 m/s, epsilon1=1, raw p_rgh2.20 MPa. Pull and run `./tests/m247Performance/InspectPhaseBlend tests/m247Performance/runs/phase-blend-20261007-182533`. Send the new localization archive. It reads existing final fields only; no rebuild or CFD. No physical/width acceptance or 4-um/full-track approval yet. See entries/2026-10-07-m247-phase-blend-result.md. Older actions below are superseded.

## Current build repair: initialise phase controls before properties

The 172208 build archive confirms a C++ scope error: createFields.H calls updateProps.H before the old time-loop-only declaration of phaseTemperatureBlendHalfWidth. The setting is now owned and initialised by createFields.H, with shared startup/runtime validation, covering normal and postProcess inclusion. Pull and run `./tests/m247Performance/BuildPhaseBlend` again and send its automatic archive. Actual Ubuntu compilation remains pending. No CFD repeat until build verification. See entries/2026-10-07-m247-phase-blend-initialisation-fix.md. Older actions below are superseded.

## Immediate action: establish the rebuilt solver before more CFD

The 170639 phase-blend archive used the prior binary and lacks both new mode diagnostics in all three cases. Collection correctly failed; these results do not test smoothing. Pull the branch and run `./tests/m247Performance/BuildPhaseBlend`. Send its automatic build review archive. This builds the solver directly and captures build errors, environment, executable path/hash and static feature checks. Do not repeat CFD yet. RunPhaseBlendProbe now rejects old or shadowed solvers before starting cases. See entries/2026-10-07-m247-phase-blend-build-gate.md. Older immediate actions below are superseded.

## Immediate development test: continuous phase-temperature override

Rebuild the branch on Ubuntu and run `./tests/m247Performance/RunPhaseBlendProbe`. It compares hard-rule enthalpyTight and smooth half-widths 0.005/0.01 over 180–180.2 us, all tight thermal tolerances, matched outputs and independent original checkpoints. Send the single automatic archive. Width defaults to zero in the solver and all older probes. This is an experimental mixed-cell closure change; coupling review confirms actual case PowderSim=false and direct epsilon Darcy, with same epsilon/latent/phase-consistency path and candidate rhok recomputation. Restart latent adjustment, width sensitivity, energy and longer-field validation remain pending. Do not interpret smoothing as an approved physical fix. Details: tests/m247Performance/PHASE_BLEND_PROBE.md. Older next actions below are superseded.

## Latest diagnosis: alpha=0.05 phase-rule discontinuity

Localization archive received and verified. The large global T/U extrema are in gasBoth; metalBoth max/RMS differences are T 3.49/0.0123 K and U 0.0355/0.000169 m/s. Interface still has up to 39.2 K and 2.21 m/s differences. All seven epsilon endpoint differences coincide with alpha crossing 0.05. updateProps jumps phase temperatures from pseudo-gas-dominated about 78/91 K to metal 1537/1631 K at this threshold, demonstrating an equilibrium-rule artifact. Next code design must address continuous interface phase treatment together with enthalpy and flow-mask semantics, under an opt-in experimental mode and validation; do not hide it by ignoring interface cells or merely changing convergence tolerance. No localization rerun needed. Full-track/4-um production remains pending. See entries/2026-10-07-m247-localization-diagnosis.md. Older next-action items below are superseded.

## Latest gate: convergence passed, local field acceptance unresolved

User archive validation-20261007-161510 verified. Both 166-step candidates converge, 5.71/6.32 min, no cap hits. But final max differences are T 316.08 K, U 10.59 m/s, epsilon 1, alpha 0.01193. Low RMS does not establish local accuracy. Before more CFD, pull and run `./tests/m247Performance/InspectThermalValidation tests/m247Performance/runs/validation-20261007-161510`; send its new localization archive. It only reads existing fields and reports alpha regions, worst cell state and counts including alpha=0.05 crossings. See tests/m247Performance/FIELD_LOCALIZATION.md. Earlier next actions below are historical and superseded.

## Immediate action: candidate convergence-tolerance validation

Pull and run `./tests/m247Performance/RunThermalValidation` on Ubuntu using the previous candidate solver binary. This compares enthalpyStandard (1e-4 / 0.01 K) with enthalpyTight (1e-5 / 0.001 K) over 180–182 us, with equal ASCII output, independent original checkpoints and 30-minute budgets per job. Send the automatically generated review archive. The collector checks convergence and reports all-rank final internal-field sensitivity; it does not grant physical production approval. Details: tests/m247Performance/THERMAL_VALIDATION.md. After review, plan longer 10–20-us field/keyhole/energy validation before 4-um refinement. Earlier next-action entries below are historical.

## Latest Ubuntu gate and file delivery

The 180–180.2-us candidate completed all 16 steps in 35.04 s versus legacy 127.13 s (3.63x). Thermal correctors fell 151 -> 10–14; cap hits 16 -> 0, with both candidate residual criteria met. Worst legacy cells are at alphaMetal about 0.054 and switch liquid fraction between 0 and 1. Candidate physical diagnostics are close but not identical; long-window, converged reference and field/energy validation are next. See `entries/2026-10-07-m247-thermal-probe-result.md`. Earlier next-action text below is historical.

Both test wrappers now create a named review tar.gz automatically; send one archive. Manual packaging of existing runs uses `python3 tests/m247Performance/package_results.py --work <run-directory>` and requires no new CFD calculation. The user's current run is `tests/m247Performance/runs/thermal-20261007-154702`.

## Current priority after Ubuntu logs

The 180–182-us ray pair measured 1.120x job speedup, but both variants hit the thermal cap in all 166 steps. All 25,066 logged max epsilon increments equal 1; temperature linear solves take 1–2 iterations. Full residual histories match between modes. Investigate nonlinear phase correction before any 4-um or full-track run.

Next Ubuntu action: build and run `./tests/m247Performance/RunThermalProbe`, an independent 180–180.2-us legacy/candidate pair with residual cell locations and a 15-minute wall budget per job. See `tests/m247Performance/THERMAL_PROBE.md`. The candidate is default-off, includes a phase-temperature consistency gate, and is not production approved. Send both logs and metadata. Older pending-test notes below are historical and superseded by this priority.

## Active branch

    feat/m247-material-port

## Physics gates already passed

- Wang near-vacuum model frozen.
- M247 Mondal/Wang constitutive gate passed.
- 100-us M247 bare-plate transfer passed.
- Fixed-PSD M247 powder generator passed.
- 100-us powder preflight passed.
- 200-us / 756k-cell M247 powder track completed on 48 ranks.

## 200-us result

- wall time: 29.18 h;
- keyhole depth at 200 us: about 316.5 um;
- depth-growth rate is decreasing but not yet a strict plateau;
- final liquidus-envelope clearances are adequate in x/y/z for this case;
- straightforward full-domain 1.5-2 mm CFD is computationally unacceptable.

## Current engineering constraint

Any M247 4-um validation job should finish within 24 h.

Do not run a full-domain 4-um case.

The planned 4-um validation is:
- restart from an evolved 8-um state;
- refine only a compact keyhole/melt-pool ROI to 4 um;
- run approximately 20-30 us;
- compare against the corresponding 8-um history.

## Immediate next gate — mature-state performance pair

The 2026-10-07 phase-1 development provides an optional ray-history optimization
and MPI-aware schema-2 timers, including field/ray I/O and thermal cap hits.
Start with `tests/m247Performance/README.md` and the independent180–182 us pair:

    ./Allwmake -j 48
    ./tests/m247Performance/RunPair

The pair copies the completed reference case state and preserves the original.
It tests default ray history versus `recordRayPaths false`; no measured speedup
or completed Ubuntu validation is claimed yet. Send comparison JSON/CSV and
both solver logs. Expected first-pair cost is around an hour plus preparation,
with a2-hour budget per job. Details and failure rules are in the test README.

Do not run the older initial-state10-us probe as the first gate when the mature
180-us checkpoint is available. The existing probes below remain alternatives.

## Existing performance probes

The solver has optional PERF_DIAGNOSTICS instrumentation. It preserves the
original operation order and is disabled unless requested by vacuumProperties.

Benchmark case:

    tutorials/vacuumLaserbeamFoam/M247_0p6Pa_perfProbe8um

It uses the same 756k-cell geometry and physics as the 200-us case, but runs
only 10 us.

Local sequence after pulling the current branch:

    ./Allwmake -j 48
    cd tutorials/vacuumLaserbeamFoam/M247_0p6Pa_perfProbe8um
    ./Preflight
    ./Allrun
    grep '^PERF_DIAGNOSTICS ' log.vacuumLaserbeamFoam

Do not change solver tolerances, Courant limits, ray counts or physics until
the timing split is measured.

## Production strategy under evaluation

Preferred architecture for the final 1.5-2 mm track:

1. moving/local high-fidelity VOF + momentum + recoil + ray-tracing region
   around the laser/keyhole;
2. outer/coarse region solves thermal conduction/phase thermal history only;
3. transfer temperature/enthalpy between the local CFD zone and global thermal
   domain;
4. use the thermal domain for the trailing solidification/cooling history.

This is consistent with published local moving thermal-fluid and local
multi-mesh approaches and will be validated against the existing full-CFD
100-200-us results before production use.

Solver launch reserves240s within the shared command deadline for writeNow/MPI
shutdown; the15minute solver budget is shortened if decomposition consumes most
of the shared budget. No solver starts when that reserve cannot be met. Rebuild
and launched solver hashes must match. Wake hold is initialized at the restart
time before the first time increment, so saved hold state can be read correctly.

Pilot startup deltaT1ns, maxDeltaT5ns and maxCo/maxAlphaCo0.1 avoid taking
a coarse-grid-sized first timestep across the initial refinement. These conservative
compatibility settings are not a production speed benchmark.
