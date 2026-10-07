# Seed shortcut has no measured gain; recover missing review logs

Reviewed M247_ray-seed-search-20261007-204122_review.tar.gz. All11manifest
file hashes/sizes verify,wrapper exit0,missing_files empty. However variants=[]:
the packaging whitelist omitted raySeedReference/raySeedCached,so neither
solver log,probe/run metadata nor case dictionaries was included. Empty
missing_files therefore does not establish complete review evidence. This is
a packaging bug introduced with the new variant names,not a failed CFD job.

Available build/preflight logs confirm successful compilation and loaded-library
feature checks. Independent real-mesh log:322560checks,zero mismatches,
161280Cartesian checks,39fast accepts,244eligible cells. Only0.0323% of756000
cells qualify under exact axis alignment.39is parity-test usage,not a runtime
CFD hit count. Do not loosen predicates just to force a performance result.

Archived Ubuntu report says regression/work gates true,seven final fields have
zero max/RMS differences over756000cells,166steps,14.319277correctors/step,
max18,no caps. Aggregated rank work in both profiles agrees. Full solver logs
are missing,so interval coverage,thermal convergence and physical diagnostics
cannot yet be independently rechecked from this archive. Raw fields were never
intended to be archived; field norms remain Ubuntu comparison results.

Reported job reference327.335427s,candidate332.346499s,ratio speedup0.984922;
candidate takes1.5309% longer in this pair. Loop325.602994/330.375678s,
speedup0.985554. Performance gate false. One pair does not prove a systematic
slowdown,but it supplies no evidence for promotion. Keep cartesianRaySeedSearch
disabled and retain previously validated cachedRayTraversal. No repeat CFD for
this shortcut. Candidate tracing max/mean13.3206 remains strongly imbalanced.

Fixed packaging to import VARIANTS from prepare_probe,avoiding a second variant
whitelist. Added RepackageReview,which only collects existing files into a fresh
timestamped collection archive; it neither rebuilds,runs CFD nor recomputes
fields. Recovery wrapper status is null,not a fabricated original success.
60Python tests pass,including both seed logs,metadata and dictionaries present
while large fields stay excluded; Bash syntax checked.

Ubuntu: pull feature branch,then
`./tests/m247Performance/RepackageReview tests/m247Performance/runs/ray-seed-search-20261007-204122`.
Send its printed single collection archive. The existing archive is preserved.
After restoring evidence,move development effort to tracing load distribution/
particle backend and fixed local fine-grid/domain coupling,where costs can be
reduced materially. No further strict-axis seed micro-optimization planned.
