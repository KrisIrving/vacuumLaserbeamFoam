
## 2026-10-09 005127: native regional interface PASS; local flow time loop next

Verified all review archive manifest SHA256/size entries and independently reparsed
four native logs. Build commit1317a579, solverSHA256b86d72777af4b708f3f8ebcadf84ac4577f7f15f770d7e4006307de785de7b9b.
Native compile, mesh generation, serial and MPI2 execution all complete. Wrapper
exit0; source inputs unchanged; acceptance elapsed1.865s excludes build/packaging.
16global/80localcells; constant/uniformT error0. Energy corrections+.00039J and
-.00024J; maximum ledger residual1.573e-15J, inverse error1.715e-16. Projection
initialdiv833.33/s ->serial4.687e-12/s, MPI6.617e-12/s. Serial/MPI ledgers agree.
This validates native transfer/projection/supplied-source interfaces only; it is
not a measured LPBF acceleration or physical melting/solidification benchmark.

Added m247LocalFlowAudit: persistent local fields, initial coarse alpha import,
20time steps with actual isoAdvector and its consistent density mass flux,
variable-density conservative laminar momentum and pressure projection. Pressure
kernel now operates on caller-owned U/rho/p/phi and actual inverse momentum diagonal.
Velocity correction uses rAU*reconstruct(deltaPhi/rAUf) for variable coefficients;
face phi remains authoritative. Default full LPBF solver unchanged.

Flow gate covers200us withdt10us,CFL<=.25, no mesh motion, no alpha clipping/snap.
Checks each step and cumulative metal-volume/mass versus physical boundary flux,
finite alpha bounds and pressure continuity. At least1e-12m3 interface change
required; collector rejects no-op progression, missing steps, drift or serial/MPI
inventory mismatch. No thermal equation, recoil, surface tension, radiation,
evaporation, laser/source generation or moving-history update in this cold-flow
gate. Do not infer thermodynamic moment advection from its VOF mass ledger.

177Python tests and Bash syntax pass. Existing interface module was native-confirmed;
new time-loop/refactored pressure C++ still requires Ubuntu compilation/runtime.
Next single bounded native run:
./tests/m247Performance/RunRegionalAcceptance --flow
Generatedfixture only,2MPI ranks,build5min+allnative stages shared10min caps.
Send ONE M247_regional-flow-step-<timestamp>_review.tar.gz even on failure.
This is an implementation integration gate, not a parameter sweep. After pass,
connect heat/moment advection, actual optical/source terms and moving global history.
