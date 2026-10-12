# Pressure pair preparation failed before CFD; initial continuity line fixed

Reviewed M247_m247-pressure-pair-20261012-145631_review.tar.gz,
revision5e0f94447d3396eb1e42b12b1ec88d460b4c4a5f. Manifest exit1,
completefalse; both variant run/log/geometry files absent. Build/preflight
completed against identical solver and laser hashes. No copied restart cases
were made and no CFD advanced.

track_pressure_pair.py pressure_stats rejected the completed pilot source:
12594 pressure solves (3 x4198 steps),12595 continuity records. The extra
record is OpenFOAM's initial zero continuity report before first pressure
solve. Earlier local check counted pressure calls and convergence but did not
check the correspondence to continuity records; a synthetic test only used
one continuity line per pressure solve. This was a collector error, not a
physics or solver failure.

Fix: accept exactly one initial `(0,0,0)` continuity record, then require
one continuity record per pressure solve. Any other count or nonzero extra
record still fails. Added tests for the real startup pattern and malformed
extra record. Re-run the same pair command; no cleanup or source modification.
