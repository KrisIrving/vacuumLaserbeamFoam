# Wang full-history suite: collector tuple contract error and offline repair

Reviewed M247_wang-ray-suite-20261011-000847_review.tar.gz:152 files match
manifest lengths/SHA256; all four solver jobs have returncode0, no forced/budget
stop and complete140us diagnostic/surface histories. Missing summary/volume
exports were caused by our collector assigning read_probe outputs incorrectly.
read_probe returns metadata, timing summary, physics records; summarize treated
metadata as summary and raised KeyError('steps'). Corrected unpacking and added
a summarize regression with that exact tuple contract and convergence consumer.
New CollectWangRaySuite performs collection/package only, using existing fields;
no CFD, reconstruction, native build or parameter changes.

Measured wall hours1536/768/384/192 rays:6.01290/4.22762/3.73116/3.96319.
Speedups1/1.42229/1.61154/1.51719:192 is slower than384 because steps increase
18008->20852. Growth32..136um:78.30258/80.15066/81.81625/84.30545us.
Final depths175.35517/176.65773/174.49120/164.71504um. Relative final depth
deltas0.7428%/0.4927%/6.0678%; final Tmax deltas3.8114%/3.2801%/11.0439%.
These endpoints are not full-history acceptance. Maximum Tmax history errors
normalised by reference peak are18.7429%/23.3172%/33.9068%, so no reduced-ray
variant satisfies the user's10% pointwise Tmax budget over the full history.
Early small-depth relative errors are large; absolute depth max differences
5.45846/6.89430/12.02279um are also reported for interpretation.

All variants have thermal cap/nonconverged steps163/199/232/316, roughly
0.96%/1.20%/1.29%/1.52%. This affects full-ray baseline too. Worst phase
temperature residuals0.01126/0.01917/0.01584/0.02019K against0.001K target;
not evidence of divergent temperatures, but declared convergence was not met.
Worst cells are near-pure metal in melting interval, not prior interface
epsilon0/1 oscillation. Do not silently loosen tolerances or approve production.
Historical frozen Wang growth is76.2318us; current
full-ray78.30258us is a changed numerical baseline and must be reviewed.

At75us after32um stage, current axial/scalar loads differ substantially across
variants; keep distinct quantities and avoid claiming scalar load equals axial
force. The archive lacks liquid volumes because collection failed; Ubuntu
offline collection is required before completing the three-observable report.
Next action is collect existing evidence, then address full-history thermal
convergence/current-baseline differences before more expensive CFD screening.
19 Python tests and Bash syntax passed; no new simulation result claimed.
