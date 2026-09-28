# Test results

No local experimental or solver-run result should be inferred from code review.
Record only tests that were actually executed.

## 2026-09-28 — Initial status

### Baseline Git-tree verification

Result: **PASS**

The project `main` tree SHA was verified equal to the public LaserbeamFoam
V3.0 tree:

`a37e12fa6d6828e06bbde60831db2de67dab283a`

This verifies repository-content identity, not compilation/runtime behavior.

### Phase-1 build

Result: **PENDING**

Expected automated check: repository GitHub Actions `Build` workflow after the
`dev/vacuum-solver` branch commit is pushed.

### Phase-1 solver-equivalence regression

Result: **PENDING**

Requires actual execution of the same prepared case with both executables.
