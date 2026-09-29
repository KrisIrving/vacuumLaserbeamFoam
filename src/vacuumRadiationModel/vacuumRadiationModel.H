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

#ifndef vacuumRadiationModel_H
#define vacuumRadiationModel_H

#include "dictionary.H"
#include "fvMesh.H"
#include "volFields.H"

namespace Foam
{

class vacuumRadiationModel
{
    const fvMesh& mesh_;

    bool enabled_;
    dimensionedScalar chamberTemperature_;
    scalar emissivitySolid_;
    scalar emissivityLiquid_;
    dimensionedScalar sigma_;

public:

    vacuumRadiationModel
    (
        const fvMesh& mesh,
        const dictionary& vacuumProperties
    );

    bool enabled() const
    {
        return enabled_;
    }

    const dimensionedScalar& chamberTemperature() const
    {
        return chamberTemperature_;
    }

    scalar emissivitySolid() const
    {
        return emissivitySolid_;
    }

    scalar emissivityLiquid() const
    {
        return emissivityLiquid_;
    }

    tmp<volScalarField> emissivity
    (
        const volScalarField& liquidFraction
    ) const;

    // Net outward radiative heat flux [W/m2].
    tmp<volScalarField> heatFlux
    (
        const volScalarField& T,
        const volScalarField& liquidFraction
    ) const;

    // Coefficient A in q_rad ~= A*T - B, where
    // A = 4*epsilon*sigma*T0^3 [W/m2/K].
    tmp<volScalarField> implicitCoefficient
    (
        const volScalarField& T,
        const volScalarField& liquidFraction
    ) const;

    // Explicit B in q_rad ~= A*T - B, where
    // B = epsilon*sigma*(3*T0^4 + Twall^4) [W/m2].
    tmp<volScalarField> explicitFlux
    (
        const volScalarField& T,
        const volScalarField& liquidFraction
    ) const;
};

} // End namespace Foam

#endif

// ************************************************************************* //
