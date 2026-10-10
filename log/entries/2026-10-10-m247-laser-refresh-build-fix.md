## 2026-10-10 111746: laser refresh scalar pow namespace build fix

The laser-refresh-pair review archive failed during the solver build, before
CFD started. laserRefreshUpdate.H called unqualified pow(double,double),
which is ambiguous between the global math function and Foam::pow in
OpenFOAM v2512. This was an implementation error introduced by this experiment.
Qualify the call as Foam::pow and use scalar(1)/scalar(3) for the exponent.
The compiler candidate list confirms that Foam::pow(double,double) exists.
No controls, approximation bounds, source checkpoint, or physics were changed.
The alphaEqn.H wmkdepend warning is separate from this fatal compiler error.

Retry: git pull --ff-only origin feat/m247-material-port
       bash tests/m247Performance/RunLaserRefreshPair
The wrapper uses official solver-only wmake, without wclean or library rebuild,
and packages failures as well as completed comparisons. Return its new archive.
Native OpenFOAM compilation remains an Ubuntu check; local Python checks do
not substitute for it. The experiment is still not production approved.

