# 2026-10-04 — M247 bare-plate 8 um preflight result

Case:
tutorials/vacuumLaserbeamFoam/M247_0p6Pa_barePlatePreflight8um

Status: COMPLETE / PASS as a short transfer gate.

Configuration:
- M247 substrate;
- 0.6 Pa;
- 1343.15 K global preheat;
- 350 W;
- 1 m/s;
- 86 um spot diameter;
- 1064 nm;
- 100 um path / 100 us;
- uniform 8 um mesh;
- 160,000 cells;
- 48 MPI ranks.

Runtime:
- 100 us completed in 16179.2 s = 4.49 h;
- approximately 5016 time steps;
- final deltaT approximately 2.11e-8 s;
- Courant control remained stable.

Moving-keyhole metric:
- 5 us: 13.74 um;
- 50 us: 105.26 um;
- 75 us: 155.46 um;
- 100 us: 199.86 um;
- post-50-us mean depth: 153.19 um;
- final bottom lag: -26 um behind the laser;
- atmosphere-connected main interface remained one connected component at all
  sampled times.

Depth growth remained strong at 100 us; a linear fit over 50-100 us gives
approximately 1.92 um/us. Therefore 100 us is not a quasi-steady-depth result.

Final diagnostics at 100 us:
- Tmax = 3991.97 K;
- Umax = 30.00 m/s;
- interfacePVapMax = 1.82175 MPa;
- depositedPower = 279.65 W;
- evaporationPower = 6.10 W;
- radiationPower = 0.0488 W;
- interfaceArea = 1.8919e-7 m2;
- recoilForceX = +0.4836 mN;
- recoilForceY = -0.6425 mN.

Post-50-us mean deposited power was approximately 272.0 W, around 77.7% of
350-W incident power for the present Ni optical surrogate and evolving keyhole.
This is a model result, not a frozen M247 absorptivity.

Domain decision:
- the 400-um substrate depth used in this short preflight retained about
  200 um clearance at 100 us;
- because keyhole depth was still increasing strongly, final/long-track M247
  cases should retain at least the planned approximately 600-um substrate
  depth below the original surface, subject to the powder short-track result;
- the 240-um upper headroom caused no failure in this connected-interface
  bare-plate test, but powder/spatter headroom must be checked separately.

Cost decision:
the 4.49 h / 100 us result confirms that the final 2-ms, approximately
million-cell production case will be expensive. A short powder-track benchmark
must be used to project production cost before launch; no full 2-mm run should
be started directly from this preflight.

Post-processing requirement:
all future M247 post-processing should reconstruct both alpha.metal and T so
temperature evolution is available in ParaView.
