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

namespace Foam
{
    defineTypeNameAndDebug(vacuumEvaporationModel, 0);
    defineRunTimeSelectionTable(vacuumEvaporationModel, dictionary);
}

Foam::vacuumEvaporationModel::vacuumEvaporationModel(const fvMesh& mesh)
:
    mesh_(mesh)
{}

Foam::vacuumEvaporationModel::~vacuumEvaporationModel()
{}

// ************************************************************************* //
