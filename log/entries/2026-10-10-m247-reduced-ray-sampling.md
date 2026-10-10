## 2026-10-10: user-authorized approximate optical sampling with explicit budget

User requested fast approximate ray tracing and accepted accuracy sacrifice.
User-selected budget relative to current baseline: keyhole depth and liquid
metal volume differences<=5%,Tmax<=10%. Honor this scope; no bit equality
requirement for approximate optics. No production approval on10us alone.

RunRaySamplingPair added: no native code/rebuild, existing official nAngular
setting96->24, nRadial16 fixed,1536->384ray samples. Radial weights unchanged;
angular area deltaTheta increases4x,nominal seed power sum unchanged to rounding.
Relative power cutoff unchanged; absolute per-ray cutoff follows existing max
ray power normalization. All propagation distances,absorption/reflection/
handoff/termination unchanged,every-step source update required. Packed mode
and thermal cache off,visual ray paths off in both. All other constant physics
settings exact; samefull756kmesh/initial fields and48Scotch partitions verified.
Fresh copies only; /media and home aliases resolved. Original source untouched.

Two180..190us jobs with185/190us outputs. Budget checks ALLthree metrics at
BOTHtimes, plus thermal and measurement-quality gates. Report finite values,
missing/zero-baseline metrics fail approval. Report full diagnostics including
pVap/recoil/power without hiding deviations. Actual emitted rays verified from
profile as1536 or384 per update. Automatic liquid/interface/gas localization
included in same archive to avoid another collection command. No cold cut.
No acceptance silently extrapolated to full track/4um/experiment accuracy.

Local43tests(42pass,1Windows symlink skip),Python compilation and Bash syntax
pass. New3tests cover optical-settings isolation,actual ray count mismatch,
user limits at both samples and missing/nonfinite/over-budget failures.
Native solver already compiled in99158cf test; no new C++ compilation needed.
No approximate sampling performance or accuracy measured yet. Conditional
quarter of~51.7% optical work suggests~1.63x total if other cost unchanged;
not4x full-job acceleration. Pair expectedroughly45min pluspreparation/localization.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/RunRaySamplingPair
Return one M247_ray-sampling-pair-<timestamp>_review.tar.gz,including failure.
If budget and useful speed pass, next advance longer melting/solidification
validation rather than another small angular-count screen. Major architectural
work is deferred until this authorized approximation has measured evidence.

