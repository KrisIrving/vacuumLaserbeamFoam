
## 2026-10-09: local pressure/flux projection and source-delta wiring

Added native m247LocalProjection.H: fixed-mesh variable-density pressure correction
with dt/rho face coefficient, boundary-constrained pressure solve, corrected face
flux and reconstructed velocity. Optional localProjectionAudit hooks it into the
regional utility. Physical pressure units required; fixed pressure outlet anchors
MPI solve. Supported uncoupled pairs: fixedValue U/fixedFluxPressure correction,
zeroGradient U/fixedValue correction; processor patches only for coupling.
No arbitrary MPI reference cell, incompatible BC fallback or mesh-motion shortcut.
Global max div and boundary net volume flux must meet explicit tolerance.

Added native local source-delta ledger and sourceAudit hook. Read supplied local
volumetric laser, evaporation, radiation, advection and conduction densities;
subtract mapped global conduction before scattering delta energy. Global source
ownership must be explicitly declared conduction-only. Radiation can heat or cool;
absorption/evaporation must be nonnegative. Component energy ledger reduces over
MPI. These fields are supplied snapshots; actual ray/evap/radiation calls and
pressure-to-VOF/advection coupling have NOT been wired into a timestep yet.

166 Python tests pass. Independent 1D variable-coefficient manufactured pressure
reference checks sign/through-flow; source tests check conduction replacement,
no double count, signed radiation and corrections. Tests do NOT compile or run the
new native projection. Native OpenFOAM build/MPI remains pending. Input NO_WRITE;
no solver time advance or production/performance claim. Default LPBF unchanged.

Next: actual momentum/VOF timestep, optical/source generation, interface flux and
moving history; integrate pressure phi as VOF authority, not reinterpolate U phi.
Projection presently uses externally supplied rho/U, not mapped mixture state.
Source ownership declaration is an audit contract, not proof of existing solver
ownership. Conservative interface flux must still be matched with global thermal
boundaries; this delta ledger alone cannot establish regional physical closure.
No new Ubuntu parameter screen or standalone user-run audit requested.


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


## 2026-10-09: native mixed-state regional handoff

Implemented m247MixtureEnthalpy and m247RegionalState: separate energy density,
metal volume fraction and latent-energy inventory; reconstruct T at fixed phase
inventory. Native regional audit has optional mixtureAudit branch, reads T,
alpha.metal and epsilon1 from thermalRegion, predicts conduction, gathers state,
returns only local delta energy and checks global ledger. Default solver untouched.

Actual material coefficients: rhoMetal7950,rhoGas1,cpGas520,latentGas1;
metal cp790/860,Ts1537,Tl1631,latent150000. Uses solver alpha-weighted cp and
legacy alpha_filtered latent thresholds (<.01,>.99). h reference0K is explicit.
This diagnostic closure does NOT establish advective TEqn equivalence; mapped
states remain nonequilibrium until local phase equations reconcile them.

Error prevented: averaging energy or temperature while recomputing equilibrium
liquid fraction loses phase inventory. Map latent ENERGY density independently;
alpha averaging may reduce its capacity. Such inadmissible states stop with a
specific error, not clipping. Conservative bounded inventory redistribution is
still required before production motion across such interfaces.

155 Python tests pass. Native C++ build/MPI still unverified in this Windows
environment. No local VOF/pressure/laser solve yet; no speedup or production claim.
Next: conservative admissibility handling, local flow/pressure boundary and source
ownership; build one integrated acceptance driver. No new Ubuntu micro-screen.

# M247 structural acceleration checkpoint — 2026-10-08

The user requests ending small parameter screens and accelerating development.
Freeze the dt/cadence/halo sweeps. No new Ubuntu test requested in this checkpoint.

## Latest evidence

210010 native halo pair completed with all pilot screens. Baseline371.384s/40steps;
halo514.530s/48steps; speedup0.72179 (38.54% more wall time).11topology skips did
not compensate for the added refined cells/steps. Do not adopt halo1 or extend it.
Default halo0,interval1,5ns retained. Existing options preserved for reproducibility.
All archives remain evidence; passing screens are not production approval.

