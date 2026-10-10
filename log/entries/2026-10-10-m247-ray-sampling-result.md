## 2026-10-10 202035: reduced-ray budget PASS and measured1.649x; longer validation

Review archive complete,exit0,missingfiles0; all manifest file SHA256 verified.
Both full756k48rank180..190us jobs completed834steps. Every-step optics,
actual1536/384ray counts, source unchanged and measurement/thermal gates pass.
Baseline1735.51574s(28.9253min),candidate1052.48911s(17.5415min),1.64896x:
39.356%less solver wall. Laser857.49695->220.95305s,3.881x/74.233%less;
thermal592.76080->559.30755s. Non-laser differences include run variability and
changed physics. Candidate thermal53.221%,laser21.025%,pressure14.333%:
optics sampling achieved a clear gain but remaining bottleneck shifts to heat.
Do not imply4x full-job speed or multiply older unvalidated speedups.

User budget(depth5%,liquid volume5%,Tmax10%) passes at BOTH samples.
185us depth+0.44897um(0.14952%),liquid volume0.004559%,Tmax2.89826%.
190us depth-2.33494um(0.77889%),liquid volume0.010462%,Tmax5.33138%.
Baseline/candidate depth299.77619/297.44125um at190us. Both connected,
iso-bottom support21/15. Values are8um-mesh iso diagnostics,not subgrid accuracy.
Thermal mean14.54676/14.56115,max18,no limit hits. No production approval yet.

Accuracy scope is explicitly the user-chosen three scalar metrics, not full
local temperature/phase equivalence. Liquid interface T RMS29.2811->51.2145K
from185->190us,max1097.156->2025.127K. Liquid epsilon maxdifference0.68855/
0.73160. Interface T RMS30.5246->55.3064K. At190us pVapMax29.6335%,QvMax
32.0161%,evaporationPower20.5173%,recoilX30.1659% differences; these remain
visible in reports and are not secretly subjected to unrequested new limits.
Candidate meets allowed macro metrics but has large local field differences.
No interpretation as experimental or long-track accuracy. Preserve384candidate
and user budget; do not start another smaller-angle screening sweep.

Next implemented RunRaySamplingLongPair: from SAME180us checkpoint,180..200us
20us pair, outputs190/200us. nRadial16/angular96vs24, unchanged physics flags.
Metadata duration/endTime and reconstruction/keyhole/sample/error times updated
consistently; short-probe schedule remains185/190us. Every-step refresh helper
already derives half/end times, now190/200us. No new C++ or rebuild needed.
Same source/partition/thermal/raycount checks and automatic localization. Both
stages end at existing laser path/power endpoint200us: do NOT silently continue
clamped350W heating past200us. Cooling/solidification needs an explicit later
laser-off schedule and is not claimed completed by this20us heating test.

Local44checks(43pass,1Windows symlinkskip),Python compilation/Bash syntax pass.
New regression test verifies error report uses longer sample times, not old
185/190us constants. Based on measured pair,expectroughly90min+preparation/
localization;no forced timeout. Long-run errors and benefit still unmeasured.
4um24h/full1.5..2mm track remain unverified and are later stages after sustained
accuracy/cost acceptance; this is a real acceleration milestone,not final goal.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunRaySamplingLongPair
Return one M247_ray-sampling-long-pair-<timestamp>_review.tar.gz,including failure.

