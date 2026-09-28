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

#ifndef vacuumEvaporationModel_H
#define vacuumEvaporationModel_H

#include "dictionary.H"
#include "fvMesh.H"
#include "runTimeSelectionTables.H"
#include "volFields.H"

namespace Foam
{

class vacuumEvaporationModel
{
protected:

    const fvMesh& mesh_;

public:

    TypeName("vacuumEvaporationModel");

    declareRunTimeSelectionTable
    (
        autoPtr,
        vacuumEvaporationModel,
        dictionary,
        (const fvMesh& mesh, const dictionary& dict),
        (mesh, dict)
    );

    explicit vacuumEvaporationModel(const fvMesh& mesh);

    virtual ~vacuumEvaporationModel();

    static autoPtr<vacuumEvaporationModel> New
    (
        const fvMesh& mesh,
        const dictionary& dict
    );

    virtual tmp<volScalarField> recoilPressure
    (
        const volScalarField& T
    ) const = 0;

    virtual tmp<volScalarField> evaporationHeatFlux
    (
        const volScalarField& T
    ) const = 0;
};

} // End namespace Foam

#endif

// ************************************************************************* //
