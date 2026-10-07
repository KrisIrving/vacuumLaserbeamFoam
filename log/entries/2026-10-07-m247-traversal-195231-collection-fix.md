# Cached traversal 195231: promising speed, offline field collection needed

Archive M247_ray-traversal-20261007-195231_review.tar.gz: manifest file hashes
and sizes verified; no missing listed files; wrapper exit 1. Both CFD jobs have
returncode 0, End and MPI finalisation, no wall/forced stop. Build environment
records 0ae0bc4cf5b723c02ca38624bf542d5ab7b09256. Library/solver/real-mesh
test compile and preflight pass. Solver hash
54e35ac4d9876337ae30bb5ee951b8ccd4e74cb62250aded35234cfeab141dbb;
library hash
2b3819255930b15aac5cf451432064ecc823488cd2123f819b7d0f382dbab6db.

Real-mesh search parity reports 50688 checks, zero mismatches. Reparsed logs
validate two global and 96 rank rows per case. Global interval and accumulated
per-rank ray-work counts agree exactly. Common-time physical diagnostics pass
rtol1e-8/atol1e-12. Both cases take 16 steps, 15.3125 thermal correctors/step,
maximum 18, no limit hits and passing per-step tight residuals.

| Metric | Reference | Cached |
|---|---:|---:|
| Job seconds | 36.039873 | 32.034350 |
| Sum of interval maximum loop seconds | 34.528601 | 30.328550 |
| Mean inner laser seconds | 19.228025 | 15.135064 |
| Mean trace seconds | 0.780795 | 0.614718 |
| Sum of interval maximum trace seconds | 10.185954 | 7.972226 |
| Mean exchange/wait seconds | 18.160531 | 14.233252 |

Job speedup 1.125038, loop speedup 1.138485; job wall time falls about 11.11%.
Mean inner laser time falls about 21.29%. Trace and collective wait time fall
together, consistent with accelerating the heavy ranks. One short pair does
not establish statistical, long-track or 4-um speedup. No candidate promotion
before saved physical/deposition field regression.

No comparison report is included. The collector incorrectly required
rayNumber, while the inherited constructor sets it NO_WRITE except in debug.
The archive does not retain the collector stderr, so that exact exception
cannot be read back; source inspection establishes the incompatible field
requirement. All preceding log-level checks pass. Fix collection, retain fields
on Ubuntu and avoid rerunning completed CFD just for reporting.

Seven fields remain mandatory: T, epsilon1, alpha.metal, U, p_rgh, Deposition
and rayQ. rayNumber is an optional visual ID: compare only if saved for both
cases/all ranks; report not_written explicitly when absent everywhere; reject
partial availability. This is an explicit correction of the previous eight-field
requirement, not an asserted eight-field PASS. Debug must stay off because it
routes cached searches through the legacy implementation. Cached mode remains
default off and production_approved false.

InspectRayTraversal only reads saved fields and creates reports/a new named
archive. It does not compile or run CFD. Both collection wrappers now package
collection.log so future exceptions are directly inspectable.

53 local harness tests pass, including absent/partial rayNumber behavior.
Bash syntax checks pass. Ubuntu offline field results remain pending.

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/InspectRayTraversal tests/m247Performance/runs/ray-traversal-20261007-195231
```

Send the printed collection review archive. The next decision is whether to
retain the equivalent candidate and extend its validation before larger
partitioning/particle-backend work.
