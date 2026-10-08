# M247 moving-window error register

Updated after protected164709 review. These are development failures, not a
claim that passing Python tests establishes OpenFOAM runtime correctness.
Sources are the named review archives and log/entries for each patch.

| ID / first archive | Failure and cause | Fix / prevention | Native closure |
| --- | --- | --- | --- |
| MW01 /153230 | First refinement reached1239840 cells, then missingV0 during mapFields. Mesh-only driver lacks the normal old-volume lifecycle. | Expose protected storeOldVol; validate V0 size/finite/positive/exact pre-update values. | Full initialization plus8updates confirmed160259 after MW02/MW03 fixes. |
| MW02 /154023 | Direct constructor eagerly initialized motion parent and required a motionSolver. | Staged dynamicRefineFvMesh(io,false), qualified init(true), matching refinement's optional-motion setup. | Staged constructor recorded154937; full run160259. |
| MW03 /154937 | V0 still absent before first update. Synthetic time indices could fail storeOldVol's strictly advancing history condition. Archived old indices unavailable, lifecycle cause inferred. | Start above max(Time index,mesh history index), validate and record8strictly advancing index pairs. | Small and real native runs160259 complete; all8V0 records valid. |
| MW04 /protected162215 |48 hot cells remain unrefined through8updates; only wake coverage fails. Binary cell-to-point averaging can dilute a narrow column to lower0.5 threshold, which produces zero selection error. | Protected-mode direct virtual candidate selector, binary/count checks and8native candidate records. Keep frozen wake, mapping, cold coarsening and geometry gates. Preserve actual failure diagnostics as fixture. | CLOSED for frozen prototype: protected164709 small+real native pass,48hot cells become384fine children; real205048wake children all covered. Full-solver integration remains pending. |

## Checks before requesting another Ubuntu run

1. Record archive hashes, wrapper exit, missing files and observed failure stage.
2. Reconstruct assertions from raw logs. Distinguish observed facts from inferred
   mechanisms. An old source/binary must not be credited as the revised build.
3. Check the relevant installed-version API declaration. Use override for virtual
   hooks so signature mismatch becomes a compile error. Record source-version gaps.
4. Keep the actual failed diagnostics as regression data and check that they
   cannot receive approval. Python tests validate parsing/rejection, not native
   refinement, constructors, field registration or thermodynamic accuracy.
5. Run small native preflight automatically before copying the real case. Persist
   failure type/reason/stage in its report and include logs in the single archive.
6. Close a runtime issue only after the user's native logs show its corrected
   behavior. Successful mesh topology tests do not authorize production CFD.

The2506 official source confirms cellToPoint averaging/error/positive selection;
the2512 official header confirms the protected virtual signature. The complete
2512 C source could not be fetched (403). Sparse-selector revised native compilation and frozen topology pass confirmed164709.
New full-solver moving-mesh compilation/runtime remain pending Ubuntu; Python
suite124tests passes and is recorded separately.

Next: pull feat/m247-material-port and run RunMovingCFDPilot once, returning
the automatically named moving-cfd-pilot archive. This starts from the hash-checked
original coarse state, not the stale-field mesh-only snapshots. Do not bypass wake coverage or reduce
thresholds merely to make this test pass.

## MW05 — missing thermal metadata after successful native CFD (172613)

Cause: moving_cfd prepared probe.json without epsilon_tolerance and
phase_temperature_tolerance_K, then called residual_gate requiring those keys.
Native40-step run succeeded; collection raised KeyError. Parser-only tests missed
the complete collection call. Fix: read and validate explicit MELTING controls,
persist them before future launches, and recollect immutable existing evidence.
No fallback tolerance, skipped gate or CFD rerun. Actual diagnostic fixture plus
full collector and resume/package tests pass locally. Ubuntu recollection pending.
Native full-solver build/runtime are now confirmed by172613; production approval
and measured acceleration remain pending.
