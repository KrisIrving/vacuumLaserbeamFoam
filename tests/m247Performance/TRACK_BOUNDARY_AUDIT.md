# M247 1.5 mm static pilot: boundary audit after 50--60 us pressure pair

This audit uses the native20261012-105416 pilot mesh/log/initial input hashes,
the native20261012-150149 PCG/GAMG restart archive, and the exact case
dictionaries in revision64e88511. Normalising Windows checkout line endings
toLF matches all five original initial-field SHA256 hashes recorded by the
pilot. The pair's constant and system copies are byte-identical except
fvSolution pressure method and controlDict time/write controls. Native
checkMesh reports one connected region, correct three patches and Mesh OK.

Patch layout: bottomWall at y=-240um, atmosphere at y=960um, sideWalls on
all remaining x/z planes. Original substrate top is y=600um. Both current
50--60us molten pools are y>=477um, at least717um from bottom. At60us,
PCG molten x[-153,189]um and z[-147,123]um; the nearest exterior side
plane is z=-384um,237um away. Thus no molten metal touches an exterior
boundary in these observations. Flow/thermal boundary independence has not
been established without a larger-domain comparison or patch flux data.

Field boundary review:

* alpha.metal: zeroGradient on bottom/sides, inletOutlet with inflow0 at
  atmosphere. This prevents metal entering on backflow and lets it leave
  the open top. U slip on bottom/sides enforces zero normal velocity, so
  those alpha zeroGradient patches do not by themselves drive metal flux.
  A bottom no-slip wall would be more physical, but here it is840um below
  the substrate surface and outside observed melt. The solid damping term
  also suppresses motion in solid metal. No boundary sensitivity is proved.
* U: slip at bottom/sides, pressureInletOutletVelocity at atmosphere is
  mathematically compatible with an open velocity patch. Side slip also
  reflects/confines gas flow, which can matter at longer times. Confirm
  with patch fluxes or a larger atmosphere/side domain before final physics
  claims.
* T: fixed1343.15K at bottom (experimental preheat); zeroGradient at
  sides/top. At the open top, any reverse flow extrapolates the interior
  gas temperature rather than prescribing fresh chamber gas. The model's
  chamberTemperature is298K while the initial pseudo-gas is1343.15K.
  These serve different model roles, but zeroGradient top backflow is a
  modelling assumption, not a proven chamber-gas condition. Inspect top
  backflow and temperature; then compare an inletOutlet T boundary with
  explicit inflow temperature if material.
* p_rgh: fixedFluxPressure at bottom/sides and totalPressure with p0=0
  on top. The evaporation model independently uses chamberPressure=0.6Pa;
  p0=0 therefore acts as a flow-pressure reference, not proof of a physical
  zero-pressure vacuum. OpenFOAM v2512 defines a separate prghTotalPressure
  condition that explicitly subtracts rho*g*h from total p. Applying
  totalPressure directly to p_rgh omits that correction. In the present
  pseudo-gas (rho=1kg/m3), its magnitude at y=960um is about0.0094Pa,
  but it could differ if metal reaches the top. A corrected p_rgh boundary
  and consistent absolute/gauge reference should be compared from a common
  checkpoint before production. Do not silently change this archived pair.
* Laser_boundary: top fixed1 and other exterior faces fixed-1 match the
  downward V_incident=(0,-1,0) and the three mesh patch names. The beam
  starts0.5um beneath the top plane. No boundary-name mismatch or laser
  source fatal error appeared in the native runs.

Critical fine-grid issue: the configured x-fine interval is[-240,1620]um,
while the laser travels from x0 to1500um. At60us its molten front x=189um
is129um ahead of beam x=60um. The terminal allowance is120um,9um less than
that observed forward reach, even before a safety margin or later change
of pool size. The current pilot passes its local fine-margin test only
because it has not approached the x-fine endpoint. Extend the fine x strip
to at least1680um (180um terminal allowance) and then rerun blockMesh,
checkMesh and a new pilot; do not attempt to restart the old4.23M-cell
partition on a different mesh without validated field mapping. A moving
window is a separate development path, not yet accepted for production.

OpenFOAM primary references for the conditional inletOutlet behaviour and
the p_rgh total-pressure relation:
https://doc.openfoam.com/2312/tools/processing/boundary-conditions/rtm/derived/inletOutlet/inletOutlet/
https://api.openfoam.com/2512/prghTotalPressureFvPatchScalarField_8H_source.html
