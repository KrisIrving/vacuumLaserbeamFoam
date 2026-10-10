## 2026-10-10: opt-in packed optical broadcast and gated full pair

Next implementation after failed lagged optics and ineffective thermal cache:
packedRayBroadcast(defaultfalse), preserving every-step optical updates.
Only final per-wave Pstream broadcast representation changes; combineGather
and ray ordering, stepping/absorption/handoff/termination are unchanged.
Seven scalar values+three labels+two byte flags copied individually with
memcpy to List<char>, broadcastList and exact reconstruction. No raw copying
of polymorphic compactRay, pointers or padding; no conversion of label to scalar.
Requires recordRayPaths false and rejects nonempty paths. Overflow/truncation/
invalid flag guards. Homogeneous scalar/label ABI as native contiguous MPI
transfers, not a portable file format. Empty arrays explicitly supported.

Native m247RayWireCheck exercises0,1,7,1536ray messages on48ranks including
signed zero/scalar extrema/label limits/flags; checks field and byte roundtrip.
RunPackedRayPair rebuilds changed library/dependent solver/checker with official
wmakeLnInclude/wmake only; no wclean/timeouts/kill. Gates library feature marker
and MPI checker before any optical/CFD work. Both frozen180us optical jobs
finish before BOTH transient jobs; identical input fields, Deposition/rayQ,
deposited power and optical work counts required. No time or T/alpha/epsilon/U
advancement permitted during frozen trace. Failure packages archive and stops.
Then full756k180..190us48rank matched-initial/partition10us pair automatically.
Baseline old stream broadcast vs packed candidate; both every-step optics and
thermal cachefalse. Strict sampled field/physical diagnostic/corrector/optical
work equality required; completion is not a production approval.

Package includes all wire/frozen logs even if incomplete; variant names explicit.
Local40tests(39pass,1Windows symlink skip),Python compilation and Bash syntax
pass. Native OpenFOAM/MPI compilation and performance cannot be checked here.
No measured benefit yet. This does not route rays to owners or balance optical
work; blocking broadcast cost still includes imbalance wait. Serialization
change might save little/nothing; do not claim it solves major scaling cost.
Long-track/local-global coupled solution remains outstanding.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunPackedRayPair
Send one M247_packed-ray-pair-<timestamp>_review.tar.gz, even if failed.
Details: tests/m247Performance/PACKED_RAYS.md.

## 2026-10-10 122734: invariant thermal cache equivalent but no measured speed benefit

Review archive complete, wrapper exit0, missing files0; every manifest SHA256
verified. Ubuntu OpenFOAM v2512 compile/link succeeded. Both180..190us full
756000cell48-rank runs completed834steps; all initial fields and partitions
matched, source unchanged. Both thermal gates and exact sampled equivalence
passed: all T/alpha/epsilon/U/p_rgh differences at185 and190us zero; all
compared physical diagnostics and keyhole depths identical. Mean thermal
correctors14.54676259,max18,limit hits0 in both. Cache records834 in each.

Baseline solver1653.52078s(27.5587min), cache1674.08059s(27.9013min),
speedup0.987719: candidate1.2434%longer. Thermal542.73022->548.13480s(+0.996%),
laser849.64750->844.83857s(-0.566%),pressure144.98111->158.59165s(+9.388%).
Single sequential pair does not isolate a systematic cache slowdown from
machine/run variability. It DOES provide no measured acceleration and no
reason to enable this optional cache or repeat it. Defaultfalse retained.
Numerical equivalence at sampled times is not a long-track production approval.

Baseline modules: laser51.433%,thermal32.854%,pressure8.776%,momentum3.117%,
alpha2.551%. These are mature-state10us measurements, not an attribution of
all29.18hours of the older full200us run. Historical thermal151correctors/step
was fixed by previous phase/enthalpy work; current14.55correctors is not the
same old bottleneck. Do not extrapolate this single mature segment into a
24h4um guarantee, combine unvalidated speedups, or claim tiny invariant-cache
work solves the major cost problem.

