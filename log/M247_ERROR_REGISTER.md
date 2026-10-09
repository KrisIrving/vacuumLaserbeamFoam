## 2026-10-09 101823: real-pair no-reduction selection fixed

Verified17manifest hashes/sizes. Rebuild,180us reconstruction and native CSV
read completed; no CFD launched. Source hashes unchanged. No physical difference
or speedup exists yet. Missing solver log/run.json are expected for this stop.

Root cause: prior same180us spatial audit already showed fast material envelope
x[-456,248]um,z[-271,271]um. Adding96um gives bounds beyond the original
x[-520,320]um,z[-320,320]um. Fullheight policy therefore prevented any cell saving.
This should have been identified before requesting the native pair. Current
archive omitted seed-category bounds because plan raised before recording them.

Keep identical active predicates,96um padding and all active/spatter/gas seeds.
Permit cropping the cold lower reservoir below activeymin-96um; preserve original
atmosphere/top. Original bottom is replaced by a held-checkpoint cut boundary,
so this is a new explicit approximation measured by the same real pair, not a
claim of equivalent BC or large acceleration. Padding is not relaxed. Native
initial/per-step cut checks remain mandatory. If active state reaches original
bottom the no-saving rejection remains; do not silently drop active particles.
Selection now records per-category counts and xyz bounds, selectedcell fraction,
original bounds and retained physical boundaries even if selection is rejected.

201Python regressions PASS including dispersedfast material spanning x/z with
retained buffer and cold-bottom reduction; no nativeC++/solver changes this fix.
Run one fresh ./tests/m247Performance/RunLocalMeltPair afterpull. Same180..190us
physical pair, no parameter screening. Gains likely limited on this compact
existing8um domain; measuredcost must decide, not cellratio alone. Full moving
local/global coupling remains the structural target for1.5..2mm tracks.

## 2026-10-09: real melt pair preventive checks

Use native OpenFOAM reader for binary restart; no Python binary-field parsing.
Crop on copies, native mapped cut values retained, no silent zero inlet fields.
Reject empty/full/no-saving selection and any active metal on initialcut.
Per-step cut audit detects latercontact; geometry/field mismatch blocks CFD.
Compare retained cells by physical coordinates, not unrelated processor indices;
volume-weighted norms and sameROI liquid inventory exclude removed cold material.
Gas numericalepsilon belowalpha.05 cannot seed the whole powderbed as melted.
Source hashes checked, including failed runs where possible. Native qualityFAIL
not waived. Bounds apply to entire laser interval. Complete status requires all
commands succeeded; failures package incomplete evidence. Entire MPI group kill,
no helper-process timeout orphan. Shell bytes/uploadsLF checked; explicitLFwrites.
Native compile/physics/cost not markedPASS from offline200tests.

## 2026-10-09: fix Ubuntu CRLF interpreter failure

RunRegionalAcceptance failed before starting: /bin/bash^M bad interpreter.
Cause: Windows Python write_text used default newline translation; the uploaded
extensionless shell script contained CRLF. Bash -n alone did not detect this
kernel shebang failure. This was a developer packaging error, not Ubuntu setup.
Normalize wrapper bytes to LF; add .gitattributes * text=auto eol=lf, explicit LF
writes and regression checking raw shebang bytes/no CR. Existing CFD logic and
parameters unchanged. Remote upload content is also normalized to LF.
Native test remains pending; no successful simulation implied by syntax tests.
Ubuntu can temporarily use sed -i 's/\r$//' on this wrapper, then rerun --physics.

## 2026-10-09: conduction/phase integration checks

Prevented owner-only processor conductivity values: use processor field patches
and correctBoundaryConditions before every conduction matrix assembly.
Prevented a false nonlinear PASS when enthalpy is linear but conductivity changes:
convergence includes relative temperature change as well as energy consistency.
Prevented gas-only melting acceptance: gate capacity-weighted liquid inventory,
not temperature extrema. Require actual internal conductive energy redistribution.
Local analytic check found2e13W/m3 over100us only reaches1628.8787K in pure metal;
raised manufactured cycle to3e13 to cross liquidus. This is fixture sizing, not
physical laser calibration. Final equilibrium remap preserves total energy.
189 tests/Bash syntax pass; native C++ build/run pending, never recorded as PASS.


## 2026-10-09 091028: native local flow PASS; passive thermodynamic transport

Manifest bytes/SHA256 verified; independently reparsed serial/MPI20step logs.
Native build/run complete from e114e5d5; solverSHA256df4c273cf7526a63d91aa0f44bd942ed27bdd4deab8adb3b6a138a4f54bfd0c6.
Metal volume3.0e-10 ->3.2e-10m3 matches2.0e-11m3 net inflow. Maximum step volume
residual1.5833e-25m3, mass residual1.1019e-21kg. Interface change2.0e-11m3.
Serial/MPI inventories match; inputs unchanged. Acceptance elapsed0.99234s excludes
build/packaging. Tiny alpha excess<=9.9e-14 is within1e-10 roundoff bound, no clipping.
productionApproved false is expected: this proves cold local time-loop viability,
not LPBF accuracy, actual optical/thermal closure or a production speedup.

