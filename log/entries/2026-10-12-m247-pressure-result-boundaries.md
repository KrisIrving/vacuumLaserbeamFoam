# PCG retained; static full-track envelope and open boundaries reviewed

Reviewed M247_m247-pressure-pair-20261012-150149_review.tar.gz. Both native
solvers completed50--60us with identical pre-edit restart hash
8bcd47e4322a6db54b66b0b45aa9b9c02844abdd459c80db1a0fdef97bd8d64,
same solver/library hashes, all archive file hashes matching. Manifest is
incomplete only because the collector rejected the extra first continuity
line at a nonzero restart; comparison.json was absent. The first local and
global continuity terms are roundoff (5.82e-16,-3.73e-18); cumulative
3.19e-8 carries the prior run. Fixed parser to accept precisely that
pre-pressure startup pattern, while retaining count/finite checks. Native
fields and CFD need not be rerun. Recollection from archived logs, geometry,
run metadata yields a complete comparison.

PCG2788.89s, GAMG3806.36s per10us; GAMG is36.48% slower. Pressure section
1433.52s versus2498.52s (74.3% slower). PCG964/GAMG963 steps. Both have
zero nonlinear thermal cap hits, normal residuals and linear T/pressure
convergence. At55us depth117um,width264um; at60us depth123um,width270um
for both, to6um cell-centre resolution. No molten metal leaves fine region.
GAMG also produces different peak temperature/recoil at60us; geometry
agreement alone would not rescue its performance. Retain PCG for future
work; no long-run acceleration claim from this method.

Boundary audit is in tests/m247Performance/TRACK_BOUNDARY_AUDIT.md.
Most urgent: observed molten forward reach129um at60us exceeds terminal
fine-strip allowance120um. Current mesh cannot justify the entire1.5mm
track with6um cells in the molten front. Top T backflow and use of
totalPressure directly on p_rgh also need a measured sensitivity/BC choice.
Do not proceed with the current static mesh to1500us. New mesh must be
checked and benchmarked; no unvalidated mapping of existing partitions.

Prepared a separate V2 template and RunM247TrackPilotV2. Fine x extends
to1680um; the fine substrate begins y180um (420um depth) rather than y0.
Expected3,814,272 cells (9.9% fewer). The old200us8um result supports a
326.50um liquidus depth, leaving93.50um historical fine margin in V2;
future1.5mm depth remains unknown. Original material, powder, thermal,
laser and boundary dictionaries are copied unchanged to isolate the mesh.
Native V2 mesh quality/CFD/cost are still pending. Do not transfer old
processor fields to V2 without a validated map.

Eleven targeted Python tests and new Bash syntax pass; no changed CFD solver code. The collector
fix was also exercised against both full native logs from the uploaded
archive. Native boundary revisions have not been run.
