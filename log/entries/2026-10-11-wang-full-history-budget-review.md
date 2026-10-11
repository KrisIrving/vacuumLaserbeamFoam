# Completed Wang ray-count evidence; no passing reduced-ray full history

Archive M247_wang-ray-suite-20261011-000847_review(1).tar.gz:161 manifest
files all match size/SHA256; missing_files[], exit0, complete true. Four jobs
and volume/depth/recoil histories complete. No CFD rerun needed.

1536/768/384/192 cost6.013/4.228/3.731/3.963h.384 is fastest,1.6115x and
37.95% less wall. Final depth/volume/Tmax relative differences for768:
0.7428%/0.5678%/3.8114%;384:0.4927%/2.6788%/3.2801%;192:
6.0678%/8.0803%/11.0439%. Full-history pointwise maxima differ substantially:
768 depth23.53%,volume20.54%,Tmax18.74%;38464.39%/53.87%/27.97%;
192181.04%/41.74%/43.28%. Huge initial depth ratios occur at0.056um or
0.897um and must be interpreted with absolute errors, not erased from gates.
After40us768 max depth4.003%,volume3.187%,Tmax18.743%;384
6.836%/6.335%/27.969%;1927.922%/11.459%/43.282%.

Worst sampled Tmax discrepancy times:768 at124us,384 at54us,192 at98us.
All full histories fail agreed5/5/10% budget. All variants, including current
1536 baseline, retain prior163/199/232/316 thermal cap/residual failures.
production_approved false; no automatic recommendation. Near endpoint agreement
does not establish local temperature/recoil accuracy or experimental validity.

Next useful development is offline hotspot classification at actual worst
times, onset2us and final140us, using retained reconstructed fields. Added
temperatureHotspots.json with global hottest cells, gas/interface/metal
temperature maxima and largest cell temperature differences. Coordinates are
not guessed. This diagnoses whether the peak is metal/interface/pseudo-gas;
the global Tmax budget is not silently changed. No new CFD/build/native code,
ray-count sweep or relaxation/tolerance change.21 local tests passed.
Then choose sampling/thermal work based on actual hotspot evidence. Do not
attribute cap failure to old interface phase oscillation: prior worst cap cells
were almost pure metal in1697..1727K interval. Classification pending Ubuntu
offline collection; full model/production claims remain withheld.
