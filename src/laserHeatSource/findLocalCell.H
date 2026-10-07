/*---------------------------------------------------------------------------*\
Function
    findLocalCell

Description
    Function that uses a local search to find a cell given its coordinates.
    If the local search fails then default to an N2 search.

Author
    Philip Cardiff, UCD.

\*---------------------------------------------------------------------------*/

#ifndef findLocalCell_H
#define findLocalCell_H

#include "DynamicList.H"
#include "HashSet.H"
#include "SLList.H"
#include "polyMesh.H"
#include "scalarField.H"

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

namespace Foam
{

    // Accept only points strictly inside the six axis-aligned face planes.
    // Ambiguous face points and every non-Cartesian cell use the old predicate.
    // Rebuild per laser update so moving/topology-changing meshes cannot leave
    // stale bounds. This shortcut never selects a different seed or neighbour.
    struct cartesianSeedBounds
    {
        pointField lower, upper;
        scalarField margins;
        labelList eligible;

        void reset(const polyMesh& mesh)
        {
            lower.setSize(mesh.nCells(), point::zero);
            upper.setSize(mesh.nCells(), point::zero);
            eligible.setSize(mesh.nCells(), 0);
            eligible=0;
            margins.setSize(mesh.nCells(), 0);
            const vectorField& areas=mesh.faceAreas();
            const pointField& centres=mesh.faceCentres();
            const labelList& owners=mesh.faceOwner();
            forAll(mesh.cells(), celli)
            {
                const cell& faces=mesh.cells()[celli];
                if (faces.size()!=6) continue;
                label mask=0;
                forAll(faces, i)
                {
                    const label facei=faces[i];
                    const vector normal=(owners[facei]==celli)
                        ? areas[facei] : -areas[facei];
                    label axis=-1;
                    for (label d=0; d<3; ++d)
                        if (normal[d]!=0)
                        {
                            if (axis!=-1) { axis=-2; break; }
                            axis=d;
                        }
                    if (axis<0) { mask=0; break; }
                    const bool positive=normal[axis]>0;
                    const label bit=1 << (2*axis+label(positive));
                    if (mask & bit) { mask=0; break; }
                    mask |= bit;
                    (positive ? upper[celli] : lower[celli])[axis]=centres[facei][axis];
                }
                if (mask==63 && lower[celli].x()<upper[celli].x()
                    && lower[celli].y()<upper[celli].y()
                    && lower[celli].z()<upper[celli].z())
                {
                    eligible[celli]=1;
                    margins[celli]=64*SMALL*(mag(lower[celli])+mag(upper[celli])
                        +mag(upper[celli]-lower[celli]));
                }
            }
        }

        bool containsInterior(const point& p, const label seed) const
        {
            if (seed<0 || seed>=eligible.size() || !eligible[seed]) return false;
            const point& lo=lower[seed];
            const point& hi=upper[seed];
            const scalar margin=margins[seed];
            return p.x()>lo.x()+margin && p.x()<hi.x()-margin
                && p.y()>lo.y()+margin && p.y()<hi.y()-margin
                && p.z()>lo.z()+margin && p.z()<hi.z()-margin;
        }
    };

    // Reuse FIFO storage while preserving the legacy traversal order,
    // duplicate queue entries, containment predicates and search limit.
    struct localCellSearchWorkspace
    {
        DynamicList<label> queue;
        labelHashSet checked;
    };

    label findLocalCellCached
    (
        const point& p,
        const label seedCellID,
        const polyMesh& mesh,
        const label maxLocalSearch,
        const Switch debug,
        localCellSearchWorkspace& workspace,
        const cartesianSeedBounds* seedBounds=nullptr
    )
    {
        if (seedCellID < 0 || seedCellID >= mesh.nCells())
            return mesh.findCell(p);
        if (seedBounds && seedBounds->containsInterior(p, seedCellID))
            return seedCellID;
        if (mesh.primitiveMesh::pointInCell(p, seedCellID))
            return seedCellID;

        workspace.queue.clear();
        workspace.checked.clear();
        const labelListList& cellCells=mesh.cellCells();
        const labelList& seedNeighbours=cellCells[seedCellID];
        forAll(seedNeighbours, i) workspace.queue.append(seedNeighbours[i]);
        label head=0, localSearchI=0;
        while (head < workspace.queue.size())
        {
            const label cellID=workspace.queue[head++];
            if (mesh.pointInCell(p, cellID)) return cellID;
            workspace.checked.insert(cellID);
            const labelList& neighbours=cellCells[cellID];
            forAll(neighbours, i)
                if (!workspace.checked.found(neighbours[i]))
                    workspace.queue.append(neighbours[i]);
            if (++localSearchI > maxLocalSearch) break;
        }
        return mesh.findCell(p);
    }

