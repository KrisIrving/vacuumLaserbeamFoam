# Protected moving-window sparse-mask failure (162215)

## Evidence and status

Archive M247_moving-window-protected-20261008-162215_review.tar.gz:7 file
SHA256/size checks valid, wrapper exit1, no missing files. buildEnvironment
records6f541e68966ebc30c9ab932fa302dfd5f1d8354b. Native program compiles and
completes all8 small-mesh updates. Raw-log reconstruction matches smoke report.
Only wake_gate fails: initial48 hot cells remain48 cells with0 covered through
all updates. Linear mapping/window coverage/cold coarsening pass. Large case
was not copied and no CFD or production result exists for this run.

## Root cause and previous verification gap

The cell mask is Boolean, but base selectRefineCandidates averages it to points
before thresholding. A one-cell-wide hot column can reach at most0.5 at its
points; with lowerRefineLevel0.5 this yields zero error, not a positive candidate.
The archived behavior is consistent with this mechanism. Official OpenCFD2506
source confirms average/error/positive-selection chain, and2512 header confirms
protected virtual hook signature. Direct2512 C source retrieval was blocked403;
no claim that its full implementation was locally compiled/inspected.
Sources:
https://api.openfoam.com/2506/dynamicRefineFvMesh_8C_source.html
https://api.openfoam.com/2512/dynamicRefineFvMesh_8H_source.html

Prior Python tests proved input generation and rejection logic, not native sparse
refinement behavior. Reporting their pass count as native confidence was
insufficient. The new native preflight caught this before expensive real work.

## Fix and checks

Protected mode overrides ONLY selectRefineCandidates in diagnostic subclass,
selecting exact1-valued cells directly. It uses override to enforce the2512
signature at compile time, checks binary input/control interval/counts and emits
8 native candidate records. Base selectRefineCells, budgets, topology restrictions,
2:1 consistency, coarsening and mapping remain responsible for actual updates.
Unprotected mode delegates to the original selector. No threshold lowering or
coverage-gate bypass. Collector requires mode and8matching candidate records;
requested/selected counts must agree. Existing wake coverage/marked-volume,
cold coarsening/geometry/original-source gates stay enabled. Failure message names
failed gates. Smoke report also persists error type, reason, failure stage and
large_case_started=false for native/collection exceptions. Archive exact diagnostic records retained as regression fixture.

121 Python tests pass, including archived failure rejection and missing/lost/
wrong-index selection evidence. Python compilation passes. Wrapper unchanged;
previous Bash syntax check applies. Modified native C++ build/runtime PENDING
Ubuntu. Only an actual protected small+real native pass may close this issue.
Next pull and RunMovingWindow --protect-wake; use automatic protected archive.
