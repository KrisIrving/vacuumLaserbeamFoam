## 2026-10-10 160619: packed broadcast exact, no overall saving; optical load architecture

Archive complete, wrapper exit0,missing files0; all manifest SHA256 checked.
Native library/solver/wire-check utility compiled successfully.48-rank wire
roundtrip passed all4payload sizes. Both frozen180us captures/traces completed
before transient jobs; Deposition/rayQ/input fields, power326.66753538336195W
and optical work matched exactly, no CFD advancement. Both10us834step full
runs complete, thermal/measurement/packed equivalence gates true,source unchanged.
All sampled fields/diagnostics/keyhole outputs identical; max18thermal
correctors,mean14.54676259,zero cap hits. Numerical acceptance at these sampled
states is not production or long-track acceptance.

Solver baseline1628.91063s(27.1485min),packed1691.15014s(28.1858min),
speedup0.963197: candidate3.8209%longer. Laser841.25042->850.43047s(+1.091%),
thermal540.14689->564.97453s(+4.597%),pressure129.90471->152.58129s(+17.456%).
One sequential pair does not establish systematic regression; it establishes
no measured total acceleration. Do not promote packed mode or repeat this pair.
Default packedRayBroadcastfalse and thermalInvariantCachefalse retained;
every-step laser refresh remains mandatory after molten-interface lag failure.

Independent archived rank rows show root0 trace3.73610/3.73677s,gather
820.99912/838.49231s,broadcast9.83095/0.83007s. Representation reduced the
root broadcast timer substantially, but only ~9s compared with1629s job cost;
root gather includes waiting for tracing and communication. Worker broadcast
mean717.719/724.344s is mostly consistent with wait at synchronization, NOT
a direct measurement of payload transport. Timers on different ranks/stages
must not be summed to infer a critical path or pure MPI bandwidth.
Baseline rank44 trace446.26385s,rank46 trace300.68923s;top2~48.825%of aggregate
trace time. Candidate top2~49.336%. Rank44advances309257364,rank46advances
264607646 (~60.67%of945834767total), unchanged exactly. Rank44 alone ~15.7x
mean per-rank advances. This strongly supports addressing work concentration;
packed serialization does not address it. Baseline laser51.694%,thermal33.192%.

Development decision: stop transmission-format and thermal-coefficient micro
trials. Next architectural target is optical work distribution independent of
CFD mesh partition, preserving per-step input updates and deposition return
by global cell identity. Previous rayQ-weighted CFD Scotch was slower and
failed physics gates; do not repeat it or treat the same repartition as a fix.
An optical-only partition must exchange alpha_filtered,n_filtered,resistivity
from CFD owners each step, run corrected handoff/termination and return deposited
energy to CFD cell owners with explicit conservation/duplicate-ownership audits.
Current code has no such separate optical mesh or mapping. No implementation,
performance gain or full-track approval claimed by this checkpoint.

Next prototype gates: conservative cell ownership/mapping on the same mesh;
frozen optical inputs/deposition/power/termination validation, then10us full
physics/cost comparison including map/trace/return costs. This is a coupled
algorithm implementation, not a sweep of packet/threshold settings. One archive
per executable stage; official OpenFOAM utilities,normal completion,no wclean/
timeout/kill. No new Ubuntu test requested until prototype is ready.

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

## 2026-10-09: real fixed-local/full-domain melt pair

094616 thermophysics archive:15manifest hashes/sizes verified; native build and
20step serial/MPI2 gates independently rechecked. Melt fraction0->1->0;
max energyresidual8.9928e-15J, finalserial/MPIE difference8.8818e-16J,
phase/conduction2..3correctors. This confirms infrastructure, not LPBF speed.

Priority changed to direct realistic physics/cost evidence. RunLocalMeltPair
reuses the complete vacuumLaserbeamFoam physics, not the experimental regional
enthalpy closure. Same180us checkpoint,8um,48ranks,180..190us continuous interval,
identical laser/material/thermal controls; corrected-ray flags on in both.
Fullheight fixedlocal submesh retains original cells/resolution. Bounds cover
active material, gasjet and laser path plus96um padding in x/z. No halo sweep.
Reject no-reduction crop, active initialcut, changed initialfield/geometry,
invalid native snapshots, missing diagnostics, incomplete solver/mesh checks.
Initial internal cells are matched at1pm coordinates with volume checks.

Cut T/alpha/epsilon/U values held from the checkpoint; p_rgh fixedFluxPressure.
Retains original top atmospheric pressure outlet and bottom BC. This is an
EXPLICIT short-window boundary approximation, not advancing global thermal
coupling. Default solver remains unchanged unless localMeltBoundaryAudit true.
Candidate cut state/flux recorded EACH timestep, not only stored output.
Same-ROI field RMS/max errors and metal/liquid/meltcentre extents at185/190us;
existing surface-connected alpha=.5 extractor measures matching keyhole depth.
Whole-domain diagnostics are scope-labelled; differing totalinterface areas
must not be mistaken for retained-region physical error. No invented physical
error tolerance or production approval. Real speedup only after native pair.
Includes job/loop/module costs, prep/postprocessing separately; no new moving
or global thermal overhead hidden as a production speedup.

One Ubuntu command,source never simulated in place:
  git pull --ff-only origin feat/m247-material-port
  ./tests/m247Performance/RunLocalMeltPair
Optional source path is first argument if checkpoint is on /media rather than
repository tutorial. Builds optics,solver and read-only native snapshot helper;
2h wall budget per solver case, whole MPI process group terminated on timeout;
all logs/partial reports bundled on failure. Send ONE
M247_local-melt-pair-<timestamp>_review.tar.gz. Large snapshotCSV remain on Ubuntu,
not in reviewarchive. This uses8um first to isolate domain effects before4um.

200Python tests and Bash syntax/raw-LF checks PASS; native added utility and
solver diagnostic build/run pending Ubuntu. Next after actual evidence: replace
held reservoir with advancing global thermal state and conservative exchange,
then translating window handoff. Do not promote fixedcrop to1.5..2mm production.

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

## 2026-10-09: native thermal transport PASS; integrated conduction/phase cycle

