# Longer candidate convergence validation tooling

Following the measured successful 0.2-us probe, added RunThermalValidation: same original 180-us checkpoint, 2-us duration, standard versus ten-times-tighter epsilon/phase-temperature tolerances, 30-minute per-job wall limit, unchanged candidate binary. Both use noRayPaths and identical ASCII field output cadence, avoiding a comparison to the known capped legacy algorithm.

Collector verifies completion, source/binary provenance, per-step phase/epsilon convergence and cap counts. Compares final all-rank internal T/epsilon1/alpha.metal/U/p_rgh fields with scalar/vector maxima and unweighted-by-volume cell RMS, including uniform and gzipped ASCII support. Missing/truncated/non-finite/type/count errors fail collection. Fixed-mesh scope is explicit. Outputs are tolerance sensitivity data, not production PASS; production_approved remains false. Energy balance, keyhole topology, boundaries, larger windows and grid validation remain separate requirements.

Archives now recognise enthalpyStandard/enthalpyTight and include the new field/thermal summaries. Original RunPair and RunThermalProbe numerical controls and output format remain unchanged; ASCII output is limited to the new two validation variants.

Local verification: 25 Python tests passed, including complete validation collection, missing-field rejection, parser cases, and equal setup except tolerances. Shell syntax/diff checks passed. Ubuntu execution and actual tighter-reference runtime remain pending. See tests/m247Performance/THERMAL_VALIDATION.md.
