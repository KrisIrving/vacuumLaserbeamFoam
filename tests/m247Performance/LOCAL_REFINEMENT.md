# Static local-refinement preview

## Recovery after the 003900 mesh-quality failure

The four-layer preview has 2,283,911 cells and preserves all four checked
moments, but native checkMesh finds 15,101 concave cells. It is rejected;
the ten-layer preview did not execute. Pull the update and reuse the serial
coarse restart from that run:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/PreviewLocalRefinement --resume tests/m247Performance/runs/local-refinement-20261008-003900
```

Resume copies only constant/system/180 us serial data into a fresh output,
hashes every copied file, and checks the new coarse moments against the previous
record exactly. It skips 48-rank restart copying and reconstructPar. The native
checker is rebuilt, and both refinement alternatives are regenerated from coarse
data. Previous cases are not overwritten. Each completed quality failure is
reported and the next variant is evaluated. A budget skip or quality failure
still exits with status 2 and packages the evidence; this is expected and is
not approval to advance CFD. Partial reports have complete=false.

For failed concaveCells sets, a separate native diagnostic reads that exact
set, checks its count, and reports vertex bounds and maximum outward signed
distance to the cell's outward face planes, in metres and normalized by cube
root of cell volume. The count above a relative 1e-9 is descriptive, not a new
quality threshold. This supports investigation of geometric versus roundoff
effects; it does not reproduce or waive the native concavity algorithm.

Run from the repository root in an OpenFOAM v2512 shell:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/PreviewLocalRefinement
```

The wrapper builds only `m247MeshPreviewCheck`. It copies the original completed
48-rank case at 180 us, reconstructs all restart fields on the copy, then creates
two serial mesh previews. It does not run the CFD solver or advance time.
The original case is read only. Allow disk space for the copied parallel restart
and three serial cases. Each native utility has a 20-minute timeout; this is not
a total wall-time guarantee. Compilation time is additional.

Selection retains every mixed material interface (`0.001 <= alpha.metal <=
0.999`), including cold powder, and every warm cell (`T >= 1368.15 K`, preheat
plus 25 K), including gas. `localRefine4` adds four neighbouring cell layers;
`localRefine10` adds ten. In the central 8 um mesh these nominally represent
32/80 um, but graph layers do not guarantee that metric clearance in graded
regions. These are sizing alternatives, not two approved physical settings.

Native `refineHexMesh` splits selected cells once, halving their local edges,
and may extend the selection for consistency. Central selected cells become
4 um; graded shoulder cells do not all become 4 um. The predicted cell count
is `756000 + 7 * selected_cells`. A preview above three million predicted cells
is skipped. Actual cell count must also remain below three million.

Before and after refinement, checks require positive finite cell volumes,
finite positive temperature, bounded alpha/epsilon, and preserved total volume,
metal volume, liquid-volume proxy, and metal-temperature moment. The relative
moment tolerance is 1e-9 plus an absolute 1e-20. These moments are not enthalpy
or flux conservation checks. `checkMesh -allGeometry -allTopology` must report
`Mesh OK.`. A failed or skipped variant makes the overall preview gate false.
Failures still trigger packaging, with partial logs rather than a PASS report.

Send the one automatically generated archive:

```text
tests/m247Performance/runs/M247_local-refinement-YYYYMMDD-HHMMSS_review.tar.gz
```

Every preview log/dictionary has its variant in the filename. Large mesh/field
files stay on Ubuntu and are not included in the review archive.

Passing this gate establishes only snapshot mesh size/quality and selected
mapping moments. It does not establish isoAdvector interface reconstruction,
enthalpy/velocity/flux mapping, optical equivalence, future melt coverage,
MPI performance, or a CFD speedup. Cost ratios assume equal per-cell work and
twice as many steps; they are planning scenarios, not timings. A mature-state
restart is not a substitute for a complete 4 um powder-track simulation.

Next development uses the preview to choose a feasible mesh, verifies the
restart and interface/flux treatment, then runs a bounded 2 us CFD pilot before
setting any 24-hour validation duration. Longer tracks still need a region
following the laser and a conservative thermal treatment of the outer domain.
Merely suppressing flow equations in remote cells does not remove global matrix
cost or the global small timestep.

Native utility references:
[refineHexMesh source](https://api.openfoam.com/2406/refineHexMesh_8C_source.html),
[fieldToCell](https://api.openfoam.com/2312/classFoam_1_1fieldToCell.html),
[haloToCell](https://api.openfoam.com/2506/classFoam_1_1haloToCell.html).
Actual v2512 compilation and execution remain Ubuntu checks.
