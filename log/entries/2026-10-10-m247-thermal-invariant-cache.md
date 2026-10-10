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