Implemented m247ThermalTransport.H: conservative implicit Euler/upwind transport
of sensible energy, latent inventory, unused latent reserve and cp-capacity moments
with the same pre-advection face phi. Carries capacity history independently of
sharper isoAdvector alpha. Capacity is latent+nonnegative reserve, avoiding an
unstable remapped-capacity minus latent subtraction. Cell temperature inverse uses
mapped cp moments and transported latent state, without forcing phase equilibrium.
Each field has a boundary-flux ledger; cumulative total energy includes prescribed
volumetric heat gain and physical boundary energy. Supports signed heat source,
rejects negative moment inventories; no clipping. Energy components remainNO_WRITE.

New --heat mode runs20steps,serial/MPI2,checks existing flow gates plus moment
ledger/source integral and temperature inversion. Prescribed Q1e7W/m3 contributes
1.2e-6J across6e-10m3 domain over200us. This is PASSIVE advection/heat-source transport:
no conduction, latent phase relaxation, thermal-to-flow feedback, ray tracing,
evaporation/radiation or moving/global correction yet. Source is manufactured.
Do not treat it as a validated LPBF heat equation or latent melting model.

181Python tests and Bash syntax pass; new moment FV C++ uncompiled locally.
Next bounded Ubuntu command:
./tests/m247Performance/RunRegionalAcceptance --heat
Send ONE M247_regional-thermal-transport-<timestamp>_review.tar.gz on success/failure.
After this transport contract is native-confirmed, integrate implicit heat conduction,
phase feedback and actual source/moving-global history; do not repeat cold-flow gate.


## 2026-10-09 005127: native regional interface PASS; local flow time loop next

Verified all review archive manifest SHA256/size entries and independently reparsed
four native logs. Build commit1317a579, solverSHA256b86d72777af4b708f3f8ebcadf84ac4577f7f15f770d7e4006307de785de7b9b.
Native compile, mesh generation, serial and MPI2 execution all complete. Wrapper
exit0; source inputs unchanged; acceptance elapsed1.865s excludes build/packaging.
16global/80localcells; constant/uniformT error0. Energy corrections+.00039J and
-.00024J; maximum ledger residual1.573e-15J, inverse error1.715e-16. Projection
initialdiv833.33/s ->serial4.687e-12/s, MPI6.617e-12/s. Serial/MPI ledgers agree.
This validates native transfer/projection/supplied-source interfaces only; it is
not a measured LPBF acceleration or physical melting/solidification benchmark.

Added m247LocalFlowAudit: persistent local fields, initial coarse alpha import,
20time steps with actual isoAdvector and its consistent density mass flux,
variable-density conservative laminar momentum and pressure projection. Pressure
kernel now operates on caller-owned U/rho/p/phi and actual inverse momentum diagonal.
Velocity correction uses rAU*reconstruct(deltaPhi/rAUf) for variable coefficients;
face phi remains authoritative. Default full LPBF solver unchanged.

Flow gate covers200us withdt10us,CFL<=.25, no mesh motion, no alpha clipping/snap.
Checks each step and cumulative metal-volume/mass versus physical boundary flux,
finite alpha bounds and pressure continuity. At least1e-12m3 interface change
required; collector rejects no-op progression, missing steps, drift or serial/MPI
inventory mismatch. No thermal equation, recoil, surface tension, radiation,
evaporation, laser/source generation or moving-history update in this cold-flow
gate. Do not infer thermodynamic moment advection from its VOF mass ledger.

177Python tests and Bash syntax pass. Existing interface module was native-confirmed;
new time-loop/refactored pressure C++ still requires Ubuntu compilation/runtime.
Next single bounded native run:
./tests/m247Performance/RunRegionalAcceptance --flow
Generatedfixture only,2MPI ranks,build5min+allnative stages shared10min caps.
Send ONE M247_regional-flow-step-<timestamp>_review.tar.gz even on failure.
This is an implementation integration gate, not a parameter sweep. After pass,
connect heat/moment advection, actual optical/source terms and moving global history.


## 2026-10-09: bounded native regional acceptance ready for Ubuntu

RunRegionalAcceptance now builds m247RegionalCouplingAudit and generates its own
16-cell thermalRegion/80-cell flowRegion fixtures (fully liquid metal/cold gas,
uniform1580K across interface; manufactured, not equilibrium physics). Local mesh
crosses coarse interface. Runs positive and negative source ledgers, pressure
projection, thermal/moment transfer, serial and two-rank MPI in one command.
No prior powder-case directory or archived checkpoint required.