Decision checkpoint: stop the lagged-optics approximation (failed molten
interface/phase accuracy), stop invariant-coefficient performance tuning
(no saving). No additional Ubuntu rerun requested for either experiment.
Next major development target is exact every-step optical parallel transport
and workload balance, with unchanged rays/path stepping/absorption/cutoff.
Current replicated ray lists combineGather+broadcast after local tracing;
blocking exchange times include idle ranks waiting for expensive tracing.
Top2trace ~49% persists. Do not label94.7%exchange as pure network transfer
or repeat rejected rayQ-weighted Scotch (previously slower and physics failed).

Implementation constraints for next optics transport development:
- Preserve baseline route and default configuration for reproducible comparison.
- Keep mesh/CFD decomposition and every-step optics identical; optical work
  routing must not silently change cell owner or absorption deposition owner.
- Account for every ray by globalRayIndex, route position/direction/power and
  termination consistently, reject duplicate ownership rather than lose energy.
- Verify frozen deposition distribution plus total power and ray termination
  before full180..190us matched-field/cost comparison. These are validation
  stages of transport correctness, not another mesh/threshold screening sweep.
- Rebuild only modified library and dependent solver with official wmake;
  package any build/validation failure in one uniquely named review archive.
Moving local CFD/global heat remains long-track architectural work; optical
transport is a substantial prerequisite, not an already achieved coupled solver.
No new optics implementation or measured speedup is claimed by this checkpoint.

## 2026-10-10 122036: reject current lagged optics; invariant thermal cache pair

Laser refresh impact archive complete, exit0, no missing files; all manifest
file hashes verified. Liquid-metal T RMS185..190us3.73255->14.16624K;
interface RMS4.17808->16.14118K. Worst T difference903.176K at(92,508,4)um,
alpha0.422385/0.341227,epsilon1/1: a molten interface error, not gas-only.
MetalEither max713.022K. Liquid-metal epsilon max0.292854 at nearlypuremetal
alpha~1,epsilon1/0.707146; liquid-metal phase flips3->7 (epsilon>=0.5).
Largest epsilon1-versus0 difference still lies at alpha~0.05 material override,
but that does not dismiss real liquid-metal phase errors. Liquid-metal U max
5.83939m/s,RMS0.102343m/s; p_rgh max408.472kPa,RMS5.88153kPa.
Optical workload imbalance unchanged: top2trace fraction49.166/49.011%.
Current interval2 approximation is not accepted despite25%wall saving and
near-identical keyhole depth. Default remains every-step optical refresh.
No evidence of thermal instability; source-lag feedback causes differences
on same input mesh/partition. No tighter-threshold sweep requested now.

Next implementation: opt-in thermalInvariantCache(defaultfalse). rhoCp and
rhophicp are assigned before TEqn correctors and unchanged inside the loop.
Cache only fvc::ddt(rhoCp)+fvc::div(rhophicp) per TEqn invocation, reusing this
explicit coefficient in fvm::Sp for either radiation branch. Cache rebuilt on
every TEqn call, not across CFD steps. Radiation/evaporation/thermal damper,
latent heat RHS, T and epsilon updates remain recomputed per corrector.
No full matrix reuse or changed tolerances/caps. autoPtr holds a field;
fvm::Sp reads its const field, avoiding consumption of a reusable owning tmp.
Default branch retains original expression. No measured speed claim yet;
this targets redundant thermal work and may give only a modest benefit.
Major long-track acceleration still requires scalable optics/local coupling.

RunThermalCachePair makes two new full756000cell copies from180us input,
180..190us48ranks, identical initial fields/partition, every-step laser calls
validated on both. Baseline cachefalse vs candidate cachetrue. Existing
fullMelt/localMelt directory names label two FULL meshes for compatibility.
Checks native cache marker and per-step diagnostics, thermal gates, same
snapshot fields/physical diagnostics/steps/mean corrector count. Exact sampled
field and diagnostic equality is required by thermal_cache_equivalence_gate;
a completed run alone never implies equivalence or production approval.
Build only solver with official wmake, no wclean/library rebuild/timeout/kill.
Native OpenFOAM build and benefit must be checked on Ubuntu. Local33checks
before added gate tests pass(32pass,1symlinkskip); final26checks(25pass,1skip)
include3new strict-equivalence tests; Bash syntax passes. No native build here.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunThermalCachePair
Return one M247_thermal-cache-pair-<timestamp>_review.tar.gz, even if failed.
Expected wall budget based on recent baseline is roughly55minutes plus build
and postprocessing for the pair, not a guarantee or production runtime estimate.