## Development objective

Replace whole-domain coupled CFD with global coarse conduction and moving local
VOF/flow/laser physics. Merely adding AMR leaves equations solved everywhere and
cannot supply the needed order-of-magnitude cost reduction. Regional solver is
NOT implemented yet; this change starts its conservative transfer reference.

## Implemented now

regional_transfer.py provides exact axis-aligned box overlap weights, coarse-to-local
volume-average density gathering and local-to-coarse integrated correction scatter.
Sparse weights reuse a spatial bucket index. Source/target overlaps, incomplete
coverage and invalid inputs reject. Corrections conserve integrated quantity and
must be DELTAS from the coarse prediction, not absolute local energy. Global cells
outside the local overlap receive zero correction.147Python tests pass, including
crossing-cell weights, negative corrections, gaps/overlap and finite-data rejection.
This is an offline correctness reference, not an OpenFOAM runtime implementation
or a general polyhedral mapper. No runtime speedup or full thermodynamic validation
is claimed. No existing solver equations/defaults changed.

## Next coherent implementation milestone

1. Native global/local meshes and fields with separate ownership: global conduction
   prediction, local isoAdvector/momentum/pressure/thermal/laser correction. Retain
   material model and validated optics; avoid replacing fine optics with coarse normals.
2. Port overlap transfer to native parallel code with cached addressing and ownership
   across ranks. Validate box-volume equality for the current orthogonal hex geometry;
   reject deformed/non-box cells until general overlap is available.
3. Use true material enthalpy with reference and temperature-dependent cp/latent
   state; rho*(cp*T+L*epsilon) remains a proxy and is NOT the conserved-energy contract.
   Solve enthalpy-to-T/liquid inversion consistently with current M247 physics.
4. Local-core ownership of laser/evaporation/radiation/recoil and advective transport;
   global prediction must not count the same local heat source twice. Match interface
   conductive flux with opposite signs. Scatter integrated local corrections only.
5. Move the region using laser position plus active liquid/hot/fast wake; preserve old
   and new overlap fields, history and cold powder entry. Do not discard active flow
   or material at a region boundary. Boundary criteria must be validated, not relaxed
   to force a small region. Pressure/free-surface outlet treatment remains unresolved.
6. Package native build, transfer/energy/interface checks, matched physics and cost
   into ONE integrated driver. User runs one bounded acceptance job, not individual
   small parameter screens. Report numerical budget stop/failure, conserved energy,
   mass, molten/keyhole geometry, optical power and total wall cost together.

## Acceptance and production promotion

First integrated milestone is a functioning coupled regional solver with an auditable
energy/material ledger, not a promise of24h full-track execution. Then compare a
meaningful melting/solidification interval against the protected full-CFD reference.
Region and mesh/timestep errors must be separated. Proceed to a24h-budget4um
verification and1.5-2mm full track only after physical/cost evidence supports it.
2um accuracy and full-track affordability remain unproven.

Do not ask the user to run more dt/cadence/halo combinations. Continue implementation
locally until the integrated native milestone is concrete enough to test.


## Native regional stage: transfer/enthalpy/FV wiring implemented, LPBF coupling pending

Added src/m247RegionalCoupling/m247RegionalTransfer.H:owned MPI geometry/data
exchange,sparse rectangular overlap,cache invalidation,integrated correction ledger.
Added pure-metal exactclamped cp/latent enthalpy and inversion,checked with actual
M247790/860cp,150kJ/kg latent parameters in independent Python analytic tests.
Added two-region FV conduction/correction wiring utility with explicitdiffusion guard;
no sourcefield writes.150Python tests pass. Native compilation/MPI runtime unverified.
This is not yet local CFD:mixtureenthalpy,pressure/VOF/laser subdomain boundary,
moving field migration and matched physical/cost acceptance remain outstanding.
No new user-run small test in this checkpoint; preserve old validated solver.
Next development connects region ownership and actual local equations before one
combined user acceptance command. See src/m247RegionalCoupling/README.md.
