#!/bin/bash

echo "Reconstructing pVap time directories"
reconstructPar -fields '(pVap)' -time '2e-6:' > log.reconstructPar.pVap 2>&1

echo "Sampling pVap on the complete alpha.metal=0.5 interface"
rm -rf postProcessing/keyholeRecoilSurface
postProcess \
    -dict system/keyholeRecoilDict \
    -fields '(alpha.metal pVap)' \
    -time '2e-6:' \
    > log.postProcess.keyholeRecoil 2>&1

if ! find postProcessing/keyholeRecoilSurface -type f -name '*.vtk' 2>/dev/null | grep -q .
then
    echo "ERROR: keyhole recoil VTK surfaces were not generated." >&2
    echo "Check log.postProcess.keyholeRecoil" >&2
    exit 1
fi

python3 scripts/extractKeyholeRecoil.py \
    --post-processing postProcessing/keyholeRecoilSurface \
    --surface-y 200e-6 \
    --surface-band 8e-6 \
    --output keyholeRecoilSurface.csv

if [ $? -ne 0 ]; then
    echo "ERROR: keyhole-surface recoil extraction failed." >&2
    exit 1
fi

echo
echo "Wrote keyholeRecoilSurface.csv"
tail -5 keyholeRecoilSurface.csv
