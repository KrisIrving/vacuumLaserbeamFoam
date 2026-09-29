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
