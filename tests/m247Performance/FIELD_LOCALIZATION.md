# Inspect the existing 2-us validation fields before extending CFD

The submitted validation-20261007-161510 review archive has complete metadata; all manifest SHA256 values and byte counts were verified. Both variants covered 180–182 us, 166 steps, zero thermal cap hits and their configured nonlinear tolerances. Standard wall time is 342.355821 s (5.71 min), tight 379.395654 s (6.32 min), total 12.03 min excluding preparation/collection.

However, final all-cell maxima are T difference 316.081105 K, U difference 10.5905171 m/s and epsilon1 difference 1. Their cell RMS differences are 0.5579569 K, 0.0214054 m/s and 0.00304298, respectively. Alpha max difference is 0.01193368 and pressure max difference 53.683 kPa. Global extrema/integral diagnostic differences are much smaller: final Tmax difference 1.493445 K, deposited-power difference 0.0115544 W and interface-area relative difference about 4.925e-7. Such integral agreement does not settle local field accuracy. Low RMS/high maxima suggest concentrated differences, but the supplied archive has no full fields or locations; the regions remain unknown. Strict diagnostic_pass=false is the original equality check, not an assigned field acceptance test.

Do not extend the CFD run merely to collect these locations. In the Ubuntu repository root, use the already saved fields:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/InspectThermalValidation \
  tests/m247Performance/runs/validation-20261007-161510
```

This launches no CFD, changes no stored fields and needs no solver rebuild. It reads both cases' final 182-us ASCII fields across all 48 processors and adds small localization summaries to the existing comparison directory. Existing localization files are not overwritten. The job may take minutes for field reads/analysis, depending on storage. Original review archives are retained; a differently named localization archive is printed. Send that single new `.tar.gz` file.

The report includes:
- max/RMS and counts above explicit diagnostic thresholds for T/U/epsilon/alpha/p_rgh;
- disjoint gasBoth (both alpha<=0.01), metalBoth (both alpha>=0.99), and interfaceOrChanged bins;
- top 10 cells by difference for each field, with rank/local index and both states' T, epsilon, alpha, U and p_rgh;
- counts of cells whose alpha crosses 0.05, the phase-temperature override threshold, and how many also have epsilon difference >0.99.

Threshold counts are descriptive, not physical acceptance limits. Regions require both states, so a shifted interface is not mislabeled as gas or pure metal. Coordinates are not inferred from local indices; the mesh is fixed and source snapshots/decomposition match. This report excludes boundary fields and is not an energy/keyhole-conservation test. Convergence gate is distinct from production approval, which remains false. Whether gas/interface differences can be accepted requires examining their magnitude and influence, not just relabeling them.

If localization confirms an unacceptable material/interface difference, next development will target that cause or require tighter settings before longer 10–20-us/grid validation. The new report avoids an extra simulation while resolving the immediate uncertainty.

Local verification: 27 Python harness/model/parser/localization tests and Bash syntax/diff checks passed. Actual localization of the user's saved fields is pending Ubuntu.
