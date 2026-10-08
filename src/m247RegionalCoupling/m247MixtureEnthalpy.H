// State closure for regional energy exchange; not a replacement for TEqn.
#ifndef m247MixtureEnthalpy_H
#define m247MixtureEnthalpy_H
#include "m247MetalEnthalpy.H"
namespace Foam
{
class m247MixtureEnthalpy
{
    m247MetalEnthalpy metal_;
    scalar rhoMetal_,rhoGas_,cpGas_,latentMetal_,latentGas_,minimumCp_,ts_,tl_,cs_,cl_;
    static void fraction(scalar x)
    {
        if(!std::isfinite(x)||x<0||x>1)
            FatalErrorInFunction<<"Regional fraction outside [0,1]; clipping would lose inventory"<<exit(FatalError);
    }
public:
    m247MixtureEnthalpy(scalar ts,scalar tl,scalar cs,scalar cl,scalar lm,
        scalar rm,scalar rg,scalar cg,scalar lg)
    :metal_(ts,tl,cs,cl,lm),rhoMetal_(rm),rhoGas_(rg),cpGas_(cg),
      latentMetal_(lm),latentGas_(lg),minimumCp_(min(min(cs,cl),cg)),ts_(ts),tl_(tl),cs_(cs),cl_(cl)
    {
        if(!std::isfinite(rm)||!std::isfinite(rg)||!std::isfinite(cg)||!std::isfinite(lg)
            ||rm<=0||rg<=0||cg<=0||lg<0)
            FatalErrorInFunction<<"Invalid regional mixture parameters"<<exit(FatalError);
    }
    scalar solidus() const {return ts_;}
    scalar liquidus() const {return tl_;}
    scalar sensibleSolidCapacity(scalar a) const {return rho(a)*(a*cs_+(1-a)*cpGas_);}
    scalar sensibleLiquidCapacity(scalar a) const {return rho(a)*(a*cl_+(1-a)*cpGas_);}
    scalar rho(scalar a) const {fraction(a);return a*rhoMetal_+(1-a)*rhoGas_;}
    scalar latent(scalar a) const
    {
        fraction(a);const scalar filtered=a<0.01?0:(a>0.99?1:a);
        return filtered*latentMetal_+(1-filtered)*latentGas_;
    }
    scalar capacity(scalar a) const {return rho(a)*latent(a);}
    scalar latentDensity(scalar a,scalar e) const {fraction(e);return capacity(a)*e;}
    scalar epsilon(scalar a,scalar inventory) const
    {
        const scalar cap=capacity(a);
        if(!std::isfinite(inventory)||inventory<0||inventory>cap)
            FatalErrorInFunction<<"Mapped latent inventory incompatible with alpha; conservative remap required"<<exit(FatalError);
        return cap>0?inventory/cap:0;
    }
    scalar density(scalar t,scalar a,scalar e) const
    {
        fraction(e);
        return rho(a)*(a*metal_.sensible(t)+(1-a)*cpGas_*t)+latentDensity(a,e);
    }
    // Hold transported liquid inventory fixed; never invent equilibrium epsilon.
    scalar temperature(scalar energy,scalar a,scalar e) const
    {
        const scalar latentEnergy=latentDensity(a,e),r=rho(a);
        if(!std::isfinite(energy)||energy<latentEnergy)
            FatalErrorInFunction<<"Insufficient regional energy for transported latent inventory"<<exit(FatalError);
        scalar lo=0,hi=(energy-latentEnergy)/(r*minimumCp_);
        for(label iter=0;iter<100;++iter)
        {const scalar mid=lo+(hi-lo)*0.5;if(density(mid,a,e)<energy)lo=mid;else hi=mid;}
        return lo+(hi-lo)*0.5;
    }
};
}
#endif
