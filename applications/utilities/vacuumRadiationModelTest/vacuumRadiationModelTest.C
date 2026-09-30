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
#include "vacuumRadiationModel.H"

#include <iomanip>
#include <iostream>

using namespace Foam;

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    const IOdictionary vacuumProperties
    (
        IOobject
        (
            "vacuumProperties",
            runTime.constant(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        )
    );

    const dimensionedScalar testTemperature
    (
        "testTemperature",
        dimTemperature,
        vacuumProperties
    );

    const scalar testLiquidFraction =
        readScalar(vacuumProperties.lookup("testLiquidFraction"));

    volScalarField T
    (
        IOobject
        (
            "TradTest",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        testTemperature
    );

    volScalarField liquidFraction
    (
        IOobject
        (
            "liquidFractionRadTest",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        dimensionedScalar("liquidFraction", dimless, testLiquidFraction)
    );

    vacuumRadiationModel radiation(mesh, vacuumProperties);

    tmp<volScalarField> tE = radiation.emissivity(liquidFraction);
    tmp<volScalarField> tQ = radiation.heatFlux(T, liquidFraction);
    tmp<volScalarField> tA = radiation.implicitCoefficient(T, liquidFraction);
    tmp<volScalarField> tB = radiation.explicitFlux(T, liquidFraction);

    std::cout
        << std::setprecision(16)
        << "VACUUM_RADIATION_TEST "
        << testTemperature.value() << " "
        << testLiquidFraction << " "
        << gMax(tE().primitiveField()) << " "
        << gMax(tQ().primitiveField()) << " "
        << gMax(tA().primitiveField()) << " "
        << gMax(tB().primitiveField())
        << std::endl;

    return 0;
}

// ************************************************************************* //
