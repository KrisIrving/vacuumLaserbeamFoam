# Current fix and automatic small native preflight

154937 constructor succeeded and read the initial state; V0 was still absent
because storeOldVol only acts when the current index exceeds mesh history.
The diagnostic driver had reset synthetic indices to1..8. It now advances from
max(initial Time index, mesh history index), logs both indices and checks that
they increase continuously before every topology change.

The same RunMovingWindow command now automatically generates a2400cell uniform
case and runs all8 refine/coarsen updates before copying the original case.
The small preflight has a120second budget and tests the identical compiled native
lifecycle, linear product proxy mapping, interior coverage and positivecoarsening.
It tests machinery, not powder/optical/enthalpy correctness. Failure stops the
real-case launch and is automatically packaged. Native repaired small and real
runs are still pending Ubuntu; Python unit tests do not certify native behavior.

Keep the old directories. Pull and run the command below to obtain a fresh run.
The small preflight budget is additional to the real native30minute budget;
build/copy/hash costs remain extra. No change to real meshquality/cellbudget gates.

# Fix after the 154023 constructor exit

The tools compiled; the diagnostic subclass's direct constructor triggered the
motion-solver parent's mandatory initialization, failing before any mesh update.
Construct with doInit=false and then call dynamicRefineFvMesh::init(true), which
performs the staged refinement initialization allowing zero motion solvers.
The V0 lifecycle fix and all mapping/quality/budget checks remain active.

Pull and rerun RunMovingWindow below using its default fresh output. Native
corrected constructor/updates still require Ubuntu validation.

# Fix after the 153230 first-update abort

The two diagnostic utilities compiled. The first refinement reached1239840cells
from756000, then dynamicRefineFvMesh::mapFields aborted because V0 was missing.
The mesh-only driver's synthetic time labels did not initialize old cell volumes.
The driver now uses a diagnostic subclass to call the protected OpenCFD lifecycle
helper storeOldVol(V) before each update, checks finite positive old volumes equal
current pre-update volumes, and emits8 initialization records checked by Python.
It introduces no point motion and keeps physical fields frozen between mappings.

Pull and rerun the same RunMovingWindow command below; the default creates a
fresh work directory. No data from the aborted topology operation is reused.
Native repaired compilation/mapping is still to be validated on Ubuntu.

