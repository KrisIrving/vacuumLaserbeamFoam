# Exchange details and rank work: next M247 cost measurement

The validated schema-1 profile puts 94.47% of inner mean laser time in
exchange, with trace max/mean 12.82. Blocking waits make this insufficient to
choose between merge/transport optimization and tracing load distribution.

Schema 2 preserves the existing list copy, combineGather(combineRayLists)
and broadcast operations. Timers distinguish copy/gather/broadcast and nested
merge; counters capture merge invocations, X/Y inputs and appends. The original
HashSet and equality/append behavior are unchanged, including destruction.
Only output-time reports gather rank tracing, ownership, exchange and merge
work. No ray-round communication is introduced for reporting.

Collector validates rank coverage and IDs, interval order, nested times,
means/maxima, work sums, source/binary provenance, thermal convergence, common
physical diagnostics and final saved fields. Merge is inside gather and must
not be added again. Neither gather nor broadcast measures pure network time
or idle time directly. Logging uses 15 significant digits to preserve counters.

RunLaserProfile rebuilds both targets and requires schema-2 global/rank
markers in the actual loaded library. It runs the same independent 180–180.2-us
profiling off/on pair, width zero, tight bounded enthalpy, ray paths off,
48 ranks and a 15-minute budget per solver job. Build/copy are additional.
The default archive M247_laser-exchange-..._review.tar.gz includes the new
laserExchangeDetails.csv and laserRankWork.csv plus existing logs/reports.

Local validation: 45 Python tests and Bash syntax pass. Tests cover rank
mismatch/missing/duplicate/order handling, nested timing nonadditivity,
provenance, field equivalence and archive inclusion. Actual OpenFOAM build
and CFD are pending Ubuntu; no new speedup or physical approval is claimed.

Ubuntu commands from repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunLaserProfile
```

Send the single automatically printed review archive, including on failure.
The result will choose the next equivalent ray-exchange or tracing optimization
without reducing ray count or changing phase closure.
