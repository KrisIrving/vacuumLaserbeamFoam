
## 2026-10-08 190128: incomplete long pair; completion gate and read-only recovery

Verified archive contains only reference initialreport/build/collectionlog. Report
complete=false,pilot_gate=false,commands=[]; no solver log/candidate/comparison.
Manifest wrapperexit0 is inconsistent with completion. Cannot infer whether native
job stopped, is still running, or failed in decompose stage from this evidence.
Do not rerun or claim0.4us outcome. Source protection/CFD failures are not proven.

MW06: parent wrapper trusted shellstatus and omitted decomposition/pilot logs.
Fix explicit pilot/pair completion checks,signal exit130/143 handling, archived
status report and stage logs/run/probe metadata. Missing/incomplete reports force
nonzero wrapper status even if incomingstatus0. Existing package manifests remain
historical evidence; incomplete archives are never upgraded without actual reports.

Next after pull:
```bash
./tests/m247Performance/CollectMovingLongPair
```
Default originaldirectory runs/moving-long-pair-20261008-190128. Copies existing
child stage logs/reports into a fresh timestamp directory; no build/decompose/CFD.
Send M247_moving-long-collection-<timestamp>_review.tar.gz even when incomplete.
Changing input during copy is rejected and partial evidence packaged. Do not
interrupt an active job just to collect it. Collection success means evidence was
copied, not simulation completion; manifest status records actual completion.

136Python tests/Bash syntax pass, including initial-only false-zero regression,
130/143 status retention and read-only partial-decompose evidence packaging.
Ubuntu recovery pending. No native solver changes;5ns remains default and10ns
experimental. Physical optimization resumes after actual long-run state is known.
