# Current optimized solver: Wang304L full-history ray-count suite

User requests multiple simplification levels to choose a configuration for M247.
Added RunWangRaySuite: four sequential0..140us4um512k-cell48-rank histories,
16 radial rings and96/48/24/12 angular seeds (1536/768/384/192 rays).
All use current bounded enthalpy iteration at tight1e-5/0.001K tolerances,
zero phase blending, cached traversal, corrected handoff/termination,
every-step optics and unchanged Wang304L physics/Fe optics.
No library/solver changes and no automatic native rebuild or timeout.

Official OpenFOAM commands create one mesh/partition/initial state; copied
variant initial hashes are checked before CFD. Fresh timestamped directories
leave original Wang validation and M247 results intact. Solver/load preflight,
binary and source hashes, full logs and dictionaries are archived on failure.
Connected3D alpha0.5 depth and reconstructed pressure surfaces use existing
Wang extraction scripts. Beam axis is-y here: signed y surface force is axial,
not z; scalar integral(p dS) is retained separately. Equivalent recoil stage
is75us after first32um depth crossing. Current baseline also compares to frozen
76.2318us, Wang~75us and x-ray~70us; no empirical coefficient retuning.

Offline collection reports full histories, thermal residual gates, cap hits,
metal liquid volume integral(alpha*epsilon dV), Tmax, deposition/evaporation,
recoil and section/job costs. User5%/5%/10% budgets apply to nonzero reference
sample relative errors, with absolute/peak-normalised errors also retained.
Fastest passing converged candidate is only a recommendation for M247
confirmation; full paper comparison and M247 transfer remain unverified.
production_approved stays false. Native execution is Ubuntu-only and pending.

Checks caught dictionary ownership (performanceDiagnostics is in
vacuumProperties), actual refresh diagnostic key interval, and lexical vs
numeric OpenFOAM general time-directory order; corrected before handoff.
Python harness/parser tests and Bash syntax pass. No CFD results claimed.
