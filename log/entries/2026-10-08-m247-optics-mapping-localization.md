Reviewed local-optics-124829: all43 archive hashes/sizes valid; wrapper1,
only mapped trace solver/run missing because guard stopped before launch.
Independently parsed both completed frozen logs: coarse326.667535W,
fine288.999073W (-11.53%), one1536-ray update, no time/material evolution.
Native mapFieldsPar ended normally after553s. Actual offending file changes were
not included by old wrapper; do not infer exact cause or bypass strict gate.
Added read-only AuditLocalOpticsMapping comparing retained mapped/fine file hashes,
reporting rename candidates and original-source hash gates. Future mapping failures
preserve before/after fingerprints and explicit changed paths. No CFD/rebuild/re-map.
Next: pull and ./tests/m247Performance/AuditLocalOpticsMapping; send its one archive.
Python tests and Bash syntax verified locally; native data localization pendingUbuntu.
