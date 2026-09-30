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
    componentMode_(false),
    componentNames_(),
    componentMoleFractions_(),
    componentMolarMasses_(),
    componentReferencePressures_(),
    componentReferenceTemperatures_(),
    componentLatentHeats_(),
    componentPressureScale_(1.0),
    boilingTemperature_(0.0),
    activationTemperature_(0.0),
    Tk0_(0.0),
    Tk1_(0.0),
    useSubcriticalCommonBranch_(false)
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

    const dictionary& coeffs = modelDict.subDict("nearVacuumWangCoeffs");

    if (coeffs.found("componentNames"))
    {
        componentMode_ = true;
        componentNames_ = wordList(coeffs.lookup("componentNames"));

        if (componentNames_.empty())
        {
            FatalIOErrorInFunction(modelDict)
                << "componentNames is present but empty."
                << exit(FatalIOError);
        }

        const dictionary& components = coeffs.subDict("components");
        const label nComponents = componentNames_.size();

        componentMoleFractions_.setSize(nComponents, 0.0);
        componentMolarMasses_.setSize(nComponents, 0.0);
        componentReferencePressures_.setSize(nComponents, 0.0);
        componentReferenceTemperatures_.setSize(nComponents, 0.0);
        componentLatentHeats_.setSize(nComponents, 0.0);

        scalarList amountFractions(nComponents, 0.0);
        scalar amountSum = 0.0;

        forAll(componentNames_, componenti)
        {
            const word& componentName = componentNames_[componenti];
            const dictionary& component = components.subDict(componentName);

            const dimensionedScalar massFraction
            (
                "massFraction",
                dimless,
                component
            );
            const dimensionedScalar componentMolarMass
            (
                "molarMass",
                dimensionSet(1, 0, 0, 0, -1, 0, 0),
                component
            );
            const dimensionedScalar componentReferencePressure
            (
                "referencePressure",
                dimPressure,
                component
            );
            const dimensionedScalar componentReferenceTemperature
            (
                "referenceTemperature",
                dimTemperature,
                component
            );
            const dimensionedScalar componentLatentHeat
            (
                "latentHeatVap",
                dimensionSet(0, 2, -2, 0, 0, 0, 0),
                component
            );

            if
            (
                massFraction.value() <= 0
             || componentMolarMass.value() <= 0
             || componentReferencePressure.value() <= 0
             || componentReferenceTemperature.value() <= 0
             || componentLatentHeat.value() <= 0
            )
            {
                FatalIOErrorInFunction(modelDict)
                    << "All component properties must be positive for "
                    << componentName
                    << exit(FatalIOError);
            }

            componentMolarMasses_[componenti] =
                componentMolarMass.value();
            componentReferencePressures_[componenti] =
                componentReferencePressure.value();
            componentReferenceTemperatures_[componenti] =
                componentReferenceTemperature.value();
            componentLatentHeats_[componenti] =
                componentLatentHeat.value();

            // Wang Eq. (18) uses molar fraction ki. The paper tabulates
            // alloy composition by mass fraction, so convert wi -> ki here.
            amountFractions[componenti] =
                massFraction.value()/componentMolarMass.value();
            amountSum += amountFractions[componenti];
        }

        if (amountSum <= SMALL)
        {
            FatalIOErrorInFunction(modelDict)
                << "Invalid component mass fractions."
                << exit(FatalIOError);
        }

        forAll(componentMoleFractions_, componenti)
        {
            componentMoleFractions_[componenti] =
                amountFractions[componenti]/amountSum;
        }

        if
        (
            coeffs.found("alloyReferencePressure")
         || coeffs.found("alloyReferenceTemperature")
        )
        {
            if
            (
                !coeffs.found("alloyReferencePressure")
             || !coeffs.found("alloyReferenceTemperature")
            )
            {
                FatalIOErrorInFunction(modelDict)
                    << "alloyReferencePressure and alloyReferenceTemperature "
                    << "must be supplied together."
                    << exit(FatalIOError);
            }

            const dimensionedScalar alloyReferencePressure
            (
                "alloyReferencePressure",
                dimPressure,
                coeffs
            );
            const dimensionedScalar alloyReferenceTemperature
            (
                "alloyReferenceTemperature",
                dimTemperature,
                coeffs
            );

            scalar rawReferencePressure = 0.0;
            scalar rawReferenceMolarMass = 0.0;
            mixtureProperties
            (
                alloyReferenceTemperature.value(),
                rawReferencePressure,
                rawReferenceMolarMass
            );

            if
            (
                alloyReferencePressure.value() <= 0
             || alloyReferenceTemperature.value() <= 0
             || rawReferencePressure <= VSMALL
            )
            {
                FatalIOErrorInFunction(modelDict)
                    << "Invalid alloy saturation-pressure reference state."
                    << exit(FatalIOError);
            }

            componentPressureScale_ =
                alloyReferencePressure.value()/rawReferencePressure;

            Info<< "        alloy Pe anchor       = "
                << alloyReferencePressure.value() << " Pa at "
                << alloyReferenceTemperature.value() << " K" << nl
                << "        component Pe scale    = "
                << componentPressureScale_ << endl;
        }

        if
        (
            !boilingTemperatureForPressure
            (
                thresholdTemperatureMin_.value(),
                thresholdTemperatureMax_.value(),
                boilingTemperature_
            )
        )
        {
            FatalIOErrorInFunction(modelDict)
                << "Could not bracket the alloy boiling temperature in ["
                << thresholdTemperatureMin_ << ", "
                << thresholdTemperatureMax_ << "]."
                << exit(FatalIOError);
        }
    }
    else
    {
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
    }

    activationTemperature_ =
        max(liquidusTemperature_.value(), boilingTemperature_);

    const bool tk0Ok =
        thresholdTemperatureForState
        (
            0.05,
            thresholdTemperatureMin_.value(),
            thresholdTemperatureMax_.value(),
            Tk0_
        );

    const bool tk1Ok =
        thresholdTemperatureForState
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

    useSubcriticalCommonBranch_ = activationTemperature_ < Tk0_;

    Info<< "    nearVacuumWang thresholds" << nl
        << "        component mode       = "
        << (componentMode_ ? "Wang Eqs. (18)-(20)" : "single-component") << nl
        << "        boilingTemperature   = " << boilingTemperature_ << " K" << nl
        << "        liquidusTemperature  = " << liquidusTemperature_ << nl
        << "        activationTemperature= " << activationTemperature_ << " K" << nl
        << "        Tk0 (Ma=0.05)        = " << Tk0_ << " K" << nl
        << "        Tk1 (Ma=1)           = " << Tk1_ << " K" << nl
        << "        active regime        = "
        << (
            activationTemperature_ >= Tk1_
          ? "sonic"
          : (
                useSubcriticalCommonBranch_
              ? "common-to-sonic (Wang step 4)"
              : "transition-to-sonic"
            )
        )
        << endl;

    if (componentMode_)
    {
        Info<< "        alloy components     =";
        forAll(componentNames_, componenti)
        {
            Info<< " " << componentNames_[componenti]
                << "(k=" << componentMoleFractions_[componenti] << ")";
        }
        Info<< endl;
    }
}


