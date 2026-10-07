# Build failure confirmed and declaration order repaired

Archive M247_build-phase-blend-20261007-172208_review.tar.gz hashes verified.
The build at commit 704c97b returned 2, captured build.log/environment and
started no CFD. Both normal and postProcess expansions of createFields.H
failed because updateProps.H referenced phaseTemperatureBlendHalfWidth
before readControls.H declared it inside the time loop. This was introduced
by our continuous-phase candidate patch. The new build gate exposed it.

createFields.H now owns a mutable scalar initialised from the existing mesh
fvSolution MELTING dictionary before its first updateProps.H call. A shared
readPhaseBlendControls.H validates range and bounded-enthalpy prerequisite
both at startup and when readControls.H reloads settings. The runtime code
assigns that scalar instead of creating a shadowed local const. This covers
both createFields inclusion paths and applies the requested closure during
initial pressure/property construction. Default width remains zero.

Existing 35 Python tests pass. Manual scope/include audit checks startup,
postProcess and runtime paths. These are not an OpenFOAM C++ compilation;
the Ubuntu rebuild and physical phase-probe validation remain pending.
Next action: pull, BuildPhaseBlend, send its one automatic archive.

API reference used for mesh fvSolution access:
https://api.openfoam.com/2512/classFoam_1_1fvMesh.html
