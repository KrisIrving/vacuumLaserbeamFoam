{
    int iter = 0;
    scalarField residual(epsilon1.primitiveField().size(), 1.0);
    scalar maxResidual = 1.0;
    scalar meanResidual = 1.0;
    scalar phaseTemperatureResidual = 0;
    //scalar Tresidual = 1.0;

    TRHS *= 0.0;

    rhoCp = rho*cp;
    rhophicp = fvc::interpolate(cp)*rhoPhi;

    // rhoCp/rhophicp are assigned above and stay fixed through this corrector
    // loop. Cache only their explicit transport correction, never T-dependent
    // radiation, evaporation, damping, or latent-heat terms.
    const bool thermalInvariantCache =
        runTime.controlDict().getOrDefault<bool>("thermalInvariantCache", false);
    autoPtr<volScalarField> thermalTransportCorrection;
    if (thermalInvariantCache)
    {
        thermalTransportCorrection.reset
        (
            new volScalarField(fvc::ddt(rhoCp) + fvc::div(rhophicp))
        );
    }
    Info<< "THERMAL_INVARIANT_CACHE schema=1 time=" << runTime.value()
        << " enabled=" << label(thermalInvariantCache) << endl;

    if (boundedEnthalpyCorrection)
    {
        label invalid = 0;
        forAll(residual, celli)
        {
            if
            (
                cp[celli] <= 0 || LatentHeat[celli] <= 0
             || TLiquidus[celli] <= TSolidus[celli]
            ) ++invalid;
        }
        reduce(invalid, sumOp<label>());
        if (invalid)
        {
            FatalErrorInFunction
                << "Enthalpy correction requires positive cp, latent heat"
                << " and melting interval in every cell"
                << exit(FatalError);
        }
    }

    // const volTensorField gradU(fvc::grad(U));
    // volTensorField tau
    // (
    //     ((mixture.mu()*gradU) + (mixture.mu()*gradU.T()))
    //   - ((2.0/3.0)*mixture.mu()*(fvc::div(phi))*I)
    // );

    do
    {
        epsilon1.storePrevIter();
        T.storePrevIter();
        TRHS =
            LatentHeat*((fvc::ddt(rho, epsilon1) + fvc::div(rhoPhi, epsilon1)));

        Qv = evaporationModel->evaporationHeatFlux(T);
        Qrad = radiationModel.heatFlux(T, epsilon1);

        if (damperSwitch)
        {
            scalarField& thermalDamperI = thermalDamper;
            const scalarField& rhoCpI = rhoCp;
            const scalarField& TI = T;
            forAll(thermalDamperI, celli)
            {
                thermalDamperI[celli] =
                    2.0*rhoCpI[celli]
                   /(
                       (rho1.value()*polycp_m.value(TI[celli]))
                     + (rho2.value()*polycp_g.value(TI[celli]))
                   );
            }

            thermalDamper.correctBoundaryConditions();
        }



        

        if (radiationModel.enabled())
        {
            const volScalarField interfaceDelta
            (
                mag(gradAlpha)*thermalDamper
            );

            tmp<volScalarField> tRadImplicit =
                radiationModel.implicitCoefficient(T, epsilon1);
            tmp<volScalarField> tRadExplicit =
                radiationModel.explicitFlux(T, epsilon1);

            // Semi-implicit linearisation of
            // qRad = epsilon*sigma*(T^4 - Tchamber^4).
            fvScalarMatrix TEqn
            (
                fvm::ddt(rhoCp,T)
              + fvm::div(rhophicp, T)
              - (thermalInvariantCache
                ? fvm::Sp(thermalTransportCorrection(), T)
                : fvm::Sp(fvc::ddt(rhoCp) + fvc::div(rhophicp), T))
              - fvm::laplacian(kappa, T)
              + fvm::Sp(tRadImplicit()*interfaceDelta, T)
              //- (tau && gradU) // Viscous dissipation
             ==
                laser.deposition()
              - Qv*interfaceDelta
              + tRadExplicit()*interfaceDelta
              - TRHS
            );

            TEqn.relax();
            TEqn.solve();
        }
        else
        {
            // Preserve the original LaserbeamFoam equation/operation order
            // exactly when radiation is disabled.
            fvScalarMatrix TEqn
            (
                fvm::ddt(rhoCp,T)
              + fvm::div(rhophicp, T)
              - (thermalInvariantCache
                ? fvm::Sp(thermalTransportCorrection(), T)
                : fvm::Sp(fvc::ddt(rhoCp) + fvc::div(rhophicp), T))
              - fvm::laplacian(kappa, T)
              //- (tau && gradU) // Viscous dissipation
             ==
                laser.deposition()
              - Qv*mag(gradAlpha)*thermalDamper
              - TRHS
            );

            TEqn.relax();
            TEqn.solve();
        }

        // T.relax();

        Tcorr = (TLiquidus - TSolidus)*epsilon1 + TSolidus;

        if (boundedEnthalpyCorrection)
        {
            // Account for both latent and sensible enthalpy slopes.
            // Do not weaken the residual tolerance or iteration cap.
            epsilon1 = max
            (
                min
                (
                    epsilon1
                  + (epsilonRel*cp
                    /(LatentHeat + cp*(TLiquidus - TSolidus)))*(T - Tcorr),
                    scalar(1)
                ),
                scalar(0)
            );
        }
        else
        {
            epsilon1 =
                max
                (
                    min
                    (
                        epsilon1 + (epsilonRel*cp/LatentHeat)*(T - Tcorr),
                        scalar(1)
                    ),
                    scalar(0)
                );
        }

        residual =
            mag
            (
                epsilon1.primitiveField()
              - epsilon1.prevIter().primitiveField()
            );

        maxResidual = gMax(residual);

        if (boundedEnthalpyCorrection)
        {
            // Small updates alone can hide under-relaxation. Also enforce
            // the phase relation in kelvin, including the pure-phase bounds.
            phaseTemperatureResidual = 0;
            forAll(residual, celli)
            {
                scalar mismatch = 0;
                if (epsilon1[celli] <= 0)
                    mismatch = max(T[celli] - TSolidus[celli], scalar(0));
                else if (epsilon1[celli] >= 1)
                    mismatch = max(TLiquidus[celli] - T[celli], scalar(0));
                else
                    mismatch = mag(T[celli] - TSolidus[celli]
                        - (TLiquidus[celli]-TSolidus[celli])*epsilon1[celli]);
                phaseTemperatureResidual = max(phaseTemperatureResidual, mismatch);
            }
            reduce(phaseTemperatureResidual, maxOp<scalar>());
        }

        meanResidual = gSum(residual*mesh.V())/gSum(mesh.V().field());

        //ddte1 = fvc::ddt(epsilon1);

        if (thermalCorrectorLogging)
        {
            Info<< "Correcting epsilon1, mean residual = " << meanResidual
                << ", max residual = " << maxResidual << endl;
            if (boundedEnthalpyCorrection)
                Info<< "Phase temperature residual = "
                    << phaseTemperatureResidual << " K" << endl;
        }
    }
    while
    (
        (
            ++iter < minTCorr
         // || (meanResidual > epsilonTol.value())
         || (maxResidual > epsilonTol.value())
         || (boundedEnthalpyCorrection
          && phaseTemperatureResidual > phaseTemperatureTolerance)
        )
     && iter <= maxTCorr
    );

    performance.addThermalCorrectors
    (
        iter, iter > maxTCorr
           && (maxResidual > epsilonTol.value()
            || (boundedEnthalpyCorrection
             && phaseTemperatureResidual > phaseTemperatureTolerance))
    );
    if (thermalResidualDiagnostics)
    {
        #include "thermalResidualDiagnostics.H"
    }
    gradT = fvc::grad(T);
}
