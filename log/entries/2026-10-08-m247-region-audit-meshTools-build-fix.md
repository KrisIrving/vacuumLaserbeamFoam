# Region audit build dependency repair

Ubuntu v2512 compiler output fails before the audit utility can run:
fvCFD.H includes finiteVolume AMI patch/matrix headers, which in turn require
cyclicAMIPolyPatch.H and related meshTools headers. regionAudit/Make/options
included and linked only finiteVolume. This was an omitted build dependency,
not evidence of missing simulation fields or a CFD numerical failure.

Added meshTools/lnInclude and -lmeshTools, matching the existing working
m247CachedSearchTest target's OpenFOAM dependencies. InspectRegionBudget now
cleans only its own regionAudit build before wmake, so the failed dependency
scan/object cannot be reused. No solver/library rebuild, equations, thresholds
or audit semantics change. Existing source and impact fields are reused.

Bash syntax and static build configuration checks pass. Native OpenFOAM
compilation is unavailable locally and remains pending Ubuntu. The user's
compiler output suffices to identify this failure; no additional failed archive
is required. Pull feat/m247-material-port and rerun InspectRegionBudget. It
creates a fresh timestamped directory and automatically packages a new
M247_region-budget-..._review.tar.gz on success or failure.
