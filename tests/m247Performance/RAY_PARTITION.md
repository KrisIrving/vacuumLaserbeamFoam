# Ray-weighted partition experiment

The recovered 180–182 us seed experiment had 21 of 48 ranks with no ray searches; ranks 44 and 46 carried 58.31% of searches. The seed shortcut did not improve performance. This experiment tests whether redistributing cells can reduce tracing imbalance and the associated exchange waits.

Run from the repository root in the Ubuntu OpenFOAM environment:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunRayPartition
```

Optional arguments are SOURCE and a fresh WORK directory. The source must contain the original serial `constant/polyMesh`, the complete 48-rank 180 us checkpoint, and nonuniform nonnegative `rayQ`. The script requires `reconstructPar`, `decomposePar` and the existing instrumented solver/library. It changes no C++ code and does not rebuild. Missing prerequisites stop the experiment and still produce a review archive.

Both variants use the validated traversal cache, 1536 rays per laser call, tight bounded enthalpy controls, zero phase blend width and no ray paths. `rayPartitionReference` retains the source decomposition. `rayPartitionWeighted` uses Scotch with `weightField rayWorkWeight`, where each cell has weight `1 + rayQ/mean(rayQ)` from the checkpoint. This gives equal total weight to base cell work and the ray proxy. `rayQ` measures power-weighted paths, not search cost, so improvement is uncertain. OpenFOAM's decomposition code reads a configured weight field's internal values as cell weights ([official implementation](https://api.openfoam.com/2406/domainDecompositionDistribute_8C_source.html)).

Native utilities reconstruct all available checkpoint fields, repartition only the copied candidate case, then reconstruct it again. Before either solver job, the original global mesh digest must match and seven initial internal fields must be exactly equal: T, epsilon1, alpha.metal, U, p_rgh, Deposition and rayQ. Output precision is 17 digits. The source case is not modified.

Each solver job covers 180–182 us on 48 ranks, with a 30-minute wall budget. Each native preprocessing/postprocessing utility has a five-minute timeout; copying and solver shutdown grace add time. After each job, the seven final fields are reconstructed onto the original global mesh. Processor-local indices are deliberately not compared across different decompositions. Each profile's rank counters must reconcile internally; cross-variant ownership, stepping and exchange counters may differ. Sampling, loaded binaries, convergence, physical diagnostics and strict final-field gates remain checked. Changing decomposition can change numerical results; failure is reported without relaxing tolerances.

Performance passes only if regression passes and both loop and job speedups are at least 1.05. This short experiment does not approve production or establish full-track cost.

The wrapper automatically produces one `M247_ray-partition-YYYYMMDD-HHMMSS_review.tar.gz`, including both distinctly named solver logs, configuration, native utility log, weights summary, initial checks and `rayPartitionReview.json`. Send that single archive, including when the run fails. Full field data are not archived; field norms are computed on Ubuntu before packaging.
