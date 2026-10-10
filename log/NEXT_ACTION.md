## 2026-10-10 202035: reduced-ray budget PASS and measured1.649x; longer validation

Review archive complete,exit0,missingfiles0; all manifest file SHA256 verified.
Both full756k48rank180..190us jobs completed834steps. Every-step optics,
actual1536/384ray counts, source unchanged and measurement/thermal gates pass.
Baseline1735.51574s(28.9253min),candidate1052.48911s(17.5415min),1.64896x:
39.356%less solver wall. Laser857.49695->220.95305s,3.881x/74.233%less;
thermal592.76080->559.30755s. Non-laser differences include run variability and
changed physics. Candidate thermal53.221%,laser21.025%,pressure14.333%:
optics sampling achieved a clear gain but remaining bottleneck shifts to heat.
Do not imply4x full-job speed or multiply older unvalidated speedups.

User budget(depth5%,liquid volume5%,Tmax10%) passes at BOTH samples.
185us depth+0.44897um(0.14952%),liquid volume0.004559%,Tmax2.89826%.
190us depth-2.33494um(0.77889%),liquid volume0.010462%,Tmax5.33138%.
Baseline/candidate depth299.77619/297.44125um at190us. Both connected,
iso-bottom support21/15. Values are8um-mesh iso diagnostics,not subgrid accuracy.
Thermal mean14.54676/14.56115,max18,no limit hits. No production approval yet.

Accuracy scope is explicitly the user-chosen three scalar metrics, not full
local temperature/phase equivalence. Liquid interface T RMS29.2811->51.2145K
from185->190us,max1097.156->2025.127K. Liquid epsilon maxdifference0.68855/
0.73160. Interface T RMS30.5246->55.3064K. At190us pVapMax29.6335%,QvMax
32.0161%,evaporationPower20.5173%,recoilX30.1659% differences; these remain
visible in reports and are not secretly subjected to unrequested new limits.
Candidate meets allowed macro metrics but has large local field differences.
No interpretation as experimental or long-track accuracy. Preserve384candidate
and user budget; do not start another smaller-angle screening sweep.

Next implemented RunRaySamplingLongPair: from SAME180us checkpoint,180..200us
20us pair, outputs190/200us. nRadial16/angular96vs24, unchanged physics flags.
Metadata duration/endTime and reconstruction/keyhole/sample/error times updated
consistently; short-probe schedule remains185/190us. Every-step refresh helper
already derives half/end times, now190/200us. No new C++ or rebuild needed.
Same source/partition/thermal/raycount checks and automatic localization. Both
stages end at existing laser path/power endpoint200us: do NOT silently continue
clamped350W heating past200us. Cooling/solidification needs an explicit later
laser-off schedule and is not claimed completed by this20us heating test.

Local44checks(43pass,1Windows symlinkskip),Python compilation/Bash syntax pass.
New regression test verifies error report uses longer sample times, not old
185/190us constants. Based on measured pair,expectroughly90min+preparation/
localization;no forced timeout. Long-run errors and benefit still unmeasured.
4um24h/full1.5..2mm track remain unverified and are later stages after sustained
accuracy/cost acceptance; this is a real acceleration milestone,not final goal.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunRaySamplingLongPair
Return one M247_ray-sampling-long-pair-<timestamp>_review.tar.gz,including failure.

## 2026-10-10: user-authorized approximate optical sampling with explicit budget

User requested fast approximate ray tracing and accepted accuracy sacrifice.
User-selected budget relative to current baseline: keyhole depth and liquid
metal volume differences<=5%,Tmax<=10%. Honor this scope; no bit equality
requirement for approximate optics. No production approval on10us alone.

RunRaySamplingPair added: no native code/rebuild, existing official nAngular
setting96->24, nRadial16 fixed,1536->384ray samples. Radial weights unchanged;
angular area deltaTheta increases4x,nominal seed power sum unchanged to rounding.
Relative power cutoff unchanged; absolute per-ray cutoff follows existing max
ray power normalization. All propagation distances,absorption/reflection/
handoff/termination unchanged,every-step source update required. Packed mode
and thermal cache off,visual ray paths off in both. All other constant physics
settings exact; samefull756kmesh/initial fields and48Scotch partitions verified.
Fresh copies only; /media and home aliases resolved. Original source untouched.

Two180..190us jobs with185/190us outputs. Budget checks ALLthree metrics at
BOTHtimes, plus thermal and measurement-quality gates. Report finite values,
missing/zero-baseline metrics fail approval. Report full diagnostics including
pVap/recoil/power without hiding deviations. Actual emitted rays verified from
profile as1536 or384 per update. Automatic liquid/interface/gas localization
included in same archive to avoid another collection command. No cold cut.
No acceptance silently extrapolated to full track/4um/experiment accuracy.

Local43tests(42pass,1Windows symlink skip),Python compilation and Bash syntax
pass. New3tests cover optical-settings isolation,actual ray count mismatch,
user limits at both samples and missing/nonfinite/over-budget failures.
Native solver already compiled in99158cf test; no new C++ compilation needed.
No approximate sampling performance or accuracy measured yet. Conditional
quarter of~51.7% optical work suggests~1.63x total if other cost unchanged;
not4x full-job acceleration. Pair expectedroughly45min pluspreparation/localization.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunRaySamplingPair
Return one M247_ray-sampling-pair-<timestamp>_review.tar.gz,including failure.
If budget and useful speed pass, next advance longer melting/solidification
validation rather than another small angular-count screen. Major architectural
work is deferred until this authorized approximation has measured evidence.

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
