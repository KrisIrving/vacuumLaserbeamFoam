"""Offline safety contract for DEM archive -> 50 us pilot transfer."""
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import m247_dem_handoff as handoff

TEMP_ROOT = Path(__file__).resolve().parents[2] / ".test-tmp"


def fixture_archive(path, corrupt=False):
    dump = b"final DEM dump\n"
    manifest = dict(generator="LIGGGHTS-PUBLIC-DEM", particleCount=1,
                    finalDumpSha256=handoff.digest(dump),productionApproved=False,
                    actualPackingFractionNominalLayer=.614,
                    preflightGates=dict(particleCount=True,boundary=True,d10=True,
                                        d50=True,d90=True,packing=False,overlap=True,settled=True))
    data = {
        "demInput.json": json.dumps(dict(sourceConfigSha256=handoff.digest(handoff.CONFIG.read_bytes()))).encode(),
        "run.json": b'{"returncode":0}',
        "powderManifest.json": json.dumps(manifest).encode(),
        "powderParticles.csv": b"id,x_m,y_m,z_m,radius_m,diameter_m\n1,0,0.00063,0,3e-5,6e-5\n",
        "setFieldsDict": b"FoamFile {}\n",
        "post/final.dump": dump,
    }
    review = dict(exitCode=0,missingFiles=[],files={k:handoff.digest(v) for k,v in data.items()})
    if corrupt:data["setFieldsDict"] = b"changed after manifest"
    data["reviewManifest.json"] = json.dumps(review).encode()
    with tarfile.open(path,"w:gz") as tar:
        for name,payload in data.items():
            info=tarfile.TarInfo("dem/"+name);info.size=len(payload)
            tar.addfile(info,io.BytesIO(payload))


class HandoffTest(unittest.TestCase):
    def test_pilot_only_accepts_verified_archive(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            archive=Path(directory)/"dem.tar.gz";stage=Path(directory)/"stage"
            fixture_archive(archive)
            handoff.prepare(archive,stage)
            report=json.loads((stage/"handoff.json").read_text())
            self.assertTrue(report["pilotOnly"])
            self.assertFalse(report["nominalPackingAdvisoryPass"])
            self.assertEqual(report["particleCount"],1)

    def test_nominal_packing_is_advisory(self):
        manifest=dict(generator="LIGGGHTS-PUBLIC-DEM",productionApproved=False,
                      actualPackingFractionNominalLayer=.71,
                      preflightGates=dict(particleCount=True,boundary=True,d10=True,
                                          d50=True,d90=True,packing=False,overlap=True,settled=True))
        self.assertEqual(handoff.validate_manifest(manifest),.71)

    def test_corrupt_archive_is_rejected_before_stage_creation(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            archive=Path(directory)/"dem.tar.gz";stage=Path(directory)/"stage"
            fixture_archive(archive,corrupt=True)
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                handoff.prepare(archive,stage)
            self.assertFalse(stage.exists())

    def test_other_failed_gate_cannot_use_pilot_exception(self):
        manifest=dict(generator="LIGGGHTS-PUBLIC-DEM",productionApproved=False,
                      actualPackingFractionNominalLayer=.614,
                      preflightGates=dict(particleCount=True,boundary=True,d10=True,
                                          d50=False,d90=True,packing=False,overlap=True,settled=True))
        with self.assertRaisesRegex(ValueError,"d50"):
            handoff.validate_manifest(manifest)


if __name__ == "__main__":unittest.main()

