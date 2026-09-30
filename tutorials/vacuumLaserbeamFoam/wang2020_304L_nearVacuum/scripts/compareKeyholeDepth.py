#!/usr/bin/env python3
"""Compare centreline and connected-surface keyhole-depth metrics."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


def read_depth(path: Path):
    rows = []
    with path.open(newline="") as f:
        for row in csv.DictReader(f):
            try:
                t = float(row["time_s"])
                d = float(row["keyhole_depth_um"])
            except (KeyError, ValueError):
                continue
            if math.isfinite(t) and math.isfinite(d):
                rows.append((t, d))
    return sorted(rows)


def crossing_time(rows, target_um):
    for (t0, d0), (t1, d1) in zip(rows[:-1], rows[1:]):
        if d0 < target_um <= d1:
            if d1 == d0:
                return t1
            f = (target_um - d0) / (d1 - d0)
            return t0 + f * (t1 - t0)
    return None


def report(label, rows):
    t32 = crossing_time(rows, 32.0)
    t136 = crossing_time(rows, 136.0)

    print(label)
    print(f"  latest depth: {rows[-1][1]:.6g} um at {rows[-1][0]*1e6:.6g} us")

    if t32 is None:
        print("  t32: not reached")
    else:
        print(f"  t32: {t32*1e6:.6g} us")

    if t136 is None:
        print("  t136: not reached")
    else:
        print(f"  t136: {t136*1e6:.6g} us")

    if t32 is not None and t136 is not None:
        dt = (t136 - t32) * 1e6
        print(f"  32->136 um growth time: {dt:.6g} us")

    return t32, t136


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--centerline", type=Path, required=True)
    ap.add_argument("--surface", type=Path, required=True)
    args = ap.parse_args()

    center = read_depth(args.centerline)
    surface = read_depth(args.surface)

    if not center or not surface:
        raise SystemExit("Missing finite depth rows in comparison CSVs")

    c32, c136 = report("Centerline metric:", center)
    s32, s136 = report("3-D connected-surface metric:", surface)

    common = {}
    for t, d in center:
        common.setdefault(t, [None, None])[0] = d
    for t, d in surface:
        common.setdefault(t, [None, None])[1] = d

    diffs = [
        sd - cd
        for cd, sd in common.values()
        if cd is not None and sd is not None
    ]

    if diffs:
        print(
            "Surface minus centerline depth: "
            f"median={sorted(diffs)[len(diffs)//2]:.6g} um, "
            f"max={max(diffs):.6g} um"
        )

    if None not in (c32, c136, s32, s136):
        center_dt = (c136 - c32) * 1e6
        surface_dt = (s136 - s32) * 1e6
        print(
            "Growth-time metric difference "
            f"(surface-centerline): {surface_dt-center_dt:.6g} us"
        )


if __name__ == "__main__":
    main()
