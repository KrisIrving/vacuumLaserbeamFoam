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

#include "knudsenTransitionRelations.H"
#include "error.H"

#include <cmath>

namespace Foam
{
namespace vacuumEvaporationModels
{

knudsenTransitionRelations::knudsenTransitionRelations
(
    const scalar referencePressure,
    const scalar referenceTemperature,
    const scalar molarMass,
    const scalar latentHeatVap,
    const scalar ambientPressure,
    const scalar ambientTemperature
)
:
    referencePressure_(referencePressure),
    referenceTemperature_(referenceTemperature),
    molarMass_(molarMass),
    latentHeatVap_(latentHeatVap),
    ambientPressure_(ambientPressure),
    ambientTemperature_(ambientTemperature),
    gasConstant_(8.314),
    gamma_(5.0/3.0)
{
    if
    (
        referencePressure_ <= 0
     || referenceTemperature_ <= 0
     || molarMass_ <= 0
     || latentHeatVap_ <= 0
     || ambientPressure_ <= 0
     || ambientTemperature_ <= 0
    )
    {
        FatalErrorInFunction
            << "All thermodynamic pressures/temperatures/material values must "
            << "be positive for the transition-state solver."
            << exit(FatalError);
    }
}


scalar knudsenTransitionRelations::saturationPressure(const scalar T) const
{
    if (T <= 0)
    {
        FatalErrorInFunction
            << "Surface temperature must be positive."
            << exit(FatalError);
    }

    return
        referencePressure_
       *std::exp
        (
            latentHeatVap_*molarMass_/gasConstant_
           *(1.0/referenceTemperature_ - 1.0/T)
        );
}


knudsenJumpState knudsenTransitionRelations::jumpState(const scalar Ma) const
{
    if (Ma <= 0 || Ma > 1.0)
    {
        FatalErrorInFunction
            << "Knudsen-layer Mach number must satisfy 0 < Ma <= 1."
            << exit(FatalError);
    }

    const scalar pi = M_PI;
    const scalar sqrtPi = std::sqrt(pi);

    knudsenJumpState state;

    state.Ma = Ma;
    state.m = std::sqrt(gamma_/2.0)*Ma;

    const scalar m2 = state.m*state.m;
    const scalar expMinusM2 = std::exp(-m2);
    const scalar erfcM = std::erfc(state.m);

    const scalar Fminus =
        -sqrtPi*state.m*erfcM + expMinusM2;

    const scalar Gminus =
        (2.0*m2 + 1.0)*erfcM
      - (2.0/sqrtPi)*state.m*expMinusM2;

    const scalar sqrtTemperatureRatio =
        std::sqrt(1.0 + (pi/64.0)*m2)
      - (sqrtPi/8.0)*state.m;

    state.temperatureRatio = sqr(sqrtTemperatureRatio);

    if (state.temperatureRatio <= SMALL)
    {
        FatalErrorInFunction
            << "Invalid Knudsen-layer temperature ratio."
            << exit(FatalError);
    }

    const scalar jumpDenominator =
        Fminus + std::sqrt(state.temperatureRatio)*Gminus;

    if (jumpDenominator <= SMALL)
    {
        FatalErrorInFunction
            << "Invalid Knudsen-layer jump denominator."
            << exit(FatalError);
    }

    state.peOverP3 =
        2.0*expMinusM2/jumpDenominator;

    state.p3OverPe = 1.0/state.peOverP3;

    state.massFluxRatio =
        2.0*sqrtPi*state.m
       *state.p3OverPe/sqrtTemperatureRatio;

    state.recoilCoefficient =
        state.p3OverPe*(2.0*m2 + 1.0);

    return state;
}


scalar knudsenTransitionRelations::shockMachNumber
(
    const scalar surfaceTemperature,
    const scalar Ma
) const
{
    const knudsenJumpState state = jumpState(Ma);

    const scalar C =
        std::sqrt(state.temperatureRatio)
       *state.m
       *std::sqrt
        (
            2.0*surfaceTemperature
           /(gamma_*ambientTemperature_)
        );

    // Eq. (17), using
    // 2(M2^2-1)/((gamma+1)M2^2) = C/M2.
    // The physically admissible root has M2 > 1.
    const scalar A = C*(gamma_ + 1.0);

    return
        (A + std::sqrt(A*A + 16.0))/4.0;
}


scalar knudsenTransitionRelations::pressureResidual
(
    const scalar surfaceTemperature,
    const scalar Ma
) const
{
    return pressureResidualFromSaturation
    (
        surfaceTemperature,
        Ma,
        saturationPressure(surfaceTemperature)
    );
}


scalar knudsenTransitionRelations::pressureResidualFromSaturation
(
    const scalar surfaceTemperature,
    const scalar Ma,
    const scalar surfaceSaturationPressure
) const
{
    const knudsenJumpState state = jumpState(Ma);
    const scalar M2 = shockMachNumber(surfaceTemperature, Ma);

    const scalar shockPressureRatio =
        1.0
      + 2.0*gamma_/(gamma_ + 1.0)*(M2*M2 - 1.0);

    const scalar predictedPeOverP1 =
        state.peOverP3*shockPressureRatio;

    const scalar actualPeOverP1 =
        surfaceSaturationPressure/ambientPressure_;

    if (predictedPeOverP1 <= 0 || actualPeOverP1 <= 0)
    {
        FatalErrorInFunction
            << "Non-positive pressure ratio in transition-state solver."
            << exit(FatalError);
    }

    // Log form avoids poor scaling over many orders of pressure.
    return
        std::log(actualPeOverP1)
      - std::log(predictedPeOverP1);
}


bool knudsenTransitionRelations::solveMachNumber
(
    const scalar surfaceTemperature,
    scalar& Ma,
    const scalar MaMin,
    const scalar MaMax,
    const scalar tolerance,
    const label maxIterations
) const
{
    if (MaMin <= 0 || MaMax > 1.0 || MaMin >= MaMax)
    {
        FatalErrorInFunction
            << "Invalid Mach-number bracket ["
            << MaMin << ", " << MaMax << "]"
            << exit(FatalError);
    }

    scalar lo = MaMin;
    scalar hi = MaMax;
    scalar flo = pressureResidual(surfaceTemperature, lo);
    scalar fhi = pressureResidual(surfaceTemperature, hi);

    if (mag(flo) <= tolerance)
    {
        Ma = lo;
        return true;
    }

    if (mag(fhi) <= tolerance)
    {
        Ma = hi;
        return true;
    }

    if (flo*fhi > 0)
    {
        return false;
    }

    for (label iter = 0; iter < maxIterations; ++iter)
    {
        const scalar mid = 0.5*(lo + hi);
        const scalar fmid = pressureResidual(surfaceTemperature, mid);

        if (mag(fmid) <= tolerance || (hi - lo) <= tolerance)
        {
            Ma = mid;
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

    Ma = 0.5*(lo + hi);
    return mag(pressureResidual(surfaceTemperature, Ma)) <= 10.0*tolerance;
}


bool knudsenTransitionRelations::solveMachNumberFromSaturation
(
    const scalar surfaceTemperature,
    const scalar surfaceSaturationPressure,
    scalar& Ma,
    const scalar MaMin,
    const scalar MaMax,
    const scalar tolerance,
    const label maxIterations
) const
{
    if (MaMin <= 0 || MaMax > 1.0 || MaMin >= MaMax)
    {
        FatalErrorInFunction
            << "Invalid Mach-number bracket ["
            << MaMin << ", " << MaMax << "]"
            << exit(FatalError);
    }

    if (surfaceSaturationPressure <= 0)
    {
        FatalErrorInFunction
            << "Surface saturation pressure must be positive."
            << exit(FatalError);
    }

    scalar lo = MaMin;
    scalar hi = MaMax;
    scalar flo = pressureResidualFromSaturation
    (
        surfaceTemperature,
        lo,
        surfaceSaturationPressure
    );
    scalar fhi = pressureResidualFromSaturation
    (
        surfaceTemperature,
        hi,
        surfaceSaturationPressure
    );

    if (mag(flo) <= tolerance)
    {
        Ma = lo;
        return true;
    }

    if (mag(fhi) <= tolerance)
    {
        Ma = hi;
        return true;
    }

    if (flo*fhi > 0)
    {
        return false;
    }

    for (label iter = 0; iter < maxIterations; ++iter)
    {
        const scalar mid = 0.5*(lo + hi);
        const scalar fmid = pressureResidualFromSaturation
        (
            surfaceTemperature,
            mid,
            surfaceSaturationPressure
        );

        if (mag(fmid) <= tolerance || (hi - lo) <= tolerance)
        {
            Ma = mid;
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

    Ma = 0.5*(lo + hi);
    return
        mag
        (
            pressureResidualFromSaturation
            (
                surfaceTemperature,
                Ma,
                surfaceSaturationPressure
            )
        ) <= 10.0*tolerance;
}


bool knudsenTransitionRelations::thresholdTemperature
(
    const scalar targetMa,
    const scalar Tmin,
    const scalar Tmax,
    scalar& temperature,
    const scalar tolerance,
    const label maxIterations
) const
{
    if (Tmin <= 0 || Tmin >= Tmax)
    {
        FatalErrorInFunction
            << "Invalid temperature bracket ["
            << Tmin << ", " << Tmax << "]"
            << exit(FatalError);
    }

    scalar lo = Tmin;
    scalar hi = Tmax;
    scalar flo = pressureResidual(lo, targetMa);
    scalar fhi = pressureResidual(hi, targetMa);

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
        const scalar fmid = pressureResidual(mid, targetMa);

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
        mag(pressureResidual(temperature, targetMa))
     <= 10.0*tolerance;
}

} // End namespace vacuumEvaporationModels
} // End namespace Foam

// ************************************************************************* //
