# Wang hotspots require interface accuracy; one ring-staggered candidate

Archive(2):162 manifest files match bytes/SHA256, missing[], complete true.
temperatureHotspots.errors[]. Selected worst global temperatures for768/384/192
are interface, not gas-only diagnostics:124us4848.99 vs5967.47K;54us6366.41
vs4974.97K;98us6698.20 vs4674.82K. Metal-only maxima also differ at some
times:76898us4220.65 vs3807.36K. Removing gas or changing Tmax definition
cannot establish acceptance. Large serial-cell deltas often coincide with
alpha/geometry changes; do not treat all as same-material thermal errors.

Implemented default-off staggeredAngularSampling in createInitialRays:
rotate each uniform radial ring through a different phase within one angular
sector. Preserve radius, powers/areas, total ray count, temporal refresh,
Fresnel, multiple reflection and termination. This addresses aligned-spoke
spatial coverage as a hypothesis, not a proven cause or accuracy gain.
No new header or ABI changes; unchanged original angular expression when off.
Added one complete384-ray Wang candidate using verified retained prepared
fields/partition and unchanged settings. Official wmake libso only rebuilds
the laser library. Runtime feature and per-call coverage gates prevent old or
disabled candidate binaries; one archive includes both retained references.
Historical cost comparison is labelled as such. No repeated1536 baseline,
192-ray screen, tolerance relaxation, iteration-cap reduction or automatic
production approval. Existing thermal nonconvergence remains a separate issue.
25 Python checks and Bash syntax pass; native compile/CFD is Ubuntu pending.
