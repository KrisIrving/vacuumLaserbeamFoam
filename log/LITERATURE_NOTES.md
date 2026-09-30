# Literature notes

This file records literature-to-code mappings used during model development.
It is not a general bibliography; each entry should explain exactly which
equations or assumptions influenced the implementation.

## Wang, Zhang & Yan (2020) — evaporation / Knudsen-layer model

Reference:

Lu Wang, Yanming Zhang, Wentao Yan,
"Evaporation Model for Keyhole Dynamics During Additive Manufacturing of Metal",
Physical Review Applied 14, 064039 (2020).
DOI: 10.1103/PhysRevApplied.14.064039

### Code mapping

Phase-4a model:
`src/vacuumEvaporationModels/knudsenLayerSonic/`

The implementation uses the single-component sonic Knudsen-layer limit,
`Ma = 1`, from the paper's Eqs. (9)-(13). For monatomic metal vapour the model
fixes `gamma = 5/3`, matching the assumption used in the paper rather than
exposing gamma as a calibration parameter.

For the dimensionless velocity:
`m = sqrt(gamma/2) * Ma`.

The Knudsen-layer jump functions define the temperature and pressure ratios
between the liquid surface and the gas side of the Knudsen layer. For
`gamma = 5/3` and `Ma = 1`, the implementation obtains approximately:

- `T3/Te = 0.6691164507`;
- `P3/Pe = 0.2061848244`;
- net mass-flux coefficient relative to the maximum Hertz flux:
  `0.8156806362`;
- absolute recoil-pressure coefficient:
  `Precoil/Pe = 0.5498261984`.

### Equation-transcription correction (2026-09-29)

A source-to-code audit before Phase 4c found that the first Phase-4a
implementation had parsed the square-root structure in Eq. (10) incorrectly.
The correct relation is

`sqrt(T3/Te) = sqrt(1 + pi*m^2/64) - sqrt(pi)*m/8`.

The mass-flux coefficient must therefore use `sqrt(T3/Te)`, not
`T3/Te`, in the denominator after normalization by the maximum Hertz flux.
The production model, transition helper, and independent regression constants
were corrected together.

The mass-loss and recoil relations are evaluated from the same Knudsen-layer
state. Saturation pressure is calculated with the Clausius-Clapeyron relation.

### Important scope limitation

This is **not** yet the paper's complete near-vacuum interpolation procedure.
The paper distinguishes the sonic gas-dynamic evaporation limit from weaker
evaporation/conduction regimes and proposes interpolation using Mach-number
thresholds. Phase 4a implements only the analytically testable strong-evaporation
`Ma=1` branch.

The full interpolation/transition logic will be a separate change so that its
assumptions and tests remain traceable.

### Solver pressure convention

The paper's recoil expression is an absolute surface momentum flux. In
vacuumLaserbeamFoam the outer VOF phase is a numerical pseudo-gas and the CFD
pressure is gauge-like. Therefore `knudsenLayerSonic::recoilPressure()`
returns the net applied normal stress:

`max(Precoil_absolute - chamberPressure, 0)`.

This convention is explicitly tested and should be revisited if the solver later
uses an absolute-pressure gas/vapour formulation.

## Wang common-atmosphere state relations — Phase 4b

The paper links the Knudsen-layer state to ambient gas through a shock-wave
model. For monatomic gas, Eqs. (16)-(17) determine the Knudsen-layer Mach number
and shock state.

A useful numerical reduction is applied in the code:

Given surface temperature `Te` and a trial Knudsen-layer Mach number `Ma`,
Eq. (17) can be reduced to a quadratic equation for the region-II shock Mach
number `M2`. Therefore the coupled state does not require a two-dimensional
Newton solve.

With
`C = sqrt(T3/Te) * m * sqrt(2*Te/(gamma*T1))`,

the physical positive root is

`M2 = [C(gamma+1) + sqrt(C^2(gamma+1)^2 + 16)] / 4`.

Eq. (16) then becomes a scalar residual in either `Ma` or `Te`.
The implementation uses a logarithmic pressure-ratio residual and bounded
bisection.

This solver is intended to:
- recover `Ma(Te)` where the common-atmosphere relation is applicable;
- compute `Tk0` at `Ma=0.05`;
- compute `Tk1` at `Ma=1`;
- provide the threshold information required by the paper's near-vacuum
  interpolation procedure.

## Wang near-vacuum production closure — Phase 4c

Model:
`src/vacuumEvaporationModels/nearVacuumWang/`

The implementation follows the paper's staged near-vacuum construction:
- compute the pressure-dependent boiling point from the same
  Clausius-Clapeyron saturation relation;
- compute `Tk0` at `Ma=0.05` and `Tk1` at `Ma=1`;
- below the liquid/boiling activation temperature, liquid evaporation is zero;
- in the active interval below `Tk1`, solve the common-atmosphere transition
  relations for `Ma(T)`;
- at and above `Tk1`, use the sonic `Ma=1` Knudsen-layer state.

The current implementation deliberately refuses configurations whose active
liquid state begins below `Tk0`. Such a case would enter the `Ma<0.05`
weak-evaporation/conduction regime, where the source paper explicitly warns
that the convection-flow assumptions used for the transition relations are not
valid. No undocumented extrapolation is introduced.

## Wang alloy-composition closure — fast-track extension

The paper's Eqs. (18)-(20) are now mapped explicitly into
`nearVacuumWang`:

- `Pe = sum(ki Pi)`;
- `M = sum(Mi ki Pi)/Pe`;
- `R = Rmol/M`.

