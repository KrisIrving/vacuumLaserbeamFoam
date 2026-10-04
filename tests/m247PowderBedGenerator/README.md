# M247 fixed-PSD powder geometry gate

This test exercises the M247-specific powder-generator mode before CFD.

Design target:
- nominal layer thickness = 50 um;
- geometric particle envelope = 80 um;
- requested D10/D50/D90 = 36.5/52.6/74.4 um;
- diameter support = 30-80 um;
- nominal-layer packing target = 0.58;
- fixed diameter set before placement;
- no silent redraw of a smaller particle if a large particle cannot be placed.

The requested PSD is represented as a piecewise quantile CDF through
Dmin/D10/D50/D90/Dmax. The small deterministic particle set therefore matches
the supplied PSD more closely than a random truncated-lognormal sample.

The geometry gate also reports projected coverage in the active scan corridor
and the maximum uncovered gap along the laser centerline.

This remains a geometric initialization model, not DEM.
