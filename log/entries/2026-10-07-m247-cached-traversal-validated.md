# Cached traversal passes short physical/deposition regression and speed gate

Reviewed M247_ray-traversal-20261007-195231_collection-20261007-200224_review.tar.gz.
All 29 manifest file hashes and sizes match, missing_files empty, wrapper exit 0.
This is offline collection of the completed 195231 runs, not a new CFD pair.
Build environment remains 0ae0bc4cf5b723c02ca38624bf542d5ab7b09256; collection
uses the subsequent recovery workflow. No solver change occurred in recovery.

rayTraversalReview.json reports regression_gate, work_counter_gate and
performance_gate true, with production_approved false. Seven mandatory final
internal fields over 756000 cells have zero maximum and RMS differences:
T, epsilon1, alpha.metal, U, p_rgh, Deposition and rayQ. Saved field files remain
on Ubuntu and are excluded from this archive; these norms are the Ubuntu
comparison report, not a local recomputation of the field data.

Optional rayNumber is explicitly not_written, consistent with non-debug
NO_WRITE. This is seven-field PASS, not eight-field PASS. Debug stays off.
Real-mesh search test reports 50688 comparisons and zero mismatches.

Independent archive-log parsing validates schema-2 additive/nested statistics
and complete 96-rank-row coverage per case. Reported global counts match logs,
reference/candidate counts agree exactly, and physical diagnostics at both
common output times are identical. Both cases finish 16 steps with average
15.3125 thermal correctors/step, maximum 18, no caps, passing residual gates.

| Metric | Reference | Cached |
|---|---:|---:|
| Job wall seconds | 36.039873 | 32.034350 |
| Sum of interval maximum loop seconds | 34.528601 | 30.328550 |
| Mean inner laser seconds | 19.228025 | 15.135064 |
| Sum of interval maximum trace seconds | 10.185954 | 7.972226 |
| Mean exchange including waits, seconds | 18.160531 | 14.233252 |

Observed job speedup 1.125038 and loop speedup 1.138485 exceed the 5% gates.
Job duration falls 11.114%; inner laser duration falls 21.286%. The JSON field
profiling_job_overhead_ratio is reused from the instrumentation collector;
here its value 0.888859 is candidate/reference job duration, not overhead of
profiling, since both cases enable profiling.

The cache does not solve load imbalance: tracing maximum/mean changes from
13.046 to 12.969. Blocking exchange remains about 94% of inner mean laser time.
Do not interpret that fraction as pure network transport or removable cost.
Faster tracing and shorter collective waits are consistent with the measured
job improvement, while optics and sampled deposition stay equal in this test.

## Decision and next development

Retain cachedRayTraversal as an opt-in candidate that passed this 180–180.2-us,
8-um, 48-rank checkpoint test. Keep the global default false. This result does
not approve phase closure, full-track physics or 4-um production, nor establish
statistical speedup across repeated or longer runs.

Next prepare a matched 180–182-us (2-us) reference/cached validation, preserving
tight bounded thermal controls, phase width zero and ray count. Its acceptance
must cover seven final fields, common-time physics/energy diagnostics, work
counters, convergence and cost. The planned per-job budget is 30 minutes;
the current short timing suggests several minutes, not a guaranteed runtime.
No new command or code is introduced in this review, so do not rerun the short
pair or the already completed offline collection.

After the broader equivalence check, target tracing load distribution and a
separately benchmarked upstream V3.1 particle backend. Cache gains alone are
insufficient to make the 1.5–2-mm full track affordable. Repartitioning/backend
changes need comparison of ownership, absorbed/deposited power and local fields;
4-um ROI and moving thermal/fluid-domain design remain subsequent stages.
