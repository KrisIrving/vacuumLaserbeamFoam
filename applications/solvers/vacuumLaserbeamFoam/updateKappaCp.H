{
    const scalarField& alpha1I = alpha1;
    const scalarField& TI = T;
    scalarField& kappaI = kappa;
    scalarField& cpI = cp;

    forAll(kappaI, celli)
    {
        const scalar boundedAlpha =
            max(min(alpha1I[celli], scalar(1)), scalar(0));

        scalar metalKappa = polykappa_m.value(TI[celli]);
        scalar metalCp = polycp_m.value(TI[celli]);

        if (useClampedLinearMetalThermalProperties)
        {
            const scalar boundedTemperature =
                max
                (
                    min(TI[celli], Tliquidus1.value()),
                    Tsolidus1.value()
                );

            const scalar liquidFraction =
                (boundedTemperature - Tsolidus1.value())
               /(Tliquidus1.value() - Tsolidus1.value());

            metalKappa =
                metalKappaSolidus
              + liquidFraction
               *(metalKappaLiquidus - metalKappaSolidus);

            metalCp =
                metalCpSolidus
              + liquidFraction
               *(metalCpLiquidus - metalCpSolidus);
        }

        kappaI[celli] =
            boundedAlpha*metalKappa
          + (1.0 - boundedAlpha)*polykappa_g.value(TI[celli]);

        cpI[celli] =
            boundedAlpha*metalCp
          + (1.0 - boundedAlpha)*polycp_g.value(TI[celli]);
    }

    kappa.correctBoundaryConditions();
    cp.correctBoundaryConditions();
}
