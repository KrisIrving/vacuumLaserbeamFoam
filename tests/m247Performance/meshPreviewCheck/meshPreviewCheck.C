// Serial geometry/restart moment check; no equations or field writes.
#include "fvCFD.H"
#include "cellSet.H"
#include <cmath>
using namespace Foam;
int main(int argc,char *argv[])
{
    argList::noParallel();
    argList::noFunctionObjects();
    argList::addBoolOption("concavity", "Diagnose checkMesh concaveCells without waiving quality");
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
    if (args.found("concavity"))
    {
        const cellSet selected(mesh,"concaveCells",IOobject::MUST_READ);
        scalar worst=0,relativeWorst=0;
        label aboveRelative1e9=0;
        vector lo(GREAT,GREAT,GREAT),hi(-GREAT,-GREAT,-GREAT);
        const labelList ids=selected.toc();
        forAll(ids,si)
        {
            const label ci=ids[si];
            if (ci<0 || ci>=mesh.nCells())
                FatalErrorInFunction<< "Invalid concave cell id" << exit(FatalError);
            scalar cellWorst=0;
            const labelList& vertices=mesh.cellPoints()[ci];
            const cell& faces=mesh.cells()[ci];
            forAll(vertices,vi)
            {
                const point& p=mesh.points()[vertices[vi]];
                for (direction cmpt=0;cmpt<3;++cmpt)
                {
                    lo[cmpt]=min(lo[cmpt],p[cmpt]);hi[cmpt]=max(hi[cmpt],p[cmpt]);
                }
                forAll(faces,fi)
                {
                    const label facei=faces[fi];
                    vector outward=mesh.faceAreas()[facei];
                    if (mesh.faceOwner()[facei]!=ci)outward=-outward;
                    const scalar area=mag(outward);
                    if (!(area>0))FatalErrorInFunction<< "Invalid face area" << exit(FatalError);
                    cellWorst=max(cellWorst,((p-mesh.faceCentres()[facei]) & outward)/area);
                }
            }
            const scalar relative=cellWorst/std::cbrt(mesh.V()[ci]);
            worst=max(worst,cellWorst);relativeWorst=max(relativeWorst,relative);
            if (relative>1e-9)++aboveRelative1e9;
        }
        if (ids.empty())lo=hi=vector::zero;
        Info<< "M247_MESH_CONCAVITY schema=1 count=" << ids.size()
            << " worstPlaneDistance=" << worst << " maxRelativePlaneDistance=" << relativeWorst
            << " aboveRelative1e9=" << aboveRelative1e9
            << " xmin=" << lo.x() << " xmax=" << hi.x()
            << " ymin=" << lo.y() << " ymax=" << hi.y()
            << " zmin=" << lo.z() << " zmax=" << hi.z() << endl;
    }
    Info<< "End" << endl;
    return 0;
}
