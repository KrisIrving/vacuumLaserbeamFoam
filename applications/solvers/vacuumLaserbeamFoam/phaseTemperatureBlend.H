#ifndef phaseTemperatureBlend_H
#define phaseTemperatureBlend_H

// Numerical regularisation of the historical alpha=0.05 override.
// This changes the mixed-cell closure; it is not a new material property.
inline Foam::scalar phaseTemperatureOverrideWeight
(
    const Foam::scalar alpha, const Foam::scalar halfWidth
)
{
    if (halfWidth == 0) return alpha > 0.05 ? 1 : 0;
    const Foam::scalar s = Foam::max
    (
        Foam::min((alpha - (0.05-halfWidth))/(2*halfWidth), Foam::scalar(1)),
        Foam::scalar(0)
    );
    return s*s*(3-2*s);
}
#endif
