#!/usr/bin/env python3
"""Verify one native DEM review archive for the 50 us M247 pilot only."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tutorials/vacuumLaserbeamFoam/M247_0p6Pa_track1500um6umV2/powderBedConfig.json"
REQUIRED = ("demInput.json", "run.json", "powderManifest.json",
            "powderParticles.csv", "setFieldsDict", "post/final.dump")
PILOT_PACKING_RANGE = (0.54, 0.62)  # exploratory bracket, not final .58 +/- .03 gate


def digest(data):
    return hashlib.sha256(data).hexdigest()


def validate_manifest(manifest):
    gates = manifest.get("preflightGates", {})
    if manifest.get("generator") != "LIGGGHTS-PUBLIC-DEM":
        raise ValueError("Expected native LIGGGHTS powder")
    failed = [key for key, passed in gates.items() if key != "packing" and not passed]
    if failed:
        raise ValueError(f"DEM pilot safety gates failed: {failed}")
    if not all(key in gates for key in
               ("particleCount", "boundary", "d10", "d50", "d90", "overlap", "settled")):
        raise ValueError("DEM pilot safety gates are incomplete")
    packing = manifest.get("actualPackingFractionNominalLayer")
    if not isinstance(packing, (int, float)) or not PILOT_PACKING_RANGE[0] <= packing <= PILOT_PACKING_RANGE[1]:
        raise ValueError(f"DEM pilot packing outside {PILOT_PACKING_RANGE}: {packing}")
    if manifest.get("productionApproved"):
        raise ValueError("DEM archive unexpectedly claims production approval")
    return packing


def prepare(archive_path, stage):
    archive_path = Path(archive_path).resolve()
    stage = Path(stage)
    if stage.exists():
        raise FileExistsError(f"DEM stage already exists: {stage}")
    with tarfile.open(archive_path, "r:gz") as tar:
        matches = [name for name in tar.getnames() if name.endswith("/reviewManifest.json")]
        if len(matches) != 1:
            raise ValueError("Archive must contain exactly one reviewManifest.json")
        prefix = matches[0][:-len("reviewManifest.json")]
        def read(name):
            member = tar.getmember(prefix + name)
            if not member.isfile():
                raise ValueError(f"Not a regular archive file: {name}")
            return tar.extractfile(member).read()
        review = json.loads(read("reviewManifest.json"))
        if review.get("exitCode") != 0 or review.get("missingFiles"):
            raise ValueError("DEM archive was incomplete or failed")
        for name, expected in review.get("files", {}).items():
            if digest(read(name)) != expected:
                raise ValueError(f"DEM archive hash mismatch: {name}")
        if any(name not in review.get("files", {}) for name in REQUIRED):
            raise ValueError("DEM archive lacks a required hashed file")
        data = {name: read(name) for name in REQUIRED}
    dem_input = json.loads(data["demInput.json"])
    if dem_input.get("sourceConfigSha256") != digest(CONFIG.read_bytes()):
        raise ValueError("DEM input used a different powder configuration")
    run = json.loads(data["run.json"])
    if run.get("returncode") != 0:
        raise ValueError("Native LIGGGHTS run failed")
    manifest = json.loads(data["powderManifest.json"])
    packing = validate_manifest(manifest)
    if manifest.get("finalDumpSha256") != digest(data["post/final.dump"]):
        raise ValueError("Final DEM dump hash mismatch")
    rows = list(csv.DictReader(io.StringIO(data["powderParticles.csv"].decode("utf-8"))))
    if len(rows) != manifest.get("particleCount"):
        raise ValueError("DEM particle CSV count differs from manifest")
    stage.mkdir(parents=True)
    for name in ("powderManifest.json", "powderParticles.csv", "setFieldsDict"):
        (stage/name).write_bytes(data[name])
    report = dict(schema=1,archive=str(archive_path),archiveSha256=digest(archive_path.read_bytes()),
                  finalDumpSha256=manifest["finalDumpSha256"],particleCount=len(rows),
                  packingNominal=packing,strictPackingGate=manifest["preflightGates"]["packing"],
                  pilotPackingRange=PILOT_PACKING_RANGE,
                  experimentalPsdBasis=manifest.get("experimentalPsdBasis", "unknown"),
                  pilotOnly=True,productionApproved=False)
    (stage/"handoff.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("stage", type=Path)
    args = parser.parse_args()
    prepare(args.archive, args.stage)

