#!/usr/bin/env python3
"""Integrate recoil pressure on the atmosphere-connected 3-D keyhole surface."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path



def infer_time(path: Path) -> float:
    for parent in path.parents:
        try:
            return float(parent.name)
        except ValueError:
            pass
    raise RuntimeError(f"Could not infer time from {path}")


def read_legacy_vtk(path: Path):
    tokens = path.read_text(errors="ignore").split()

    def locate(name):
        try:
            return tokens.index(name)
        except ValueError as exc:
            raise RuntimeError(f"Missing {name} in {path}") from exc

    ip = locate("POINTS")
    npoints = int(tokens[ip + 1])
    p0 = ip + 3
    raw_points = [float(x) for x in tokens[p0:p0 + 3*npoints]]
    coords = [
        (raw_points[i], raw_points[i + 1], raw_points[i + 2])
        for i in range(0, len(raw_points), 3)
    ]

    if "POLYGONS" in tokens:
        ic = locate("POLYGONS")
    elif "CELLS" in tokens:
        ic = locate("CELLS")
    else:
        raise RuntimeError(f"Missing POLYGONS/CELLS in {path}")

    nfaces = int(tokens[ic + 1])
    pos = ic + 3
    faces = []
    for _ in range(nfaces):
        n = int(tokens[pos])
        pos += 1
        face = [int(v) for v in tokens[pos:pos+n]]
        pos += n
        if len(face) >= 3:
            faces.append(face)

    data_kind = None
    pvap = None
    pos = 0
    current_kind = None
    current_count = None

    while pos < len(tokens):
        tok = tokens[pos]

        if tok in ("POINT_DATA", "CELL_DATA") and pos + 1 < len(tokens):
            current_kind = tok
            current_count = int(tokens[pos + 1])
            pos += 2
            continue

        if tok == "FIELD" and pos + 2 < len(tokens):
            nfields = int(tokens[pos + 2])
            pos += 3

            for _ in range(nfields):
                name = tokens[pos]
                ncomp = int(tokens[pos + 1])
                ntuple = int(tokens[pos + 2])
                pos += 4  # skip datatype
                count = ncomp*ntuple
                vals = [float(x) for x in tokens[pos:pos+count]]
                pos += count

                if name == "pVap":
                    pvap = [
                        vals[i]
                        for i in range(0, len(vals), ncomp)
                    ]
                    data_kind = current_kind
            continue

        if tok == "SCALARS" and pos + 2 < len(tokens):
            name = tokens[pos + 1]
            ncomp = 1
            if pos + 3 < len(tokens):
                try:
                    ncomp = int(tokens[pos + 3])
                    pos += 4
                except ValueError:
                    pos += 3
            else:
                pos += 3

            if pos + 1 < len(tokens) and tokens[pos] == "LOOKUP_TABLE":
                pos += 2

            if current_count is None:
                raise RuntimeError(
                    f"SCALARS encountered before POINT/CELL_DATA in {path}"
                )

            count = current_count*ncomp
            vals = [float(x) for x in tokens[pos:pos+count]]
            pos += count

            if name == "pVap":
                pvap = [
                    vals[i]
                    for i in range(0, len(vals), ncomp)
                ]
                data_kind = current_kind
            continue

        pos += 1

    if pvap is None or data_kind is None:
        raise RuntimeError(f"pVap field not present in {path}")

    expected = npoints if data_kind == "POINT_DATA" else len(faces)
    if len(pvap) != expected:
        raise RuntimeError(
            f"pVap count {len(pvap)} != expected {expected} in {path}"
        )

    return coords, faces, data_kind, pvap


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


def components(points, faces):
    uf = UnionFind(len(points))
    used = set()
    for face in faces:
        used.update(face)
        for b in face[1:]:
            uf.union(face[0], b)

    comp_vertices = defaultdict(set)
    comp_faces = defaultdict(list)
    for fi, face in enumerate(faces):
        root = uf.find(face[0])
        comp_faces[root].append(fi)
        comp_vertices[root].update(face)

    return [
        (sorted(comp_vertices[root]), comp_faces[root])
        for root in comp_faces
    ]


def choose_main_component(points, comps, surface_y, band):
    candidates = []
    for verts, face_ids in comps:
        near = sum(
            1 for i in verts
            if abs(points[i][1] - surface_y) <= band
        )
        if near:
            candidates.append((near, len(face_ids), verts, face_ids))

    if candidates:
        _, _, verts, face_ids = max(candidates, key=lambda x: (x[0], x[1]))
        return verts, face_ids, True

    verts, face_ids = max(comps, key=lambda x: len(x[1]))
    return verts, face_ids, False


def triangle_fan(face):
    a = face[0]
    for j in range(1, len(face)-1):
        yield (a, face[j], face[j+1])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--post-processing", type=Path, required=True)
    ap.add_argument("--surface-y", type=float, required=True)
    ap.add_argument("--surface-band", type=float, default=8e-6)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()

    files = sorted(
        list(args.post_processing.rglob("*.vtk")),
        key=infer_time,
    )
    if not files:
        raise SystemExit(
            f"No legacy VTK surfaces found under {args.post_processing}"
        )

    rows = []

    for path in files:
        pts, faces, data_kind, pvap = read_legacy_vtk(path)
        comps = components(pts, faces)
        verts, face_ids, connected = choose_main_component(
            pts,
            comps,
            args.surface_y,
            args.surface_band,
        )

        force = [0.0, 0.0, 0.0]
        keyhole_area = 0.0
        pressures = []
        ntri = 0

        for fi in face_ids:
            face = faces[fi]
            for tri in triangle_fan(face):
                xyz = [pts[i] for i in tri]
                centroid_y = sum(p[1] for p in xyz)/3.0

                # Match the paper's "keyhole surface": only the cavity wall
                # below the original substrate surface is integrated.
                if centroid_y >= args.surface_y:
                    continue

                ab = tuple(xyz[1][j] - xyz[0][j] for j in range(3))
                ac = tuple(xyz[2][j] - xyz[0][j] for j in range(3))
                area_vec = (
                    0.5*(ab[1]*ac[2] - ab[2]*ac[1]),
                    0.5*(ab[2]*ac[0] - ab[0]*ac[2]),
                    0.5*(ab[0]*ac[1] - ab[1]*ac[0]),
                )
                area = math.sqrt(sum(v*v for v in area_vec))
                if area <= 0:
                    continue

                if data_kind == "POINT_DATA":
                    p = sum(pvap[i] for i in tri)/3.0
                    pressures.extend(float(pvap[i]) for i in tri)
                else:
                    p = float(pvap[fi])
                    pressures.append(p)

                for j in range(3):
                    force[j] += p*area_vec[j]
                keyhole_area += area
                ntri += 1

        if not pressures or keyhole_area <= 0:
            continue

        # Iso-surface face orientation can be globally opposite depending on
        # alpha convention. The paper compares the absolute axial recoil force.
        force_y_abs = abs(float(force[1]))

        rows.append(
            (
                infer_time(path),
                max(pressures),
                max(pressures)/101325.0,
                float(force[0]),
                float(force[1]),
                float(force[2]),
                force_y_abs,
                keyhole_area,
                ntri,
                len(comps),
                connected,
                path,
            )
        )

    if not rows:
        raise SystemExit("No usable keyhole-surface recoil rows were produced")

    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "time_s",
                "surface_p_recoil_max_pa",
                "surface_p_recoil_max_atm",
                "recoil_force_x_N",
                "recoil_force_y_N",
                "recoil_force_z_N",
                "recoil_force_y_abs_N",
                "keyhole_surface_area_m2",
                "keyhole_triangles",
                "interface_components",
                "surface_connected",
                "source",
            ]
        )
        for row in rows:
            w.writerow(
                [
                    f"{row[0]:.12g}",
                    f"{row[1]:.12g}",
                    f"{row[2]:.8g}",
                    f"{row[3]:.12g}",
                    f"{row[4]:.12g}",
                    f"{row[5]:.12g}",
                    f"{row[6]:.12g}",
                    f"{row[7]:.12g}",
                    row[8],
                    row[9],
                    "yes" if row[10] else "fallback",
                    row[11],
                ]
            )

    latest = rows[-1]
    peak_p = max(rows, key=lambda r: r[1])
    peak_f = max(rows, key=lambda r: r[6])

    print(
        f"Latest keyhole-surface recoil: "
        f"pMax={latest[1]/101325.0:.6g} atm, "
        f"|Fy|={latest[6]:.6g} N"
    )
    print(
        f"Peak surface pRecoil: {peak_p[1]/101325.0:.6g} atm "
        f"at {peak_p[0]*1e6:.6g} us"
    )
    print(
        f"Peak |keyhole recoil Fy|: {peak_f[6]:.6g} N "
        f"at {peak_f[0]*1e6:.6g} us"
    )


if __name__ == "__main__":
    main()
