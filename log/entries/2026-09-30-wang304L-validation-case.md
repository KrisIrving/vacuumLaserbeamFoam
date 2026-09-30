# 2026-09-30 — Wang 304L near-vacuum validation case

## Purpose

Build the first physical benchmark after the OpenFOAM-v2512 constitutive and
coupling checkpoint.

## Production-model changes

1. Added an optional alloy saturation-pressure anchor. This preserves
   temperature-dependent component fractions while forcing the mixture Pe(T)
   through Wang Table-II Pe(2009 K)=20.16 Pa.
2. Completed the low-Mach Wang near-vacuum step-(4) branch for cases whose
   boiling activation begins below Tk0.
3. Added optional clamped-linear cp/k evaluation from paper-tabulated
   solidus/liquidus values. Existing cases remain on the original polynomial
   path unless the switch is enabled.
4. Added `tests/wang304LReference` for the Table-I/II composition and
   near-vacuum constitutive states.

## CFD case

Added:
`tutorials/vacuumLaserbeamFoam/wang2020_304L_nearVacuum`

Fast smoke mesh:
8 um, 64k cells.

Paper-resolution reference mesh:
4 um, 512k cells.

Domain:
- x,z = +/-160 um;
- y = 0...320 um;
- initial substrate surface at y=200 um.

Laser:
- stationary;
- 260 W;
- 100 um spot -> Rb=50 um;
- 1070 nm;
- Gaussian Radius_Flavour=2.3, corresponding to Wang N=4.6;
- incident along -y.

## Quantitative validation targets

Primary:
- keyhole depth 32 -> 136 um;
- experiment: about 70 us;
- Wang-paper simulation: about 75 us;
- Anisimov-paper simulation: about 100 us.

Secondary:
- peak recoil pressure approximately 5 atm near the keyhole bottom;
- overflow height: experiment about 18 um, paper current model about 14 um;
- paper current-model z-direction recoil force about 4e-3 N.

## Automated depth extraction

The case contains a centerline sampling dictionary and
`extractKeyholeDepth.sh`. It samples alpha.metal from the numerical gas
through the plate and identifies the first alpha=0.5 crossing connected to the
atmosphere, avoiding buried gas pores when estimating keyhole depth.

## Deliberate fast-track limitations

- no explicit evaporation VOF mass sink;
- no resolved rarefied plume;
- pseudo-gas remains numerical;
- radiation/convection surface losses are not yet active;
- LaserbeamFoam optical closure is not identical to Wang's iron-index Fresnel
  model.

These limitations must remain visible when interpreting the first benchmark.
