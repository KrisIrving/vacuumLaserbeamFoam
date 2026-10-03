# M247 input provenance and freeze status

Status:
- **FROZEN** — experiment/project supplied or formally accepted;
- **CANDIDATE** — literature-supported, awaiting final implementation;
- **TBD** — must not be silently inherited from older cases.

| Input | Current value/status | Provenance / decision |
|---|---|---|
| Chamber pressure | **0.6 Pa — FROZEN** | project target |
| Laser power | **350 W — FROZEN** | user experiment |
| Scan speed | **1000 mm/s — FROZEN** | user experiment |
| Track length | **~2 mm — FROZEN** | user experiment |
| Beam diameter/radius | **TBD** | do not inherit old 43/50 um radius |
| Wavelength | **TBD** | do not inherit old 1064/1070 nm |
| Initial/preheat temperature | **TBD** | old-repo value not accepted as experiment truth |
| Powder PSD | **provisional D10 36.5 / D50 52.6 / D90 74.4 um** | old repo numerical design; experiment should confirm |
| Powder support | **~30-80 um provisional** | old repo numerical design |
| Powder layer envelope | **80-100 um provisional** | numerical starting point |
| Single-layer packing | **~0.45 target, 0.44-0.56 literature band — CANDIDATE** | Wischeropp et al., Additive Manufacturing 28 (2019), DOI 10.1016/j.addma.2019.04.019 |
| Exact chemistry | **TBD; powder certificate preferred** | literature fallback below |
| Solidus/liquidus | **~1539/1639 K — CANDIDATE** | Torroba et al. 2014, DOI 10.1186/s40192-014-0025-5 |
| Melting latent heat | **CANDIDATE; not frozen** | later DSC work reports ~140-164 kJ/kg |
| rho(T), k(T), cp/enthalpy(T), mu(T) | **CANDIDATE** | MAR-M247 literature; fit independently |
| Surface tension / dSigma-dT | **TBD / sensitivity** | needs defensible M247/Ni-superalloy source |
| Emissivity | **TBD / sensitivity** | no old-case inheritance |
| Optical n,k / reflectivity | **TBD; Ni surrogate only if needed** | direct M247 preferred |
| Alloy vapor-pressure anchor | **none** | do not invent an M247 anchor |
| Preferential depletion | **not implemented** | fixed-bulk-composition morphology model |

## Literature chemistry fallback

If the actual powder certificate is unavailable, one recent measured MAR-M247
powder composition reports wt.%:
- Cr 8.09;
- Co 9.31;
- W 9.40;
- Ta 3.21;
- Al 5.49;
- Hf 1.50;
- Ti 0.69;
- Mo 0.51;
- Ni balance.

Source: Shi et al., Advanced Engineering Materials (2025),
DOI 10.1002/adem.202501177.

This is a fallback/reference composition, not a claim about the user's powder.

## Evaporation-component screening

Recommended pure-element vapor-pressure source:
Mondal et al., Materials 16 (2023) 50,
DOI 10.3390/ma16010050.

Using the literature fallback chemistry above with the recommended pure-element
relations gives a screening-level, unanchored trend:
- 1600-1800 K: Al dominates mixture vapor pressure;
- Ni grows strongly with temperature and becomes dominant at high LPBF T;
- Cr is the next important contributor;
- Co is smaller but non-negligible;
- Ti is minor;
- W, Ta, Mo and Hf are negligible for total pressure over the principal first-
  pass LPBF temperature interval.

Illustrative pressure fractions:
- 1650 K: Al ~92%, Ni ~4%, Cr ~4%, Co <1%;
- 2000 K: Al ~80%, Ni ~10%, Cr ~8%, Co ~1.5%;
- 2500 K: Al ~55%, Ni ~31%, Cr ~11%, Co ~3%;
- 3000 K: Al ~32%, Ni ~54%, Cr ~10.5%, Co ~3.5%.

The same unanchored screening predicts total mixture pSat of order:
- ~0.6 Pa near 1580 K;
- ~20 Pa near 1850 K;
- ~1 atm near 2970 K.

These are **not a validated M247 alloy-vapor-pressure calibration**. They are
used to choose active components and design regression tests.

At 0.6 Pa, the predicted mixture boiling pressure can be reached near/below the
candidate M247 liquidus, so Wang evaporation activation is expected to be
limited by the liquid-state activation temperature rather than an atmospheric
boiling point.

## Optical fallback

Do not reuse the Fe optical constants from the 304L Wang benchmark.

Priority:
1. measured M247 optical response at the actual wavelength;
2. published M247/Ni-superalloy data;
3. Johnson-Christy Ni complex index as documented surrogate;
4. sensitivity bounds.

Ni source: P. B. Johnson and R. W. Christy, Phys. Rev. B 9, 5056 (1974),
DOI 10.1103/PhysRevB.9.5056.

## Vapor-model implementation decision

Wang gas-dynamic/Knudsen equations remain frozen.

For M247, pure-component pSat(T) is material data. The current code uses one
Clausius-Clapeyron latent heat per component; better wide-range correlations
are available. The material-input layer may therefore be extended to accept
literature pSat(T) correlation coefficients.

Any extension must:
- preserve the existing 304L path;
- have a standalone analytical regression;
- avoid empirical recoil multipliers;
- avoid fabricated alloy-level pressure anchors.

Evaporation heat loss currently uses one alloy-level Lv. This remains an
explicit first-pass approximation because vapor composition changes strongly
with temperature. Preferential depletion/composition transport remain outside
the first morphology/keyhole study.
