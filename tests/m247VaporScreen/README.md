# M247 provisional vapor-contribution screen

This is the first M247 material-port gate. It independently evaluates the
ideal multi-component saturation-pressure construction used by the current
nearVacuumWang alloy path.

Run:

    ./tests/m247VaporScreen/Allrun

The test converts wt.% to mole fraction, evaluates each component's
Clausius-Clapeyron pressure, reports ki*Pi(T), vapor-pressure fractions,
mixture vapor molar mass, and the 0.6-Pa mixture boiling temperature.

This is a screening test, not a calibrated M247 vapor-pressure model.
It does not validate thermodynamic activity coefficients, preferential
evaporation, local composition depletion, or final alloy mass loss.

Replace the provisional literature chemistry with the actual powder
certificate before production CFD.
