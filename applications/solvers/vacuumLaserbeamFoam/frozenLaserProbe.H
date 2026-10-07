// Opt-in diagnostic, before flux correction and the time loop. Normal runs
// retain the original three-argument update/report API.
{
    const word frozenMode = runTime.controlDict().lookupOrDefault<word>
        ("frozenLaserProbe", "off");
    if (frozenMode != "off")
    {
        if (frozenMode != "capture" && frozenMode != "trace")
        {
            FatalErrorInFunction << "frozenLaserProbe must be off, capture or trace"
                << exit(FatalError);
        }
        if (frozenMode == "capture")
        {
            volScalarField frozenAlpha
            (
                IOobject("frozenAlphaInput", runTime.timeName(), mesh,
                    IOobject::NO_READ, IOobject::NO_WRITE), alpha_filtered
            );
            volVectorField frozenNormal
            (
                IOobject("frozenNormalInput", runTime.timeName(), mesh,
                    IOobject::NO_READ, IOobject::NO_WRITE), n_filtered
            );
            volScalarField frozenResistivity
            (
                IOobject("frozenResistivityInput", runTime.timeName(), mesh,
                    IOobject::NO_READ, IOobject::NO_WRITE), electrical_resistivity
            );
            if (!frozenAlpha.write() || !frozenNormal.write()
                || !frozenResistivity.write())
            {
                FatalErrorInFunction << "Cannot write frozen optical inputs"
                    << exit(FatalError);
            }
            Info<< "FROZEN_LASER_CAPTURE schema=1 time=" << runTime.value()
                << " calls=0" << endl;
        }
        else
        {
            volScalarField frozenAlpha(IOobject("frozenAlphaInput",
                runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh);
            volVectorField frozenNormal(IOobject("frozenNormalInput",
                runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh);
            volScalarField frozenResistivity(IOobject("frozenResistivityInput",
                runTime.timeName(), mesh, IOobject::MUST_READ, IOobject::NO_WRITE), mesh);
            const scalarField beforeT(T.primitiveField());
            const scalarField beforeAlpha(alpha1.primitiveField());
            const scalarField beforeEpsilon(epsilon1.primitiveField());
            const vectorField beforeU(U.primitiveField());
            laser.updateDeposition(frozenAlpha, frozenNormal, frozenResistivity, false);
            laser.reportPerformance();
            if (!laser.deposition().write()
                || !mesh.lookupObject<volScalarField>("rayQ").write())
            {
                FatalErrorInFunction << "Cannot write frozen optical outputs"
                    << exit(FatalError);
            }
            Ostream& frozenInfo = Info();
            const auto oldPrecision = frozenInfo.precision();
            frozenInfo.precision(17);
            frozenInfo << "FROZEN_LASER_DIAGNOSTICS schema=1 time=" << runTime.value()
                << " calls=1 advancedTime=0"
                << " Tchange=" << gMax(mag(T.primitiveField()-beforeT))
                << " alphaChange=" << gMax(mag(alpha1.primitiveField()-beforeAlpha))
                << " epsilonChange=" << gMax(mag(epsilon1.primitiveField()-beforeEpsilon))
                << " Uchange=" << gMax(mag(U.primitiveField()-beforeU))
                << " depositedPower=" << fvc::domainIntegrate(laser.deposition()).value()
                << endl;
            frozenInfo.precision(oldPrecision);
        }
        Info<< "End\n" << endl;
        return 0;
    }
}
