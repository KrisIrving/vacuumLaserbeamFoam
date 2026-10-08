// Inventory-preserving state handoff using the cached native transfer.
#ifndef m247RegionalState_H
#define m247RegionalState_H
#include "m247RegionalTransfer.H"
#include "m247MixtureEnthalpy.H"
#include "m247CapacityEnthalpy.H"
namespace Foam
{
struct m247RegionalState
{
    scalar solidus,liquidus;
    scalarField energy,alpha,latentInventory,solidCapacity,liquidCapacity,latentCapacity,epsilon,temperature;
private:
    static scalarField coefficients(const m247MixtureEnthalpy& m,const scalarField& a,label which)
    {
        scalarField values(a.size());
        forAll(values,i)values[i]=which==0?m.sensibleSolidCapacity(a[i]):
            (which==1?m.sensibleLiquidCapacity(a[i]):m.capacity(a[i]));
        return values;
    }
public:
    // Initial checkpoint import only. Later moves MUST use the moment overload.
    m247RegionalState(const m247RegionalTransfer& transfer,
        const m247MixtureEnthalpy& material,const scalarField& globalEnergy,
        const scalarField& globalAlpha,const scalarField& globalLatent)
    :m247RegionalState(transfer,material.solidus(),material.liquidus(),globalEnergy,
        globalAlpha,globalLatent,coefficients(material,globalAlpha,0),
        coefficients(material,globalAlpha,1),coefficients(material,globalAlpha,2))
    {}
    // Persistent moment remap: carries subcell capacities across repeated moves.
    m247RegionalState(const m247RegionalTransfer& transfer,scalar ts,scalar tl,
        const scalarField& globalEnergy,const scalarField& globalAlpha,const scalarField& globalLatent,
        const scalarField& globalCs,const scalarField& globalCl,const scalarField& globalCapacity)
    :solidus(ts),liquidus(tl),energy(transfer.gatherDensity(globalEnergy)),alpha(transfer.gatherDensity(globalAlpha)),
     latentInventory(transfer.gatherDensity(globalLatent)),solidCapacity(transfer.gatherDensity(globalCs)),
     liquidCapacity(transfer.gatherDensity(globalCl)),latentCapacity(transfer.gatherDensity(globalCapacity)),
     epsilon(energy.size()),temperature(energy.size())
    {
        forAll(energy,i)
        {
            if(!std::isfinite(alpha[i])||alpha[i]<0||alpha[i]>1)
                FatalErrorInFunction<<"Invalid mapped alpha"<<exit(FatalError);
            const m247CapacityEnthalpy closure(solidus,liquidus,solidCapacity[i],liquidCapacity[i],latentCapacity[i]);
            epsilon[i]=closure.epsilon(latentInventory[i]);
            temperature[i]=closure.temperature(energy[i],latentInventory[i]);
        }
    }
    m247CapacityEnthalpy closure(label i) const
    {return m247CapacityEnthalpy(solidus,liquidus,solidCapacity[i],liquidCapacity[i],latentCapacity[i]);}
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
            closure(i).temperature(finalEnergy[i],latentInventory[i]);
            delta[i]=(finalEnergy[i]-energy[i])*localVolumes[i];
        }
        return transfer.scatterIntegratedCorrection(delta);
    }
};
}
#endif
