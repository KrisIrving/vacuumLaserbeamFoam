
## 2026-10-08 183756: paired diagnostics verified; stored-field profile audit

Comparison archive3files, hashes/bytes verified, wrapperexit0, missingfilesnone.
Read-only comparison confirms1.21797 job/1.22141 loop speedup and33vs40steps;
no production approval.10nsUmax differs-6.82%/-4.43% at matched snapshots.

Next after pull and sourcing OpenFOAM:
```bash
./tests/m247Performance/CompareMovingProfiles
```
Builds a separate read-only utility using the existing validated regionAudit include/
link settings; never rebuilds/runs the CFD solver. Reads final180.2us from existing
48-rank5ns180928 and10ns182248 cases. Each native audit has600s wall timeout.
InputT/U/alpha/epsilon and latest stored topology files are hashed before/after.
Outputs automatically named M247_moving-profiles-<timestamp>_review.tar.gz on
success or native audit failure. Compilation is still pending Ubuntu;132Python
tests and Bash syntax pass locally, not proof of native runtime.

153coordinate slabs (53x-direction,60y,40z) report geometric volume,metal/liquid
volumes,metal-weightedT and signedU-component integrals. These are three1D
projections, not1533Dcells. Cell-centroid assignment can produce bin-boundary
bias when grids differ; domain/axis-integral closure checks catch missing evidence,
but passing does not imply conservative geometric overlap or3D field equivalence.
No acceptance tolerance or production approval is invented. This screening locates
whether velocity changes accompany distributed material/thermal shifts before
implementing a more costly conservative3D comparison. No enthalpy field is
estimated fromT; no keyhole geometry claim from these slab profiles.
