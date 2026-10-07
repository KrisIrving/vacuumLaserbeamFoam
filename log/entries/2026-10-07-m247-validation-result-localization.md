# Two-us candidate validation result and offline localization

Reviewed M247_validation-20261007-161510_review.tar.gz; all manifest file lengths/SHA256 checks pass, missing_files empty, wrapper exit 0. Both source snapshots and binary hashes match. Both 166-step runs finish with no cap/budget/forced stop. Standard correctors average 10.518 (range 9–14), tight 14.319 (13–18). Maximum final per-step epsilon increments 7.971068003e-5 / 7.938431958e-6; phase consistency 0.009972830162 / 0.0009979917791 K. Nonlinear convergence gate passes.

Standard/tight actual wall 342.355821 / 379.395654 s. Standard MPI mean laser 217.975327 s (64.065%), thermal 74.766989 s (21.975%), pressure 25.547022 s (7.509%). Laser is now the dominant runtime component, but local field sensitivity must be resolved before further production acceleration.

Final field max differences: T 316.081105 K; epsilon 1; alpha 0.011933679; U 10.5905171 m/s; p_rgh 53682.664639 Pa. RMS values 0.5579569 K / 0.00304298 / 3.764889e-5 / 0.0214054 m/s / 158.7337 Pa. Global diagnostic differences are comparatively small, so they cannot substitute for cell-level field inspection. The archive does not contain fields or differing-cell locations. No physical acceptance gate is declared passed; no gas/interface origin is assumed. Production approval remains false.

Added offline localize_field_differences.py and InspectThermalValidation wrapper to read the already saved final fields, classify disjoint alpha regions based on both states, count diagnostic exceedances, locate top 10 cells/field, record full local field values and alpha=0.05 crossings. Coordinates are not guessed from processor cell indices. Added small summaries to automatic archives, using a new archive name so existing uploads remain untouched. No solver/numerical changes or CFD reruns.

Local verification: 27 tests, shell syntax and diff checks passed. Actual localization pending user's Ubuntu fields. Immediate action and command are in tests/m247Performance/FIELD_LOCALIZATION.md. Longer 10–20-us/grid/energy/keyhole validation remains contingent on resolving field sensitivity.
