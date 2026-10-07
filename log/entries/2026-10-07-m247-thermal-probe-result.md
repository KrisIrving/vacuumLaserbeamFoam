# Ubuntu enthalpy-correction result and named review archives

User provided two logs and probe/run metadata. Variant identities were resolved from case headers and boundedEnthalpy records, not download suffixes: log (8) is enthalpyBounded; log (9) is thermalLegacy. probe.json is legacy; probe (1).json is candidate. run.json (35.036218 s) is candidate; run (1).json (127.133841 s) is legacy. Solver/library hashes match, source snapshot hashes match. Logs cover 180–180.2 us and end normally; neither run metadata reports a budget or forced stop.

| Quantity | Legacy | Candidate |
|---|---:|---:|
| Physical steps | 16 | 16 |
| Total thermal correctors | 2416 | 180 |
| Correctors per step | 151 | 10–14 (mean 11.25) |
| Thermal cap hits | 16 | 0 |
| Actual job wall seconds | 127.133841 | 35.036218 |
| Sum interval rank-max loop seconds | 125.126998 | 33.112092 |
| MPI mean thermal seconds | 101.064188 | 7.694360 |
| MPI mean laser seconds | 19.665065 | 20.909014 |

Actual job speedup is about 3.629x (72.44% less wall time); thermal section is about 13.13x faster. This is a single 0.2-us sample, not an extrapolated full-track multiplier. Candidate final max epsilon increment <= 8.000739225e-5 and phase-temperature mismatch <= 0.009980752911 K; every step has zero cells above epsilon tolerance. Legacy final maximum remains 1 in interface cells; gas maximum is zero. The deterministic worst legacy cell is rank 0/local 8837 at (-100,676,-140) um, alphaMetal about 0.05361–0.05447, cp about 536 J/(kg K), mixed latent heat about 8.0–8.2 kJ/kg, full 1537–1631 K melting interval and sensibleLatentRatio about 6.17–6.26. Its final update explicitly switches epsilon 0->1 or 1->0. This supports the interface over-correction hypothesis; other cells and the full nonlinear mechanism still require validation.

Physics is close but not identical to the unconverged legacy reference. Over the two output times, Tmax difference <= 0.009244 K; maximum deposited-power difference 0.0766759 W (0.02348%); max pVap relative difference about 0.01608%; interface-area difference <= 0.0002444%. The small recoil Z component differs by 2.37% at the first output, with absolute difference 3.9726273e-8 N, and about 0.02117% at the last output. Do not describe all quantities as within 0.03%, or this as a passed physical regression. Longer intervals, tighter converged reference, alpha/T/U fields, keyhole topology and energy accounting remain required before production/grid refinement.

User requested unambiguous names and one archive to upload. Added package_results.py, automatic EXIT collection in both wrappers, and explicit run/variant names for logs, probe/run JSON, selected dictionaries and comparison files. Manifest includes SHA256, missing files and wrapper exit code. Processor fields/mesh are excluded. No files are renamed or removed in the source run; archives are exclusively created. Failed/incomplete runs can be collected without implying PASS. A packaging failure preserves an existing nonzero wrapper status and makes an otherwise successful wrapper nonzero. Shell termination that prevents an EXIT trap may require manual packaging.

Next development priority: extend the candidate beyond 0.2 us and compare to a tighter converged enthalpy reference, with field/energy validation. Do not rerun this short investigation merely to rename files: package the existing run with --work tests/m247Performance/runs/thermal-20261007-154702.

Local verification: 19 Python harness/model/packaging tests and shell syntax. No solver changes in this packaging commit; the candidate defaults remain off.
