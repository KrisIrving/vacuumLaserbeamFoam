# 2026-10-05 — M247 widened-domain powder preflight result

Case:

    tutorials/vacuumLaserbeamFoam/M247_0p6Pa_powderPreflight8um

Result bundle commit:

    26bc68d0feca462f8a925cb86af760b93dcbd730

Configuration:
- M247 substrate + M247 powder;
- 0.6 Pa;
- 1343.15 K global preheat;
- 350 W;
- 1 m/s;
- 86 um spot;
- 1064 nm;
- 100 um / 100 us scan;
- 8 um central transverse corridor with graded shoulders;
- approximately 360k cells;
- 48 MPI ranks.

Powder geometry:
- seed 247081;
- 58 particles;
- 50-um nominal-layer packing = 0.577640;
- 80-um geometric-envelope solid fraction = 0.361025;
- D10/D50/D90 = 36.739 / 52.661 / 74.026 um;
- active-corridor projected coverage = 0.84132;
- maximum uncovered centerline gap = 7.921 um;
- equivalent dense thickness = 28.882 um.

## Completion and cost

Result: **PASS as a 100-us powder transfer gate**.

- completed to 100 us;
- wall time = 26511.2 s = 7.36 h;
- 5609 time steps;
- final deltaT = 1.68537e-8 s;
- max Courant approximately 0.1590;
- max interface Courant approximately 0.1300.

Compared with the 160k-cell bare-plate preflight:
- wall time ratio = approximately 1.64;
- time-step count ratio = approximately 1.12.

## Moving-keyhole depth

Powder case:
- 5 us: 0.84 um;
- 25 us: 48.68 um;
- 50 us: 112.31 um;
- 75 us: 161.23 um;
- 100 us: **202.53 um**.

Post-50-us:
- mean depth = 157.47 um;
- linear depth-growth trend = approximately 1.85 um/us;
- final bottom lag = -18 um.

The keyhole is still deepening strongly at 100 us. No depth plateau is
established.

Bare-plate comparison, post-50-us:
- bare mean depth = 153.19 um;
- powder mean depth = 157.47 um;
- difference = +4.27 um, approximately +2.8%;
- bare final depth = 199.86 um;
- powder final depth = 202.53 um.

Early in the run (5-25 us), the powder case is shallower on average despite
higher absorbed power, consistent with additional energy being spent heating /
melting the powder geometry before the substrate keyhole catches up.

## Diagnostics: powder versus bare plate

Post-50-us mean values:

- Tmax: 4355 K versus 4330 K (+0.6%);
- Umax: 47.18 versus 43.22 m/s (+9.2%);
- interfacePVapMax: 3.158 versus 3.016 MPa (+4.7%);
- depositedPower: 296.79 versus 272.04 W (+9.1%);
- absorbed fraction: 84.8% versus 77.7% of 350 W;
- evaporationPower: 7.79 versus 7.06 W (+10.4%);
- recoil resultant: 1.103 versus 1.019 mN (+8.3%);
- interfaceArea: 6.70e-7 versus 1.72e-7 m2.

The approximately fourfold interface-area increase is expected because the
powder case contains many additional free surfaces and must not be interpreted
as a fourfold melt-pool area.

At 100 us powder diagnostics:
- Tmax = 4087.7 K;
- Umax = 44.03 m/s;
- interfacePVapMax = 2.1566 MPa;
- depositedPower = 325.05 W;
- evaporationPower = 8.043 W;
- interfaceArea = 6.635e-7 m2;
- recoilForce = (+0.848, -0.869, +0.022) mN.

## Temperature reconstruction

The result bundle confirms successful reconstruction of both:
- T;
- alpha.metal.

No CFD rerun is required for temperature visualization.

## Remaining gate before longer / resolution runs

The widened transverse domain was introduced because the earlier bare-plate
melt pool reached the old z=+/-160-um slip boundaries. The current result bundle
does not include a quantitative liquidus-isosurface transverse clearance
metric.

A dedicated T=1631-K melt-pool-envelope postprocessor is therefore required on
the already reconstructed T field. The next CFD decision should wait for this
cheap post-processing gate.

Because depth is still growing at approximately 1.85 um/us at 100 us, the
current result is not sufficient to freeze a steady keyhole depth or proceed
directly to the 8/4-um M247 resolution pair.
