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
            # axis xyz -> x y z alpha
            y, alpha = vals[1], vals[-1]
        elif len(vals) >= 2:
            # Fallback if the OpenFOAM writer collapses the coordinate.
            y, alpha = vals[0], vals[-1]
        else:
            continue
        if math.isfinite(y) and math.isfinite(alpha):
            points.append((y, alpha))

    if len(points) < 2:
        raise RuntimeError(f"Not enough samples in {path}")

    return sorted(points, key=lambda p: p[0], reverse=True)


def interface_y(points, surface_y: float):
    # Follow the atmosphere-connected gas column from high y downward.
    prev = None
    for y, alpha in points:
        if y > surface_y and alpha >= 0.5:
            # A bad initial profile: metal exists above the nominal surface.
            continue

        if prev is None:
            prev = (y, alpha)
            continue

        py, pa = prev
        if pa < 0.5 <= alpha:
            if abs(alpha - pa) < 1e-14:
                return y
            frac = (0.5 - pa) / (alpha - pa)
            return py + frac * (y - py)

        prev = (y, alpha)

    return None


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
        iy = interface_y(pts, args.surface_y)
        if iy is None:
            depth = float("nan")
        else:
            depth = max(args.surface_y - iy, 0.0)
        rows.append((t, depth, path))

    # If multiple files exist at a time, keep the deepest valid result.
    by_time = {}
    for t, depth, path in rows:
        old = by_time.get(t)
        if old is None or (
            math.isfinite(depth)
            and (not math.isfinite(old[0]) or depth > old[0])
        ):
            by_time[t] = (depth, path)

    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time_s", "keyhole_depth_m", "keyhole_depth_um", "source"])
        for t in sorted(by_time):
            depth, path = by_time[t]
            depth_um = depth * 1e6 if math.isfinite(depth) else float("nan")
            w.writerow([f"{t:.12g}", f"{depth:.12g}", f"{depth_um:.8g}", path])

    finite = [(t, d) for t, (d, _) in by_time.items() if math.isfinite(d)]
    if finite:
        t, d = max(finite, key=lambda x: x[0])
        print(f"Latest sampled time: {t:.12g} s")
        print(f"Centerline keyhole depth: {d*1e6:.6g} um")


if __name__ == "__main__":
    main()
