# NEXT ACTION — M247 fast-track checkpoint

Updated: 2026-10-07

## Current action: offline phase width-response localization

182533 phase probe is valid: new binary/modes, all 16 steps converge, zero caps, 36–38 s. Width sensitivity remains unresolved: narrow/wide max T21.9 K, U5.56 m/s, epsilon1=1, raw p_rgh2.20 MPa. Pull and run `./tests/m247Performance/InspectPhaseBlend tests/m247Performance/runs/phase-blend-20261007-182533`. Send the new localization archive. It reads existing final fields only; no rebuild or CFD. No physical/width acceptance or 4-um/full-track approval yet. See entries/2026-10-07-m247-phase-blend-result.md. Older actions below are superseded.

## Current build repair: initialise phase controls before properties

The 172208 build archive confirms a C++ scope error: createFields.H calls updateProps.H before the old time-loop-only declaration of phaseTemperatureBlendHalfWidth. The setting is now owned and initialised by createFields.H, with shared startup/runtime validation, covering normal and postProcess inclusion. Pull and run `./tests/m247Performance/BuildPhaseBlend` again and send its automatic archive. Actual Ubuntu compilation remains pending. No CFD repeat until build verification. See entries/2026-10-07-m247-phase-blend-initialisation-fix.md. Older actions below are superseded.

## Immediate action: establish the rebuilt solver before more CFD

The 170639 phase-blend archive used the prior binary and lacks both new mode diagnostics in all three cases. Collection correctly failed; these results do not test smoothing. Pull the branch and run `./tests/m247Performance/BuildPhaseBlend`. Send its automatic build review archive. This builds the solver directly and captures build errors, environment, executable path/hash and static feature checks. Do not repeat CFD yet. RunPhaseBlendProbe now rejects old or shadowed solvers before starting cases. See entries/2026-10-07-m247-phase-blend-build-gate.md. Older immediate actions below are superseded.

## Immediate development test: continuous phase-temperature override

Rebuild the branch on Ubuntu and run `./tests/m247Performance/RunPhaseBlendProbe`. It compares hard-rule enthalpyTight and smooth half-widths 0.005/0.01 over 180–180.2 us, all tight thermal tolerances, matched outputs and independent original checkpoints. Send the single automatic archive. Width defaults to zero in the solver and all older probes. This is an experimental mixed-cell closure change; coupling review confirms actual case PowderSim=false and direct epsilon Darcy, with same epsilon/latent/phase-consistency path and candidate rhok recomputation. Restart latent adjustment, width sensitivity, energy and longer-field validation remain pending. Do not interpret smoothing as an approved physical fix. Details: tests/m247Performance/PHASE_BLEND_PROBE.md. Older next actions below are superseded.

## Latest diagnosis: alpha=0.05 phase-rule discontinuity

Localization archive received and verified. The large global T/U extrema are in gasBoth; metalBoth max/RMS differences are T 3.49/0.0123 K and U 0.0355/0.000169 m/s. Interface still has up to 39.2 K and 2.21 m/s differences. All seven epsilon endpoint differences coincide with alpha crossing 0.05. updateProps jumps phase temperatures from pseudo-gas-dominated about 78/91 K to metal 1537/1631 K at this threshold, demonstrating an equilibrium-rule artifact. Next code design must address continuous interface phase treatment together with enthalpy and flow-mask semantics, under an opt-in experimental mode and validation; do not hide it by ignoring interface cells or merely changing convergence tolerance. No localization rerun needed. Full-track/4-um production remains pending. See entries/2026-10-07-m247-localization-diagnosis.md. Older next-action items below are superseded.

## Latest gate: convergence passed, local field acceptance unresolved

User archive validation-20261007-161510 verified. Both 166-step candidates converge, 5.71/6.32 min, no cap hits. But final max differences are T 316.08 K, U 10.59 m/s, epsilon 1, alpha 0.01193. Low RMS does not establish local accuracy. Before more CFD, pull and run `./tests/m247Performance/InspectThermalValidation tests/m247Performance/runs/validation-20261007-161510`; send its new localization archive. It only reads existing fields and reports alpha regions, worst cell state and counts including alpha=0.05 crossings. See tests/m247Performance/FIELD_LOCALIZATION.md. Earlier next actions below are historical and superseded.

## Immediate action: candidate convergence-tolerance validation

Pull and run `./tests/m247Performance/RunThermalValidation` on Ubuntu using the previous candidate solver binary. This compares enthalpyStandard (1e-4 / 0.01 K) with enthalpyTight (1e-5 / 0.001 K) over 180–182 us, with equal ASCII output, independent original checkpoints and 30-minute budgets per job. Send the automatically generated review archive. The collector checks convergence and reports all-rank final internal-field sensitivity; it does not grant physical production approval. Details: tests/m247Performance/THERMAL_VALIDATION.md. After review, plan longer 10–20-us field/keyhole/energy validation before 4-um refinement. Earlier next-action entries below are historical.

