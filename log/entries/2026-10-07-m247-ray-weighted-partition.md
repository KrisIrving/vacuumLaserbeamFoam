# Next experiment: ray-weighted Scotch partition

Recovered seed-test evidence identifies severe tracing imbalance (21/48 ranks without searches; two ranks carry 58.31%). The seed shortcut remains off because its measured speedup was below one. Proceed with a copied-case repartition experiment before changing the ray transport backend.

Added RunRayPartition and ray_partition.py: original partition versus checkpoint-rayQ-weighted Scotch, same 48 ranks and 180–182 us interval. Both keep validated traversal caching and tight unsmoothed enthalpy controls. Native reconstruction/decomposition preserves the original global mesh and checks initial internal fields before CFD. Final fields are compared after serial reconstruction, rather than by processor-local address. The collector checks binary provenance, sampling, convergence, physical diagnostics, seven final fields and internally reconciled rank profiles. No tolerance relaxation and no production approval.

The weight is a power-path proxy with equal aggregate base/ray weighting, not measured per-cell tracing cost. Its benefit is unverified. Thirty-minute budgets apply to each solver job, with five-minute utility timeouts. Automatically packaged evidence distinguishes both variants and includes native failures. No solver modification or rebuild is required.

Local Python regression and Bash syntax checks cover the workflow. OpenFOAM native utility compatibility and actual performance require Ubuntu execution. See tests/m247Performance/RAY_PARTITION.md for the single command and evidence contract. The longer-term goal remains a moving local CFD region coupled to a coarser global thermal field; this experiment measures an immediate parallel bottleneck.
