# Ring-staggered384 full history fails; full-ray thermal convergence next

M247_wang-staggered-20261011-231010_review.tar.gz:53 manifest files all match
size/SHA256,missing[],exit0,complete true. Build/runtime/marker gates pass.
17561 steps,12774.814s3.54856h. Historical full-ray job speedup1.69446, original
aligned384 speedup1.05146; historical comparisons, not same-binary timing pair.
Growth32..136um80.33974us versus78.30258us reference (2.60165%).
Final depth/volume/Tmax differences2.71617%/4.95920%/12.96956%.
Full-history pointwise max differences90.1325%/48.1644%/34.8858%; max absolute
depth8.86327um. Tmax error worsens compared to aligned38427.969%.
Thermal gatefalse,222 cap hits,max151,mean15.675; thermal53.75%,laser23.45%.
No approximation/production approval. Staggered option stays default-off.

Stop ray-count/stagger screens. Added one full1536-ray Wang history with
epsilonRelaxation1.0 instead of0.5, the existing bounded-enthalpy supported
range; no new C++ or rebuild. Keep tight1e-5/0.001K residuals,max150,
original aligned optics and unchanged physics/initial mesh/partition.
Hypothesis: full slope correction may converge faster than half correction.
Not a claim of fully coupled Newton convergence. Existing update accounts for
latent+sensible slope; transport/evaporation/diffusion still couple iterations.
Dictionary audit allows only the specified relaxation difference. Thermal
and macro gates remain strict; all cost comparisons to saved runs are labelled
historical. Old1536 reference itself is nonconverged in163 steps, so candidate
passing convergence alone does not establish experimental/model validity.
Shared candidate runner/packager preserves staggered CLI default and adds an
explicit thermal mode; one new complete run, no expensive reference duplicate.
Ubuntu execution pending; local Python and Bash checks pass.
