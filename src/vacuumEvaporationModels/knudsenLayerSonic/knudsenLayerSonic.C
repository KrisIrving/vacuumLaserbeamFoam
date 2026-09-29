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

#include "knudsenLayerSonic.H"
#include "addToRunTimeSelectionTable.H"

#include <cmath>

namespace Foam
{
namespace vacuumEvaporationModels
{
    defineTypeNameAndDebug(knudsenLayerSonic, 0);
    addToRunTimeSelectionTable
    (
        vacuumEvaporationModel,
        knudsenLayerSonic,
        dictionary
    );
}
}

Foam::vacuumEvaporationModels::knudsenLayerSonic::knudsenLayerSonic
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
    referencePressure_
    (
        "referencePressure",
        dimensionSet(1, -1, -2, 0, 0, 0, 0),
        modelDict.subDict("knudsenLayerSonicCoeffs")
    ),
    referenceTemperature_
    (
        "referenceTemperature",
        dimensionSet(0, 0, 0, 1, 0, 0, 0),
        modelDict.subDict("knudsenLayerSonicCoeffs")
    ),
    molarMass_
    (
        "molarMass",
        dimensionSet(1, 0, 0, 0, -1, 0, 0),
        modelDict.subDict("knudsenLayerSonicCoeffs")
    ),
    latentHeatVap_
    (
        "latentHeatVap",
        dimensionSet(0, 2, -2, 0, 0, 0, 0),
        modelDict.subDict("knudsenLayerSonicCoeffs")
    ),
    R_
    (
        "R",
        dimensionSet(1, 2, -2, -1, -1, 0, 0),
        8.314
    ),
    gamma_(5.0/3.0),
    m_(0.0),
    temperatureRatio_(0.0),
    p3OverPe_(0.0),
    massFluxRatio_(0.0),
    recoilCoefficient_(0.0)
{
    (void)materialDict;

    if (chamberPressure_.value() < 0)
    {
        FatalIOErrorInFunction(modelDict)
            << "chamberPressure must be non-negative"
            << exit(FatalIOError);
    }

    // Wang, Zhang & Yan, Phys. Rev. Applied 14, 064039 (2020),
    // Eqs. (9)-(13), evaluated at the sonic Knudsen-layer edge Ma = 1.
    // The paper takes gamma = 5/3 for monatomic metal vapour; keep this fixed
    // rather than exposing a non-physical tuning parameter.
    const scalar pi = M_PI;
    const scalar sqrtPi = std::sqrt(pi);

    m_ = std::sqrt(gamma_/2.0);

    const scalar m2 = m_*m_;
    const scalar expMinusM2 = std::exp(-m2);
    const scalar erfcM = std::erfc(m_);

    const scalar Fminus =
        -sqrtPi*m_*erfcM + expMinusM2;

    const scalar Gminus =
        (2.0*m2 + 1.0)*erfcM
      - (2.0/sqrtPi)*m_*expMinusM2;

    // Wang et al. Eq. (10):
    // sqrt(T3/Te) = sqrt(1 + pi*m^2/64) - sqrt(pi)*m/8.
    const scalar sqrtTemperatureRatio =
        std::sqrt(1.0 + (pi/64.0)*m2)
      - (sqrtPi/8.0)*m_;

    temperatureRatio_ = sqr(sqrtTemperatureRatio);

    const scalar jumpDenominator =
        Fminus + sqrtTemperatureRatio*Gminus;

    if (jumpDenominator <= SMALL || temperatureRatio_ <= SMALL)
    {
        FatalIOErrorInFunction(modelDict)
            << "Invalid sonic Knudsen-layer jump state"
            << exit(FatalIOError);
    }

    // Eq. (10): Pe/P3 = 2 exp(-m^2)/(F- + sqrt(T3/Te) G-)
    p3OverPe_ =
        jumpDenominator/(2.0*expMinusM2);

    // Eq. (11), expressed relative to the maximum Hertz flux:
    // mLoss = phi * Pe * sqrt(M/(2*pi*R*Te)).
    massFluxRatio_ =
        2.0*sqrtPi*m_*p3OverPe_/sqrtTemperatureRatio;

    // Eq. (12), equivalently P_recoil = P3*(2*m^2 + 1).
    recoilCoefficient_ =
        p3OverPe_*(2.0*m2 + 1.0);

    Info<< "    sonic Knudsen-layer constants (Ma=1)" << nl
        << "        gamma             = " << gamma_ << nl
        << "        m                 = " << m_ << nl
        << "        T3/Te             = " << temperatureRatio_ << nl
        << "        P3/Pe             = " << p3OverPe_ << nl
        << "        massFluxRatio     = " << massFluxRatio_ << nl
        << "        recoilCoefficient = " << recoilCoefficient_
        << endl;
}


Foam::vacuumEvaporationModels::knudsenLayerSonic::~knudsenLayerSonic()
{}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::knudsenLayerSonic::saturationPressure
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
Foam::vacuumEvaporationModels::knudsenLayerSonic::massFlux
(
    const volScalarField& T
) const
{
    tmp<volScalarField> tPsat = saturationPressure(T);
    const volScalarField& pSat = tPsat();

    return
        Foam::pos(pSat - chamberPressure_)
       *massFluxRatio_
       *pSat
       *Foam::sqrt(molarMass_/(2.0*M_PI*R_*T));
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::knudsenLayerSonic::recoilPressure
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

    // Eq. (12) gives the absolute surface recoil pressure. The incompressible
    // pseudo-gas solver uses gauge pressure, so return the net normal stress
    // relative to the configured chamber pressure.
    return
        Foam::max
        (
            recoilCoefficient_*tPsat() - chamberPressure_,
            zeroPressure
        );
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::knudsenLayerSonic::evaporationHeatFlux
(
    const volScalarField& T
) const
{
    return latentHeatVap_*massFlux(T);
}

// ************************************************************************* //
