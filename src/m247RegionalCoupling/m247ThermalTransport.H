// Conservative transported moments with optional implicit conduction/phase closure.
#ifndef m247ThermalTransport_H
#define m247ThermalTransport_H
#include "m247RegionalState.H"
#include "m247ConductionPhase.H"
#include <initializer_list>
namespace Foam
{
class m247ThermalTransport
{
    fvMesh& mesh_;
    dictionary controls_;
    bool physics_;
    autoPtr<volScalarField> temperature_;
    scalar ts_,tl_;
    volScalarField sensible_,latent_,reserve_,cs_,cl_,source_;
    scalar cumulativeSource_=0,maxResidual_=0,initialEnergy_=0,cumulativeBoundary_=0;
    scalar integral(const volScalarField& f) const
    {scalar total=0;forAll(f,i)total+=f[i]*mesh_.V()[i];reduce(total,sumOp<scalar>());return total;}
    scalar transport(volScalarField& f,const surfaceScalarField& phi,scalar dt,bool heating)
    {
        const scalar before=integral(f);
        volScalarField rhs(IOobject("regionalTransportRHS",mesh_.time().timeName(),mesh_,IOobject::NO_READ,IOobject::NO_WRITE),
            mesh_,dimensionedScalar("zero",f.dimensions()/dimTime,0));
        if(heating)rhs=source_;
        fvScalarMatrix equation(fvm::ddt(f)+fvm::div(phi,f)==rhs);
        equation.solve();
        const surfaceScalarField flux(equation.flux());
        scalar boundary=0;
        forAll(mesh_.boundary(),p)if(!mesh_.boundary()[p].coupled())
            forAll(flux.boundaryField()[p],i)boundary+=flux.boundaryField()[p][i];
        reduce(boundary,sumOp<scalar>());boundary*=dt;
        const scalar added=heating?dt*integral(source_):0;
        const scalar residual=mag(integral(f)-before+boundary-added);
        if(!std::isfinite(residual)||residual>1e-8*max(mag(before)+mag(boundary)+mag(added),scalar(1e-20)))
            FatalErrorInFunction<<"Thermodynamic moment transport ledger failed: "<<f.name()<<exit(FatalError);
        if(heating){cumulativeSource_+=added;maxResidual_=max(maxResidual_,residual);}
        forAll(f,i)if(!std::isfinite(f[i])||f[i]<0)
            FatalErrorInFunction<<"Negative/nonfinite transported moment: "<<f.name()<<exit(FatalError);
        return boundary;
    }
public:
    m247ThermalTransport(fvMesh& thermal,fvMesh& mesh,Time& time,const dictionary& c)
    :mesh_(mesh),controls_(c),physics_(c.getOrDefault<bool>("regionalThermophysics",false)),ts_(c.get<scalar>("Tsolidus")),tl_(c.get<scalar>("Tliquidus")),
     sensible_(IOobject("regionalSensible",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh),
     latent_(IOobject("regionalLatent",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh),
     reserve_(IOobject("regionalLatentReserve",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh),
     cs_(IOobject("regionalCs",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh),
     cl_(IOobject("regionalCl",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh),
     source_(IOobject("regionalHeatGain",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh)
    {
        const dimensionSet energy(1,-1,-2,0,0,0,0),capacity(1,-1,-2,-1,0,0,0);
        if(sensible_.dimensions()!=energy||latent_.dimensions()!=energy||reserve_.dimensions()!=energy
            ||cs_.dimensions()!=capacity||cl_.dimensions()!=capacity||source_.dimensions()!=energy/dimTime)
            FatalErrorInFunction<<"Invalid thermodynamic moment dimensions"<<exit(FatalError);
        volScalarField T(IOobject("T",time.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
        volScalarField a(IOobject("alpha.metal",time.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
        volScalarField e(IOobject("epsilon1",time.timeName(),thermal,IOobject::MUST_READ,IOobject::NO_WRITE),thermal);
        if(T.dimensions()!=dimTemperature||a.dimensions()!=dimless||e.dimensions()!=dimless)
            FatalErrorInFunction<<"Invalid thermal import field dimensions"<<exit(FatalError);
        m247MixtureEnthalpy m(ts_,tl_,c.get<scalar>("cpSolidus"),c.get<scalar>("cpLiquidus"),c.get<scalar>("LatentHeat"),c.get<scalar>("rho"),c.get<scalar>("rhoGas"),c.get<scalar>("cpGas"),c.get<scalar>("LatentHeatGas"));
        scalarField sensible(a.size()),latent(a.size()),reserve(a.size()),cs(a.size()),cl(a.size());
        forAll(a,i)
        {
            latent[i]=m.latentDensity(a[i],e[i]);reserve[i]=m.capacity(a[i])*(1-e[i]);
            sensible[i]=m.density(T[i],a[i],e[i])-latent[i];
            cs[i]=m.sensibleSolidCapacity(a[i]);cl[i]=m.sensibleLiquidCapacity(a[i]);
        }
        m247RegionalTransfer mapping(thermal,mesh);
        sensible_.primitiveFieldRef()=mapping.gatherDensity(sensible);
        latent_.primitiveFieldRef()=mapping.gatherDensity(latent);
        reserve_.primitiveFieldRef()=mapping.gatherDensity(reserve);
        cs_.primitiveFieldRef()=mapping.gatherDensity(cs);cl_.primitiveFieldRef()=mapping.gatherDensity(cl);
        for(volScalarField* f:{&sensible_,&latent_,&reserve_,&cs_,&cl_})
        {f->correctBoundaryConditions();f->oldTime();mesh_.setFluxRequired(f->name());}
        forAll(source_,i)if(!std::isfinite(source_[i]))FatalErrorInFunction<<"Invalid heat source"<<exit(FatalError);
        initialEnergy_=integral(sensible_)+integral(latent_);
        if(physics_)
        {
            temperature_.reset(new volScalarField(IOobject("regionalTemperature",time.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh));
            if(temperature_().dimensions()!=dimTemperature)FatalErrorInFunction<<"Invalid local temperature dimensions"<<exit(FatalError);
        }
    }
    void advance(const surfaceScalarField& phi,scalar dt,label step)
    {
        if(physics_)
        {
            // Manufactured cycle only: material-scaled heating then cooling.
            const scalar rate=controls_.get<scalar>("cycleHeatRate"),reference=controls_.get<scalar>("cycleReferenceCapacity");
            if(!std::isfinite(rate)||rate<=0||!std::isfinite(reference)||reference<=0)
                FatalErrorInFunction<<"Invalid manufactured heat cycle controls"<<exit(FatalError);
            const scalar sign=step<=10?1:-1;
            forAll(source_,i)source_[i]=sign*rate*cs_[i]/reference;
        }
        cumulativeBoundary_+=transport(sensible_,phi,dt,true);
        cumulativeBoundary_+=transport(latent_,phi,dt,false);
        transport(reserve_,phi,dt,false);transport(cs_,phi,dt,false);transport(cl_,phi,dt,false);
        if(physics_)
        {
            scalarField energy(sensible_.size()),capacity(sensible_.size());
            forAll(energy,i){energy[i]=sensible_[i]+latent_[i];capacity[i]=latent_[i]+reserve_[i];}
            cumulativeBoundary_+=m247ConductionPhase(temperature_(),cs_,cl_,capacity,energy,ts_,tl_,dt,controls_,
                sensible_.primitiveFieldRef(),latent_.primitiveFieldRef(),reserve_.primitiveFieldRef());
            for(volScalarField* f:{&sensible_,&latent_,&reserve_})f->correctBoundaryConditions();
        }
        scalar lo=GREAT,hi=-GREAT,maxInverse=0;
        forAll(sensible_,i)
        {
            const m247CapacityEnthalpy closure(ts_,tl_,cs_[i],cl_[i],latent_[i]+reserve_[i]);
            const scalar energy=sensible_[i]+latent_[i],t=closure.temperature(energy,latent_[i]);
            lo=min(lo,t);hi=max(hi,t);
            maxInverse=max(maxInverse,mag(closure.density(t,latent_[i])-energy)/max(energy,scalar(1)));
        }
        reduce(lo,minOp<scalar>());reduce(hi,maxOp<scalar>());reduce(maxInverse,maxOp<scalar>());
        const scalar energy=integral(sensible_)+integral(latent_);
        const scalar residual=mag(energy-initialEnergy_+cumulativeBoundary_-cumulativeSource_);
        if(residual>1e-8*max(initialEnergy_,scalar(1e-20))||maxInverse>1e-10)
            FatalErrorInFunction<<"Cumulative regional thermal transport ledger failed"<<exit(FatalError);
        Info().precision(17);
        Info<<"M247_THERMAL_TRANSPORT schema=1 step="<<step<<" Tmin="<<lo<<" Tmax="<<hi
            <<" initialEnergyJ="<<initialEnergy_<<" energyJ="<<energy<<" cumulativeBoundaryOutJ="<<cumulativeBoundary_
            <<" cumulativeSourceJ="<<cumulativeSource_<<" residualJ="<<residual
            <<" maxStepResidualJ="<<maxResidual_<<" inverseRelativeError="<<maxInverse
            <<" phaseRelaxation="<<physics_<<" conduction="<<physics_<<" productionApproved=0"<<endl;
    }
};
}
#endif
