# Legacy versus corrected optical policy

The corrected cache off/on transient pair passes, with seven reported final-field differences zero and 1.08x job speedup. Next measure how the two optical corrections affect the old physical solution:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunRayTraversal --physics-impact
```

The wrapper builds/checks the library, clean solver and real-mesh MPI packet/search utility, then copies the original 48-rank 180 us checkpoint. Both cases use traversal cache, 1536 rays/call, tight bounded enthalpy and zero phase smoothing. rayImpactLegacy turns both corrections off; rayImpactCorrected turns both on. Only preserveRayHandoffSample and consistentRayTermination differ. Frozen mode is off and output precision is 17 digits in both cases. No repartitioning or source modification occurs.

Both solve the full coupled 180–182 us interval with a 30-minute budget per solver job; compilation, copying, search tests and shutdown grace add time. This is an impact measurement, not an equivalent optimization test. Ray work is expected to change. The collector still validates complete timing/sampling, loaded binary provenance, correction switches/work, convergence and no caps. It reports strict legacy field and physical-diagnostic equality separately from the execution gate. A completed converged test may report legacy-equivalence false; this is evidence to assess, not physical approval. No equality tolerance is loosened and production_approved remains false. Timing ratios compare different policies.

The comparison contains seven final-field norms, physical diagnostic differences at both output times, per-step candidate correction accounting, and a localization report covering metalBoth, gasBoth and interfaceOrChanged bins. Threshold counts and worst-cell records help interpret the differences; they are diagnostic, not acceptance limits. Local indices are not spatial coordinates and RMS is cell-unweighted. This short interval cannot establish long-time stability, keyhole geometry or mesh convergence.

Send the single `M247_ray-physics-impact-YYYYMMDD-HHMMSS_review.tar.gz`, including on failure. It includes distinct complete legacy/corrected logs and settings, build/preflight/packet/search evidence, rayTraversalReview.json, diagnosticComparison.csv, fieldLocalization.json, fieldRegions.csv and worstCells.csv. Raw final fields are not archived; norms/localization are computed on Ubuntu.
