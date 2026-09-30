#!/bin/bash

if compgen -G "processor0/[0-9]*" > /dev/null; then
    reconstructPar -fields '(alpha.metal)' -newTimes > log.reconstructPar.alpha 2>&1
fi

postProcess -func sample -time '0:' > log.postProcess.sample 2>&1

python3 scripts/extractKeyholeDepth.py     --post-processing postProcessing/sample     --surface-y 200e-6     --output keyholeDepth.csv

echo "Wrote keyholeDepth.csv"
tail -5 keyholeDepth.csv
