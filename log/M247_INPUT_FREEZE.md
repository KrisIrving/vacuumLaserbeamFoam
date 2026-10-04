# M247 experiment-input freeze — v0

## Purpose

This file separates experimentally fixed inputs from provisional material-model
choices for the M247 transfer. The Wang near-vacuum equations remain frozen.
Only M247-specific inputs and numerical design are being added.

## Experimentally fixed inputs

| Quantity | Frozen value | Notes |
|---|---:|---|
| Chamber pressure | 0.6 Pa | experiment |
| Metal/powder/substrate initial temperature | 1343.15 K (1070 °C) | global preheat retained from the prior experimental case |
| Laser power | 350 W | experiment |
| Scan speed | 1.0 m/s (1000 mm/s) | experiment |
| Nominal melt-track length | 2.0 mm | experiment |
| Nominal laser-on travel time | 2.0 ms | derived from length/speed |
| Line energy | 0.35 J/mm | derived from power/speed |
| Spot diameter | 86 um | experiment |
| Spot radius | 43 um | derived |
| Wavelength | 1064 nm | experiment |
| Nominal powder layer thickness | 50 um | experiment/numerical target |
| Powder size support | approximately 30–80 um | retained target PSD definition |
| Powder D10/D50/D90 | 36.5 / 52.6 / 74.4 um | retained target PSD definition |

## Temperature convention

The **1343.15 K preheat** is the initial temperature of the modeled metal
substrate and powder. It is not automatically the same as either:

1. the far-field residual-gas temperature used by the Wang common-atmosphere
   transition relations; or
2. the effective radiative environment / chamber-wall temperature.

For the first constitutive transfer:

- metal/powder initial temperature = 1343.15 K (frozen);
- Wang far-field chamber temperature = 298 K primary reference;
- Wang chamber-temperature sensitivity = 1343.15 K;
- effective radiative-environment temperature remains to be frozen separately.

No production claim should silently identify these three temperatures.

## Frozen numerical policy from T13b

The strict 304L 0.6-Pa pair established:

- 8 um is acceptable for full-track/broad engineering screening;
- 4 um is required for key quantitative verification of local evaporation,
  recoil, bottom-lag and publication-quality short/key cases;
- 8 um must not be described as grid-independent.

For M247, a short matched 8/4-um transfer check is still required before the
final publication claim.

## Provisional M247 material inputs

Until the actual powder certificate is supplied, the material-port screening
uses a literature M247 composition (wt.%):

- Cr 8.09
- Co 9.31
- W 9.40
- Ta 3.21
- Al 5.49
- Hf 1.50
- Ti 0.69
- Mo 0.51
- Ni balance = 61.80

This composition is a **temporary screening input**, not the final experiment
chemistry.

Likewise, the first material-property bracket uses literature values around:

- solidus: 1536–1537 K;
- liquidus: 1629–1632 K.

Final rho(T), cp(T), k(T), viscosity, surface tension, d(sigma)/dT,
emissivity and alloy-level latent heat remain to be frozen from traceable
sources.

## Provisional powder-bed interpretation

The nominal deposited layer is 50 um, but particles extend to roughly 80 um in
diameter. Therefore the generator must distinguish:

- nominal layer thickness: 50 um;
- geometric particle envelope: approximately 80 um;
- equivalent dense thickness / packing;
- projected surface coverage.

A target packing fraction near 0.58 from the earlier numerical design may be
used only as an initial engineering target until experimental bed-density data
are available.

The new generator must preserve the target final PSD. It must not preferentially
remove large particles by redrawing smaller particles whenever a large particle
does not fit below a geometric clipping plane.

## Provisional production-domain envelope

First full-track design target, subject to the M247 short bare-plate result:

- x (scan): -1.30 to +1.30 mm;
- y (vertical): -0.50 to +0.40 mm, with substrate surface y=0;
- z (transverse): -0.25 to +0.25 mm;
- laser path: x=-1.00 to +1.00 mm.

The upper boundary is an open atmosphere boundary. The domain is intended to
resolve near-field protrusions/jets/droplets, not to retain every high-speed
spatter particle for the full 2-ms track.

## Still required before production M247 CFD

1. actual powder chemistry certificate / heat composition;
2. substrate material identity;
3. final thermophysical-property source set;
4. M247/Ni-based optical surrogate and sensitivity at 1064 nm;
5. effective radiative-environment temperature;
6. final powder packing/coverage target;
7. desired post-scan cooling duration.

None of these blocks the initial constitutive vapor-pressure screening.
