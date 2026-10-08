// Conservatively mapped capacity moments; never regenerate them from averaged alpha.
#ifndef m247CapacityEnthalpy_H
#define m247CapacityEnthalpy_H
#include "m247MetalEnthalpy.H"
namespace Foam
{
class m247CapacityEnthalpy
{
    m247MetalEnthalpy sensible_;
    scalar latentCapacity_;
public:
    // cs/cl in J/m3/K; latentCapacity/inventory in J/m3.
    m247CapacityEnthalpy(scalar ts,scalar tl,scalar cs,scalar cl,scalar capacity)
    :sensible_(ts,tl,cs,cl,1),latentCapacity_(capacity)
    {
        if(!std::isfinite(capacity)||capacity<0)
            FatalErrorInFunction<<"Invalid mapped latent capacity"<<exit(FatalError);
    }
    scalar epsilon(scalar inventory) const
    {
        if(!std::isfinite(inventory)||inventory<0||inventory>latentCapacity_)
            FatalErrorInFunction<<"Mapped inventory exceeds mapped capacity"<<exit(FatalError);
        return latentCapacity_>0?inventory/latentCapacity_:0;
    }
    scalar density(scalar t,scalar inventory) const
    {epsilon(inventory);return sensible_.sensible(t)+inventory;}
    scalar temperature(scalar energy,scalar inventory) const
    {
        epsilon(inventory);
        if(!std::isfinite(energy)||energy<inventory)
            FatalErrorInFunction<<"Energy below mapped latent inventory"<<exit(FatalError);
        scalar lo=0,hi=1;
        // Doubling brackets any finite nonnegative sensible energy without cp getters.
        for(label iter=0;sensible_.sensible(hi)<energy-inventory;++iter)
        {
            if(iter>=1023||!std::isfinite(hi*2))
                FatalErrorInFunction<<"Mapped temperature bracket overflow"<<exit(FatalError);
            hi*=2;
        }
        for(label iter=0;iter<100;++iter)
        {scalar mid=lo+(hi-lo)*0.5;if(sensible_.sensible(mid)<energy-inventory)lo=mid;else hi=mid;}
        return lo+(hi-lo)*0.5;
    }
};
}
#endif
