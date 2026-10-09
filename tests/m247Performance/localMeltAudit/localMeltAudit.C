// Native binary/ASCII snapshot reader. Default read-only; explicit copied-case cut initialization only.
#include "fvCFD.H"
#include "timeSelector.H"
#include <fstream>
#include <iomanip>
#include <cmath>
using namespace Foam;
// Opt-in initialization on a copied local case only. The native owner-cell
// checkpoint values define the explicitly approximated held cut reservoir.
template<class Type>
void initializeCut(GeometricField<Type,fvPatchField,volMesh>& field,const label patch,const word& kind)
{
    const tmp<Field<Type>> values=field.boundaryField()[patch].patchInternalField();
    field.boundaryFieldRef().set
    (
        patch,
        fvPatchField<Type>::New(kind,field.mesh().boundary()[patch],field.internalField()).ptr()
    );
    field.boundaryFieldRef()[patch] == values();
    if(!field.write())FatalErrorInFunction<<"Cut field write failed: "<<field.name()<<exit(FatalError);
    Info<<"M247_LOCAL_CUT_FIELD field="<<field.name()<<" type="<<kind
        <<" faces="<<values().size()<<" source=checkpointOwnerCells"<<endl;
}
template<class Type>
void verifyCut(const GeometricField<Type,fvPatchField,volMesh>& field,const label patch,const word& kind)
{
    const tmp<Field<Type>> expected=field.boundaryField()[patch].patchInternalField();
    const scalar error=gMax(mag(field.boundaryField()[patch]-expected()));
    const scalar scale=max(scalar(1),gMax(mag(expected())));
    if(field.boundaryField()[patch].type()!=kind||error>1e-12*scale)
        FatalErrorInFunction<<"Held cut verification failed: "<<field.name()<<" error="<<error<<exit(FatalError);
    Info<<"M247_LOCAL_CUT_VERIFIED_FIELD field="<<field.name()<<" relativeError="<<error/scale<<endl;
}
int main(int argc,char *argv[])
{
    argList::noParallel();argList::noFunctionObjects();timeSelector::addOptions();
    argList::addBoolOption("verifyCut","Verify serialized cut types/values against native checkpoint owner cells");
    argList::addBoolOption("initializeCut","Initialize held cut BCs from native checkpoint owner cells on a copied local case");
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
    if(args.found("initializeCut"))
    {
        if(mag(runTime.value()-0.00018)>1e-14||cutFaces<=0||activeCut)
            FatalErrorInFunction<<"Unsafe cut initialization: expected clear localCut at180us"<<exit(FatalError);
        initializeCut(T,patch,"fixedValue");
        initializeCut(a,patch,"fixedValue");
        initializeCut(e,patch,"fixedValue");
        initializeCut(U,patch,"fixedValue");
        initializeCut(p,patch,"fixedFluxPressure");
        Info<<"M247_LOCAL_CUT_INITIALIZED schema=1 fields=5 faces="<<cutFaces
            <<" source=checkpointOwnerCells internalFieldsChanged=0"<<endl;
    }
    if(args.found("verifyCut"))
    {
        if(mag(runTime.value()-0.00018)>1e-14||cutFaces<=0||activeCut)
            FatalErrorInFunction<<"Unsafe cut verification"<<exit(FatalError);
        verifyCut(T,patch,"fixedValue");verifyCut(a,patch,"fixedValue");
        verifyCut(e,patch,"fixedValue");verifyCut(U,patch,"fixedValue");
        verifyCut(p,patch,"fixedFluxPressure");
        Info<<"M247_LOCAL_CUT_VERIFIED schema=1 fields=5 faces="<<cutFaces<<endl;
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
