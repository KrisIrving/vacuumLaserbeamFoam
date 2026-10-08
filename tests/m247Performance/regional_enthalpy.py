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