Reviewed M247_regional-thermal-transport-20261009-092319_review.tar.gz:
manifest size/SHA256 and native serial/MPI logs verified. eba5bc42 build/run
complete, 20 steps, unchanged inputs, max cumulative energy residual3.7364e-15J;
serial/MPI final energy difference5.9566e-12J. Runtime1.1133s excludes build.
This establishes passive thermodynamic transport, not LPBF acceleration.

Added optional implicit conduction and equilibrium latent closure in the existing
local thermal time loop. cp/latent capacities remain conservative transported
moments. Backward-Euler conduction solves a tangent linearization of total
enthalpy; both energy residual and nonlinear temperature/conductivity change
must converge, maximum60 correctors. Recover sensible/latent/reserve from the
conserved energy after solving, without resetting energy from temperature.
Processor conductivity patches exchange neighbouring values; physical patches
use zeroGradient in this fixture. Conductive face flux feeds the cumulative
energy ledger. Invalid fields, controls, nonconvergence fail explicitly.

One --physics command integrates20 flow/VOF/thermal steps: initial1500K solid,
10 heating +10 cooling, source3e13W/m3 scaled by cp capacity/6280500.
Checks conduction actually redistributes energy, capacity-weighted melt fraction
reaches>.5 then falls>.25, phase bounds, nonlinear convergence, cumulative energy,
existing VOF/mass/pressure gates, serial/MPI and unchanged inputs. Gas extrema
alone cannot pass melting. No parameter sweep or production case used.

Local validation:189 Python tests and Bash syntax PASS. C++ native compilation
and numerical execution are pending Ubuntu. This common Ts/Tl capacity closure
is experimental; it is not established equivalent to the legacy filtered alpha
and gas phase thresholds or TEqn. Thermal feedback into momentum, true ray
sources, evaporation/radiation/recoil/Marangoni, moving geometry and repeated
global thermal exchange remain pending. No production approval or speedup claim.

Ubuntu (one archive on success/failure; build300s + runtime600s budgets):
  git pull --ff-only origin feat/m247-material-port
  ./tests/m247Performance/RunRegionalAcceptance --physics
Send M247_regional-thermophysics-<timestamp>_review.tar.gz.
Next development integrates physical sources/phase-flow feedback and moving
history into this loop before a realistic4um wall-cost/physics comparison.


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

2026-10-08: protected164709 native pass closes sparse wake selector issue. Added opt-in runtime moving mesh using existing full-solver isoAdvector/CorrectPhi path and bounded0.2us48-rank RunMovingCFDPilot; native integration pending,124Python tests pass.

2026-10-08: Protected162215 smoke caught48 hot cells never refined; no large run. Replace protected-mode point-average candidate selection with exact binary-cell hook, require8 native selection witnesses; archive failure fixture and error register added. 120 local tests pass; native fix still pending.

2026-10-08: 160259 moving-window native prototype passed; peak1.32048M cells,58.40s updates. Added opt-in frozen hot/molten wake retention with strict marker/coverage gates and protected small preflight; 118 tests pass, new native run pending.

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

# Development changelog

## 2026-10-08 — Local CFD compatibility passes; frozen grid/input optics

11042223archivehashes verified;projectedphi divL1~9.84e-10/s;0.2us22steps
133.14s,no thermalcaps,boundedalpha/epsilon,finaldivL1.01164/s. Compatibility
only:globalT4448K/power288W versusearliercoarse requirematchedopticalisolation.
Addedthree frozen opticalroleswithrestrictedmapping/protectedhashes/reconciled
profiles andnamedarchive;noCFD/C++changes/production approval.103Pythontests/Bash
pass;nativeorchestration pendingUbuntu. NextRunLocalOptics.

## 2026-10-08 — Mapped phi continuity rejected; projection and gated pilot

10482112archivehashesverified, nativebuild/readchecks pass; fine divL1~88759
versuscoarse0.02664/s, restartblocked. Explicit copiedphi-only geometric
projection withprotected-fieldhashes andrereadcontinuity; ifpassed, gated
48rank0.2us/15minute CFD pilot plusnative finalbounds/thermalchecks. Original
cases retained, no production/matchedspeedup claim.100Python tests/Bash pass;
newnative projection/time option pendingUbuntu. NextRunLocalFluxPilot.

## 2026-10-08 — Coplanar transitions qualified; mapped restart flux audit

10110123archive hashes valid,both variants complete2.284/2.889millioncells,
moments pass,native concavity onlyfailure. Outward distances<=8.7e-19m/1.02e-13
relative;official test includesplanar pairs. Retain strictfailure and add narrow
coplanar geometry screening,notproduction. Added AuditLocalRestart freshquality,
unchangedfield/meshhashes andnative U/phi/alphaPhi continuity diagnostics on
existingmeshes;noCFD/refinement/fieldwrites.96Python tests/Bashpass;nativefluxmode
pendingUbuntu. Next AuditLocalRestart,send automaticlocal-restartarchive.

## 2026-10-08 — Local refinement concavity rejection and recovery

13archive hashes verified;4-layer mesh2.284million cells,all four mapped moments
pass,15101concave cells fail native mesh quality.10-layer execution absent.
Keep rejection. Save partial/final reports and continue independent variants;
add hash-checked serial-only --resume and native failed-set plane-distance/bounds
diagnostic. No CFD/quality waiver/speedup approval.92Python tests/Bash pass;
native diagnostic pendingUbuntu. Next PreviewLocalRefinement --resume003900.

## 2026-10-08 — Region budget passes; local mesh sizing previews

Verified 30 archive hashes and independently reproduced the regional report.
12 snapshots bounded; molten minimum clearance136um; original late keyhole
still grows0.870376um/us. Padded active box covers77.5pct, so added field-driven
static previews preserving powder interfaces/warm cells with4/10-layer halos,
native hex refinement,3million-cell budget,mapping moments and mesh quality.
Only copied fields change; no CFD. Automatic distinctly named archive on
success/failure.88Python tests/Bash syntax pass; native build/run pendingUbuntu.
Next pull and PreviewLocalRefinement; no repeated region audit required.

## 2026-10-08 — Region audit meshTools dependency repair

User v2512 build fails on missing cyclicAMIPolyPatch.H through fvCFD.H.
Added meshTools include/link dependencies and clean the audit target before
rebuild. No solver equations, fields or audit semantics change. Bash/static
checks pass; actual Ubuntu build pending. Pull and rerun InspectRegionBudget;
existing fields reused and a fresh named review archive generated automatically.

