## 2026-10-10: real prepared full/local pair COMPLETE; impact localization next

Archive213729 passes all manifest hashes and reports complete/source_unchanged/
measurement_quality_gate true. Both834steps180..190us48ranks, thermal residual
gates pass, mean correctors14.55,max18,zero cap hits. dt11.945..12.239ns,
maxCo~0.10060. Both use default isoAlpha (missing reconstructionScheme warning).
Full756000cells1720.98s28.68min; local604800cells1398.56s23.31min:
1.23054x,18.735% less solver wall. Loop1.23063x. Prep/postprocess not included.
Full/local mean module times(s): laser871.71/789.92,thermal569.33/412.61,
pressure147.25/101.13,momentum66.09/37.53. Local laser56.54%,thermal29.53%.
Initial604800retained cells exactly match. Cut834records all inactive,
maximumT1343.150008K,epsilon0,U2.94e-10m/s; no active-melt/cut contact.
185us depth300.27333/300.28487um;190us299.77619/299.79078um;
difference0.01154/0.01459um (iso-surface difference, not sub-grid accuracy).
Final retained T weightedRMS1.0075K BUT max237.68K;alpha max0.09933;
epsilon max1,RMS0.01098;Uz RMS0.03730m/s,max14.875m/s;
p_rgh RMS1682.55Pa,max242707.74Pa. Liquid volume difference-0.007254%.
Final Tmax differs1.246%,pVapMax7.705%,QvMax7.516%,depositedPower-0.4154%,
evaporationPower-0.4516%,recoilForceZ29.05%. Do not approve physics based
only on mean temperature/keyhole agreement; local maxima need localization.

Laser profiler2intervals/rank records complete. In last interval full trace
mean16.74s,max244.58s; local mean18.19s,max190.27s;mean exchange415.30/366.37s.
Top two ranks carry48.87%/36.10% of total trace time over10us. Exchange includes
waiting: these values do NOT establish network bandwidth as bottleneck.
Trace imbalance/communication scheduling remain the major laser target;
repeat of prior weighted repartition is not automatically justified.

Next command: bash tests/m247Performance/CollectLocalMeltImpact
Existing mid/final native CSV snapshots only: gasBoth,metalEither,interfaceEither,
liquidMetalEither,coldCutReservoir; maximum locations,weighted norms,phase flips,
worst20cells; validated stage/rank laser profile. No CFD, rebuild or OpenFOAM
utility run. One M247_local-melt-impact-<timestamp>_review.tar.gz.
This is analysis of the completed physical test, not another mesh screening.
Current20% crop alone is insufficient for target24h4um/long tracks. Select
moving/local envelope and optical parallel changes after determining whether
large differences are in retained liquid metal or primarily phase/interface/gas.
Package fix: identical duplicate archive names coalesced; conflicting contents
rejected. Original archive duplicated two solver members with identical hashes.
Production approval remainsfalse.
Local checks:205test cases completed with1Windows symlink skip;
additional output-time-roundoff regression passes(7localization tests).
Actual uploaded laser profiles validated. Normalize only serialization
drift<=1e-12s; reject missing/shifted samples, no nearest-time sampling
or interpolation.

