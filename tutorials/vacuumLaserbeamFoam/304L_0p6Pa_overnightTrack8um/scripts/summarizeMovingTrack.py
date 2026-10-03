#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path


def read_depth(path):
    with path.open(newline="") as f:
        rows=[]
        for r in csv.DictReader(f):
            rows.append(
                {
                    "time": float(r["time_s"]),
                    "depth": float(r["keyhole_depth_um"]),
                    "dx": float(r["bottom_dx_from_laser_um"]),
                    "support": int(r["bottom_support_vertices"]),
                    "components": int(r["interface_components"]),
                }
            )
    return rows


def read_diag(path):
    pat=re.compile(r"(\w+)=([+\-0-9.eE]+)")
    rows=[]
    for line in path.read_text(errors="ignore").splitlines():
        if line.startswith("VACUUM_DIAGNOSTICS "):
            d={k:float(v) for k,v in pat.findall(line)}
            if "time" in d:
                rows.append(d)
    return rows


def stats(vals):
    n=len(vals)
    mean=sum(vals)/n
    rms=math.sqrt(sum((v-mean)**2 for v in vals)/n)
    return mean,rms,min(vals),max(vals)


def first_at_least(rows, threshold):
    for r in rows:
        if r["depth"] >= threshold:
            return r
    return None


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--depth", type=Path, default=Path("movingKeyholeDepth.csv"))
    ap.add_argument("--log", type=Path, default=Path("log.vacuumLaserbeamFoam"))
    args=ap.parse_args()

    depth=read_depth(args.depth)
    diag=read_diag(args.log)

    print("MOVING_TRACK_SUMMARY")
    for threshold in (10,20,30,40):
        r=first_at_least(depth, threshold)
        if r:
            print(
                f"depth{threshold}_time_us={r['time']*1e6:.6g} "
                f"depth{threshold}_um={r['depth']:.6g}"
            )

    peak=max(depth,key=lambda r:r["depth"])
    print(
        f"peak_depth_um={peak['depth']:.6g} "
        f"peak_depth_time_us={peak['time']*1e6:.6g}"
    )

    for label,lo,hi in (
        ("plateau",75e-6,210e-6),
        ("late",220e-6,300e-6),
    ):
        part=[r for r in depth if lo <= r["time"] <= hi]
        vals=[r["depth"] for r in part]
        dx=[r["dx"] for r in part]
        mean,rms,vmin,vmax=stats(vals)
        dxmean,dxrms,dxmin,dxmax=stats(dx)
        boundary_hits=sum(1 for x in dx if x <= -92)
        print(
            f"{label}_depth_mean_um={mean:.6g} "
            f"{label}_depth_rms_um={rms:.6g} "
            f"{label}_depth_min_um={vmin:.6g} "
            f"{label}_depth_max_um={vmax:.6g}"
        )
        print(
            f"{label}_dx_mean_um={dxmean:.6g} "
            f"{label}_dx_rms_um={dxrms:.6g} "
            f"{label}_dx_min_um={dxmin:.6g} "
            f"{label}_trailing_boundary_hits={boundary_hits}/{len(dx)}"
        )

    if diag:
        for label,lo,hi in (
            ("plateau",75e-6,210e-6),
            ("late",220e-6,300e-6),
        ):
            part=[r for r in diag if lo <= r["time"] <= hi]
            print(f"{label}_diagnostics_samples={len(part)}")
            for key in (
                "depositedPower","evaporationPower","radiationPower",
                "Tmax","Umax","interfacePVapMax","interfaceArea","recoilForceY"
            ):
                vals=[r[key] for r in part if key in r]
                mean,rms,vmin,vmax=stats(vals)
                print(
                    f"{label}_{key}_mean={mean:.10g} "
                    f"{label}_{key}_rms={rms:.10g} "
                    f"{label}_{key}_min={vmin:.10g} "
                    f"{label}_{key}_max={vmax:.10g}"
                )


if __name__=="__main__":
    main()
