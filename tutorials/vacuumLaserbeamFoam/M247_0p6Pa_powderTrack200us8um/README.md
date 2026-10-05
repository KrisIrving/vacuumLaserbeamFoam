# M247 0.6-Pa powder track — 200 us / 8 um

This is the next gate after the completed 100-us powder preflight.

## Why this case exists

At 100 us the M247 powder case reached a keyhole depth of about 203 um and the
50-100-us depth trend was still about 1.85 um/us. The T=1631 K liquidus
envelope also reached the old x=-200-um boundary.

Therefore the previous domain cannot establish a quasi-steady keyhole depth or
support a longer-track decision.

## Frozen process input

- M247 substrate and powder;
- 0.6 Pa;
- 1343.15 K global preheat;
- 350 W;
- 1.0 m/s;
- 86 um spot diameter;
- 1064 nm;
- 200 um scan / 200 us.

## Domain / mesh

- x = -520 to +320 um;
- y = 0 to 960 um;
- z = -320 to +320 um;
- original substrate surface y = 600 um;
- x is uniformly 8 um throughout the domain;
- central |z|<=160 um is 8 um;
- transverse shoulders retain the validated grading;
- total cells = 756,000;
- 48 MPI ranks.

The enlarged x domain is intentionally conservative. The 100-us liquidus
envelope touched x=-200 um; this case adds 320 um of extra trailing space and
120 um of extra forward space.

## Powder

- nominal layer thickness: 50 um;
- geometric envelope: 80 um;
- target packing: 0.58;
- Dmin/D10/D50/D90/Dmax = 30/36.5/52.6/74.4/80 um;
- fixed PSD before placement;
- footprint x=-450..+260 um, z=-280..+280 um;
- deterministic seed 247479;
- expected particle count about 115;
- central scan-corridor projected coverage about 80%;
- expected maximum uncovered centerline gap below 30 um.

## Output cadence

Fields are written every 10 us. Post-processing reconstructs both alpha.metal
and T and quantifies:
- moving keyhole depth;
- liquidus-envelope x/y/z extent;
- all six domain clearances.

## Acceptance gate

Before any 4-um M247 resolution pair or approximately 2-mm production run:

1. the 200-us run must complete stably;
2. no liquidus envelope may approach any boundary closer than 80 um;
3. keyhole-depth growth over the late window should be assessed for plateau;
4. if late growth remains strong, extend the 8-um duration again before
   spending resources on 4-um verification;
5. measured wall-time must be used for the production-cost estimate.