Foam::vacuumEvaporationModels::nearVacuumWang::~nearVacuumWang()
{}


Foam::scalar
Foam::vacuumEvaporationModels::nearVacuumWang::componentSaturationPressure
(
    const label componenti,
    const scalar temperature
) const
{
    if (temperature <= 0)
    {
        FatalErrorInFunction
            << "Surface temperature must be positive."
            << exit(FatalError);
    }

    return
        componentReferencePressures_[componenti]
       *std::exp
        (
            componentLatentHeats_[componenti]
           *componentMolarMasses_[componenti]/R_.value()
           *(1.0/componentReferenceTemperatures_[componenti]
           - 1.0/temperature)
        );
}


void Foam::vacuumEvaporationModels::nearVacuumWang::mixtureProperties
(
    const scalar temperature,
    scalar& saturationPressureValue,
    scalar& mixtureMolarMass
) const
{
    if (!componentMode_)
    {
        saturationPressureValue = relations_.saturationPressure(temperature);
        mixtureMolarMass = molarMass_.value();
        return;
    }

    saturationPressureValue = 0.0;
    scalar molarMassNumerator = 0.0;

    forAll(componentNames_, componenti)
    {
        const scalar partialSaturationPressure =
            componentPressureScale_
           *componentMoleFractions_[componenti]
           *componentSaturationPressure(componenti, temperature);

        saturationPressureValue += partialSaturationPressure;
        molarMassNumerator +=
            componentMolarMasses_[componenti]*partialSaturationPressure;
    }

    if (saturationPressureValue <= VSMALL)
    {
        FatalErrorInFunction
            << "Non-positive alloy saturation pressure at T="
            << temperature << " K"
            << exit(FatalError);
    }

    // Wang Eq. (19).
    mixtureMolarMass = molarMassNumerator/saturationPressureValue;
}


Foam::scalar
Foam::vacuumEvaporationModels::nearVacuumWang::transitionResidual
(
    const scalar temperature,
    const scalar Ma
) const
{
    if (!componentMode_)
    {
        return relations_.pressureResidual(temperature, Ma);
    }

    scalar pSat = 0.0;
    scalar mixtureMolarMass = 0.0;
    mixtureProperties(temperature, pSat, mixtureMolarMass);

    return relations_.pressureResidualFromSaturation
    (
        temperature,
        Ma,
        pSat
    );
}


bool Foam::vacuumEvaporationModels::nearVacuumWang::solveMachNumberForState
(
    const scalar temperature,
    scalar& Ma
) const
{
    const scalar MaMin =
        (useSubcriticalCommonBranch_ && temperature < Tk0_)
      ? 1e-8
      : 0.05;

    if (!componentMode_)
    {
        return relations_.solveMachNumber
        (
            temperature,
            Ma,
            MaMin,
            1.0
        );
    }

    scalar pSat = 0.0;
    scalar mixtureMolarMass = 0.0;
    mixtureProperties(temperature, pSat, mixtureMolarMass);

    return relations_.solveMachNumberFromSaturation
    (
        temperature,
        pSat,
        Ma,
        MaMin,
        1.0
    );
}