Native gate checks exact cell counts, preserved constant alpha and uniform T,
source component/global correction energy, finite pressure continuity, unchanged
all case inputs, expected correction+.00039J/-.00024J and serial/MPI agreement.
Native stages record RUNNING before launch, then return code/error.10min shared
runtime budget stops process group on timeout/interruption; build budget5min.
Failure/incomplete exit0 cannot masquerade as success. INT130/TERM143 retained.
One uniquely named review tar.gz includes logs, build/binary provenance, original
fixture inputs, input hashes, reports and final completion status. No field dumps
from production and no production case touched. No resume/overwrite of run folders.

Fixed potential pure-alpha roundoff rejection: native/Python gathering normalizes
by geometric covered row volume after full coverage-to-mesh.V check; constant1
is retained rather than exceeding1 by geometric division roundoff. No fraction
clipping. Scatter remains integrated-delta conservation checked against mesh.V.

172Python tests and Bash syntax pass. New native C++ remains uncompiled locally.
This is the next required Ubuntu checkpoint, not an LPBF parameter screen or a
regional production simulation. Pass means native interface viability; it does
NOT validate actual momentum/VOF/ray/source generation or a24h/full-track speedup.

Run from project repository after pull and sourcing OpenFOAM2512:
./tests/m247Performance/RunRegionalAcceptance
Default build2jobs, MPI2ranks, 16/80cells. Build5min + native stage shared10min caps,
plus short setup/packaging; actual elapsed unknown until Ubuntu. Send the single
M247_regional-acceptance-<timestamp>_review.tar.gz even on failure. If pass, proceed
to actual local CFD/source timestep without further interface parameter screens.


## 2026-10-09: local pressure/flux projection and source-delta wiring

Added native m247LocalProjection.H: fixed-mesh variable-density pressure correction
with dt/rho face coefficient, boundary-constrained pressure solve, corrected face
flux and reconstructed velocity. Optional localProjectionAudit hooks it into the
regional utility. Physical pressure units required; fixed pressure outlet anchors
MPI solve. Supported uncoupled pairs: fixedValue U/fixedFluxPressure correction,
zeroGradient U/fixedValue correction; processor patches only for coupling.
No arbitrary MPI reference cell, incompatible BC fallback or mesh-motion shortcut.
Global max div and boundary net volume flux must meet explicit tolerance.

Added native local source-delta ledger and sourceAudit hook. Read supplied local
volumetric laser, evaporation, radiation, advection and conduction densities;
subtract mapped global conduction before scattering delta energy. Global source
ownership must be explicitly declared conduction-only. Radiation can heat or cool;
absorption/evaporation must be nonnegative. Component energy ledger reduces over
MPI. These fields are supplied snapshots; actual ray/evap/radiation calls and
pressure-to-VOF/advection coupling have NOT been wired into a timestep yet.

166 Python tests pass. Independent 1D variable-coefficient manufactured pressure
reference checks sign/through-flow; source tests check conduction replacement,
no double count, signed radiation and corrections. Tests do NOT compile or run the
new native projection. Native OpenFOAM build/MPI remains pending. Input NO_WRITE;
no solver time advance or production/performance claim. Default LPBF unchanged.

Next: actual momentum/VOF timestep, optical/source generation, interface flux and
moving history; integrate pressure phi as VOF authority, not reinterpolate U phi.
Projection presently uses externally supplied rho/U, not mapped mixture state.
Source ownership declaration is an audit contract, not proof of existing solver
ownership. Conservative interface flux must still be matched with global thermal
boundaries; this delta ledger alone cannot establish regional physical closure.
No new Ubuntu parameter screen or standalone user-run audit requested.


## 2026-10-09: preserve capacity moments through regional remapping

Native state handoff now conservatively maps sensible capacity endpoints [J/m3/K]
and latent capacity [J/m3] alongside energy, alpha and latent-energy inventory.
The capacities are moments of the source coefficients, NOT regenerated from mapped
alpha. This preserves uniform T across interface mapping and keeps a fully liquid
metal/cold gas crossing admissible. Fixed phase inventory is reconstructed using
mapped capacity. No clipping, arbitrary neighbor redistribution or energy deletion.

Added m247CapacityEnthalpy.H and persistent-moment m247RegionalState overload.
Import coefficients from alpha only once at original checkpoint; repeated regional
moves MUST supply the stored moments. Native mixed audit now reports schema2 and
capacityMomentsMapped=1, uses mapped closure for local inverse/delta checks.
Global energy-only correction still preserves original global inventories.

160 Python tests pass, including fully molten/gas interface, uniform temperature,
two sequential remaps of nonmatching partitions, moment integrals, invalid energy,
and signed energy changes. Native build/MPI remains unverified; no acceleration
claim. These are thermodynamic remap diagnostics, NOT a solved local CFD system.

Remaining: momentum/VOF transport and correction ownership, pressure/open boundary,
energy-source/interface flux accounting, moving persistent field migration,
native fixture and integrated acceptance driver. Moment evolution/advection must
be supplied with the local equations; recomputing cp/rho/L from averaged alpha
would discard these moments and reintroduce the error. Existing TEqn is unchanged;
its advective compatibility with the moment formulation is not established.
No new Ubuntu micro-screen requested.


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
