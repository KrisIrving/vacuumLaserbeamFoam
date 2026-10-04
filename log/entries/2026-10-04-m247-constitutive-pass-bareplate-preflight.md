# 2026-10-04 — M247 constitutive PASS and bare-plate preflight design

## M247 Mondal/Wang constitutive gate — PASS

Measured local test result:

- chamber pressure = 0.6 Pa;
- initial metal preheat reference = 1343.15 K;
- mixture boiling temperature = approximately 1580.31 K;
- provisional liquidus = 1631 K;
- activation temperature = 1631 K because liquidus exceeds the 0.6-Pa
  mixture-boiling temperature.

Wang far-field chamber-temperature sensitivity:

- 298 K: Tk0 approximately 1599.18 K, Tk1 approximately 1893.15 K;
- 1343.15 K: Tk0 approximately 1592.58 K, Tk1 approximately 1797.36 K.

The mixture saturation pressure is independent of the Wang far-field gas
temperature; only the common-atmosphere transition changes.

The M247 first-pass component vapor-pressure path now uses the optional
Mondal et al. (2023) wide-range pure-element correlations. The original
Clausius-Clapeyron path remains available and the frozen 304L configuration is
not changed.

## Radiation-temperature architecture

The grey radiation model now accepts:

    radiation
    {
        environmentTemperature ...;
    }

If this entry is omitted, the previous chamberTemperature behavior is retained.
This preserves existing cases while allowing the M247 experimental global
preheat/radiative environment to be separated from the Wang far-field
residual-gas temperature.

## Bare-plate preflight

Case:

    tutorials/vacuumLaserbeamFoam/M247_0p6Pa_barePlatePreflight8um

Frozen process input:
- M247 substrate;
- 0.6 Pa;
- 1343.15 K global initial preheat;
- 350 W;
- 1.0 m/s;
- 86 um spot diameter;
- 1064 nm.

Preflight geometry:
- 400 x 640 x 320 um;
- original surface y=400 um;
- 400 um substrate depth;
- 240 um gas headroom;
- uniform 8 um;
- 160,000 cells;
- 48 ranks;
- 100 um path / 100 us.

The case is not a final material validation. It is a domain/runtime/physics
sanity gate before a short powder run and the eventual approximately 2-mm
production track.
