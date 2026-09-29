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
`Ma = 1`, from the paper's Eqs. (9)-(13).

For the dimensionless velocity:
`m = sqrt(gamma/2) * Ma`.

The Knudsen-layer jump functions define the temperature and pressure ratios
between the liquid surface and the gas side of the Knudsen layer. For
`gamma = 5/3` and `Ma = 1`, the implementation obtains approximately:

- `T3/Te = 0.8386534551`;
- `P3/Pe = 0.2148343054`;
- net mass-flux coefficient relative to the maximum Hertz flux:
  `0.8289634846`;
- absolute recoil-pressure coefficient:
  `Precoil/Pe = 0.5728914811`.

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
