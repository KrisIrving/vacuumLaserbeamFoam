# M247 moving window: first native pass and frozen wake retention

Reviewed M247_moving-window-20261008-160259_review.tar.gz:27 file hashes/sizes
verified; wrapper0,missing_files empty. Reconstructed raw mapping log agrees
with report. Small preflight passed. Real eight topology updates completed:
756000 initial -> peak1320480 cells; update sum58.397611577s; native commands
sum324.090973s. Window coverage and positive coarsening873600 cumulative cells
passed. Max relative linear proxy error4.23985e-11; nonlinear direct alpha*T
max7.86513e-12 and alpha*epsilon max2.98639e-13. Eight checkMesh snapshots have
native concavity failure only; scoped coplanar-roundoff qualification passes.
No full CFD, enthalpy/flux/isoAdvector mapping or measured speedup established.

Added opt-in RunMovingWindow --protect-wake (named protected review archive),
mask union with hot/molten metal and conservatively mapped initial-wake marker.
Use case solidus1537K, epsilon1>=1e-4, alpha>1e-6. Strict settled level1 wake
coverage, external-wake presence, marker-volume conservation, original source
and existing cold coarsening/geometry/budget gates. Small preflight includes48
hot cells outside all windows to check retention before large case copying.
No clipping, enthalpy surrogate correction or physical equations changed.
Permanent marker is frozen-audit-only: transient release after cooling and
conservative energy/flow/VOF transfer remain required for production integration.

118 Python tests pass including protected coverage, absent evidence, marker
loss, external coverage and small-case input generation. Native changed C++
compilation/execution requires Ubuntu. Next one protected run; do not repeat
the already-passed unprotected run or expand optical matrices.
