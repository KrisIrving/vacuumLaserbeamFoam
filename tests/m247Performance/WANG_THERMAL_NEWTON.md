# Complete Wang full-ray thermal iteration test

Ring-staggered384 failed the agreed full-history budget. It remains default-off.
Do not run another reduced-ray sweep to hide interface Tmax discrepancies.
All original histories, including1536-ray reference, have thermal cap hits;
their hottest cap cells are nearly pure metal in the melting interval.

The existing boundedEnthalpyCorrection update already uses latent+sensible
enthalpy slope. epsilonRelaxation0.5 halves each update. New test uses1.0,
within the solver's existing0<relaxation<=1 supported range, to test a full
correction instead of half correction. This is a convergence hypothesis,
not guaranteed Newton convergence for coupled transport/evaporation/VOF.
No C++ change, solver rebuild, tolerance relaxation, raised/reduced cap, source
hold or angular simplification. Optical count remains1536, staggered false.

```bash
git pull --ff-only origin feat/m247-material-port
bash tests/m247Performance/RunWangThermalNewton
```

One fresh0..140us,4um,48-rank history from the retained verified initial seed.
Source argument optionally overrides default completed wang-ray-suite-20261011-000847.
All other physics/numerical dictionaries must match the retained1536 case.
Iteration epsilon tolerance1e-5, phase consistency0.001K, maxTempCorrector150.
Official mpirun/reconstructPar/postProcess; no automatic kill, timeout or clean.
Prior full-ray run took6.01h; actual new runtime/convergence must be measured.

Reports compare current full-ray thermal gate, step/iteration costs, complete
depth/volume/Tmax and absorbed power/recoil histories to retained1536/384.
These are historical job cost comparisons. The old1536 reference has163 cap
hits; a converged candidate cannot be called validated solely against that
unconverged reference. production_approved stays false. First decision is
whether convergence and cost improve without new temperature/geometry errors.
If still capped, do not merely loosen thresholds or change phase physics.

Archive M247_wang-thermal-newton-TIMESTAMP_review.tar.gz contains build-note,
preflight, current logs/settings/results, reference evidence and hashes.
Send it even on failure. Runs and archived reference evidence are retained.
Collection-only recovery (no CFD):

```bash
python3 tests/m247Performance/wang_staggered.py --thermal-newton --collect --work tests/m247Performance/runs/wang-thermal-newton-TIMESTAMP
python3 tests/m247Performance/wang_staggered.py --thermal-newton --package --work tests/m247Performance/runs/wang-thermal-newton-TIMESTAMP
```
