# M247 numerical design — 0.6 Pa / 350 W / 1000 mm/s / 2 mm

Status: **design baseline; not yet a completed CFD result**

## 1. Frozen process target

User-specified inputs:
- chamber pressure: 0.6 Pa;
- laser power: 350 W;
- scan speed: 1000 mm/s = 1 m/s;
- melt-track length: approximately 2 mm;
- powder: approximately one layer, with the active track region covered as
  continuously as practicable.

At 1 m/s, a 2-mm scan requires 2.0 ms laser-on time.

Still to be frozen before the final production run:
- exact beam diameter/radius convention and beam profile;
- laser wavelength;
- initial/preheat temperature;
- actual powder chemistry certificate/heat composition;
- nominal recoater/layer setting if available.

None of these unresolved items is inherited from the old V2 case.

## 2. Legacy-repository scope

`KrisIrving/M247-github` is used only as a numerical-design reference.

Useful observations:
- intended powder PSD: D10 about 36.5 um, D50 about 52.6 um, D90 about 74.4 um;
- discrete support approximately 32.5-77.5 um;
- a settled one-layer realization occupied roughly an 80-um vertical envelope;
- the old mesh used a fine near-surface slab and graded deeper substrate.

Not retained:
- material constants;
- optical constants/absorptivity;
- preheat;
- evaporation formulation;
- saved DEM particle coordinates.

## 3. Powder-bed design

Until a newer experimental measurement/certificate is supplied, use the older
PSD only as the **provisional target distribution**:
- D10 about 36.5 um;
- D50 about 52.6 um;
- D90 about 74.4 um;
- support approximately 30-80 um.

Initial engineering layer envelope:
- substrate surface y = 0;
- powder top limit 80-100 um.

The exact envelope is not yet an experimental fact.

Single-layer SLM measurements report packing densities about 44-56%; therefore
an initial engineering target around 0.45 with a documented sensitivity band is
reasonable, but the actual M247 bed measurement must override it.

Because the bed must be well covered, the manifest must report projected
track-corridor coverage/gap statistics as well as volumetric solid fraction.

Required powder-manifest outputs:
- fixed seed and exact particle CSV;
- requested and realized D10/D50/D90;
- number/volume-weighted PSD where relevant;
- packing fraction;
- projected coverage and maximum uncovered gap in the active corridor;
- highest particle top;
- overlap/minimum-gap diagnostics.

If layer-ceiling rejection biases the PSD or leaves large bare corridors,
modify the generator before CFD rather than tuning laser/material physics.

## 4. Coordinate system and production domain

Current convention:
- x: scan direction;
- y: vertical;
- z: transverse;
- substrate surface y = 0.

Recommended first production envelope:
- x = -0.25 to +2.25 mm (2.50 mm total);
- z = -0.30 to +0.30 mm (0.60 mm total);
- y = -0.60 to +0.65 mm (1.25 mm total).

Rationale:
- 0.25-mm start/end margins keep the 2-mm heated track away from x boundaries;
- 0.60-mm substrate depth leaves clearance below the expected keyhole and
  reduces bottom-boundary influence;
- an 80-100-um powder layer leaves at least about 0.55 mm gas headroom for
  protrusions, droplets and spatter before the top boundary;
- +/-0.30 mm transverse extent keeps the melt pool/keyhole away from side
  boundaries while remaining computationally manageable.

This is a first design, not a universal convergence result. A short
boundary-sensitivity run must verify it before final publication cases.

## 5. Mesh layout

T13b establishes:
- 8 um captures mean moving-keyhole depth adequately for engineering screening;
- 4 um remains necessary for local evaporation/recoil/interface quantities.

Do not use a globally uniform 4 um mesh for the 2-mm case.

Initial 8-um fine corridor:
- x: full scan/buffer region;
- z: approximately -0.18 to +0.18 mm;
- y: approximately -0.32 to +0.18 mm.

Coarsen smoothly outside it:
- deep substrate below y=-0.32 mm;
- upper gas above y=+0.18 mm;
- transverse shoulders outside |z|=0.18 mm.

Target outer cell sizes increase gradually toward roughly 16-32 um.
Avoid abrupt large cell-size jumps adjacent to the active VOF region.

Expected first-design cell count is approximately 1.0-1.3 million cells,
subject to final block grading.

## 6. Laser path and physical time

Nominal path:
- x = 0 at t = 0;
- x = 2.0 mm at t = 2.0 ms;
- scan speed = 1 m/s;
- laser power = 350 W during the scan.

After 2.0 ms:
- laser off;
- optionally retain 0.1-0.2 ms post-scan if final morphology is required.

Do not freeze ray count, beam radius, wavelength or complex refractive index
until actual optical inputs are resolved.

## 7. Output strategy

Recommended:
- compact VACUUM_DIAGNOSTICS throughout;
- full fields every 10-20 us initially;
- binary output;
- restart points retained;
- reconstruct only fields/times needed for analysis.

Required histories:
- moving keyhole depth and bottom lag;
- Tmax/Umax;
- interfacePVapMax;
- deposited power;
- evaporation/radiation power;
- recoil-force components;
- interface area;
- deltaT/Courant/interface-Courant.

## 8. Runtime strategy

The completed 304L 8-um, 160k-cell, 300-us track required about 6.68 h on
48 ranks.

A 2-ms M247 case with about 1.0-1.3 million cells is therefore expected to be a
multi-day job on the same workstation. Simple linear scaling gives order
10-15 days before material-dependent timestep changes.

Before full launch:
1. run a 20-50 us M247 preflight;
2. measure cells/step, steps/us and wall time/us;
3. project full 2-ms cost from the actual M247 case;
4. then launch production.

## 9. 4-um verification

Use a short M247 segment with the same powder realization, material/optics,
power/speed and pressure. Compare 8 and 4 um before publication-level claims.

A global 4-um 2-mm run is not the baseline plan.

## 10. Boundary-model caution

The outer phase remains a numerical pseudo-gas reservoir. At 0.6 Pa it is not
a resolved rarefied Ar/plume model.

Therefore:
- top/side boundaries provide numerical reservoir accommodation, not a
  quantitative plume exhaust model;
- pseudo-gas density/viscosity sensitivity remains required;
- spatter trajectories are metal-VOF dynamics in a numerical outer phase, not
  a validated rarefied-gas particle-transport prediction.
