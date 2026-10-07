# Localization diagnosis: gas extrema and a discontinuous phase-temperature rule

Reviewed validation-20261007-161510_localization-20261007-164811.tar.gz. Manifest file SHA256 values match archive bytes. This is analysis of existing results; no new CFD or solver change.

| Region (classified from both states) | Cells | Max T difference / RMS (K) | Max U difference / RMS (m/s) | Max epsilon difference |
|---|---:|---:|---:|---:|
| gasBoth, alpha<=0.01 in both | 255814 | 316.081 / 0.944276 | 10.5905 / 0.0362056 | 0 |
| interfaceOrChanged | 16125 | 39.2151 / 0.667449 | 2.21029 / 0.0261725 | 1 |
| metalBoth, alpha>=0.99 in both | 484061 | 3.48884 / 0.0122611 | 0.0354517 / 0.000168745 | 0.00552520 |

The two >100-K temperature differences and sole >10-m/s velocity difference are in gasBoth. Gas extrema cannot be dismissed automatically: the pseudo-gas participates in the coupled interface/thermal problem. Interface contains 15 cells with T difference >10 K and 2 cells with U difference >1 m/s. MetalBoth has 11 cells with T difference >1 K, no U differences >0.1 m/s, but 7 pressure differences >10 kPa; max metal pressure difference is 21.069 kPa. Pressure accuracy and interface influence remain to assess. Low gas RMS and small pure-metal errors do not constitute a full physical acceptance gate.

All seven epsilon differences >0.99 coincide with alpha crossing 0.05; seven total alpha=0.05 crossing cells are reported. Source updateProps first mixes gas/metal phase temperatures, then overrides both with full metal values only for alpha>0.05. Thus the gas-side limit near 0.05 is roughly TS=77.8 K/TL=91.05 K, while the metal-side limit is 1537/1631 K. This creates a discontinuous equilibrium mapping irrespective of the thermal iteration tolerance.

Concrete example: rank 41/local 15314 has alpha 0.04995474134 (tight) versus 0.05001547892 (standard), T 1356.928364 versus 1370.667164 K, and epsilon 1 versus 0. Both temperatures are below the physical metal solidus. The code nevertheless gives epsilon=1 below the alpha threshold because it uses pseudo-gas-dominated phase temperatures. Another crossing is only about 1.17e-6 in alpha (rank 39/local 1239) and still flips epsilon 0/1. These records demonstrate the abrupt phase-rule artifact, not actual full melting of the metallic material in one solution and solidification in the other.

It would be wrong to smooth only the convergence residual or exclude these cells to declare success. The variable epsilon is coupled to latent heat, radiation, surface forces and flow suppression/masks; the next development must examine those meanings together. A continuous regularization of the override, if trialled, changes the interface closure and needs an opt-in switch, matching gas/full-metal limits, enthalpy consistency and transition-width sensitivity. It must not silently replace the constitutive law or be claimed validated merely because the seven endpoint flips disappear.

Decision: the enthalpy-slope iteration fix passed nonlinear convergence and is promising for runtime. Ordinary versus tight field acceptance remains unresolved at the interface. Do not schedule full-track/fine-grid production yet. Next code work should design a consistent continuous interface phase treatment and short regression checks, then compare longer histories, alpha/T/U fields, keyhole topology and energy accounting. Tight tolerances cost about 11% more than ordinary in the 2-us pair and can serve as a provisional development reference, not proof of physical accuracy. New runtime bottleneck is laser tracing (~60–64%); further laser acceleration should retain the same optical calculation.

All required localization data for this diagnosis have been received. No additional rerun is needed simply to reproduce the localization.
