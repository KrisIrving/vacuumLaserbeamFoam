# Restart continuity defect; copied phi projection and bounded pilot

104821archive12SHA256/sizes verified, wrapper0, no missing files. Independently
reconciled all native moment/flux/concavity and fresh geometry records against
the report. Native checker build succeeded; source/field hashes recorded unchanged.
Scoped geometry qualification passes all cases, raw native concavity stays false.

Coarse divL1/RMS/max =0.0266445/12.4486/12498.0 per second.
Four-layer =88759.3/516417/82984974; ten-layer=93421.8/517827/82984974.
Four-layer L1 amplification is about3.33million and RMS about41484x. Refined
net flux8.28e-9/6.69e-9m3/s versus coarse5.50e-12. Internal zero-flux face
counts are zero throughout; don't assume omitted zero faces. Umax76.4862m/s
and material moments unchanged. Mapped phi is not restart-ready. alphaFluxAbs
is zero in all three cases, so this is not evidence of a newly broken history field.

Added explicit native -project (requires-restart): rebuild phi from mapped U,
five constant-coefficient nonorthogonal Laplace solves, subtract equation flux,
write onlyphi. Fixed-potential outlets follow fixed p_rgh patches; zero gradient
elsewhere; require an outlet. q dimensionsL2/T, not physical pressure. No U or
thermodynamic field write. Existing read-only checker options remain read-only.

Added RunLocalFluxPilot: verify audited source/copy hashes, operate on fresh
localRefine4 copy, protected-file hashes, reread writtenphi, screen divergence
against coarse baseline. Failure blocks CFD. If passed, decompose48ranks and
run180.0-180.2us with15minute CFD budget plusgrace. Reconcile timers/diagnostics,
check thermal convergence/no caps and native final finite/bounded/static fields.
Automatic named archive includes full solver log/settings/provenance and all
projection/pilot logs. No full-track, matched speedup or production approval.

100Python tests pass, including changed-U/material/mesh rejection, failed
projection preventing CFD, continuity amplification rejection, and final-time
validation. Tests caught and fixed Windows fingerprint slash normalization;
Ubuntu hash keys remain unchanged. Bash syntax/pycompile pass. Added projection
and snapshot-time C++ features require Ubuntu native build/execution. Next
RunLocalFluxPilot, send M247_local-flux-pilot archive; no repeated audit needed.

Reference: https://api.openfoam.com/2406/CorrectPhi_8C_source.html
(same discrete divergence/matrix-flux subtraction, independent geometric
coefficient instead of momentum-equation rAUf).
