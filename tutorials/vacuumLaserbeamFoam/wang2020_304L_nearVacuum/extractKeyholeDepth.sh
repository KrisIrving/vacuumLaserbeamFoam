#!/bin/bash
set -euo pipefail

# The reference solver is normally run in parallel. Reconstruct alpha.metal
# first if reconstructed time directories are not already present.
if compgen -G "processor0/[0-9]*" > /dev/null; then
    reconstructPar -fields '(alpha.metal)' -newTimes         > log.reconstructPar.alpha 2>&1 || true
fi

postProcess -func sample -time '0:' > log.postProcess.sample 2>&1
python3 scripts/extractKeyholeDepth.py     --post-processing postProcessing/sample     --surface-y 200e-6     --output keyholeDepth.csv

echo "Wrote keyholeDepth.csv"
