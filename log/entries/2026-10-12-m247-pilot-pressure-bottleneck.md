# 1.5mm pilot completed; pressure becomes the main bottleneck

Reviewed M247_m247-track1500-pilot-20261012-105416_review.tar.gz,
revision64e88511c7808226671b2313f87730a688595847. Archive sha256:
c7f54425d08e9de4c42096daa91f4903d90949ed969aada520762f7ad02ea782.
All manifest file hashes match. Native mesh/CFD completed successfully.

50us cost3.0146h; pressure50.44%, thermal16.51%. Average thermal
correctors3.13, maximum6, no nonlinear cap hits. All4198 nonlinear
thermal diagnostics pass. Every final pressure solve reaches1e-7.
Depth105um/width270um are connected solidus molten cell-centre extents,
not keyhole/final track geometry. Fine-grid margin39um, no molten cells
outside fine zone. Domain-boundary sensitivity remains untested.

Recorded first-step T linear iteration cap1000 with residual7.93e-9
above1e-9. Later T solves converge; nonlinear gate does not erase this
exception. Maximum printed Co0.1548 is also recorded versus target0.1.
Do not label this pilot entirely free of convergence exceptions.

Added standard GAMG pressure restart pair50--60us, exact-time55/60us
melt depth/width comparisons, binary/snapshot matching, pressure/T linear
convergence and continuity reporting. Ray/thermal/time-step controls and
pressure tolerances/correction counts are unchanged. Mature restart source
audit carries the initial linear failure forward; does not claim to fix it.
No full-track launch or production acceleration claim.

90.44h linear heating projection excludes cooling and evolving cost. Even
eliminating pressure entirely would yield at most2.02x speedup here; reaching
24h needs further mesh/time-step evidence. Static whole-path fine corridor
remains costly. Avoid repeating thermal/ray screens now.

Nine focused Python tests and Bash syntax check passed. GAMG native execution
and actual speed/geometry differences remain Ubuntu checks.
