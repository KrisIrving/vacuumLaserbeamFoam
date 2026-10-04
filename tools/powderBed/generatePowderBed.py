#!/usr/bin/env python3
"""Generate a deterministic non-overlapping spherical powder bed for setFields.

Two modes are supported:

1. legacy sequential sampling: a new diameter is sampled for every placement
   attempt. This preserves all existing 304L cases.
2. fixed-PSD placement: the complete diameter set is frozen first, then each
   particle is placed without redrawing a smaller replacement if it does not
   fit. This is the preferred M247 path.

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


def piecewise_quantile_value(cfg, u):
    qs = [float(v) for v in cfg["quantiles"]]
    ds = [float(v) for v in cfg["diameters"]]

    if len(qs) != len(ds) or len(qs) < 2:
        raise ValueError("piecewiseQuantile requires matching quantiles/diameters")
    if qs[0] != 0.0 or qs[-1] != 1.0:
        raise ValueError("piecewiseQuantile quantiles must start at 0 and end at 1")
    if any(b <= a for a, b in zip(qs[:-1], qs[1:])):
        raise ValueError("piecewiseQuantile quantiles must be strictly increasing")
    if any(b < a for a, b in zip(ds[:-1], ds[1:])):
        raise ValueError("piecewiseQuantile diameters must be nondecreasing")

    u = min(max(float(u), 0.0), 1.0)
    for i in range(len(qs)-1):
        if qs[i] <= u <= qs[i+1]:
            w = (u-qs[i])/(qs[i+1]-qs[i])
            return ds[i]*(1.0-w) + ds[i+1]*w

    return ds[-1]


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

    if kind == "piecewiseQuantile":
        return piecewise_quantile_value(cfg, rng.random())

    raise ValueError(f"Unknown diameter distribution type: {kind}")


def sphere_volume_from_diameter(d):
    return math.pi*d**3/6.0


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


def target_volume_from_config(cfg, footprint_area, envelope_thickness):
    if "nominalLayerThickness" in cfg or "targetPackingFraction" in cfg:
        if "nominalLayerThickness" not in cfg or "targetPackingFraction" not in cfg:
            raise ValueError(
                "nominalLayerThickness and targetPackingFraction must be supplied together"
            )

        nominal = float(cfg["nominalLayerThickness"])
        packing = float(cfg["targetPackingFraction"])

        if nominal <= 0 or packing <= 0 or packing > 1:
            raise ValueError("Invalid nominal layer thickness / packing fraction")

        return footprint_area*nominal*packing, nominal, packing

    target_fraction = float(cfg["targetSolidFraction"])

    if target_fraction <= 0 or target_fraction > 1:
        raise ValueError("Invalid targetSolidFraction")

    return (
        footprint_area*envelope_thickness*target_fraction,
        envelope_thickness,
        target_fraction,
    )


def fixed_quantile_diameters(cfg, target_volume):
    dist = cfg["diameterDistribution"]

    # Estimate the particle count from a dense deterministic quadrature of the
    # requested CDF, then choose the nearby integer count whose total volume is
    # closest to target. This preserves the requested D10/D50/D90 much better
    # than a small random sample.
    n_probe = 10000
    probe = [
        piecewise_quantile_value(dist, (i+0.5)/n_probe)
        for i in range(n_probe)
    ]
    mean_volume = sum(sphere_volume_from_diameter(d) for d in probe)/n_probe
    n0 = max(1, int(round(target_volume/mean_volume)))

    best = None
    for n in range(max(1, n0-3), n0+4):
        diameters = [
            piecewise_quantile_value(dist, (i+0.5)/n)
            for i in range(n)
        ]
        volume = sum(sphere_volume_from_diameter(d) for d in diameters)
        candidate = (abs(volume-target_volume), diameters)
        if best is None or candidate[0] < best[0]:
            best = candidate

    return list(best[1])


def build_fixed_diameter_set(rng, cfg, target_volume):
    dist = cfg["diameterDistribution"]

    if dist["type"] == "piecewiseQuantile":
        diameters = fixed_quantile_diameters(cfg, target_volume)
    else:
        diameters = []
        volume = 0.0

        while volume < target_volume:
            d = sample_diameter(rng, dist)
            diameters.append(d)
            volume += sphere_volume_from_diameter(d)

            if len(diameters) > 100000:
                raise RuntimeError("Excessive particle count while sampling PSD")

    order = cfg.get("placementOrder", "sampled")

    if order == "largestFirst":
        diameters.sort(reverse=True)
    elif order == "smallestFirst":
        diameters.sort()
    elif order == "shuffle":
        rng.shuffle(diameters)
    elif order != "sampled":
        raise ValueError(f"Unknown placementOrder: {order}")

    return diameters


def place_fixed_diameters
(
    rng,
    diameters,
    bounds,
    substrate_y,
    top_y,
    clearance,
    attempts_per_particle,
):
    x_min = float(bounds["xMin"])
    x_max = float(bounds["xMax"])
    z_min = float(bounds["zMin"])
    z_max = float(bounds["zMax"])

    particles = []
    attempts = 0
    rejected_layer = 0

    for particlei, d in enumerate(diameters):
        r = 0.5*d

        if x_min+r >= x_max-r or z_min+r >= z_max-r:
            raise RuntimeError("Particle diameter is larger than powder footprint")

        placed = False

        for _ in range(attempts_per_particle):
            attempts += 1

            x = rng.uniform(x_min+r, x_max-r)
            z = rng.uniform(z_min+r, z_max-r)
            y = settling_height(
                x,
                z,
                r,
                particles,
                substrate_y,
                clearance,
            )

            if y+r > top_y+1e-15:
                rejected_layer += 1
                continue

            particles.append({"x": x, "y": y, "z": z, "r": r})
            placed = True
            break

        if not placed:
            raise RuntimeError(
                "Could not place fixed-PSD particle "
                f"{particlei} (D={1e6*d:.6g} um) after "
                f"{attempts_per_particle} position attempts. "
                "Increase the geometric envelope/footprint or reduce the "
                "requested nominal packing; do not silently redraw a smaller "
                "particle."
            )

    return particles, attempts, rejected_layer


def legacy_generate
(
    rng,
    cfg,
    bounds,
    substrate_y,
    top_y,
    target_volume,
    clearance,
    max_attempts,
):
    x_min = float(bounds["xMin"])
    x_max = float(bounds["xMax"])
    z_min = float(bounds["zMin"])
    z_max = float(bounds["zMax"])

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
            x,
            z,
            r,
            particles,
            substrate_y,
            clearance,
        )

        if y+r > top_y+1e-15:
            rejected_layer += 1
            continue

        particles.append({"x": x, "y": y, "z": z, "r": r})
        solid_volume += sphere_volume_from_diameter(d)

    if solid_volume < target_volume:
        raise RuntimeError(
            "Failed to reach target solid volume after "
            f"{attempts} attempts"
        )

    return particles, attempts, rejected_layer


def projected_coverage(particles, region, spacing):
    x_min = float(region["xMin"])
    x_max = float(region["xMax"])
    z_min = float(region["zMin"])
    z_max = float(region["zMax"])

    if x_max <= x_min or z_max <= z_min:
        raise ValueError("Invalid projected-coverage region")

    nx = max(1, int(math.ceil((x_max-x_min)/spacing)))
    nz = max(1, int(math.ceil((z_max-z_min)/spacing)))

    covered = 0
    total = nx*nz

    for ix in range(nx):
        x = x_min + (ix+0.5)*(x_max-x_min)/nx

        for iz in range(nz):
            z = z_min + (iz+0.5)*(z_max-z_min)/nz

            for p in particles:
                dx = x-p["x"]
                dz = z-p["z"]

                if dx*dx + dz*dz <= p["r"]*p["r"]:
                    covered += 1
                    break

    return covered/total


def maximum_centerline_gap
(
    particles,
    x_min,
    x_max,
    z0,
    spacing,
):
    n = max(1, int(math.ceil((x_max-x_min)/spacing)))
    covered = []

    for i in range(n):
        x = x_min + (i+0.5)*(x_max-x_min)/n
        hit = False

        for p in particles:
            dx = x-p["x"]
            dz = z0-p["z"]

            if dx*dx + dz*dz <= p["r"]*p["r"]:
                hit = True
                break

        covered.append(hit)

    longest = 0
    current = 0

    for hit in covered:
        if hit:
            current = 0
        else:
            current += 1
            longest = max(longest, current)

    return longest*(x_max-x_min)/n


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
    max_attempts = int(cfg.get("maxAttempts", 200000))
    clearance = float(cfg.get("clearance", 0.0))

    footprint_area = (x_max-x_min)*(z_max-z_min)

    (
        target_volume,
        nominal_layer_thickness,
        target_packing_fraction,
    ) = target_volume_from_config(
        cfg,
        footprint_area,
        layer_thickness,
    )

    preserve_psd = bool(cfg.get("preserveSampledPSD", False))

    if preserve_psd:
        diameters = build_fixed_diameter_set(
            rng,
            cfg,
            target_volume,
        )

        particles, attempts, rejected_layer = place_fixed_diameters(
            rng,
            diameters,
            bounds,
            substrate_y,
            top_y,
            clearance,
            int(cfg.get("placementAttemptsPerParticle", 20000)),
        )
    else:
        particles, attempts, rejected_layer = legacy_generate(
            rng,
            cfg,
            bounds,
            substrate_y,
            top_y,
            target_volume,
            clearance,
            max_attempts,
        )

    solid_volume = sum(
        4.0*math.pi*p["r"]**3/3.0
        for p in particles
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

    equivalent_dense_thickness = solid_volume/footprint_area
    envelope_fraction = solid_volume/(footprint_area*layer_thickness)
    nominal_packing = (
        solid_volume
       /(footprint_area*nominal_layer_thickness)
    )

    manifest = {
        "generator": "sequentialVerticalDeposition-v2",
        "seed": seed,
        "particleCount": len(particles),
        "attempts": attempts,
        "rejectedLayerThickness": rejected_layer,
        "preserveSampledPSD": preserve_psd,
        "substrateSurfaceY_m": substrate_y,
        "layerThickness_m": layer_thickness,
        "nominalLayerThickness_m": nominal_layer_thickness,
        "targetPackingFractionNominalLayer": target_packing_fraction,
        "highestParticleTop_m": max(tops),
        "targetSolidVolume_m3": target_volume,
        "solidVolume_m3": solid_volume,
        "layerVolume_m3": footprint_area*layer_thickness,
        "equivalentDenseThickness_m": equivalent_dense_thickness,
        "actualPackingFractionNominalLayer": nominal_packing,
        "actualSolidFractionGeometricEnvelope": envelope_fraction,

        # Backward-compatible key retained for existing 304L preflight scripts.
        "targetSolidFraction": (
            target_volume/(footprint_area*layer_thickness)
        ),
        "actualSolidFraction": envelope_fraction,

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

    if cfg.get("coverage"):
        coverage_cfg = cfg["coverage"]
        spacing = float(coverage_cfg.get("gridSpacing", 2e-6))

        manifest["projectedCoverageFractionFootprint"] = (
            projected_coverage(
                particles,
                bounds,
                spacing,
            )
        )

        if coverage_cfg.get("corridor"):
            corridor = coverage_cfg["corridor"]

            manifest["projectedCoverageFractionCorridor"] = (
                projected_coverage(
                    particles,
                    corridor,
                    spacing,
                )
            )

            manifest["maximumUncoveredCenterlineGap_m"] = (
                maximum_centerline_gap(
                    particles,
                    float(corridor["xMin"]),
                    float(corridor["xMax"]),
                    float(coverage_cfg.get("centerlineZ", 0.0)),
                    spacing,
                )
            )

    args.manifest.write_text(json.dumps(manifest, indent=2) + "\n")

    message = (
        "POWDER_BED "
        f"seed={seed} "
        f"particles={len(particles)} "
        f"solidFraction={envelope_fraction:.8g} "
        f"packingNominal={nominal_packing:.8g} "
        f"D10_um={1e6*manifest['diameterD10_m']:.6g} "
        f"D50_um={1e6*manifest['diameterD50_m']:.6g} "
        f"D90_um={1e6*manifest['diameterD90_m']:.6g} "
        f"top_um={1e6*manifest['highestParticleTop_m']:.6g} "
        f"minGap_um={1e6*min_gap:.6g}"
    )

    if "projectedCoverageFractionCorridor" in manifest:
        message += (
            f" corridorCoverage="
            f"{manifest['projectedCoverageFractionCorridor']:.6g}"
            f" maxCenterlineGap_um="
            f"{1e6*manifest['maximumUncoveredCenterlineGap_m']:.6g}"
        )

    print(message)


if __name__ == "__main__":
    main()
