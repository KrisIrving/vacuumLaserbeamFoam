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
#include "vacuumEvaporationModel.H"
#include <iomanip>
#include <iostream>

using namespace Foam;

int main(int argc, char *argv[])
{
    #include "setRootCase.H"
    #include "createTime.H"
    #include "createMesh.H"

    const IOdictionary transportProperties
    (
        IOobject
        (
            "transportProperties",
            runTime.constant(),
            mesh,
            IOobject::MUST_READ,
            IOobject::NO_WRITE
        )
    );

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

    volScalarField T
    (
        IOobject
        (
            "TmodelTest",
            runTime.timeName(),
            mesh,
            IOobject::NO_READ,
            IOobject::NO_WRITE
        ),
        mesh,
        testTemperature
    );

    autoPtr<vacuumEvaporationModel> evaporationModel
    (
        vacuumEvaporationModel::New
        (
            mesh,
            vacuumProperties,
            transportProperties
        )
    );

    tmp<volScalarField> tPsat = evaporationModel->saturationPressure(T);
    tmp<volScalarField> tMassFlux = evaporationModel->massFlux(T);
    tmp<volScalarField> tRecoil = evaporationModel->recoilPressure(T);
    tmp<volScalarField> tHeatFlux = evaporationModel->evaporationHeatFlux(T);

    const scalar pSat = gMax(tPsat().primitiveField());
    const scalar massFlux = gMax(tMassFlux().primitiveField());
    const scalar recoil = gMax(tRecoil().primitiveField());
    const scalar heatFlux = gMax(tHeatFlux().primitiveField());

    std::cout
        << std::setprecision(16)
        << "EVAP_MODEL_TEST "
        << testTemperature.value() << " "
        << pSat << " "
        << massFlux << " "
        << recoil << " "
        << heatFlux << std::endl;

    return 0;
}

// ************************************************************************* //
