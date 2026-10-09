## 2026-10-09: real fixed-local/full-domain melt pair

094616 thermophysics archive:15manifest hashes/sizes verified; native build and
20step serial/MPI2 gates independently rechecked. Melt fraction0->1->0;
max energyresidual8.9928e-15J, finalserial/MPIE difference8.8818e-16J,
phase/conduction2..3correctors. This confirms infrastructure, not LPBF speed.

Priority changed to direct realistic physics/cost evidence. RunLocalMeltPair
reuses the complete vacuumLaserbeamFoam physics, not the experimental regional
enthalpy closure. Same180us checkpoint,8um,48ranks,180..190us continuous interval,
identical laser/material/thermal controls; corrected-ray flags on in both.
Fullheight fixedlocal submesh retains original cells/resolution. Bounds cover
active material, gasjet and laser path plus96um padding in x/z. No halo sweep.
Reject no-reduction crop, active initialcut, changed initialfield/geometry,
invalid native snapshots, missing diagnostics, incomplete solver/mesh checks.
Initial internal cells are matched at1pm coordinates with volume checks.

Cut T/alpha/epsilon/U values held from the checkpoint; p_rgh fixedFluxPressure.
Retains original top atmospheric pressure outlet and bottom BC. This is an
EXPLICIT short-window boundary approximation, not advancing global thermal
coupling. Default solver remains unchanged unless localMeltBoundaryAudit true.
Candidate cut state/flux recorded EACH timestep, not only stored output.
Same-ROI field RMS/max errors and metal/liquid/meltcentre extents at185/190us;
existing surface-connected alpha=.5 extractor measures matching keyhole depth.
Whole-domain diagnostics are scope-labelled; differing totalinterface areas
must not be mistaken for retained-region physical error. No invented physical
error tolerance or production approval. Real speedup only after native pair.
Includes job/loop/module costs, prep/postprocessing separately; no new moving
or global thermal overhead hidden as a production speedup.

One Ubuntu command,source never simulated in place:
  git pull --ff-only origin feat/m247-material-port
  ./tests/m247Performance/RunLocalMeltPair
Optional source path is first argument if checkpoint is on /media rather than
repository tutorial. Builds optics,solver and read-only native snapshot helper;
2h wall budget per solver case, whole MPI process group terminated on timeout;
all logs/partial reports bundled on failure. Send ONE
M247_local-melt-pair-<timestamp>_review.tar.gz. Large snapshotCSV remain on Ubuntu,
not in reviewarchive. This uses8um first to isolate domain effects before4um.

200Python tests and Bash syntax/raw-LF checks PASS; native added utility and
solver diagnostic build/run pending Ubuntu. Next after actual evidence: replace
held reservoir with advancing global thermal state and conservative exchange,
then translating window handoff. Do not promote fixedcrop to1.5..2mm production.

