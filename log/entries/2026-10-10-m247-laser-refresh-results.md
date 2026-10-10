## 2026-10-10 112226: laser refresh measured saving with unresolved physics error

Archive verified against every manifest SHA256; wrapper exit0, missing files0.
OpenFOAM v2512 solver compile/link succeeded after Foam::pow qualification.
The alphaEqn.H dependency warning did not prevent compilation or execution.
Both756000cell full-domain cases have identical initial fields and all48
cellProcAddressing hashes. Both180..190us CFD runs completed834steps with
thermal gates true, max18correctors and zero thermal limit hits.
Baseline1642.2865s(27.37min), candidate1231.2856s(20.52min):1.3338x,
25.025%less solver wall. Laser section858.447->429.970s; thermal534.692->540.995s.
Candidate418updates/416held steps; held age<=12.239ns,alpha change<=0.026183,
motion<=0.115379cells. Guard compliance is not physical acceptance.
At190us Tmax4193.418->4388.374K(+4.649%),pVapMax+30.050%,QvMax+27.968%,
deposited power326.628->323.519W(-0.952%). T field max difference903.176K,
RMS2.964K; alpha max0.286795. At185us T max difference154.335K,RMS0.726K.
Error grows within10us. Keyhole depth difference190us+0.09749um on8um grid
and liquid volume difference+0.0048448% do not excuse peak/interface error.
RecoilZ relative change53.27% on a small component must be read with its
absolute change3.6791e-5N. No production approval; default refresh interval1.

Next: read existing CSV snapshots, localize liquid-metal/interface/gas errors
before changing guard thresholds. New CollectLaserRefreshImpact uses current
completed run as default; no build, OpenFOAM commands, or CFD advancement.
Collector now validates optical profile counts against actual refresh updates,
not CFD steps. Full domains have no cold cut; that region is marked inapplicable.
15 relevant tests pass; actual834/418-call archived profiles validate; Bash syntax
passes. Full CSV snapshots remain on Ubuntu and are absent from the review
archive, so spatial localization must run there. No repeat CFD requested yet.

Run: git pull --ff-only origin feat/m247-material-port
     bash tests/m247Performance/CollectLaserRefreshImpact
Return one M247_laser-refresh-impact-<timestamp>_review.tar.gz.
Moving/global thermal coupling remains necessary for the long-track target;
this measured25% saving alone does not establish24h4um feasibility.

