# Existing local mesh restart audit

The 101101 sizing preview completed both alternatives. Four layers give
2,283,911 cells; ten layers give 2,889,026. Both preserve the checked volume,
metal volume, liquid proxy and metal-temperature moment. Native allGeometry
reports only concaveCells, with no other failed checks. Outward vertex-plane
excursions are at most 8.7e-19 m / 1.02e-13 of cell-volume length.

The [OpenCFD primitiveMesh source](https://api.openfoam.com/2312/primitiveMeshCheck_8C_source.html)
tests other face centres against each outward face plane and explicitly marks
"concave or planar face". The coplanar subdivided faces at hex refinement
transitions explain these flags; the recorded tiny outward excursions are
consistent with floating-point geometry error. This is a supported inference,
not proof that arbitrary flagged meshes are safe.

The raw strict native failure remains visible. A separate scoped qualification
requires exactly one failed check and only the concaveCells flag, matching
native/diagnostic counts, face flatness >=1-1e-12, maximum outward distance
<=1e-15 m AND normalized distance <=1e-10, and zero cells above the previously
reported relative1e-9 diagnostic. These are project screening limits; they are
not OpenFOAM recommended tolerances. No native threshold or mesh coordinates
are changed. This qualification allows restart investigation, not production.

Run on Ubuntu from the repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/AuditLocalRestart
```

Default input is the retained run
`tests/m247Performance/runs/local-refinement-20261008-101101`. To use another
complete sizing preview, pass its work directory as the first argument.
Do not regenerate either mesh. The wrapper builds only m247MeshPreviewCheck,
runs fresh checkMesh and read-only native field checks on coarse/four/ten-layer
cases. checkMesh may rewrite diagnostic sets; mesh, system and field files are
hashed before/after and must remain identical (sets excluded).

The new -restart mode reads U, phi and alphaPhi0.metal, validates dimensions
and finite values, reports volume-weighted L1/RMS/max div(phi), signed integral
div(phi), maximum internal U, the sum of absolute differences from fvc::flux(U),
total absolute velocity/alpha flux and zero internal-flux face counts. Divergence
rates are in 1/s; integrated and surface flux sums are in m3/s. A zero flux
can be physically valid; flux(U) need not equal pressure-corrected phi exactly.
Compare with coarse data rather than imposing zero differences indiscriminately.
The audit does not reconstruct isoAdvector surfaces or project pressure/flux.

Every complete audit reports restart_ready=false until subsequent continuity,
interface and bounded CFD checks establish suitability. No flow or temperature
equations are advanced. Each utility has a20-minute timeout, excluding build
and hashing time. Failure evidence is packaged automatically with case names.
Send the one file:

```text
tests/m247Performance/runs/M247_local-restart-YYYYMMDD-HHMMSS_review.tar.gz
```

The next implementation will use measured flux mapping errors to decide whether
startup projection/reconstruction is necessary before a bounded four-layer CFD
pilot. Ten layers increase cell count26.5%; keep it as buffer-sensitivity evidence
rather than assuming the smaller candidate has enough future physical margin.
Neither mesh sizing nor scoped geometry qualification establishes runtime gain,
fine-grid physical convergence, or full-track coverage.