## 2026-10-10 112226: laser refresh measured saving with unresolved physics error

Archive verified against every manifest SHA256; wrapper exit0, missing files0.
OpenFOAM v2512 solver compile/link succeeded after Foam::pow qualification.
The alphaEqn.H dependency warning did not prevent compilation or execution.
Both756000cell full-domain cases have identical initial fields and all48
cellProcAddressing hashes. Both180..190us CFD runs completed834steps with
thermal gates true, max18correctors and zero thermal limit hits.
Baseline1642.2865s(27.37min), candidate1231.2856s(20.52min):1.3338x,
25.025%less solver wall. Laser section858.447->429.970s; thermal534.692->540.995s.
Candidate418updates/416held steps; held age<=12.239ns,alpha change<=0.026183,
motion<=0.115379cells. Guard compliance is not physical acceptance.
At190us Tmax4193.418->4388.374K(+4.649%),pVapMax+30.050%,QvMax+27.968%,
deposited power326.628->323.519W(-0.952%). T field max difference903.176K,
RMS2.964K; alpha max0.286795. At185us T max difference154.335K,RMS0.726K.
Error grows within10us. Keyhole depth difference190us+0.09749um on8um grid
and liquid volume difference+0.0048448% do not excuse peak/interface error.
RecoilZ relative change53.27% on a small component must be read with its
absolute change3.6791e-5N. No production approval; default refresh interval1.

Next: read existing CSV snapshots, localize liquid-metal/interface/gas errors
before changing guard thresholds. New CollectLaserRefreshImpact uses current
completed run as default; no build, OpenFOAM commands, or CFD advancement.
Collector now validates optical profile counts against actual refresh updates,
not CFD steps. Full domains have no cold cut; that region is marked inapplicable.
15 relevant tests pass; actual834/418-call archived profiles validate; Bash syntax
passes. Full CSV snapshots remain on Ubuntu and are absent from the review
archive, so spatial localization must run there. No repeat CFD requested yet.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/CollectLaserRefreshImpact
Return one M247_laser-refresh-impact-<timestamp>_review.tar.gz.
Moving/global thermal coupling remains necessary for the long-track target;
this measured25% saving alone does not establish24h4um feasibility.

## 2026-10-10 111746: laser refresh scalar pow namespace build fix

The laser-refresh-pair review archive failed during the solver build, before
CFD started. laserRefreshUpdate.H called unqualified pow(double,double),
which is ambiguous between the global math function and Foam::pow in
OpenFOAM v2512. This was an implementation error introduced by this experiment.
Qualify the call as Foam::pow and use scalar(1)/scalar(3) for the exponent.
The compiler candidate list confirms that Foam::pow(double,double) exists.
No controls, approximation bounds, source checkpoint, or physics were changed.
The alphaEqn.H wmkdepend warning is separate from this fatal compiler error.

Retry: git pull --ff-only origin feat/m247-material-port
       bash tests/m247Performance/RunLaserRefreshPair
The wrapper uses official solver-only wmake, without wclean or library rebuild,
and packages failures as well as completed comparisons. Return its new archive.
Native OpenFOAM compilation remains an Ubuntu check; local Python checks do
not substitute for it. The experiment is still not production approved.

## 2026-10-10 103418: localized interface errors; bounded optics refresh experiment

Impact archive complete; no CFD advanced. At190us liquidMetalEither T RMS4.280K,
max237.681K at(76,356,-4)um,alpha0.6523/0.6330,epsilon1/1:
this is a keyhole liquid-interface hotspot, not a dismissible gas-only error.
Liquid-metal epsilon RMS0.001082,max0.04926; zero epsilon>=0.5 flips in this
region or metalEither. All70phase flips lie near alpha0.05 switching threshold,
not bulk metal solidification. Interface alpha max0.09933; liquid-interface
alpha max0.07720 at(100,532,-4)um. All-domain large U error is mainly gas;
liquid-metal U RMS0.03097m/s,max1.539m/s. Cold cut48um reservoir T max1.18e-6K,
U max3.10e-10m/s, but p_rgh max19.546kPa: cold/no-flow cut alone does not
establish pressure independence. Interface T RMS grows3.159->4.777K over5us.
Cannot isolate crop versus changed decomposition from the present pair.
No production approval or larger-crop acceptance inferred.

