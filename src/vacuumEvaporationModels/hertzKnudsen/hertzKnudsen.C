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

#include "hertzKnudsen.H"
#include "addToRunTimeSelectionTable.H"

namespace Foam
{
namespace vacuumEvaporationModels
{
    defineTypeNameAndDebug(hertzKnudsen, 0);
    addToRunTimeSelectionTable
    (
        vacuumEvaporationModel,
        hertzKnudsen,
        dictionary
    );
}
}

Foam::vacuumEvaporationModels::hertzKnudsen::hertzKnudsen
(
    const fvMesh& mesh,
    const dictionary& modelDict,
    const dictionary& materialDict
)
:
    vacuumEvaporationModel(mesh),
    chamberPressure_
    (
        "chamberPressure",
        dimensionSet(1, -1, -2, 0, 0, 0, 0),
        modelDict
    ),
    chamberTemperature_
    (
        "chamberTemperature",
        dimensionSet(0, 0, 0, 1, 0, 0, 0),
        modelDict
    ),
    referencePressure_
    (
        "referencePressure",
        dimensionSet(1, -1, -2, 0, 0, 0, 0),
        modelDict.subDict("hertzKnudsenCoeffs")
    ),
    referenceTemperature_
    (
        "referenceTemperature",
        dimensionSet(0, 0, 0, 1, 0, 0, 0),
        modelDict.subDict("hertzKnudsenCoeffs")
    ),
    molarMass_
    (
        "molarMass",
        dimensionSet(1, 0, 0, 0, -1, 0, 0),
        modelDict.subDict("hertzKnudsenCoeffs")
    ),
    latentHeatVap_
    (
        "latentHeatVap",
        dimensionSet(0, 2, -2, 0, 0, 0, 0),
        modelDict.subDict("hertzKnudsenCoeffs")
    ),
    R_
    (
        "R",
        dimensionSet(1, 2, -2, -1, -1, 0, 0),
        8.314
    ),
    accommodationCoefficient_
    (
        modelDict.subDict("hertzKnudsenCoeffs")
       .lookupOrDefault<scalar>("accommodationCoefficient", 1.0)
    )
{
    (void)materialDict;

    if (chamberPressure_.value() < 0)
    {
        FatalIOErrorInFunction(modelDict)
            << "chamberPressure must be non-negative"
            << exit(FatalIOError);
    }

    if (chamberTemperature_.value() <= 0)
    {
        FatalIOErrorInFunction(modelDict)
            << "chamberTemperature must be positive"
            << exit(FatalIOError);
    }

    if
    (
        accommodationCoefficient_ < 0
     || accommodationCoefficient_ > 1
    )
    {
        FatalIOErrorInFunction(modelDict)
            << "accommodationCoefficient must lie in [0,1]"
            << exit(FatalIOError);
    }

    Info<< "    chamberPressure      = " << chamberPressure_ << nl
        << "    chamberTemperature   = " << chamberTemperature_ << nl
        << "    referencePressure    = " << referencePressure_ << nl
        << "    referenceTemperature = " << referenceTemperature_ << nl
        << "    accommodationCoeff   = " << accommodationCoefficient_
        << endl;
}


Foam::vacuumEvaporationModels::hertzKnudsen::~hertzKnudsen()
{}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::hertzKnudsen::saturationPressure
(
    const volScalarField& T
) const
{
    return
        referencePressure_
       *Foam::exp
        (
            latentHeatVap_*molarMass_
           *((T - referenceTemperature_)
           /(R_*T*referenceTemperature_))
        );
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::hertzKnudsen::massFlux
(
    const volScalarField& T
) const
{
    const dimensionedScalar zeroPressure
    (
        "zeroPressure",
        chamberPressure_.dimensions(),
        0.0
    );

    tmp<volScalarField> tPsat = saturationPressure(T);

    return
        accommodationCoefficient_
       *Foam::max(tPsat() - chamberPressure_, zeroPressure)
       *Foam::sqrt(molarMass_/(2*M_PI*R_*T));
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::hertzKnudsen::recoilPressure
(
    const volScalarField& T
) const
{
    const dimensionedScalar zeroPressure
    (
        "zeroPressure",
        chamberPressure_.dimensions(),
        0.0
    );

    tmp<volScalarField> tPsat = saturationPressure(T);

    // Free-molecular half-range momentum-flux reference closure.
    // This is intentionally a simple pressure-aware benchmark, not the final
    // near-vacuum/Knudsen-layer recoil model.
    return
        0.5
       *Foam::max(tPsat() - chamberPressure_, zeroPressure);
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::hertzKnudsen::evaporationHeatFlux
(
    const volScalarField& T
) const
{
    return latentHeatVap_*massFlux(T);
}

// ************************************************************************* //
