IOdictionary solutionDict
(
    IOobject
    (
        "fvSolution",
        runTime.system(),
        runTime,
        IOobject::MUST_READ
    )
);

dictionary& meltingDict = solutionDict.subDict("MELTING");

const label minTCorr(readLabel(meltingDict.lookup("minTempCorrector")));

const label maxTCorr(readLabel(meltingDict.lookup("maxTempCorrector")));

const dimensionedScalar epsilonTol
(
    readScalar(meltingDict.lookup("epsilonTolerance"))
);

const dimensionedScalar epsilonRel
(
    readScalar(meltingDict.lookup("epsilonRelaxation"))
);

const bool thermalCorrectorLogging =
    meltingDict.lookupOrDefault<bool>("thermalCorrectorLogging", true);

// Experimental correction: same interior fixed point, different iteration.
const bool boundedEnthalpyCorrection =
    meltingDict.lookupOrDefault<bool>("boundedEnthalpyCorrection", false);
const bool thermalResidualDiagnostics =
    meltingDict.lookupOrDefault<bool>("thermalResidualDiagnostics", false);
const scalar phaseTemperatureTolerance =
    meltingDict.lookupOrDefault<scalar>("phaseTemperatureTolerance", 0.01);

if
(
    boundedEnthalpyCorrection
 && (epsilonRel.value() <= 0 || epsilonRel.value() > 1
     || phaseTemperatureTolerance <= 0)
)
{
    FatalErrorInFunction
        << "boundedEnthalpyCorrection requires 0 < epsilonRelaxation <= 1"
        << " and positive phaseTemperatureTolerance (K)"
        << exit(FatalError);
}

const bool damperSwitch =
    meltingDict.lookupOrDefault<bool>("damperSwitch", false);
