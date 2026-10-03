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

## Current open research questions after T12

These are deliberately **not** accepted conclusions yet.

### Moving-track stage change
- Why does the engineering 0.6 Pa track transition from an approximately
  49-um quasi-steady keyhole to an approximately 43-um late stage?
- Current evidence points more toward evolving geometry/optical coupling than
  weakened evaporation/recoil, but causality is not established.
- Compare 8/4 um histories before attributing the change to physical powder-bed
  evolution.

### Production mesh policy
- Can 8 um be used for broad screening while 4 um is reserved for key cases?
- Does the moving keyhole lag converge at the same rate as depth?
- If 8/4 um differs strongly, is an intermediate/finer mesh or local refinement
  more efficient than globally using 4 um?

### Powder stochasticity
- How much of the moving-keyhole/absorption variability is seed-dependent?
- Freeze an experiment-matched PSD first, then use a small deterministic seed
  ensemble rather than changing both PSD and seed simultaneously.

### Numerical pseudo-gas
- Quantify whether pseudo-gas density/viscosity materially changes moving
  keyhole depth, recoil coupling or timestep restrictions at 0.6 Pa.
- Do not interpret pseudo-gas flow as physical rarefied chamber flow.

### Missing mass removal
- The Wang validation succeeded without an explicit evaporation VOF mass sink,
  but long low-pressure tracks may make cumulative mass removal more important.
- Revisit only after mesh/pseudo-gas effects and experiment comparison are
  quantified.
