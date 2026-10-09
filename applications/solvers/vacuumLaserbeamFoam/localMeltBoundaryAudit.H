// Opt-in per-step cut-boundary observations; never alters solver fields.
if(runTime.controlDict().getOrDefault<bool>("localMeltBoundaryAudit",false))
{
    scalar metalT=0,metalE=0,speed=0,netFlux=0;label faces=0,active=0;
    const label patch=mesh.boundaryMesh().findPatchID("localCut");
    if(patch>=0)
    {
        const labelUList& cells=mesh.boundary()[patch].faceCells();faces=cells.size();
        forAll(cells,j)
        {
            const label i=cells[j];speed=max(speed,mag(U[i]));netFlux+=phi.boundaryField()[patch][j];
            if(alpha1[i]>=0.05)
            {metalT=max(metalT,T[i]);metalE=max(metalE,epsilon1[i]);
                if(T[i]>=1487||epsilon1[i]>=1e-6||mag(U[i])>=1)++active;}
        }
    }
    reduce(faces,sumOp<label>());reduce(active,sumOp<label>());reduce(metalT,maxOp<scalar>());
    reduce(metalE,maxOp<scalar>());reduce(speed,maxOp<scalar>());reduce(netFlux,sumOp<scalar>());
    Info().precision(17);
    Info<<"M247_LOCAL_MELT_BOUNDARY schema=1 time="<<runTime.value()<<" cutFaces="<<faces
        <<" activeCutFaces="<<active<<" cutMetalTmax="<<metalT<<" cutMetalEpsilonMax="<<metalE
        <<" cutUmax="<<speed<<" cutNetFluxM3PerS="<<netFlux<<" productionApproved=0"<<endl;
}
