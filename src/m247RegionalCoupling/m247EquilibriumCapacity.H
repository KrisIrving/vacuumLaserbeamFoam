#ifndef m247EquilibriumCapacity_H
#define m247EquilibriumCapacity_H
#include "m247MetalEnthalpy.H"
namespace Foam
{
// Experimental common Ts/Tl closure for transported capacity moments.
class m247EquilibriumCapacity
{
    m247MetalEnthalpy sensible_;
    scalar ts_,tl_,cs_,cl_,capacity_;
public:
    m247EquilibriumCapacity(scalar ts,scalar tl,scalar cs,scalar cl,scalar capacity)
    :sensible_(ts,tl,cs,cl,1),ts_(ts),tl_(tl),cs_(cs),cl_(cl),capacity_(capacity)
    {
        if(!std::isfinite(capacity)||capacity<0)
            FatalErrorInFunction<<"Invalid equilibrium latent capacity"<<exit(FatalError);
    }
    scalar fraction(scalar t) const {return sensible_.liquidFraction(t);}
    scalar sensible(scalar t) const {return sensible_.sensible(t);}
    scalar value(scalar t) const {return sensible(t)+capacity_*fraction(t);}
    scalar tangent(scalar t) const
    {
        if(!std::isfinite(t)||t<0)FatalErrorInFunction<<"Invalid equilibrium temperature"<<exit(FatalError);
        return cs_+(cl_-cs_)*fraction(t)+(t>=ts_&&t<=tl_?capacity_/(tl_-ts_):0);
    }
    scalar temperature(scalar energy) const
    {
        if(!std::isfinite(energy)||energy<0)FatalErrorInFunction<<"Invalid equilibrium energy"<<exit(FatalError);
        scalar lo=0,hi=max(tl_,energy/min(cs_,cl_));
        for(label i=0;i<100;++i)
        {const scalar mid=lo+(hi-lo)*0.5;if(value(mid)<energy)lo=mid;else hi=mid;}
        return lo+(hi-lo)*0.5;
    }
};
}
#endif
