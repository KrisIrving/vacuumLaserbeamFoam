# Exchange profile 193145: tracing imbalance, negligible merge cost

M247_laser-exchange-20261007-193145_review.tar.gz: all 27 manifest file hashes
and sizes verified, no missing files, wrapper exit 0. Build environment records
0995edf512e227dc15239dbd80e9bc22264fe9f5. Compilation and loaded-library
checks pass. Solver SHA256
54e35ac4d9876337ae30bb5ee951b8ccd4e74cb62250aded35234cfeab141dbb;
library SHA256
1919b421d127960e68e90a0101a6c1e2e850627221ee8a7286420ba3b62430f3.

Both jobs finish with returncode 0 and no budget/forced stop. Instrumentation
regression passes. Ubuntu field comparison reports exact zero differences in
T, epsilon1, alpha.metal, U and p_rgh over 756000 cells. Field files are excluded
from the small archive, so these norms are the archived Ubuntu report rather
than a local recomputation. Both common-time VACUUM_DIAGNOSTICS records are
identical. Reparsed logs independently pass schema-2 timing, counter, rank
group and coverage checks: two global reports and 96 rank rows.

Each case takes 16 steps, 15.3125 thermal correctors/step (maximum 18), zero
limit hits. All 16 residual rows meet tight limits: maximum epsilon residual
7.944428304e-6; phase-temperature residual 0.0009695427797 K; aboveTolerance 0;
phase blend width 0. Jobs take 36.038474 s off / 36.037603 s on. The observed
overhead ratio 0.999976 is effectively indistinguishable in this single pair;
it does not establish a speedup or zero statistical overhead.

Mean inner laser total 19.024777 s. Trace mean 0.775650 s, maximum rank total
10.014016 s (rank 44), max/mean 12.91. Exchange mean 17.961356 s, 94.41% of
inner time. The existing solver laser section is about 55.6% of the off loop.

| Exchange child | Mean seconds | Fraction of exchange |
|---|---:|---:|
| List copy | 0.0000523 | 0.000291% |
| Gather including waits | 1.787958 | 9.954% |
| Broadcast including waits | 16.173306 | 90.045% |
| Merge, nested inside gather | 0.0017705 | 0.009857% |

Merge rank-sum time 0.084983 s, highest rank merge 0.027015 s. Optimizing this
hash/append path is a low priority for this state. Broadcast timing includes
waiting for trace and gather completion; it is not a pure network-time measure.
For example rank 0 gathers for 18.675 s and broadcasts for only 0.0716 s, while
rank 1 gathers for 0.0106 s and broadcasts for 18.815 s. These collective
timings overlap other ranks' work and must not be added across ranks or treated
as independently removable idle time. Do not infer a 90% broadcast speedup.

18943103 searches, 18791614 advances and 151489 local segments are unchanged
from the previous profile. 21 of 48 ranks have no tracing searches. Ranks 44
and 46 perform 59.20% of searches; the top six perform 88.91%.

| Rank | Searches | Trace seconds | Interface events |
|---|---:|---:|---:|
| 44 | 5955888 | 10.0140 | 360831 |
| 46 | 5259186 | 6.5118 | 0 |
| 34 | 2938385 | 5.9691 | 511876 |
| 43 | 1458305 | 4.0277 | 136474 |
| 35 | 774615 | 3.2986 | 159769 |
| 38 | 456821 | 0.9818 | 0 |

Rank 46 also has zero bulk events: 27.76% of all searches there incur no
interface/bulk deposition branch. This does not authorize skipping those
searches: ray positions, cell identity and later reflections still matter.

## Development decision

The profiling question is answered; do not request another identical timing
pair. Prioritize reducing repeated tracing/cell-search cost and improving
spatial tracing balance, then measure the effect on collective waits. The
current template uses 48-way scotch decomposition; the saved rank workloads
demonstrate tracing imbalance without proving the exact decomposition geometry.

First candidate should preserve ray count, step locations, reflection and
absorption rules, ownership and deposition accumulation order. Inspect repeated
cell geometry/search allocations and cache opportunities on the fixed mesh.
Use the original cell lookup as a reference/fallback and require paired field,
deposited-power, convergence and runtime gates. A workload-aware decomposition
comparison is a separate candidate because repartitioning changes accumulation
order and requires mesh/state mapping and appropriate comparison tolerances.

No new numerical candidate is implemented in this review, and no additional
Ubuntu action or data upload is needed now. Production approval, long-track
cost and 4-um accuracy/cost validation remain pending. Mature-state short-loop
cost near 171 s/us is not a full-track or fine-grid runtime prediction.
