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
