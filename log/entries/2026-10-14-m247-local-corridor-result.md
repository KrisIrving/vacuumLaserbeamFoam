# 2026-10-14: local corridor gives 2.38x cost reduction, fails temperature screen

Reviewed M247_m247-local-corridor-pilot-20261013-192358_review.tar.gz.
All 45 manifested file hashes pass; exit 0 and complete true. Matched
baseline archive also passes all 42 file hashes. Both recorded environments
are v2512, with the same solver/library, 384 rays, 48 ranks, verified native
341-particle DEM handoff and non-mesh input hashes. Only blockMeshDict changes.

| Metric | V2 full fine corridor | Local fine corridor |
|---|---:|---:|
| Mesh cells | 3,814,272 | 1,929,312 |
| 50 us solver wall, s | 12,347.94 | 5,190.88 |
| Steps | 4,980 | 4,139 |
| Mean thermal correctors | 3.07 | 3.13 |
| Max thermal correctors | 5 | 19 |
| Nonlinear thermal cap hits | 0 | 0 |
| Final connected solidus depth, um | 93 | 93 |
| Final connected solidus width, um | 234 | 234 |
| Liquidus metal cells | 6,508 | 6,394 |
| Final global Tmax, K | 4,230.72 | 4,797.55 |
| Final alpha>=0.99 metal Tmax, K | 3,012.42 | 3,247.39 |
| Final deposited power, W | 257.30 | 284.09 |
| Final interface vapour pressure, MPa | 2.647 | 4.969 |
| Final Umax, m/s | 156.04 | 84.80 |

The measured job speedup is 2.378775x (-57.96% wall), combining fewer
cells and 16.89% fewer timesteps. Wall per timestep improves about 1.98x;
do not attribute the full speedup solely to computational efficiency with
unchanged dynamics. Pressure rank-mean aggregate falls 6,307.77 -> 2,202.87 s
(-65.08%), thermal 2,217.37 -> 888.29 s (-59.94%), laser
933.40 -> 819.29 s (-12.22%). Candidate loop shares: pressure 42.47%, thermal 17.12%,
laser 15.79%, alpha 10.75%, momentum 8.99%, properties 4.33%.

Final liquidus-cell proxy differs 1.75%, metal peak 7.80%, but global peak
13.398% exceeds the user's <=10% criterion. Keep local_50us_screen_pass=false.
The five saved diagnostic samples show changes from 10 us; velocity and
vapour-pressure differences are substantial. Sampled Tmax over those five
times peaks at 4,785.67 / 5,209.27 K (8.85% difference); this is neither an
all-step maximum nor grounds to override the failed final-state screen.
One startup T linear solve hits 1000 iterations above tolerance in each
case; no worsening in count. Zero nonlinear caps do not prove all linear
solves converged. Molten metal stays in the fine region, minimum margin45um.

Conclusion: reducing active cell cost has useful evidence, but accepted
physics and full-track acceleration are not established. Equal DEM input
and near-melt 6um spacing do not prove equal represented initial powder;
far-ahead powder has been coarsened. Neither that mechanism nor parallel
decomposition/flow sensitivity is isolated by these archives.

Next implement one read-only collection of initial and all saved 10�C50us
fields from both existing cases. Compare initial alpha/T on identical
coordinates, integrate alpha*epsilon volume, and report top-connected
gas-cavity depth and temperatures by region. No new CFD, no relaxed limit,
no full-track projection. Native reconstruction is an Ubuntu check.
