# Both local meshes reviewed; scoped coplanar qualification and flux audit

101101 archive:23manifest SHA256/sizes verified, exit2, no listed files missing.
Complete schema2 report. Independently reconciled both selections, refined counts,
mapped moments, native failures and exact concavity diagnostics against raw logs.
Build succeeded on v2512; four-layer result repeats003900 exactly. Coarse moments
match the reused original180us restart. Raw field/mesh copy hashes are recorded
on Ubuntu but large files are not archived for independent cell-level replay.

Four layers:218273selected =>2283911cells; native15101concave flags.
Ten layers:304718selected =>2889026cells; native13607concave flags.
These are37.7631/47.7683pct of global one-level refinement,3.02105/3.82146x original.
Ten layers costs26.49pct more cells. All eight mapped moments pass; bounds[0,1].
Refinement itself takes55.99/70.69s. These preprocessing times are not CFD timings.
Native allGeometry has exactly one failure in each case; face flatness,tets,
positive volumes/determinants and other checks pass. Worst outward plane distances
8.67e-19/8.13e-19m, max relative1.01644e-13 in both, zero above relative1e-9.

Official OpenCFD primitiveMesh check tests face centres and explicitly includes
planar pairs in the concave predicate, with planarCosAngle1e-6. Hex refinement
transitions have coplanar split faces, so the flag does not by itself prove real
inward geometry. This explains the evidence better than treating these15000cells
as macroscopic deformations. Raw native failures remain false, not rewritten.

Added separate geometry qualification: only one concavity failure, no other
native flags, matching count, flatness>=1-1e-12, outward excursion<=1e-15m and
relative<=1e-10. Project screening limits, not official recommendations; does
not approve CFD/production. Both archived cases meet this screening criterion.
No global OpenFOAM checking tolerance or mesh is altered.

Added AuditLocalRestart using retained meshes, no refinement/reconstruction/CFD:
fresh quality check plus unchanged field/mesh hashes, native U/phi/alphaPhi
dimension/finite check, divergence L1/RMS/max/net and phi-versus-flux(U) metrics.
These measurements guide startup flux correction before an expensive pilot.
restart_ready stays false regardless of geometry screening. Native utility writes
no fields; checkMesh rewrites diagnostic sets only. Root logs distinguish all
three cases and automatically package failure/success evidence.

96Python tests and Bash syntax pass. Tests reject real concavity, other mesh
failures, count/nonfinite errors, changed input files; report flux amplification
without accidentally approving restart. Added C++ flux mode needs Ubuntu native
compilation/execution. Next ./tests/m247Performance/AuditLocalRestart; send new
M247_local-restart archive, not another sizing rerun.

Reference: https://api.openfoam.com/2312/primitiveMeshCheck_8C_source.html
(OpenCFD source; no Foundation-version API substituted).
