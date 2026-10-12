# M247 1.5 mm powder provenance hold — 2026-10-12

The V2 1.5 mm template currently contains 330 spheres from
`sequentialVerticalDeposition-v2`, not LIGGGHTS. The user now requires a
LIGGGHTS-generated bed before the next CFD run. `RunM247TrackPilotV2` rejects
the geometric bed before building the solver or preparing CFD.

The geometric bed does match the provisional number-based PSD target:
D10/D50/D90 = 36.545/52.611/74.334 um versus 36.5/52.6/74.4 um; diameter
range 30.098–79.915 um. Its analytic sphere volume gives 0.580013 of the
nominal 50 um layer, but only 0.362508 of the 80 um geometric envelope.
The 1.5 mm by 150 um laser corridor has projected coverage 0.725102 on a
2 um grid, with a 58 um maximum uncovered centerline span. Five consecutive
300 um sections have coverages 0.7240, 0.7100, 0.6927, 0.7453, and 0.7535.
The earlier 200 us case had 0.802204 coverage over a *different*, only
240 um long corridor, so these coverage values are not a matched comparison.

`largestFirst` placement induces strong size-height sorting: 118/120 spheres
with D >= 60 um touch the substrate, versus 5/62 with D < 40 um; the
Pearson correlation of diameter and lower-surface height is -0.803. This
geometric arrangement cannot establish physically representative DEM packing.
The actual 6 um mesh-voxelised metal fraction has not been measured for V2.

`RunM247PowderDEM` now creates a candidate through LIGGGHTS rain deposition,
trims to the 80 um envelope, checks the raw/final dump and conversion, records
PSD, nominal packing, overlap, residual particle speed, five-section coverage
and vertical sorting, and packages one archive. It does not alter the case or
run CFD. Contact stiffness, restitution and friction are provisional values
adapted from the upstream laserbeamFoam DEM tutorial, with M247 solid density.
No recoater is modelled. Native LIGGGHTS execution and powder acceptance remain
outstanding. The final experimental bed-density and coverage targets remain
unfrozen. After reviewing the native archive, install an accepted DEM bed,
check `blockMesh`/`setFields`/`checkMesh` on Ubuntu, then run the 50 us V2 CFD
pilot.

