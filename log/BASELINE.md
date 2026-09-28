# Baseline

## Upstream source

- Upstream repository: `laserbeamfoam/LaserbeamFoam`
- Upstream tag: `V3.0`
- Upstream commit: `f42e08a0bfc1749675beadcf7c6a90334d7aa9f8`
- Upstream tree: `a37e12fa6d6828e06bbde60831db2de67dab283a`

## Project baseline

- Repository: `KrisIrving/vacuumLaserbeamFoam`
- Baseline branch: `main`
- Baseline commit before project development:
  `9cfaddf297830129a2ed248e6fd8e9a66a78d8c6`
- The baseline commit has the same Git tree SHA as upstream LaserbeamFoam V3.0.

## Development policy

`main` is treated as the upstream V3.0 reference until a deliberate integration
decision is made. Vacuum-specific development starts on feature/development
branches. The original `laserbeamFoam` solver is retained as a regression
reference.

## Initial experimental target

The target application is LPBF melt-pool/keyhole simulation in a vacuum chamber
with nominal chamber pressure `p_chamber = 0.6 Pa`.

The chamber pressure is not to be conflated with the CFD pressure field
(`p`/`p_rgh`) or the reference pressure used in saturation-pressure
correlations.
