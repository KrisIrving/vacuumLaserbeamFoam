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
    if not vertices:
        raise RuntimeError(f"No vertices found in {path}")
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


def main_component(vertices, components, surface_y, band):
    candidates = []
    for comp in components:
        near = sum(
            1 for i in comp
            if abs(vertices[i][1] - surface_y) <= band
        )
        if near:
            candidates.append((near, len(comp), comp))
    if candidates:
        return max(candidates, key=lambda x: (x[0], x[1]))[2], True
    return max(components, key=len), False


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-processing", type=Path, required=True)
    ap.add_argument("--laser-path", type=Path, required=True)
    ap.add_argument("--surface-y", type=float, required=True)
    ap.add_argument("--surface-band", type=float, default=8e-6)
    ap.add_argument("--trailing-window", type=float, default=100e-6)
    ap.add_argument("--forward-window", type=float, default=60e-6)
    ap.add_argument("--half-width-z", type=float, default=75e-6)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    path_rows = read_path_table(args.laser_path)
    objects = [
        p for p in args.post_processing.rglob("*.obj")
        if "metalgasinterface" in p.name.lower()
    ]
    if not objects:
        raise SystemExit("No metalGasInterface OBJ files found")

    by_time = {}
    for path in objects:
        t = time_from_path(path)
        vertices, faces = read_obj(path)
        comps = connected_components(vertices, faces)
        comp, connected = main_component(
            vertices, comps, args.surface_y, args.surface_band
        )

        lx, ly, lz = laser_position(path_rows, t)
        local = [
            idx for idx in comp
            if vertices[idx][1] <= args.surface_y + 1e-12
            and -args.trailing_window <= vertices[idx][0] - lx <= args.forward_window
            and abs(vertices[idx][2] - lz) <= args.half_width_z
        ]

        if local:
            bottom = min(local, key=lambda i: vertices[i][1])
            x, y, z = vertices[bottom]
            depth = max(args.surface_y-y, 0.0)
            support = sum(
                1 for idx in local
                if vertices[idx][1] <= y + 8e-6
                and math.hypot(vertices[idx][0]-x, vertices[idx][2]-z) <= 16e-6
            )
        else:
            x, y, z = lx, args.surface_y, lz
            depth = 0.0
            support = 0

        row = (
            t, lx, lz, depth, x, z, x-lx, z-lz, support,
            len(local), len(comp), len(comps), connected, path
        )
        old = by_time.get(t)
        if old is None or depth > old[3]:
            by_time[t] = row

    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "time_s","laser_x_um","laser_z_um","keyhole_depth_um",
            "bottom_x_um","bottom_z_um","bottom_dx_from_laser_um",
            "bottom_dz_from_laser_um","bottom_support_vertices",
            "local_interface_vertices","main_component_vertices",
            "interface_components","surface_connected","source"
        ])
        for t in sorted(by_time):
            r = by_time[t]
            w.writerow([
                f"{r[0]:.12g}", f"{r[1]*1e6:.8g}", f"{r[2]*1e6:.8g}",
                f"{r[3]*1e6:.8g}", f"{r[4]*1e6:.8g}", f"{r[5]*1e6:.8g}",
                f"{r[6]*1e6:.8g}", f"{r[7]*1e6:.8g}", r[8], r[9],
                r[10], r[11], "yes" if r[12] else "fallback", r[13]
            ])

    latest = by_time[max(by_time)]
    print(f"Latest time: {latest[0]*1e6:.6g} us")
    print(f"Laser-following keyhole depth: {latest[3]*1e6:.6g} um")
    print(
        "Bottom offset from laser: "
        f"dx={latest[6]*1e6:.6g} um, dz={latest[7]*1e6:.6g} um"
    )
    print(f"Bottom support vertices: {latest[8]}")
    print(f"Interface components: {latest[11]}")


if __name__ == "__main__":
    main()