## Latest Ubuntu gate and file delivery

The 180–180.2-us candidate completed all 16 steps in 35.04 s versus legacy 127.13 s (3.63x). Thermal correctors fell 151 -> 10–14; cap hits 16 -> 0, with both candidate residual criteria met. Worst legacy cells are at alphaMetal about 0.054 and switch liquid fraction between 0 and 1. Candidate physical diagnostics are close but not identical; long-window, converged reference and field/energy validation are next. See `entries/2026-10-07-m247-thermal-probe-result.md`. Earlier next-action text below is historical.

Both test wrappers now create a named review tar.gz automatically; send one archive. Manual packaging of existing runs uses `python3 tests/m247Performance/package_results.py --work <run-directory>` and requires no new CFD calculation. The user's current run is `tests/m247Performance/runs/thermal-20261007-154702`.

## Current priority after Ubuntu logs

The 180–182-us ray pair measured 1.120x job speedup, but both variants hit the thermal cap in all 166 steps. All 25,066 logged max epsilon increments equal 1; temperature linear solves take 1–2 iterations. Full residual histories match between modes. Investigate nonlinear phase correction before any 4-um or full-track run.

Next Ubuntu action: build and run `./tests/m247Performance/RunThermalProbe`, an independent 180–180.2-us legacy/candidate pair with residual cell locations and a 15-minute wall budget per job. See `tests/m247Performance/THERMAL_PROBE.md`. The candidate is default-off, includes a phase-temperature consistency gate, and is not production approved. Send both logs and metadata. Older pending-test notes below are historical and superseded by this priority.

## Active branch

    feat/m247-material-port

## Physics gates already passed

- Wang near-vacuum model frozen.
- M247 Mondal/Wang constitutive gate passed.
- 100-us M247 bare-plate transfer passed.
- Fixed-PSD M247 powder generator passed.
- 100-us powder preflight passed.
- 200-us / 756k-cell M247 powder track completed on 48 ranks.

## 200-us result

- wall time: 29.18 h;
- keyhole depth at 200 us: about 316.5 um;
- depth-growth rate is decreasing but not yet a strict plateau;
- final liquidus-envelope clearances are adequate in x/y/z for this case;
- straightforward full-domain 1.5-2 mm CFD is computationally unacceptable.

## Current engineering constraint

Any M247 4-um validation job should finish within 24 h.

Do not run a full-domain 4-um case.

The planned 4-um validation is:
- restart from an evolved 8-um state;
- refine only a compact keyhole/melt-pool ROI to 4 um;
- run approximately 20-30 us;
- compare against the corresponding 8-um history.

## Immediate next gate — mature-state performance pair

The 2026-10-07 phase-1 development provides an optional ray-history optimization
and MPI-aware schema-2 timers, including field/ray I/O and thermal cap hits.
Start with `tests/m247Performance/README.md` and the independent180–182 us pair:

    ./Allwmake -j 48
    ./tests/m247Performance/RunPair

The pair copies the completed reference case state and preserves the original.
It tests default ray history versus `recordRayPaths false`; no measured speedup
or completed Ubuntu validation is claimed yet. Send comparison JSON/CSV and
both solver logs. Expected first-pair cost is around an hour plus preparation,
with a2-hour budget per job. Details and failure rules are in the test README.

Do not run the older initial-state10-us probe as the first gate when the mature
180-us checkpoint is available. The existing probes below remain alternatives.

## Existing performance probes

The solver has optional PERF_DIAGNOSTICS instrumentation. It preserves the
original operation order and is disabled unless requested by vacuumProperties.

Benchmark case:

    tutorials/vacuumLaserbeamFoam/M247_0p6Pa_perfProbe8um

It uses the same 756k-cell geometry and physics as the 200-us case, but runs
only 10 us.

Local sequence after pulling the current branch:

    ./Allwmake -j 48
    cd tutorials/vacuumLaserbeamFoam/M247_0p6Pa_perfProbe8um
    ./Preflight
    ./Allrun
    grep '^PERF_DIAGNOSTICS ' log.vacuumLaserbeamFoam

Do not change solver tolerances, Courant limits, ray counts or physics until
the timing split is measured.

## Production strategy under evaluation

Preferred architecture for the final 1.5-2 mm track:

1. moving/local high-fidelity VOF + momentum + recoil + ray-tracing region
   around the laser/keyhole;
2. outer/coarse region solves thermal conduction/phase thermal history only;
3. transfer temperature/enthalpy between the local CFD zone and global thermal
   domain;
4. use the thermal domain for the trailing solidification/cooling history.

This is consistent with published local moving thermal-fluid and local
multi-mesh approaches and will be validated against the existing full-CFD
100-200-us results before production use.
