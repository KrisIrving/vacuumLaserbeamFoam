# Projected-flux local-grid compatibility pilot

110422 completes this pilot successfully. Next use RunLocalOptics as described
in LOCAL_OPTICS.md to isolate the observed optical/grid sensitivity. Do not
repeat the flux pilot or extend CFD until that evidence is reviewed.

104821 restart audit identifies a real continuity defect in mapped phi:
coarse volume-weighted |div(phi)|=0.02664/s, four-layer=88759.27/s,
ten-layer=93421.85/s. Refined maximum divergence=8.2985e7/s. Scalar moment
preservation does not imply conservative surface-flux mapping. Zero internal
flux face counts are zero in all cases; no evidence that simply filling zero
faces fixes this defect. All alphaPhi0.metal absolute sums are zero even on
coarse; this alone does not establish a new mapping defect in that history field.

Run from the repository root on Ubuntu:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunLocalFluxPilot
```

Default input is `tests/m247Performance/runs/local-restart-20261008-104821`.
Pass another complete qualified restart audit as the first argument if needed.
The original meshes/cases remain unchanged. The wrapper builds only the checker;
existing solver/library preflight is performed before CFD. No solver equations
or default production controls are changed.

The program checks audited source hashes, copies only the four-layer serial
case, checks copy hashes, then rebuilds phi from fvc::flux(mapped U). A scalar
potential q satisfies laplacian(q)=div(phi), and phi is corrected by subtracting
the discrete equation flux. Five nonorthogonal solves use PCG/DIC, residual
tolerance1e-13, relTol0, maxIter10000. q has dimensions m2/s. Its boundary value
is zero where p_rgh fixes pressure, with zero normal gradient elsewhere; a
fixed-pressure outlet is required. This is a geometric flux-only projection,
not a new physical pressure or velocity solution.

The explicit native `-restart -project` option writes phi only. T, alpha,
epsilon, U, pressure, material coefficients, mesh and other restart files must
remain byte-identical. The projected field is re-read and screened against coarse
data: L1<=max(0.05,1.05*coarse L1), RMS<=max(15,1.05*coarse RMS), and
max<=max(15000,1.05*coarse max), all in1/s. These are initial pilot screens,
not production accuracy tolerances. Material moments must stay identical.
Failed projection never launches CFD. Copies and partial logs remain reviewable.

After projection passes, native decomposePar creates48Scotch partitions and
the existing solver advances180.0 to180.2us with the tight unsmoothed enthalpy
controls and corrected/cached rays inherited from the sizing copy. CFD has a
15-minute wall budget, then a checkpoint request and the existing180s stop grace
plus termination handling. Build, copy, projection and postprocessing are extra;
each serial/native orchestration command has a20-minute timeout. This is not
a15-minute total wrapper guarantee.

Collection checks interval completion, reconciled timers, physical diagnostics,
per-step thermal convergence and no corrector caps. Native reconstruction and
read-only final checks require finite fields, bounded alpha/epsilon and unchanged
static cell count. Final continuity is reported for assessment. This is one
0.2us compatibility pilot, not mesh convergence or a matched coarse/fine speedup
experiment. A longer mature-state pilot and interface/flux/physics assessment
are still required. Production approval remains false.

Send the automatically generated single archive (also created on failure):

```text
tests/m247Performance/runs/M247_local-flux-pilot-YYYYMMDD-HHMMSS_review.tar.gz
```

Partial reports have complete=false. No need to rerun mesh sizing or restart
audits. Large field/mesh files stay on Ubuntu. The single CFD directory retains
the existing rayTraversalCached runner name; its probe purpose explicitly states
that it is the projected four-layer local mesh, and projection logs use
localProjected names.

Discrete correction follows the same divergence-minus-matrix-flux pattern as
[OpenCFD CorrectPhi](https://api.openfoam.com/2406/CorrectPhi_8C_source.html).
It uses a constant geometric coefficient rather than solver momentum rAUf;
the subsequent CFD pilot must test the resulting startup compatibility.
