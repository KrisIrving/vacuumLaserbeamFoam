#ifndef m247ConductionPhase_H
#define m247ConductionPhase_H
#include "fvCFD.H"
#include "m247EquilibriumCapacity.H"
namespace Foam
{
// Backward Euler conduction with exact enthalpy and a semismooth Newton tangent.
inline scalar m247ConductionPhase(volScalarField& T,const volScalarField& cs,const volScalarField& cl,
    const scalarField& capacity,const scalarField& advectedEnergy,scalar ts,scalar tl,scalar dt,
    const dictionary& controls,scalarField& sensible,scalarField& latent,scalarField& reserve)
{
    fvMesh& mesh=const_cast<fvMesh&>(T.mesh());
    const scalar tolerance=controls.get<scalar>("phaseEnergyTolerance");
    const label limit=controls.get<label>("phaseCorrectors");
    const scalar km=controls.get<scalar>("kappa"),kl=controls.get<scalar>("kappaLiquid"),kg=controls.get<scalar>("kappaGas");
    if(!std::isfinite(tolerance)||tolerance<=0||tolerance>1e-6||limit<1||limit>100
        ||!std::isfinite(km)||km<=0||!std::isfinite(kl)||kl<=0||!std::isfinite(kg)||kg<=0||!std::isfinite(dt)||dt<=0)
        FatalErrorInFunction<<"Invalid conduction/phase controls"<<exit(FatalError);
    const volScalarField& alpha=mesh.lookupObject<volScalarField>("alpha.metal");
    volScalarField coefficient(IOobject("regionalEnthalpyTangent",mesh.time().timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),mesh,
        dimensionedScalar("zero",dimensionSet(1,-1,-2,-1,0,0,0),0));
    volScalarField rhs(IOobject("regionalPhaseRHS",mesh.time().timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),mesh,
        dimensionedScalar("zero",dimensionSet(1,-1,-3,0,0,0,0),0));
    wordList kPatches(mesh.boundary().size(), "zeroGradient");
    forAll(mesh.boundary(),p)if(mesh.boundary()[p].coupled())kPatches[p]=mesh.boundary()[p].type();
    volScalarField k(IOobject("regionalConductivity",mesh.time().timeName(),mesh,IOobject::NO_READ,IOobject::NO_WRITE),mesh,
        dimensionedScalar("k",dimensionSet(1,1,-3,-1,0,0,0),km),kPatches);
    mesh.setFluxRequired(T.name());
    scalarField conserved(advectedEnergy);scalar maxError=GREAT,boundary=0;label used=0;
    forAll(T,i)T[i]=m247EquilibriumCapacity(ts,tl,cs[i],cl[i],capacity[i]).temperature(advectedEnergy[i]);
    T.correctBoundaryConditions();
    for(label iteration=1;iteration<=limit;++iteration)
    {
        const scalarField previousTemperature(T.primitiveField());
        forAll(T,i)
        {
            const m247EquilibriumCapacity h(ts,tl,cs[i],cl[i],capacity[i]);
            coefficient[i]=h.tangent(T[i]);
            rhs[i]=(advectedEnergy[i]-h.value(T[i])+coefficient[i]*T[i])/dt;
            k[i]=alpha[i]*(km+(kl-km)*h.fraction(T[i]))+(1-alpha[i])*kg;
        }
        // Physical patches extrapolate; processor patches exchange neighbour values.
        k.correctBoundaryConditions();
        const dimensionedScalar step("dt",dimTime,dt);
        fvScalarMatrix equation(fvm::Sp(coefficient/step,T)-fvm::laplacian(k,T)==rhs);
        equation.solve();
        const surfaceScalarField flux(equation.flux());
        const volScalarField div(fvc::div(flux));
        maxError=0;boundary=0;
        forAll(T,i)
        {
            conserved[i]=advectedEnergy[i]-dt*div[i];
            const m247EquilibriumCapacity h(ts,tl,cs[i],cl[i],capacity[i]);
            if(!std::isfinite(T[i])||T[i]<0||!std::isfinite(conserved[i])||conserved[i]<0)
                FatalErrorInFunction<<"Invalid conduction/phase state"<<exit(FatalError);
            maxError=max(maxError,mag(h.value(T[i])-conserved[i])/max(mag(conserved[i]),scalar(1)));
            // Also converge temperature-dependent conductivity, not only enthalpy.
            maxError=max(maxError,mag(T[i]-previousTemperature[i])/max(mag(T[i]),scalar(1)));
        }
        reduce(maxError,maxOp<scalar>());
        forAll(mesh.boundary(),p)if(!mesh.boundary()[p].coupled())
            forAll(flux.boundaryField()[p],j)boundary+=dt*flux.boundaryField()[p][j];
        reduce(boundary,sumOp<scalar>());used=iteration;
        if(maxError<=tolerance)break;
    }
    if(maxError>tolerance)FatalErrorInFunction<<"Conduction/phase corrector limit: residual="<<maxError<<exit(FatalError);
    scalar minLiquid=GREAT,maxLiquid=0,phaseChange=0,conducted=0,liquidInventory=0,totalCapacity=0;
    forAll(T,i)
    {
        const m247EquilibriumCapacity h(ts,tl,cs[i],cl[i],capacity[i]);
        T[i]=h.temperature(conserved[i]);const scalar liquid=h.fraction(T[i]);
        const scalar old=latent[i];latent[i]=capacity[i]*liquid;reserve[i]=capacity[i]*(1-liquid);
        conducted+=mag(conserved[i]-advectedEnergy[i])*mesh.V()[i];
        liquidInventory+=latent[i]*mesh.V()[i];totalCapacity+=capacity[i]*mesh.V()[i];
        sensible[i]=h.sensible(T[i]);phaseChange+=mag(latent[i]-old)*mesh.V()[i];
        minLiquid=min(minLiquid,liquid);maxLiquid=max(maxLiquid,liquid);
    }
    T.correctBoundaryConditions();reduce(minLiquid,minOp<scalar>());reduce(maxLiquid,maxOp<scalar>());reduce(phaseChange,sumOp<scalar>());reduce(conducted,sumOp<scalar>());reduce(liquidInventory,sumOp<scalar>());reduce(totalCapacity,sumOp<scalar>());
    Info().precision(17);
    Info<<"M247_CONDUCTION_PHASE schema=1 time="<<mesh.time().value()<<" correctors="<<used
        <<" energyRelativeError="<<maxError<<" liquidMin="<<minLiquid<<" liquidMax="<<maxLiquid
        <<" liquidCapacityFraction="<<liquidInventory/max(totalCapacity,scalar(VSMALL))<<" conductionRedistributedJ="<<conducted<<" latentRedistributedJ="<<phaseChange<<" conductiveBoundaryOutJ="<<boundary<<" productionApproved=0"<<endl;
    return boundary;
}
}
#endif
