# M247 1.5 mm, 6um corridor V2: geometry correction

This is a separate mesh template. The original50/60us archives retain the
original geometry for reproducibility. Use RunM247TrackPilotV2 to create a
fresh case; never restart old partitions on this changed mesh.

The old 60us molten front was129um ahead of the laser but the old terminal
fine-zone allowance was only120um. V2 extends fine x to1680um, giving180um
ahead of the planned1500um endpoint (51um margin at the observed front).
The domain ends at x1920um, so the observed-size forward front would still
be291um from the external x boundary at the endpoint.

The finest y region begins at180um:420um below the original substrate
surface y600um. The older M247 powder-track 200us8um archive recorded a
moving keyhole depth316.55um and liquidus-isotherm minimum y273.50um
(326.50um below the substrate surface). V2 has about93.50um fine-grid
allowance below that older molten extent; a full new run must verify it.
The graded bottom block is 24 cells with simpleGrading0.18 to connect
approximately to6um cells at y180um. This is a cost/accuracy hypothesis;
only native blockMesh/checkMesh and the new pilot can validate it.

Fine core x[-240,1680], y[180,720], z[-192,192]um at6um. Outer domain
x[-480,1920], y[-240,960], z[-384,384]um. Expected3,814,272 hexes,
9.9% fewer than the original4,232,448. The original powder, process,
thermal settings and boundary field conditions are retained for a controlled
mesh comparison. Native speed, melt depth/width and fine-zone margins are
not established. PressurePCG remains the solver method; GAMG was slower.

Boundary audit: tests/m247Performance/TRACK_BOUNDARY_AUDIT.md. The top T
backflow and p_rgh total-pressure choices need further sensitivity evidence;
this V2 geometry correction does not imply final boundary approval.

From the repository root with OpenFOAM-v2512 loaded:

```bash
git pull --ff-only
bash tests/m247Performance/RunM247TrackPilotV2
```

The first run stops at50us and produces one uniquely named review archive.
No previous case is modified and no full-track run starts automatically.
