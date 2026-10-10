// Opt-in approximation: retain the last deposition between guarded refreshes.
// Flow, interface, properties, evaporation and thermal solves still run normally.
const dictionary& laserRefreshDict = runTime.controlDict();
const label laserRefreshInterval =
    laserRefreshDict.getOrDefault<label>("laserRefreshIntervalSteps", 1);
const scalar laserRefreshMaxAge =
    laserRefreshDict.getOrDefault<scalar>("laserRefreshMaxAge", 0);
const scalar laserRefreshMaxAlpha =
    laserRefreshDict.getOrDefault<scalar>("laserRefreshMaxAlphaChange", 0.1);
const scalar laserRefreshMaxMotion =
    laserRefreshDict.getOrDefault<scalar>("laserRefreshMaxCellDisplacement", 0.25);
if (laserRefreshInterval < 1 || laserRefreshInterval > 4
 || (laserRefreshInterval > 1
     && (!(laserRefreshMaxAge > 0) || !(laserRefreshMaxAlpha > 0)
         || !(laserRefreshMaxMotion > 0))))
{
    FatalIOErrorInFunction(laserRefreshDict)
        << "Invalid experimental laser refresh controls: interval1..4; "
        << "positive age/alpha/motion bounds required when interval>1"
        << exit(FatalIOError);
}
const label laserStepIndex = runTime.timeIndex();
const scalar laserSourceAge = laserLastRefreshIndex < 0
    ? 0 : runTime.value() - laserLastRefreshTime;
bool laserDoRefresh = laserRefreshInterval == 1
    || laserLastRefreshIndex < 0
    || laserLastAttemptIndex == laserStepIndex // every additional PIMPLE pass
    || laserStepIndex - laserLastRefreshIndex >= laserRefreshInterval
    || runTime.outputTime()
    || mesh.changing()
    || laserRefreshAlpha.size() != alpha_filtered.size();
// A local mesh/cache condition must not split ranks around collectives.
if (laserRefreshInterval > 1) reduce(laserDoRefresh, orOp<bool>());
scalar laserAlphaChange = 0;
scalar laserMotionCells = 0;
if (laserRefreshInterval > 1 && !laserDoRefresh)
{
    laserAlphaChange = gMax
    (
        mag(alpha_filtered.primitiveField() - laserRefreshAlpha)
    );
    const scalarField& laserCellVolumes = mesh.V();
    const scalar laserMinCellLength = pow(gMin(laserCellVolumes), 1.0/3.0);
    laserMotionCells = gMax(mag(U.primitiveField()))*laserSourceAge
        /max(laserMinCellLength, VSMALL);
    laserDoRefresh = laserSourceAge >= laserRefreshMaxAge
        || laserAlphaChange >= laserRefreshMaxAlpha
        || laserMotionCells >= laserRefreshMaxMotion;
}
if (laserDoRefresh)
{
    laser.updateDeposition(alpha_filtered, n_filtered, electrical_resistivity);
    laserLastRefreshIndex = laserStepIndex;
    laserLastRefreshTime = runTime.value();
    if (laserRefreshInterval > 1)
        laserRefreshAlpha = alpha_filtered.primitiveField();
}
laserLastAttemptIndex = laserStepIndex;
Info<< "LASER_REFRESH_DIAGNOSTICS schema=1 time=" << runTime.value()
    << " interval=" << laserRefreshInterval
    << " refreshed=" << label(laserDoRefresh)
    << " heldAge_s=" << (laserDoRefresh ? scalar(0) : laserSourceAge)
    << " preRefreshAge_s=" << laserSourceAge
    << " maxAlphaChange=" << laserAlphaChange
    << " displacementCells=" << laserMotionCells
    << " productionApproved=0" << endl;