API reference: [v2512 fvMesh.H](https://api.openfoam.com/2512/fvMesh_8H_source.html).

# Moving fine-window prototype

Run from the repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunMovingWindow
```

Defaults reuse the hash-verified coarse serial case referenced by the retained
104821 restart audit (101101 preview), not a new copy/reconstruction of48ranks.
The wrapper builds m247MovingWindowCheck and the geometry audit utility; it does
not rebuild the production solver. Keep the original audit/preview directories.

The native prototype uses OpenCFD v2512 dynamicRefineFvMesh/hexRef8, one refinement
level, one buffer layer, maximum2000000 cells. Starting756000 cells, the moving
window spans192um in x and192um in z through the existing full y height. Central
original cells are8um; their children are4um. Refine and unrefine are active.
Window x centres80,160,0,80um are a mechanical stress path, not a laser trajectory
or simulated scan speed. Two topology updates at each position test retention,
coarsening and return;8 snapshots are saved at synthetic audit slots180us+i*1ns.
These slots carry the frozen180us state, not physical elapsed time.

At every update it records cell/protected-cell counts, refinement coverage of the
window interior (16um inset), mapping bounds/integrals, and update wall time.
T/alpha/epsilon and two independently mapped product proxies are registered;
no native flow/energy equations run. The saved cases contain mesh snapshots only
and are not valid CFD restarts. Existing stale velocity/flux/native fields must
not be used to resume this mesh audit as a solver case.

Checks distinguish:

- Domain volume/metal volume and independently mapped alpha*T, alpha*epsilon
  proxy integrals:1e-20+1e-9*initial magnitude mapping limits.
- Direct products of independently mapped T/alpha/epsilon: signed drift is
  reported separately. Passive proxy conservation does not prove enthalpy or
  physical liquid volume conservation. There is no correction/clipping to hide drift.
- Settled interior refinement coverage at all four centres and observed native
  coarsening with a positive removed-cell count.
- Native checkMesh for every snapshot. Native failures remain recorded. Existing
  scoped coplanar-roundoff qualification applies only to that one failure with
  the native concavity geometry diagnostic; all other failures reject the prototype.

A passing prototype gate certifies only the above topology/linear-mapping checks.
It does not establish isoAdvector, pressure continuity, normals/optics, momentum,
enthalpy conservation, molten-wake coverage, speedup, or thermal-only exterior.
Artificial coarsening through frozen material is deliberate: nonlinear product
drift reveals what conservative solver-state transfer will require.

Native stages share a30minute wall budget; each subprocess is capped at20minutes
or remaining budget. Compile, serial copying and initial/source hashing are extra.
Eight full mesh snapshots require several GB of additional disk space. The review
archive contains small logs/reports/dictionaries only and is created on success
or failure. Send:

`tests/m247Performance/runs/M247_moving-window-<timestamp>_review.tar.gz`

Development order after this test: integrate a protected molten/hot-wake moving
mask into existing mesh.update/isoAdvector/correctPhi path, preserve conservative
energy/material state across coarsening, and run a short matched fixed/moving CFD
pair with the same normal reconstruction. Only measured cell/work/physics results
justify longer tracks. Thermal-only outer region coupling follows this moving-mesh
foundation rather than disabling pressure/flow cells independently.

Official APIs checked:
[dynamicRefineFvMesh v2512](https://api.openfoam.com/2512/dynamicRefineFvMesh_8H_source.html)
and [createDynamicFvMesh v2512](https://api.openfoam.com/2512/createDynamicFvMesh_8H.html).

## Protected frozen hot/molten wake

The 160259 baseline completed: 27 archive hashes/sizes verified, wrapper exit0,
2400-cell smoke passed, all eight real updates completed, source unchanged.
Real peak1320480 cells, total update58.397612s, all native stages324.091s.
Observed coarsening removed873600 cells cumulatively (not unique cells).
Maximum relative linear proxy drift4.24e-11; direct alpha*T drift7.87e-12,
alpha*epsilon drift2.99e-13. Native checkMesh still reports one concavity failure
per snapshot; all eight pass the existing scoped coplanar-roundoff qualification.
This is a completed topology/mapping prototype, not measured CFD acceleration.

Run the next bounded stage:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunMovingWindow --protect-wake
```

The optional mask includes the moving box AND cells with metal fraction>1e-6
and T>=1537K (this case's metal solidus) or epsilon1>=1e-4. An independently
mapped initial hot/molten marker also retains every descendant with a positive
marker. It prevents averaging across a threshold from silently releasing frozen
hot material. The marker is passive; fields are not corrected or clipped.
This uses the same one-level refiner and cell cap, not protectedCell's topology
restriction mechanism. All settled wake cells must reach level1, including cells
outside the moving window; initial marked volume must be conserved and cold-area
coarsening must still occur. The collector rejects absent protection evidence.
The graded shoulders are not uniformly4um merely because they reach level1.

The 2400-cell preflight also uses protection: a48-cell1600K column outside all
four window positions, with1400K/epsilon0 background. It checks independent wake
coverage while the window moves and cold cells coarsen. The budget remains120s
plus30minutes for real native stages; build/copy/hashing are extra.
Send the single `M247_moving-window-protected-<timestamp>_review.tar.gz`.

The retained initial marker is deliberately permanent ONLY for this frozen-state
mapping audit. A production solver must release cooled/solidified material from
protection with a justified buffer/hysteresis policy; it must not accumulate all
historically heated cells indefinitely. This test does not certify transient wake
length, enthalpy/momentum transfer, pressure/VOF mapping, optics or solver restart.
After this stage, integrate state/flux transfer into the actual solver and run
one short matched CFD pilot before increasing track length.

## Sparse binary mask correction (162215)

The first protected smoke failed correctly:48 hot cells were never refined,
although all8 updates completed. Large-case copying did not start. Default point
averaging diluted the one-cell-wide mask to the lower0.5 threshold, producing no
positive refinement error. Protected mode now directly selects exact1-valued cell
mask entries through the2512 virtual candidate hook. Other refinement selection,
2:1/topology restrictions/cell budgets and all coverage checks remain enforced.
Unprotected mode retains the base selector. Each protected update must report
matching requested/selected candidate counts and the correct time index. Sparse
column smoke and outside-window coverage remain mandatory, not weakened.

The archived native failure is a regression fixture; Python pass count does not
prove native behavior. New C++ build and small+real native passes remain pending.
Run the same --protect-wake command. Errors/status are tracked in
`log/M247_ERROR_REGISTER.md`. Freeze solver integration until this gate passes.

Preflight failures now retain exception type, text and failure stage in
movingWindowSmokeReview.json, with large_case_started=false. Native command
completion, topology gate pass and CFD validation are distinct states. The
archived sparse-column diagnostic records are checked by the Python regression
suite; they must never receive protected-mode approval. See the
[error register](../../log/M247_ERROR_REGISTER.md) for previous failures and
required closure evidence.
