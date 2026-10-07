# Exchange profiler build repair: messageStream versus Ostream

The user supplied compiler output from laser-exchange-20261007-192743.
Both compactRay.C and laserHeatSource.C fail at the precision calls in
laserPerformance.H. Info is a messageStream, so Info.precision() is invalid.
No archive integrity or CFD-success claim is made from this pasted output.

The profiler now obtains Ostream& diagnosticStream=Info(), saves its precision,
sets 15 significant digits for global/rank statistics, and restores the saved
precision after reporting. OSstream.H is included explicitly for the complete
stream type. The existing 45 Python harness tests pass. This retains large-counter reporting without
changing timers, collective order, ray merge behavior or physical controls.

OpenFOAM's official messageStream API documents operator()() returning OSstream&:
https://api.openfoam.com/2512/messageStream_8H_source.html
https://api.openfoam.com/2506/classFoam_1_1messageStream.html

Full C++ compilation and runtime regression remain pending on Ubuntu; this
Windows workspace does not contain an OpenFOAM compiler environment.

From the Ubuntu repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunLaserProfile
```

The wrapper automatically rebuilds the library and clean solver, stops on build
failure, and packages one new timestamped archive. Send the printed archive.
No manual deletion or source-case modification is required.
