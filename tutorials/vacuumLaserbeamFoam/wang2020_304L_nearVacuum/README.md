# Wang 2020 — 304L near-vacuum stationary-laser validation

This case targets the near-vacuum 304L validation in Wang, Zhang & Yan,
Physical Review Applied 14, 064039 (2020).

## Paper-direct inputs

- 304L: Cr/Ni/Fe = 18/8/74 wt%
- ambient pressure: 0.0002 atm = 20.265 Pa
- ambient temperature: 298 K
- laser power: 260 W
- laser spot size: 100 um
- wavelength: 1070 nm
- solidus/liquidus: 1697/1727 K
- density: 7200 kg/m3
- melting latent heat: 2.74e5 J/kg
- evaporation latent heat: 6.36e6 J/kg
- Pe = 20.16 Pa at 2009 K
- cp(Ts/Tl) = 712/837 J/(kg K)
- k(Ts/Tl) = 19.2/22 W/(m K)
- sigma0 = 1.76 N/m
- d(sigma)/dT = -4.3e-4 N/(m K)

The paper uses Gaussian concentration coefficient N=4.6 and defines Rb as the
radius containing 99% of beam energy. LaserbeamFoam uses the same exponential
form with Radius_Flavour=N/2, so this case sets Radius_Flavour=2.3 and
laserRadius=50e-6 m for the reported 100 um spot size.

## Meshes

Default system/blockMeshDict: 8 um smoke mesh, 40^3 = 64,000 cells.

system/blockMeshDict.reference4um: 4 um reference mesh, 80^3 = 512,000 cells.

The plate surface is y=200 um. The domain contains 200 um of substrate and
120 um of numerical gas, with 320 um lateral extent in x and z.

## Run

Smoke:
```bash
./Allrun.smoke
```

Reference, 48 MPI ranks:
```bash
./Allrun.reference
```

## Deliberately visible model differences

This is a validation candidate, not a parameter-identical reproduction.

1. The outer phase remains LaserbeamFoam's incompressible numerical pseudo-gas;
   chamber pressure enters the evaporation model explicitly.
2. LaserbeamFoam currently uses its inherited Drude/resistivity optical closure.
   Wang et al. used Fresnel absorption with iron's complex refractive index for
   304L.
3. Surface radiation/convection from Wang Eq. (32) are not yet merged into this
   fast-track case. Evaporation cooling is active.
4. No explicit VOF mass sink from evaporation is added.
5. Cr/Ni/Fe vapor-pressure curves use NIST/Chase thermochemical references.
   A common pressure scale anchors the alloy mixture to Wang Table II:
   Pe(2009 K)=20.16 Pa.

## Keyhole-depth extraction

After a reference run, reconstruct/sample and write the centerline depth curve:

```bash
./extractKeyholeDepth.sh
```

Output:
`keyholeDepth.csv`

The sampling line begins in the numerical gas above the original plate surface
and follows the laser axis downward. The extractor locates the first
`alpha.metal=0.5` crossing connected to the atmosphere, so a buried gas pore
does not automatically become the reported keyhole bottom.

Primary comparison window:
- start depth: approximately 32 um;
- target depth: approximately 136 um;
- experiment: approximately 70 us between the two depths;
- Wang-paper current model: approximately 75 us.

## 8 um local activation/stability checkpoint

The smoke run is intentionally local rather than a GitHub CI workload:

```bash
./Allrun.smoke
```

It uses 48 MPI ranks. The first completed checkpoint ran to 5 us; the next activation checkpoint runs to 10 us. At every 1 us output it prints one
machine-readable line:

```text
VACUUM_DIAGNOSTICS time=... Tmax=... Umax=... pVapMax=... QvMax=... depositedPower=...
```

Those lines are copied to `smokeDiagnostics.log`.

At the end, the latest time is reconstructed for:
`T`, `U`, `alpha.metal`, `pVap`, `Qv`, and `Deposition`.

Convenience commands:

```bash
./Run_background
./Status
./Reconstruct
```

These are case-management helpers only. They do not alter the evaporation
model or import electron-beam physics.

This checkpoint is considered successful when:
- the requested end time is reached without FatalError/NaN/Inf;
- deposited laser power is finite and non-zero;
- Tmax rises above the initial 298 K;
- pVap and Qv remain finite;
- the final alpha.metal field remains bounded and physically oriented.

The 5 us local run reached Tmax=1980.19 K, still below the 2009.50 K
near-vacuum activation threshold, so pVap and Qv correctly remained zero.
The 10 us extension is intended to cross that threshold and verify stable
recoil/evaporation activation before the 4 um paper run.

It is a short-time physical/numerical gate, not the 4 um paper validation.

