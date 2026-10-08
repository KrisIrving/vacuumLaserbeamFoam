// Inventory-preserving state handoff using the cached native transfer.
#ifndef m247RegionalState_H
#define m247RegionalState_H
#include "m247RegionalTransfer.H"
#include "m247MixtureEnthalpy.H"
namespace Foam
{
struct m247RegionalState
{
    scalarField energy,alpha,latentInventory,epsilon,temperature;
    m247RegionalState(const m247RegionalTransfer& transfer,
        const m247MixtureEnthalpy& material,const scalarField& globalEnergy,
        const scalarField& globalAlpha,const scalarField& globalLatent)
    :energy(transfer.gatherDensity(globalEnergy)),alpha(transfer.gatherDensity(globalAlpha)),
     latentInventory(transfer.gatherDensity(globalLatent)),epsilon(energy.size()),temperature(energy.size())
    {
        forAll(energy,i)
        {
            epsilon[i]=material.epsilon(alpha[i],latentInventory[i]);
            temperature[i]=material.temperature(energy[i],alpha[i],epsilon[i]);
        }
    }
    // Energy is returned as a delta from prediction, never an absolute replacement.
    scalarField energyCorrection(const m247RegionalTransfer& transfer,
        const scalarField& finalEnergy,const scalarField& localVolumes) const
    {
        if(finalEnergy.size()!=energy.size()||localVolumes.size()!=energy.size())
            FatalErrorInFunction<<"Regional state topology changed: rebuild and migrate state"<<exit(FatalError);
        scalarField delta(energy.size());
        forAll(delta,i)
        {
            if(!std::isfinite(localVolumes[i])||localVolumes[i]<=0||!std::isfinite(finalEnergy[i]))
                FatalErrorInFunction<<"Invalid regional energy correction"<<exit(FatalError);
            delta[i]=(finalEnergy[i]-energy[i])*localVolumes[i];
        }
        return transfer.scatterIntegratedCorrection(delta);
    }
};
}
#endif
