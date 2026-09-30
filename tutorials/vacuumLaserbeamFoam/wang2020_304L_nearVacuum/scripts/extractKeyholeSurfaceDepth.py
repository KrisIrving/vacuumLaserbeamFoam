#!/usr/bin/env python3
"""Measure the deepest atmosphere-connected alpha=0.5 interface component."""

from __future__ import annotations

import argparse
import csv
import math
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
            parts = line.split()
            if len(parts) >= 4:
                vertices.append(tuple(map(float, parts[1:4])))
        elif line.startswith("f "):
            ids = []
            for token in line.split()[1:]:
                head = token.split("/")[0]
                if not head:
                    continue
                idx = int(head)
                if idx < 0:
                    idx = len(vertices) + idx
                else:
                    idx -= 1
                ids.append(idx)
            if len(ids) >= 3:
                faces.append(ids)

    if not vertices:
        raise RuntimeError(f"No vertices found in {path}")

    return vertices, faces


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n

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
        root = face[0]
        for idx in face[1:]:
            uf.union(root, idx)

    if not faces:
        used.update(range(len(vertices)))

    comps = defaultdict(list)
    for idx in used:
        comps[uf.find(idx)].append(idx)

    return list(comps.values())


def main_component(vertices, components, surface_y, surface_band):
    candidates = []

    for comp in components:
        near_surface = sum(
            1 for idx in comp
            if abs(vertices[idx][1] - surface_y) <= surface_band
        )
        if near_surface:
            candidates.append((near_surface, len(comp), comp))

    if candidates:
        # The atmosphere-connected free surface has by far the broadest
        # population of vertices near the original substrate surface.
        return max(candidates, key=lambda x: (x[0], x[1]))[2], True

    # Fallback is deliberately flagged in the CSV.
    return max(components, key=len), False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-processing", type=Path, required=True)
    ap.add_argument("--surface-y", type=float, required=True)
    ap.add_argument("--surface-band", type=float, default=8e-6)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("keyholeDepthSurface.csv"),
    )
    args = ap.parse_args()

    objects = [
        p for p in args.post_processing.rglob("*.obj")
        if "metalgasinterface" in p.name.lower()
    ]
    if not objects:
        raise SystemExit(
            "No metalGasInterface OBJ files found under "
            f"{args.post_processing}"
        )

    rows = []
    for path in objects:
        vertices, faces = read_obj(path)
        components = connected_components(vertices, faces)
        comp, surface_connected = main_component(
            vertices,
            components,
            args.surface_y,
            args.surface_band,
        )

        bottom_idx = min(comp, key=lambda idx: vertices[idx][1])
        x, y, z = vertices[bottom_idx]

        depth = max(args.surface_y - y, 0.0)
        offset = math.hypot(x, z)

        rows.append(
            (
                time_from_path(path),
                depth,
                x,
                z,
                offset,
                len(comp),
                len(components),
                surface_connected,
                path,
            )
        )

    by_time = {}
    for row in rows:
        t = row[0]
        old = by_time.get(t)
        if old is None or row[1] > old[1]:
            by_time[t] = row

    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "time_s",
                "keyhole_depth_m",
                "keyhole_depth_um",
                "bottom_x_um",
                "bottom_z_um",
                "bottom_offset_um",
                "main_component_vertices",
                "interface_components",
                "surface_connected",
                "source",
            ]
        )
        for t in sorted(by_time):
            (
                _,
                depth,
                x,
                z,
                offset,
                nvert,
                ncomp,
                connected,
                path,
            ) = by_time[t]
            w.writerow(
                [
                    f"{t:.12g}",
                    f"{depth:.12g}",
                    f"{depth*1e6:.8g}",
                    f"{x*1e6:.8g}",
                    f"{z*1e6:.8g}",
                    f"{offset*1e6:.8g}",
                    nvert,
                    ncomp,
                    "yes" if connected else "fallback",
                    path,
                ]
            )

    latest = by_time[max(by_time)]
    print(f"Latest sampled time: {latest[0]:.12g} s")
    print(f"3-D connected-surface keyhole depth: {latest[1]*1e6:.6g} um")
    print(
        "Bottom lateral offset from laser axis: "
        f"{latest[4]*1e6:.6g} um"
    )
    print(f"Interface connected components: {latest[6]}")


if __name__ == "__main__":
    main()
