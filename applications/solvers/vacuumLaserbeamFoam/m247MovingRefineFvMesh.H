// Experimental opt-in moving mesh. No change to static-case behavior.
#ifndef m247MovingRefineFvMesh_H
#define m247MovingRefineFvMesh_H
#include "dynamicRefineFvMesh.H"
#include "addToRunTimeSelectionTable.H"
#include "interpolationTable.H"
#include <cmath>
namespace Foam
{
class m247MovingRefineFvMesh : public dynamicRefineFvMesh
{
    autoPtr<volScalarField> mask_;
    autoPtr<volScalarField> hold_;
    autoPtr<interpolationTable<vector>> position_;
    label lastIndex_=-1;
protected:
    void selectRefineCandidates(const scalar lower,const scalar upper,
        const scalarField& values,bitSet& candidates) const override
    {
        if (!(lower>0 && lower<1 && upper>1) || values.size()!=nCells())
            FatalErrorInFunction<<"Invalid binary mask controls"<<exit(FatalError);
        candidates=bitSet(nCells());
        forAll(values,i)
        {
            if (values[i]!=0 && values[i]!=1)
                FatalErrorInFunction<<"Mask must be binary"<<exit(FatalError);
            if (values[i]==1)candidates.set(i);
        }
    }
public:
    TypeName("m247MovingRefineFvMesh");
    explicit m247MovingRefineFvMesh(const IOobject& io,const bool doInit=true)
    : dynamicRefineFvMesh(io,false)
    {
        if (doInit)dynamicRefineFvMesh::init(true);
    }
    void initializeMaskState()
    {
        // Read persisted hold at restart time, before Time is incremented.
        if (mask_.valid())return;
        mask_.reset(new volScalarField(IOobject("m247RefineMask",time().timeName(),*this,
            IOobject::NO_READ,IOobject::NO_WRITE),*this,dimensionedScalar("zero",dimless,0),"zeroGradient"));
        hold_.reset(new volScalarField(IOobject("m247WakeHold",time().timeName(),*this,
            IOobject::READ_IF_PRESENT,IOobject::AUTO_WRITE),*this,dimensionedScalar("zero",dimless,0),"zeroGradient"));
    }
    void reportPilotState() const
    {
        const auto& alpha=lookupObject<volScalarField>("alpha.metal");
        const auto& T=lookupObject<volScalarField>("T");
        const auto& eps=lookupObject<volScalarField>("epsilon1");
        const auto& U=lookupObject<volVectorField>("U");
        const tmp<volScalarField> tDiv=fvc::div(lookupObject<surfaceScalarField>("phi"));
        const auto& div=tDiv();
        label invalid=0;scalar amin=GREAT,amax=-GREAT,emin=GREAT,emax=-GREAT;
        scalar tmin=GREAT,tmax=-GREAT,umax=0,divL1=0,volume=0,divMax=0;
        forAll(T,i)
        {
            if (!std::isfinite(T[i])||!std::isfinite(alpha[i])||!std::isfinite(eps[i])
                ||!std::isfinite(mag(U[i]))||!std::isfinite(div[i]))++invalid;
            amin=min(amin,alpha[i]);amax=max(amax,alpha[i]);emin=min(emin,eps[i]);emax=max(emax,eps[i]);
            tmin=min(tmin,T[i]);tmax=max(tmax,T[i]);umax=max(umax,mag(U[i]));
            volume+=V()[i];divL1+=V()[i]*mag(div[i]);divMax=max(divMax,mag(div[i]));
        }
        reduce(invalid,sumOp<label>());reduce(amin,minOp<scalar>());reduce(amax,maxOp<scalar>());
        reduce(emin,minOp<scalar>());reduce(emax,maxOp<scalar>());reduce(tmin,minOp<scalar>());
        reduce(tmax,maxOp<scalar>());reduce(umax,maxOp<scalar>());reduce(divL1,sumOp<scalar>());
        reduce(volume,sumOp<scalar>());reduce(divMax,maxOp<scalar>());
        const auto precision=Info().precision();Info().precision(17);
        Info<<"M247_MOVING_CFD_STATE schema=1 time="<<time().value()
            <<" alphaMin="<<amin<<" alphaMax="<<amax<<" epsilonMin="<<emin<<" epsilonMax="<<emax
            <<" Tmin="<<tmin<<" Tmax="<<tmax<<" Umax="<<umax
            <<" divL1="<<divL1/volume<<" divMax="<<divMax<<" invalid="<<invalid<<endl;
        Info().precision(precision);
        if (invalid||amin<-1e-8||amax>1+1e-8||emin<-1e-8||emax>1+1e-8||tmin<=0)
            FatalErrorInFunction<<"Invalid moving-CFD final-step fields"<<exit(FatalError);
    }
    bool update() override
    {
        if (lastIndex_==time().timeIndex())return false;
        lastIndex_=time().timeIndex();
        IOdictionary controls(IOobject("m247MovingWindowDict",time().system(),*this,
            IOobject::MUST_READ,IOobject::NO_WRITE));
        const scalar halfX=controls.get<scalar>("halfX");
        const scalar halfZ=controls.get<scalar>("halfZ");
        const scalar hot=controls.get<scalar>("hotTemperature");
        const scalar release=controls.get<scalar>("releaseTemperature");
        const scalar liquid=controls.get<scalar>("liquidThreshold");
        const scalar solid=controls.get<scalar>("solidThreshold");
        const scalar metal=controls.get<scalar>("metalThreshold");
        if (!std::isfinite(halfX)||!std::isfinite(halfZ)||halfX<=0||halfZ<=0
            ||!std::isfinite(hot)||!std::isfinite(release)||release<=0||release>=hot
            ||!std::isfinite(liquid)||!std::isfinite(solid)||solid<0||solid>=liquid||liquid>1
            ||!std::isfinite(metal)||metal<=0||metal>=1)
            FatalErrorInFunction<<"Invalid moving wake controls"<<exit(FatalError);
        const auto& alpha=lookupObject<volScalarField>("alpha.metal");
        const auto& T=lookupObject<volScalarField>("T");
        const auto& eps=lookupObject<volScalarField>("epsilon1");
        if (!mask_.valid() || !hold_.valid())
            FatalErrorInFunction<<"Moving mask must initialize at restart time"<<exit(FatalError);
        if (!position_.valid())
        {
            IOdictionary laser(IOobject("LaserProperties",time().constant(),*this,
                IOobject::MUST_READ,IOobject::NO_WRITE,false));
            if (!laser.found("timeVsLaserPosition"))
                FatalErrorInFunction<<"Pilot supports one laser table only"<<exit(FatalError);
            position_.reset(new interpolationTable<vector>(laser.subDict("timeVsLaserPosition")));
        }
        const vector centre=(*position_)(time().value());
        label invalid=0,requested=0,wake=0;
        forAll(T,i)
        {
            if (!std::isfinite(T[i])||!std::isfinite(alpha[i])||!std::isfinite(eps[i])||!std::isfinite((*hold_)[i])
                ||(*hold_)[i]<-1e-8||(*hold_)[i]>1+1e-8)++invalid;
            if (alpha[i]>metal && (T[i]>=hot || eps[i]>=liquid))(*hold_)[i]=1;
            else if (alpha[i]<=metal || (T[i]<release && eps[i]<=solid))(*hold_)[i]=0;
            const bool retained=(*hold_)[i]>0;
            if (retained)++wake;
            const vector& c=C()[i];
            const bool inside=mag(c.x()-centre.x())<=halfX && mag(c.z()-centre.z())<=halfZ;
            (*mask_)[i]=(inside||retained)?1:0;
            if ((*mask_)[i]==1)++requested;
        }
        reduce(invalid,sumOp<label>());
        if (invalid)FatalErrorInFunction<<"Nonfinite moving-mask state"<<exit(FatalError);
        mask_->correctBoundaryConditions();hold_->correctBoundaryConditions();
        const scalar beforeMetal=fvc::domainIntegrate(alpha).value();
        const scalar beforeThermal=fvc::domainIntegrate
            (lookupObject<volScalarField>("rho")*(lookupObject<volScalarField>("cp")*T
             +lookupObject<volScalarField>("LatentHeat")*eps)).value();
        if (curTimeIndex_<time().timeIndex())storeOldVol(V());
        const scalarField& old=V0();
        if (old.size()!=nCells())FatalErrorInFunction<<"Invalid V0 size"<<exit(FatalError);
        forAll(old,i)if (!std::isfinite(old[i]) || old[i]<=0)
            FatalErrorInFunction<<"Invalid pre-update old volume"<<exit(FatalError);
        const bool changed=dynamicRefineFvMesh::update();
        const auto& levels=meshCutter().cellLevel();
        label missed=0,afterWake=0;
        forAll(T,i)if ((*hold_)[i]>0)
        { ++afterWake;if (levels[i]!=1)++missed; }
        reduce(missed,sumOp<label>());reduce(afterWake,sumOp<label>());
        reduce(requested,sumOp<label>());reduce(wake,sumOp<label>());
        const scalar afterMetal=fvc::domainIntegrate(alpha).value();
        const scalar afterThermal=fvc::domainIntegrate
            (lookupObject<volScalarField>("rho")*(lookupObject<volScalarField>("cp")*T
             +lookupObject<volScalarField>("LatentHeat")*eps)).value();
        const auto precision=Info().precision();Info().precision(17);
        Info<<"M247_MOVING_CFD schema=1 time="<<time().value()
            <<" cells="<<returnReduce(nCells(),sumOp<label>())<<" changed="<<label(changed)
            <<" centreX="<<centre.x()<<" centreZ="<<centre.z()
            <<" requested="<<requested<<" wakeBefore="<<wake<<" wakeAfter="<<afterWake
            <<" wakeMissed="<<missed<<" metalBefore="<<beforeMetal<<" metalAfter="<<afterMetal
            <<" thermalProxyBefore="<<beforeThermal<<" thermalProxyAfter="<<afterThermal<<endl;
        Info().precision(precision);
        if (!std::isfinite(afterMetal)||!std::isfinite(afterThermal)||beforeMetal<=0||beforeThermal<=0
            ||mag(afterMetal/beforeMetal-1)>1e-6||mag(afterThermal/beforeThermal-1)>1e-6)
            FatalErrorInFunction<<"Experimental moving mapping screen failed"<<exit(FatalError);
        if (missed)FatalErrorInFunction<<"Moving wake refinement incomplete"<<exit(FatalError);
        return changed;
    }
};
defineTypeNameAndDebug(m247MovingRefineFvMesh,0);
addToRunTimeSelectionTable(dynamicFvMesh,m247MovingRefineFvMesh,IOobject);
addToRunTimeSelectionTable(dynamicFvMesh,m247MovingRefineFvMesh,doInit);
}
#endif
