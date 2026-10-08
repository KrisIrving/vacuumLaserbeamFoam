Reviewed moving-window154937:8archive files SHA256/size valid,exit1,no missing.
Stagedconstructor works and step0 initialstate records756000cells; V0() still
aborts inside prepareOldVolumes before topologyupdate. storeOldVol isconditional
on new timeindex exceedingcurTimeIndex; driverresetindices1..8 can be behind
restart's currenthistoryindex. Fix syntheticindices to max(currentTimeIndex,
meshhistoryIndex)+step. Emit previous/current indices andcheckstrictadvance,
continuity andpreupdateV0size/finite/exactvalues; noprivatepointer/geometryhack.
Addedautomatic2400cell blockMesh preflight exercisingidentical8nativeupdates,
linearproxy/coverage/coarsening checks beforelargecasehash/copy.120secondpreflight
budget, failurelogs/report bundled; actual2400cell count validatedseparately.
Realnative30minute budget andsource/cell/geometry gates unchanged. NoCFD or
production/speedupapproval.116Python tests passed includingindexfailure and
smallpreflight failurepackaging; py_compile/whitespacepass. Nativefix/small+large
runs require Ubuntu. Nextpull andsameRunMovingWindow freshdefaultwork;
sendautomaticM247_moving-window-...review.tar.gz on success orfailure.