The paper defines `ki` as molar fraction, while Table I reports alloy
composition by mass fraction. The implementation therefore accepts component
mass fractions and converts them to molar fractions internally using
`ki = (wi/Mi)/sum(wj/Mj)`.

Each pure-component saturation pressure `Pi(T)` is evaluated from its own
Clausius-Clapeyron reference state and latent heat. The resulting mixture
`Pe(T)` is used in the Eq. (16) pressure residual, and the temperature-dependent
mixture molar mass is used in Eq. (11) through `R=Rmol/M`.

Evaporation heat loss remains `mLoss*Lv` as in Eq. (32), using the configured
alloy-level latent heat of evaporation. No composition transport or preferential
depletion of the liquid phase is introduced in this fast-track implementation.

When `componentNames` is absent the previous single-component code path is
retained, so the existing Phase-4c regression remains a backward-compatibility
gate.

## 304L near-vacuum benchmark parameter provenance

Primary source:
Wang, Zhang & Yan, Physical Review Applied 14, 064039 (2020),
DOI 10.1103/PhysRevApplied.14.064039.

### Paper-direct quantities

For the near-vacuum stationary-laser benchmark the paper directly supplies:
- 304L composition Cr/Ni/Fe = 18/8/74 wt% (Table I);
- Ts/Tl = 1697/1727 K;
- rho = 7200 kg/m3;
- Lm = 2.74e5 J/kg;
- Lv = 6.36e6 J/kg;
- alloy Pe = 20.16 Pa at Tb = 2009 K;
- cp(Ts/Tl) = 712/837 J/(kg K);
- k(Ts/Tl) = 19.2/22 W/(m K);
- emissivity = 0.4;
- sigma0 = 1.76 N/m;
- d(sigma)/dT = -4.3e-4 N/(m K);
- chamber = 0.0002 atm and 298 K;
- laser = 260 W, 100 um spot, 1070 nm;
- reference mesh size = 4 um.

The paper's Eq. (29) uses concentration coefficient N=4.6 and beam radius Rb
containing 99% of beam energy. LaserbeamFoam's Gaussian exponent is
`-Radius_Flavour*r^2/Rb^2`, so the equivalent setting is
`Radius_Flavour = N/2 = 2.3`.

### External pure-element thermodynamics

The paper defines Eqs. (18)-(20) using pure-component saturation pressures but
does not tabulate the complete Cr/Ni/Fe Clausius-Clapeyron input set.

The fast-track implementation therefore uses NIST Chemistry WebBook / Chase
(1998) thermochemistry to define pure-element normal-boiling reference states:
- Cr: M=51.9961 g/mol, Tref=2952.078 K;
- Ni: M=58.6934 g/mol, Tref=3156.584 K;
- Fe: M=55.845 g/mol, Tref=3133.345 K.

Latent heats used in the component Clausius-Clapeyron curves are evaluated from
the NIST gas/liquid enthalpy difference at those phase boundaries:
- Cr: 6.528895261154893e6 J/kg;
- Ni: 6.432819434153015e6 J/kg;
- Fe: 6.259774057660581e6 J/kg.

NIST source pages:
- https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440473
- https://webbook.nist.gov/cgi/cbook.cgi?ID=C7440020
- https://webbook.nist.gov/cgi/cbook.cgi?ID=C7439896

### Alloy pressure anchor

Direct Raoult-like Eq. (18) evaluation with the above pure-element references
does not exactly reproduce Wang Table-II `Pe(2009 K)=20.16 Pa`. To avoid
silently replacing the paper's measured/alloy-level reference, an optional
common pressure scale was added.

When `alloyReferencePressure` and `alloyReferenceTemperature` are provided,
all component partial pressures are multiplied by one common factor so that the
total mixture pressure passes through the supplied alloy reference point. The
same factor is applied to every component, so the relative vapor composition
and Eq. (19) mixture molar mass are unchanged.

For the current 304L NIST curves the raw Eq. (18) pressure at 2009 K is
approximately 72.113676 Pa and the scale factor is approximately
0.279558622, giving exactly 20.16 Pa at 2009 K.

### Wang near-vacuum step (4)

For the anchored 304L case at 20.265 Pa / 298 K:
- boiling activation is about 2009.5 K;
- Tk0 (Ma=0.05) is about 2039.7 K;
- Tk1 (Ma=1) is about 2530.6 K.

Thus the active evaporation range begins below Tk0. The original conservative
implementation rejected this configuration. The production model now follows
the paper's near-vacuum step (4) by solving the same common-atmosphere residual
with a low-Mach bracket approaching zero between boiling and Tk0, then
continuing through the existing Ma=0.05-to-1 transition and sonic branch.

A dedicated 304L regression checks the Table-II anchor, a low-Mach state at
2020 K, an intermediate state at 2300 K, and the sonic state at 3000 K.

### Thermal-property representation

Table II supplies cp and k only at Ts and Tl. A new optional
`useClampedLinearThermalProperties` path linearly interpolates between the
tabulated solidus/liquidus values, holds the solidus value below Ts, and holds
the liquidus value above Tl. The default remains disabled, preserving every
existing LaserbeamFoam regression.

### Known optical mismatch

Wang et al. calculate reflection/absorption with Fresnel equations and use
iron's complex refractive index for 304L due to lack of reliable alloy data.
LaserbeamFoam V3 instead uses its inherited Drude/electrical-resistivity optical
closure. The first 304L CFD smoke/reference case deliberately records this as a
model-form difference rather than tuning resistivity to force agreement.
