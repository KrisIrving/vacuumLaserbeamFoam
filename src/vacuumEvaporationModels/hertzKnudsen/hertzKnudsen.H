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

#ifndef hertzKnudsen_H
#define hertzKnudsen_H

#include "vacuumEvaporationModel.H"

namespace Foam
{
namespace vacuumEvaporationModels
{

class hertzKnudsen
:
    public vacuumEvaporationModel
{
    dimensionedScalar chamberPressure_;
    dimensionedScalar chamberTemperature_;
    dimensionedScalar referencePressure_;
    dimensionedScalar referenceTemperature_;
    dimensionedScalar molarMass_;
    dimensionedScalar latentHeatVap_;
    dimensionedScalar R_;
    scalar accommodationCoefficient_;

public:

    TypeName("hertzKnudsen");

    hertzKnudsen
    (
        const fvMesh& mesh,
        const dictionary& modelDict,
        const dictionary& materialDict
    );

    virtual ~hertzKnudsen();

    virtual tmp<volScalarField> saturationPressure
    (
        const volScalarField& T
    ) const override;

    virtual tmp<volScalarField> massFlux
    (
        const volScalarField& T
    ) const override;

    virtual tmp<volScalarField> recoilPressure
    (
        const volScalarField& T
    ) const override;

    virtual tmp<volScalarField> evaporationHeatFlux
    (
        const volScalarField& T
    ) const override;
};

} // End namespace vacuumEvaporationModels
} // End namespace Foam

#endif

// ************************************************************************* //
