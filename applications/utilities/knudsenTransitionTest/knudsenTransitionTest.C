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

#include "fvCFD.H"
#include "knudsenTransitionRelations.H"

#include <iomanip>
#include <iostream>

using namespace Foam;
using namespace Foam::vacuumEvaporationModels;

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"

    const scalar pRef = 1.0e5;
    const scalar TRef = 3500.0;
    const scalar molarMass = 0.05;
    const scalar latentHeat = 6.0e5;
    const scalar ambientTemperature = 300.0;
    const scalar surfaceTemperature = 3000.0;

    // Independently generated Eq. (16)-(17) reference states at Te=3000 K.
    const scalar targetMa[] = {0.05, 0.5, 1.0};
    const scalar ambientPressure[] =
    {
        59403.51400772722,
        5079.126204780357,
        869.2696694468876
    };

    for (label i = 0; i < 3; ++i)
    {
        knudsenTransitionRelations relations
        (
            pRef,
            TRef,
            molarMass,
            latentHeat,
            ambientPressure[i],
            ambientTemperature
        );

        scalar recoveredMa = -1;
        const bool machOk =
            relations.solveMachNumber(surfaceTemperature, recoveredMa);

        scalar recoveredTemperature = -1;
        const bool temperatureOk =
            relations.thresholdTemperature
            (
                targetMa[i],
                1000.0,
                5000.0,
                recoveredTemperature
            );

        const scalar M2 =
            relations.shockMachNumber(surfaceTemperature, targetMa[i]);

        std::cout
            << std::setprecision(16)
            << "KNUDSEN_TRANSITION_TEST "
            << targetMa[i] << " "
            << ambientPressure[i] << " "
            << recoveredMa << " "
            << recoveredTemperature << " "
            << M2 << " "
            << (machOk ? 1 : 0) << " "
            << (temperatureOk ? 1 : 0)
            << std::endl;
    }

    return 0;
}

// ************************************************************************* //
