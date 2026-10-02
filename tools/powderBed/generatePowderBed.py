#!/usr/bin/env python3
"""Generate a deterministic non-overlapping spherical powder bed for setFields.

The packing is built by sequential vertical deposition. Each candidate sphere
is assigned a random (x,z) position and PSD radius, then dropped vertically
until it contacts either the substrate or an existing sphere. Candidates whose
top exceeds the configured layer thickness are rejected.

This is a geometry generator, not a DEM solver.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path


def percentile(values, q):
    if not values:
        return float("nan")
    values = sorted(values)
    if len(values) == 1:
        return values[0]
    x = q*(len(values)-1)
    lo = int(math.floor(x))
    hi = int(math.ceil(x))
    if lo == hi:
        return values[lo]
    w = x-lo
    return values[lo]*(1.0-w) + values[hi]*w


def sample_diameter(rng, cfg):
    kind = cfg["type"]

    if kind == "uniform":
        return rng.uniform(cfg["min"], cfg["max"])

    if kind == "lognormal":
        median = cfg["median"]
        geometric_sigma = cfg["geometricSigma"]
        dmin = cfg["min"]
        dmax = cfg["max"]

        for _ in range(10000):
            d = rng.lognormvariate(
                math.log(median),
                math.log(geometric_sigma),
            )
            if dmin <= d <= dmax:
                return d

        raise RuntimeError(
            "Could not sample truncated lognormal diameter after 10000 tries"
        )

    raise ValueError(f"Unknown diameter distribution type: {kind}")


def settling_height(x, z, r, particles, substrate_y, clearance):
    y = substrate_y + r + clearance

    for p in particles:
        dx = x - p["x"]
        dz = z - p["z"]
        horizontal2 = dx*dx + dz*dz
        contact = r + p["r"] + clearance

        if horizontal2 < contact*contact:
            vertical = math.sqrt(max(contact*contact-horizontal2, 0.0))
            y = max(y, p["y"] + vertical)

    return y


def check_no_overlap(particles, clearance):
    min_gap = float("inf")
    for i, a in enumerate(particles):
        for b in particles[i+1:]:
            dx = a["x"]-b["x"]
            dy = a["y"]-b["y"]
            dz = a["z"]-b["z"]
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            gap = distance-(a["r"]+b["r"])
            min_gap = min(min_gap, gap)
            if gap < clearance-1e-12:
                raise RuntimeError(
                    f"Particle overlap detected: gap={gap:.6g} m"
                )

    if not math.isfinite(min_gap):
        min_gap = 0.0
    return min_gap


def write_set_fields(path, particles, substrate_y):
    lines = [
        "FoamFile",
        "{",
        "    version 2.0;",
        "    format ascii;",
        "    class dictionary;",
        '    location "system";',
        "    object setFieldsDict;",
        "}",
        "",
        "defaultFieldValues",
        "(",
        "    volScalarFieldValue alpha.metal 0",
        ");",
        "",
        "regions",
        "(",
        "    boxToCell",
        "    {",
        "        box (-1 -1 -1) (1 %.12g 1);" % substrate_y,
        "        fieldValues",
        "        (",
        "            volScalarFieldValue alpha.metal 1",
        "        );",
        "    }",
        "",
    ]

    for i, p in enumerate(particles):
        lines.extend(
            [
                "    // particle %d, diameter %.12g m" % (i, 2.0*p["r"]),
                "    sphereToCell",
                "    {",
                "        origin (%.12g %.12g %.12g);"
                % (p["x"], p["y"], p["z"]),
                "        radius %.12g;" % p["r"],
                "        fieldValues",
                "        (",
                "            volScalarFieldValue alpha.metal 1",
                "        );",
                "    }",
                "",
            ]
        )

    lines.extend([");", ""])
    path.write_text("\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, required=True)
    ap.add_argument("--set-fields", type=Path, required=True)
    ap.add_argument("--particles", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text())

    seed = int(cfg["seed"])
    rng = random.Random(seed)

    bounds = cfg["footprint"]
    x_min = float(bounds["xMin"])
    x_max = float(bounds["xMax"])
    z_min = float(bounds["zMin"])
    z_max = float(bounds["zMax"])

    substrate_y = float(cfg["substrateSurfaceY"])
    layer_thickness = float(cfg["layerThickness"])
    top_y = substrate_y + layer_thickness
    target_fraction = float(cfg["targetSolidFraction"])
    max_attempts = int(cfg.get("maxAttempts", 200000))
    clearance = float(cfg.get("clearance", 0.0))

    footprint_area = (x_max-x_min)*(z_max-z_min)
    layer_volume = footprint_area*layer_thickness
    target_volume = target_fraction*layer_volume

    particles = []
    solid_volume = 0.0
    rejected_layer = 0

    attempts = 0
    while solid_volume < target_volume and attempts < max_attempts:
        attempts += 1
        d = sample_diameter(rng, cfg["diameterDistribution"])
        r = 0.5*d

        if x_min+r >= x_max-r or z_min+r >= z_max-r:
            raise RuntimeError("Particle diameter is larger than powder footprint")

        x = rng.uniform(x_min+r, x_max-r)
        z = rng.uniform(z_min+r, z_max-r)
        y = settling_height(
            x, z, r, particles, substrate_y, clearance
        )

        if y+r > top_y+1e-15:
            rejected_layer += 1
            continue

        p = {"x": x, "y": y, "z": z, "r": r}
        particles.append(p)
        solid_volume += 4.0*math.pi*r**3/3.0

    if solid_volume < target_volume:
        raise RuntimeError(
            "Failed to reach target solid fraction: "
            f"{solid_volume/layer_volume:.6g} < {target_fraction:.6g} "
            f"after {attempts} attempts"
        )

    min_gap = check_no_overlap(particles, clearance)

    args.set_fields.parent.mkdir(parents=True, exist_ok=True)
    args.particles.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.parent.mkdir(parents=True, exist_ok=True)

    write_set_fields(args.set_fields, particles, substrate_y)

    with args.particles.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "x_m", "y_m", "z_m", "radius_m", "diameter_m"])
        for i, p in enumerate(particles):
            w.writerow(
                [
                    i,
                    f'{p["x"]:.12g}',
                    f'{p["y"]:.12g}',
                    f'{p["z"]:.12g}',
                    f'{p["r"]:.12g}',
                    f'{2.0*p["r"]:.12g}',
                ]
            )

    diameters = [2.0*p["r"] for p in particles]
    tops = [p["y"]+p["r"] for p in particles]

    manifest = {
        "generator": "sequentialVerticalDeposition-v1",
        "seed": seed,
        "particleCount": len(particles),
        "attempts": attempts,
        "rejectedLayerThickness": rejected_layer,
        "substrateSurfaceY_m": substrate_y,
        "layerThickness_m": layer_thickness,
        "highestParticleTop_m": max(tops),
        "targetSolidFraction": target_fraction,
        "actualSolidFraction": solid_volume/layer_volume,
        "solidVolume_m3": solid_volume,
        "layerVolume_m3": layer_volume,
        "diameterMin_m": min(diameters),
        "diameterD10_m": percentile(diameters, 0.10),
        "diameterD50_m": percentile(diameters, 0.50),
        "diameterD90_m": percentile(diameters, 0.90),
        "diameterMax_m": max(diameters),
        "diameterMean_m": sum(diameters)/len(diameters),
        "minimumInterparticleGap_m": min_gap,
        "clearance_m": clearance,
        "config": cfg,
    }
    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")

    print(
        "POWDER_BED "
        f"seed={seed} "
        f"particles={len(particles)} "
        f"solidFraction={manifest['actualSolidFraction']:.8g} "
        f"D10_um={1e6*manifest['diameterD10_m']:.6g} "
        f"D50_um={1e6*manifest['diameterD50_m']:.6g} "
        f"D90_um={1e6*manifest['diameterD90_m']:.6g} "
        f"top_um={1e6*manifest['highestParticleTop_m']:.6g} "
        f"minGap_um={1e6*min_gap:.6g}"
    )


if __name__ == "__main__":
    main()
