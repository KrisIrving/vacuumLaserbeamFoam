# Full Ubuntu thermal log review and candidate development

Inputs: user-supplied log (6).vacuumLaserbeamFoam (baseline), log (7).vacuumLaserbeamFoam (noRayPaths), comparison.json. Case headers confirm variant identities and OpenFOAM v2512, 48 ranks.

Each log contains 166 physical steps and 25,066 temperature/nonlinear phase solves. All 25,066 maximum epsilon increments are exactly 1. The two logs' complete (mean,max) epsilon residual sequences are identical at logged precision. Final-step mean increments range from 7.96035792e-6 to 1.447513268e-5. First step: mean increment falls from 7.583892514e-5 at corrector 1 to 1.180927298e-5 at 2, then plateaus around 1.182e-5 through corrector 151; maximum stays 1 throughout.

Temperature linear solves: 24,734 use 1 iteration and 332 use 2; maximum reported final linear residual is 4.431423425e-10. Thus the principal measured failure is nonlinear phase correction, not a large temperature linear iteration count. A maximum increment of 1 in a field clamped to [0,1] proves some cell changes between the endpoints during every correction; logs cannot determine whether it is always the same cell, its alpha or location.

Exact mean-rank section totals from comparison.json: thermal 1075.052055 -> 1060.548269 s; laser 362.132328 -> 223.885442 s. Laser drops 38.18%, while thermal changes only 1.35%. Actual job wall drops 10.728%. Single sequential-pair repeatability remains untested.

The phase update coefficient cp/L can be large in mixed cells while updateProps assigns the full metal melting interval for alpha>0.05. This motivates, but does not establish, an interface over-correction cause. Added opt-in final-residual cell location diagnostics and a default-off enthalpy slope correction cp/(L+cp*meltingInterval). Same interior fixed point, changed numerical trajectory. Added a separate candidate phase-temperature consistency criterion of 0.01 K to guard against false convergence from small updates; original max-epsilon tolerance and corrector cap are retained.

Next Ubuntu action: RunThermalProbe, legacy versus candidate, both noRayPaths, 180–180.2 us, independent snapshots and a 15-minute budget per job. It reports both logs and metadata, not a production PASS. Details and isolated-cell derivation: tests/m247Performance/THERMAL_PROBE.md. The existing original RunPair explicitly uses the legacy correction.

Validation: 16 Python harness/model tests, Bash syntax, diff checks passed. Initial local test invocation was blocked by Windows temporary-directory permissions; using a workspace-contained temporary root succeeded. Bash startup required a read-only syntax check outside the sandbox. No OpenFOAM compiler/runtime is available here; Ubuntu compilation, nonlinear improvement, field accuracy and measured candidate speed remain unverified. Longer-window, converged reference, field/topology and energy validation are required before production.