bool Foam::vacuumEvaporationModels::nearVacuumWang::thresholdTemperatureForState
(
    const scalar targetMa,
    const scalar Tmin,
    const scalar Tmax,
    scalar& temperature
) const
{
    if (!componentMode_)
    {
        return relations_.thresholdTemperature
        (
            targetMa,
            Tmin,
            Tmax,
            temperature
        );
    }

    const scalar tolerance = 1e-10;
    const label maxIterations = 200;

    scalar lo = Tmin;
    scalar hi = Tmax;
    scalar flo = transitionResidual(lo, targetMa);
    scalar fhi = transitionResidual(hi, targetMa);

    if (mag(flo) <= tolerance)
    {
        temperature = lo;
        return true;
    }

    if (mag(fhi) <= tolerance)
    {
        temperature = hi;
        return true;
    }

    if (flo*fhi > 0)
    {
        return false;
    }

    for (label iter = 0; iter < maxIterations; ++iter)
    {
        const scalar mid = 0.5*(lo + hi);
        const scalar fmid = transitionResidual(mid, targetMa);

        if
        (
            mag(fmid) <= tolerance
         || (hi - lo) <= tolerance*max(mid, scalar(1))
        )
        {
            temperature = mid;
            return true;
        }

        if (flo*fmid <= 0)
        {
            hi = mid;
            fhi = fmid;
        }
        else
        {
            lo = mid;
            flo = fmid;
        }
    }

    temperature = 0.5*(lo + hi);
    return
        mag(transitionResidual(temperature, targetMa))
     <= 10.0*tolerance;
}


bool Foam::vacuumEvaporationModels::nearVacuumWang::boilingTemperatureForPressure
(
    const scalar Tmin,
    const scalar Tmax,
    scalar& temperature
) const
{
    const scalar tolerance = 1e-10;
    const label maxIterations = 200;

    auto pressureResidual =
        [this](const scalar T)
        {
            scalar pSat = 0.0;
            scalar mixtureMolarMass = 0.0;
            mixtureProperties(T, pSat, mixtureMolarMass);
            return std::log(pSat/chamberPressure_.value());
        };

    scalar lo = Tmin;
    scalar hi = Tmax;
    scalar flo = pressureResidual(lo);
    scalar fhi = pressureResidual(hi);

    if (mag(flo) <= tolerance)
    {
        temperature = lo;
        return true;
    }

    if (mag(fhi) <= tolerance)
    {
        temperature = hi;
        return true;
    }

    if (flo*fhi > 0)
    {
        return false;
    }

    for (label iter = 0; iter < maxIterations; ++iter)
    {
        const scalar mid = 0.5*(lo + hi);
        const scalar fmid = pressureResidual(mid);

        if
        (
            mag(fmid) <= tolerance
         || (hi - lo) <= tolerance*max(mid, scalar(1))
        )
        {
            temperature = mid;
            return true;
        }

        if (flo*fmid <= 0)
        {
            hi = mid;
            fhi = fmid;
        }
        else
        {
            lo = mid;
            flo = fmid;
        }
    }

    temperature = 0.5*(lo + hi);
    return mag(pressureResidual(temperature)) <= 10.0*tolerance;
}


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
        if (!solveMachNumberForState(temperature, Ma))
        {
            FatalErrorInFunction
                << "Could not solve the Wang transition state at T="
                << temperature << " K"
                << exit(FatalError);
        }
    }

    const knudsenJumpState state = relations_.jumpState(Ma);

    scalar pSat = 0.0;
    scalar mixtureMolarMass = 0.0;
    mixtureProperties(temperature, pSat, mixtureMolarMass);

    // Eq. (11), expressed with R = Rmol/M from Wang Eq. (20).
    massFluxValue =
        state.massFluxRatio*pSat
       *std::sqrt
        (
            mixtureMolarMass
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
    tmp<volScalarField> tResult
    (
        new volScalarField
        (
            IOobject
            (
                "nearVacuumWangSaturationPressure",
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
        scalar mixtureMolarMass = 0.0;
        mixtureProperties
        (
            temperatures[celli],
            values[celli],
            mixtureMolarMass
        );
    }

    forAll(result.boundaryField(), patchi)
    {
        scalarField& patchValues = result.boundaryFieldRef()[patchi];
        const scalarField& patchT = T.boundaryField()[patchi];

        forAll(patchValues, facei)
        {
            scalar mixtureMolarMass = 0.0;
            mixtureProperties
            (
                patchT[facei],
                patchValues[facei],
                mixtureMolarMass
            );
        }
    }

    return tResult;
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
    // The paper couples evaporation heat loss as m_loss * Lv (Eq. 32).
    // latentHeatVap_ remains the alloy-level heat of evaporation used by the
    // thermal model, while Eqs. (18)-(20) determine Pe(T) and vapor M(T).
    return latentHeatVap_*massFlux(T);
}

// ************************************************************************* //