## 2026-10-08 — Ray impact reviewed; regional/domain cost audit

Verified32archivehashes,166convergedsteps/no caps and full corrected MPI/cutoff
records. Strict legacy equality fails; metal maxT50.631K/maxU0.08873m/s, final
absorbed-power change0.0590%; no physical promotion. Original late keyhole still
grows0.87um/us. Added read-only48-rank field envelope/volume/mask utility and
InspectRegionBudget with automatic provenance/archive, boundary clearances,
keyhole trend and explicit fine-mesh/full-track cost scenarios. No CFD equations,
source fields or defaults changed.85Python tests/Bash syntax pass; Ubuntu utility
build/reductions pending. Regional sizing feeds local refinement and conservative
thermal/fluid coupling development, not another legacy/corrected CFD pair.

## 2026-10-07 — Corrected transient cache pass; physical impact harness

Verified31archivehashes/full interval and correction/rank records.166 converged steps/no caps, seven reported final-field differences0; strict regression/performance pass,377.372 to349.341s (1.08024x). Added cached original-partition legacy/corrected180–182us impact pair with expected policy switches, strict equality reporting, separate execution gate, per-step correction accounting and automatic regional/worst-cell localization. No new solver algorithm or physical approval.76 Python tests and Bash syntax pass; Ubuntu impact run pending.

## 2026-10-07 — Frozen optical partition regression passes

Verified 29 archive hashes and complete fixed-state profiles/provenance. Both corrections reduce power partition delta to 1.7e-13 W and spatial relative differences to about 1e-14, with equal advances/interface/bulk/cutoff counts and discarded power. Added RunRayTraversal --corrected for original-partition cache off/on coupled 180–182-us validation, both corrections enabled. Preparation explicitly disables frozen mode and corrections in ordinary probes. Collector verifies per-call correction coverage/bounds and equal work alongside existing strict physics/thermal/field/performance gates.74 Python tests and Bash syntax pass; coupled Ubuntu test pending. No production or weighted-partition approval.

## 2026-10-07 — Handoff sensitivity reduced; consistent cutoff candidate

Verified 29 archive hashes, MPI packet/search checks, frozen profiles, binary provenance and zero reported shared-input differences. Handoff correction reduces power delta from 2.346 W to 2.563e-5 W, but strict power/spatial gates still fail. Added default-off consistentRayTermination to apply the existing ray-power cutoff every local iteration, with stopped-ray/discarded-power accounting and collector bounds. RunFrozenLaser --termination enables both candidates only in copied frozen cases and produces a distinct archive.71 local Python tests and Bash syntax pass; OpenFOAM compilation/optical regression pending Ubuntu. No promotion or speedup claim.

## 2026-10-07 — Frozen optical sensitivity; pending-sample candidate

Verified all 29 archive hashes and independently reparsed one-call/1536-ray frozen profiles. Shared input norms zero; absorbed power differs 2.346 W and spatial fields fail. Added default-off preserveRayHandoffSample to process the sender's moved-to point on receipt before another step; ray state is serialized/reset/compared. Added real MPI packet checks and RunFrozenLaser --handoff with mode/work/packet gates and distinct archive. No equivalence, speedup, unique-cause or production approval claim; actual OpenFOAM build and regression pending Ubuntu.

## 2026-10-07 — Shared-input fixed-state optical probe

Added default-off solver capture/trace diagnostics and RunFrozenLaser. Generates one shared set of filtered alpha/normal/resistivity, checks exact initial internal fields and optical inputs across decompositions, then traces once per partition at 180 us without flow/thermal/time advancement. Checks frozen state, capture/trace provenance, 1536-ray sampling, rank/global profiles, deposition/rayQ spatial norms and absorbed power. Normal update/report path retained. Automatic rebuild, preflight, budgets and archive packaging. Actual OpenFOAM build/execution pending Ubuntu; no speedup or production approval claim.

## 2026-10-07 — Weighted partition rejected; isolate optical sensitivity

Verified all 25 archive hashes and independently checked both complete logs, binary/input provenance, thermal convergence, sampling and global/rank profiles. Weighted repartition improves tracing balance but increases job time by 39.63%, exchange rounds by 2.27x and thermal cost by 74.7%. Seven final field norms and physical diagnostics fail; initial internal field checks report zero differences. Retain original partition. Next development is fixed-state optical comparison across decompositions; no additional Ubuntu run requested in this review. Raw field norms were generated on Ubuntu, not recomputed from this archive.

## 2026-10-07 — Ray-weighted partition benchmark

Added a matched original/weighted Scotch benchmark using checkpoint rayQ, native reconstruction/decomposition, exact initial checks and serial global final-field comparison. Retains validated cache, sampling and thermal controls; verifies rank counters within each partition without demanding equal cross-partition work. Each CFD job is budgeted at 30 minutes. Automatic archives include native logs, initial checks, weights and distinct variant evidence. No solver code changes or measured acceleration claim; Ubuntu validation pending.

## 2026-10-07 — Seed recovery complete; tracing distribution target

210403recovery27hashes verified; full logs independently confirm matched
180–182-us physics/work and thermal convergence. Seed performance still fails,
switch remains off; validated cache retained.21ranks search nothing;44/46carry
58.314% of searches. Record next tracing distribution/backend and local-domain
targets. No code change or additional Ubuntu action. See
entries/2026-10-07-m247-seed-recovery-verified.md.

## 2026-10-07 — Seed performance FAIL; repair review packaging

204122report:seven fields equal/work matched,no thermal caps,but job0.98492x
and performance gate false. Parity322560/0; only244eligible cells. Do not
promote or repeat seed candidate. Archive omitted seed variants due to stale
packaging whitelist; full-log audit pending recovery. Import shared preparation
catalog and add RepackageReview for collection only with original files retained.
60Python tests/Bash syntax pass. See entries/2026-10-07-m247-seed-search-result.md.

## 2026-10-07 — Broader cache PASS and seed search candidate

201432archive hashes/log/work/thermal checks pass; seven saved-field norms zero.
Job400.4→334.3s,1.19758x; loop1.19772x. Added default-off strict Cartesian
seed interior shortcut with legacy fallback and per-call geometry rebuilding.
RunRaySeedSearch isolates the new switch atop validated cache,expanded real-mesh
parity and marker/runtime gates,2us/30-minute budget and tagged archive.
59Python tests/Bash syntax pass; new OpenFOAM build/CFD pending Ubuntu.
See entries/2026-10-07-m247-seed-search-candidate.md.

