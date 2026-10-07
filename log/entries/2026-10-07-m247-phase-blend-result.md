# Valid phase blend short probe: convergence passes, width acceptance pending

Archive phase-blend-20261007-182533 hashes/sizes verified, wrapper exit 0.
All jobs use new solver SHA256 99acccf70ef844888d8ff9e2fbd4eb6d60527f9ba9b2e2347ea942b213572440,
same laser library, matched snapshots, 180–180.2 us and 48 ranks.
All 16 runtime records per variant report the expected width 0/0.005/0.01.
All converge with 14–18 correctors and no cap hits. Maximum epsilon residual
is below 8.59e-6; phase-temperature residual below 0.000996 K.

| Variant | Job seconds | Correctors/step | Laser fraction | Thermal fraction |
|---|---:|---:|---:|---:|
| Hard tight | 36.039 | 15.313 | 55.6% | 30.3% |
| Narrow | 37.038 | 17.125 | 53.8% | 32.6% |
| Wide | 38.039 | 16.750 | 54.6% | 31.7% |

Smoothing is not a speedup: observed job overhead about 2.8%/5.6%.
Laser calculation is now the largest measured section in this short sample.

Final all-cell maxima, hard vs narrow: T29.123 K, U8.651 m/s, epsilon1=1,
alpha0.01910, p_rgh1.922 MPa. Narrow vs wide: T21.859 K, U5.558 m/s,
epsilon1=1, alpha0.01642, p_rgh2.197 MPa. Corresponding temperature RMS
0.618/0.448 K and velocity RMS0.0582/0.0468 m/s. RMS is cell unweighted.
Global Tmax/powers change little, but they cannot establish local acceptance.
Raw pressure differences have not been gauge-aligned and do not alone prove
instability. Restart latent response and flow coupling remain unvalidated.
Strict diagnostic equality fails descriptively; convergence does not grant
production approval. Do not choose a width or advance the 4-um/full track yet.

Next: InspectPhaseBlend reads existing final fields of both comparisons,
reports disjoint gasBoth/interfaceOrChanged/metalBoth regions, threshold
counts and worst-cell context, and packages one new localization archive.
No rebuild or CFD. This determines which regions hold large pressure/U/phase
differences before designing energy or longer-window validation.
