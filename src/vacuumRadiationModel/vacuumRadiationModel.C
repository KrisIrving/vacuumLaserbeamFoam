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

#include "vacuumRadiationModel.H"

Foam::vacuumRadiationModel::vacuumRadiationModel
(
    const fvMesh& mesh,
    const dictionary& vacuumProperties
)
:
    mesh_(mesh),
    enabled_(false),
    chamberTemperature_
    (
        "chamberTemperature",
        dimTemperature,
        vacuumProperties
    ),
    emissivitySolid_(0.0),
    emissivityLiquid_(0.0),
    sigma_
    (
        "StefanBoltzmann",
        dimensionSet(1, 0, -3, -4, 0, 0, 0),
        5.670374419e-8
    )
{
    if (vacuumProperties.found("radiation"))
    {
        const dictionary& radiationDict =
            vacuumProperties.subDict("radiation");

        enabled_ =
            radiationDict.lookupOrDefault<bool>("enabled", false);

        if (enabled_)
        {
            emissivitySolid_ =
                readScalar(radiationDict.lookup("emissivitySolid"));
            emissivityLiquid_ =
                readScalar(radiationDict.lookup("emissivityLiquid"));

            if
            (
                emissivitySolid_ < 0.0
             || emissivitySolid_ > 1.0
             || emissivityLiquid_ < 0.0
             || emissivityLiquid_ > 1.0
            )
            {
                FatalIOErrorInFunction(radiationDict)
                    << "Radiative emissivities must lie in [0,1]"
                    << exit(FatalIOError);
            }
        }
    }

    Info<< "Vacuum radiation model" << nl
        << "    enabled             = " << enabled_ << nl
        << "    chamberTemperature  = " << chamberTemperature_ << nl
        << "    emissivitySolid     = " << emissivitySolid_ << nl
        << "    emissivityLiquid    = " << emissivityLiquid_
        << endl;
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumRadiationModel::emissivity
(
    const volScalarField& liquidFraction
) const
{
    return
        emissivitySolid_
      + (emissivityLiquid_ - emissivitySolid_)*liquidFraction;
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumRadiationModel::heatFlux
(
    const volScalarField& T,
    const volScalarField& liquidFraction
) const
{
    tmp<volScalarField> tEmissivity = emissivity(liquidFraction);

    return
        sigma_*tEmissivity()
       *(
            Foam::pow(T, 4)
          - Foam::pow(chamberTemperature_, 4)
        );
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumRadiationModel::implicitCoefficient
(
    const volScalarField& T,
    const volScalarField& liquidFraction
) const
{
    tmp<volScalarField> tEmissivity = emissivity(liquidFraction);

    return
        4.0*sigma_*tEmissivity()*Foam::pow(T, 3);
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumRadiationModel::explicitFlux
(
    const volScalarField& T,
    const volScalarField& liquidFraction
) const
{
    tmp<volScalarField> tEmissivity = emissivity(liquidFraction);

    return
        sigma_*tEmissivity()
       *(
            3.0*Foam::pow(T, 4)
          + Foam::pow(chamberTemperature_, 4)
        );
}

// ************************************************************************* //