## 2026-10-07 — Broaden cached traversal regression to2 us

Added ValidateRayTraversal: shared build/parity/run/package pipeline, matched
180–182-us reference/cached cases and30-minute budget per job. Collector rejects
short or mislabelled intervals in validation mode.56 Python tests pass, including
interval and mode rejection; Bash syntax checked. Solver/physics unchanged,
broader OpenFOAM execution pending Ubuntu. See
entries/2026-10-07-m247-traversal-broader-validation.md.

## 2026-10-07 — Cached traversal short validation complete

Collection-200224 integrity and regression/performance gates pass. Seven756k-cell physical/deposition fields have zero differences, search parity and ray-work gates pass. Observed job1.125x/loop1.1385x, inner laser cost minus21.29%. Retain opt-in cache; default/production approval unchanged. Next development broadens paired validation to2us before tracing balance/backend work. No new solver change or additional Ubuntu run in this review. See entries/2026-10-07-m247-cached-traversal-validated.md.

## 2026-10-07 — Recover cached-traversal field collection

195231 build/parity and both jobs pass; logged physics/work agree, job speedup1.125, loop1.1385. Archive has no comparison report. Fix inherited non-debug rayNumber NO_WRITE incompatibility: seven physical/deposition fields mandatory, visual ID optional with explicit absence/partial checks. Added offline InspectRayTraversal and collection stderr packaging; 53 harness tests pass. No solver change or physical approval. See entries/2026-10-07-m247-traversal-195231-collection-fix.md.

## 2026-10-07 — Official ray review and cached traversal candidate

Reviewed tagged upstream V3.0/V3.1 and merged particle-tracing PR113. Added default-off cached step lengths and reusable FIFO search storage with legacy containment/order/limit/fallback semantics. RunRayTraversal builds a real-mesh old/new search test before matched short CFD, checks eight fields and identical ray work, and packages a single named archive. 51 Python tests and Bash syntax pass; actual C++/CFD and speed remain pending Ubuntu. See entries/2026-10-07-m247-official-ray-traversal-candidate.md.

## 2026-10-07 — Exchange profile result and tracing target

193145 archive integrity/build/regression pass; 756k saved cells have identical five-field results. Independent log checks reconcile 96 rank rows. Merge is negligible; tracing strongly concentrated in two ranks, and blocking broadcast includes waits. Recorded evidence and selected equivalent tracing/search optimization before partitioning comparison. No additional CFD request or numerical change in this review. See entries/2026-10-07-m247-exchange-profile-result.md.

## 2026-10-07 — Correct precision target in exchange profiler

Ubuntu compilation exposed precision() being called on messageStream Info. Obtain the underlying Ostream with Info(), then set/restore precision there. This repairs logging only; profiling stages and ray/physics behavior are unchanged. The supplied compiler output is sufficient to identify the failure; its archive was not inspected. Full OpenFOAM compilation remains pending Ubuntu. See entries/2026-10-07-m247-exchange-stream-fix.md.

## 2026-10-07 — Schema-2 exchange and rank profiler

Split outgoing copy/gather/broadcast, measure nested existing merge work, and gather rank tracing/merge counters only at output times. Strict collector reconciles groups and rejects older libraries; automatic archive includes both new CSVs under a laser-exchange tag. Ray transport, merge semantics and physics stay unchanged. 45 Python tests and Bash syntax pass; actual OpenFOAM compilation and regression remain pending Ubuntu. See entries/2026-10-07-m247-laser-exchange-profiler.md.

## 2026-10-07 — Verified laser profiling result

190239 archive passes build/provenance/convergence/instrumentation regression; five saved final fields are identical. Exchange/wait path dominates mean laser time, with strong trace-rank imbalance. Recorded measured evidence and exchange/ownership optimization target; no new solver change or speedup claim in this review. See `entries/2026-10-07-m247-laser-profile-result.md`.

## 2026-10-07 — Refresh laser lnInclude on incremental builds

User compilation exposed a missing new laserPerformance.H link in existing lnInclude. Added explicit refresh/header check in direct profiling build and library Allwmake; failures stop build dispatch. No ray/solver physics changes. Ubuntu rebuild pending. See `entries/2026-10-07-m247-laser-lninclude-fix.md`.

## 2026-10-07 — Default-off laser internal profiler

Added write-time MPI substage means/maxima, work counters and stride128 trace-search sampling without changing ray physics. RunLaserProfile builds/preflights library and solver, compares off/on tight width-zero restarts and packages build/results. Collector gates on unchanged diagnostics/final fields and convergence.42 local Python checks pass; actual OpenFOAM build and measured costs remain pending. See `tests/m247Performance/LASER_PROFILE.md`.

## 2026-10-07 — Phase localization decision

Verified 183545 archive: width response changes interface phase/Darcy state and raw pressure in solid metal despite converged thermal solves. Recorded arithmetic, field and pressure-log evidence; smoothing remains default-off and unapproved. No further width tests requested. Next speed work targets laser substage profiling and equivalent optimization; no new solver change in this review. See `entries/2026-10-07-m247-phase-localization-decision.md`.

## 2026-10-07 — Phase width-response review and offline localization

Valid phase probe converges but large local width differences remain. Added InspectPhaseBlend for existing hard/narrow and narrow/wide final fields, with region/threshold/worst-cell reports and one archive. Checks runtime mode, provenance and fixed mesh; preserves prior outputs. Thirty-seven local tests pass; no new CFD or closure acceptance. See `entries/2026-10-07-m247-phase-blend-result.md`.

## 2026-10-07 — Initialise blend control before createFields property update

Ubuntu build log confirms a missing declaration in both normal and postProcess createFields inclusion. Moved width ownership/initialisation before the first updateProps call; share validation with runtime reload and avoid a shadowed time-loop width. Existing 35 Python checks pass; actual OpenFOAM rebuild remains pending. See `entries/2026-10-07-m247-phase-blend-initialisation-fix.md`.

## 2026-10-07 — Reject stale phase-probe executables

