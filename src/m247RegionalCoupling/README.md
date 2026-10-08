# Native regional coupling: integration in progress

This module is not yet a regional LPBF solver. Static/default vacuumLaserbeamFoam
is untouched. No performance or native compile result is claimed.

m247RegionalTransfer.H binds a coarse global fvMesh and a local fvMesh on the same
MPI communicator. It gathers coarse owned rectangular-cell geometry once, builds
sparse overlaps with local owned cells, gathers current global density, and reduces
integrated local corrections to the correct coarse owners. Zero-cell ranks are
supported. Global mesh limit200000cells is an explicit reference scalability cap,
not a prescribed production resolution. Replicated coarse addressing is a prototype;
neighbor-only exchange must replace it if communication costs dominate.

Inputs must be valid non-overlapping FV meshes, rectangular cell bounding volumes
matching mesh.V(), and local domain fully inside the global domain. Geometry/
connectivity stamps reject reuse after point motion or topology/ownership changes,
even if cell counts are unchanged. Rebuild transfer after a regional move.
Local correction is an integrated DELTA from coarse prediction (joules for energy),
not absolute energy. Methods operate on dimensionless scalar arrays; the calling
solver owns dimensions and thermodynamic meaning. Constant values and negative
corrections are allowed; nonfinite values and incomplete coverage stop execution.

m247MetalEnthalpy.H integrates clamped-linear cp(T) and equilibrium latent heat,
with h(0K)=0 reference. Exact sensible integral, monotone bisection inverse; pure
metal only. Current M247 values:Ts1537K,Tl1631K,cpSolidus790,cpLiquidus860J/kg/K,
latent150000J/kg. This equilibrium model remains pure-metal only. Mixed cells use the separate
fixed-phase closure below; never apply the equilibrium inverse to them.

regionalCouplingAudit reads two named regions thermalRegion and flowRegion. It
performs one pure-metal explicit global conduction prediction, density gathering,
manufactured local correction scatter, and global energy ledger. Input T and mesh
are NO_WRITE; no solver time advancement/VOF/pressure/laser equations occur.
Diffusion number<=0.5 conservatively limits its explicit step. This is an engineering
wiring audit, not a physical LPBF benchmark or approved timestep policy.
Required constant/regionalTransferDict scalars:rho,kappa,auditDeltaT,
manufacturedCorrectionDensity,Tsolidus,Tliquidus,cpSolidus,cpLiquidus,LatentHeat.
Global named region supplies T with temperature dimensions and valid BCs/schemes.
Native utility build, multi-region fixture and MPI runtime are pending; do not ask
the user to run this audit alone. Bundle it into the integrated regional milestone.

Official2512communications interfaces checked:allGatherList andlistCombineReduce
https://api.openfoam.com/2512/classFoam_1_1Pstream.html


m247MixtureEnthalpy.H implements a ledger closure with alpha-weighted integrated
sensible cp and rho(alpha)*L(alpha_filtered)*epsilon. The latent filter matches
updateProps (<.01 ->0, >.99 ->1); density uses bounded alpha. Constant gas cp,
clamped-linear metal cp only. It is not a general polynomial material model or
proof of equivalence to the existing variable-coefficient advective TEqn.
Fixed epsilon inversion preserves transported latent inventory, without imposing
phase equilibrium. Phase relaxation and energy/VOF advection remain solver work.

m247RegionalState.H gathers energy [J/m3], alpha [metal m3/m3], and latent energy
[J/m3] independently. It reconstructs epsilon and T, fails on inadmissible state,
and returns integrated energy DELTAS only. Average alpha can lower latent capacity:
a crossing cell containing fully liquid metal and cold gas may be inadmissible.
No clipping or silent energy loss; a bounded conservative redistribution is pending.
The state object is a handoff snapshot; regenerate after topology/field changes.
It does not migrate momentum or return VOF/latent corrections from local CFD yet.

Optional mixtureAudit true in regionalTransferDict selects mixed audit; add
rhoGas,cpGas,LatentHeatGas; thermalRegion requires alpha.metal and epsilon1 with
dimless dimensions. All original controls retained. Global/local phase inventories
are fixed during manufactured energy-only correction. M247_REGIONAL_MIXTURE_AUDIT
reports conduction, delta source, final energy, residual, inverse error and diffusion
guard. Input fields remain NO_WRITE. This is still a wiring audit, not local CFD.
155 Python tests pass; native build/runtime remain pending. No standalone user
micro-screen is requested: include in the future integrated acceptance command.


## Persistent capacity moments (current native state contract)

The initial alpha-only inverse above remains a diagnostic for original cell states.
Regional state handoff now uses m247CapacityEnthalpy.H: map Csolid=rho*cpSolidMix,
Cliquid=rho*cpLiquidMix and latent capacity=rho*Lfiltered as independent densities,
plus energy, alpha and latent inventory. The common metal Ts/Tl define the sensible
capacity ramp; constant gas cp is included in both endpoints. Because these
capacities are volume averaged with the same positive overlap weights, valid
source inventories remain bounded by mapped latent capacity. Uniform source T
remains uniform after remapping even across metal/gas. An alpha-only reconstruction
can fail both properties due to nonlinear rho(alpha)*cp(alpha)/L(alpha).

m247RegionalState original-material constructor imports moments from checkpoint
coefficients ONCE. Its explicit-moment overload supports repeated remaps; callers
must carry stored solidCapacity,liquidCapacity,latentCapacity fields thereafter.
Regenerating them from averaged alpha loses subcell information. Volume integrals
are conserved over equal covered domains; a cropped window retains only overlap
and requires the future global history/migration ledger for excluded material.
This carries subcell coefficient moments; it does not reconstruct VOF geometry,
prove phase equilibrium, or supply their evolution under local flow/advection.

Mixed native audit schema2 uses capacityMomentsMapped=1 and checks mapped energy
inversion. Original global energy-only correction is unchanged. Native build/MPI
pending; 160 Python reference tests pass. Default LPBF solver is untouched. No
production promotion, full track cost prediction or standalone user test requested.
