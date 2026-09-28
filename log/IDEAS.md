# Ideas and open questions

These are hypotheses or possible extensions, not accepted implementation decisions.

## Vacuum thermodynamics

- Evaluate whether the final near-vacuum closure should use a Knudsen-layer
  solution/table, an analytical approximation, or a hybrid model.
- Determine how strongly the 0.6 Pa far-field pressure influences back pressure
  once the local metal vapour pressure becomes much larger than chamber pressure.
- Store model outputs (`pSat`, `mDot`, `pRecoil`, `qEvap`) as optional
  write fields to simplify paper figures and debugging.

## Ti-6Al-4V

- Begin with an effective single-component alloy model for melt-pool validation.
- Add preferential Al evaporation only if composition measurements or model
  discrepancies justify it.
- Collect temperature-dependent `rho`, `cp`, `k`, `mu`, `sigma`,
  `dSigma/dT`, emissivity, fusion latent heat, and vaporisation data with
  uncertainty/source notes.

## Numerical void phase

- Sweep pseudo-gas density and viscosity over several orders of magnitude.
- Monitor pressure oscillation, parasitic currents, interface curvature, melt-pool
  dimensions, and time-step restrictions.
- Consider whether a modified density-damper treatment is preferable to extreme
  pseudo-gas property ratios.

## Validation observables

- Bare-plate single-track experiments are preferred before powder-bed tuning.
- Useful outputs: width/depth/length, track cross-section, depression/keyhole
  depth, cooling rate, peak temperature (if measurable), and mass loss.
- For powder bed, keep denudation/plume-driven powder motion outside the first
  solver-validation target unless experimental data requires it.
