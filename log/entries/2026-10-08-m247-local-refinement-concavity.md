# Local refinement sizing succeeds; mesh-quality gate fails

Reviewed M247_local-refinement-20261008-003900_review.tar.gz: all 13 manifest
sizes/SHA256 match, wrapper exit1, no listed files missing. Absence of the final
report and ten-layer logs is a stopped preview, not successful validation.
Ubuntu built the checker and reconstructed the original serial restart.

Four-layer selection: 18,140 interface seeds, 145,741 after warm-cell union,
218,273 after halo. Native refinement gives exactly 756000+7*218273 = 2,283,911
cells:3.02105x original,37.7631% of a global one-level refinement. This is mesh
sizing evidence, not a measured speedup. Field bounds stay [0,1]; independent
moment comparisons all pass. Total-volume relative change2.74e-11, metal-volume
relative change1.13e-11, liquid proxy8.65e-13, metal-temperature moment2.78e-12.
None establishes flux/enthalpy or isoAdvector reconstruction conservation.

checkMesh-allGeometry/-allTopology finds one failure:15,101 concave cells,
0.661% of cells. Positive volume, determinant, face-tet, flatness and other
reported checks pass. Max nonorthogonality48.6596deg, skewness0.360988,
aspect3.26005, min edge4um. These passing quantities do not waive concavity.
The gate correctly stops; its orchestration incorrectly loses the report and
prevents independent evaluation of ten layers.

Fixed orchestration to save partial/final schema2 reports and continue after
completed quality failures. Added --resume to hash/copy only the prior verified
serial coarse restart, check identical coarse moments, and skip expensive
parallel copy/reconstruction. Both variants are fresh, not overwritten.
Added native concaveCells diagnostic for bounds and outward vertex-to-face
plane distances, normalized by cell-volume length; descriptive counts do not
relax quality. Distinct root logs and resume hashes automatically packaged.

Local validation:92 Python tests, including real-format native concavity
rejection, second-variant continuation, report persistence, diagnostic count
mismatch, and serial-only resume copying. Bash syntax passes; native added
cellSet/plane diagnostic compile and execution remain Ubuntu validation.
No CFD or production promotion. Next recover the sizing/geometry evidence,
then choose mesh correction using measured severity rather than changing
quality tolerances speculatively.

Native API reviewed:
[refineHexMesh](https://api.openfoam.com/2512/refineHexMesh_8C_source.html),
[cellSet](https://api.openfoam.com/2406/classFoam_1_1cellSet.html).