Laser full/local inner cost869.895/788.757s; mean exchange94.80/93.46% includes
waiting, not pure network bandwidth. Top2trace fractions48.87/36.10%.
Total advances945.835M/945.810M essentially unchanged by20% crop; local
exchange rounds21699vs18926(+14.65%). Repeating rejected rayQ-weighted
Scotch is not the next step. No reinterpretation of isotope depth differences
as sub-grid physical accuracy.

New opt-in solver laser refresh interval(default1 preserves every-call update).
Candidate interval2 holds deposition at most one CFD step; experimental
max age25ns,global filtered-alpha change0.1,global Umax*age/minCellLength0.25.
Trigger crossing forces refresh, as do firstcall/outputTime/mesh change/new
cellcount/additional PIMPLE passes. All ranks reduce the refresh decision
before conditional collectives, avoiding rank divergence on local mesh/cache
conditions. CFD/VOF/properties/thermal/evaporation all still run every step.
This is a source-lag approximation, not exact optical transport acceleration,
and does not implement moving-window/global thermal coupling.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunLaserRefreshPair
Uses identical full756000cell180us serial input twice, same48rank Scotch,
10us180..190us, candidateinterval2 vs baselineinterval1. Rebuild solver only
with official wmake -j8; no wclean/library rebuild/timeout/kill. Both initial
fields exact and candidate cellProcAddressing must match all48reference ranks
before candidate CFD. Two output times must have freshly computed source.
Collector validates per-step refresh bounds, actual optical call counts/rank
profiles, thermal gates, field/ROI/keyhole/power differences and timings.
Existing fullMelt/localMelt archive directory names label reference/candidate
for collector compatibility; BOTH are full domains in this experiment.
Return one M247_laser-refresh-pair-<timestamp>_review.tar.gz, even if build fails.
Local checks30tests(29pass,1Windows symlink skip),Bash syntax/Python compile/LF;
no native OpenFOAM compiler available here. New C++ must compile on Ubuntu.
Expected benefit is conditional: reducing half the50.7% laser workload would
ideally save~25%total, before guards/overhead/physics limits. This is not measured.
Moving local/global-thermal remains the long-track direction; current1.23x
crop is insufficient for24h4um or1.5..2mm production. First obtain a faster
physically acceptable optics mode; do not weaken physics gates for speed.

## 2026-10-10: real prepared full/local pair COMPLETE; impact localization next

Archive213729 passes all manifest hashes and reports complete/source_unchanged/
measurement_quality_gate true. Both834steps180..190us48ranks, thermal residual
gates pass, mean correctors14.55,max18,zero cap hits. dt11.945..12.239ns,
maxCo~0.10060. Both use default isoAlpha (missing reconstructionScheme warning).
Full756000cells1720.98s28.68min; local604800cells1398.56s23.31min:
1.23054x,18.735% less solver wall. Loop1.23063x. Prep/postprocess not included.
Full/local mean module times(s): laser871.71/789.92,thermal569.33/412.61,
pressure147.25/101.13,momentum66.09/37.53. Local laser56.54%,thermal29.53%.
Initial604800retained cells exactly match. Cut834records all inactive,
maximumT1343.150008K,epsilon0,U2.94e-10m/s; no active-melt/cut contact.
185us depth300.27333/300.28487um;190us299.77619/299.79078um;
difference0.01154/0.01459um (iso-surface difference, not sub-grid accuracy).
Final retained T weightedRMS1.0075K BUT max237.68K;alpha max0.09933;
epsilon max1,RMS0.01098;Uz RMS0.03730m/s,max14.875m/s;
p_rgh RMS1682.55Pa,max242707.74Pa. Liquid volume difference-0.007254%.
Final Tmax differs1.246%,pVapMax7.705%,QvMax7.516%,depositedPower-0.4154%,
evaporationPower-0.4516%,recoilForceZ29.05%. Do not approve physics based
only on mean temperature/keyhole agreement; local maxima need localization.

Laser profiler2intervals/rank records complete. In last interval full trace
mean16.74s,max244.58s; local mean18.19s,max190.27s;mean exchange415.30/366.37s.
Top two ranks carry48.87%/36.10% of total trace time over10us. Exchange includes
waiting: these values do NOT establish network bandwidth as bottleneck.
Trace imbalance/communication scheduling remain the major laser target;
repeat of prior weighted repartition is not automatically justified.

