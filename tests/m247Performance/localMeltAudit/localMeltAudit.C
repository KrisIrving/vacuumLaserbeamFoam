// Native binary/ASCII snapshot reader. No field/mesh writes or CFD equations.
#include "fvCFD.H"
#include "timeSelector.H"
#include <fstream>
#include <iomanip>
#include <cmath>
using namespace Foam;
int main(int argc,char *argv[])
{
    argList::noParallel();argList::noFunctionObjects();timeSelector::addOptions();
    argList::addOption("output","file","Exclusive CSV snapshot output on a copied case");
    #include "setRootCase.H"
    #include "createTime.H"
    const instantList times=timeSelector::select0(runTime,args);
    if(times.size()!=1||!args.found("output"))FatalErrorInFunction<<"Select one time and -output"<<exit(FatalError);
    runTime.setTime(times[0],0);
    #include "createMesh.H"
    volScalarField T(IOobject("T",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField a(IOobject("alpha.metal",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField e(IOobject("epsilon1",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField p(IOobject("p_rgh",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volVectorField U(IOobject("U",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    const fileName output(args.get<fileName>("output"));
    std::ifstream existing(output.c_str());
    if(existing.good())FatalErrorInFunction<<"CSV output already exists"<<exit(FatalError);
    std::ofstream stream(output.c_str());stream<<std::setprecision(17);
    stream<<"x,y,z,volume,T,alpha,epsilon,Ux,Uy,Uz,p_rgh\n";
    forAll(T,i)
    {
        const vector c=mesh.C()[i],u=U[i];const scalar v=mesh.V()[i];
        if(!std::isfinite(T[i])||T[i]<=0||!std::isfinite(a[i])||a[i]<-1e-8||a[i]>1+1e-8
            ||!std::isfinite(e[i])||e[i]<-1e-8||e[i]>1+1e-8||!std::isfinite(mag(u))
            ||!std::isfinite(p[i])||!std::isfinite(v)||v<=0)
            FatalErrorInFunction<<"Invalid local-melt snapshot"<<exit(FatalError);
        stream<<c.x()<<','<<c.y()<<','<<c.z()<<','<<v<<','<<T[i]<<','<<a[i]<<','<<e[i]
            <<','<<u.x()<<','<<u.y()<<','<<u.z()<<','<<p[i]<<'\n';
    }
    stream.flush();if(!stream.good())FatalErrorInFunction<<"CSV output failed"<<exit(FatalError);
    scalar cutT=0,cutE=0,cutU=0;label cutFaces=0,activeCut=0;
    const label patch=mesh.boundaryMesh().findPatchID("localCut");
    if(patch>=0)
    {
        const labelUList& cells=mesh.boundary()[patch].faceCells();cutFaces=cells.size();
        forAll(cells,j)
        {
            const label i=cells[j];cutU=max(cutU,mag(U[i]));
            if(a[i]>=0.05){cutT=max(cutT,T[i]);cutE=max(cutE,e[i]);
                if(T[i]>=1487||e[i]>=1e-6||mag(U[i])>=1)++activeCut;}
        }
    }
    const boundBox bounds(mesh.points(),false);
    Info().precision(17);
    Info<<"M247_LOCAL_MELT_SNAPSHOT schema=1 time="<<runTime.value()<<" cells="<<mesh.nCells()
        <<" xmin="<<bounds.min().x()<<" xmax="<<bounds.max().x()
        <<" ymin="<<bounds.min().y()<<" ymax="<<bounds.max().y()
        <<" zmin="<<bounds.min().z()<<" zmax="<<bounds.max().z()
        <<" cutFaces="<<cutFaces<<" activeCutFaces="<<activeCut<<" cutMetalTmax="<<cutT
        <<" cutMetalEpsilonMax="<<cutE<<" cutUmax="<<cutU<<" productionApproved=0"<<endl;
    Info<<"End"<<endl;return 0;
}
