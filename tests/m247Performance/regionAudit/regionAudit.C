// Read-only cell/volume envelopes; no solver equations or field writes.
#include "fvCFD.H"
#include "timeSelector.H"
#include <cmath>

using namespace Foam;

struct regionEnvelope
{
    label cells=0;
    scalar volume=0;
    point lo=point(GREAT,GREAT,GREAT), hi=point(-GREAT,-GREAT,-GREAT);

    void add(const label celli, const fvMesh& mesh)
    {
        ++cells;
        volume+=mesh.V()[celli];
        const cell& faces=mesh.cells()[celli];
        forAll(faces,i)
        {
            const face& vertices=mesh.faces()[faces[i]];
            forAll(vertices,j)
            {
                const point& p=mesh.points()[vertices[j]];
                for (label d=0;d<3;++d)
                {
                    lo[d]=min(lo[d],p[d]); hi[d]=max(hi[d],p[d]);
                }
            }
        }
    }

    void report(const scalar time, const label region)
    {
        reduce(cells,sumOp<label>()); reduce(volume,sumOp<scalar>());
        for (label d=0;d<3;++d)
        {
            reduce(lo[d],minOp<scalar>()); reduce(hi[d],maxOp<scalar>());
        }
        if (!cells) lo=hi=point::zero;
        Info<< "M247_REGION schema=1 time=" << time << " region=" << region
            << " cells=" << cells << " volume=" << volume
            << " xmin=" << lo.x() << " xmax=" << hi.x()
            << " ymin=" << lo.y() << " ymax=" << hi.y()
            << " zmin=" << lo.z() << " zmax=" << hi.z() << endl;
    }
};

int main(int argc, char *argv[])
{
    timeSelector::addOptions();
    #include "setRootCase.H"
    #include "createTime.H"
    const instantList times=timeSelector::select0(runTime,args);
    if (times.empty())
        FatalErrorInFunction<< "No selected snapshots" << exit(FatalError);
    runTime.setTime(times[0],0);
    #include "createMesh.H"
    IOdictionary material(IOobject("transportProperties",runTime.constant(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE));
    const scalar solidus=readScalar(material.subDict("metal").lookup("Tsolidus"));
    const scalar liquidus=readScalar(material.subDict("metal").lookup("Tliquidus"));
    Info().precision(17);
    Info<< "M247_REGION_CONFIG schema=1 liquidus=" << liquidus << " solidus=" << solidus
        << " alphaMin=0.01 metalMin=0.5 epsilonMin=0.01 fastSpeed=1"
        << " thermalThreshold=1368.15" << endl;

    forAll(times,ti)
    {
        runTime.setTime(times[ti],ti);
        if (mesh.readUpdate()!=polyMesh::UNCHANGED)
            FatalErrorInFunction<< "Audit requires a fixed mesh" << exit(FatalError);
        volScalarField T(IOobject("T",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        volScalarField alpha(IOobject("alpha.metal",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        volScalarField epsilon(IOobject("epsilon1",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        volVectorField U(IOobject("U",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
        // 0 mesh, 1 molten metal, 2 active CFD proxy, 3 warm metal,
        // 4 hot gas, 5 fast material. Proxies do not define future equations.
        regionEnvelope regions[6];
        label invalid=0,alphaBounds=0,epsilonBounds=0;
        scalar metalTmax=-GREAT,allTmax=-GREAT,Umax=0,liquidVolume=0;
        forAll(T,celli)
        {
            const scalar t=T[celli],a=alpha[celli],e=epsilon[celli],u=mag(U[celli]);
            const scalar vol=mesh.V()[celli];
            if (!std::isfinite(t)||!std::isfinite(a)||!std::isfinite(e)
                ||!std::isfinite(u)||!std::isfinite(vol)||vol<=0)
            { ++invalid; continue; }
            regions[0].add(celli,mesh);
            allTmax=max(allTmax,t); Umax=max(Umax,u);
            alphaBounds+=label(a < -1e-8 || a > 1+1e-8);
            epsilonBounds+=label(e < -1e-8 || e > 1+1e-8);
            if (a>=0.5) metalTmax=max(metalTmax,t);
            liquidVolume+=vol*a*e;
            if (a>=0.5 && t>=liquidus) regions[1].add(celli,mesh);
            if (a>=0.01 && (e>=0.01 || (a<0.99 && t>=solidus))) regions[2].add(celli,mesh);
            if (a>=0.5 && t>=1368.15) regions[3].add(celli,mesh);
            if (a<0.01 && t>=liquidus) regions[4].add(celli,mesh);
            if (a>=0.01 && u>=1) regions[5].add(celli,mesh);
        }
        reduce(invalid,sumOp<label>()); reduce(alphaBounds,sumOp<label>());
        reduce(epsilonBounds,sumOp<label>()); reduce(metalTmax,maxOp<scalar>());
        reduce(allTmax,maxOp<scalar>()); reduce(Umax,maxOp<scalar>());
        reduce(liquidVolume,sumOp<scalar>());
        if (invalid)
            FatalErrorInFunction<< "Invalid field/volume cells=" << invalid << exit(FatalError);
        Info<< "M247_REGION_STATE schema=1 time=" << runTime.value()
            << " ranks=" << Pstream::nProcs() << " invalid=" << invalid
            << " alphaBounds=" << alphaBounds << " epsilonBounds=" << epsilonBounds
            << " metalTmax=" << metalTmax << " Tmax=" << allTmax
            << " Umax=" << Umax << " liquidVolume=" << liquidVolume << endl;
        for (label r=0;r<6;++r) regions[r].report(runTime.value(),r);
    }
    Info<< "End" << endl;
    return 0;
}
