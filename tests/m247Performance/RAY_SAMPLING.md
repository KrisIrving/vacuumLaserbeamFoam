# Reduced-ray accuracy/cost pair

```bash
git pull --ff-only origin feat/m247-material-port
bash tests/m247Performance/RunRaySamplingPair
```

No new C++ feature or rebuild required. Uses current compiled solver/laser
library and a fresh pair of full756000cell copies from the prepared180us input.
An optional first argument selects a compatible prepared serial full source.
Default tests/m247Performance/runs/local-melt-pair-20261009-164947/fullMelt.
Baseline must use nRadial16,nAngular96. Candidate changes only nAngular to24:
1536->384rays. Radial positions/weights unchanged; angular weight deltaTheta
scales by4, preserving nominal summed seed power to rounding while making
angular coverage coarser. This is an explicit optical discretization error.
Relative rayPowerRelTol remains unchanged; its absolute per-ray cutoff scales
with ray power as defined by the existing solver. No source-hold approximation,
tracking-distance change, packet transfer, thermal cache or residual relaxation.
Both cases preserve every-step optical updates and identical48rank partitions.

The user-selected comparison budget is depth difference<=5%, liquid metal
volume difference<=5%, Tmax difference<=10%, evaluated at BOTH185 and190us.
Measurement-quality/thermal gates must also pass. Report stores the budget
and agreed_error_budget_gate, not a silent tolerance. All diagnostics including
pVap/Qv/recoil/deposited power remain reported even when outside these three
specified metrics. Liquid volume is alpha-weighted liquid inventory; not the
same as a bounding-box volume. Localized T/alpha/epsilon/U/p_rgh errors in gas,
interface and liquid metal are produced in the same archive automatically;
no separate collection command required. Cold-cut mask inapplicable(full mesh).

The pair compares180..190us with outputs185/190us; field distributions may differ
and bit equality is intentionally not required. Profiling verifies actual
1536/384rays per update, source refresh every step, source inputs unchanged.
Error percentages are relative to the current8um baseline, not experimental
truth or proof of long-track/4um accuracy. Passing this short budget is a
candidate for longer validation; production_approved remains false.

One archive contains timing, fields/inventories/keyhole differences, budget
results and automatic localization. Return M247_ray-sampling-pair-*_review.tar.gz
including any failure. Normal completion, no timeout/kill/wclean/rebuild. Baseline
~27minutes; pair anticipated~45minutes plus preparation/localization, no timing
guarantee. With optical51.7% of total, quarter optical cost alone would yield
~1.63x overall speed, not4x. This is a conditional estimate, not measured speed.

## 20261010-202035 measured result and next stage

10us pair:1735.52->1052.49s,1.649x; laser857.50->220.95s. User budget passes
at185/190us. Final depth0.779%, liquid inventory0.0105%,Tmax5.331% differences.
Local interface T errors still exceed2000K; accepted macro metrics do not
establish local field accuracy. Native384-ray candidate is now a measured
accelerator, pending longer validation. No smaller sampling sweep requested.

```bash
git pull --ff-only origin feat/m247-material-port
bash tests/m247Performance/RunRaySamplingLongPair
```

Runs180..200us20us same-checkpoint pair with190/200us outputs and the SAME
384-ray setting/budget. No rebuild. Expected~90minutes plus preparation and
localization; one M247_ray-sampling-long-pair-*_review.tar.gz. Ends at current
laser-path/power table endpoint200us. It does not extend clamped350W into
cooling; an explicit beam-off protocol is needed for the later solidification
stage. This is still8um validation,not24h4um or full1.5..2mm production approval.
