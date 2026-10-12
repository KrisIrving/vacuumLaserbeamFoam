"""Offline contract checks for the LIGGGHTS-to-OpenFOAM powder handoff."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

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
    def test_explicit_executable_and_bad_override(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            executable = Path(directory) / "liggghts"
            executable.write_text("fake")
            with patch.dict(dem.os.environ, {"LIGGGHTS_EXECUTABLE": str(executable)}), \
                 patch.object(dem.os, "access", return_value=True):
                self.assertEqual(dem.resolve_liggghts(), executable.resolve())
            with patch.dict(dem.os.environ, {"LIGGGHTS_EXECUTABLE": str(executable)+".missing"}):
                with self.assertRaisesRegex(FileNotFoundError, "LIGGGHTS_EXECUTABLE"):
                    dem.resolve_liggghts()

    def test_failed_run_packages_input_and_reason(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            work = Path(directory) / "failed-dem"
            with patch.object(dem, "resolve_liggghts", side_effect=FileNotFoundError("missing")):
                with self.assertRaisesRegex(FileNotFoundError, "missing"):
                    dem.run_native(work)
            self.assertTrue((work / "input.liggghts").is_file())
            dem.package(work, 1)
            manifest = json.loads((work / "reviewManifest.json").read_text())
            self.assertIn("input.liggghts", manifest["files"])

    def test_command_failure_archive_explains_missing_binary(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            work = Path(directory) / "missing-binary"
            env = dict(dem.os.environ, LIGGGHTS_EXECUTABLE=str(work / "absent"))
            result = subprocess.run(
                [sys.executable, str(Path(dem.__file__)), "run", "--work", str(work)],
                env=env, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 1)
            self.assertTrue((work / "failure.json").is_file())
            self.assertIn("LIGGGHTS_EXECUTABLE", (work / "failure.json").read_text())
            with dem.tarfile.open(Path(directory) / "M247_missing-binary_review.tar.gz") as archive:
                self.assertTrue(any(name.endswith("failure.json") for name in archive.getnames()))

    def test_preparation_and_unit_conversion(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            work = Path(directory)
            dem.create_input(work)
            setup = (work / "input.liggghts").read_text()
            self.assertIn("gravity 981 vector 0 -1 0", setup)
            self.assertIn("particledistribution/discrete", setup)
            self.assertIn("write_dump all custom post/final.dump", setup)
            self.assertLess(setup.index("compute radiusSum all reduce sum c_rad"),
                            setup.index("group trim variable above"))
            self.assertIn("thermo_style custom step atoms c_radiusSum\nrun 0\nvariable above", setup)
            metadata = json.loads((work / "demInput.json").read_text())
            self.assertEqual(metadata["insertedParticlesRequested"], 460)
            self.assertIn("delete_atoms group trim compress yes\nrun 250000", setup)
            self.assertIn("post/relaxed.dump", setup)
            self.assertAlmostEqual(sum(metadata["trimCalibration"]["massWeights"]), 1)
            rows = ["1 0 0.0629992 0 0.003 0 0 0",
                    "2 0.02 0.062 0 0.002 0 0 0"]
            dump(work / "post/raw.dump", rows)
            dump(work / "post/final.dump", rows)
            dem.audit(work)
            manifest = json.loads((work / "powderManifest.json").read_text())
            self.assertEqual(manifest["generator"], "LIGGGHTS-PUBLIC-DEM")
            self.assertEqual(manifest["particleCount"], 2)
            self.assertAlmostEqual(manifest["diameterMax_m"], 60e-6)
            self.assertGreater(manifest["diameterVolumeD50_m"],
                               manifest["diameterD50_m"])
            self.assertIn("sphereToCell", (work / "setFieldsDict").read_text())
            self.assertFalse(manifest["readyForReview"])
            self.assertTrue(manifest["preflightGates"]["boundary"])
            self.assertAlmostEqual(manifest["boundaryPenetrationMax_m"]["floor"], 8e-9)

    def test_material_boundary_crossing_still_fails(self):
        TEMP_ROOT.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=TEMP_ROOT) as directory:
            work = Path(directory)
            dem.create_input(work)
            rows = ["1 0 0.062995 0 0.003 0 0 0"]
            dump(work / "post/raw.dump", rows)
            dump(work / "post/final.dump", rows)
            with self.assertRaisesRegex(ValueError, "boundary penetration exceeds"):
                dem.audit(work)

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

