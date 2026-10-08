// Disposable-case topology/mapping prototype. No thermal/VOF/flow equations.
#include "fvCFD.H"
#include "dynamicFvMesh.H"
#include "dynamicRefineFvMesh.H"
#include <chrono>
#include <cmath>
using namespace Foam;

int main(int argc,char *argv[])
{
    argList::noParallel();
    argList::noFunctionObjects();
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createDynamicFvMesh.H"
    dynamicRefineFvMesh& refiner=refCast<dynamicRefineFvMesh>(mesh);
    IOdictionary controls(IOobject("movingWindowAuditDict",runTime.system(),mesh,
        IOobject::MUST_READ,IOobject::NO_WRITE));
    const scalar physicalTime=runTime.value();
    const scalar halfX=controls.get<scalar>("halfX");
    const scalar halfZ=controls.get<scalar>("halfZ");
    const scalar margin=controls.get<scalar>("interiorMargin");
    const label maxCells=controls.get<label>("maxCells");
    const scalarList centres(controls.lookup("centres"));
    if (halfX<=margin || halfZ<=margin || centres.size()!=4 || maxCells<mesh.nCells())
        FatalErrorInFunction<< "Invalid moving window audit controls" << exit(FatalError);
    volScalarField T(IOobject("T",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField alpha(IOobject("alpha.metal",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField epsilon(IOobject("epsilon1",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    // Independently mapped product proxies expose nonlinear mapping loss.
    // These are not a thermodynamic enthalpy model or corrected restart fields.
    volScalarField metalT(IOobject("mappedMetalTemperature",runTime.timeName(),mesh,
        IOobject::NO_READ,IOobject::NO_WRITE),alpha*T);
    volScalarField liquid(IOobject("mappedLiquidFraction",runTime.timeName(),mesh,
        IOobject::NO_READ,IOobject::NO_WRITE),alpha*epsilon);
    volScalarField mask(IOobject("movingRefineMask",runTime.timeName(),mesh,
        IOobject::NO_READ,IOobject::NO_WRITE),mesh,dimensionedScalar("zero",dimless,0),"zeroGradient");
    Info().precision(17);
    label step=0;
    auto report=[&](scalar centre,scalar elapsed,bool changed)
    {
        scalar volume=0,metal=0,mappedT=0,mappedLiquid=0,directT=0,directLiquid=0;
        scalar amin=GREAT,amax=-GREAT,emin=GREAT,emax=-GREAT,tmin=GREAT,tmax=-GREAT;
        label fine=0,interior=0,covered=0;
        const labelList& levels=refiner.meshCutter().cellLevel();
        forAll(T,i)
        {
            const scalar v=mesh.V()[i],a=alpha[i],e=epsilon[i],t=T[i];
            if (!std::isfinite(v)||v<=0||!std::isfinite(a)||!std::isfinite(e)||!std::isfinite(t)
                ||!std::isfinite(metalT[i])||!std::isfinite(liquid[i]))
                FatalErrorInFunction<< "Invalid mapped fields" << exit(FatalError);
            volume+=v;metal+=v*a;mappedT+=v*metalT[i];mappedLiquid+=v*liquid[i];
            directT+=v*a*t;directLiquid+=v*a*e;
            amin=min(amin,a);amax=max(amax,a);emin=min(emin,e);emax=max(emax,e);
            tmin=min(tmin,t);tmax=max(tmax,t);if (levels[i]>0)++fine;
            const vector& c=mesh.C()[i];
            if (mag(c.x()-centre)<halfX-margin && mag(c.z())<halfZ-margin)
            { ++interior;if (levels[i]==1)++covered; }
        }
        Info<< "M247_MOVING_WINDOW schema=1 step="<<step
            << " physicalTime="<<physicalTime<<" auditTime="<<runTime.value()
            << " centreX="<<centre<<" changed="<<label(changed)
            << " cells="<<mesh.nCells()<<" fineCells="<<fine
            << " protectedCells="<<refiner.protectedCell().count()
            << " interiorCells="<<interior<<" coveredCells="<<covered
            << " updateWall_s="<<elapsed<<" volume="<<volume<<" metalVolume="<<metal
            << " mappedMetalTemperature="<<mappedT<<" mappedLiquidVolume="<<mappedLiquid
            << " directMetalTemperature="<<directT<<" directLiquidVolume="<<directLiquid
            << " alphaMin="<<amin<<" alphaMax="<<amax<<" epsilonMin="<<emin
            << " epsilonMax="<<emax<<" Tmin="<<tmin<<" Tmax="<<tmax<<endl;
        if (mesh.nCells()>maxCells)FatalErrorInFunction<< "Cell budget exceeded" <<exit(FatalError);
    };
    report(centres[0],0,false);
    forAll(centres,position)
    {
        // Two topology updates per position allow refinement and coarsening to settle.
        for (label pass=0;pass<2;++pass)
        {
            ++step;
            // Synthetic output slots, not physical elapsed time.
            runTime.setTime(physicalTime+step*1e-9,step);
            scalarField& values=mask.primitiveFieldRef();
            forAll(values,i)
            {
                const vector& c=mesh.C()[i];
                values[i]=(mag(c.x()-centres[position])<=halfX && mag(c.z())<=halfZ) ? 1 : 0;
            }
            mask.correctBoundaryConditions();
            const auto started=std::chrono::steady_clock::now();
            const bool changed=mesh.update();
            const scalar elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-started).count();
            report(centres[position],elapsed,changed);
            if (!mesh.write())FatalErrorInFunction<<"Mesh snapshot write failed"<<exit(FatalError);
        }
    }
    Info<< "M247_MOVING_WINDOW_END schema=1 updates="<<step<<" advancedPhysics=0"<<endl;
    Info<< "End" <<endl;
    return 0;
}
