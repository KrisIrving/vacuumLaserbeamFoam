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


## Local pressure/flux and source wiring (snapshot audits only)

localProjectionAudit true invokes m247LocalProjection.H on flowRegion before the
thermal audit. Required flowRegion U [m/s], rho [kg/m3], pRegionalCorrection [Pa];
controls projectionPasses (1..10), projectionDivergenceTolerance [1/s], auditDeltaT
[s]. pRegionalCorrection is an incremental physical pressure, NOT kinematic p or
legacy p_rgh. Give it a fixedValue pressure outlet anchor. Supported external
boundary pairs: U fixedValue + pRegionalCorrection fixedFluxPressure (walls/inlet),
U zeroGradient + pRegionalCorrection fixedValue (pressure outlet). Processor-only
coupling; no cyclic/empty/symmetry/moving mesh or closed gauge-only domain yet.
Provide pressure solver entry and required laplacian/interpolation/div schemes in
flowRegion fvSolution/fvSchemes. The module uses constrainPressure before pressure
Poisson solve and subtracts pressure matrix flux, then reconstructs U correction.
The corrected FACE phi remains continuity authority; reinterpolating corrected U
can spoil conservation. Inputs are NO_WRITE. M247_LOCAL_PROJECTION reports initial/
final max divergence, integral absolute divergence and physical boundary net flux;
processor flux is excluded from physical boundary ledger. Gate requires final
max divergence<=specified tolerance and abs(net)<=tolerance*global local volume.
Projection rho/U are supplied snapshots; they are not yet obtained from the mapped
state or a momentum predictor. This is not a VOF/free-surface boundary validation.

sourceAudit true requires mixtureAudit true and explicit globalContainsLocalSources
false. flowRegion supplies five [W/m3] fields: regionalLaserGain,
regionalEvaporationLoss, regionalRadiationLoss, regionalAdvectionGain,
regionalConductionGain. Arrays must already include interface localization, damping,
flux divergence and sign conventions from their physical models. Do not pass raw
surface evaporation [W/m2]. Local energy delta is dt*(laser-evaporation-radiation
+advection+localConduction-mappedGlobalConduction); its MPI-reduced components are
reported in M247_REGIONAL_SOURCES. This replaces manufacturedCorrectionDensity as
the mixed audit local correction. Global prediction still includes conduction once.
The ownership flag is a caller contract; no existing production source is redirected
by this utility. Actual source generation and matched conductive interface fluxes
are pending. Pressure and source audits are independent snapshot steps, not a
coupled local CFD timestep. 166 Python tests pass; native C++ compile/MPI unverified.

OpenFOAM2512 pressure-boundary/flux pattern checked against official solver source:
https://api.openfoam.com/2512/adjointShapeOptimizationFoam_8C_source.html


## First integrated native acceptance command

After pulling the current branch, in an OpenFOAM2512 Ubuntu shell at repository root:

```bash
./tests/m247Performance/RunRegionalAcceptance
```

Build2jobs by default; generated thermal16cells/local80cells; serial and MPI2ranks.
One invocation checks both positive/negative manufactured source corrections,
fully liquid/gas cross-interface capacity mapping, constant alpha and uniform T,
pressure flux projection, component/global energy ledger, unchanged inputs and
serial/MPI consistency. Geometry/power expectations are explicit in collector.
No existing powder case/checkpoint used. It is a native integration gate, not a
physical LPBF melting simulation, mesh-accuracy study or performance comparison.
No momentum predictor/VOF advection or actual ray tracing/source generation occurs.
Fixtures deliberately include nonequilibrium fully liquid metal at1580K to check
state preservation; this must not be read as an equilibrium M247 material result.

Build is capped at300s; all mesh/setup/serial/MPI commands share600s. MPI process
group terminates on timeout/interruption. Unique fresh run folder required;
completed native stages and reports are checked before declaring success. Every
exit packages M247_regional-acceptance-<timestamp>_review.tar.gz including named
logs, fixture source dictionaries/fields, input hashes, binarySHA256, build info,
checks and completion status. Send the archive even on failure. No production
case fields are edited. Changing number of MPI ranks is not exposed as a sweep.
The optional second positional argument changes build jobs only; runtime remains2.

Current172Python tests/Bash syntax pass; native compile/MPI runtime unverified.
All-region decomposition follows the official OpenFOAM2512 selection interface:
https://api.openfoam.com/2512/getAllRegionOptions_8H_source.html
