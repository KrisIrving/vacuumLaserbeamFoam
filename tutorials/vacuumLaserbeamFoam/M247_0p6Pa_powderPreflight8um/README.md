# M247 0.6-Pa powder preflight — 8 um

Purpose: the first powder-bed transfer gate after the completed 100-us
bare-plate test. This case deliberately keeps the same laser duration/path so
the effect of adding one M247 powder layer can be compared directly.

## Frozen process input

- substrate: M247;
- powder: M247;
- chamber pressure: 0.6 Pa;
- global initial preheat: 1343.15 K (1070 degC);
- laser: 350 W;
- scan speed: 1.0 m/s;
- spot diameter: 86 um;
- wavelength: 1064 nm;
- scan: 100 um / 100 us.

## Domain / mesh

- x = -200 to +200 um;
- y = 0 to 960 um;
- z = -160 to +160 um;
- original substrate surface y = 600 um;
- substrate depth = 600 um;
- powder geometric envelope = 80 um;
- gas headroom above powder envelope = 280 um;
- uniform 8 um;
- 240,000 cells;
- 48 MPI ranks.

The deeper substrate is a direct response to the bare-plate result:
keyhole depth reached approximately 200 um at 100 us and was still increasing.

## Powder definition

The supplied experimental/numerical PSD target is represented as a fixed
piecewise quantile distribution:

- Dmin = 30 um;
- D10 = 36.5 um;
- D50 = 52.6 um;
- D90 = 74.4 um;
- Dmax = 80 um.

Nominal layer thickness is 50 um. The geometric ceiling is 80 um because the
largest particles exceed the nominal recoater thickness.

Target nominal-layer packing is 0.58. The generator freezes the complete
diameter set before placement and therefore never replaces an unplaceable large
particle with a smaller draw.

Seed 247001 was selected deterministically because it gives high coverage in
the active corridor while preserving the same PSD:
- expected particle count approximately 29;
- expected nominal-layer packing approximately 0.577;
- expected active-corridor projected coverage approximately 0.836;
- expected maximum uncovered centerline gap approximately 26 um.

This is still a geometric initial-condition generator, not DEM.

## Post-processing

PostprocessTrack reconstructs both:
- alpha.metal;
- T.

The keyhole metric still uses only the atmosphere-connected main alpha=0.5
interface.

## Gate

Do not proceed directly to the approximately 2-mm production track unless this
case:
1. completes without fatal/non-finite behavior;
2. retains adequate bottom/top boundary clearance;
3. has plausible deposited-power / evaporation / recoil histories;
4. yields an acceptable powder/keyhole topology;
5. provides a measured wall-time projection for the final 2-ms case.
