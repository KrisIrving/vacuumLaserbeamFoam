# NEXT ACTION — M247 fast-track checkpoint

Updated: 2026-10-07

## Active branch

    feat/m247-material-port

## Physics gates already passed

- Wang near-vacuum model frozen.
- M247 Mondal/Wang constitutive gate passed.
- 100-us M247 bare-plate transfer passed.
- Fixed-PSD M247 powder generator passed.
- 100-us powder preflight passed.
- 200-us / 756k-cell M247 powder track completed on 48 ranks.

## 200-us result

- wall time: 29.18 h;
- keyhole depth at 200 us: about 316.5 um;
- depth-growth rate is decreasing but not yet a strict plateau;
- final liquidus-envelope clearances are adequate in x/y/z for this case;
- straightforward full-domain 1.5-2 mm CFD is computationally unacceptable.

## Current engineering constraint

Any M247 4-um validation job should finish within 24 h.

Do not run a full-domain 4-um case.

The planned 4-um validation is:
- restart from an evolved 8-um state;
- refine only a compact keyhole/melt-pool ROI to 4 um;
- run approximately 20-30 us;
- compare against the corresponding 8-um history.

## Immediate next gate — performance profile

The solver has optional PERF_DIAGNOSTICS instrumentation. It preserves the
original operation order and is disabled unless requested by vacuumProperties.

Benchmark case:

    tutorials/vacuumLaserbeamFoam/M247_0p6Pa_perfProbe8um

It uses the same 756k-cell geometry and physics as the 200-us case, but runs
only 10 us.

Local sequence after pulling the current branch:

    ./Allwmake -j 48
    cd tutorials/vacuumLaserbeamFoam/M247_0p6Pa_perfProbe8um
    ./Preflight
    ./Allrun
    grep '^PERF_DIAGNOSTICS ' log.vacuumLaserbeamFoam

Do not change solver tolerances, Courant limits, ray counts or physics until
the timing split is measured.

## Production strategy under evaluation

Preferred architecture for the final 1.5-2 mm track:

1. moving/local high-fidelity VOF + momentum + recoil + ray-tracing region
   around the laser/keyhole;
2. outer/coarse region solves thermal conduction/phase thermal history only;
3. transfer temperature/enthalpy between the local CFD zone and global thermal
   domain;
4. use the thermal domain for the trailing solidification/cooling history.

This is consistent with published local moving thermal-fluid and local
multi-mesh approaches and will be validated against the existing full-CFD
100-200-us results before production use.
