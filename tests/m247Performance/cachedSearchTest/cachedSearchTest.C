#include "fvCFD.H"
#include "findLocalCell.H"

using namespace Foam;

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    localCellSearchWorkspace workspace;
    label checks=0, mismatches=0;
    const label n=mesh.nCells();
    const pointField& centres=mesh.cellCentres();
    const pointField& faceCentres=mesh.faceCentres();
    auto check=[&](const point& p, const label seed)
    {
        const label limits[3]={0,1,100};
        for (label limit : limits)
        {
            const label expected=findLocalCell(p,seed,mesh,limit,false);
            const label actual=findLocalCellCached(p,seed,mesh,limit,false,workspace);
            ++checks;
            if (actual!=expected) ++mismatches;
        }
    };
    // Repeated calls reuse storage; exact face points exercise ambiguous bounds.
    for (label sample=0; sample<min(n,label(32)); ++sample)
    {
        const label cell=sample*n/min(n,label(32));
        check(centres[cell],cell);
        check(centres[cell],(cell+n/2)%n);
        check(centres[cell],-1);
        check(centres[cell],n);
        const labelList& faces=mesh.cells()[cell];
        forAll(faces, faceI) check(faceCentres[faces[faceI]],cell);
        check(centres[cell]+vector(1000,1000,1000),cell);
    }
    reduce(checks,sumOp<label>());
    reduce(mismatches,sumOp<label>());
    Info<< "CACHED_SEARCH_TEST checks=" << checks
        << " mismatches=" << mismatches << endl;
    return checks>0 && mismatches==0 ? 0 : 1;
}
