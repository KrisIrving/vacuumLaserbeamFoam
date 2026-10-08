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
latent150000J/kg. No gas/metal mixture closure or nonequilibrium liquid treatment
is implemented. Do not apply this model to alpha-weighted powder/gas cells yet.

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
