# vacuumLaserbeamFoam development log

This directory is the persistent research and development record for the
vacuumLaserbeamFoam project. It is intended to support reproducibility,
debugging, later paper/thesis writing, and traceability from physical assumptions
to code changes and validation results.

## Files

- `BASELINE.md` — immutable upstream baseline and environment assumptions.
- `DEVELOPMENT_PLAN.md` — phased solver-development roadmap.
- `ARCHITECTURE_DECISIONS.md` — design decisions and their rationale.
- `CHANGELOG_DEV.md` — chronological code-development record.
- `IDEAS.md` — hypotheses, possible extensions, and questions not yet decided.
- `SOURCE_MAP.md` — map from physical mechanisms to source files and planned edits.\n- `LITERATURE_NOTES.md` — literature equations/assumptions mapped to code.
- `TEST_PLAN.md` — numerical/physics validation strategy and acceptance criteria.
- `TEST_RESULTS.md` — actual test results; do not record a test as passed until run.
- `entries/` — dated detailed notes for individual development sessions.

## Record-keeping rule

Each physics-changing pull request should update at least:
1. `CHANGELOG_DEV.md`;
2. `ARCHITECTURE_DECISIONS.md` when a design decision changes;
3. `TEST_PLAN.md` if validation requirements change;
4. `TEST_RESULTS.md` after tests are actually executed.

Do not replace failed or unexpected results with only the final successful result.
Keep the failure, diagnosis, fix, and re-test trail when it is scientifically useful.
