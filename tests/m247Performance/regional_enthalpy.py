"""Independent pure-metal equilibrium enthalpy reference for native coupling tests."""
import math
class MetalEnthalpy:
    def __init__(self,solidus,liquidus,cp_s,cp_l,latent):
        if any(not math.isfinite(x) for x in (solidus,liquidus,cp_s,cp_l,latent)) or solidus<=0 or liquidus<=solidus or min(cp_s,cp_l,latent)<=0:raise ValueError('Invalid metal properties')
        self.ts,self.tl,self.cs,self.cl,self.latent=solidus,liquidus,cp_s,cp_l,latent
    def liquid(self,t):return min(1,max(0,(t-self.ts)/(self.tl-self.ts)))
    def sensible(self,t):
        if not math.isfinite(t) or t<0:raise ValueError('Invalid temperature')
        if t<=self.ts:return self.cs*t
        x=min(t,self.tl)-self.ts
        return self.cs*self.ts+self.cs*x+.5*(self.cl-self.cs)*x*x/(self.tl-self.ts)+self.cl*max(t-self.tl,0)
    def value(self,t):return self.sensible(t)+self.latent*self.liquid(t)
    def temperature(self,h):
        if not math.isfinite(h) or h<0:raise ValueError('Invalid enthalpy')
        solid=self.cs*self.ts;liquid=self.value(self.tl)
        if h<=solid:return h/self.cs
        if h>=liquid:return self.tl+(h-liquid)/self.cl
        # Independent quadratic inverse, unlike native bisection.
        a=.5*(self.cl-self.cs)/(self.tl-self.ts)
        b=self.cs+self.latent/(self.tl-self.ts);c=solid-h
        x=-c/b if a==0 else -2*c/(b+math.sqrt(b*b-4*a*c))
        return self.ts+x


class MixtureEnthalpy:
    """Fixed liquid state, alpha-weighted cp and legacy filtered latent coefficient.

    This ledger closure does not assert equivalence to the advective TEqn.
    """
    def __init__(self,metal,rho_m=7950,rho_g=1,cp_g=520,latent_g=1):
        if any(not math.isfinite(x) for x in (rho_m,rho_g,cp_g,latent_g)) or min(rho_m,rho_g,cp_g)<=0 or latent_g<0:
            raise ValueError('Invalid mixture properties')
        self.m,self.rm,self.rg,self.cg,self.lg=metal,rho_m,rho_g,cp_g,latent_g
    @staticmethod
    def fraction(x):
        if not math.isfinite(x) or not 0<=x<=1:raise ValueError('Invalid fraction')
    def rho(self,a):
        self.fraction(a);return a*self.rm+(1-a)*self.rg
    def capacity(self,a):
        r=self.rho(a);filtered=0 if a<.01 else 1 if a>.99 else a
        return r*(filtered*self.m.latent+(1-filtered)*self.lg)
    def epsilon(self,a,inventory):
        cap=self.capacity(a)
        if not math.isfinite(inventory) or not 0<=inventory<=cap:raise ValueError('Incompatible latent inventory')
        return inventory/cap if cap else 0
    def density(self,t,a,e):
        self.fraction(e)
        return self.rho(a)*(a*self.m.sensible(t)+(1-a)*self.cg*t)+self.capacity(a)*e
    def temperature(self,energy,a,e):
        self.fraction(e);r=self.rho(a);latent=self.capacity(a)*e
        if not math.isfinite(energy) or energy<latent:raise ValueError('Insufficient energy')
        # Independent analytic sensible inverse with effective cp endpoints.
        sensible=MetalEnthalpy(self.m.ts,self.m.tl,a*self.m.cs+(1-a)*self.cg,
                              a*self.m.cl+(1-a)*self.cg,1)
        h=(energy-latent)/r;hs=sensible.sensible(sensible.ts);hl=sensible.sensible(sensible.tl)
        if h<=hs:return h/sensible.cs
        if h>=hl:return sensible.tl+(h-hl)/sensible.cl
        qa=.5*(sensible.cl-sensible.cs)/(sensible.tl-sensible.ts);qb=sensible.cs;qc=hs-h
        return sensible.ts+(-qc/qb if qa==0 else -2*qc/(qb+math.sqrt(qb*qb-4*qa*qc)))


class CapacityEnthalpy:
    """Persistent volume capacity moments, independent analytic inverse."""
    def __init__(self,ts,tl,cs,cl,capacity):
        self.s=MetalEnthalpy(ts,tl,cs,cl,1)
        if not math.isfinite(capacity) or capacity<0:raise ValueError('Invalid mapped capacity')
        self.capacity=capacity
    def epsilon(self,inventory):
        if not math.isfinite(inventory) or not 0<=inventory<=self.capacity:
            raise ValueError('Inventory exceeds mapped capacity')
        return inventory/self.capacity if self.capacity else 0
    def density(self,t,inventory):
        self.epsilon(inventory);return self.s.sensible(t)+inventory
    def temperature(self,energy,inventory):
        self.epsilon(inventory)
        if not math.isfinite(energy) or energy<inventory:raise ValueError('Energy below inventory')
        h=energy-inventory;hs=self.s.sensible(self.s.ts);hl=self.s.sensible(self.s.tl)
        if h<=hs:return h/self.s.cs
        if h>=hl:return self.s.tl+(h-hl)/self.s.cl
        a=.5*(self.s.cl-self.s.cs)/(self.s.tl-self.s.ts);b=self.s.cs;c=hs-h
        return self.s.ts+(-c/b if a==0 else -2*c/(b+math.sqrt(b*b-4*a*c)))


def remap_capacity_state(transfer,energy,alpha,inventory,cs,cl,capacity,ts=1537,tl=1631):
    """Use stored moments after initialization; no regeneration from mapped alpha."""
    arrays=[transfer.gather_density(x) for x in (energy,alpha,inventory,cs,cl,capacity)]
    temperatures=[];fractions=[]
    for en,a,inv,s,l,cap in zip(*arrays):
        MixtureEnthalpy.fraction(a)
        closure=CapacityEnthalpy(ts,tl,s,l,cap)
        temperatures.append(closure.temperature(en,inv));fractions.append(closure.epsilon(inv))
    return dict(zip(('energy','alpha','inventory','cs','cl','capacity'),arrays),temperature=temperatures,epsilon=fractions)
