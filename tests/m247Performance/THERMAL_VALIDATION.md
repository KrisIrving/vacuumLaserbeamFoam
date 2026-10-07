# Next Ubuntu gate: 2-us convergence-tolerance sensitivity

The 0.2-us candidate converged and measured a 3.63x job speedup against the unconverged legacy algorithm. The next gate compares two converged uses of the same candidate, over a ten-times-longer interval. It does not run the legacy capped algorithm again.

From the Ubuntu repository root, with OpenFOAM v2512 sourced and the solver built for the previous thermal probe:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunThermalValidation
```

Both cases restart independently from the original 180-us state and run to 182 us on the same 48-rank decomposition. Both use the candidate correction and disable visual ray histories. enthalpyStandard uses epsilonTolerance=1e-4 and phaseTemperatureTolerance=0.01 K. enthalpyTight uses 1e-5 and 0.001 K. Everything else in their configured controls is equal. Both write new fields in ASCII at 181/182 us; original binary restart fields are copied unchanged. This output choice supports dependency-free comparison and can increase I/O versus the earlier binary probes. The two validation variants have equal output cadence/format. Standard and tight tolerances are recorded in probe.json.

Each job has a 30-minute wall budget. Scaling the earlier short candidate gives about 6 minutes per standard run plus copy/startup/ASCII output; the tighter run is unmeasured. Allow roughly 15–30 minutes for the pair as a planning estimate, not a promise. A budget stop fails completion. Do not increase the budget or loosen tolerances silently after a failure.

The collector requires complete intervals and matching source snapshots, ranks and solver/library hashes. Every step must satisfy its configured epsilon and phase-temperature criteria with zero cap hits. It compares final internal T, epsilon1, alpha.metal, U and p_rgh for every processor, reporting max differences and cell-count-weighted (not volume-weighted) RMS; vector differences use Euclidean magnitude. Uniform/nonuniform ASCII fields and gzip are supported. Truncated, binary, missing fields or inconsistent cell counts are rejected. The comparator targets this fixed M247 mesh, rejects dynamicMeshDict and new time/polyMesh states, and does not compare boundary fields or directly compute keyhole topology/energy balance.

The comparison outputs are thermalValidation.json, diagnosticComparison.csv and fieldComparison.csv. Strict diagnostic_pass retains the earlier very tight equality test only as a sensitivity indicator; it is not the acceptance criterion for changed convergence tolerance. convergence_gate checks nonlinear convergence. production_approved is always false: physical accuracy, keyhole topology and energy accounting still require review. No arbitrary field-error acceptance threshold is assigned by this tool.

On exit, a named archive is created automatically:

```text
tests/m247Performance/runs/M247_validation-YYYYMMDD-HHMMSS_review.tar.gz
```

Send that single archive. It includes labelled logs/metadata/configurations and comparison summaries; large processor fields remain on Ubuntu. The printed live log paths can be followed in another terminal. Failures collect available evidence and are not reported as successful validation.

If this gate shows convergence and small tolerance sensitivity, the next engineering gate is a 10–20-us candidate run with keyhole/field/energy inspection, then local 4-um refinement. This tool does not authorize that later production gate automatically.

Local verification: 25 harness/model/parser/comparison tests and shell syntax. Actual Ubuntu execution is pending. This change adds test tooling only; it uses the existing candidate solver binary.
