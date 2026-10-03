# vacuumLaserbeamFoam development log

This directory is the persistent research and development record for the
vacuumLaserbeamFoam project. It supports reproducibility, debugging, project
management, and later paper/thesis writing.

## Current navigation

Start here:
- `PROJECT_STATUS.md` — **current project state, completed work, running work and next priorities**;
- `DEVELOPMENT_PLAN.md` — milestone roadmap;
- `PAPER_AND_REPORTING_PLAN.md` — writing, figures, tables and reproducibility workstream;
- `M247_MATERIAL_PORT_PLAN.md` — material-data and 2 mm-track transfer plan for the final M247 target;
- `M247_NUMERICAL_DESIGN.md` — production-domain, mesh, powder and run design;
- `M247_INPUT_PROVENANCE.md` — frozen/candidate/TBD material and experiment inputs.

Detailed records:
- `BASELINE.md` — immutable upstream baseline and environment assumptions;
- `ARCHITECTURE_DECISIONS.md` — accepted design decisions and rationale;
- `CHANGELOG_DEV.md` — chronological implementation history;
- `IDEAS.md` — open hypotheses/extensions, not accepted decisions;
- `SOURCE_MAP.md` — physical mechanisms mapped to code;
- `LOCAL_TESTING_WSL2.md` — local build/regression notes;
- `LITERATURE_NOTES.md` — source equations/assumptions and literature mapping;
- `TEST_PLAN.md` — planned tests and acceptance criteria;
- `TEST_RESULTS.md` — measured test results only;
- `entries/` — dated detailed development notes.

## Record-keeping rule

Each physics-changing development step should update as applicable:
1. `CHANGELOG_DEV.md`;
2. `ARCHITECTURE_DECISIONS.md` when a design decision changes;
3. `TEST_PLAN.md` before/when a validation requirement is introduced;
4. `TEST_RESULTS.md` only after the test is actually executed;
5. `PROJECT_STATUS.md` after a major milestone changes state.

Paper/figure work is a formal project deliverable. Update
`PAPER_AND_REPORTING_PLAN.md` as figures/tables/scripts are completed.

Do not replace failed or unexpected results with only the final successful
result. Keep scientifically useful failure, diagnosis, fix and re-test history.
