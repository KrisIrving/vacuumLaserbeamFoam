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
