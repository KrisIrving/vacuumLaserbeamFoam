# Region budget reviewed; field-driven local mesh preview

Reviewed `M247_region-budget-20261008-002346_review.tar.gz`: all 30 manifest
sizes/SHA256 match, wrapper exit 0, no missing files. Recomputed the collector
report from the archived audit/reference logs and obtained the same JSON.
Raw fields are not archived; native cell reductions are Ubuntu evidence.

All 12 original/legacy/corrected snapshots complete with finite fields and
zero alpha/epsilon bound violations. Molten metal has minimum boundary
clearance 136 um, above the 80 um audit threshold. This is snapshot evidence,
not a full-track boundary guarantee. Original molten occupancy grows from
0.9423% at 100 us to 2.3052% at 200 us. Active proxy occupancy grows from
1.6426% to 3.4200%, but dispersed powder interfaces stretch its bounding box.
The padded union box covers 77.5% of the domain and estimates 6.35 million
4 um cells. Reject that box as an economical refinement selection.

Original keyhole depth grows 189.260 to 316.546 um between 100 and 200 us.
The 150-200 us fitted growth is 0.870376 um/us: no established plateau.
Legacy and corrected 182 us molten envelopes/counts coincide, but this does
not erase the previously measured field differences or approve corrected physics.

The corrected short-run cost is 170.665 s/us on 48 ranks. Fixed-workload
1.5-2 mm scenarios at 1 m/s are already 71.1-94.8 hours on the 8 um case,
before cooling/domain-growth costs. Uniform edge halving assumed at 16x work
makes 2 us at 4 um about 1.52 hours and a 19.2-hour compute allocation about
25.3 us. At 2 um the assumed 256x scaling makes even 2 us about 24.27 hours.
These are extrapolations, not measured fine-mesh runtime. Removing every flow
stage has only a 1.19x theoretical cap in this window; laser removal caps at
about 2x. Therefore regional mesh reduction is the next measurable step.

Added `PreviewLocalRefinement`: copied 180 us fields, all mixed cold powder
interfaces plus warm material/gas, four/ten cell halo alternatives, one native
hex split, three-million-cell pre/post budget, strict mapped moments/bounds
and full mesh-quality checks. No solver runs. A new finiteVolume/meshTools
utility avoids the prior missing AMI dependency. Root logs are distinctly named
and automatically packaged on success/failure. See LOCAL_REFINEMENT.md.

Local validation: 88 Python tests pass, including mapping-loss detection,
selection completion/count validation, and partial preview packaging. Bash
syntax passes. No OpenFOAM compiler here: native build/refinement is pending
Ubuntu. No production, isoAdvector/enthalpy/flux, optical, or speedup approval.
After mesh evidence, validate restart treatment and a bounded CFD pilot;
moving fine region with conservative outer thermal coupling remains the
long-track architecture rather than a claim that disabling flow alone suffices.
