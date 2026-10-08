# Experimental full-solver moving-window pilot

The protected frozen prototype164709 passed. The next stage runs the actual
vacuumLaserbeamFoam isoAdvector, pressure, momentum and thermal equations with
an opt-in m247MovingRefineFvMesh. It tests compatibility, not measured speedup.

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunMovingCFDPilot
```

Default prerequisite: runs/moving-window-protected-20261008-164709. The script
revalidates its raw protected topology log and source hashes, then copies the
ORIGINAL audited coarse180us case. Mesh-only snapshots are not solver restarts.
It rebuilds the solver only; previously built laser/material libraries remain
required. The window follows the existing single laser table, covers full yheight
and192um x/z. One-level refinement and2M global cell cap are retained. Graded
shoulder cells at level1 are not all4um. Static cases do not select this mesh.

Hot metal (alpha>1e-6,T>=1537K or epsilon>=1e-4) activates a mapped/written wake
hold field; cold solid cells release below1487K and epsilon<=1e-6. The50K buffer
is an experimental numerical policy. Releasing cooled material prevents permanent
accumulation of all historic hot cells, but needs later cooling/hysteresis study.

The pilot advances180..180.2us on48ranks. Its first topology change exercises full
registered fields, geometric VOF mapping and phi reconstruction/CorrectPhi.
The laser moves only0.2um: large window translations/coarsening were tested by
the frozen prototype; this pilot cannot establish meaningful transient movement
or cooling behavior. Initial refinement adds startup cost, so it cannot establish
steady moving-window acceleration. A matched fixed/moving CFD pair follows only
once compatibility and state-transfer checks pass.

Every topology call reports material volume and rho*(cp*T+L*epsilon) before/after
RAW field mapping (before isoAdvector subsequently remaps alpha). The latter is
a screening proxy, not integral thermodynamic enthalpy with temperature-dependent
cp. No energy correction is implemented. Relative drift>1e-6 or uncovered held
wake stops the native solver; this does not prove full-step energy conservation.
Final-step records include alpha/epsilon bounds,T/U finiteness and phi divergence.
Collector requires all per-step records and final time, converged thermal iterations
with no limit hits, and divL1<=0.05/s,divMax<=15000/s continuity screens. These are
pilot gates, not production tolerances. No production approval is issued.

Solver budget15minutes plus graceful checkpoint-stop allowance; native command
budget30minutes includes decomposition. Compilation/copying/hashing are extra.
Writes full decomposed fields twice; allow severalGB disk headroom. Reports,
binary hashes, dictionaries, full solver log and failure evidence are bundled:
`tests/m247Performance/runs/M247_moving-cfd-pilot-<timestamp>_review.tar.gz`.
Send that single archive on success or failure.

124Python tests and shell checks do not establish native OpenFOAM runtime:
the changed C++ build and48-rank pilot are pending Ubuntu. Check log/M247_ERROR_REGISTER.md
for closed prototype issues and the separate pending solver integration.

Solver launch reserves240s within the shared command deadline for writeNow/MPI
shutdown; the15minute solver budget is shortened if decomposition consumes most
of the shared budget. No solver starts when that reserve cannot be met. Rebuild
and launched solver hashes must match. Wake hold is initialized at the restart
time before the first time increment, so saved hold state can be read correctly.

Pilot startup deltaT1ns, maxDeltaT5ns and maxCo/maxAlphaCo0.1 avoid taking
a coarse-grid-sized first timestep across the initial refinement. These conservative
compatibility settings are not a production speed benchmark.
