// Fixed regional cold-flow time steps: actual momentum, pressure and isoAdvector.
// Thermal/phase/source/moving-window coupling is deliberately absent at this gate.
#ifndef m247LocalFlowAudit_H
#define m247LocalFlowAudit_H
#include "isoAdvection.H"
#include "m247LocalProjection.H"
#include "m247RegionalTransfer.H"
namespace Foam
{
inline scalar m247BoundaryFlux(const surfaceScalarField& flux)
{
    scalar sum=0;
    forAll(flux.boundaryField(),patchi)if(!flux.mesh().boundary()[patchi].coupled())
        forAll(flux.boundaryField()[patchi],i)sum+=flux.boundaryField()[patchi][i];
    reduce(sum,sumOp<scalar>());return sum;
}
inline void m247LocalFlowAudit(fvMesh& thermal,fvMesh& mesh,Time& time,const dictionary& c)
{
    const scalar dt=c.get<scalar>("flowDeltaT"),nuM=c.get<scalar>("flowNuMetal"),nuG=c.get<scalar>("flowNuGas");
    const label steps=c.get<label>("flowSteps");
    if(!std::isfinite(dt)||dt<=0||!std::isfinite(nuM)||nuM<=0||!std::isfinite(nuG)||nuG<=0||steps<2||steps>100)
        FatalErrorInFunction<<"Invalid regional flow step controls"<<exit(FatalError);
    const dimensionedScalar rm("rhoMetal",dimDensity,c.get<scalar>("rho")),rg("rhoGas",dimDensity,c.get<scalar>("rhoGas"));
    if(!std::isfinite(rm.value())||rm.value()<=0||!std::isfinite(rg.value())||rg.value()<=0)
        FatalErrorInFunction<<"Invalid regional flow densities"<<exit(FatalError);
    volScalarField coarseAlpha(IOobject("alpha.metal",time.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
    volScalarField alpha(IOobject("alpha.metal",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volVectorField U(IOobject("U",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField p(IOobject("pRegionalCorrection",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    if(alpha.dimensions()!=dimless||coarseAlpha.dimensions()!=dimless)
        FatalErrorInFunction<<"Invalid alpha dimensions"<<exit(FatalError);
    m247RegionalTransfer transfer(thermal,mesh);
    alpha.primitiveFieldRef()=transfer.gatherDensity(coarseAlpha.primitiveField());alpha.correctBoundaryConditions();
    volScalarField rho(IOobject("rho",time.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),alpha*rm+(1-alpha)*rg);
    surfaceScalarField phi(IOobject("phi",time.timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),fvc::flux(U));
    const volScalarField initialRAU("initialRAU",dimensionedScalar("dt",dimTime,dt)/rho);
    m247ProjectFlux(U,rho,p,phi,initialRAU,c);
    surfaceScalarField rhoPhi("rhoPhi",fvc::interpolate(rho)*phi);
    mesh.setFluxRequired(alpha.name());
    isoAdvection advector(alpha,phi,U);
    const scalarField original(alpha.primitiveField());
    scalar initialVolume=0;
    forAll(alpha,i)
    {
        if(!std::isfinite(alpha[i])||alpha[i]<0||alpha[i]>1)
            FatalErrorInFunction<<"Invalid imported regional alpha"<<exit(FatalError);
        initialVolume+=alpha[i]*mesh.V()[i];
    }
    reduce(initialVolume,sumOp<scalar>());
    scalar cumulativeMetalOut=0,maxVolumeResidual=0,maxMassResidual=0;
    time.setDeltaT(dt);alpha.oldTime();rho.oldTime();U.oldTime();
    for(label step=1;step<=steps;++step)
    {
        scalar beforeVolume=0,beforeMass=0;
        forAll(alpha,i){beforeVolume+=alpha[i]*mesh.V()[i];beforeMass+=rho[i]*mesh.V()[i];}
        reduce(beforeVolume,sumOp<scalar>());reduce(beforeMass,sumOp<scalar>());
        const volScalarField faceSum(fvc::surfaceSum(mag(phi)));
        scalar courant=0;
        forAll(faceSum,i)courant=max(courant,0.5*dt*faceSum[i]/mesh.V()[i]);
        reduce(courant,maxOp<scalar>());
        if(!std::isfinite(courant)||courant>0.25)FatalErrorInFunction<<"Regional flow Courant guard failed"<<exit(FatalError);
        ++time;
        advector.advect(zeroField(),zeroField());
        rho=alpha*rm+(1-alpha)*rg;rho.correctBoundaryConditions();
        rhoPhi=advector.getRhoPhi(rm,rg);
        scalar afterVolume=0,afterMass=0,lo=GREAT,hi=-GREAT;
        forAll(alpha,i)
        {
            if(!std::isfinite(alpha[i])||alpha[i]<-1e-10||alpha[i]>1+1e-10)
                FatalErrorInFunction<<"Regional VOF bound failed; no clipping applied"<<exit(FatalError);
            afterVolume+=alpha[i]*mesh.V()[i];afterMass+=rho[i]*mesh.V()[i];lo=min(lo,alpha[i]);hi=max(hi,alpha[i]);
        }
        reduce(afterVolume,sumOp<scalar>());reduce(afterMass,sumOp<scalar>());reduce(lo,minOp<scalar>());reduce(hi,maxOp<scalar>());
        const scalar metalOut=dt*m247BoundaryFlux(advector.alphaPhi()),massOut=dt*m247BoundaryFlux(rhoPhi);
        if(!std::isfinite(metalOut)||!std::isfinite(massOut))
            FatalErrorInFunction<<"Nonfinite regional boundary flux"<<exit(FatalError);
        cumulativeMetalOut+=metalOut;
        const scalar volumeResidual=mag(afterVolume-beforeVolume+metalOut),massResidual=mag(afterMass-beforeMass+massOut);
        maxVolumeResidual=max(maxVolumeResidual,volumeResidual);maxMassResidual=max(maxMassResidual,massResidual);
        if(volumeResidual>1e-8*max(beforeVolume,scalar(1e-20))||massResidual>1e-8*max(beforeMass,scalar(1e-20)))
            FatalErrorInFunction<<"Regional VOF/mass boundary ledger failed"<<exit(FatalError);
        const volScalarField mu("mu",rho*(alpha*dimensionedScalar("nuM",dimViscosity,nuM)+(1-alpha)*dimensionedScalar("nuG",dimViscosity,nuG)));
        fvVectorMatrix momentum(fvm::ddt(rho,U)+fvm::div(rhoPhi,U)
            -fvm::Sp(fvc::ddt(rho)+fvc::div(rhoPhi),U)-fvm::laplacian(mu,U));
        momentum.solve();
        const volScalarField rAU("flowRAU",1.0/momentum.A());
        m247ProjectFlux(U,rho,p,phi,rAU,c);
        Info().precision(17);
        Info<<"M247_REGIONAL_FLOW_STEP schema=1 step="<<step<<" time="<<time.value()
            <<" courant="<<courant<<" alphaMin="<<lo<<" alphaMax="<<hi
            <<" metalVolumeM3="<<afterVolume<<" massKg="<<afterMass
            <<" metalBoundaryOutM3="<<metalOut<<" massBoundaryOutKg="<<massOut
            <<" volumeResidualM3="<<volumeResidual<<" massResidualKg="<<massResidual<<endl;
    }
    scalar finalVolume=0,changed=0;
    forAll(alpha,i){finalVolume+=alpha[i]*mesh.V()[i];changed+=mag(alpha[i]-original[i])*mesh.V()[i];}
    reduce(finalVolume,sumOp<scalar>());reduce(changed,sumOp<scalar>());
    Info<<"M247_REGIONAL_FLOW_COMPLETE schema=1 ranks="<<Pstream::nProcs()<<" steps="<<steps
        <<" initialMetalM3="<<initialVolume<<" finalMetalM3="<<finalVolume<<" cumulativeMetalOutM3="<<cumulativeMetalOut
        <<" alphaChangeL1M3="<<changed<<" maxVolumeResidualM3="<<maxVolumeResidual
        <<" maxMassResidualKg="<<maxMassResidual<<" productionApproved=0"<<endl;
}
}
#endif
