#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path


def time_from_path(path: Path) -> float:
    for parent in path.parents:
        try:
            return float(parent.name)
        except ValueError:
            pass
    raise RuntimeError(f"Could not infer time from {path}")


def read_vertices(path: Path):
    vertices = []
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if line.startswith("v "):
            parts = line.split()
            if len(parts) >= 4:
                vertices.append(tuple(map(float, parts[1:4])))
    return vertices


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-processing", type=Path, required=True)
    ap.add_argument("--xmin", type=float, required=True)
    ap.add_argument("--xmax", type=float, required=True)
    ap.add_argument("--ymin", type=float, required=True)
    ap.add_argument("--ymax", type=float, required=True)
    ap.add_argument("--zmin", type=float, required=True)
    ap.add_argument("--zmax", type=float, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    objects = [
        p for p in args.post_processing.rglob("*.obj")
        if "liquidus" in p.name.lower()
    ]
    if not objects:
        raise SystemExit("No liquidus-isotherm OBJ files found")

    rows = []
    for path in objects:
        vertices = read_vertices(path)
        if not vertices:
            continue

        t = time_from_path(path)
        xs = [p[0] for p in vertices]
        ys = [p[1] for p in vertices]
        zs = [p[2] for p in vertices]

        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        zmin, zmax = min(zs), max(zs)

        rows.append(
            (
                t,
                xmin, xmax, ymin, ymax, zmin, zmax,
                xmin-args.xmin,
                args.xmax-xmax,
                ymin-args.ymin,
                args.ymax-ymax,
                zmin-args.zmin,
                args.zmax-zmax,
                len(vertices),
                path,
            )
        )

    if not rows:
        raise SystemExit("Liquidus OBJ files contained no vertices")

    rows.sort(key=lambda r: r[0])

    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "time_s",
                "xmin_um","xmax_um","ymin_um","ymax_um","zmin_um","zmax_um",
                "xminus_clearance_um","xplus_clearance_um",
                "bottom_clearance_um","top_clearance_um",
                "zminus_clearance_um","zplus_clearance_um",
                "vertices","source",
            ]
        )
        for r in rows:
            w.writerow(
                [
                    f"{r[0]:.12g}",
                    *[f"{1e6*v:.8g}" for v in r[1:13]],
                    r[13],
                    r[14],
                ]
            )

    latest = rows[-1]
    min_transverse = min(latest[11], latest[12])
    min_x = min(latest[7], latest[8])
    print(f"Latest time: {latest[0]*1e6:.6g} us")
    print(
        "Liquidus-temperature extent: "
        f"x=[{latest[1]*1e6:.3f},{latest[2]*1e6:.3f}] um "
        f"y=[{latest[3]*1e6:.3f},{latest[4]*1e6:.3f}] um "
        f"z=[{latest[5]*1e6:.3f},{latest[6]*1e6:.3f}] um"
    )
    print(
        "Boundary clearances: "
        f"x_min={latest[7]*1e6:.3f} um "
        f"x_max={latest[8]*1e6:.3f} um "
        f"bottom={latest[9]*1e6:.3f} um "
        f"top={latest[10]*1e6:.3f} um "
        f"z_min={latest[11]*1e6:.3f} um "
        f"z_max={latest[12]*1e6:.3f} um"
    )
    print(
        f"Minimum latest transverse clearance: {min_transverse*1e6:.3f} um"
    )
    print(f"Minimum latest scan-direction clearance: {min_x*1e6:.3f} um")


if __name__ == "__main__":
    main()
