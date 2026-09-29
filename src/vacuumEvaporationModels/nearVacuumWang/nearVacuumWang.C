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

#include "nearVacuumWang.H"
#include "addToRunTimeSelectionTable.H"

#include <cmath>

namespace Foam
{
namespace vacuumEvaporationModels
{
    defineTypeNameAndDebug(nearVacuumWang, 0);
    addToRunTimeSelectionTable
    (
        vacuumEvaporationModel,
        nearVacuumWang,
        dictionary
    );
}
}

Foam::vacuumEvaporationModels::nearVacuumWang::nearVacuumWang
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
        dimTemperature,
        modelDict
    ),
    referencePressure_
    (
        "referencePressure",
        dimensionSet(1, -1, -2, 0, 0, 0, 0),
        modelDict.subDict("nearVacuumWangCoeffs")
    ),
    referenceTemperature_
    (
        "referenceTemperature",
        dimTemperature,
        modelDict.subDict("nearVacuumWangCoeffs")
    ),
    molarMass_
    (
        "molarMass",
        dimensionSet(1, 0, 0, 0, -1, 0, 0),
        modelDict.subDict("nearVacuumWangCoeffs")
    ),
    latentHeatVap_
    (
        "latentHeatVap",
        dimensionSet(0, 2, -2, 0, 0, 0, 0),
        modelDict.subDict("nearVacuumWangCoeffs")
    ),
    liquidusTemperature_
    (
        "Tliquidus",
        dimTemperature,
        materialDict.subDict("metal")
    ),
    thresholdTemperatureMin_
    (
        "thresholdTemperatureMin",
        dimTemperature,
        modelDict.subDict("nearVacuumWangCoeffs")
    ),
    thresholdTemperatureMax_
    (
        "thresholdTemperatureMax",
        dimTemperature,
        modelDict.subDict("nearVacuumWangCoeffs")
    ),
    R_
    (
        "R",
        dimensionSet(1, 2, -2, -1, -1, 0, 0),
        8.314
    ),
    relations_
    (
        referencePressure_.value(),
        referenceTemperature_.value(),
        molarMass_.value(),
        latentHeatVap_.value(),
        chamberPressure_.value(),
        chamberTemperature_.value()
    ),
    boilingTemperature_(0.0),
    activationTemperature_(0.0),
    Tk0_(0.0),
    Tk1_(0.0)
{
    if (chamberPressure_.value() <= 0)
    {
        FatalIOErrorInFunction(modelDict)
            << "nearVacuumWang requires chamberPressure > 0"
            << exit(FatalIOError);
    }

    if
    (
        thresholdTemperatureMin_.value() <= 0
     || thresholdTemperatureMax_.value()
        <= thresholdTemperatureMin_.value()
    )
    {
        FatalIOErrorInFunction(modelDict)
            << "Invalid threshold-temperature search bracket"
            << exit(FatalIOError);
    }

    const scalar denominator =
        1.0/referenceTemperature_.value()
      - R_.value()
       /(latentHeatVap_.value()*molarMass_.value())
       *std::log
        (
            chamberPressure_.value()/referencePressure_.value()
        );

    if (denominator <= 0)
    {
        FatalIOErrorInFunction(modelDict)
            << "Could not determine a positive boiling temperature from "
            << "the configured saturation-pressure reference."
            << exit(FatalIOError);
    }

    boilingTemperature_ = 1.0/denominator;
    activationTemperature_ =
        max(liquidusTemperature_.value(), boilingTemperature_);

    const bool tk0Ok =
        relations_.thresholdTemperature
        (
            0.05,
            thresholdTemperatureMin_.value(),
            thresholdTemperatureMax_.value(),
            Tk0_
        );

    const bool tk1Ok =
        relations_.thresholdTemperature
        (
            1.0,
            thresholdTemperatureMin_.value(),
            thresholdTemperatureMax_.value(),
            Tk1_
        );

    if (!tk0Ok || !tk1Ok)
    {
        FatalIOErrorInFunction(modelDict)
            << "Could not bracket Tk0/Tk1 in ["
            << thresholdTemperatureMin_ << ", "
            << thresholdTemperatureMax_ << "]. "
            << "Widen the physically justified search bracket."
            << exit(FatalIOError);
    }

    if (Tk0_ > Tk1_)
    {
        FatalIOErrorInFunction(modelDict)
            << "Invalid transition thresholds: Tk0=" << Tk0_
            << " > Tk1=" << Tk1_
            << exit(FatalIOError);
    }

    if (activationTemperature_ < Tk0_)
    {
        FatalIOErrorInFunction(modelDict)
            << "The active liquid-surface temperature "
            << activationTemperature_ << " K lies below Tk0=" << Tk0_
            << " K. This would require the Ma<0.05 weak-evaporation regime, "
            << "which is intentionally not extrapolated by this model."
            << exit(FatalIOError);
    }

    Info<< "    nearVacuumWang thresholds" << nl
        << "        boilingTemperature   = " << boilingTemperature_ << " K" << nl
        << "        liquidusTemperature  = " << liquidusTemperature_ << nl
        << "        activationTemperature= " << activationTemperature_ << " K" << nl
        << "        Tk0 (Ma=0.05)        = " << Tk0_ << " K" << nl
        << "        Tk1 (Ma=1)           = " << Tk1_ << " K" << nl
        << "        active regime        = "
        << (activationTemperature_ >= Tk1_ ? "sonic" : "transition-to-sonic")
        << endl;
}


