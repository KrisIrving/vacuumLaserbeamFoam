#!/usr/bin/env python3
import json
import sys
from pathlib import Path

m = json.loads(Path(sys.argv[1]).read_text())

checks = [
    (m["preserveSampledPSD"] is True, "fixed PSD mode not enabled"),
    (27 <= m["particleCount"] <= 31, "unexpected particle count"),
    (0.55 <= m["actualPackingFractionNominalLayer"] <= 0.60,
     "nominal-layer packing outside engineering target"),
    (0.34 <= m["actualSolidFractionGeometricEnvelope"] <= 0.38,
     "80-um envelope fraction outside expected range"),
    (abs(1e6*m["diameterD10_m"] - 36.5) <= 2.0, "D10 drift"),
    (abs(1e6*m["diameterD50_m"] - 52.6) <= 2.0, "D50 drift"),
    (abs(1e6*m["diameterD90_m"] - 74.4) <= 2.0, "D90 drift"),
    (m["projectedCoverageFractionCorridor"] >= 0.80,
     "active-corridor projected coverage below 80%"),
    (1e6*m["maximumUncoveredCenterlineGap_m"] <= 30.0,
     "centerline uncovered gap exceeds 30 um"),
    (m["minimumInterparticleGap_m"] >= -1e-12, "particle overlap"),
]

for ok, message in checks:
    if not ok:
        raise SystemExit(message)

print(
    "M247_POWDER_BED "
    f"particles={m['particleCount']} "
    f"packing50={m['actualPackingFractionNominalLayer']:.6f} "
    f"envelopeSolid={m['actualSolidFractionGeometricEnvelope']:.6f} "
    f"D10={1e6*m['diameterD10_m']:.3f}um "
    f"D50={1e6*m['diameterD50_m']:.3f}um "
    f"D90={1e6*m['diameterD90_m']:.3f}um "
    f"corridorCoverage={m['projectedCoverageFractionCorridor']:.4f} "
    f"maxGap={1e6*m['maximumUncoveredCenterlineGap_m']:.3f}um"
)
print("PASS: M247 fixed-PSD single-layer geometry screen")
