## 2026-10-10 122734: invariant thermal cache equivalent but no measured speed benefit

Review archive complete, wrapper exit0, missing files0; every manifest SHA256
verified. Ubuntu OpenFOAM v2512 compile/link succeeded. Both180..190us full
756000cell48-rank runs completed834steps; all initial fields and partitions
matched, source unchanged. Both thermal gates and exact sampled equivalence
passed: all T/alpha/epsilon/U/p_rgh differences at185 and190us zero; all
compared physical diagnostics and keyhole depths identical. Mean thermal
correctors14.54676259,max18,limit hits0 in both. Cache records834 in each.

Baseline solver1653.52078s(27.5587min), cache1674.08059s(27.9013min),
speedup0.987719: candidate1.2434%longer. Thermal542.73022->548.13480s(+0.996%),
laser849.64750->844.83857s(-0.566%),pressure144.98111->158.59165s(+9.388%).
Single sequential pair does not isolate a systematic cache slowdown from
machine/run variability. It DOES provide no measured acceleration and no
reason to enable this optional cache or repeat it. Defaultfalse retained.
Numerical equivalence at sampled times is not a long-track production approval.

Baseline modules: laser51.433%,thermal32.854%,pressure8.776%,momentum3.117%,
alpha2.551%. These are mature-state10us measurements, not an attribution of
all29.18hours of the older full200us run. Historical thermal151correctors/step
was fixed by previous phase/enthalpy work; current14.55correctors is not the
same old bottleneck. Do not extrapolate this single mature segment into a
24h4um guarantee, combine unvalidated speedups, or claim tiny invariant-cache
work solves the major cost problem.

Decision checkpoint: stop the lagged-optics approximation (failed molten
interface/phase accuracy), stop invariant-coefficient performance tuning
(no saving). No additional Ubuntu rerun requested for either experiment.
Next major development target is exact every-step optical parallel transport
and workload balance, with unchanged rays/path stepping/absorption/cutoff.
Current replicated ray lists combineGather+broadcast after local tracing;
blocking exchange times include idle ranks waiting for expensive tracing.
Top2trace ~49% persists. Do not label94.7%exchange as pure network transfer
or repeat rejected rayQ-weighted Scotch (previously slower and physics failed).

Implementation constraints for next optics transport development:
- Preserve baseline route and default configuration for reproducible comparison.
- Keep mesh/CFD decomposition and every-step optics identical; optical work
  routing must not silently change cell owner or absorption deposition owner.
- Account for every ray by globalRayIndex, route position/direction/power and
  termination consistently, reject duplicate ownership rather than lose energy.
- Verify frozen deposition distribution plus total power and ray termination
  before full180..190us matched-field/cost comparison. These are validation
  stages of transport correctness, not another mesh/threshold screening sweep.
- Rebuild only modified library and dependent solver with official wmake;
  package any build/validation failure in one uniquely named review archive.
Moving local CFD/global heat remains long-track architectural work; optical
transport is a substantial prerequisite, not an already achieved coupled solver.
No new optics implementation or measured speedup is claimed by this checkpoint.

