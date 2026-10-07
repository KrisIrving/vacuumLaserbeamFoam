# Existing-field region and budget audit

Run from the repository after pulling feat/m247-material-port:

```bash
./tests/m247Performance/InspectRegionBudget
```

Defaults: original M247_0p6Pa_powderTrack200us8um source and latest completed
ray-physics-impact pair. Explicit paths can be supplied:

```bash
./tests/m247Performance/InspectRegionBudget \
  tutorials/vacuumLaserbeamFoam/M247_0p6Pa_powderTrack200us8um \
  tests/m247Performance/runs/ray-physics-impact-20261007-233712
```

This builds only m247RegionAudit, then reads original 100/120/140/160/180/200-us
snapshots and both existing impact cases at180/181/182us on48ranks. No CFD solver,
time advancement, reconstruction, mesh modification or field write. Each utility
launch has a10-minute budget plus30s kill grace; build time is additional. Inputs
must retain the original fixed756000-cell mesh, M2471537/1631K phase limits and
the existing movingKeyholeDepth.csv/moltenExtent.csv. Defaults are deliberately
specific to this checkpoint. All new logs/reports go to a fresh audit directory.
No new copied CFD state or large field archive is created.

Regions use actual cell volumes and full selected-cell vertex bounds, reduced
over all ranks. A metal-masked liquidus region (alpha>=0.5,T>=1631K) separates
molten metal from hot gas. Additional diagnostics: active material
(alpha>=0.01 and epsilon>=0.01 or hot mixed-interface cells), warm metal
(alpha>=0.5,T>=1368.15K, the1343.15K preheat plus25K preset), hot gas
(alpha<0.01,T>=1631K), and material moving>=1m/s. These are sizing proxies,
not definitions of future pressure, VOF or thermal subdomains. Volumes are
weighted; envelope bounds are conservative cell bounds, not interpolated
isotherms. Finite/positive cell volumes and finite fields are required; alpha/
epsilon bounds are separately reported. Snapshots cannot certify full-history
stability. The old unmasked isotherm CSV is included for comparison, not treated
as a material-filtered melt boundary gate.

The collector requires all selected times and all six region rows per time,
fixed mesh bounds/count, expected48ranks/material configuration and completed
utility logs. It hashes copied reference files, checks matched/converged impact
logs, reports existing connected/supported keyhole trends, and calculates six
clearances. Raw fields are not packaged: region reductions remain Ubuntu
utility output, independently parsable from its full logs.

It produces an80um-padded union envelope of active-material snapshots, reports
clipping and a uniform4um box cell-count estimate. This envelope does not cover
future keyhole growth, cold powder preservation, gas transport or optical-path
resolution; it is not a mesh or coupling approval. No flow equation is disabled.
The next implementation uses these measurements to size a graded fixed local
fine mesh, followed by a conservative thermal/fluid coupling prototype. A mere
velocity mask cannot justify a cost reduction or preserve pressure/VOF coupling.

Budget scenarios use the measured corrected 180–182us job cost, with explicit
cell r^3 and timestep r assumptions when refining all existing edges by r.
They reserve20% of24h and report a2us pilot. Full-track timing holds the measured
workload fixed and omits domain growth/cooling: it is a scenario, not a forecast.
Initial4um validation should be a bounded2us cost/mapping pilot; allocate longer
physics verification only after measuring its actual cost and mapping quality.
Original100–200us data still show positive late depth growth, so a200us4um run
or full-track production is not approved by this audit.

Send the single automatically printed
`M247_region-budget-..._review.tar.gz`, including failures. It contains named
audit logs, utility/source hashes, source CSVs, reference impact logs/provenance,
regionAuditReview.json and regionEnvelopes.csv. Wrapper exit0 means collection
completed; production_approved always remains false.