Next command: bash tests/m247Performance/CollectLocalMeltImpact
Existing mid/final native CSV snapshots only: gasBoth,metalEither,interfaceEither,
liquidMetalEither,coldCutReservoir; maximum locations,weighted norms,phase flips,
worst20cells; validated stage/rank laser profile. No CFD, rebuild or OpenFOAM
utility run. One M247_local-melt-impact-<timestamp>_review.tar.gz.
This is analysis of the completed physical test, not another mesh screening.
Current20% crop alone is insufficient for target24h4um/long tracks. Select
moving/local envelope and optical parallel changes after determining whether
large differences are in retained liquid metal or primarily phase/interface/gas.
Package fix: identical duplicate archive names coalesced; conflicting contents
rejected. Original archive duplicated two solver members with identical hashes.
Production approval remainsfalse.
Local checks:205test cases completed with1Windows symlink skip;
additional output-time-roundoff regression passes(7localization tests).
Actual uploaded laser profiles validated. Normalize only serialization
drift<=1e-12s; reject missing/shifted samples, no nearest-time sampling
or interpolation.

## 2026-10-09 211303: checkpoint field preparation PASS; run real prepared pair

Uploaded M247_local-melt-fields-20261009-211303: exit0,stage=prepared;
all retained canonical hashes and source hashes identical, no errors.
Five held BC value errors0;6300cutfaces,activeCutFaces0;
cutMetalTmax1343.150000424K,epsilon0,Umax8.7143e-11m/s.
This gives143.85K initial margin below the1487K solidus threshold.
patchSummary reads18volume fields; it does NOT list surface fields.
setExprBoundaryFields successfully wrote phi/alphaPhi cut values; their
solver restart compatibility still needs the real run, not a claimed
all-field native validation. No CFD advanced, no measured speedup yet.

Next: git pull --ff-only origin feat/m247-material-port
      bash tests/m247Performance/RunPreparedLocalMeltPair
Use existing164947/fullMelt serial reference and verified211303/localMelt.
Fresh copies only, matched constants/fvSolution/fvSchemes, native initial
retained-field comparison,3D mesh gates, same scotch48ranks, same180..190us.
Normal foreground decomposePar/mpirun/reconstructPar/postProcess; no
forced timeout/kill/rebuild. Binary diagnostics marker required before CFD.
Source hashes now cover serial180us fields as well as decomposed inputs.
Output: solver timings/module costs, thermal residual/limit gate,
185/190us retained-field/ROI inventories and connected keyhole depth,
per-step cold-cut/flux diagnostics. Production approval remainsfalse.
Local checks:205test cases completed with1Windows symlink skip;
additional output-time-roundoff regression passes(7localization tests).
Actual uploaded laser profiles validated. Normalize only serialization
drift<=1e-12s; reject missing/shifted samples, no nearest-time sampling
or interpolation.
Return one M247_local-melt-prepared-pair-<timestamp>_review.tar.gz, even
on failure. Native CFD still requires Ubuntu; local Python tests18cases,
17passed and1Windows symlink permission skip; Bash syntax/LF checked.
Do not rerun old RunLocalMeltPair preparation/rebuild wrapper.
A20% cell reduction alone cannot establish the acceleration needed for
long tracks; use this direct accuracy/cost result to choose larger local
reductions/moving-window coupling next, instead of more screening.

## 2026-10-09 202509: official mesh repair PASS; prepare checkpoint field boundaries

Ubuntu review M247_local-melt-mesh-repair-20261009-202509: exit0,
604800 cells, 3 geometric and solution directions, Mesh OK; localCut6300
faces/startFace1830240 preserved. Only empty->patch and inGroups() changed.
20% fewer cells than756000 is a mesh reduction, NOT measured speedup.
No CFD advanced. Field empty boundary conditions still require repair.

Next: bash tests/m247Performance/PrepareLocalMeltFields
Default source is the successful202509 repaired copy. Copies constant/system/
180us into a fresh physical path; source remains unchanged. Official
foamDictionary replaces all localCut BC dictionaries with readable temporary
BCs; official setExprBoundaryFields initializes five primary held values from
internalField(field). Surface cut flux is explicitly initialized as U_owner dot
Sf, alphaPhi as alpha_owner times flux; this is an initialization approximation,
not a reproduced original cut flux or validated conservative handoff.
Final primary types: T/alpha.metal/epsilon1/U fixedValue, p_rgh fixedFluxPressure.
Other checkpoint volume fields use zeroGradient; surface fields calculated.

