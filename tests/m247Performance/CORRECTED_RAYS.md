# Corrected transient cache regression

The 225102 frozen optical pair passes strict power and spatial gates with handoff-sample preservation and consistent termination. Next verify complete coupled flow/thermal behaviour and cache performance on the original decomposition:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunRayTraversal --corrected
```

The wrapper automatically rebuilds the laser library, clean solver and search/packet utility. It copies the original 48-rank 180 us checkpoint into rayTraversalReference and rayTraversalCached. Both enable preserveRayHandoffSample and consistentRayTermination, disable frozen mode, keep the seed shortcut off, use the same 1536-ray sampling and tight unsmoothed enthalpy settings. Only cachedRayTraversal differs. Both solve flow, thermal and interface evolution from 180 to 182 us; each solver job has a 30-minute wall budget. Build/copy/test and shutdown grace add time. The source and its partition are unchanged.

The collector requires the real MPI packet and cell-search tests, actual correction switches, complete per-call correction records and bounded discarded power. It compares correction records, global/per-rank ray work, physical diagnostics and seven mandatory final fields, with thermal convergence and zero caps. The existing strict tolerances remain unchanged; speedup passes only after regression and at least 1.05x loop and job improvement. This harness assumes one laser call per timestep on this single-beam case and rejects different schedules rather than silently accepting partial coverage.

Send the single automatically printed `M247_ray-corrected-validation-YYYYMMDD-HHMMSS_review.tar.gz`, including failures. It includes both distinctly named complete solver logs, build/preflight/search evidence, settings, timing and physics/field reports. The report is comparison/rayTraversalReview.json; corrected_ray_work stores per-step crossing, resumption and cutoff accounting. Raw field files are not archived.

This compares cache off/on within corrected physics, not correction versus the legacy solution. Passing does not establish physical adequacy of the model, validate weighted partitioning or authorize long-track/finer-mesh production. Globally the two correction switches remain default-off; they are enabled only in these copied cases. Ordinary prepared probes now explicitly set both corrections and frozen mode off, so a modified source dictionary cannot silently enable this diagnostic configuration.
