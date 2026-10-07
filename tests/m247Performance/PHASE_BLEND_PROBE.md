# Experimental continuous phase-temperature override

Purpose: replace the demonstrated hard alpha=0.05 phase-temperature jump with a continuous numerical candidate, while retaining the same phase variable across its existing energy and flow couplings. This is a changed mixed-cell closure, not merely a faster iteration or a new material law. It is default off and not production approved.

## Candidate

MELTING/phaseTemperatureBlendHalfWidth defaults to 0, preserving the old operation order and override. Positive widths require boundedEnthalpyCorrection and must be <0.04, ensuring the transition stays above the gas-filter threshold 0.01 and below full-metal cells.

For centre a0=0.05 and half-width h, s=clamp((alpha-(a0-h))/(2h),0,1), w=s*s*(3-2*s). The solidus and liquidus both become (1-w)*legacyMixedTemperature + w*metalTemperature. At/below a0-h the old mixed branch remains exact; at/above a0+h the full-metal branch remains exact. Inside the band, both values and their first derivatives are continuous and the positive melting interval is preserved for bounded alpha. Widths 0.005 and 0.01 are numerical sensitivity choices, not measured material properties. No physical justification of either width is claimed yet.

The solver keeps epsilon1 as its existing numerical mixture phase indicator, not a newly defined pure-metal liquid fraction. It uses the new phase temperatures in Tcorr, the enthalpy-slope correction and the phase-temperature convergence check. Existing mixture cp and filtered latent heat, latent ddt/advection terms, evaporation/radiation functions and Darcy/surface-force expressions remain. Candidate rhok is recomputed after phase temperatures are updated, so buoyancy uses the same curve. In the actual M247 case PowderSim=false despite the powder geometry: Darcy acts directly on epsilon1. In PowderSim=true cases the legacy e1temp<=0.95 mask still exists; it is a separate discontinuity this experiment does not eliminate or validate.

The alpha_filtered 0.01/0.99 clips and other legacy rules remain. Thus this patch does not establish a wholly continuous or physically conservative multiphase model. It targets one evidenced discontinuity, examines coupled response, and must not be accepted merely because endpoint flips disappear.

Restart epsilon is copied unchanged, not reset to the new phase curve. The first steps can therefore contain a latent enthalpy adjustment from changing the closure. That response is included in TEqn's existing latent term; it still needs energy-accounting validation. The short probe measures restart/convergence/width response, not a settled new-model trajectory.

## Ubuntu test

With OpenFOAM v2512 sourced, from the repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./Allwmake -j 48
./tests/m247Performance/RunPhaseBlendProbe
```

Three fresh independent runs restart the original 180-us checkpoint and finish at 180.2 us:

| Variant | Half-width | Transition alpha range |
|---|---:|---|
| enthalpyTight | 0 | original hard rule |
| phaseBlendNarrow | 0.005 | 0.045–0.055 |
| phaseBlendWide | 0.01 | 0.04–0.06 |

All use identical epsilonTolerance=1e-5, phaseTemperatureTolerance=0.001 K, noRayPaths, ASCII field output, laser/material data, ranks and other controls. Only the candidate width changes. New diagnostics report width and override weight, and the collector rejects binaries that do not report the new mode. This patch requires a rebuild.

Default budget is 15 minutes per job. Earlier tight-candidate speed suggests roughly 40 seconds per 0.2-us baseline plus preparation/writes; new closure runtimes are unmeasured. Allow several minutes for the triplet and collection, but no completion-time promise is made. Failed runs also produce an archive of available evidence.

The collector checks matching snapshots/binary hashes, fixed mesh, complete intervals, per-step residual criteria and zero cap hits. It reports hard-versus-narrow response and narrow-versus-wide sensitivity for diagnostics and final T/epsilon/alpha/U/p fields. The report always has production_approved=false; strict diagnostic equality is only descriptive for different closures. Energy/phase topology/longer-window validation remains required. No arbitrary field threshold is assigned as approval.

Send the single printed archive `runs/M247_phase-blend-<timestamp>_review.tar.gz`. It contains named logs, probe/run metadata, exact dictionaries and phaseBlendReview.json/phaseBlendFields.csv/phaseBlendDiagnostics.csv. Full processor fields remain on Ubuntu for later localization.

Local checks: 31 Python harness/model/collector tests and shell syntax/diff checks. Mathematical tests cover endpoint matching, threshold continuity, positive phase span, and isolated enthalpy iteration; they do not compile or execute OpenFOAM. Ubuntu compilation, closure response, width sensitivity, energy accounting and CFD accuracy remain pending.
# Build gate after the 170639 review

The uploaded run used the previous binary; missing phase-blend diagnostics
correctly caused collection failure. First run `./tests/m247Performance/BuildPhaseBlend`
and send its single review archive. It captures direct solver build output,
selected OpenFOAM paths, executable hash and compiled diagnostic markers.
Failures are packaged too. The phase wrapper now checks markers and rejects
PATH shadowing before CFD. Runtime width/weight validation remains necessary.
Do not rerun the three cases until the build archive is reviewed.