Foam::vacuumEvaporationModels::nearVacuumWang::~nearVacuumWang()
{}


void Foam::vacuumEvaporationModels::nearVacuumWang::evaluateState
(
    const scalar temperature,
    scalar& massFluxValue,
    scalar& recoilPressureValue
) const
{
    massFluxValue = 0.0;
    recoilPressureValue = 0.0;

    if (temperature < activationTemperature_)
    {
        return;
    }

    scalar Ma = 1.0;

    if (temperature < Tk1_)
    {
        if (!relations_.solveMachNumber(temperature, Ma))
        {
            FatalErrorInFunction
                << "Could not solve the Wang transition state at T="
                << temperature << " K"
                << exit(FatalError);
        }
    }

    const knudsenJumpState state = relations_.jumpState(Ma);
    const scalar pSat = relations_.saturationPressure(temperature);

    massFluxValue =
        state.massFluxRatio*pSat
       *std::sqrt
        (
            molarMass_.value()
           /(2.0*M_PI*R_.value()*temperature)
        );

    recoilPressureValue =
        max
        (
            state.recoilCoefficient*pSat - chamberPressure_.value(),
            scalar(0)
        );
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::nearVacuumWang::saturationPressure
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
Foam::vacuumEvaporationModels::nearVacuumWang::massFlux
(
    const volScalarField& T
) const
{
    tmp<volScalarField> tResult
    (
        new volScalarField
        (
            IOobject
            (
                "nearVacuumWangMassFlux",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE,
                false
            ),
            mesh_,
            dimensionedScalar
            (
                "zeroMassFlux",
                dimensionSet(1, -2, -1, 0, 0, 0, 0),
                0.0
            )
        )
    );

    volScalarField& result = tResult.ref();
    scalarField& values = result.primitiveFieldRef();
    const scalarField& temperatures = T.primitiveField();

    forAll(values, celli)
    {
        scalar recoil = 0.0;
        evaluateState(temperatures[celli], values[celli], recoil);
    }

    forAll(result.boundaryField(), patchi)
    {
        scalarField& patchValues = result.boundaryFieldRef()[patchi];
        const scalarField& patchT = T.boundaryField()[patchi];

        forAll(patchValues, facei)
        {
            scalar recoil = 0.0;
            evaluateState(patchT[facei], patchValues[facei], recoil);
        }
    }

    return tResult;
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::nearVacuumWang::recoilPressure
(
    const volScalarField& T
) const
{
    tmp<volScalarField> tResult
    (
        new volScalarField
        (
            IOobject
            (
                "nearVacuumWangRecoilPressure",
                mesh_.time().timeName(),
                mesh_,
                IOobject::NO_READ,
                IOobject::NO_WRITE,
                false
            ),
            mesh_,
            dimensionedScalar
            (
                "zeroPressure",
                dimPressure,
                0.0
            )
        )
    );

    volScalarField& result = tResult.ref();
    scalarField& values = result.primitiveFieldRef();
    const scalarField& temperatures = T.primitiveField();

    forAll(values, celli)
    {
        scalar mDot = 0.0;
        evaluateState(temperatures[celli], mDot, values[celli]);
    }

    forAll(result.boundaryField(), patchi)
    {
        scalarField& patchValues = result.boundaryFieldRef()[patchi];
        const scalarField& patchT = T.boundaryField()[patchi];

        forAll(patchValues, facei)
        {
            scalar mDot = 0.0;
            evaluateState(patchT[facei], mDot, patchValues[facei]);
        }
    }

    return tResult;
}


Foam::tmp<Foam::volScalarField>
Foam::vacuumEvaporationModels::nearVacuumWang::evaporationHeatFlux
(
    const volScalarField& T
) const
{
    return latentHeatVap_*massFlux(T);
}

// ************************************************************************* //
