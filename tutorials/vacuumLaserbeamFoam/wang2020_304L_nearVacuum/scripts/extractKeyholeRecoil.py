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
    points = [
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

    fields = {}
    field_kind = {}
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
                pos += 4
                count = ncomp*ntuple
                vals = [float(x) for x in tokens[pos:pos+count]]
                pos += count
                fields[name] = [
                    vals[i:i+ncomp]
                    for i in range(0, len(vals), ncomp)
                ]
                field_kind[name] = current_kind
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
            fields[name] = [
                vals[i:i+ncomp]
                for i in range(0, len(vals), ncomp)
            ]
            field_kind[name] = current_kind
            continue

        pos += 1

    for required in ("pVap", "T"):
        if required not in fields:
            raise RuntimeError(f"{required} field not present in {path}")

        expected = npoints if field_kind[required] == "POINT_DATA" else len(faces)
        if len(fields[required]) != expected:
            raise RuntimeError(
                f"{required} count {len(fields[required])} "
                f"!= expected {expected} in {path}"
            )

    return points, faces, fields, field_kind


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
    for face in faces:
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


def scalar_on_triangle(name, fields, field_kind, fi, tri):
    vals = fields[name]
    if field_kind[name] == "POINT_DATA":
        return sum(vals[i][0] for i in tri)/3.0
    return vals[fi][0]


def area_weighted_percentile(values_and_areas, fraction):
    ordered = sorted(values_and_areas, key=lambda x: x[0])
    total = sum(area for _, area in ordered)
    if total <= 0:
        return float("nan")

    target = fraction*total
    cumulative = 0.0
    for value, area in ordered:
        cumulative += area
        if cumulative >= target:
            return value

    return ordered[-1][0]


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
        points, faces, fields, field_kind = read_legacy_vtk(path)
        comps = components(points, faces)
        _, face_ids, connected = choose_main_component(
            points,
            comps,
            args.surface_y,
            args.surface_band,
        )

        signed_force = [0.0, 0.0, 0.0]
        axial_abs_sum = 0.0
        projected_area_y = 0.0
        keyhole_area = 0.0
        scalar_pressure_load = 0.0

        full_signed_force = [0.0, 0.0, 0.0]
        full_axial_abs_sum = 0.0
        full_projected_area_y = 0.0
        full_surface_area = 0.0
        full_scalar_pressure_load = 0.0

        above_signed_force = [0.0, 0.0, 0.0]
        above_axial_abs_sum = 0.0
        above_projected_area_y = 0.0
        above_surface_area = 0.0
        above_scalar_pressure_load = 0.0

        face_pressures = []
        pressure_area = []
        face_temperatures = []
        ntri = 0

        for fi in face_ids:
            face = faces[fi]
            for tri in triangle_fan(face):
                xyz = [points[i] for i in tri]
                centroid_y = sum(p[1] for p in xyz)/3.0

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

                p = scalar_on_triangle(
                    "pVap", fields, field_kind, fi, tri
                )
                temperature = scalar_on_triangle(
                    "T", fields, field_kind, fi, tri
                )

                # Whole atmosphere-connected main interface. Flat cold regions
                # naturally contribute essentially zero recoil, while overflow
                # and the keyhole rim remain included as in Wang's discussion.
                for j in range(3):
                    full_signed_force[j] += p*area_vec[j]
                full_axial_abs_sum += p*abs(area_vec[1])
                full_projected_area_y += abs(area_vec[1])
                full_surface_area += area
                full_scalar_pressure_load += p*area

                if centroid_y >= args.surface_y:
                    for j in range(3):
                        above_signed_force[j] += p*area_vec[j]
                    above_axial_abs_sum += p*abs(area_vec[1])
                    above_projected_area_y += abs(area_vec[1])
                    above_surface_area += area
                    above_scalar_pressure_load += p*area
                    continue

                # Below-substrate cavity-only metric retained for continuity.
                for j in range(3):
                    signed_force[j] += p*area_vec[j]

                axial_abs_sum += p*abs(area_vec[1])
                projected_area_y += abs(area_vec[1])

                keyhole_area += area
                scalar_pressure_load += p*area
                face_pressures.append(p)
                pressure_area.append((p, area))
                face_temperatures.append(temperature)
                ntri += 1

        if not face_pressures or keyhole_area <= 0:
            continue

        raw_pvap = [row[0] for row in fields["pVap"]]
        raw_surface_max = max(raw_pvap)
        face_pmax = max(face_pressures)
        face_p99 = area_weighted_percentile(pressure_area, 0.99)
        face_tmax = max(face_temperatures)

        rows.append(
            (
                infer_time(path),
                raw_surface_max,
                raw_surface_max/101325.0,
                face_pmax,
                face_pmax/101325.0,
                face_p99,
                face_p99/101325.0,
                face_tmax,
                signed_force[0],
                signed_force[1],
                signed_force[2],
                abs(signed_force[1]),
                axial_abs_sum,
                projected_area_y,
                keyhole_area,
                scalar_pressure_load,
                full_signed_force[0],
                full_signed_force[1],
                full_signed_force[2],
                abs(full_signed_force[1]),
                full_axial_abs_sum,
                full_projected_area_y,
                full_surface_area,
                full_scalar_pressure_load,
                above_signed_force[1],
                abs(above_signed_force[1]),
                above_axial_abs_sum,
                above_projected_area_y,
                above_surface_area,
                above_scalar_pressure_load,
                ntri,
                len(comps),
                connected,
                field_kind["pVap"],
                path,
            )
        )

    if not rows:
        raise SystemExit("No usable keyhole-surface recoil rows were produced")

    header = [
        "time_s",
        "sampled_p_recoil_max_pa",
        "sampled_p_recoil_max_atm",
        "face_p_recoil_max_pa",
        "face_p_recoil_max_atm",
        "face_p_recoil_area_p99_pa",
        "face_p_recoil_area_p99_atm",
        "face_T_max_K",
        "recoil_force_x_signed_N",
        "recoil_force_y_signed_N",
        "recoil_force_z_signed_N",
        "recoil_force_y_signed_abs_N",
        "recoil_force_y_abs_sum_N",
        "projected_area_y_m2",
        "keyhole_surface_area_m2",
        "cavity_scalar_pressure_load_N",
        "full_recoil_force_x_signed_N",
        "full_recoil_force_y_signed_N",
        "full_recoil_force_z_signed_N",
        "full_recoil_force_y_signed_abs_N",
        "full_recoil_force_y_abs_sum_N",
        "full_projected_area_y_m2",
        "full_surface_area_m2",
        "full_scalar_pressure_load_N",
        "above_recoil_force_y_signed_N",
        "above_recoil_force_y_signed_abs_N",
        "above_recoil_force_y_abs_sum_N",
        "above_projected_area_y_m2",
        "above_surface_area_m2",
        "above_scalar_pressure_load_N",
        "keyhole_triangles",
        "interface_components",
        "surface_connected",
        "pVap_data_kind",
        "source",
    ]

    with args.output.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow(
                [
                    f"{row[0]:.12g}",
                    f"{row[1]:.12g}",
                    f"{row[2]:.8g}",
                    f"{row[3]:.12g}",
                    f"{row[4]:.8g}",
                    f"{row[5]:.12g}",
                    f"{row[6]:.8g}",
                    f"{row[7]:.12g}",
                    f"{row[8]:.12g}",
                    f"{row[9]:.12g}",
                    f"{row[10]:.12g}",
                    f"{row[11]:.12g}",
                    f"{row[12]:.12g}",
                    f"{row[13]:.12g}",
                    f"{row[14]:.12g}",
                    f"{row[15]:.12g}",
                    f"{row[16]:.12g}",
                    f"{row[17]:.12g}",
                    f"{row[18]:.12g}",
                    f"{row[19]:.12g}",
                    f"{row[20]:.12g}",
                    f"{row[21]:.12g}",
                    f"{row[22]:.12g}",
                    f"{row[23]:.12g}",
                    f"{row[24]:.12g}",
                    f"{row[25]:.12g}",
                    f"{row[26]:.12g}",
                    f"{row[27]:.12g}",
                    f"{row[28]:.12g}",
                    f"{row[29]:.12g}",
                    row[30],
                    row[31],
                    "yes" if row[32] else "fallback",
                    row[33],
                    row[34],
                ]
            )

    latest = rows[-1]
    peak_face_p = max(rows, key=lambda r: r[3])
    peak_p99 = max(rows, key=lambda r: r[5])
    peak_abs_sum = max(rows, key=lambda r: r[12])
    peak_full_abs_sum = max(rows, key=lambda r: r[20])
    peak_full_scalar_load = max(rows, key=lambda r: r[23])

    print(
        "Latest keyhole-surface recoil: "
        f"facePmax={latest[4]:.6g} atm, "
        f"areaP99={latest[6]:.6g} atm, "
        f"|sum Fy signed|={latest[11]:.6g} N, "
        f"sum |dFy|={latest[12]:.6g} N"
    )
    print(
        f"Latest keyhole-surface Tmax: {latest[7]:.6g} K; "
        f"pVap VTK data={latest[33]}"
    )
    print(
        f"Peak face-centre pRecoil: {peak_face_p[4]:.6g} atm "
        f"at {peak_face_p[0]*1e6:.6g} us"
    )
    print(
        f"Peak area-weighted p99 recoil: {peak_p99[6]:.6g} atm "
        f"at {peak_p99[0]*1e6:.6g} us"
    )
    print(
        f"Peak cavity-only orientation-independent axial recoil: "
        f"{peak_abs_sum[12]:.6g} N "
        f"at {peak_abs_sum[0]*1e6:.6g} us"
    )
    print(
        f"Latest full connected-surface axial recoil: "
        f"signed |Fy|={latest[19]:.6g} N, "
        f"sum |dFy|={latest[20]:.6g} N; "
        f"scalar integral p*dS={latest[23]:.6g} N; "
        f"above-surface contribution={latest[26]:.6g} N"
    )
    print(
        f"Peak full connected-surface orientation-independent axial recoil: "
        f"{peak_full_abs_sum[20]:.6g} N "
        f"at {peak_full_abs_sum[0]*1e6:.6g} us"
    )
    print(
        f"Peak full connected-surface scalar pressure load integral p*dS: "
        f"{peak_full_scalar_load[23]:.6g} N "
        f"at {peak_full_scalar_load[0]*1e6:.6g} us"
    )


if __name__ == "__main__":
    main()
