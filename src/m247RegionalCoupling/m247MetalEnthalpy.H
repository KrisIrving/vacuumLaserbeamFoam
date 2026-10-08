// Pure-metal clamped-linear cp with equilibrium latent heat. No mixed-cell closure.
#ifndef m247MetalEnthalpy_H
#define m247MetalEnthalpy_H
#include "scalar.H"
#include "label.H"
#include "error.H"
#include <cmath>
namespace Foam
{
class m247MetalEnthalpy
{
    scalar ts_,tl_,cs_,cl_,latent_;
public:
    m247MetalEnthalpy(scalar ts,scalar tl,scalar cs,scalar cl,scalar latent)
    :ts_(ts),tl_(tl),cs_(cs),cl_(cl),latent_(latent)
    {
        if(!std::isfinite(ts)||!std::isfinite(tl)||!std::isfinite(cs)||!std::isfinite(cl)||!std::isfinite(latent)
            ||ts<=0||tl<=ts||cs<=0||cl<=0||latent<=0)
            FatalErrorInFunction<<"Invalid clamped-linear metal enthalpy parameters"<<exit(FatalError);
    }
    scalar liquidFraction(scalar t) const {return max(min((t-ts_)/(tl_-ts_),scalar(1)),scalar(0));}
    scalar sensible(scalar t) const
    {
        if(!std::isfinite(t)||t<0)FatalErrorInFunction<<"Invalid temperature"<<exit(FatalError);
        if(t<=ts_)return cs_*t;
        const scalar x=min(t,tl_)-ts_;
        return cs_*ts_+cs_*x+0.5*(cl_-cs_)*x*x/(tl_-ts_)+cl_*max(t-tl_,scalar(0));
    }
    scalar value(scalar t) const {return sensible(t)+latent_*liquidFraction(t);}
    scalar temperature(scalar h) const
    {
        if(!std::isfinite(h)||h<0)FatalErrorInFunction<<"Invalid equilibrium enthalpy"<<exit(FatalError);
        scalar lo=0,hi=max(tl_,h/min(cs_,cl_));
        for(label iter=0;iter<100;++iter)
        { const scalar mid=lo+(hi-lo)*0.5;if(value(mid)<h)lo=mid;else hi=mid; }
        return lo+(hi-lo)*0.5;
    }
};
}
#endif
