// Serial geometry/restart moment check; no equations or field writes.
#include "fvCFD.H"
#include <cmath>
using namespace Foam;
int main(int argc,char *argv[])
{
    argList::noParallel();
    argList::noFunctionObjects();
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"
    volScalarField T(IOobject("T",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField alpha(IOobject("alpha.metal",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField epsilon(IOobject("epsilon1",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    scalar volume=0,metalVolume=0,liquidVolume=0,metalTemperatureMoment=0;
    scalar amin=GREAT,amax=-GREAT,emin=GREAT,emax=-GREAT,tmin=GREAT,tmax=-GREAT;
    forAll(T,i)
    {
        const scalar v=mesh.V()[i],a=alpha[i],e=epsilon[i],t=T[i];
        if (!std::isfinite(v)||v<=0||!std::isfinite(a)||!std::isfinite(e)||!std::isfinite(t))
            FatalErrorInFunction<< "Invalid field/volume" << exit(FatalError);
        volume+=v;metalVolume+=v*a;liquidVolume+=v*a*e;
        metalTemperatureMoment+=v*a*t;
        amin=min(amin,a);amax=max(amax,a);emin=min(emin,e);emax=max(emax,e);
        tmin=min(tmin,t);tmax=max(tmax,t);
    }
    Info().precision(17);
    Info<< "M247_MESH_MOMENTS schema=1 time=" << runTime.value()
        << " cells=" << mesh.nCells() << " volume=" << volume
        << " metalVolume=" << metalVolume << " liquidVolume=" << liquidVolume
        << " metalTemperatureMoment=" << metalTemperatureMoment
        << " alphaMin=" << amin << " alphaMax=" << amax
        << " epsilonMin=" << emin << " epsilonMax=" << emax
        << " Tmin=" << tmin << " Tmax=" << tmax << endl;
    Info<< "End" << endl;
    return 0;
}
