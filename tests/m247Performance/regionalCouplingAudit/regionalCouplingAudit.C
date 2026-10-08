// Native two-region FV/enthalpy/transfer wiring audit. No VOF/flow/laser equations.
#include "fvCFD.H"
#include "timeSelector.H"
#include "m247RegionalTransfer.H"
#include "m247MetalEnthalpy.H"
#include "m247RegionalState.H"
using namespace Foam;
// Mixture branch audits fixed transported phase inventory, not equilibrium melting.
void auditMixture(fvMesh& thermal,fvMesh& local,Time& runTime,const IOdictionary& c)
{
    m247MixtureEnthalpy material(c.get<scalar>("Tsolidus"),c.get<scalar>("Tliquidus"),
        c.get<scalar>("cpSolidus"),c.get<scalar>("cpLiquidus"),c.get<scalar>("LatentHeat"),
        c.get<scalar>("rho"),c.get<scalar>("rhoGas"),c.get<scalar>("cpGas"),c.get<scalar>("LatentHeatGas"));
    const scalar dt=c.get<scalar>("auditDeltaT"),k=c.get<scalar>("kappa"),change=c.get<scalar>("manufacturedCorrectionDensity");
    if(!std::isfinite(dt)||dt<=0||!std::isfinite(k)||k<=0||!std::isfinite(change))
        FatalErrorInFunction<<"Invalid mixture audit controls"<<exit(FatalError);
    volScalarField T(IOobject("T",runTime.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
    volScalarField alpha(IOobject("alpha.metal",runTime.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
    volScalarField epsilon(IOobject("epsilon1",runTime.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
    if(T.dimensions()!=dimTemperature||alpha.dimensions()!=dimless||epsilon.dimensions()!=dimless)
        FatalErrorInFunction<<"Invalid regional mixture field dimensions"<<exit(FatalError);
    const dimensionedScalar kappa("kappa",dimensionSet(1,1,-3,-1,0,0,0),k);
    const volScalarField divergence(fvc::laplacian(kappa,T));
    const volScalarField geometry(fvc::surfaceSum(thermal.magSf()*thermal.deltaCoeffs()));
    scalarField energy(thermal.nCells()),latent(thermal.nCells());
    scalar before=0,heat=0,diffusion=0;
    const scalar minCp=min(min(c.get<scalar>("cpSolidus"),c.get<scalar>("cpLiquidus")),c.get<scalar>("cpGas"));
    forAll(energy,i)
    {
        const scalar old=material.density(T[i],alpha[i],epsilon[i]);
        latent[i]=material.latentDensity(alpha[i],epsilon[i]);
        energy[i]=old+dt*divergence[i];
        material.temperature(energy[i],alpha[i],epsilon[i]);
        before+=old*thermal.V()[i];heat+=dt*divergence[i]*thermal.V()[i];
        diffusion=max(diffusion,dt*k*geometry[i]/(material.rho(alpha[i])*minCp*thermal.V()[i]));
    }
    reduce(diffusion,maxOp<scalar>());
    if(!std::isfinite(diffusion)||diffusion>0.5)
        FatalErrorInFunction<<"Mixture audit diffusion step exceeds guard"<<exit(FatalError);
    m247RegionalTransfer transfer(thermal,local);
    const m247RegionalState state(transfer,material,energy,alpha.primitiveField(),latent);
    scalarField finalEnergy(state.energy);scalar added=0,maxInverseError=0;
    forAll(finalEnergy,i)
    {
        finalEnergy[i]+=change;
        const scalar back=state.closure(i).temperature(finalEnergy[i],state.latentInventory[i]);
        maxInverseError=max(maxInverseError,mag(state.closure(i).density(back,state.latentInventory[i])-finalEnergy[i])/max(mag(finalEnergy[i]),scalar(1)));
        added+=change*local.V()[i];
    }
    const scalarField correction=state.energyCorrection(transfer,finalEnergy,local.V());
    scalar after=0;
    forAll(energy,i)
    {
        material.temperature(energy[i]+correction[i],alpha[i],epsilon[i]);
        after+=(energy[i]+correction[i])*thermal.V()[i];
    }
    reduce(before,sumOp<scalar>());reduce(heat,sumOp<scalar>());reduce(added,sumOp<scalar>());
    reduce(after,sumOp<scalar>());reduce(maxInverseError,maxOp<scalar>());
    const scalar residual=mag(after-before-heat-added);
    if(residual>1e-10*max(mag(before)+mag(heat)+mag(added),scalar(1e-300))||maxInverseError>1e-10)
        FatalErrorInFunction<<"Regional mixture energy ledger failed"<<exit(FatalError);
    Info().precision(17);
    Info<<"M247_REGIONAL_MIXTURE_AUDIT schema=2 ranks="<<Pstream::nProcs()
        <<" beforeJ="<<before<<" heatAddedJ="<<heat<<" correctionJ="<<added<<" afterJ="<<after
        <<" ledgerResidualJ="<<residual<<" inverseRelativeError="<<maxInverseError
        <<" diffusionNumber="<<diffusion<<" phaseInventoryFixed=1 capacityMomentsMapped=1 productionApproved=0"<<endl;
}
int main(int argc,char *argv[])
{
    timeSelector::addOptions();
    #include "setRootCase.H"
    #include "createTime.H"
    const instantList times=timeSelector::select0(runTime,args);
    if(times.size()!=1)FatalErrorInFunction<<"Select exactly one regional snapshot"<<exit(FatalError);
    runTime.setTime(times[0],0);
    fvMesh thermal(IOobject("thermalRegion",runTime.timeName(),runTime,IOobject::MUST_READ));
    fvMesh local(IOobject("flowRegion",runTime.timeName(),runTime,IOobject::MUST_READ));
    IOdictionary controls(IOobject("regionalTransferDict",runTime.constant(),runTime,IOobject::MUST_READ,IOobject::NO_WRITE));
    if(controls.getOrDefault<bool>("mixtureAudit",false))
    {auditMixture(thermal,local,runTime,controls);Info<<"End"<<endl;return 0;}
    const scalar rho=controls.get<scalar>("rho"),conductivity=controls.get<scalar>("kappa");
    const scalar dt=controls.get<scalar>("auditDeltaT");
    const scalar correctionDensity=controls.get<scalar>("manufacturedCorrectionDensity");
    if(!std::isfinite(rho)||rho<=0||!std::isfinite(conductivity)||conductivity<=0||!std::isfinite(dt)||dt<=0||!std::isfinite(correctionDensity))
        FatalErrorInFunction<<"Invalid pure-metal wiring audit controls"<<exit(FatalError);
    m247MetalEnthalpy material(controls.get<scalar>("Tsolidus"),controls.get<scalar>("Tliquidus"),
        controls.get<scalar>("cpSolidus"),controls.get<scalar>("cpLiquidus"),controls.get<scalar>("LatentHeat"));
    volScalarField T(IOobject("T",runTime.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
    if(T.dimensions()!=dimTemperature)FatalErrorInFunction<<"Expected temperature dimensions"<<exit(FatalError);
    const dimensionedScalar kappa("kappa",dimensionSet(1,1,-3,-1,0,0,0),conductivity);
    const volScalarField divergence(fvc::laplacian(kappa,T));
    const volScalarField diffusionGeometry(fvc::surfaceSum(thermal.magSf()*thermal.deltaCoeffs()));
    const scalar minimumCp=min(controls.get<scalar>("cpSolidus"),controls.get<scalar>("cpLiquidus"));
    scalar diffusionNumber=0;
    forAll(T,i)diffusionNumber=max(diffusionNumber,dt*conductivity*diffusionGeometry[i]/(rho*minimumCp*thermal.V()[i]));
    reduce(diffusionNumber,maxOp<scalar>());
    if(!std::isfinite(diffusionNumber)||diffusionNumber>0.5)
        FatalErrorInFunction<<"Explicit pure-metal audit diffusion step too large"<<exit(FatalError);
    scalarField prediction(thermal.nCells());scalar before=0,heatAdded=0,maxInverseError=0;
    forAll(prediction,i)
    {
        if(!std::isfinite(T[i])||T[i]<=0||!std::isfinite(divergence[i]))
            FatalErrorInFunction<<"Invalid thermal predictor input"<<exit(FatalError);
        const scalar old=rho*material.value(T[i]);
        prediction[i]=old+dt*divergence[i];
        if(!std::isfinite(prediction[i])||prediction[i]<0)
            FatalErrorInFunction<<"Invalid explicit audit enthalpy prediction"<<exit(FatalError);
        before+=old*thermal.V()[i];heatAdded+=dt*divergence[i]*thermal.V()[i];
        const scalar back=material.temperature(prediction[i]/rho);
        maxInverseError=max(maxInverseError,mag(rho*material.value(back)-prediction[i])/max(prediction[i],scalar(1)));
    }
    m247RegionalTransfer transfer(thermal,local);
    const scalarField localPrediction=transfer.gatherDensity(prediction);
    scalarField delta(local.nCells());scalar localAdded=0;
    forAll(delta,i)
    {
        const scalar t=material.temperature(localPrediction[i]/rho);
        if(!std::isfinite(t))FatalErrorInFunction<<"Invalid gathered local temperature"<<exit(FatalError);
        delta[i]=correctionDensity*local.V()[i];localAdded+=delta[i];
    }
    const scalarField correction=transfer.scatterIntegratedCorrection(delta);
    scalar after=0;
    forAll(correction,i)
    {
        if(!std::isfinite(prediction[i]+correction[i])||prediction[i]+correction[i]<0)
            FatalErrorInFunction<<"Correction produced invalid enthalpy density"<<exit(FatalError);
        after+=(prediction[i]+correction[i])*thermal.V()[i];
    }
    reduce(before,sumOp<scalar>());reduce(heatAdded,sumOp<scalar>());
    reduce(localAdded,sumOp<scalar>());reduce(after,sumOp<scalar>());reduce(maxInverseError,maxOp<scalar>());
    const scalar residual=mag(after-before-heatAdded-localAdded);
    const scalar scale=max(mag(before)+mag(heatAdded)+mag(localAdded),scalar(1e-300));
    if(residual>1e-10*scale||maxInverseError>1e-10)
        FatalErrorInFunction<<"Regional heat/correction ledger failed"<<exit(FatalError);
    Info().precision(17);
    Info<<"M247_REGIONAL_AUDIT schema=1 ranks="<<Pstream::nProcs()
        <<" globalCells="<<returnReduce(thermal.nCells(),sumOp<label>())
        <<" localCells="<<returnReduce(local.nCells(),sumOp<label>())
        <<" beforeJ="<<before<<" heatAddedJ="<<heatAdded<<" correctionJ="<<localAdded
        <<" afterJ="<<after<<" ledgerResidualJ="<<residual<<" inverseRelativeError="<<maxInverseError
        <<" diffusionNumber="<<diffusionNumber<<" productionApproved=0"<<endl;
    Info<<"End"<<endl;return 0;
}
