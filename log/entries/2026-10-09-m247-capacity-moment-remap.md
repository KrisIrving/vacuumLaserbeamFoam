
## 2026-10-09: preserve capacity moments through regional remapping

Native state handoff now conservatively maps sensible capacity endpoints [J/m3/K]
and latent capacity [J/m3] alongside energy, alpha and latent-energy inventory.
The capacities are moments of the source coefficients, NOT regenerated from mapped
alpha. This preserves uniform T across interface mapping and keeps a fully liquid
metal/cold gas crossing admissible. Fixed phase inventory is reconstructed using
mapped capacity. No clipping, arbitrary neighbor redistribution or energy deletion.

Added m247CapacityEnthalpy.H and persistent-moment m247RegionalState overload.
Import coefficients from alpha only once at original checkpoint; repeated regional
moves MUST supply the stored moments. Native mixed audit now reports schema2 and
capacityMomentsMapped=1, uses mapped closure for local inverse/delta checks.
Global energy-only correction still preserves original global inventories.

160 Python tests pass, including fully molten/gas interface, uniform temperature,
two sequential remaps of nonmatching partitions, moment integrals, invalid energy,
and signed energy changes. Native build/MPI remains unverified; no acceleration
claim. These are thermodynamic remap diagnostics, NOT a solved local CFD system.

Remaining: momentum/VOF transport and correction ownership, pressure/open boundary,
energy-source/interface flux accounting, moving persistent field migration,
native fixture and integrated acceptance driver. Moment evolution/advection must
be supplied with the local equations; recomputing cp/rho/L from averaged alpha
would discard these moments and reintroduce the error. Existing TEqn is unchanged;
its advective compatibility with the moment formulation is not established.
No new Ubuntu micro-screen requested.