The 170639 archive used the prior binary and failed runtime mode checks. Fixed application build error propagation and argument-parser path; added a direct build/log/archive command and static binary/PATH preflight before phase CFD. MPI launches the verified absolute path. Thirty-five Python tests, Bash syntax and a mocked solver-build failure check pass. Ubuntu build diagnosis pending; no new CFD evidence or closure approval. See `entries/2026-10-07-m247-phase-blend-build-gate.md`.

## 2026-10-07 — Opt-in continuous phase-temperature candidate

Added default-off smooth alpha-phase override, coupled phase/enthalpy diagnostics and a three-way width-sensitivity short probe. Preserves legacy branches outside the transition; numerical closure and restart energy response require validation. Thirty-one local tests pass; Ubuntu compilation/CFD pending. See `entries/2026-10-07-m247-continuous-phase-candidate.md` and `tests/m247Performance/PHASE_BLEND_PROBE.md`.

## 2026-10-07 — Localization diagnosis

Verified existing localization archive. Global large T/U differences are in numerical gas; seven epsilon endpoint flips all cross the hard alpha=0.05 phase-temperature override. Recorded evidence and coupled interface-treatment requirements. No solver changes or new CFD. See `entries/2026-10-07-m247-localization-diagnosis.md`.

## 2026-10-07 — Two-us result and offline field localization

Both candidate tolerances converge over 2 us, but local field maxima remain unresolved. Added offline region/worst-cell localization and one-archive delivery using saved fields, with no extra CFD. Twenty-seven local tests pass. See `entries/2026-10-07-m247-validation-result-localization.md` and `tests/m247Performance/FIELD_LOCALIZATION.md`.

## 2026-10-07 — Longer candidate convergence validation

Added a 180–182-us standard/tighter candidate test with per-step convergence checks, final all-rank internal-field differences, and automatic review archives. Uses the existing candidate binary; physical production approval remains pending. Twenty-five local tests pass. See `entries/2026-10-07-m247-tolerance-validation-tooling.md` and `tests/m247Performance/THERMAL_VALIDATION.md`.

## 2026-10-07 — Ubuntu thermal result and automatic review archives

The 0.2-us Ubuntu candidate converged in 10–14 correctors/step with zero cap hits and reduced job wall from 127.13 to 35.04 s (3.63x). Longer physical validation remains pending. Both test wrappers now automatically package small review files with run/variant names and a SHA256/missing-file manifest; existing runs can be packaged without rerunning. Nineteen local tests and shell syntax checks pass. See `entries/2026-10-07-m247-thermal-probe-result.md`.

## 2026-10-07 — M247 thermal convergence investigation

Reviewed both full Ubuntu logs: all 25,066 phase corrections per run have max increment 1, while T linear solves take 1–2 iterations. Added default-off residual cell diagnostics and an experimental enthalpy slope correction with an additional phase-temperature gate. Added a 0.2-us legacy/candidate probe. Sixteen local harness/model tests pass; Ubuntu build and CFD validation are pending. See `entries/2026-10-07-m247-thermal-log-review.md` and `tests/m247Performance/THERMAL_PROBE.md`.

## 2026-10-07 — M247 performance phase 1

Added opt-in no-ray-history mode, MPI-aware/I/O-inclusive profiling and an
independent180–182-us comparison harness with a wall budget. Defaults preserve
ray history and thermal residual logging. Local tool tests pass; Ubuntu build,
physical comparison and actual speedup remain pending. See
`entries/2026-10-07-m247-performance-phase1.md` and
`tests/m247Performance/README.md`.

## 2026-09-28 — Phase 0/1 bootstrap

Branch: `dev/vacuum-solver`

Changes:
- preserved `main` as exact LaserbeamFoam V3.0 reference;
- created parallel solver `applications/solvers/vacuumLaserbeamFoam`;
- copied V3.0 laserbeamFoam numerical implementation without intentional
  equation/physics changes;
- changed executable/application identity to `vacuumLaserbeamFoam`;
- added persistent `log/` research/development record.

Physics intentionally **not** changed:
- recoil-pressure equation;
- evaporation cooling;
- laser ray tracing/Fresnel absorption;
- VOF equation;
- phase change/latent heat;
- surface tension and Marangoni force;
- pseudo-gas properties;
- radiation.

Additional Phase-1 test infrastructure:
- added `tutorials/vacuumLaserbeamFoam/bootstrapPlate2D` as a smoke test copied from the upstream Plate2D case;
- the copied case changes only the executable/application name and is explicitly not a vacuum-physics validation case.

Next intended code change:
- only after Phase-1 compilation/regression passes, create the evaporation-model
  runtime-selection architecture.

## 2026-09-28 — Phase-1 CI verification

Commit tested: `2ad22fb0930127c9d5ba596a72d37340e3af1d8e`

- OpenFOAM-v2506 `Allwmake`: PASS.
- `vacuumLaserbeamFoam` executable compiled and linked.
- Added bootstrap Plate2D smoke case was explicitly executed by CI.
- Repository `Alltest`: PASS with zero reported solver/command failures.
- Source comparison confirmed 30/33 solver files are byte-identical to V3.0;
  the only differences are the three intended application-identity changes.
- Full field-by-field `laserbeamFoam` vs `vacuumLaserbeamFoam` regression
  remains pending and is intentionally not inferred from the smoke test.

## 2026-09-28 — Phase 2 evaporation-model API

Branch: `feat/vacuum-model-api`

Implemented:
- new `libvacuumEvaporationModels` library;
- runtime-selectable `vacuumEvaporationModel` base class;
- `legacyAnisimov` model containing the exact V3.0 recoil-pressure and
  evaporation-cooling expressions;
- `UEqn.H` now obtains recoil pressure from the model;
- `TEqn.H` now obtains evaporation heat flux from the same model;
- original `p0/Tvap/Mm/LatentHeatVap/R` ownership moved out of solver field
  creation and into the legacy model;
- bootstrap tutorial explicitly selects `legacyAnisimov`.

No near-vacuum/chamber-pressure physics has been added in this change.

### Phase-2 regression infrastructure

Added `tests/legacyEquivalence/Allrun` and a GitHub Actions step that runs the
same one-step Plate2D state through upstream `laserbeamFoam` and
`vacuumLaserbeamFoam + legacyAnisimov`, then byte-compares key output fields.
This turns legacy equivalence into an automated regression gate rather than a
manual assumption.

### Phase-2 verification and closeout

