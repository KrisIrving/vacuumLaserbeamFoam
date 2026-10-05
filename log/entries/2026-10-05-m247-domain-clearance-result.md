# 2026-10-05 — M247 powder preflight domain-clearance result

The reconstructed T field was post-processed using the T=1631 K liquidus
isotherm.

At 100 us:

- liquidus extent x = [-200.000, +151.566] um;
- liquidus extent y = [385.569, 746.821] um;
- liquidus extent z = [-126.276, +101.942] um.

Boundary clearances:

- x-minus = 0.000 um;
- x-plus = 48.434 um;
- bottom = 385.569 um;
- top = 213.179 um;
- z-minus = 193.724 um;
- z-plus = 218.058 um.

Interpretation:

1. The widened transverse domain z=+/-320 um is successful. The minimum
   transverse liquidus clearance is approximately 194 um.
2. The 600-um substrate depth is also sufficient for this 100-us gate.
3. The 280-um nominal gas headroom above the powder envelope remains adequate
   for the liquidus-temperature thermal envelope in this short run.
4. The scan-direction domain x=[-200,+200] um is not adequate. The liquidus
   region reaches x=-200 um at 100 us. At 95 us the x-minus clearance is only
   approximately 0.85 um.

Therefore no longer M247 calculation should reuse the 400-um-long scan-domain
geometry. The next 8-um extension must enlarge the scan direction while
retaining the successful transverse and vertical dimensions.

The completed 100-us case remains useful for constitutive transfer, powder
optical/energy comparison, time-step/cost assessment and keyhole-depth trends,
but its late-time melt-pool length is boundary-limited.
