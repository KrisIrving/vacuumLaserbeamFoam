// Experimental source hold state; default interval1 preserves every-call optics.
label laserLastRefreshIndex = -1;
label laserLastAttemptIndex = -1;
scalar laserLastRefreshTime = -1;
scalarField laserRefreshAlpha;