- First CI run `36418680113`: FAIL because the explicit runtime-selection
  iterator type was incompatible with OpenFOAM-v2506.
- Fixed the selector by using C++17 `auto`; no physics change.
- Corrected CI run `36419254818`: PASS.
- Added automated legacy-equivalence regression.
- CI run `36419960056`: PASS.
- Critical fields were byte-identical between upstream `laserbeamFoam` and
  `vacuumLaserbeamFoam + legacyAnisimov` at time `1e-05`.
- Phase 2 is closed; no chamber-pressure or near-vacuum physics is present yet.

### Phase-2 integration

Pull request: #3 — `Phase 2: runtime-selectable evaporation model API`

Merged into:
`dev/vacuum-solver`

Merge commit:
`14a54919e6a484d6b187c0dbedbde0f83b468879`

The protected project baseline `main` remains unchanged at the LaserbeamFoam
V3.0 tree.

## 2026-09-28 — Phase 3 pressure-aware reference model started

Branch: `feat/pressure-aware-reference`

Implemented in this commit:
- new required `constant/vacuumProperties` for vacuumLaserbeamFoam cases;
- model selection moved from `transportProperties` to `vacuumProperties`;
- runtime model constructor now receives separate environment/model and material
  dictionaries;
- base evaporation-model API extended with `saturationPressure()` and
  `massFlux()`;
- `legacyAnisimov` extended with the new API while preserving the exact V3.0
  recoil and cooling operation order;
- new pressure-aware `hertzKnudsen` reference model;
- CI smoke test for the new model.

No final near-vacuum/Knudsen-layer physics has been implemented yet.

### Phase-3 first CI correction

CI run `36425725491` exposed an OpenFOAM-v2506 API compatibility issue in the
model selector: templated `lookup<word>()` is not supported here. The selector
was changed to the dictionary-stream form already used throughout OpenFOAM.
No equation or physical-model change was made by this correction.

### Phase-3 analytical model regression infrastructure

Added `vacuumEvaporationModelTest`, a small diagnostic utility that directly
evaluates the runtime-selected model without solving U/T/p. Added an independent
analytical regression for the Hertz-Knudsen reference closure at multiple
temperature/back-pressure states, including the zero-net-evaporation limit.

### Phase-3 analytical utility build correction

CI run `36427391669` showed that the new diagnostic utility needed the
OpenFOAM `meshTools` include path/library because `fvCFD.H` pulls AMI mesh
types transitively. Added the missing build dependency; no physics code changed.

### Phase-3 analytical utility output correction

CI run `36428017249` showed that `messageStream Info` cannot set stream
precision directly in OpenFOAM-v2506. The regression utility now uses
`std::cout` with 16-digit precision for its machine-readable test line.

### Phase-3 analytical test fixture correction

CI run `36428475347` reached and passed build, tutorials, legacy regression,
and the pressure-aware solver smoke test. The analytical curve regression then
failed before model evaluation because its copied `vacuumProperties` fixture
had an invalid OpenFOAM header. The fixture header was corrected; no production
model code changed in this commit.

### Phase-3 verification complete

Final CI run `36512859745`: PASS.

All Phase-3 gates pass, including the analytical curve regression. The
pressure-aware reference implementation is ready to integrate into
`dev/vacuum-solver`.

Next development target:
Phase 4 will add a literature-derived Knudsen-layer/near-vacuum model in
incremental, analytically tested steps rather than replacing the reference model
in one change.

### Phase-3 integration

Pull request: #4 — `Phase 3: pressure-aware evaporation reference model`

Merged into:
`dev/vacuum-solver`

Merge commit:
`7d1fed9a61ada6add5fc8c177a8f7fdc2e8a531e`

Final verification before merge:
GitHub Actions run `36512859745` — PASS.

The protected project baseline `main` remains unchanged at the LaserbeamFoam
V3.0 tree.

## 2026-09-29 — Phase 4a sonic Knudsen-layer model

Branch: `feat/knudsen-layer-sonic`

Implemented:
- new runtime-selectable `knudsenLayerSonic` evaporation model;
- Wang et al. (2020) Knudsen-layer jump relations evaluated at `Ma=1`;
- a mass flux and recoil pressure derived from the same sonic jump state;
- chamber-relative net recoil traction for the current pseudo-gas solver;
- evaporative heat flux from `mDot * latentHeatVap`;
- analytical constitutive regression plus one-step CFD coupling smoke test;
- literature-to-code notes in `log/LITERATURE_NOTES.md`.

Scope:
this commit intentionally implements only the strong-evaporation sonic branch.
The full near-vacuum transition/interpolation logic is deferred to Phase 4b.

### Phase-4a first regression correction

CI attempt 1 compiled and passed all pre-existing gates, but the new sonic
analytical comparison exposed a configuration-rounding issue: `foamDictionary`
rewrote a user-configurable gamma to `1.66667`.

The sonic model now fixes `gamma=5/3` in code, matching the monatomic-vapour
assumption of the literature model and eliminating an inappropriate calibration
degree of freedom. No empirical tolerance widening was used.

### Phase-4a verification complete

Final CI run `36514885821`: PASS.

The `knudsenLayerSonic` implementation now passes analytical constitutive
checks and one-step CFD coupling while preserving every Phase 0-3 regression.

Phase 4 remains open: the next sub-phase is the common-atmosphere/transition
solver required to determine the `Ma=0.05` and `Ma=1` temperature thresholds
and implement the source paper's near-vacuum interpolation logic.

### Phase-4a integration

Pull request: #5 — `Phase 4a: sonic Knudsen-layer evaporation model`

Merged into:
`dev/vacuum-solver`

Merge commit:
`6ed0a047f920a583824e484e8427bf3387eec968`

Final verification before merge:
GitHub Actions run `36514885821` — PASS.

The protected `main` branch remains the exact LaserbeamFoam V3.0 baseline.

## 2026-09-29 — Phase 4b transition-state solver started

Branch: `feat/near-vacuum-transition`

Added:
- reusable `knudsenTransitionRelations` scalar constitutive helper;
- exact Knudsen-layer jump-state evaluation for arbitrary `0 < Ma <= 1`;
- analytical reduction of Eq. (17) to the physical shock Mach number;
- logarithmic Eq. (16) residual;
- bounded bisection for `Ma(Te)`;
- bounded bisection for threshold temperature at target Ma;
- dedicated `knudsenTransitionTest` utility;
- round-trip regression at Ma = 0.05, 0.5, and 1.0.

