# Refresh new laser header links before consumer compilation

User compiler output from laser-profile-185645 shows laserHeatSource.H was
found through src/laserHeatSource/lnInclude, but its new laserPerformance.H
include was not found there. The new header exists in the committed library
source. The direct build wrapper omitted an explicit incremental lnInclude
refresh. No phase/CFD results were produced by this failed solver build.
The archive itself has not been provided locally; diagnosis uses the supplied
compiler output, not a claimed archive integrity check.

RunLaserProfile now runs wmakeLnInclude -u . and checks the header is readable
before building the library and clean solver. The library Allwmake entry also
refreshes the links and propagates errors. Existing failures remain packaged;
no manual removal of build directories or source files is required.

Next: pull and rerun RunLaserProfile, which creates a fresh timestamped archive.
Actual Ubuntu rebuild remains pending. Local42 Python tests and Bash syntax
checks pass; a mocked existing-lnInclude refresh/failure test validates build
dispatch. No solver/ray-physics change in this repair.

OpenFOAM build-script update option reference:
https://develop.openfoam.com/Development/OpenFOAM-plus/-/blob/integration-TUD/wmake/scripts/makeFiles
