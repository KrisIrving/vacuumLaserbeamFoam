# M247 DEM local corridor: one decisive 0–50 µs cost/physics comparison

The completed v2512 V2 DEM pilot required 12,347.94 s for 50 µs on 48 ranks
with 3,814,272 cells. Pressure accounted for 51.11% of loop wall time. A
pressure-only change cannot make the 1.5 mm static case affordable. The old
fixed crop achieved only 1.23× in a different 8 µm mature state; the prior
moving refinement had significant update cost. This experiment tests whether
the current 6 µm corridor can use substantially fewer cells **without changing
the first 50 µs melt result**.

It copies the V2 template and verified native DEM bed into a fresh case. The
outer domain, 6 µm y/z melt zone, 384 rays, solver, fields and all boundaries
remain the same. Fine x is restricted to −240…300 µm, 90 cells at 6 µm instead
of −240…1680 µm, 320 cells. The far-ahead right slab is graded through 72
cells to the original x=1920 µm boundary; left slab is unchanged. Expected
mesh count is 1,929,312 (49.4% fewer cells). The completed baseline melt
front at x=141 µm leaves 159 µm fine-grid allowance in this 50 µs interval.
That observation does not authorize extending this static fine zone beyond
50 µs. A true translating fine zone and global thermal history are future work.

Run in a terminal that has loaded `~/OpenFOAM/OpenFOAM-v2512/etc/bashrc`:

```bash
cd ~/OpenFOAM/kris-v2512/vacuumLaserbeamFoam-m247
git pull --ff-only origin feat/m247-material-port
bash tests/m247Performance/RunM247LocalCorridorPilot \
  tests/m247Performance/runs/M247_m247-powder-dem-20261013-140626_review.tar.gz \
  tests/m247Performance/runs/M247_m247-track1500-v2-pilot-20261013-144606_review.tar.gz
```

The wrapper verifies both archive provenance and the active v2512 environment
before compiling or launching CFD. It runs only the new candidate; the old
baseline is never changed or rerun. Standard OpenFOAM `wclean`/`wmake` and
`blockMesh`/`setFields`/`checkMesh`/`decomposePar`/`reconstructPar` commands
are used. On completion or error it packages a single uniquely named
`M247_m247-local-corridor-pilot-..._review.tar.gz` archive.

`comparison.json` requires matching DEM archive, all non-mesh input hashes,
solver and laser-library hashes, 48 ranks, 384 rays, and 50 µs duration. It
reports mesh/pressure/job cost and compares connected solidus melt depth and
width, liquidus metal cell count, and peak temperature. A provisional screen
uses ≤5% for the first three and ≤10% for temperature, plus thermal/fine-zone
checks. These are **not** keyhole-depth or final-track acceptance criteria.
Deposited power and the startup T linear-solver cap are reported separately.
An apparent speedup only supports further moving-window development; neither
this static local case nor its 50 µs projection is a 1.5 mm simulation.

