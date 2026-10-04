# M247 Wang constitutive gate

This regression couples the literature MAR-M247 powder chemistry fallback with
the optional Mondal et al. (Materials 16 (2023) 50) pure-element vapor-pressure
relations and the frozen Wang Knudsen/common-atmosphere solver.

It is deliberately a **constitutive test**, not a CFD validation.

The test checks:
- 0.6 Pa chamber pressure;
- 1537/1631 K provisional solidus/liquidus;
- evaporation inactive below liquidus;
- mixture pSat and Wang mDot/recoil/qEvap at selected temperatures;
- 298 K versus 1343.15 K Wang far-field gas-temperature sensitivity;
- pSat independence from chamber gas temperature;
- boiling/Tk0/Tk1 thresholds.

The 1343.15 K experimental metal preheat is not silently equated to the
far-field gas temperature. Both assumptions are tested explicitly.

Run after rebuilding the modified evaporation-model library:

    ./tests/m247WangConstitutive/Allrun
