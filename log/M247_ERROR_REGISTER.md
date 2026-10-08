
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

# M247 moving-window error register

Updated after protected164709 review. These are development failures, not a
claim that passing Python tests establishes OpenFOAM runtime correctness.
Sources are the named review archives and log/entries for each patch.

| ID / first archive | Failure and cause | Fix / prevention | Native closure |
| --- | --- | --- | --- |
| MW01 /153230 | First refinement reached1239840 cells, then missingV0 during mapFields. Mesh-only driver lacks the normal old-volume lifecycle. | Expose protected storeOldVol; validate V0 size/finite/positive/exact pre-update values. | Full initialization plus8updates confirmed160259 after MW02/MW03 fixes. |
| MW02 /154023 | Direct constructor eagerly initialized motion parent and required a motionSolver. | Staged dynamicRefineFvMesh(io,false), qualified init(true), matching refinement's optional-motion setup. | Staged constructor recorded154937; full run160259. |
| MW03 /154937 | V0 still absent before first update. Synthetic time indices could fail storeOldVol's strictly advancing history condition. Archived old indices unavailable, lifecycle cause inferred. | Start above max(Time index,mesh history index), validate and record8strictly advancing index pairs. | Small and real native runs160259 complete; all8V0 records valid. |
| MW04 /protected162215 |48 hot cells remain unrefined through8updates; only wake coverage fails. Binary cell-to-point averaging can dilute a narrow column to lower0.5 threshold, which produces zero selection error. | Protected-mode direct virtual candidate selector, binary/count checks and8native candidate records. Keep frozen wake, mapping, cold coarsening and geometry gates. Preserve actual failure diagnostics as fixture. | CLOSED for frozen prototype: protected164709 small+real native pass,48hot cells become384fine children; real205048wake children all covered. Full-solver integration remains pending. |

## Checks before requesting another Ubuntu run

1. Record archive hashes, wrapper exit, missing files and observed failure stage.
2. Reconstruct assertions from raw logs. Distinguish observed facts from inferred
   mechanisms. An old source/binary must not be credited as the revised build.
3. Check the relevant installed-version API declaration. Use override for virtual
   hooks so signature mismatch becomes a compile error. Record source-version gaps.
4. Keep the actual failed diagnostics as regression data and check that they
   cannot receive approval. Python tests validate parsing/rejection, not native
   refinement, constructors, field registration or thermodynamic accuracy.
5. Run small native preflight automatically before copying the real case. Persist
   failure type/reason/stage in its report and include logs in the single archive.
6. Close a runtime issue only after the user's native logs show its corrected
   behavior. Successful mesh topology tests do not authorize production CFD.

The2506 official source confirms cellToPoint averaging/error/positive selection;
the2512 official header confirms the protected virtual signature. The complete
2512 C source could not be fetched (403). Sparse-selector revised native compilation and frozen topology pass confirmed164709.
New full-solver moving-mesh compilation/runtime remain pending Ubuntu; Python
suite124tests passes and is recorded separately.

Next: pull feat/m247-material-port and run RunMovingCFDPilot once, returning
the automatically named moving-cfd-pilot archive. This starts from the hash-checked
original coarse state, not the stale-field mesh-only snapshots. Do not bypass wake coverage or reduce
thresholds merely to make this test pass.

## MW05 — missing thermal metadata after successful native CFD (172613)

Cause: moving_cfd prepared probe.json without epsilon_tolerance and
phase_temperature_tolerance_K, then called residual_gate requiring those keys.
Native40-step run succeeded; collection raised KeyError. Parser-only tests missed
the complete collection call. Fix: read and validate explicit MELTING controls,
persist them before future launches, and recollect immutable existing evidence.
No fallback tolerance, skipped gate or CFD rerun. Actual diagnostic fixture plus
full collector and resume/package tests pass locally. Ubuntu recollection pending.
Native full-solver build/runtime are now confirmed by172613; production approval
and measured acceleration remain pending.


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
