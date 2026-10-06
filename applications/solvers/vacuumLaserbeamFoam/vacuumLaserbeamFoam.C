/*---------------------------------------------------------------------------*\
  =========                 |
  \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox
   \\    /   O peration     |
    \\  /    A nd           | www.openfoam.com
     \\/     M anipulation  |
-------------------------------------------------------------------------------
    Copyright (C) 2011-2017 OpenFOAM Foundation
    Copyright (C) 2020 OpenCFD Ltd.
-------------------------------------------------------------------------------
License
    This file is part of OpenFOAM.

    OpenFOAM is free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    OpenFOAM is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
    FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
    for more details.

    You should have received a copy of the GNU General Public License
    along with OpenFOAM.  If not, see <http://www.gnu.org/licenses/>.

Application
    vacuumLaserbeamFoam

Group
    grpMultiphaseSolvers

Description
    Vacuum-aware laser melt-pool solver under active development. The current
    legacyAnisimov evaporation model is intentionally physics-equivalent to the
    hard-coded LaserbeamFoam V3.0 recoil/cooling expressions. It retains the two-phase
    incompressible VoF description of the metallic substrate and numerical gas phase,
    with optional mesh motion and mesh topology changes including adaptive
    re-meshing.
Authors
    
    Tom Flint, UoM.
    Philip Cardiff, UCD.
    Gowthaman Parivendhan, UCD.
    Joe Robson, UoM.
    Petar Cosic, UCD
    Simon Rodriguez, UCD

\*---------------------------------------------------------------------------*/

#include "fvCFD.H"
#include "dynamicFvMesh.H"
#include "isoAdvection.H"
#include "CMULES.H"
#include "EulerDdtScheme.H"
#include "localEulerDdtScheme.H"
#include "CrankNicolsonDdtScheme.H"
#include "subCycle.H"
#include "immiscibleIncompressibleTwoPhaseMixture.H"
#include "incompressibleInterPhaseTransportModel.H"
#include "turbulentTransportModel.H"
#include "pimpleControl.H"
#include "fvOptions.H"
#include "CorrectPhi.H"
#include "fvcSmooth.H"
#include "dynamicRefineFvMesh.H"

#include "Polynomial.H"
#include "laserHeatSource.H"
#include "vacuumEvaporationModel.H"
#include "vacuumRadiationModel.H"

#include <chrono>

// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

