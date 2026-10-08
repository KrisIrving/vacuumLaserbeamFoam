Reviewed mapping-audit144301:6 archive files pass SHA256/size checks; exit0,
no missing. Independently recomputed before/after differences: only three optical
inputs modified, plus phi and alphaPhi0.metal renamed to .unmapped with exactly
identical hashes. Original source gates true. This explains strict path guard
failure without evidence of material or mesh modification. Baseline remains
reconstructed from the retained fine case, not a historical pre-map digest.
Added narrowly validated byte-identical flux-name restoration in disposable
optical cases; unrelated changes/bad bytes/collisions still fail before any rename.
Added ResumeLocalOptics: verify144301 evidence/retained hashes, reuse two traces
and already mapped data, copy mapped serial case, restore names, decompose48,
verify identical fine rank ownership, run only one5-minute-budget frozen trace,
check same five-job binary provenance and unchanged material/source fields.
Restored flux is for frozen startup only; no CFD restart approval or projection.
Next pull and ./tests/m247Performance/ResumeLocalOptics; send one automatic
M247_local-optics-resume-..._review.tar.gz. No rebuild or mapping rerun.
Validation:107 Python tests, Bash syntax and py_compile pass; actual archived
before/after differences independently reconciled and normalized strict gate passes.
Native resumed decomposition/trace pending Ubuntu.
