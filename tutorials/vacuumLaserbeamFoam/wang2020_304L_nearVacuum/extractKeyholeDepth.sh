#!/bin/bash

if compgen -G "processor0/[0-9]*" > /dev/null; then
    echo "Reconstructing alpha.metal time directories"
    reconstructPar -fields '(alpha.metal)' -newTimes > log.reconstructPar.alpha 2>&1
fi

echo "Sampling keyhole centerline"
rm -rf postProcessing/sample
postProcess \
    -dict system/sampleDict \
    -fields '(alpha.metal)' \
    -time '0:' \
    > log.postProcess.sample 2>&1

if ! find postProcessing/sample -type f 2>/dev/null | grep -qi 'keyholeCenterline'; then
    echo "ERROR: keyholeCenterline samples were not generated." >&2
    echo "Check log.postProcess.sample" >&2
    exit 1
fi

if ! python3 scripts/extractKeyholeDepth.py \
    --post-processing postProcessing/sample \
    --surface-y 200e-6 \
    --output keyholeDepth.csv
then
    echo "ERROR: centerline keyhole-depth extraction failed." >&2
    exit 1
fi

echo "Sampling complete alpha.metal=0.5 interface"
rm -rf postProcessing/keyholeInterface
postProcess \
    -dict system/keyholeInterfaceDict \
    -fields '(alpha.metal)' \
    -time '0:' \
    > log.postProcess.keyholeInterface 2>&1

if ! find postProcessing/keyholeInterface -type f -name '*.obj' 2>/dev/null | grep -q .; then
    echo "ERROR: alpha.metal=0.5 interface OBJ files were not generated." >&2
    echo "Check log.postProcess.keyholeInterface" >&2
    exit 1
fi

if ! python3 scripts/extractKeyholeSurfaceDepth.py \
    --post-processing postProcessing/keyholeInterface \
    --surface-y 200e-6 \
    --surface-band 8e-6 \
    --output keyholeDepthSurface.csv
then
    echo "ERROR: 3-D connected-surface depth extraction failed." >&2
    exit 1
fi

echo
python3 scripts/compareKeyholeDepth.py \
    --centerline keyholeDepth.csv \
    --surface keyholeDepthSurface.csv

echo
echo "Wrote keyholeDepth.csv and keyholeDepthSurface.csv"
echo "Latest centreline rows:"
tail -5 keyholeDepth.csv
echo "Latest 3-D surface rows:"
tail -5 keyholeDepthSurface.csv
