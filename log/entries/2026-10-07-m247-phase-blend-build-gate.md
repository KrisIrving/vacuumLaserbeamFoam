# Phase blend review: incompatible executable

Archive M247_phase-blend-20261007-170639_review.tar.gz has valid SHA256s.
All three solver jobs completed 16 steps, returncode 0, in about 36–37 s.
The wrapper returned 1 at collection. All jobs used solver SHA256
2633f8e37c6e805087e729212fdd1b4a143be8a3f5943aa63422617848fe6cfc,
matching the previous executable. All 48 thermal records lack
phaseBlendHalfWidth and phaseOverrideWeight. These runs cannot establish
the effect or accuracy of the newly added closure. No physical approval.

The archive does not contain a build log. It cannot distinguish failed build,
skipped rebuild, or a PATH/environment selecting an old executable.
An inspected build-script defect can hide solver compilation failure:
applications/Allwmake previously did not stop on a failing solver build,
and its argument-parser path used WM_PROJECT instead of WM_PROJECT_DIR.
Both are corrected; this is a possible cause, not a demonstrated one.

BuildPhaseBlend directly builds the solver, preserves pipeline failures,
records the selected build environment and build log, then compares PATH's
resolved solver against FOAM_USER_APPBIN and checks compiled diagnostic
markers. It automatically packages results even if build/preflight fails.
RunPhaseBlendProbe performs this static preflight before copying or running
cases. Direct phase-variant run_probe calls also check it. MPI now launches
the verified absolute executable path. The static check is insufficient for
runtime validation; the collector's per-step mode/width gates remain required.

Next: pull and run BuildPhaseBlend only; review its single archive before
repeating CFD. Real OpenFOAM compilation still requires the Ubuntu host.
