"""Independent analytic checks and acceptance contract rejection tests."""
import math
import tempfile
import unittest
from pathlib import Path
from regional_acceptance import prepare_physics_fixture, parse_physics


class Equilibrium:
    # Analytic inverse independent of the native bisection implementation.
    def __init__(self, cs=6280500, cl=6837000, latent=1192500000):
        self.cs,self.cl,self.latent=cs,cl,latent
        self.ts,self.tl=1537,1631
    def fraction(self,t):return min(1,max(0,(t-self.ts)/(self.tl-self.ts)))
    def energy(self,t):
        x=min(max(t-self.ts,0),self.tl-self.ts)
        sensible=self.cs*min(t,self.ts)+self.cs*x+.5*(self.cl-self.cs)*x*x/(self.tl-self.ts)+self.cl*max(t-self.tl,0)
        return sensible+self.latent*self.fraction(t)
    def temperature(self,e):
        if e<0 or not math.isfinite(e):raise ValueError('Invalid energy')
        low=self.cs*self.ts; high=self.energy(self.tl)
        if e<=low:return e/self.cs
        if e>=high:return self.tl+(e-high)/self.cl
        b=self.cs+self.latent/(self.tl-self.ts)
        slope=(self.cl-self.cs)/(self.tl-self.ts)
        delta=e-low
        return self.ts+2*delta/(b+math.sqrt(b*b+2*slope*delta))


def two_cells(a,b,dt,conductance):
    """Solve a conservative implicit heat exchange by a bounded scalar root."""
    h=Equilibrium()
    ea,eb=h.energy(a),h.energy(b)
    lo,hi=0,ea+eb
    for _ in range(120):
        e=(lo+hi)/2
        residual=e-ea+dt*conductance*(h.temperature(e)-h.temperature(ea+eb-e))
        if residual>0:hi=e
        else:lo=e
    new=(lo+hi)/2
    return h.temperature(new),h.temperature(ea+eb-new)


def cycle_log():
    out=[]
    initial=3.0
    for i in range(1,21):
        source=.1*(i if i<=10 else 20-i)
        liquid=i/10 if i<=10 else (20-i)/10
        out.append(f'M247_THERMAL_TRANSPORT schema=1 step={i} Tmin=1500 Tmax=1700 initialEnergyJ={initial} energyJ={initial+source} cumulativeBoundaryOutJ=0 cumulativeSourceJ={source} residualJ=0 inverseRelativeError=1e-16 phaseRelaxation=1 conduction=1 productionApproved=0')
        out.append(f'M247_CONDUCTION_PHASE schema=1 time={i*1e-5} correctors=3 energyRelativeError=1e-12 liquidMin=0 liquidMax={liquid} liquidCapacityFraction={liquid} latentRedistributedJ=.01 conductionRedistributedJ=.001 conductiveBoundaryOutJ=0 productionApproved=0')
    return '\n'.join(out)


class RegionalPhysicsTests(unittest.TestCase):
    def test_ubuntu_entrypoint_has_lf_shebang(self):
        wrapper=Path(__file__).with_name("RunRegionalAcceptance").read_bytes()
        self.assertTrue(wrapper.startswith(b"#!/bin/bash\n"))
        self.assertNotIn(b"\r",wrapper)
        attributes=Path(__file__).resolve().parents[2]/".gitattributes"
        self.assertIn("* text=auto eol=lf",attributes.read_text(encoding="utf-8"))

    def test_equilibrium_inverse_and_latent_plateau(self):
        for closure in (Equilibrium(),Equilibrium(520,520,1),Equilibrium(latent=0)):
            for t in (0,1500,1537,1537.001,1580,1630.999,1631,2000,4500):
                self.assertAlmostEqual(closure.temperature(closure.energy(t)),t,places=9)
        h=Equilibrium()
        self.assertGreater(h.energy(1631)-h.energy(1537),h.latent)
    def test_phase_relaxation_preserves_energy(self):
        h=Equilibrium()
        energy=h.energy(1500)+h.latent
        t=h.temperature(energy)
        self.assertTrue(1537<t<1631)
        self.assertAlmostEqual(h.energy(t)/energy,1,places=14)
    def test_heat_cool_cycle(self):
        h=Equilibrium();e=h.energy(1500)
        peak=h.temperature(e+10*3e13*1e-5)
        self.assertGreater(peak,1631)
        self.assertAlmostEqual(h.temperature(e+10*3e13*1e-5-10*3e13*1e-5),1500,places=10)
    def test_implicit_conduction_crosses_phase_and_conserves(self):
        h=Equilibrium();a,b=two_cells(1800,1450,1e-5,3e13)
        self.assertTrue(1450<b<a<1800)
        self.assertAlmostEqual((h.energy(a)+h.energy(b))/(h.energy(1800)+h.energy(1450)),1,places=14)
        self.assertTrue(0<h.fraction(b)<1)
    def test_fixture_integrated_cycle_and_processor_ready(self):
        with tempfile.TemporaryDirectory() as temp:
            case=Path(temp)/'case';prepare_physics_fixture(case)
            self.assertIn('regionalThermophysics true',(case/'constant/regionalTransferDict').read_text())
            self.assertIn('uniform 1500',(case/'0/thermalRegion/T').read_text())
            self.assertIn('epsilon1 0',(case/'system/thermalRegion/setFieldsDict').read_text())
            self.assertIn('regional.*',(case/'system/flowRegion/fvSolution').read_text())
            self.assertIn('zeroGradient',(case/'0/flowRegion/regionalTemperature').read_text())
    def test_cycle_acceptance(self):self.assertEqual(len(parse_physics(cycle_log())['phase']),20)
    def test_reject_missing_conduction_no_freezing_bad_ledger(self):
        text=cycle_log()
        for bad in (text.replace('conductionRedistributedJ=.001','conductionRedistributedJ=0'),text.replace('liquidCapacityFraction=0.0 ','liquidCapacityFraction=1 '),text.replace('energyRelativeError=1e-12','energyRelativeError=1e-4'),text.replace('conductiveBoundaryOutJ=0','conductiveBoundaryOutJ=.1'),text.replace('phaseRelaxation=1','phaseRelaxation=0'),text.replace('energyJ=3.1','energyJ=4.1')):
            with self.subTest(bad=bad[-200:]),self.assertRaises(ValueError):parse_physics(bad)
    def test_invalid_equilibrium_energy(self):
        for e in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):Equilibrium().temperature(e)


if __name__=='__main__':unittest.main()
