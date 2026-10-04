# M247 0.6-Pa bare-plate preflight — 8 um

Purpose: a short, inexpensive transfer test before any powder-bed or 2-mm
production run.

## Frozen experiment inputs

- substrate: M247;
- chamber pressure: 0.6 Pa;
- global initial preheat: 1343.15 K (1070 degC);
- laser: 350 W;
- scan speed: 1.0 m/s;
- spot diameter: 86 um;
- wavelength: 1064 nm;
- short path: 100 um in 100 us.

## Numerical geometry

- x = -200 to +200 um;
- y = 0 to 640 um;
- z = -160 to +160 um;
- original substrate surface y = 400 um;
- 400 um substrate below the surface;
- 240 um gas headroom;
- uniform 8 um mesh;
- 160,000 cells;
- 48 MPI ranks.

This case is intentionally not the final 2-mm geometry. It is used to determine
whether the production domain needs more substrate depth/headroom.

## M247 material provenance

Direct / primary M247 choices:
- chemistry: recent measured MAR-M247 powder literature fallback;
- solidus/liquidus: recent MAR-M247 DSC, approximately 1537/1631 K;
- fusion latent heat: 150 kJ/kg, inside the measured 140-164 kJ/kg DSC band;
- rho = 7950 kg/m3: reported MAR-M247 solid density;
- liquid viscosity = 8.5 mPa s: reported MAR-M247 melt value;
- surface tension = 1.70 N/m: reported MAR-M247 melt value;
- component vapor pressure: Mondal et al. (2023) wide-range pure-element fits.

Explicit provisional/surrogate choices:
- cpSolidus/cpLiquidus = 790/860 J/kg/K: closely related CM247LC literature;
- kSolidus/kLiquidus = 29/35 W/m/K: Ni-superalloy / MAR-M247 literature range;
- dSigma/dT = -2.5e-4 N/m/K: provisional Ni-superalloy value;
- emissivity = 0.30: provisional;
- optical n=2.611, k=5.842 at 1064 nm: Johnson-Christy Ni surrogate;
- numerical pseudo-gas properties: inherited numerical reservoir, not physical
  0.6-Pa gas.

These provisional quantities are not yet publication-frozen material constants.
The short case exists partly to expose whether they require targeted sensitivity
before powder production work.

## Temperature convention

The thermal field starts globally at 1343.15 K to preserve the experimental
high-temperature preheat used in the previous numerical design.

The Wang far-field residual-gas temperature remains 298 K in the primary run.
Radiation uses an independent environmentTemperature=1343.15 K so the preheated
surface has zero initial net radiative loss.

## Optical interpretation

Ni is used only because a defensible MAR-M247 1064-nm complex index has not
been identified. For n=2.611 and k=5.842 the flat, normal-incidence single-hit
absorptivity is about 0.221. Ray tracing and multiple reflection determine the
actual deposited power.

## Acceptance questions

The run is useful if it answers:
1. does it complete without Fatal/NaN/Inf?
2. is the keyhole comfortably above y=0?
3. is the interface comfortably below the top boundary?
4. are Tmax, Umax, interfacePVapMax, recoil and energy terms finite?
5. what wall-time/us is measured on 48 ranks?
6. does the result justify the planned full-domain depth/headroom?

Run:

    ./Preflight
    ./Allrun
    ./Status
    ./PostprocessTrack
