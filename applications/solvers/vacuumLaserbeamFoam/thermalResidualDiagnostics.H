// Final nonlinear residual only; no extra reductions inside the corrector loop.
// Alpha bins locate the problem, and do not change the stopping criterion.
{
    scalar gasMax = 0, interfaceMax = 0, metalMax = 0;
    label aboveTolerance = 0, worstCell = -1;
    forAll(residual, celli)
    {
        if (alpha1[celli] <= 0.01) gasMax = max(gasMax, residual[celli]);
        else if (alpha1[celli] < 0.99)
            interfaceMax = max(interfaceMax, residual[celli]);
        else metalMax = max(metalMax, residual[celli]);
        if (residual[celli] > epsilonTol.value()) ++aboveTolerance;
        if (worstCell < 0 && residual[celli] == maxResidual) worstCell = celli;
    }
    reduce(gasMax, maxOp<scalar>());
    reduce(interfaceMax, maxOp<scalar>());
    reduce(metalMax, maxOp<scalar>());
    reduce(aboveTolerance, sumOp<label>());
    label owner = worstCell >= 0 ? Pstream::myProcNo() : Pstream::nProcs();
    reduce(owner, minOp<label>());

    // Deterministically select one cell when several tie for the global max.
    std::array<scalar, 13> sample{};
    if (Pstream::myProcNo() == owner)
    {
        const vector& centre = mesh.C()[worstCell];
        sample = {{centre.x(), centre.y(), centre.z(), alpha1[worstCell],
            T[worstCell], T.prevIter()[worstCell], epsilon1[worstCell],
            epsilon1.prevIter()[worstCell], cp[worstCell], LatentHeat[worstCell],
            TSolidus[worstCell], TLiquidus[worstCell], scalar(worstCell)}};
    }
    for (unsigned i = 0; i < sample.size(); ++i)
        reduce(sample[i], sumOp<scalar>());
    Info<< "THERMAL_RESIDUAL_DIAGNOSTICS time=" << runTime.value()
        << " correctors=" << iter
        << " boundedEnthalpy=" << boundedEnthalpyCorrection
        << " phaseBlendHalfWidth=" << phaseTemperatureBlendHalfWidth
        << " maxResidual=" << maxResidual << " meanResidual=" << meanResidual
        << " phaseTemperatureResidual_K=" << phaseTemperatureResidual
        << " phaseTemperatureChecked=" << boundedEnthalpyCorrection
        << " gasMax=" << gasMax << " interfaceMax=" << interfaceMax
        << " metalMax=" << metalMax << " aboveTolerance=" << aboveTolerance
        << " ownerRank=" << owner << " localCell=" << sample[12]
        << " x=" << sample[0] << " y=" << sample[1] << " z=" << sample[2]
        << " alphaMetal=" << sample[3] << " T=" << sample[4]
        << " phaseOverrideWeight="
        << phaseTemperatureOverrideWeight(sample[3], phaseTemperatureBlendHalfWidth)
        << " Tprev=" << sample[5] << " epsilon=" << sample[6]
        << " epsilonPrev=" << sample[7] << " cp=" << sample[8]
        << " latentHeat=" << sample[9] << " solidus=" << sample[10]
        << " liquidus=" << sample[11]
        << " sensibleLatentRatio="
        << sample[8]*(sample[11]-sample[10])/max(sample[9], SMALL) << endl;
}
