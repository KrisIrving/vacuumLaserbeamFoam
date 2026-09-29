/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           |
     \\/     M anipulation  |
-------------------------------------------------------------------------------
License
    This file is part of vacuumLaserbeamFoam and is distributed under the
    GNU General Public License version 3 or later.
\*---------------------------------------------------------------------------*/

#ifndef nearVacuumWang_H
#define nearVacuumWang_H

#include "vacuumEvaporationModel.H"
#include "knudsenTransitionRelations.H"

namespace Foam
{
namespace vacuumEvaporationModels
{

class nearVacuumWang
:
    public vacuumEvaporationModel
{
    dimensionedScalar chamberPressure_;
    dimensionedScalar chamberTemperature_;
    dimensionedScalar referencePressure_;
    dimensionedScalar referenceTemperature_;
    dimensionedScalar molarMass_;
    dimensionedScalar latentHeatVap_;
    dimensionedScalar liquidusTemperature_;
    dimensionedScalar thresholdTemperatureMin_;
    dimensionedScalar thresholdTemperatureMax_;
    dimensionedScalar R_;

    knudsenTransitionRelations relations_;

    scalar boilingTemperature_;
    scalar activationTemperature_;
    scalar Tk0_;
    scalar Tk1_;

    void evaluateState
    (
        const scalar temperature,
        scalar& massFlux,
        scalar& recoilPressure
    ) const;

public:

    TypeName("nearVacuumWang");

    nearVacuumWang
    (
        const fvMesh& mesh,
        const dictionary& modelDict,
        const dictionary& materialDict
    );

    virtual ~nearVacuumWang();

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
