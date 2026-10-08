# Current action after the 124829 mapping guard failure

Do not rerun RunLocalOptics yet. The coarse/fine frozen traces completed with
326.6675353833619 / 288.9990727177187 W absorbed (-11.53%), no time advance and
zero material-field changes reported. These grid/input effects are measurable;
the mapped-input trace is absent. The 553-second native mapping ended normally,
but the strict non-optical file guard rejected its result. The old report omitted
the changed paths, so the archive cannot identify the exact offending files.

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/AuditLocalOpticsMapping
```

This reads the retained 124829 cases, checks completed traces and optical hashes,
compares the mapped case to the fine case it was copied from, and collects file
hash differences and byte-identical rename candidates. It also checks the original
audited source hashes. It launches no OpenFOAM utilities, performs no mapping or
CFD, and does not modify the old cases. Hashing time depends on disk speed.
The reconstructed baseline is explicitly labelled, not claimed to be a historical
pre-map fingerprint. Collection completion does not mean the mapping gate passes.
Send `tests/m247Performance/runs/M247_local-optics-mapping-audit-<timestamp>_review.tar.gz`.

Future fresh runs save both mapping fingerprints before testing the guard and
include unexpected paths in the error. No protection rule has been relaxed.

# Frozen local-mesh optical comparison

The110422 projected-flux pilot completes180-180.2us in22steps/133.14seconds,
no thermal caps,16.27mean/18max correctors, bounded alpha/epsilon. Initial
projected divL1=9.84e-10/s; final divL1=0.01164/s. Compatibility passes.
Global Tmax4448K and deposited power~288W nevertheless differ appreciably from
the earlier coarse window (~328W). Those windows are not a matched physical
comparison, so neither numerical failure nor fine-grid physical convergence is
established. Global Tmax includes gas. Do not lengthen CFD yet.

Run from the repository root:

```bash
git pull --ff-only origin feat/m247-material-port
./tests/m247Performance/RunLocalOptics
```

Default input is the retained104821 restart audit, which references the coarse
and localRefine4 cases in101101. No solver or library rebuild is needed. Static
preflight verifies the existing frozen/profiling features. Inputs are hash-checked
against that audit and copied to fresh cases; original cases stay unchanged.
Allow disk space for three serial+48-partition cases and captured optical fields.

All experiments hold the original180us material snapshot and use1536rays,
48Scotch ranks, cached traversal, corrected handoff/termination and seed search
off. Three roles have distinct archive names:

| Role | Mesh | Frozen optical input |
|---|---|---|
| localOpticsCoarse | original756000cells | coarse-grid capture |
| localOpticsFine | four-layer2283911cells | fine-grid capture |
| localOpticsMapped | same four-layer mesh | coarse capture mapped to fine |

Each capture writes only filtered alpha, normal and resistivity inputs. Trace
performs exactly one optical update, checks zero changes in T/U/alpha/epsilon
and no time advance, and reports absorption and reconciled ray/rank profiles.
The mapped variant restricts native mapFieldsPar to those three fields, using
cellVolumeWeight with consistent geometry and matching boundary names. It
checks that no material/mesh files are changed by mapping and verifies identical
fine-grid rank cell ownership between the fine variants. Mapped vectors are
diagnostic volume-field interpolation, not an exact geometric interface mapping
or new production model. Input digests and whether mapping changed bytes are
reported; unchanged mapped inputs are a valid diagnostic observation.

Comparisons report signed power differences, without declaring a physics PASS:
coarse-own versus fine-own measures combined grid/input effects; coarse-own
versus fine-mapped tests residual traversal/sampling and mapping effects;
fine-mapped versus fine-own measures input reconstruction sensitivity on the
same mesh. They do not uniquely identify one cause or establish mesh convergence.
No pressure, thermal, VOF or momentum time loops run. The original mapped phi
is acceptable for this test because frozen mode exits before flux/time loops;
it remains unsuitable for an unprojected CFD restart.

Two captures and three trace launches each have a5-minute launch budget plus
existing stop grace. Native utilities have20-minute timeouts; copy/hashing time
is extra. Same solver/library digests are required across all five launches.
Partial reports/archives are retained on failure. Send the single archive:

```text
tests/m247Performance/runs/M247_local-optics-YYYYMMDD-HHMMSS_review.tar.gz
```

The current0.2us job cost665.7s/us gives a fixed-cost24h scenario of130us,
or about104us for a19.2h compute allocation.
It is not a forecast: startup, physical changes, longer-track region growth and
cooling can change cost. Full1.5-2mm at1m/s would be277-370h under this same
fixed-cost assumption. Region-following mesh and reduced thermal work remain
necessary. Current time split is thermal46.8%, laser23.8%, pressure18.8%.

Native mapping API reference:
[OpenCFD mapFieldsPar](https://api.openfoam.com/2512/mapFieldsPar_8C_source.html).
Ubuntu execution must validate this new orchestration; no C++ changes this step.
