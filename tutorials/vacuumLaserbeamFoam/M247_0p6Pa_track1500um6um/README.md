# M2471.5mm track,6um melt corridor: first50us pilot

Run from repository root after sourcing OpenFOAM-v2512:

```bash
bash tests/m247Performance/RunM247TrackPilot
```

The template is copied to a fresh timestamped runs directory. No original
case is cleaned, overwritten or continued. Official wmake libso/wmake builds
current laser library/solver, then blockMesh,setFields,checkMesh,decomposePar,
mpirun -np48. The initial run stops at50us, corresponding to50um travel.
No automatic long-run launch, kill or timeout. Build or preparation failures
also produce a uniquely named review archive. Native mesh/CFD validation is
pending Ubuntu; local checks cannot certify OpenFOAM mesh quality or runtime.

Frozen process: M247,0.6Pa,1343.15K preheat,350W,1m/s,86um diameter,
1064nm.384 rays (16 radial x24 angular), normal aligned polar seeds;
staggering false,every-step update,cached traversal/corrected handoff and
termination on,ray paths/packed broadcast/transport cache off. Original
M247 material and Wang constitutive assumptions are retained.

Full path x0..1500um runs0..1500us. Power stays350W through1500us, ramps to
zero over1ns and remains zero to2000us; position holds at1500um after scanning.
The planned500us cooling segment is a first cooling horizon, not evidence of
complete solidification. The pilot does not reach laser-off or cooling.

Static27-block conforming mesh,4,232,448 cells:
- domain x[-480,1860],y[-240,960],z[-384,384]um;
- original substrate surface y600um (840um substrate depth);
- uniform6um corridor x[-240,1620],y[0,720],z[-192,192]um;
- central2,380,800 cells; surrounding blocks geometrically coarsen outward;
-48-rank Scotch decomposition. No dynamic mesh mapping/local-flow handoff.

The whole future path is fine from the start; this is a static pilot strategy,
not a demonstrated moving-window speedup. Larger mesh means fewer rays do not
guarantee a cheap full track. Pilot reports measured wall/physical-us and a
clearly labelled30x startup-rate projection for1500us; no24h promise.
Fine-zone margin and boundary adequacy must be reviewed before continuing.

Powder: deterministic seed2471500,330 particles, fixed30..80um PSD,
D10/D50/D90=36.545/52.611/74.334um,nominal50um packing0.580013,
geometric envelope80um, no overlap. Footprint x[-300,1740],z[-280,280]um.
Full-path projected corridor coverage0.7251,max centreline gap58um are reported,
not quietly treated as the earlier short-bed80% coverage. New bed is geometrical
initialisation, not DEM. Committed particles/setFields match the manifest.

Thermal iteration: boundedEnthalpyCorrection true,epsilonRelaxation1,
epsilonTolerance1e-4,phaseTemperatureTolerance0.01K,maxTempCorrector150,
phase blending0. Standard M247 convergence tolerances are retained, unlike
the tighter Wang test. Relaxation1 is supported but not yet proved better on
this case. Final per-step diagnostics and cap counts are recorded. Extra inner
corrector printing is off; this changes logging only, not stopping criteria.
If capped or expensive, arrange a matched restart thermal comparison from
retained40us checkpoint; do not lower caps or silently loosen tolerances.

Binary field output every10us,purge0 retains restart states. After CFD,
reconstructPar exports final alpha/T in ASCII; official postProcess
-func writeCellCentres gives actual coordinates. Streaming collection avoids
holding all4.23M-cell fields in Python memory. Final geometry uses alpha>=0.5
and T>=1537K solidus, with1631K liquidus envelope also reported.6-face connected
molten substrate component near beam gives melt depth and z width separately
from all molten metal/droplets. Cell-centre extents have~6um discretisation
uncertainty and are not final solidified-track dimensions. Global Tmax and
metal/interface/gas Tmax are diagnostics, not revised acceptance gates.
Molten metal outside fine corridor or close to its edge prevents a continuation
recommendation. The pilot is not a384/full-ray accuracy comparison.

Send single M247_m247-track1500-pilot-TIMESTAMP_review.tar.gz. It includes build,
mesh/solver/preparation logs, dictionaries,powder provenance, performance,
thermal and geometry reports; large fields remain in the Ubuntu run directory.
Collection-only recovery uses existing final ASCII exports:

```bash
python3 tests/m247Performance/track1500_pilot.py --collect --work tests/m247Performance/runs/m247-track1500-pilot-TIMESTAMP
python3 tests/m247Performance/track1500_pilot.py --package --work tests/m247Performance/runs/m247-track1500-pilot-TIMESTAMP
```

After pilot review, continuation uses official foamDictionary startFrom latestTime,
endTime1500e-6 then mpirun on this same case/partition. Cooling uses endTime2000e-6
with the explicit laser-off table already present. Stage metadata/logging must
be updated for later collection; do not reuse the50us pilot report as full-track
evidence. Continuation/thermal-pair automation is arranged after pilot review.
