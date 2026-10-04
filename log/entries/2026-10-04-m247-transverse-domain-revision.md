# 2026-10-04 — M247 transverse-domain revision after bare-plate preflight

Observation:
the completed 100-us M247 bare-plate preflight visibly reached the former
transverse side boundaries at z=+/-160 um.

Those side boundaries use slip velocity conditions. Once the molten region
reaches them, transverse flow is artificially constrained. Therefore:

- melt-track width from that preflight is not a valid physical width result;
- the keyhole-depth / flow field may also contain some boundary feedback;
- the run remains useful as a numerical transfer/preflight gate and for
  identifying required domain enlargement;
- the running powder companion based on the same transverse width should not be
  used as the next quantitative gate.

Revised powder-preflight design:

- transverse CFD domain: z=-320 to +320 um;
- central active corridor: z=-160 to +160 um at 8 um;
- outer shoulders: 160 um per side with graded coarsening;
- approximate mesh size: 360k cells;
- powder footprint widened to z=-280 to +280 um;
- deterministic seed changed to 247081 for high central-corridor coverage;
- expected fixed-PSD particle count: about 58;
- substrate depth remains 600 um;
- powder geometric envelope remains 80 um;
- gas headroom above the powder envelope remains 280 um.

The next powder result must demonstrate that the molten region no longer
approaches the transverse side boundaries before any production-domain decision
is frozen.
