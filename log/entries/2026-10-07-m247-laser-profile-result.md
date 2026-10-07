# Laser internal profile result: exchange/wait path dominates mean time

Archive M247_laser-profile-20261007-190239_review.tar.gz hashes and sizes
verified; missing_files empty, wrapper exit0. Ubuntu build and loaded-library
preflight pass at checkpoint7a0ccb3b63fe831642c2cf07b0ccfefaad1d7326.
Solver SHA256 ce84cda065004fc2f1bcd9d2e821f616f277cc0be13928f52d9ca826d66b60bf;
laser library d6e38e6c243958cb1b37c2fe03f33ecdf698c53ff311b962195cc7cbb9967014.

Instrumentation regression passes. All756000 final internal cells have exactly
zero T/epsilon1/alpha.metal/U/p_rgh differences in the saved ASCII output.
Both common-time physical diagnostic samples pass equality gates. Both cases
have16 steps,15.3125 thermal correctors/step and no cap hits. Job wall36.038 s
off /37.039 s on; observed profiling overhead2.78% in this one short pair,
not a repeated statistical overhead estimate. Physics production remains
unapproved and phase smoothing remains off.

| Inner laser stage | Mean seconds | Mean fraction | Sum of interval rank maxima, seconds |
|---|---:|---:|---:|
| Initial generation | 0.000167 | 0.000862% | 0.000239 |
| Initial exchange | 0.006260 | 0.0323% | 0.008117 |
| Initial locate | 0.091101 | 0.470% | 0.180012 |
| Ownership | 0.185057 | 0.955% | 0.624206 |
| Local tracing | 0.784279 | 4.049% | 10.054098 |
| Round exchange | 18.297163 | 94.468% | 19.288548 |
| Final integration | 0.002691 | 0.0139% | 0.002744 |
| Other | 0.002006 | 0.0104% | 0.003361 |

Mean inner total19.368724 s; solver laser section19.399125 s /35.142066 s
profiled loop total. Outer reset/config work and report reductions explain the
scope difference; independent stage maxima are NOT additive.

16 calls,24576 initial rays =>1536 rays/call.327 round exchanges =>20.4375/call.
Local aggregate workload:151489 trace segments,18791614 advances,
18943103 trace searches,1233842 interface events,3513 bulk events.
Trace search sample148019 calls /0.302752 rank-sum seconds, about2.045 us
per sampled search; stride128 sample is not an unbiased full-cost estimate.

Important interpretation: exchange includes outgoing list copy, blocking
combineGather with combineRayLists, and broadcast. Early ranks may wait here
while other ranks trace. Tracing maximum/mean ratio is12.82, indicating strong
rank imbalance in aggregate tracing time. This does not identify exact idle
fractions, per-round critical ranks or network bandwidth saturation. Do not
claim94.5% is removable communication work or predict speedup from it.

Next development target: split exchange copy/gather/broadcast, record local
trace workload/time across ranks and gather combine cost, then select a
result-preserving exchange/ownership optimization. Existing code globally
replicates remaining rays, performs ownership searches on every rank, and
uses blocking gather/broadcast each round. Initial generation is negligible;
do not change ray counts or optical physics to pursue this bottleneck.

No additional Ubuntu command or file collection is required for this review.
This records verified results and the next target, not an implemented speedup.