Checks: actual3D mesh, all checkpoint classes supported, mandatory fields;
17-digit canonical hashes of internal fields/dimensions/other three boundaries
and mesh unchanged; original source hashes unchanged; official patchSummary
reads fields; existing read-only m247LocalMeltAudit -verifyCut verifies five
serialized held values and cold inactive cut. No custom field-writing helper,
rebuild, solver, forced process stop or input cleanup. Keep RunLocalMeltPair
suspended. This step prepares fields only; full/local180-190us comparison is
still needed before any physical accuracy or runtime claim. Bash syntax/LF
verified here; actual v2512 utility execution requires Ubuntu.

Official sources checked:
https://api.openfoam.com/2512/setExprBoundaryFields_8C_source.html
https://api.openfoam.com/2512/foamDictionary_8C_source.html
https://www.openfoam.com/index.php/news/main-news/openfoam-v2106/pre-processing

## 2026-10-09 201214: diagnosed empty localCut (LM04); official mesh repair only

Preparation archive shows localCut nFaces6300, mesh type empty and inGroups(empty).
All five primary field patch names include localCut; links and checkpoint are
correct. checkMesh returns0 and Mesh OK BUT reports2 geometric/solution directions
(1 0 1) and incompatible empty-face count. This is NOT an acceptable3D mesh.
Empty fvPatch has no active finite-volume face cells, explaining cutFaces0 in
the native guard; empty field has no value, explaining earlier dictionary error.
The earlier assumption that a new subset patch is an ordinary patch was wrong.

RepairLocalMeltMesh copies constant/system/180us into a fresh work directory,
uses official changeDictionary with explicit boundary/localCut type patch and
empty inGroups, then official checkMesh. Requires3 geometric AND solution
directions, no incompatible empty-face warning; packages before/after boundary
and utility logs. No rebuild, custom initializer, field edits, solver, timeout,
kill or input cleanup. It does not claim a fully prepared CFD case: field empty
BCs and held reservoir initialization must be corrected with standard utilities
before any solver run. RunLocalMeltPair remains suspended.

Command from current linked repository:
  git pull --ff-only origin feat/m247-material-port
  bash tests/m247Performance/RepairLocalMeltMesh
Send one M247_local-melt-mesh-repair-<timestamp>_review.tar.gz.
Native official utility execution remains Ubuntu verification; syntax is checked
locally. No physical accuracy/speedup claim from this preparation check.
Official source: https://api.openfoam.com/2512/changeDictionary_8C_source.html

## 2026-10-09 164947: suspend repeated pair; official read-only preparation audit

Build/linked helper succeeded; subsetMesh succeeded. No CFD advanced.
Initializer rejected a combined guard (wrong time, missing cut, or active cut).
The fatal message did not expose each condition; do NOT guess which condition
failed or relax the guard. Original input hashes remain unchanged. User requests
standard official commands, no aggressive command/process controls.

Do not rerun RunLocalMeltPair yet. Existing initializer/timeout/forced-stop driver
is experimental and is superseded pending preparation diagnosis and redesign.
The intended test is same180..190us full/local physical difference and cost;
none of the latest preparation archives proves a physical speedup.

CollectLocalMeltPreparation uses only official checkMesh and foamDictionary for
read-only diagnosis of EXISTING fullMelt/localMelt copies. Records constant and
180us boundary files, patch names, controlDict, utility help and exit statuses.
No rebuild, native initializer, field edits, solver launch, timeout, kill or
source cleanup. New uniquely named collection directory/archive; directory
links resolved with pwd -P. Invoke from current linked repository:
  bash tests/m247Performance/CollectLocalMeltPreparation
Send automatic M247_local-melt-preparation-<timestamp>_review.tar.gz.

Check which mesh instance/patch actually loads before redesigning preparation.
Prefer standard OpenFOAM utilities and explicit dictionaries for future writes;
normal foreground mpirun execution with logs; no hard timeout/automatic kill.
Compile success is not native/physics validation; prior206Python PASS did not
cover this OpenFOAM mesh/field situation. This collection is NOT a CFD test.

