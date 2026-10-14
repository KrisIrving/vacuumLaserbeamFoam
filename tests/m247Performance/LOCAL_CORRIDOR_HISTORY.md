# Existing 0�C50 us local-corridor field histories; no CFD run

The local pilot completed in 5,190.88 s versus 12,347.94 s (2.379x).
Final connected solidus depth/width match, but final global Tmax differs
by 13.398%, exceeding the user's 10% temperature limit. Do not continue
this static local case to 1.5 mm or relax the acceptance limit.

The archived liquidus-cell count is a threshold proxy, not integrated
liquid fraction. The archives also lack initial field equivalence and
keyhole histories. Collect those from the already saved processor fields:

```bash
cd ~/OpenFOAM/kris-v2512/vacuumLaserbeamFoam-m247
git pull --ff-only origin feat/m247-material-port
bash tests/m247Performance/CollectM247LocalCorridorHistory \
  tests/m247Performance/runs/m247-track1500-v2-pilot-20261013-144606/track1500 \
  tests/m247Performance/runs/m247-local-corridor-pilot-20261013-192358/track1500
```

Use the terminal with OpenFOAM-v2512 loaded. The script checks version,
project directory and actual wmake path before native operations. Both
original run directories and their 48 processor histories are needed;
the small review tar.gz files alone do not contain those fields. Missing
times/fields stop collection before reconstruction; they never trigger CFD.

Fresh analysis cases copy system/constant and link the resolved original
processor directories for reading. Official `reconstructPar -time
0:0.00005 -fields '(alpha.metal T epsilon1)'` reconstructs saved fields
in the analysis case; `postProcess -func writeCellCentres -time 0` writes
the static mesh centres there. Original file sizes/mtime are checked before
and after. This is metadata verification, not a content hash guarantee.
Initial epsilon is absent in the template; zero is assumed only after
verifying that the initial metal is below solidus. No solver is launched,
rebuilt or advanced. Reconstruction creates large local ASCII analysis
fields; only compact reports and native-command logs enter the review archive.

The common ROI is x=-240..300, y=180..720, z=-192..192 um: 518,400
identical 6 um cells. Initial alpha/T are compared by coordinates, not
cell numbering. Each saved 10 us state reports alpha*epsilon liquid volume,
metal volume, regional temperatures, solidus extents, and the depth of
alpha<0.5 gas connected to the ROI top through cell faces. This cavity
depth has approximately 3 um centre-position uncertainty and still needs
comparison with the established interface/literature definition. Metrics
are restricted to the common ROI, not the entire powder bed. The original
failed temperature screen is preserved; collection does not approve production.

Send the single `M247_m247-local-corridor-history-<timestamp>_review.tar.gz`,
including on failure. Next use the histories to distinguish initial mapping
differences from later flow/optical feedback before altering the local mesh.
