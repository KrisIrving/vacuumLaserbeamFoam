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

