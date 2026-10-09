## 2026-10-09: native thermal transport PASS; integrated conduction/phase cycle

Reviewed M247_regional-thermal-transport-20261009-092319_review.tar.gz:
manifest size/SHA256 and native serial/MPI logs verified. eba5bc42 build/run
complete, 20 steps, unchanged inputs, max cumulative energy residual3.7364e-15J;
serial/MPI final energy difference5.9566e-12J. Runtime1.1133s excludes build.
This establishes passive thermodynamic transport, not LPBF acceleration.

Added optional implicit conduction and equilibrium latent closure in the existing
local thermal time loop. cp/latent capacities remain conservative transported
moments. Backward-Euler conduction solves a tangent linearization of total
enthalpy; both energy residual and nonlinear temperature/conductivity change
must converge, maximum60 correctors. Recover sensible/latent/reserve from the
conserved energy after solving, without resetting energy from temperature.
Processor conductivity patches exchange neighbouring values; physical patches
use zeroGradient in this fixture. Conductive face flux feeds the cumulative
energy ledger. Invalid fields, controls, nonconvergence fail explicitly.

One --physics command integrates20 flow/VOF/thermal steps: initial1500K solid,
10 heating +10 cooling, source3e13W/m3 scaled by cp capacity/6280500.
Checks conduction actually redistributes energy, capacity-weighted melt fraction
reaches>.5 then falls>.25, phase bounds, nonlinear convergence, cumulative energy,
existing VOF/mass/pressure gates, serial/MPI and unchanged inputs. Gas extrema
alone cannot pass melting. No parameter sweep or production case used.

Local validation:189 Python tests and Bash syntax PASS. C++ native compilation
and numerical execution are pending Ubuntu. This common Ts/Tl capacity closure
is experimental; it is not established equivalent to the legacy filtered alpha
and gas phase thresholds or TEqn. Thermal feedback into momentum, true ray
sources, evaporation/radiation/recoil/Marangoni, moving geometry and repeated
global thermal exchange remain pending. No production approval or speedup claim.

Ubuntu (one archive on success/failure; build300s + runtime600s budgets):
  git pull --ff-only origin feat/m247-material-port
  ./tests/m247Performance/RunRegionalAcceptance --physics
Send M247_regional-thermophysics-<timestamp>_review.tar.gz.
Next development integrates physical sources/phase-flow feedback and moving
history into this loop before a realistic4um wall-cost/physics comparison.

