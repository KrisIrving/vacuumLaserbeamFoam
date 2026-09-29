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

#ifndef knudsenTransitionRelations_H
#define knudsenTransitionRelations_H

#include "scalar.H"

namespace Foam
{
namespace vacuumEvaporationModels
{

struct knudsenJumpState
{
    scalar Ma;
    scalar m;
    scalar temperatureRatio;
    scalar peOverP3;
    scalar p3OverPe;
    scalar massFluxRatio;
    scalar recoilCoefficient;
};


class knudsenTransitionRelations
{
    scalar referencePressure_;
    scalar referenceTemperature_;
    scalar molarMass_;
    scalar latentHeatVap_;
    scalar ambientPressure_;
    scalar ambientTemperature_;
    scalar gasConstant_;
    scalar gamma_;

public:

    knudsenTransitionRelations
    (
        const scalar referencePressure,
        const scalar referenceTemperature,
        const scalar molarMass,
        const scalar latentHeatVap,
        const scalar ambientPressure,
        const scalar ambientTemperature
    );

    scalar saturationPressure(const scalar T) const;

    knudsenJumpState jumpState(const scalar Ma) const;

    // Region-II shock Mach number M2 from Eq. (17), after reducing the
    // velocity relation to a quadratic equation.
    scalar shockMachNumber
    (
        const scalar surfaceTemperature,
        const scalar Ma
    ) const;

    // Logarithmic residual of Eq. (16). A root is the common-atmosphere
    // state compatible with the Knudsen-layer state and ambient condition.
    scalar pressureResidual
    (
        const scalar surfaceTemperature,
        const scalar Ma
    ) const;

    // Same Eq. (16) residual, but with saturation pressure supplied by the
    // caller. This is required for Wang Eqs. (18)-(20), where alloy Pe(T)
    // cannot be represented by one constant Clausius-Clapeyron curve.
    scalar pressureResidualFromSaturation
    (
        const scalar surfaceTemperature,
        const scalar Ma,
        const scalar surfaceSaturationPressure
    ) const;

    // Solve Eq. (16)-(17) for Ma at a prescribed surface temperature.
    // Returns false if [MaMin,MaMax] does not bracket a solution.
    bool solveMachNumber
    (
        const scalar surfaceTemperature,
        scalar& Ma,
        const scalar MaMin = 0.05,
        const scalar MaMax = 1.0,
        const scalar tolerance = 1e-10,
        const label maxIterations = 200
    ) const;

    bool solveMachNumberFromSaturation
    (
        const scalar surfaceTemperature,
        const scalar surfaceSaturationPressure,
        scalar& Ma,
        const scalar MaMin = 0.05,
        const scalar MaMax = 1.0,
        const scalar tolerance = 1e-10,
        const label maxIterations = 200
    ) const;

    // Solve for surface temperature corresponding to a prescribed Ma.
    // Used to obtain Tk0 (Ma=0.05) and Tk1 (Ma=1).
    bool thresholdTemperature
    (
        const scalar targetMa,
        const scalar Tmin,
        const scalar Tmax,
        scalar& temperature,
        const scalar tolerance = 1e-10,
        const label maxIterations = 200
    ) const;
};

} // End namespace vacuumEvaporationModels
} // End namespace Foam

#endif

// ************************************************************************* //
