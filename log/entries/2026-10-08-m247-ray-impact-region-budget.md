# Ray correction impact reviewed; move to spatial/domain cost development

Reviewed M247_ray-physics-impact-20261007-233712_review.tar.gz: all32 manifest
sizes/hashes valid, no missing files, wrapper exit0. Independently reparsed
matching restart/binary provenance, complete timing/physical samples, thermal
convergence and corrected48-rank profiling groups/per-step correction accounting.
Both cases166steps, zero thermal caps, maximum18correctors, means14.319/14.313.
All166 corrected calls have handoff/cutoff records; discarded power at most
0.000330428W per call. No new build failure or missing-file recovery is needed.

Execution passes; strict legacy equivalence fails, as intentionally measured.
Ubuntu final-field norms and localization are archived; raw fields are not,
so those spatial reductions are not independently recalculated here. All-cell
max T327.555K and U10.260m/s occur in gas. Both-state metal max T50.631K,
RMS0.151K,209cells above1K/10above10K; max U0.088729m/s. Interface max T61.232K
and U2.309m/s. Max alpha difference0.015813, epsilon0.014282; zero alpha0.05
crossings. Raw p_rgh changes reach51.696kPa overall/37.053kPa metal; pressure
differences must not be dismissed as a gauge offset without a separate check.
Final absorbed power328.886835/328.692777W, difference0.194058W(0.0590%);
two-sample absorbed-power change at most0.13072%. Final evaporation changes
0.5147%, recoilZ1.019%. Small global differences do not erase localized errors
or establish long-run/grid convergence. Both corrections remain globally off;
continue corrected experimental comparisons, not automatic production promotion.

Jobs344.337/341.329s, ratio1.00881 compares different optical policies, not
equivalent acceleration. Corrected job rate170.6647s/us; mean loop shares
laser49.996%, thermal32.424%, pressure10.255%. Eliminating alpha/momentum/
pressure entirely caps this interval speedup at1.1888x if other costs stay fixed;
eliminating laser entirely caps it at1.99984x. Full-domain work reduction is
necessary for the long-track objective; weighted partition remains rejected.

Also re-read original M247_powderTrack200us8um_results.tar.gz (legacy full run).
Supported, surface-connected moving-keyhole series:100us189.260um,200us316.546um,
growth127.286um; OLS100–200 slope1.24051um/us,150–200 slope0.870376um/us,
180–200 endpoint slope0.863669um/us. No established plateau. Late100–200 unmasked
liquidus-envelope minimum clearance139.741um; earlier20/30us top/z boundaries
approach/touch in that CSV. Because T surfaces include gas, material-filtered
audit is needed before interpreting these as melt-domain failures or selecting
a smaller fine zone. Do not replace the original29.18h full-run cost with a
short-window forecast. Corrected short-window fixed-workload1.5–2mm scenarios
at1m/s already71.1–94.8h at8um, without cooling/domain growth. Refining all
existing edges by2 with r^3 cells/r steps gives an assumed16x work:4um2us pilot
1.517h;19.2h available time permits25.3us under that model. This is a planning
scenario, not measured fine-grid performance or an affordable full-track claim.

Implemented read-only InspectRegionBudget and parallel m247RegionAudit to read
existing original/corrected/legacy fields, compute material/gas masks, volume-
weighted occupancy, conservative vertex envelopes and six boundary clearances.
Python collector validates snapshot/schema/mesh/provenance coverage, separately
reports boundedness, derives existing-keyhole slopes, an80um-padded active
material sizing box and explicit cost ceilings/scenarios. No equations, solver
defaults or source fields change. Automatic named archive includes audit logs,
CSV/report, utility hashes and copied small impact reference logs/configuration.
85 Python tests and Bash syntax pass. Ubuntu compilation/read-only reductions
remain pending; no local OpenFOAM compiler. Next: measured regional sizing for
fixed graded local refinement, then conservative coarse-thermal/local-fluid
coupling. Keep a bounded4um2us pilot before allocating a longer24h test.