This is transition-state infrastructure only. It does not yet change the
production evaporation model selected by the solver.

### Phase-4 literature equation correction

A pre-Phase-4c source audit identified an Eq. (10) transcription error in the
initial sonic/transition implementation. The correction changes the
`sqrt(T3/Te)` evaluation and the normalized mass-flux expression, and updates
all independent regression constants. This is a physics correction, not a
tolerance adjustment. The prior successful Phase-4a regression remains in the
record as evidence of the original implementation state.

## 2026-09-29 — Phase 4c near-vacuum production model

Branch: `feat/near-vacuum-model`

Added:
- runtime-selectable `nearVacuumWang` model;
- pressure-dependent boiling temperature;
- automatic `Tk0`/`Tk1` determination;
- cell-wise transition `Ma(T)` solution between the active temperature and
  the sonic threshold;
- sonic branch above `Tk1`;
- explicit refusal of unsupported `Ma<0.05` weak-evaporation configurations;
- synthetic constitutive regression covering sonic, transition, inactive, and
  coupled-CFD paths.

The 0.6 Pa production path now has an explicit near-vacuum model architecture,
but final Ti-6Al-4V material data and experiment validation remain separate
future stages.

### Phase-4c verification complete

GitHub Actions run `36519951799`: PASS.

Every pre-existing regression gate and the new `nearVacuumWang` regression
passed. The branch is ready for integration into `dev/vacuum-solver`.

The corrected Wang Eq. (9)-(13) constants, transition-state infrastructure and
production near-vacuum model are now treated as one verified Phase-4 chain.

## 2026-09-29 — Wang 2020 fast-track alloy extension

Branch: `feat/wang2020-fasttrack`

Implemented:
- generalized the transition residual so callers can supply an arbitrary
  saturation pressure `Pe(T)`;
- extended `nearVacuumWang` with optional multi-component alloy input;
- converted configured mass fractions to the molar fractions required by Wang
  Eq. (18);
- implemented Eqs. (18)-(20) for mixture saturation pressure and
  temperature-dependent vapor molar mass;
- added alloy boiling-temperature and `Tk0/Tk1` bisection using the mixture
  saturation curve;
- retained the previous single-component path unchanged when no component list
  is configured;
- added the two-temperature `wangAlloyMixture` analytical regression and a CI
  gate.

Not yet claimed:
- OpenFOAM-v2512 local validation;
- 304L paper benchmark;
- Ti-6Al-4V production material coefficients;
- composition transport / preferential elemental depletion.

Those items require the subsequent local and CFD validation checkpoints.

## 2026-09-30 — 304L near-vacuum validation implementation

Branch: `feat/wang2020-fasttrack`

Production changes:
- added optional `alloyReferencePressure/alloyReferenceTemperature` scaling for
  multi-component saturation curves while preserving relative vapor composition;
- completed the Wang near-vacuum step-(4) low-Mach branch below `Tk0`;
- added optional clamped-linear metal `cp(T)` and `k(T)` from
  solidus/liquidus tabulated values without changing the default legacy path.

Verification infrastructure:
- added `tests/wang304LReference` with 304L Cr/Ni/Fe composition and
  Table-II saturation-pressure anchor;
- added `tests/wang304LCaseSmoke` for a one-step end-to-end CFD gate;
- added an 8 um setup mesh and 4 um paper-resolution validation mesh;
- added atmosphere-connected centerline keyhole-depth extraction.

A first CI attempt of `wang304LReference` exposed a test-fixture precision
problem: `foamDictionary` rewrote high-precision component latent heats with
reduced output precision. All pre-existing gates passed in that run. The 304L
test was corrected to replace only `testTemperature` with `sed`, preserving
the original thermodynamic constants. This correction changes no production
physics.

## 2026-09-30 — 5 us local-smoke diagnostics

After the local OpenFOAM-v2512 304L constitutive and one-step CFD gates passed,
the validation case was advanced to the 8 um / 5 us short-time physics gate.

Changes:
- `pVap` is now written as an output field;
- added optional `writeDiagnostics` in `vacuumProperties`, defaulting to
  `false` so existing cases and regressions are unchanged;
- when enabled, output times report one compact line containing:
  `Tmax`, `Umax`, `pVapMax`, `QvMax`, and integrated deposited laser
  power;
- the 304L validation case enables these diagnostics;
- `Allrun.smoke` runs 16 MPI ranks to 5 us, collects
  `smokeDiagnostics.log`, and reconstructs the final
  `T/U/alpha.metal/pVap/Qv/Deposition` fields.

The 5 us run is explicitly assigned to the local Ubuntu workstation. No GitHub
CI result is required to advance the project.

## 2026-09-30 — 48-core local-test policy

Per the primary-machine workflow, all current and future full-CFD validation
runs are now configured for 48 MPI ranks.

Updated:
- 304L one-step CFD smoke;
- 304L 8 um / 5 us smoke;
- 304L 4 um paper-reference run;
- smoke/reference decomposition dictionaries;
- validation documentation.

Future local rebuild commands should use `./Allwmake -j 48`.
Pure constitutive utilities remain serial because MPI adds only startup
overhead to those non-CFD checks.

## 2026-09-30 — Wang Ma=0 endpoint/restart fix

A 4 um reference run exposed a low-Mach endpoint failure at
`T=2009.503556 K`, essentially the chamber-pressure boiling point.

The step-(4) solver now includes the exact `Ma=0` endpoint. Wang's jump
relations are regular there:
`T3/Te -> 1`, `P3/Pe -> 1`, mass-flux ratio -> 0, and recoil coefficient -> 1.

The 4 um reference case is now restartable from its latest write, and a
dedicated `Resume_background` helper was added.

## 2026-10-01 — Wang matched-physics gap-closure pass

Implemented after the first 4 um reference produced a robust
32-to-136 um growth interval of 93.88 us versus about 75 us in Wang's current
model.

### Optical closure
- preserved the original LaserbeamFoam Drude/resistivity Fresnel path as
  `opticalModel drudeResistivity`;
- added `opticalModel fixedComplexIndex`;
- the fixed-index path evaluates standard unpolarised complex Fresnel
  reflectivity and specular reflection;
- interface-normal sign is removed from the incidence angle instead of using
  the historical 50% absorption fallback;
