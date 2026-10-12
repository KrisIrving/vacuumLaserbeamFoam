# M247 parameter provenance audit (2026-10-12)

Scope: the `M247_0p6Pa_track1500um6umV2` pilot. This is a source audit, not a
claim that the parameters describe one published experimental track. The case
remains blocked before CFD until a native LIGGGHTS bed is reviewed. Do not
change material values opportunistically during the DEM handoff; preserve
matched comparisons, then run named sensitivities for uncertain parameters.

| Input in current case | Evidence checked | Status and action |
|---|---|---|
| Solidus 1537 K; liquidus 1631 K; fusion heat 150 kJ/kg | Rakoczy et al. measured 1263–1264 °C, 1356–1359 °C and 140–164 J/g in directionally solidified MAR-M247 castings [1]. | Within reported ranges. Provisional transfer from a different heat and fabrication state; compare to actual powder DSC when available. |
| Metal density 7950 kg/m3 throughout; `nu` 1.069e-6 m2/s | Current `transportProperties` comments identify 7950 as solid and about 7430 kg/m3 as liquid, with 8.5 mPa s viscosity, but the underlying primary measurement for the latter two has not been verified. | Major model uncertainty: constant solid density in molten flow. Keep the baseline, then compare a liquid-density sensitivity with viscosity recomputed consistently; do not label 7430/8.5 as independently validated here. |
| `cpSolidus/Liquidus` 790/860 J/(kg K), `kappaSolidus/Liquidus` 29/35 W/(m K) | The case explicitly identifies heat capacity as a CM247LC surrogate and conductivity as a literature range. No same-heat MAR-M247 primary measurement at these temperatures was identified in this audit. | Provisional. Prioritize sensitivity because thermal solution dominates runtime and pool geometry. |
| Surface tension 1.70 N/m; temperature slope -2.5e-4 N/(m K); emissivity 0.30 | Current files call these provisional; no same-heat, near-melt primary measurements were confirmed. | Provisional sensitivity values, not validation anchors. |
| Ni optical constants n=2.611, k=5.842 at 1064 nm | Case documents these as a pure-Ni surrogate, not MAR-M247 optical data. | Absorptivity is uncertain; preserve the ray-count comparison but do not infer alloy optical accuracy from it. |
| Nine-component composition Ni 61.80, Cr 8.09, Co 9.31, W 9.40, Ta 3.21, Al 5.49, Hf 1.50, Ti 0.69, Mo 0.51 wt.% | `M247_INPUT_FREEZE.md` labels this a temporary literature fallback. Jin et al. report ICP-OES chemistry of *their own* EPBF powder [2], not of this case's powder. | Requires actual powder certificate. C/B/Zr are absent from the evaporation mixture and pure-element vapor-pressure fits do not establish alloy activity/depletion accuracy. |
| 0.6 Pa, 1070 °C initial metal, 350 W, 1 m/s, 86 µm spot, 50 µm nominal layer, PSD D10/50/90 = 36.5/52.6/74.4 µm | These appear in `M247_INPUT_FREEZE.md` as experiment inputs, but no linked primary paper or powder certificate documents this combined condition. Searches for the combined distinctive values found no match. Published MAR-M247 conditions differ: Jin et al. used EPBF at 1000 °C with 14–125 µm powder [2]; Shi et al. used SLM at 200 W, 900 mm/s and 30 µm layers [3]. | Treat as project target inputs, **not** externally verified experimental data. Do not substitute parameters from unrelated papers. Obtain original run sheet and powder PSD/certificate before claiming experimental validation. |
| DEM contact: 5 MPa reduced Young's modulus, 0.45 Poisson ratio, 0.1 restitution, 0.065 friction; 500 particles, gravity rain with walls | Current generator adapts the upstream LaserbeamFoam LIGGGHTS rain-deposition approach. These contact coefficients are numerical/provisional, not calibrated M247 measurements. No recoater/blade is simulated. | DEM accounts for contacts/collisions *during bed generation*. It does not provide ongoing CFD–DEM collision coupling during laser melting. Check final PSD, particle count, packing, coverage, overlaps, residual motion, topography and size segregation; calibrate against measured spread bed if available. |

## Decision gates

1. Get the corrected native DEM archive. An archive containing only
   `reviewManifest.json` is a failed executable preflight, not a powder result.
2. Review `log.liggghts`, `run.json`, both dumps, `powderManifest.json` and
   particle CSV; report every gate and compare spatial/height distributions.
   A gate pass is only computational consistency, not physical calibration.
3. Install the audited bed and perform the 50 µs pilot; inspect melt-pool
   geometry, conservation, boundary margins and runtime before 1.5 mm.
4. Keep source status explicit: [1] supports melting ranges; no identified
   source supports the complete process parameter set. Upgrade to experimental
   validation only with the actual target paper/run sheet and powder data.

## Primary sources

1. Rakoczy et al., *Microstructure and selected properties of the solution
   heat-treated MAR-M247 Ni-based superalloy fabricated via directional
   solidification*, 2024, DOI [10.1007/s00170-023-12785-0](https://doi.org/10.1007/s00170-023-12785-0).
2. Jin et al., *Microstructure and mechanical properties of nickel-based
   superalloy MAR-M247 fabricated via electron beam powder bed fusion*, 2025,
   DOI [10.1016/j.matchar.2025.114938](https://doi.org/10.1016/j.matchar.2025.114938).
3. Shi et al., *Relationship between Anisotropic Stress Rupture Properties at
   High Temperature and Microstructure of Selective Laser Melting Mar-M247
   Alloy*, 2025, DOI [10.1002/adem.202501177](https://doi.org/10.1002/adem.202501177).