int main(int argc, char *argv[])
{
    argList::addNote
    (
        "Solver for two incompressible, isothermal immiscible fluids"
        " using VOF phase-fraction based interface capturing.\n"
        "With optional mesh motion and mesh topology changes including"
        " adaptive re-meshing."
    );

    #include "postProcess.H"

    #include "addCheckCaseOptions.H"
    #include "setRootCaseLists.H"
    #include "createTime.H"
    #include "createDynamicFvMesh.H"
    #include "initContinuityErrs.H"
    #include "createDyMControls.H"
    #include "createFields.H"
    #include "MULES/createAlphaFluxes.H"
    #include "initCorrectPhi.H"
    #include "createUfIfPresent.H"

    typedef std::chrono::steady_clock perfClock;

    scalar perfAlphaTotal = 0.0;
    scalar perfPropsTotal = 0.0;
    scalar perfLaserTotal = 0.0;
    scalar perfMomentumTotal = 0.0;
    scalar perfThermalTotal = 0.0;
    scalar perfPressureTotal = 0.0;
    scalar perfStepTotal = 0.0;
    label perfStepCount = 0;
    label perfThermalCorrectorsTotal = 0;

    if (interfaceTrackingScheme == "MULES")
    {
        if (!LTS)
        {
            #include "MULES/CourantNo.H"
            #include "setInitialDeltaT.H"
        }
    }
    else if (interfaceTrackingScheme == "isoAdvector")
    {
        #include "isoAdvector/porousCourantNo.H"
        #include "setInitialDeltaT.H"
    }

    // * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //
    Info<< "\nStarting time loop\n" << endl;

    while (runTime.run())
    {
        #include "readControls.H"
        #include "readDyMControls.H"

        if (interfaceTrackingScheme == "MULES")
        {
            if (LTS)
            {
                #include "MULES/setRDeltaT.H"
            }
            else
            {
                #include "MULES/CourantNo.H"
                #include "MULES/alphaCourantNo.H"
                #include "MULES/setDeltaT.H"
            }
        } 
        else if (interfaceTrackingScheme == "isoAdvector")
        {
            #include "isoAdvector/porousCourantNo.H"
            #include "isoAdvector/porousAlphaCourantNo.H"
            #include "isoAdvector/setDeltaT.H"
        }
        
        ++runTime;

        Info<< "Time = " << runTime.timeName() << nl << endl;

        const perfClock::time_point perfStepStart = perfClock::now();
        scalar perfAlphaStep = 0.0;
        scalar perfPropsStep = 0.0;
        scalar perfLaserStep = 0.0;
        scalar perfMomentumStep = 0.0;
        scalar perfThermalStep = 0.0;
        scalar perfPressureStep = 0.0;
        label perfThermalCorrectorsStep = 0;

        // --- Pressure-velocity PIMPLE corrector loop
        while (pimple.loop())
        {

            const perfClock::time_point perfAlphaStart = perfClock::now();

            if (interfaceTrackingScheme == "MULES")
            {
                #include "MULES/firstIter.H"
                #include "MULES/alphaControls.H"
                #include "MULES/alphaEqnSubCycle.H"
            } 
            else if (interfaceTrackingScheme == "isoAdvector")
            {
                #include "isoAdvector/firstIter.H"
                #include "isoAdvector/alphaControls.H"
                #include "isoAdvector/alphaEqnSubCycle.H"
            }

            perfAlphaStep += std::chrono::duration<scalar>
            (
                perfClock::now() - perfAlphaStart
            ).count();

            const perfClock::time_point perfPropsStart = perfClock::now();
            #include "updateProps.H"
            perfPropsStep += std::chrono::duration<scalar>
            (
                perfClock::now() - perfPropsStart
            ).count();

            // Update the laser deposition field
            const perfClock::time_point perfLaserStart = perfClock::now();
            laser.updateDeposition
            (
                alpha_filtered, n_filtered, electrical_resistivity
            );
            perfLaserStep += std::chrono::duration<scalar>
            (
                perfClock::now() - perfLaserStart
            ).count();

            const perfClock::time_point perfMixtureStart = perfClock::now();
            mixture.correct();
            perfPropsStep += std::chrono::duration<scalar>
            (
                perfClock::now() - perfMixtureStart
            ).count();

            if (pimple.frozenFlow())
            {
                continue;
            }

            const perfClock::time_point perfMomentumStart = perfClock::now();
            #include "UEqn.H"
            perfMomentumStep += std::chrono::duration<scalar>
            (
                perfClock::now() - perfMomentumStart
            ).count();

            const perfClock::time_point perfThermalStart = perfClock::now();
            #include "TEqn.H"
            perfThermalStep += std::chrono::duration<scalar>
            (
                perfClock::now() - perfThermalStart
            ).count();

            // --- Pressure corrector loop
            const perfClock::time_point perfPressureStart = perfClock::now();
            while (pimple.correct())
            {
                #include "pEqn.H"
            }
            perfPressureStep += std::chrono::duration<scalar>
            (
                perfClock::now() - perfPressureStart
            ).count();

            if (pimple.turbCorr())
            {
                turbulence->correct();
            }
        }

        const scalar perfThisStep = std::chrono::duration<scalar>
        (
            perfClock::now() - perfStepStart
        ).count();

        if (performanceDiagnostics)
        {
            perfAlphaTotal += perfAlphaStep;
            perfPropsTotal += perfPropsStep;
            perfLaserTotal += perfLaserStep;
            perfMomentumTotal += perfMomentumStep;
            perfThermalTotal += perfThermalStep;
            perfPressureTotal += perfPressureStep;
            perfStepTotal += perfThisStep;
            perfThermalCorrectorsTotal += perfThermalCorrectorsStep;
            ++perfStepCount;
        }

        // Update the melt history
        const volScalarField& alphaMetal = 
            mesh.lookupObject<volScalarField>("alpha.metal");
        condition = pos(alphaMetal - 0.5) * pos(epsilon1 - 0.5);
        meltHistory += condition;

        runTime.write();

        if (performanceDiagnostics && runTime.outputTime())
        {
            const scalar accounted =
                perfAlphaTotal
              + perfPropsTotal
              + perfLaserTotal
              + perfMomentumTotal
              + perfThermalTotal
              + perfPressureTotal;

            Info<< "PERF_DIAGNOSTICS"
                << " time=" << runTime.value()
                << " steps=" << perfStepCount
                << " thermalCorrectors=" << perfThermalCorrectorsTotal
                << " stepWall_s=" << perfStepTotal
                << " alpha_s=" << perfAlphaTotal
                << " props_s=" << perfPropsTotal
                << " laser_s=" << perfLaserTotal
                << " momentum_s=" << perfMomentumTotal
                << " thermal_s=" << perfThermalTotal
                << " pressure_s=" << perfPressureTotal
                << " other_s=" << max(perfStepTotal - accounted, scalar(0))
                << endl;

            perfAlphaTotal = 0.0;
            perfPropsTotal = 0.0;
            perfLaserTotal = 0.0;
            perfMomentumTotal = 0.0;
            perfThermalTotal = 0.0;
            perfPressureTotal = 0.0;
            perfStepTotal = 0.0;
            perfStepCount = 0;
            perfThermalCorrectorsTotal = 0;
        }

        if (writeVacuumDiagnostics && runTime.outputTime())
        {
            const scalar depositedPower =
                fvc::domainIntegrate(laser.deposition()).value();

            const scalar interfaceArea =
                fvc::domainIntegrate(mag(gradAlpha)).value();

            const scalar evaporationPower =
                fvc::domainIntegrate
                (
                    Qv*mag(gradAlpha)*thermalDamper
                ).value();

            const scalar radiationPower =
                fvc::domainIntegrate
                (
                    Qrad*mag(gradAlpha)*thermalDamper
                ).value();

            // Continuum-surface-force equivalent of the recoil traction used
            // in UEqn. The laser/keyhole axis in this case is y; Wang labels
            // the corresponding build-depth direction z.
            const vector recoilForce =
                fvc::domainIntegrate(pVap*gradAlpha*damper).value();

            scalar interfacePVapMax = 0.0;
            const scalarField& alphaI = alpha1.primitiveField();
            const scalarField& pVapI = pVap.primitiveField();

            forAll(alphaI, celli)
            {
                if (alphaI[celli] > 0.01 && alphaI[celli] < 0.99)
                {
                    interfacePVapMax =
                        max(interfacePVapMax, pVapI[celli]);
                }
            }
            reduce(interfacePVapMax, maxOp<scalar>());

            Info<< "VACUUM_DIAGNOSTICS"
                << " time=" << runTime.value()
                << " Tmax=" << gMax(T.primitiveField())
                << " Umax=" << gMax(mag(U.primitiveField()))
                << " pVapMax=" << gMax(pVap.primitiveField())
                << " interfacePVapMax=" << interfacePVapMax
                << " QvMax=" << gMax(Qv.primitiveField())
                << " depositedPower=" << depositedPower
                << " evaporationPower=" << evaporationPower
                << " radiationPower=" << radiationPower
                << " interfaceArea=" << interfaceArea
                << " recoilForceX=" << recoilForce.x()
                << " recoilForceY=" << recoilForce.y()
                << " recoilForceZ=" << recoilForce.z()
                << endl;
        }

        // Write ray paths to VTK files
        if (runTime.outputTime())
        {
            laser.writeRayPathsToVTK();
        }

        runTime.printExecutionTime(Info);
    }

    // Write a VTK series file for easy-opening of the ray files
    laser.writeRayPathVTKSeriesFile();

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
