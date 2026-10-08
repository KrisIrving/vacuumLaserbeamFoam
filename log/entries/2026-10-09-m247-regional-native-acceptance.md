
## 2026-10-09: bounded native regional acceptance ready for Ubuntu

RunRegionalAcceptance now builds m247RegionalCouplingAudit and generates its own
16-cell thermalRegion/80-cell flowRegion fixtures (fully liquid metal/cold gas,
uniform1580K across interface; manufactured, not equilibrium physics). Local mesh
crosses coarse interface. Runs positive and negative source ledgers, pressure
projection, thermal/moment transfer, serial and two-rank MPI in one command.
No prior powder-case directory or archived checkpoint required.

Native gate checks exact cell counts, preserved constant alpha and uniform T,
source component/global correction energy, finite pressure continuity, unchanged
all case inputs, expected correction+.00039J/-.00024J and serial/MPI agreement.
Native stages record RUNNING before launch, then return code/error.10min shared
runtime budget stops process group on timeout/interruption; build budget5min.
Failure/incomplete exit0 cannot masquerade as success. INT130/TERM143 retained.
One uniquely named review tar.gz includes logs, build/binary provenance, original
fixture inputs, input hashes, reports and final completion status. No field dumps
from production and no production case touched. No resume/overwrite of run folders.

Fixed potential pure-alpha roundoff rejection: native/Python gathering normalizes
by geometric covered row volume after full coverage-to-mesh.V check; constant1
is retained rather than exceeding1 by geometric division roundoff. No fraction
clipping. Scatter remains integrated-delta conservation checked against mesh.V.

172Python tests and Bash syntax pass. New native C++ remains uncompiled locally.
This is the next required Ubuntu checkpoint, not an LPBF parameter screen or a
regional production simulation. Pass means native interface viability; it does
NOT validate actual momentum/VOF/ray/source generation or a24h/full-track speedup.

Run from project repository after pull and sourcing OpenFOAM2512:
./tests/m247Performance/RunRegionalAcceptance
Default build2jobs, MPI2ranks, 16/80cells. Build5min + native stage shared10min caps,
plus short setup/packaging; actual elapsed unknown until Ubuntu. Send the single
M247_regional-acceptance-<timestamp>_review.tar.gz even on failure. If pass, proceed
to actual local CFD/source timestep without further interface parameter screens.
