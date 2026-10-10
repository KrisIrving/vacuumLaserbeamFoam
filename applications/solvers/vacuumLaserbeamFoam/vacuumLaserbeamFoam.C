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
#include "m247MovingRefineFvMesh.H"

#include "Polynomial.H"
#include "laserHeatSource.H"
#include "vacuumEvaporationModel.H"
#include "vacuumRadiationModel.H"

#include "vacuumPerformance.H"
#include "phaseTemperatureBlend.H"

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
    if (isA<m247MovingRefineFvMesh>(mesh))
    {
        refCast<m247MovingRefineFvMesh>(mesh).initializeMaskState();
    }
    #include "frozenLaserProbe.H"
    #include "MULES/createAlphaFluxes.H"
    #include "initCorrectPhi.H"
    #include "createUfIfPresent.H"

    vacuumPerformance performance(performanceDiagnostics, runTime.value());

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

    #include "laserRefreshState.H"

    while (runTime.run())
    {
        performance.beginStep();
        performance.start(vacuumPerformance::controls);
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

        performance.stop(vacuumPerformance::controls);

        // --- Pressure-velocity PIMPLE corrector loop
        while (pimple.loop())
        {

            performance.start(vacuumPerformance::alpha);

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

            performance.stop(vacuumPerformance::alpha);

            performance.start(vacuumPerformance::props);
            #include "updateProps.H"
            performance.stop(vacuumPerformance::props);

            // Update the laser deposition field
            performance.start(vacuumPerformance::laser);
            #include "laserRefreshUpdate.H"
            performance.stop(vacuumPerformance::laser);

            performance.start(vacuumPerformance::props);
            mixture.correct();
            performance.stop(vacuumPerformance::props);

            if (pimple.frozenFlow())
            {
                continue;
            }

            performance.start(vacuumPerformance::momentum);
            #include "UEqn.H"
            performance.stop(vacuumPerformance::momentum);

            performance.start(vacuumPerformance::thermal);
            #include "TEqn.H"
            performance.stop(vacuumPerformance::thermal);

            // --- Pressure corrector loop
            performance.start(vacuumPerformance::pressure);
            while (pimple.correct())
            {
                #include "pEqn.H"
            }
            performance.stop(vacuumPerformance::pressure);

            if (pimple.turbCorr())
            {
                turbulence->correct();
            }
        }

        performance.start(vacuumPerformance::history);
        // Update the melt history
        const volScalarField& alphaMetal =
            mesh.lookupObject<volScalarField>("alpha.metal");
        condition = pos(alphaMetal - 0.5) * pos(epsilon1 - 0.5);
        meltHistory += condition;
        performance.stop(vacuumPerformance::history);

        performance.start(vacuumPerformance::fieldWrite);
        runTime.write();
        performance.stop(vacuumPerformance::fieldWrite);

        performance.start(vacuumPerformance::diagnostics);
        #include "localMeltBoundaryAudit.H"
        if (isA<m247MovingRefineFvMesh>(mesh))
        {
            refCast<m247MovingRefineFvMesh>(mesh).reportPilotState();
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

        performance.stop(vacuumPerformance::diagnostics);

        performance.start(vacuumPerformance::rayIO);
        // Write ray paths to VTK files
        if (runTime.outputTime())
        {
            laser.writeRayPathsToVTK();
        }

        performance.stop(vacuumPerformance::rayIO);

        performance.start(vacuumPerformance::executionLog);
        runTime.printExecutionTime(Info);
        performance.stop(vacuumPerformance::executionLog);
        performance.endStep();
        if (runTime.outputTime()) performance.report(runTime.value());
    }

    // Write a VTK series file for easy-opening of the ray files
    laser.writeRayPathVTKSeriesFile();

    Info<< "End\n" << endl;

    return 0;
}


// ************************************************************************* //
