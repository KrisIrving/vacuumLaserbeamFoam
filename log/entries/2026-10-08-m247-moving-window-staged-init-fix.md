Reviewed moving-window154023:8archive SHA256/size valid,exit1,no missing;
both tools compile, native exits before initial-state/mesh updates with missing
motionSolver. PriorV0fix introduced default directconstructor path which eagerly
initializes dynamicMotionSolverListFvMesh withmandatory motion solver, before
refinement class can allowzero motion. Fixeddiagnosticsubclass constructor via
dynamicRefineFvMesh(io,false) followed by dynamicRefineFvMesh::init(true), matching
staged runtimefactory and refinement's optional-motion initialization. Keep
storeOldVol(V) checks/eightmarkers unchanged. No motion solver added, no model
change, no disabled gate. Existing114 Python tests unaffected; native C++compile
and correctedinitialization/runtimependingUbuntu. Rerun RunMovingWindow on new
copiedwork afterpull; standardarchive includes failure evidence automatically.
