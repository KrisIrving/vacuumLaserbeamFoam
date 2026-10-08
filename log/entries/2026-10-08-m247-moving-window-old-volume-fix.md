Reviewed moving-window153230:8archive SHA256/size valid,exit1,no missing.
Both tools compile; native initial756000cell state valid/protected0. First
refinement selects69120 cells, produces1239840, then SIGABRT at
fvMesh::V0 through dynamicRefineFvMesh::mapFields. No completed update snapshot,
coarsening/mapping quality or physics gate established. Cause: synthetic Time
setTime alone does not seed old cell-volume storage in mesh-only driver.
Fix diagnostic-only dynamicRefineFvMesh subclass exposing protectedstoreOldVol(V)
before every update at the new index, without point motion or privatepointer
manipulation. Check V0 count/finite/positive/exactpreupdateV match andemit8
M247_MOVING_V0 records; collector requires everyrecord count/order/zero delta.
114 Python tests pass, py_compile pass; native repairedcompile/runpendingUbuntu.
Existing wrapper/Bash unchanged, budget/celllimit/sourceprotections retained.
Next pull and rerun ./tests/m247Performance/RunMovingWindow in fresh timestamped
output. Send M247_moving-window-..._review.tar.gz on success orfailure.
Official v2512 fvMesh.H confirmsprotectedstoreOldVol andpublicconstructors;
setV0 isonlyaccessor, not aninitializer, so simplycallingitwouldstillabort.
