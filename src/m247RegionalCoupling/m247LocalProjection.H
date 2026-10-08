// Local fixed-mesh variable-density flux projection. Not a momentum/VOF solver.
#ifndef m247LocalProjection_H
#define m247LocalProjection_H
#include "fvCFD.H"
#include "constrainPressure.H"
namespace Foam
{
inline void m247LocalProjection(fvMesh& mesh,Time& time,const dictionary& c)
{
    if(mesh.moving()||mesh.topoChanging())
        FatalErrorInFunction<<"Projection prototype requires a fixed snapshot mesh"<<exit(FatalError);
    const scalar dt=c.get<scalar>("auditDeltaT"),divTolerance=c.get<scalar>("projectionDivergenceTolerance");
    const label passes=c.get<label>("projectionPasses");
    if(!std::isfinite(dt)||dt<=0||!std::isfinite(divTolerance)||divTolerance<=0||passes<1||passes>10)
        FatalErrorInFunction<<"Invalid local projection controls"<<exit(FatalError);
    volVectorField U(IOobject("U",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField dp(IOobject("pRegionalCorrection",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField rho(IOobject("rho",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    if(U.dimensions()!=dimVelocity||dp.dimensions()!=dimPressure||rho.dimensions()!=dimDensity)
        FatalErrorInFunction<<"Local projection expects U, physical pressure correction, rho"<<exit(FatalError);
    // First prototype requires a Dirichlet pressure anchor; never pin an arbitrary MPI cell.
    if(dp.needReference())FatalErrorInFunction<<"Local pressure correction requires a fixedValue outlet anchor"<<exit(FatalError);
    forAll(mesh.boundary(),patchi)
    {
        const auto& patch=mesh.boundary()[patchi];
        const word ut=U.boundaryField()[patchi].type(),pt=dp.boundaryField()[patchi].type();
        if(patch.coupled())
        {
            if(patch.type()!="processor")FatalErrorInFunction<<"Only processor coupled patches supported by projection prototype"<<exit(FatalError);
        }
        else if(!((ut=="fixedValue"&&pt=="fixedFluxPressure")||(ut=="zeroGradient"&&pt=="fixedValue")))
            FatalErrorInFunction<<"Unsupported regional U/pressure boundary pair on "<<patch.name()<<exit(FatalError);
    }
    U.correctBoundaryConditions();rho.correctBoundaryConditions();
    forAll(rho,i)
        if(!std::isfinite(rho[i])||rho[i]<=0||!std::isfinite(mag(U[i]))||!std::isfinite(dp[i]))
            FatalErrorInFunction<<"Invalid local projection fields"<<exit(FatalError);
    forAll(rho.boundaryField(),patchi)forAll(rho.boundaryField()[patchi],i)
        if(!std::isfinite(rho.boundaryField()[patchi][i])||rho.boundaryField()[patchi][i]<=0
            ||!std::isfinite(mag(U.boundaryField()[patchi][i]))||!std::isfinite(dp.boundaryField()[patchi][i]))
            FatalErrorInFunction<<"Invalid projection boundary data"<<exit(FatalError);
    const volScalarField rAU("regionalRAU",dimensionedScalar("dt",dimTime,dt)/rho);
    const surfaceScalarField rAUf("regionalRAUf",fvc::interpolate(rAU));
    surfaceScalarField predictor("regionalPhiPredictor",fvc::flux(U));
    surfaceScalarField phi("regionalPhi",predictor);
    mesh.setFluxRequired(dp.name());
    constrainPressure(dp,U,predictor,rAUf);
    scalar initialMax=0;
    const volScalarField initialDiv(fvc::div(predictor));
    forAll(initialDiv,i)initialMax=max(initialMax,mag(initialDiv[i]));
    reduce(initialMax,maxOp<scalar>());
    for(label pass=0;pass<passes;++pass)
    {
        fvScalarMatrix pressureEquation(fvm::laplacian(rAUf,dp)==fvc::div(predictor));
        pressureEquation.solve();
        if(pass==passes-1)phi=predictor-pressureEquation.flux();
    }
    U+=fvc::reconstruct(phi-predictor);U.correctBoundaryConditions();
    const volScalarField div(fvc::div(phi));
    scalar maxDiv=0,l1=0,net=0,volume=0;
    forAll(div,i)
    {
        if(!std::isfinite(div[i])||!std::isfinite(mag(U[i])))
            FatalErrorInFunction<<"Nonfinite projected flux/velocity"<<exit(FatalError);
        maxDiv=max(maxDiv,mag(div[i]));l1+=mag(div[i])*mesh.V()[i];volume+=mesh.V()[i];
    }
    forAll(mesh.boundary(),patchi)if(!mesh.boundary()[patchi].coupled())
        forAll(phi.boundaryField()[patchi],i)net+=phi.boundaryField()[patchi][i];
    reduce(maxDiv,maxOp<scalar>());reduce(l1,sumOp<scalar>());reduce(net,sumOp<scalar>());reduce(volume,sumOp<scalar>());
    if(maxDiv>divTolerance||mag(net)>divTolerance*volume)
        FatalErrorInFunction<<"Local pressure/flux continuity gate failed: maxDiv="<<maxDiv<<" boundaryNet="<<net<<exit(FatalError);
    Info().precision(17);
    Info<<"M247_LOCAL_PROJECTION schema=1 initialMaxDiv="<<initialMax<<" finalMaxDiv="<<maxDiv
        <<" divergenceL1M3PerS="<<l1<<" boundaryNetM3PerS="<<net
        <<" passes="<<passes<<" productionApproved=0"<<endl;
}
}
#endif
