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

#include "legacyAnisimov.H"
#include "addToRunTimeSelectionTable.H"

namespace Foam
{
namespace vacuumEvaporationModels
{
    defineTypeNameAndDebug(legacyAnisimov, 0);
    addToRunTimeSelectionTable
    (
        vacuumEvaporationModel,
        legacyAnisimov,
        dictionary
    );
}
}

Foam::vacuumEvaporationModels::legacyAnisimov::legacyAnisimov
(
    const fvMesh& mesh,
    const dictionary& modelDict,
    const dictionary& materialDict
)
:
    vacuumEvaporationModel(mesh),
    p0_
    (
        "p0",
        dimensionSet(1, -1, -2, 0, 0, 0, 0),
        materialDict
    ),
    Tvap_
    (
        "Tvap",
        dimensionSet(0, 0, 0, 1, 0, 0, 0),
        materialDict
    ),
    Mm_
    (
        "Mm",
        dimensionSet(1, 0, 0, 0, -1, 0, 0),
        materialDict
    ),
    latentHeatVap_
    (
        "LatentHeatVap",
        dimensionSet(0, 2, -2, 0, 0, 0, 0),
        materialDict
    ),
    R_
    (
        "R",
        dimensionSet(1, 2, -2, -1, -1, 0, 0),
        8.314
    )
{
    (void)modelDict;
}


Foam::vacuumEvaporationModels::legacyAnisimov::~legacyAnisimov()
{}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::legacyAnisimov::saturationPressure
(
    const volScalarField& T
) const
{
    return
        p0_
       *Foam::exp
        (
            latentHeatVap_*Mm_
           *((T - Tvap_)/(R_*T*Tvap_))
        );
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::legacyAnisimov::massFlux
(
    const volScalarField& T
) const
{
    return evaporationHeatFlux(T)/latentHeatVap_;
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::legacyAnisimov::recoilPressure
(
    const volScalarField& T
) const
{
    // Keep the exact V3.0 operation order for byte-level regression.
    return
        0.54*p0_
       *Foam::exp
        (
            latentHeatVap_*Mm_
           *((T - Tvap_)/(R_*T*Tvap_))
        );
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::legacyAnisimov::evaporationHeatFlux
(
    const volScalarField& T
) const
{
    // Keep the exact V3.0 operation order for byte-level regression.
    return
        0.82*latentHeatVap_*Mm_*p0_
       *Foam::exp
        (
            latentHeatVap_*Mm_
           *((T - Tvap_)/(R_*T*Tvap_))
        )
       /Foam::pow(2*M_PI*Mm_*R_*T, 0.5);
}

// ************************************************************************* //
