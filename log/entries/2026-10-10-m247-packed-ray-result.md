## 2026-10-10 160619: packed broadcast exact, no overall saving; optical load architecture

Archive complete, wrapper exit0,missing files0; all manifest SHA256 checked.
Native library/solver/wire-check utility compiled successfully.48-rank wire
roundtrip passed all4payload sizes. Both frozen180us captures/traces completed
before transient jobs; Deposition/rayQ/input fields, power326.66753538336195W
and optical work matched exactly, no CFD advancement. Both10us834step full
runs complete, thermal/measurement/packed equivalence gates true,source unchanged.
All sampled fields/diagnostics/keyhole outputs identical; max18thermal
correctors,mean14.54676259,zero cap hits. Numerical acceptance at these sampled
states is not production or long-track acceptance.

Solver baseline1628.91063s(27.1485min),packed1691.15014s(28.1858min),
speedup0.963197: candidate3.8209%longer. Laser841.25042->850.43047s(+1.091%),
thermal540.14689->564.97453s(+4.597%),pressure129.90471->152.58129s(+17.456%).
One sequential pair does not establish systematic regression; it establishes
no measured total acceleration. Do not promote packed mode or repeat this pair.
Default packedRayBroadcastfalse and thermalInvariantCachefalse retained;
every-step laser refresh remains mandatory after molten-interface lag failure.

Independent archived rank rows show root0 trace3.73610/3.73677s,gather
820.99912/838.49231s,broadcast9.83095/0.83007s. Representation reduced the
root broadcast timer substantially, but only ~9s compared with1629s job cost;
root gather includes waiting for tracing and communication. Worker broadcast
mean717.719/724.344s is mostly consistent with wait at synchronization, NOT
a direct measurement of payload transport. Timers on different ranks/stages
must not be summed to infer a critical path or pure MPI bandwidth.
Baseline rank44 trace446.26385s,rank46 trace300.68923s;top2~48.825%of aggregate
trace time. Candidate top2~49.336%. Rank44advances309257364,rank46advances
264607646 (~60.67%of945834767total), unchanged exactly. Rank44 alone ~15.7x
mean per-rank advances. This strongly supports addressing work concentration;
packed serialization does not address it. Baseline laser51.694%,thermal33.192%.

Development decision: stop transmission-format and thermal-coefficient micro
trials. Next architectural target is optical work distribution independent of
CFD mesh partition, preserving per-step input updates and deposition return
by global cell identity. Previous rayQ-weighted CFD Scotch was slower and
failed physics gates; do not repeat it or treat the same repartition as a fix.
An optical-only partition must exchange alpha_filtered,n_filtered,resistivity
from CFD owners each step, run corrected handoff/termination and return deposited
energy to CFD cell owners with explicit conservation/duplicate-ownership audits.
Current code has no such separate optical mesh or mapping. No implementation,
performance gain or full-track approval claimed by this checkpoint.

Next prototype gates: conservative cell ownership/mapping on the same mesh;
frozen optical inputs/deposition/power/termination validation, then10us full
physics/cost comparison including map/trace/return costs. This is a coupled
algorithm implementation, not a sweep of packet/threshold settings. One archive
per executable stage; official OpenFOAM utilities,normal completion,no wclean/
timeout/kill. No new Ubuntu test requested until prototype is ready.

