
## 2026-10-09 091028: native local flow PASS; passive thermodynamic transport

Manifest bytes/SHA256 verified; independently reparsed serial/MPI20step logs.
Native build/run complete from e114e5d5; solverSHA256df4c273cf7526a63d91aa0f44bd942ed27bdd4deab8adb3b6a138a4f54bfd0c6.
Metal volume3.0e-10 ->3.2e-10m3 matches2.0e-11m3 net inflow. Maximum step volume
residual1.5833e-25m3, mass residual1.1019e-21kg. Interface change2.0e-11m3.
Serial/MPI inventories match; inputs unchanged. Acceptance elapsed0.99234s excludes
build/packaging. Tiny alpha excess<=9.9e-14 is within1e-10 roundoff bound, no clipping.
productionApproved false is expected: this proves cold local time-loop viability,
not LPBF accuracy, actual optical/thermal closure or a production speedup.

Implemented m247ThermalTransport.H: conservative implicit Euler/upwind transport
of sensible energy, latent inventory, unused latent reserve and cp-capacity moments
with the same pre-advection face phi. Carries capacity history independently of
sharper isoAdvector alpha. Capacity is latent+nonnegative reserve, avoiding an
unstable remapped-capacity minus latent subtraction. Cell temperature inverse uses
mapped cp moments and transported latent state, without forcing phase equilibrium.
Each field has a boundary-flux ledger; cumulative total energy includes prescribed
volumetric heat gain and physical boundary energy. Supports signed heat source,
rejects negative moment inventories; no clipping. Energy components remainNO_WRITE.

New --heat mode runs20steps,serial/MPI2,checks existing flow gates plus moment
ledger/source integral and temperature inversion. Prescribed Q1e7W/m3 contributes
1.2e-6J across6e-10m3 domain over200us. This is PASSIVE advection/heat-source transport:
no conduction, latent phase relaxation, thermal-to-flow feedback, ray tracing,
evaporation/radiation or moving/global correction yet. Source is manufactured.
Do not treat it as a validated LPBF heat equation or latent melting model.

181Python tests and Bash syntax pass; new moment FV C++ uncompiled locally.
Next bounded Ubuntu command:
./tests/m247Performance/RunRegionalAcceptance --heat
Send ONE M247_regional-thermal-transport-<timestamp>_review.tar.gz on success/failure.
After this transport contract is native-confirmed, integrate implicit heat conduction,
phase feedback and actual source/moving-global history; do not repeat cold-flow gate.
