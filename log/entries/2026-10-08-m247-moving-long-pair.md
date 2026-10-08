
## 2026-10-08 185039: native stored-field profiles pass; bounded longer pair

Native utility compiled and read both final180.2us snapshots successfully. Archive
hashes/sizes verified,wrapperexit0,missingfilesnone. Input fields/topology hashes
unchanged. Final total metal volume difference-4.406e-9%, liquid volume+0.004549%,
metal-weightedT integral-4.904e-6%. Across three centroid slab projections relative
L1 differences:metal0.0000258-0.0001247%,liquid0.0050-0.00751%,signedmetalU
components0.0252-0.1977%. Signed slab averaging may cancel local velocity changes;
these values do not prove pointwise3D equivalence or keyhole convergence.

Next after pull:
```bash
./tests/m247Performance/RunMovingCFDLongPair
```
Automatically runs matched5ns and10ns ceilings from protected164709original
checkpoint over180-180.4us (0.4us each). Startup1ns,48ranks,CFL0.1,thermal and
coverage/mapping/continuity screens remain.15minute solver cap applies per run;
build/copy/hash/decomposition add time. Approximate prior-rate estimate~25minutes
combined CFD is planning only; adaptive CFL and later state may change cost.
If baseline fails/stops at budget, candidate does not launch and failure evidence
is packaged. No limit bypass or retry loop. Send ONE parent archive:
M247_moving-long-pair-<timestamp>_review.tar.gz. Parent includes both available
solver/build/collection logs and reports plus diagnostic comparison if completed;
child archives remain for recovery. Existing shorter runs are preserved.

134local Python tests pass, including variable mapping horizon and invalid-duration
prelaunch rejection. Bash syntax passes; longer native pair pending Ubuntu.
Default short pilot and5ns settings are unchanged. Optional --long changes only
endTime/duration and metadata; --dt10 --long is experimental. No C++ modification.
The previous profile tool intentionally remains scoped to final180.2us snapshots;
do not apply it to new180.4us cases until its horizon/coordinate provenance is
extended. Subsequent work: compare growth of velocity differences and conservation,
then common3D geometry/field validation before accepting10ns or full-track work.
