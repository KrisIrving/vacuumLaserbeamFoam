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
    argList::addBoolOption("restart", "Read velocity and mapped fluxes; report continuity without writes");
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
    if (args.found("restart"))
    {
        const volVectorField U(IOobject("U",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        const surfaceScalarField phi(IOobject("phi",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        const surfaceScalarField alphaPhi(IOobject("alphaPhi0.metal",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        if (U.dimensions()!=dimensionSet(0,1,-1,0,0,0,0)
            || phi.dimensions()!=dimensionSet(0,3,-1,0,0,0,0)
            || alphaPhi.dimensions()!=phi.dimensions())
            FatalErrorInFunction<< "Unexpected restart velocity/flux dimensions" << exit(FatalError);
        const surfaceScalarField velocityPhi(fvc::flux(U));
        const volScalarField divergence(fvc::div(phi));
        scalar divL1=0,divSquare=0,divMax=0,divSigned=0,umax=0;
        forAll(U,i)
        {
            const scalar d=divergence[i],speed=mag(U[i]),v=mesh.V()[i];
            if (!std::isfinite(d)||!std::isfinite(speed))
                FatalErrorInFunction<< "Nonfinite restart velocity/divergence" << exit(FatalError);
            divL1+=v*mag(d);divSquare+=v*d*d;divMax=max(divMax,mag(d));
            divSigned+=v*d;umax=max(umax,speed);
        }
        scalar fluxDifference=0,velocityFluxAbs=0,alphaFluxAbs=0;
        label zeroInternalFluxFaces=0;
        auto addFlux=[&](const scalar p,const scalar vp,const scalar ap)
        {
            if (!std::isfinite(p)||!std::isfinite(vp)||!std::isfinite(ap))
                FatalErrorInFunction<< "Nonfinite restart surface flux" << exit(FatalError);
            fluxDifference+=mag(p-vp);velocityFluxAbs+=mag(vp);alphaFluxAbs+=mag(ap);
        };
        forAll(phi,i)
        {
            addFlux(phi[i],velocityPhi[i],alphaPhi[i]);
            if (phi[i]==0)++zeroInternalFluxFaces;
        }
        forAll(phi.boundaryField(),patchi)
        {
            forAll(phi.boundaryField()[patchi],i)
                addFlux(phi.boundaryField()[patchi][i],velocityPhi.boundaryField()[patchi][i],alphaPhi.boundaryField()[patchi][i]);
        }
        Info<< "M247_RESTART_FLUX schema=1 cells=" << mesh.nCells()
            << " divL1=" << divL1/volume << " divRMS=" << std::sqrt(divSquare/volume)
            << " divMax=" << divMax << " netFlux=" << divSigned << " Umax=" << umax
            << " velocityFluxDifference=" << fluxDifference << " velocityFluxAbs=" << velocityFluxAbs
            << " alphaFluxAbs=" << alphaFluxAbs << " internalFaces=" << mesh.nInternalFaces()
            << " zeroInternalFluxFaces=" << zeroInternalFluxFaces << endl;
    }
    Info<< "End" << endl;
    return 0;
}
