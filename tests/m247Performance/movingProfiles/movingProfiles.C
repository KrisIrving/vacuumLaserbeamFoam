// Read stored final snapshot only. Coordinate slabs are a screening projection.
#include "fvCFD.H"
#include "timeSelector.H"
#include <cmath>
using namespace Foam;
int main(int argc,char *argv[])
{
    timeSelector::addOptions();
    #include "setRootCase.H"
    #include "createTime.H"
    const instantList times=timeSelector::select0(runTime,args);
    if (times.size()!=1)FatalErrorInFunction<<"Select exactly one saved snapshot"<<exit(FatalError);
    runTime.setTime(times[0],0);
    #include "createMesh.H"
    volScalarField T(IOobject("T",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField a(IOobject("alpha.metal",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volScalarField e(IOobject("epsilon1",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    volVectorField U(IOobject("U",runTime.timeName(),mesh,IOobject::MUST_READ,IOobject::NO_WRITE),mesh);
    const scalar lows[3]={-520e-6,0,-320e-6}, highs[3]={320e-6,960e-6,320e-6};
    const label counts[3]={53,60,40};
    label invalid=0;
    forAll(T,i)
    {
        if (!std::isfinite(T[i])||T[i]<=0||!std::isfinite(a[i])||!std::isfinite(e[i])
            ||a[i]<-1e-8||a[i]>1+1e-8||e[i]<-1e-8||e[i]>1+1e-8
            ||!std::isfinite(mag(U[i]))||!std::isfinite(mesh.V()[i])||mesh.V()[i]<=0)++invalid;
        for(label d=0;d<3;++d)
            if (!std::isfinite(mesh.C()[i][d])||mesh.C()[i][d]<lows[d]||mesh.C()[i][d]>=highs[d])++invalid;
    }
    reduce(invalid,sumOp<label>());
    if(invalid)FatalErrorInFunction<<"Invalid profile inputs"<<exit(FatalError);
    Info().precision(17);
    Info<<"M247_PROFILE_STATE schema=1 time="<<runTime.value()<<" ranks="<<Pstream::nProcs()
        <<" cells="<<returnReduce(mesh.nCells(),sumOp<label>())<<" invalid="<<invalid<<endl;
    for(label d=0;d<3;++d)
    {
        const label n=counts[d];
        List<scalarField> bins(n);
        forAll(bins,j)bins[j]=scalarField(7,0);
        forAll(T,i)
        {
            const label j=label(std::floor((mesh.C()[i][d]-lows[d])/(highs[d]-lows[d])*n));
            if(j<0||j>=n)FatalErrorInFunction<<"Coordinate slab index out of range"<<exit(FatalError);
            const scalar v=mesh.V()[i],av=v*a[i];
            bins[j][0]+=v;bins[j][1]+=av;bins[j][2]+=av*e[i];bins[j][3]+=av*T[i];
            for(label k=0;k<3;++k)bins[j][4+k]+=av*U[i][k];
        }
        forAll(bins,j)
        {
            forAll(bins[j],k)reduce(bins[j][k],sumOp<scalar>());
            Info<<"M247_PROFILE schema=1 time="<<runTime.value()<<" axis="<<d<<" bin="<<j
                <<" low="<<lows[d]+(highs[d]-lows[d])*j/n
                <<" high="<<lows[d]+(highs[d]-lows[d])*(j+1)/n
                <<" volume="<<bins[j][0]<<" metal="<<bins[j][1]<<" liquid="<<bins[j][2]
                <<" metalT="<<bins[j][3]<<" metalUx="<<bins[j][4]
                <<" metalUy="<<bins[j][5]<<" metalUz="<<bins[j][6]<<endl;
        }
    }
    Info<<"End"<<endl;
    return 0;
}