## 2026-10-09 162747: native held cut initialization (LM03)

Verified27 archive manifest SHA256/size entries. Build,180us reconstruction,
selection and subsetMesh all completed. Native subset retained604800/756000
cells at180us. Script failed reading boundaryField/localCut/value through
foamDictionary before CFD; its stderr/patch dictionary were not archived, so
absence of value vs dictionary read limitation is NOT established. This is a
harness error, not evidence of a directory-link issue or physical instability.

User confirms /media is a directory link to ~/OpenFOAM. Resolve source/work
before overlap checks (already used); now record supplied and resolved paths.
Treat aliases as the same physical tree. No copy/move of the user repository
or original checkpoint; only distinct run copies are simulated.

Replace fragile dictionary-value lookup/type edits with opt-in native
m247LocalMeltAudit -initializeCut. Read actual binary/ASCII checkpoint fields,
require180us and an inactive cut, initialize T/alpha/epsilon/U fixedValue and
p_rgh fixedFluxPressure from NATIVE RETAINED OWNER CELL values. Never invent
zero or assume subsetMesh writes a value entry. This explicitly defines a
held owner-cell approximation; it is not claimed to preserve an unknown
subset-interpolated boundary value or to implement global thermal coupling.

Reread files with -verifyCut and check all five serialized types/values against
owner cells; verify initial internal fields/coordinates/volumes unchanged,
then compare to full-domain checkpoint before any decomposition/CFD. Native
helper help output, initialization and verification logs are archived. Default
helper behavior remains read-only. Solver physical equations are unchanged.

207Python checks:206passed,1symlink test skipped (Windows cannot create links).
Native C++ API reviewed against official fvPatchField factory signatures;
actual v2512 compilation/initialization/CFD is pending Ubuntu, not claimed PASS.
No forecasted speedup from20% fewer cells. Next run one fresh pair from the
existing linked repository, without a separate /media source argument:
  cd ~/OpenFOAM/kris-v2512/vacuumLaserbeamFoam-m247
  git pull --ff-only origin feat/m247-material-port
  ./tests/m247Performance/RunLocalMeltPair
Send the automatic M247_local-melt-pair-<timestamp>_review.tar.gz on any outcome.

Official API reviewed:
https://api.openfoam.com/2406/fvPatchField_8H_source.html
https://api.openfoam.com/2512/classFoam_1_1kaqRWallFunctionFvPatchScalarField-members.html

## 2026-10-09 111021: fix subsetMesh command-line incompatibility (LM02)

Verified all26 review manifest sizes/SHA256 values. Build/reconstruction/native
initial export/topoSet completed; subsetMesh failed during argument parsing:
Invalid option: -time. No CFD advanced; source hashes unchanged. This is a
harness developer error, not a physical instability or Ubuntu setup problem.

Selection now retains604800 of756000 cells (80%), cutting only the cold lower
reservoir. Active seeds24867, minimum retained y196um with96um padding.
This establishes20% fewer cells, NOT a measured speedup or physical acceptance.
The compact domain may have limited gains; do not weaken active/buffer gates.

Remove unsupported -time from subsetMesh. Its input time comes from controlDict
startFrom=startTime/startTime=0.00018, now checked immediately before cropping.
Do not replace it with -resultTime (output time only) or unverified -latestTime.
Keep -patch localCut/-overwrite. OpenCFD2506 source creates a missing named
patch; actual2512 run and mapped values remain guarded by native audit.
Capture installed subsetMesh -help-full before preparation and validate required
options. Include this help log in every review package when present.

204Python regression tests PASS. Checks cover wrong/implicit/nonfinite input
times and missing required CLI options. Native subset execution still requires
Ubuntu. Run ONE fresh:
  git pull --ff-only origin feat/m247-material-port
  ./tests/m247Performance/RunLocalMeltPair
The wrapper rebuilds/copies; unchanged180..190us/48ranks/2h per solver budget.
Send automatic M247_local-melt-pair-<timestamp>_review.tar.gz even on failure.
No separate small CFD screening or production acceleration claim.

Official source reviewed:
https://api.openfoam.com/2506/subsetMesh_8C_source.html
User2512 log is the direct evidence that -time is unsupported.

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
