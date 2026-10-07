# Seed recovery archive independently verified; no further Ubuntu action

Reviewed M247_ray-seed-search-20261007-204122_collection-20261007-210403_review.tar.gz.
All27manifest hashes/sizes match,both variant logs/probe/run metadata and case
dictionaries present,missing_files empty. wrapper_exit_code is null by design:
this is packaging recovery,not a new solver run or fabricated wrapper success.
Each original run.json independently reports completed successful CFD,without
budget/forced stop,and full logs end normally.

Independent parsing verifies180–182-us coverage,166steps in both cases,
14.319277thermal correctors/step,max18,no caps; per-step residuals satisfy tight
controls. Solver/library hashes and source snapshot provenance match. Runtime
cache enabled in both cases,seed shortcut off/on as expected,phase width zero.
Common physical diagnostic samples agree; interval global and all48rank work
totals reconcile and match exactly. Two output groups per case give96rank rows.
Seven final physical/deposition fields have zero max/RMS differences across
756000cells according to the original Ubuntu field-norm report. Raw fields
remain on Ubuntu; this audit does not recompute those norms locally.

Job327.335427→332.346499s,0.984922x; loop325.602994→330.375678s,0.985554x.
Regression passes,performance fails; one pair does not establish statistical
slowdown. Keep cartesianRaySeedSearch off and retain previously validated
cachedRayTraversal. Do not repeat this experiment or its completed recovery.

Search parity322560checks,zero mismatches,244eligible cells and39fast accepts
in the parity test. Trace max/mean reference13.2311,candidate13.3206. Search
counts:rank44=60334012,rank46=53936729,rank34=35600690. Top two ranks carry
58.3141% of searches;21/48ranks perform zero searches. These are summed local
search-call counts,not unique rays. Blocking exchange timers include waiting;
do not interpret roughly95% inner mean exchange fraction as pure network cost.

Next development should address tracing work distribution and separately
benchmark the upstream particle backend,while developing fixed local fine-grid
and regional heat/fluid coupling for full-track cost reduction. Compare physics,
ownership and deposited power when decomposition/backend changes; per-rank work
is not expected to remain identical after repartitioning. Do not recycle the
cache collector's exact per-rank-work gate for that different experiment.
No new code/numerical change or additional Ubuntu command is introduced here.