- the Wang 304L case now uses Johnson-Christy Fe values interpolated to
  1070 nm: n=2.961346153846154, k=4.013269230769231;
- the corresponding normal-incidence single-hit absorptivity is about 0.3725.

### Surface radiation
- ported the separately developed `vacuumRadiationModel` into the active
  fast-track branch;
- kept radiation distinct from evaporation heat loss;
- coupled it semi-implicitly in the temperature equation;
- enabled epsilon=0.4 for the Wang 304L validation case.

### Diagnostics
Added output-time quantities for direct physical comparison:
- `interfacePVapMax`;
- integrated recoil-force x/y/z components;
- evaporation heat-loss power;
- radiation heat-loss power;
- VOF interface area;
- existing absorbed/deposited laser power remains reported.

### Test isolation
- added a serial analytical radiation regression;
- added a dedicated 48-rank 8 um / 10 us matched-physics smoke test;
- froze explicit smoke control/mesh dictionaries so the smoke test cannot
  accidentally inherit a locally overwritten 4 um / 140 us reference state;
- the matched smoke copies only `initial`, `constant`, and `system`, so it
  does not copy large local processor/output directories.

Status: **implementation complete, pending local build and smoke validation.**

## 2026-10-02 — Begin 0.6 Pa / powder / moving-laser stage

Created branch `feat/0p6Pa-powder-movingLaser` from the frozen Wang validation
line.

Added:
- 3-D 304L 0.6 Pa moving-powder smoke tutorial;
- 13-sphere deterministic single-layer powder fixture;
- 2 m/s tabulated moving-laser smoke path;
- 20 us / 8 um / 48-rank integration configuration;
- isolated automated smoke gate and status helper.

No evaporation-model coefficients were changed.

Status: **implementation ready for local integration test; not yet PASS.**

## 2026-10-02 — 0.6 Pa moving-powder integration gate passed

The first target-stage integration gate is complete:
- 0.6 Pa constitutive regression PASS;
- explicit 3-D powder geometry PASS;
- moving laser PASS;
- 48-rank CFD PASS through 20 us;
- recoil/evaporation/radiation diagnostics active.

Next stage:
replace the hand-authored 13-sphere fixture with a deterministic,
configuration-driven powder-bed generator that records seed, particle-size
statistics, packing fraction and generated setFields geometry. Then extend the
domain/path into a reproducible moving single-track case.

No validated Wang evaporation coefficients are changed.

## 2026-10-02 — Add reproducible powder-bed infrastructure

Added `tools/powderBed/generatePowderBed.py` with:
- seeded deterministic generation;
- uniform or truncated-lognormal diameter sampling;
- vertical contact settling;
- overlap validation;
- layer-thickness rejection;
- exact particle CSV;
- powder manifest with PSD/packing statistics;
- generated OpenFOAM setFields geometry.

Added a frozen generator regression and a second 48-rank 0.6 Pa
moving-laser smoke using a generated 56-particle bed.

Status: implementation complete; local T11a/T11b validation pending.

## 2026-10-02 — Wang validation line closed for paper documentation

Project decision:
the Wang-type near-vacuum evaporation-model development and the 304L
0.0002-atm stationary-laser validation are complete and frozen as
`Wang 304L matched validation v1`.

Scope of this closure:
- constitutive Wang/Knudsen transition implementation;
- Cr/Ni/Fe alloy extension and 304L anchor;
- Ma=0 boiling-endpoint handling;
- VOF recoil/evaporation coupling;
- Fe fixed-complex-index Fresnel alignment;
- grey-body radiation;
- 4 um / 48-rank / 140 us benchmark;
- connected-3D keyhole-depth validation;
- reconstructed keyhole-surface recoil/load diagnostics.

Primary final metrics:
- 32-to-136 um connected-3D growth interval: 76.23 us;
- Wang current-model reference: about 75 us;
- x-ray reference: about 70 us;
- full surface pressure-load integral at the equivalent comparison stage:
  about 3.52 mN versus Wang about 4 mN;
- time-history peak full pressure-load integral: 4.70 mN.

The single hottest reconstructed recoil-pressure face remains an OPEN
mesh/interpolation sensitivity metric and is not a reason to retune the model.

This closure validates the project-relevant 304L near-vacuum case. It is not a
claim that every Ti-6Al-4V/common-atmosphere/scanning case in Wang et al. has
been independently reproduced.

A paper-oriented summary/figure package is maintained separately from the
production physics code.

## 2026-10-03 — Project review, moving-metric freeze and roadmap reset

The project was reviewed while the strict 8 um / 4 um moving-powder resolution
pair was running.

Completed since the previous roadmap snapshot:
- Wang 304L matched validation v1 frozen;
- 0.6 Pa constitutive gate passed;
- explicit moving-powder integration passed;
- deterministic powder generator passed;
- 300-us / 600-um / 48-rank engineering long-track completed;
- moving-keyhole trailing-window sensitivity completed;
- 120-um trailing window frozen as the formal moving-keyhole metric.

The original DEVELOPMENT_PLAN had become stale because it still described the
Wang near-vacuum and radiation phases as incomplete. It was replaced with a
milestone-based roadmap aligned with the actual project state.

Added:
- PROJECT_STATUS.md for a concise current-state snapshot;
- PAPER_AND_REPORTING_PLAN.md to treat manuscript/figure/reproducibility work as
  a formal parallel workstream;
- updated log/README.md navigation.

Current running milestone:
- strict matched 8 um versus 4 um moving-powder resolution pair.

Immediate decision after that pair:
- define production mesh policy before further experimental-parameter runs.

Physics extensions such as explicit evaporation mass removal, preferential
composition evolution and rarefied plume coupling remain conditional. They are
not introduced simply because the base solver can support more complexity.


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


## 2026-10-08 210010: stop micro screens; structural regional acceleration

Halo candidate failed performance (514.530s vs371.384s,11skips but48vs40steps).
User requests faster development and no more small screens. Freeze these branches;
defaults unchanged. Implemented conservative axis-aligned overlap transfer reference
with147passing Python tests; true regional OpenFOAM solver remains pending.
Next milestone is native global-conduction/local-CFD coupling and one combined
acceptance driver. No new Ubuntu command in this update. See M247_REGIONAL_DEVELOPMENT.md.


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
