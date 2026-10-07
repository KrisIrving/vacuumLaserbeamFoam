# Short thermal convergence investigation

The uploaded Ubuntu logs establish that each variant took 166 steps and 25,066 thermal correctors. Every logged maximum epsilon increment was exactly 1. Final temperature linear residuals were at most 4.431423425e-10, with 24,734 one-iteration and 332 two-iteration solves. Both variants' complete epsilon residual histories match at logged precision. The final volume-mean epsilon increments range from 7.96035792e-6 to 1.447513268e-5. These are nonlinear phase-update failures, not expensive linear temperature iterations.

The location and cell identity of those unit increments are not in the original logs. They can indicate different cells flipping at successive iterations; do not assume one particular cell has a two-cycle yet.

## Candidate and its limits

Let f be epsilon1, cp heat capacity, L mixture latent heat, D=TLiquidus-TSolidus, and r=epsilonRelaxation. The legacy update adds r*cp/L*(T-TSolidus-D*f), then clamps to [0,1]. The candidate adds r*cp/(L+cp*D)*(T-TSolidus-D*f), with the same clamp. This accounts for the sensible as well as latent enthalpy slope and keeps the same interior phase-relation fixed point.

For an ideal isolated implicit enthalpy cell, dT/df=-L/cp. The legacy iteration's local amplification is 1-r*(1+cp*D/L); the candidate gives 1-r. This scalar model motivates the correction; it is not a proof of contraction for the complete advective, diffusive, evaporating CFD system.

At alphaMetal > 0.05, updateProps uses the full metal 94-K melting span while L is mixed with alpha_filtered. A representative alpha=0.06 cell with cp about 536–540 J/(kg K) and L about 9001 J/kg has cp*D/L about 5.6, implying legacy local amplification about -2.3 for r=0.5 in the isolated model. This makes interface over-correction plausible, but the worst cells must be located in the new diagnostic before claiming the actual cause. These representative values are not measured worst-cell values.

The candidate does not change the energy equation, tolerances, existing corrector cap, phase temperatures, material data, ray count or Courant control. Its trajectory and final physical fields can change: the legacy run was not converged. Defaults retain the legacy algorithm. This is an experimental numerical change, not an approved production speedup.

Because a smaller correction could otherwise give a misleading small increment, the candidate also requires a phase-temperature consistency residual <= 0.01 K: |T-(TS+D*f)| in mixed-phase cells; max(T-TS,0) at f=0; max(TL-T,0) at f=1. Both this condition and the original maximum epsilon-increment tolerance must hold. Cap hits include failure of either test. This phase relation check is not a complete energy-conservation test.

## Ubuntu command

With OpenFOAM v2512 sourced, from the repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./Allwmake -j 48
./tests/m247Performance/RunThermalProbe
```

The probe makes independent copies of the original 180-us state. Both variants disable ray history; thermalLegacy retains the legacy correction, enthalpyBounded enables only the candidate correction. Both enable final-iteration residual location diagnostics. No source cleanup or changes are made. The two runs cover 180–180.2 us, with writes at 180.1 and 180.2 us. Default per-job wall budget is 15 minutes. At the earlier measured rate, the legacy 0.2-us run is roughly 2–3 minutes plus setup/output; no candidate runtime is promised.

The same prepared-case protection, source hashing and laser-table checks apply. All other run controls are held equal. `RunPair` remains the ray-only pair and explicitly disables the experimental correction, even if the source dictionary enabled it.

Return both log.vacuumLaserbeamFoam files and both probe.json/run.json files in the printed runs/thermal-<timestamp> directory. New THERMAL_RESIDUAL_DIAGNOSTICS records report final residuals by alpha bin, number of cells above tolerance, and a deterministic worst cell's rank/local index, position, alpha, current/previous T and epsilon, cp, L and phase temperatures. Gas/interface/metal bins only diagnose the residual; no cells are removed from the stopping criterion. phaseTemperatureChecked=0 means the legacy record's phase-temperature metric was not evaluated.

This short investigation intentionally does not invoke the existing comparison collector or claim production PASS. Strict matching to an unconverged legacy result cannot establish the correctness of the new algorithm. First inspect residual location and convergence; then validate longer windows, alpha/T/U fields, keyhole topology and energy accounting against a converged reference before accepting the candidate.

Local verification: 16 Python harness/model tests, Bash syntax and diff checks; actual OpenFOAM compilation/MPI execution pending on Ubuntu. The isolated enthalpy-cell model test is not a solver regression test.
