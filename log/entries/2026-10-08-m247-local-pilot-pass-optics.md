# Projected local pilot passes compatibility; investigate optical grid sensitivity

110422archive23SHA256/sizes valid, wrapper0, no missing files. Independently
reconciled read_probe timers/physical samples,22 per-step thermal residuals,
pre/post writtenflux and final native moments/flux. Source fingerprints equal
the104821 audited fine case. Actual raw fields are Ubuntu evidence, not archived.

Projection changes only180us phi. divL1 falls88759.27 to9.84136e-10/s,
divRMS2.1383e-9,max1.3822e-7/s, net5.6655e-21m3/s. Written field reread passes.
0.2us48rank pilot:22steps,133.1398s job,128.9584s loopmax sum,665.699s/us job,
644.792s/us loop. Thermalmean16.2727/max18,no caps, all residual gates pass.
Final alpha/epsilon[0,1], original2283911cells, divL1/RMS/max
0.0116444/0.0673477/20.4963 persecond. Source remains unchanged.

Compatibility passes, not production. FinalglobalTmax4448.045K versus mapped
initial4151.291K; global includesgas. Depositedpower287.944/287.988W at180.1/180.2us.
Earlier coarse-windowpower~328W is not same-time/frozen matched evidence.
Need separate optical grid/input effects before spending longer CFD time.

Currenttimings thermal46.79pct,laser23.76pct,pressure18.83pct,alpha3.48pct,
momentum4.02pct. Fixed-cost24h~129.8us or19.2h~103.8us; full1.5-2mm~277-370h
at1m/s beforegrowth/cooling. Not a forecast; local refinement saves cell count
versus globalrefinement but cannot alone make complete tracks affordable.

Added RunLocalOptics: hash-checked copies of coarse/fine180us snapshots,
two frozen captures and three one-call traces (coarse owninputs,fine owninputs,
fine withmapped coarse opticalinputs). Restricted native mapFieldsPar only
maps filteredalpha/normal/resistivity withcellVolumeWeight, guard all other
files; eachtrace verifies no material/time advance and ray/rank work. Same
binary provenance across five launches; all roles archived distinctly. Reports
powercontrasts asobservations, not equality/production approval. No CFD loops,
solverdefaults or C++ changes. Existing frozen mode ends before flux/time loops,
so the retained unprojected phi in original snapshots is not used to advance CFD.

103Python tests pass plusBashsyntax/pycompile. New native mapping/orchestration
pendingUbuntu. NextRunLocalOptics and send M247_local-optics archive; no repeated
fluxpilot or longer CFD required now. See LOCAL_OPTICS.md.
