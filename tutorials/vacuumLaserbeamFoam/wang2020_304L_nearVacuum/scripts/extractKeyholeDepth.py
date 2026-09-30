#!/usr/bin/env python3
"""Extract atmosphere-connected centerline keyhole depth from OpenFOAM samples."""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path

FLOAT = re.compile(
    r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?"
)


def read_profile(path: Path):
    points = []
    for line in path.read_text(errors="ignore").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        vals = [float(v) for v in FLOAT.findall(stripped)]
        if len(vals) >= 4:
            y, alpha = vals[1], vals[-1]
        elif len(vals) >= 2:
            y, alpha = vals[0], vals[-1]
        else:
            continue
        if math.isfinite(y) and math.isfinite(alpha):
            points.append((y, alpha))

    if len(points) < 2:
        raise RuntimeError(f"Not enough samples in {path}")

    return sorted(points, key=lambda p: p[0], reverse=True)


def analyse_profile(points, surface_y: float):
    # Ignore all geometry above the original substrate surface. Overflowing
    # metal/spatter above y=surface_y must not create an artificial long
    # interpolation segment to the keyhole bottom.
    below = [(y, a) for y, a in points if y <= surface_y + 1e-12]
    if len(below) < 2:
        return None, 0, 0

    gas_to_metal = 0
    metal_to_gas = 0

    for (py, pa), (y, alpha) in zip(below[:-1], below[1:]):
        if pa < 0.5 <= alpha:
            gas_to_metal += 1
        elif pa >= 0.5 > alpha:
            metal_to_gas += 1

    # If the first point immediately below the nominal surface is metal, the
    # atmosphere-connected depression has zero depth along this centreline.
    if below[0][1] >= 0.5:
        return surface_y, gas_to_metal, metal_to_gas

    # Starting in gas, the first gas->metal crossing is the bottom of the
    # atmosphere-connected centreline cavity. Any later crossings correspond
    # to disconnected gas pockets along this one-dimensional line.
    for (py, pa), (y, alpha) in zip(below[:-1], below[1:]):
        if pa < 0.5 <= alpha:
            if abs(alpha - pa) < 1e-14:
                return y, gas_to_metal, metal_to_gas
            frac = (0.5 - pa) / (alpha - pa)
            return py + frac * (y - py), gas_to_metal, metal_to_gas

    return None, gas_to_metal, metal_to_gas


def time_from_path(path: Path):
    for parent in path.parents:
        try:
            return float(parent.name)
        except ValueError:
            pass
    raise RuntimeError(f"Could not infer time from {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-processing", type=Path, required=True)
    ap.add_argument("--surface-y", type=float, required=True)
    ap.add_argument("--output", type=Path, default=Path("keyholeDepth.csv"))
    args = ap.parse_args()

    candidates = []
    for path in args.post_processing.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if "keyholecenterline" in name and "alpha" in name:
            candidates.append(path)

    if not candidates:
        raise SystemExit(
            "No keyholeCenterline alpha.metal sample files found under "
            f"{args.post_processing}"
        )

    rows = []
    for path in candidates:
        t = time_from_path(path)
        pts = read_profile(path)
        iy, gas_to_metal, metal_to_gas = analyse_profile(pts, args.surface_y)
        if iy is None:
            depth = float("nan")
        else:
            depth = max(args.surface_y - iy, 0.0)
        rows.append((t, depth, gas_to_metal, metal_to_gas, path))

    by_time = {}
    for row in rows:
        t, depth, *_ = row
        old = by_time.get(t)
        if old is None or (
            math.isfinite(depth)
            and (not math.isfinite(old[1]) or depth > old[1])
        ):
            by_time[t] = row

    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "time_s",
                "keyhole_depth_m",
                "keyhole_depth_um",
                "gas_to_metal_crossings",
                "metal_to_gas_crossings",
                "source",
            ]
        )
        for t in sorted(by_time):
            _, depth, g2m, m2g, path = by_time[t]
            depth_um = depth * 1e6 if math.isfinite(depth) else float("nan")
            w.writerow(
                [
                    f"{t:.12g}",
                    f"{depth:.12g}",
                    f"{depth_um:.8g}",
                    g2m,
                    m2g,
                    path,
                ]
            )

    finite = [(t, row[1]) for t, row in by_time.items() if math.isfinite(row[1])]
    if finite:
        t, d = max(finite, key=lambda x: x[0])
        print(f"Latest sampled time: {t:.12g} s")
        print(f"Centerline keyhole depth: {d*1e6:.6g} um")

    complex_times = [
        t
        for t, row in by_time.items()
        if row[2] > 1 or row[3] > 0
    ]
    if complex_times:
        print(
            "WARNING: multiple below-surface alpha=0.5 crossings occur at "
            f"{len(complex_times)} sampled times; use the 3-D surface metric "
            "for the formal keyhole depth."
        )


if __name__ == "__main__":
    main()
