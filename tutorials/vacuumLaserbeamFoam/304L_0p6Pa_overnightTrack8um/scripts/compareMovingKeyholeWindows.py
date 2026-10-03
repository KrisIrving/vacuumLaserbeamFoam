#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def read(path):
    with path.open(newline="") as f:
        return {float(r["time_s"]): r for r in csv.DictReader(f)}


def f(row, name):
    return float(row[name])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--labels", nargs="+", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    if len(args.inputs) != len(args.labels):
        raise SystemExit("inputs/labels length mismatch")

    tables = [read(Path(p)) for p in args.inputs]
    times = sorted(set.intersection(*(set(t) for t in tables)))

    if not times:
        raise SystemExit("No common times across sensitivity CSVs")

    with args.output.open("w", newline="") as fobj:
        w = csv.writer(fobj)
        header = ["time_s", "laser_x_um"]
        for label in args.labels:
            header += [f"depth_{label}_um", f"dx_{label}_um"]
        header += ["depth_spread_um"]
        w.writerow(header)

        for t in times:
            depths = [f(tab[t], "keyhole_depth_um") for tab in tables]
            dxs = [f(tab[t], "bottom_dx_from_laser_um") for tab in tables]
            row = [f"{t:.12g}", tables[0][t]["laser_x_um"]]
            for d, dx in zip(depths, dxs):
                row += [f"{d:.8g}", f"{dx:.8g}"]
            row += [f"{max(depths)-min(depths):.8g}"]
            w.writerow(row)

    print("Moving-keyhole trailing-window sensitivity")
    for i, label in enumerate(args.labels):
        vals = [f(tables[i][t], "keyhole_depth_um") for t in times if t >= 75e-6]
        dx = [f(tables[i][t], "bottom_dx_from_laser_um") for t in times if t >= 75e-6]
        print(
            f"  {label}: meanDepth={sum(vals)/len(vals):.6g} um "
            f"maxDepth={max(vals):.6g} um "
            f"minDx={min(dx):.6g} um"
        )

    ref_i = args.labels.index("160um") if "160um" in args.labels else len(args.labels)-1
    ref = tables[ref_i]

    for i, label in enumerate(args.labels):
        if i == ref_i:
            continue
        diffs = [
            abs(f(tables[i][t], "keyhole_depth_um") - f(ref[t], "keyhole_depth_um"))
            for t in times if t >= 75e-6
        ]
        print(
            f"  vs 160um: {label} maxAbsDepthDiff={max(diffs):.6g} um "
            f"meanAbsDepthDiff={sum(diffs)/len(diffs):.6g} um"
        )

    spreads = []
    for t in times:
        if t < 75e-6:
            continue
        depths = [f(tab[t], "keyhole_depth_um") for tab in tables]
        spreads.append((max(depths)-min(depths), t))
    worst = max(spreads)
    print(
        f"  worst post-75us window spread={worst[0]:.6g} um "
        f"at {worst[1]*1e6:.6g} us"
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
