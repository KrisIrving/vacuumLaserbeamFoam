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

#ifndef legacyAnisimov_H
#define legacyAnisimov_H

#include "vacuumEvaporationModel.H"

namespace Foam
{
namespace vacuumEvaporationModels
{

class legacyAnisimov
:
    public vacuumEvaporationModel
{
    dimensionedScalar p0_;
    dimensionedScalar Tvap_;
    dimensionedScalar Mm_;
    dimensionedScalar latentHeatVap_;
    dimensionedScalar R_;

public:

    TypeName("legacyAnisimov");

    legacyAnisimov
    (
        const fvMesh& mesh,
        const dictionary& modelDict,
        const dictionary& materialDict
    );

    virtual ~legacyAnisimov();

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
