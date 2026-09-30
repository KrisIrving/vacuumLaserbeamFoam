#!/bin/bash

if compgen -G "processor0/[0-9]*" > /dev/null; then
    echo "Reconstructing alpha.metal time directories"
    reconstructPar -fields '(alpha.metal)' -newTimes > log.reconstructPar.alpha 2>&1
fi

echo "Sampling keyhole centerline"
rm -rf postProcessing/sample
postProcess     -dict system/sampleDict     -fields '(alpha.metal)'     -time '0:'     > log.postProcess.sample 2>&1

if ! find postProcessing/sample -type f 2>/dev/null | grep -qi 'keyholeCenterline'; then
    echo "ERROR: keyholeCenterline samples were not generated." >&2
    echo "Check log.postProcess.sample" >&2
    exit 1
fi

if ! python3 scripts/extractKeyholeDepth.py     --post-processing postProcessing/sample     --surface-y 200e-6     --output keyholeDepth.csv
then
    echo "ERROR: keyhole-depth extraction failed." >&2
    exit 1
fi

echo "Wrote keyholeDepth.csv"
tail -5 keyholeDepth.csv
