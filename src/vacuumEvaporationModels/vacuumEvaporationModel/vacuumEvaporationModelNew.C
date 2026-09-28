/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           |
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of vacuumLaserbeamFoam.

    vacuumLaserbeamFoam is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by the
    Free Software Foundation, either version 3 of the License, or (at your
    option) any later version.
\*---------------------------------------------------------------------------*/

#include "vacuumEvaporationModel.H"

Foam::autoPtr<Foam::vacuumEvaporationModel>
Foam::vacuumEvaporationModel::New
(
    const fvMesh& mesh,
    const dictionary& modelDict,
    const dictionary& materialDict
)
{
    const word modelType(modelDict.lookup<word>("evaporationModel"));

    Info<< "Selecting vacuum evaporation model " << modelType << endl;

    auto cstrIter = dictionaryConstructorTablePtr_->find(modelType);

    if (cstrIter == dictionaryConstructorTablePtr_->end())
    {
        FatalIOErrorInFunction(modelDict)
            << "Unknown vacuum evaporation model " << modelType << nl << nl
            << "Valid model types are:" << nl
            << dictionaryConstructorTablePtr_->sortedToc()
            << exit(FatalIOError);
    }

    return cstrIter()(mesh, modelDict, materialDict);
}

// ************************************************************************* //
