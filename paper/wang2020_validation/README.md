# Wang 2020 validation paper assets

Status: **Wang 304L matched validation v1 frozen**.

Scope:
this package closes the project-relevant Wang-type near-vacuum evaporation
implementation and the 304L / 0.0002-atm stationary-laser benchmark. It does
not claim independent reproduction of every Ti-6Al-4V/common-atmosphere case
in Wang et al. (2020).

Primary final metrics:
- connected-3D 32-to-136 um growth interval: 76.2318 us;
- Wang current-model reference: about 75 us;
- x-ray reference: about 70 us;
- centreline cross-check: 76.0169 us;
- full surface integral(p dS) at the equivalent recoil-comparison stage:
  about 3.52 mN;
- Wang z-direction recoil force: about 4 mN;
- peak full integral(p dS): 4.7046 mN at 122 us;
- area-weighted p99 recoil near comparison stage: about 6.29 atm;
- single-face recoil maximum remains an OPEN mesh/interpolation sensitivity
  diagnostic.

The original Drude-optics development baseline required 93.8816 us for the
same 32-to-136 um growth interval. After aligning the benchmark optics to an
Fe fixed-complex-index Fresnel closure, the interval reduced to 76.2318 us
without empirical rescaling of the Wang evaporation coefficients.

## Full-history figures

After the completed local cases are present, run:

```bash
python3 paper/wang2020_validation/scripts/plot_full_wang_validation.py
```

Default inputs:
- `tutorials/vacuumLaserbeamFoam/wang2020_304L_nearVacuum/keyholeDepthSurface.csv`
- `tests/run/wang304LMatchedReference/keyholeDepthSurface.csv`
- `tests/run/wang304LMatchedReference/keyholeRecoilSurface.csv`
- `tests/run/wang304LMatchedReference/log.vacuumLaserbeamFoam`

Output:
`paper/wang2020_validation/figures/full/`

The local output directories are intentionally not committed.
