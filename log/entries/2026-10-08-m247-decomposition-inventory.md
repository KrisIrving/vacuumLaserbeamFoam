
## 2026-10-08 191618: incomplete decomposition confirmed; live resource inventory

Archive hashes/bytes verified,manifestexit1 correctly denotes incomplete pair.
Native build succeeded. Reference decompose log stops during Processor18field
transfer, no End; no solver/run.json/candidate. Initial commands[] does not mean
no launch: old launcher recorded commands only AFTER success. Cause is unknown:
no native fatal/OOM/disk/error exit evidence in saved logs. User supplied successful
collection output only, not original interrupted-run output. Do not diagnose solver
instability or restart originalcase based on this archive.

Collector now writes movingLongInventory.json before copying: disk/inode free
space, Linux MemAvailable/SwapFree, matching processnames/PIDs/states (own collector
flagged),48rank initialfield progress and solver/run metadata existence. No kill,
cleanup, build,decompose or CFD launch. Point-in-time resources cannot prove a
historical cause. Run same fast read-only collector after pull, send fresh
M247_moving-long-collection-<timestamp>_review.tar.gz. Source stays untouched.

Future native launches persist running stage BEFORE subprocess starts, then
completed/failed-or-interrupted,elapsed wall,error type/returncode. SIGKILL cannot
be trapped; a running record is therefore not proof process is still alive.
137Python tests pass (resource inventory/partial18field preservation), previous
Bash wrapper unchanged. Live Ubuntu inventory pending; no solver physics change.
