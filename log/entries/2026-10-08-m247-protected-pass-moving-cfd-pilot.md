# M247 protected native pass and full-solver pilot

Reviewed protected164709:27 archive SHA256/size checks valid; wrapper0,
missing_files empty. Independently reconstructed small and real native mapping
reports (timing sums tolerance1e-12) and all eight geometry qualifications.
48 small hot cells become384 children and remain covered at every position.
Real initial25631 hot cells become205048 children; wake coverage stays complete
including105384..184312 fine cells outside the moving box. Peak1428574 cells;
8updates57.067949519s; all native commands339.735414s; coarsening720664 cumulative
cells. Maximum relative linear proxy error4.95407e-11; maximum nonlinear direct
product drift6.65122e-12. Native checkMesh still reports one concavity failure
per snapshot (25471 cells in step1); all scoped coplanar-roundoff qualifications
pass. This closes MW04 sparse-selector runtime failure, not production CFD.

Added opt-in m247MovingRefineFvMesh runtime mesh inside vacuumLaserbeamFoam.
Both IOobject and doInit constructor tables registered; constructor defers base
initialization exactly as verified in the native prototype. The2512 official
header confirms both tables and virtual selection signature;2506 source confirms
base coefficient dictionary behavior; full2512 source retrieval was unavailable.
Static cases retain their selected mesh and equations. Custom mask follows the
single original laser interpolation table, keeps full height and192um x/z span,
uses direct binary candidates and one-level/2M cap. Hot/mushy metal activates
m247WakeHold, released only below1487K and epsilon<=1e-6 (50K hysteresis below
1537K solidus); hold state is mapped and saved. This is an experimental policy,
not validated wake length or cooling physics. The solver uses its existing
isoAdvector reconstruction/mapAlphaField and CorrectPhi/pressure/energy path.
No new flow/thermal equations or energy correction are introduced.

New RunMovingCFDPilot rebuilds solver only and advances copied original coarse
180..180.2us on48ranks, requiring the completed protected prototype, raw logs,
source hashes, isoAdvector/rank/table/binary checks before launching. Existing
laser/model libraries must already be built. Solver budget15minutes plus stop
checkpoint grace; decompose/run subprocesses share30minute command budget;
build/copy/hashing extra. Errors/partial logs/reports automatically packaged with
movingCFD names. No production restart from mesh-only prototype snapshots.

M247_MOVING_CFD records actual topology/wake and pre/post raw-field mapping
integrals before isoAdvector remaps alpha. rho*(cp*T+L*epsilon) is a stored-field
screening proxy, not integral thermodynamic enthalpy; native stops on relative
metal/proxy drift>1e-6 or missed wake. Final-step records check bounded alpha/eps,
finite T/U and phi divergence after the full solve. Collector requires one mesh
and state record per step, exact final time, thermal residual convergence/no caps,
and continuity divL1<=0.05/s,divMax<=15000/s (pilot screens only). No speedup pair,
physical equivalence, long-wake release or enthalpy conservation claim.

124 Python tests pass; py_compile and Bash syntax pass. Changed solver native
compilation and48-rank runtime pending Ubuntu. Next pull and
./tests/m247Performance/RunMovingCFDPilot; send automatic
M247_moving-cfd-pilot-..._review.tar.gz. After compatibility passes: matched
fixed/moving-grid CFD comparison with energy/flux audit, meaningful longer
movement/cooling interval, then resolution/cost assessment. Do not extrapolate
24h feasibility from frozen mesh timing or this0.2us interval alone.

Solver launch reserves240s within the shared command deadline for writeNow/MPI
shutdown; the15minute solver budget is shortened if decomposition consumes most
of the shared budget. No solver starts when that reserve cannot be met. Rebuild
and launched solver hashes must match. Wake hold is initialized at the restart
time before the first time increment, so saved hold state can be read correctly.

Pilot startup deltaT1ns, maxDeltaT5ns and maxCo/maxAlphaCo0.1 avoid taking
a coarse-grid-sized first timestep across the initial refinement. These conservative
compatibility settings are not a production speed benchmark.
