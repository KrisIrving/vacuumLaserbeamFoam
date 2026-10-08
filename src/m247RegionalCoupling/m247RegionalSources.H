// Local delta relative to a global conduction-only prediction, densities W/m3.
#ifndef m247RegionalSources_H
#define m247RegionalSources_H
#include "scalar.H"
#include "error.H"
#include <cmath>
namespace Foam
{
inline scalar m247RegionalSourceDelta(scalar dt,scalar laser,scalar evaporation,
    scalar radiationLoss,scalar advectiveGain,scalar localConduction,scalar mappedGlobalConduction)
{
    if(!std::isfinite(dt)||dt<=0||!std::isfinite(laser)||laser<0||!std::isfinite(evaporation)||evaporation<0
        ||!std::isfinite(radiationLoss)||!std::isfinite(advectiveGain)||!std::isfinite(localConduction)||!std::isfinite(mappedGlobalConduction))
        FatalErrorInFunction<<"Invalid regional source densities"<<exit(FatalError);
    // Radiation can be negative in a radiatively heated environment.
    const scalar delta=dt*(laser-evaporation-radiationLoss+advectiveGain+localConduction-mappedGlobalConduction);
    if(!std::isfinite(delta))FatalErrorInFunction<<"Regional source delta overflow"<<exit(FatalError);
    return delta;
}
}
#endif
