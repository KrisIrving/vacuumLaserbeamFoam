# Wang 304L current-solver optical approximation suite

Run from repository root after sourcing the intended OpenFOAM-v2512 environment:

```bash
bash tests/m247Performance/RunWangRaySuite
```

Uses the existing current compiled solver; preflight verifies solver/library identity
and profiling/refresh markers. No automatic rebuild, timeout, kill or cleanup.
Four sequential fresh cases: rays1536/rays768/rays384/rays192, angular counts
96/48/24/12 and radial count16. All start at0 and end140us; 4um80^3 mesh,
48 ranks, identical copied decomposition and initial fields, output every2us.
Do not run concurrently with another48-rank simulation.

Common physics: original Wang304L near-vacuum template,20.265Pa,260W,
100um beam,1070nm, stationary plate, Fe fixed-complex-index Fresnel optics,
unchanged evaporation/radiation/material/boundaries. Common current numerical
settings: bounded enthalpy correction, epsilon tolerance1e-5, phase-temperature
tolerance0.001K, phase blending0; cached traversal, corrected handoff and
consistent termination enabled. Every-step laser updates, path recording off,
packed broadcast/cache experiments off. Angular sampling is the only variant
difference. This is not a legacy/current thermal-algorithm pair.

Official blockMesh/setFields/checkMesh/decomposePar prepare one common seed;
mpirun launches each variant; reconstructPar and postProcess generate connected
alpha0.5 depth and recoil surfaces using existing Wang extraction scripts.
Initial/decomposition/physics settings remain in each case. Raw fields/surfaces
remain on Ubuntu; the single uniquely named review archive contains all four
logs, dictionaries, provenance, depth/recoil CSVs and liquid-volume summaries.
Failures also package; see failure.json/comparison.json/manifest.json.

Reports: job wall and section timing; thermal convergence/caps; full connected
depth history; interpolated first32-to136um growth interval versus historical
76.2318us, Wang~75us and experiment~70us; absorption/evaporation/Tmax;
metal liquid volume integral(alpha.metal*epsilon1 dV); axial force and scalar
pressure load. In this coordinate system the beam is along-y, so the axial
surface force is full_recoil_force_y_signed_N, not the z component.
Scalar integral(p dS) is reported separately and must not be called axial force.

User budgets are applied to depth/volume/Tmax histories relative to current
1536-ray baseline:5%/5%/10%. Per-step diagnostics interpolate baseline times
only within common coverage; geometric/volume histories compare2us outputs.
Early nonzero ratios are retained, with peak-normalised and absolute errors
also reported for interpretation. Candidate-nonzero/reference-zero samples
prevent a budget PASS. These are numerical comparison budgets, not experiment
accuracy bounds. No recoil/evaporation acceptance threshold is invented.

Fastest passing converged candidate is recommended only for M247 confirmation.
Wang literature/history review and M247 longer heating/cooling/grid checks
are still required; production_approved remains false. If no candidate passes,
do not automatically select192 or relax criteria.

After a postprocessing/collection repair, reuse existing results without CFD:

```bash
python3 tests/m247Performance/wang_ray_suite.py --collect --work tests/m247Performance/runs/wang-ray-suite-TIMESTAMP
python3 tests/m247Performance/wang_ray_suite.py --package --work tests/m247Performance/runs/wang-ray-suite-TIMESTAMP
```

Four full4um histories may take hours; do not extrapolate M247 mature8um cost
into a promise for this stationary-growth run. Printed stage names and each
case's live log show progress. Retain the runs for further offline analysis.
