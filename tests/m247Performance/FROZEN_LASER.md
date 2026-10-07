# Fixed-state optical partition diagnostic

The weighted partition pair changed both coupled physics and execution cost. This diagnostic isolates the laser update by using identical precomputed internal optical inputs, the same mesh and 1536 rays, with no time advancement or flow/thermal solve.

From the Ubuntu repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunFrozenLaser
```

The wrapper rebuilds the laser library and cleans/rebuilds the solver, then checks the actual executable, loaded library and new diagnostic marker. Optional arguments are SOURCE, a fresh WORK directory and build JOBS (default 48). Requirements are the original serial fixed mesh and complete 48-rank 180 us checkpoint including rayQ, as for RunRayPartition. Source files are not modified; all native reconstruction/decomposition and writes affect copied cases.

There are three short solver launches, all at 180 us:

1. Capture the original partition's filtered alpha, interface normal and electrical resistivity into named frozen input fields. No laser call or time advancement occurs.
2. Execute one laser update on the original partition using those captured fields.
3. Execute one laser update on the rayQ-weighted Scotch partition using the same captured fields.

Shared inputs are reconstructed on the original global mesh and copied before candidate decomposition. Seven checkpoint internal fields and all three optical input fields must be exactly equal after repartition, before tracing starts. The collector also checks that inputs remain equal, reference input bytes remain unchanged, binaries match the capture and both trace jobs, sampling and rank profiles reconcile, and T, alpha, epsilon and U do not change during either laser update. Outputs Deposition and rayQ are reconstructed at the same checkpoint time and compared on the original global mesh. Total absorbed power is checked separately; agreement of total power alone cannot pass a spatial discrepancy.

The solver's `frozenLaserProbe` control defaults to `off`. `capture` and `trace` exit before flux correction and the normal time loop. Normal laser calls retain automatic profiling at write times; the trace diagnostic suppresses that automatic report and emits exactly one explicit profile. There is no material-model, ray sampling, stepping, absorption or exchange algorithm change.

Each solver launch has a five-minute budget, with the existing checkpoint request/shutdown grace on timeout. Each native utility has a five-minute timeout. Builds, copying and postprocessing add time; the whole wrapper is not limited to five minutes. Job timing includes startup and does not represent full-CFD speedup. Metadata's duration/end fields belong to the preparation helper; the explicit frozen time is 180 us and transient steps are zero.

The wrapper creates one `M247_frozen-laser-YYYYMMDD-HHMMSS_review.tar.gz`, including build/preflight evidence, capture log/provenance, both distinctly named trace logs/configurations, native logs, weight summary, initial/input checks and `frozenLaserReview.json`. Send this archive on success or failure. A wrapper exit of zero means collection completed; the report's `optical_partition_gate` determines optical equivalence. Raw fields are not archived; norms are computed on Ubuntu.

Failure with verified identical inputs implicates the optical calculation's partition sensitivity; it does not by itself identify a specific ownership, stepping or merge defect. Passing narrows the earlier coupled discrepancy toward transient field preparation, flow/thermal discretisation and nonlinear evolution; it does not prove every timestep or partition equivalent. This is a diagnostic, not production approval. Strict field/power tolerances remain `1e-12 + 1e-8 * reference magnitude`.