    // Find the cell containing the given point and return its cell index. The
    // local search starts from the provided seed cell. If the local search
    // fails then a global search is performed.
    // Searching across processor boundaries is achieved by defaulting to the N2
    // search.
    // The local search will stop after it have performed maxLocalSearch
    // searches; this is to avoid searching the entire domain when loooking for
    // a point that crossed a processor boundary
    label findLocalCell
    (
        const point& p,
        const label seedCellID,
        const polyMesh& mesh,
        const label maxLocalSearch = 100,
        const Switch debug = false
    )
    {
        // If the seed is out-of-range then use N2 search
        if (seedCellID < 0 || seedCellID >= mesh.nCells())
        {
            const label cellID = mesh.findCell(p);
            if (debug)
            {
                Pout<< "    Seed cell out of range: use N2 search. "
                    << "Seed ID = " << seedCellID
                    << ", Cell ID = " << cellID << endl;
            }
            return cellID;
        }

        // Trivial case: check if the point is in the seed cell
        // The default pointInCell decomposes the cell into tets; this is more
        // robust on general polyhedral meshes but is expensive. As we almost
        // exclusively use structured grids, we will use the primitiveMesh
        // implementation based on the face planes, which is similar to
        // polyMesh::cellDecomposition::FACE_PLANES
        // if (mesh.pointInCell(p, seedCellID))
        // if
        // (
        //     mesh.pointInCell
        //     (
        //         p, seedCellID, polyMesh::cellDecomposition::FACE_PLANES
        //     )
        // )
        if (mesh.primitiveMesh::pointInCell(p, seedCellID))
        {
            if (debug)
            {
                Pout<< "    Found point in seed cell. Seed ID = " << seedCellID
                    << ", Cell ID = " << seedCellID
                    << endl;
            }
            return seedCellID;
        }

        // We will perform the search by checking cell-cells
        // We need two lists for storing cell indices: toCheck, and
        // checked

        // Take a reference to the cell-cells
        const labelListList& cellCells = mesh.cellCells();

        // Create toCheck list to store cells to be checked
        // Insert the seed cell-cell neighbours
        SLList<label> toCheck;
        const labelList& seedCellCells = cellCells[seedCellID];
        forAll(seedCellCells, ccI)
        {
            toCheck.append(seedCellCells[ccI]);
        }

        // Create checked list
        labelHashSet checked;

        // Track the number of local searches
        label localSearchI = 0;

        // Perform local search
        while (toCheck.size() > 0)
        {
            // Get next cell to be checked, remove it from the toCheck list and
            // add it to the checked list
            const label cellID = toCheck.removeHead();

            // Check if the point is in this cell
            if (mesh.pointInCell(p, cellID))
	    {
                if (debug)
                {
                    Pout<< "    local search: found after " << localSearchI
                        << " checks. Seed ID = " << seedCellID
                        << ", Cell ID = " << cellID << endl;
                }
                return cellID;
            }

            // Mark the point as checked
            checked.insert(cellID);

            // Insert all cell-cell neighbours of cellID, if they have not
            // already been checked
            const labelList& curCellCells = cellCells[cellID];
            forAll(curCellCells, ccI)
            {
                if (!checked.found(curCellCells[ccI]))
                {
                    toCheck.append(curCellCells[ccI]);
                }
            }

            if (++localSearchI > maxLocalSearch)
            {
                // Break to the N2 search
                if (debug)
                {
                    Pout<< "    Max number of local searches reached: "
                        << maxLocalSearch << endl;
                }
                break;
            }
        }

        // Resort to N2 search
        const label cellID = mesh.findCell(p);
        if (debug)
        {
            Pout<< "    Defaults to N2 search. Seed ID = " << seedCellID
                << ", Cell ID = " << cellID << endl;
        }
        return cellID;
    }

} // End namespace Foam

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

#endif

// ************************************************************************* //
