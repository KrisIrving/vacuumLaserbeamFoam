"""Offline contract checks for the LIGGGHTS-to-OpenFOAM powder handoff."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools/powderBed"))
import m247_liggghts as dem

TEMP_ROOT = Path(__file__).resolve().parents[2] / ".test-tmp"


def dump(path, rows):
    header = ("ITEM: TIMESTEP\n450000\nITEM: NUMBER OF ATOMS\n"
              f"{len(rows)}\nITEM: BOX BOUNDS ff ff ff\n-0.03 0.174\n"
              "0.06 0.105\n-0.028 0.028\n"
              "ITEM: ATOMS id x y z radius vx vy vz\n")
    path.write_text(header + "\n".join(rows) + "\n")


class PowderDEMTest(unittest.TestCase):
    def test_preparation_and_unit_conversion(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            work = Path(directory)
            dem.create_input(work)
            setup = (work / "input.liggghts").read_text()
            self.assertIn("gravity 981 vector 0 -1 0", setup)
            self.assertIn("particledistribution/discrete", setup)
            self.assertIn("write_dump all custom post/final.dump", setup)
            rows = ["1 0 0.063 0 0.003 0 0 0",
                    "2 0.02 0.062 0 0.002 0 0 0"]
            dump(work / "post/raw.dump", rows)
            dump(work / "post/final.dump", rows)
            dem.audit(work)
            manifest = json.loads((work / "powderManifest.json").read_text())
            self.assertEqual(manifest["generator"], "LIGGGHTS-PUBLIC-DEM")
            self.assertEqual(manifest["particleCount"], 2)
            self.assertAlmostEqual(manifest["diameterMax_m"], 60e-6)
            self.assertIn("sphereToCell", (work / "setFieldsDict").read_text())
            self.assertFalse(manifest["readyForReview"])

    def test_dump_count_mismatch_is_rejected(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            path = Path(directory) / "broken.dump"
            dump(path, ["1 0 0.063 0 0.003 0 0 0"])
            path.write_text(path.read_text().replace("NUMBER OF ATOMS\n1", "NUMBER OF ATOMS\n2"))
            with self.assertRaisesRegex(ValueError, "count"):
                dem.read_dump(path)

    def test_provisional_template_is_blocked(self):
        with self.assertRaisesRegex(ValueError, "provisional geometric powder"):
            dem.verify_template()


if __name__ == "__main__":
    unittest.main()

