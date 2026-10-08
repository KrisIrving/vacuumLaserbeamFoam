
## 2026-10-08 203504: cadence native-valid but no skips; opt-in refinement halo

Verified paired archive: both nativebuild/run,gates pass,40steps,zero thermalcaps.
Reference370.380s,candidate377.393s,speedup0.98142; physicaldiagnostics identical.
Interval4 attempted40updates,skipped0,30coverage overrides. Native protection did
its job; cadence alone provides no acceleration. Do not adopt interval4alone or
weaken coverage. First-stepneeded87687cells,step2needed2610,then485/408/313...
new corewindow/hotwake cells require refinement eachstep. Split cause betweenwindow
andwake not recorded, so do not assert thermal-only cause.

Develop opt-in one face-neighbour refinementhalo around unionwindow/heldwake on
attempted updates. Uses official2512protectedextendMarkedCells(bitSet&) method:
https://api.openfoam.com/2512/dynamicRefineFvMesh_8H_source.html
Default halo0/interval1 unchanged. Candidatehalo1/interval4 may pre-refine cells
before coverage demands them. CoverageRequired still counts unrefined CORE cells
before halo; first/scheduled/required updates remain enforced; window/wake checks,
2Mcellcap,V0,mapping/thermal/continuity gates retained. No halo guarantee is assumed.
Halo growth on attempted update only; no dilation on skippedstep. New nativecadence
records prove haloLayers/haloAdded; metadata/dictionary/binary markers validated.
Larger cellcount can outweigh fewerupdates; require measured netcost,not claim
speedup from skipcount. Changesmesh/opticalinput,so physicalequivalence pending.

Next after pull:
```bash
./tests/m247Performance/RunMovingHaloPair
```
Same rebuiltbinary,5nsceiling,48ranks,0.2us each: baselineinterval1/halo0 versus
candidateinterval4/halo1.15minute solver cap each;prepare/build/decomposeextra.
Send ONE M247_moving-halo-pair-<timestamp>_review.tar.gz on successorfailure.
144Python tests/Bash syntax/pycompilepass; newC++compile/runtime pendingUbuntu.
If halo still cannot skip or netcost worsens, stop this cadence branch rather than
adding more layers without region/cost evidence.10ns remains experimental.
