// Shared startup/runtime validation. The caller supplies meltingDict and
// the phaseTemperatureBlendHalfWidth variable owned by createFields.H.
phaseTemperatureBlendHalfWidth =
    meltingDict.lookupOrDefault<scalar>("phaseTemperatureBlendHalfWidth", 0);
if (!(phaseTemperatureBlendHalfWidth >= 0 && phaseTemperatureBlendHalfWidth < 0.04))
{
    FatalErrorInFunction
        << "phaseTemperatureBlendHalfWidth must satisfy 0 <= width < 0.04"
        << exit(FatalError);
}
if
(
    phaseTemperatureBlendHalfWidth > 0
 && !meltingDict.lookupOrDefault<bool>("boundedEnthalpyCorrection", false)
)
{
    FatalErrorInFunction
        << "Experimental phase blending requires boundedEnthalpyCorrection"
        << exit(FatalError);
}
