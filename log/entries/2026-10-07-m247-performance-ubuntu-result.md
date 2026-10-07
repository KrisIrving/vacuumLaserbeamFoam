# Ubuntu mature-state performance pair: measured result

Evidence: user-pasted RunPair terminal output on 2026-10-07. Full solver logs and comparison.json have not yet been inspected. This supersedes the pending-execution status in the phase-1 entry.

Both probes completed 180–182 us on 48 ranks with returncode 0 and no wall-budget stop. Identical source snapshot SHA256: b16bd0abd549c1b2e978f13921c60f9a0be065b9143d038e40f303efbeb19943. Identical solver/library hashes were reported for both variants.

| Metric | baseline | noRayPaths |
|---|---:|---:|
| Actual job wall seconds | 1493.520464 | 1333.288906 |
| Loop proxy seconds/us | 745.86 | 665.98 |
| Mean-rank thermal fraction | 72.27% | 79.62% |
| Mean-rank laser fraction | 24.34% | 16.81% |
| Thermal correctors/step | 151.00 | 151.00 |
| Thermal limit hits | 166 | 166 |

Measured job speedup is 1.120x, or 10.728% less wall time (160.232 s saved). A single sequential pair does not establish repeatability or production speedup. Laser fraction includes tracing/search/MPI, not just output-file I/O; rayIO itself was only 0.01% in the baseline. Section fractions are MPI means; do not multiply them by max-rank wall totals and label the result exact section times.

Physical diagnostic comparison PASS; thermal limit gate FAIL. This is not a successful full regression gate. Both modes have the same pre-existing thermal convergence problem. The code's do/while permits 151 actual iterations for maxTempCorrector=150; limit hits indicate the final max epsilon increment exceeded epsilonTolerance (case default 1e-4). This does not alone prove divergence or quantify solution error. Equal diagnostics can still share the same under-convergence.

Next required evidence: comparison.json and both full log.vacuumLaserbeamFoam files. Inspect per-corrector epsilon residual histories and temperature linear-solver convergence. Determine declining vs stalled/oscillatory behaviour and whether gas/interface cells control the global max; the current max residual is not metal-masked. The gas/interface hypothesis is unverified.

Priority is the thermal loop, not pressure (about 2%). Do not lower iteration caps or loosen residual tolerance as an accepted speed fix before residual/field validation. Keep noRayPaths as a measured promising candidate, not a production-approved setting. Next numerical development must target the measured thermal convergence behaviour; long-track local-flow/global-thermal architecture remains future work.

