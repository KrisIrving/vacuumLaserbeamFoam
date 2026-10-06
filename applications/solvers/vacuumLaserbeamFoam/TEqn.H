{
    int iter = 0;
    scalarField residual(epsilon1.primitiveField().size(), 1.0);
    scalar maxResidual = 1.0;
    scalar meanResidual = 1.0;
    //scalar Tresidual = 1.0;

    TRHS *= 0.0;

    rhoCp = rho*cp;
    rhophicp = fvc::interpolate(cp)*rhoPhi;

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
              - fvm::Sp(fvc::ddt(rhoCp) + fvc::div(rhophicp), T)
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
              - fvm::Sp(fvc::ddt(rhoCp) + fvc::div(rhophicp), T)
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

        residual =
            mag
            (
                epsilon1.primitiveField()
              - epsilon1.prevIter().primitiveField()
            );

        maxResidual = gMax(residual);

        meanResidual = gSum(residual*mesh.V())/gSum(mesh.V().field());

        //ddte1 = fvc::ddt(epsilon1);

        Info<< "Correcting epsilon1, mean residual = " << meanResidual
            << ", max residual = " << maxResidual
            << endl;
    }
    while
    (
        (
            ++iter < minTCorr
         // || (meanResidual > epsilonTol.value())
         || (maxResidual > epsilonTol.value())
        )
     && iter <= maxTCorr
    );

    perfThermalCorrectorsStep += iter;
    gradT = fvc::grad(T);
}
