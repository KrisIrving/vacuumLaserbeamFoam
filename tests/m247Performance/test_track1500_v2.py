import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
V2=ROOT/'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_track1500um6umV2'
OLD=V2.parent/'M247_0p6Pa_track1500um6um'

class CorrectedCorridorTest(unittest.TestCase):
    def test_mesh_covers_observed_front_with_fewer_cells(self):
        text=(V2/'system/blockMeshDict').read_text()
        blocks=re.findall(r'hex \(([^)]+)\) \((\d+) (\d+) (\d+)\)',text)
        self.assertEqual(len(blocks),27)
        self.assertEqual(sum(int(x)*int(y)*int(z) for _,x,y,z in blocks),3814272)
        self.assertAlmostEqual((1680e-6+240e-6)/320,6e-6)
        self.assertAlmostEqual((720e-6-180e-6)/90,6e-6)
        self.assertAlmostEqual(384e-6/64,6e-6)
        self.assertGreaterEqual((1680e-6-1500e-6-129e-6)*1e6,50)
        self.assertGreaterEqual((600e-6-180e-6)*1e6-326.50,90)
        self.assertIn('0.00192',text)
        self.assertLess(3814272,4232448)
        self.assertIn('pilot.CELLS=3814272',(ROOT/'tests/m247Performance/track1500_pilot_v2.py').read_text())

    def test_boundary_fields_and_process_are_unchanged(self):
        for directory in ('initial','constant'):
            for path in (OLD/directory).iterdir():
                if path.is_file():
                    self.assertEqual(path.read_bytes(),(V2/directory/path.name).read_bytes())
        for name in ('controlDict','fvSolution','fvSchemes','setFieldsDict'):
            self.assertEqual((OLD/'system'/name).read_bytes(),(V2/'system'/name).read_bytes())

if __name__=='__main__':unittest.main()
