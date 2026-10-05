#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import math
import re
from collections import defaultdict
from pathlib import Path


def time_from_path(path: Path):
    for parent in path.parents:
        try:
            return float(parent.name)
        except ValueError:
            pass
    raise RuntimeError(f"Could not infer time from {path}")


def read_obj(path: Path):
    vertices = []
    faces = []
    for raw in path.read_text(errors="ignore").splitlines():
        line = raw.strip()
        if line.startswith("v "):
            p = line.split()
            if len(p) >= 4:
                vertices.append(tuple(map(float, p[1:4])))
        elif line.startswith("f "):
            ids = []
            for token in line.split()[1:]:
                head = token.split("/")[0]
                if not head:
                    continue
                idx = int(head)
                ids.append(len(vertices) + idx if idx < 0 else idx - 1)
            if len(ids) >= 3:
                faces.append(ids)
    return vertices, faces


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1]*n

    def find(self, a):
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def union(self, a, b):
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]


def connected_components(vertices, faces):
    if not vertices:
        return []
    uf = UnionFind(len(vertices))
    used = set()
    for face in faces:
        used.update(face)
        for idx in face[1:]:
            uf.union(face[0], idx)
    if not faces:
        used.update(range(len(vertices)))
    comps = defaultdict(list)
    for idx in used:
        comps[uf.find(idx)].append(idx)
    return list(comps.values())


def read_path_table(path: Path):
    pattern = re.compile(
        r"\(\s*([+\-0-9.eE]+)\s+"
        r"\(\s*([+\-0-9.eE]+)\s+([+\-0-9.eE]+)\s+([+\-0-9.eE]+)\s*\)\s*\)"
    )
    rows = []
    for line in path.read_text().splitlines():
        m = pattern.search(line)
        if m:
            rows.append(tuple(float(x) for x in m.groups()))
    if len(rows) < 2:
        raise RuntimeError(f"Could not parse laser path from {path}")
    rows.sort()
    return rows


def laser_position(rows, t):
    if t <= rows[0][0]:
        return rows[0][1:]
    if t >= rows[-1][0]:
        return rows[-1][1:]
    for a, b in zip(rows[:-1], rows[1:]):
        if a[0] <= t <= b[0]:
            w = (t-a[0])/(b[0]-a[0])
            return tuple(a[j] + w*(b[j]-a[j]) for j in range(1,4))
    return rows[-1][1:]


def choose_primary_component(vertices, components, laser_x, laser_z):
    # Select the component that comes closest to the current laser axis in the
    # scan plane. This rejects remote molten powder islands more robustly than
    # simply taking the largest disconnected isosurface.
    scored = []
    for comp in components:
        d2 = min(
            (vertices[i][0]-laser_x)**2 + (vertices[i][2]-laser_z)**2
            for i in comp
        )
        scored.append((d2, -len(comp), comp))
    return min(scored, key=lambda item: (item[0], item[1]))[2]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-processing", type=Path, required=True)
    ap.add_argument("--laser-path", type=Path, required=True)
    ap.add_argument("--z-min", type=float, required=True)
    ap.add_argument("--z-max", type=float, required=True)
    ap.add_argument("--surface-y", type=float, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    path_rows = read_path_table(args.laser_path)
    objects = [
        p for p in args.post_processing.rglob("*.obj")
        if "liquidus" in p.name.lower()
    ]
    if not objects:
        raise SystemExit("No liquidus isosurface OBJ files found")

    by_time = {}
    for path in objects:
        t = time_from_path(path)
        vertices, faces = read_obj(path)
        if not vertices:
            continue
        components = connected_components(vertices, faces)
        if not components:
            continue

        lx, ly, lz = laser_position(path_rows, t)
        comp = choose_primary_component(vertices, components, lx, lz)
        pts = [vertices[i] for i in comp]

        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]

        row = {
            "time_s": t,
            "laser_x_um": lx*1e6,
            "z_min_um": min(zs)*1e6,
            "z_max_um": max(zs)*1e6,
            "transverse_span_um": (max(zs)-min(zs))*1e6,
            "clearance_zmin_um": (min(zs)-args.z_min)*1e6,
            "clearance_zmax_um": (args.z_max-max(zs))*1e6,
            "x_min_um": min(xs)*1e6,
            "x_max_um": max(xs)*1e6,
            "y_min_um": min(ys)*1e6,
            "y_max_um": max(ys)*1e6,
            "melt_depth_below_surface_um": max((args.surface_y-min(ys))*1e6, 0.0),
            "melt_height_above_surface_um": max((max(ys)-args.surface_y)*1e6, 0.0),
            "primary_vertices": len(comp),
            "components": len(components),
            "source": str(path),
        }
        old = by_time.get(t)
        if old is None or row["primary_vertices"] > old["primary_vertices"]:
            by_time[t] = row

    fields = [
        "time_s","laser_x_um","z_min_um","z_max_um","transverse_span_um",
        "clearance_zmin_um","clearance_zmax_um","x_min_um","x_max_um",
        "y_min_um","y_max_um","melt_depth_below_surface_um",
        "melt_height_above_surface_um","primary_vertices","components","source"
    ]
    with args.output.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for t in sorted(by_time):
            w.writerow(by_time[t])

    if not by_time:
        raise SystemExit("No usable liquidus isosurface components found")

    latest = by_time[max(by_time)]
    min_left = min(r["clearance_zmin_um"] for r in by_time.values())
    min_right = min(r["clearance_zmax_um"] for r in by_time.values())
    max_span = max(r["transverse_span_um"] for r in by_time.values())

    print("M247_MELT_POOL_ENVELOPE")
    print(
        f"latest_time_us={latest['time_s']*1e6:.6g} "
        f"latest_span_um={latest['transverse_span_um']:.6g} "
        f"latest_clearance_left_um={latest['clearance_zmin_um']:.6g} "
        f"latest_clearance_right_um={latest['clearance_zmax_um']:.6g}"
    )
    print(
        f"history_max_span_um={max_span:.6g} "
        f"history_min_left_clearance_um={min_left:.6g} "
        f"history_min_right_clearance_um={min_right:.6g}"
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
