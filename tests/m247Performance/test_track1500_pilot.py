import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
from track1500_pilot import field_rows,pool_geometry,TEMPLATE,CELLS

class TrackPilotTest(unittest.TestCase):
    def test_mesh_has_expected_cells_and_exact_fine_spacing(self):
        text=(TEMPLATE/'system/blockMeshDict').read_text()
        blocks=re.findall(r'hex\s*\(([^)]+)\)\s*\((\d+) (\d+) (\d+)\)',text)
        self.assertEqual(len(blocks),27)
        self.assertEqual(sum(int(x)*int(y)*int(z) for _,x,y,z in blocks),CELLS)
        self.assertAlmostEqual((1620e-6+240e-6)/310,6e-6)
        self.assertAlmostEqual(720e-6/120,6e-6)
        self.assertAlmostEqual(384e-6/64,6e-6)
        faces={}
        for ids,*_ in blocks:
            v=list(map(int,ids.split()))
            for indices in ((0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2),(0,1,2,3),(4,7,6,5)):
                key=tuple(sorted(v[i] for i in indices));faces[key]=faces.get(key,0)+1
        self.assertEqual(sum(n==1 for n in faces.values()),54)
        self.assertEqual(sum(n==2 for n in faces.values()),54)
        self.assertTrue(all(n in (1,2) for n in faces.values()))

    def test_full_scan_and_laser_off_are_not_clamped_heating(self):
        power=(TEMPLATE/'constant/timeVsLaserPower').read_text()
        position=(TEMPLATE/'constant/timeVsLaserPosition').read_text()
        self.assertIn('(0.001500001 0)',power)
        self.assertIn('(0.002 0)',power)
        self.assertIn('(0.0015 (0.0015 0.0009595 0))',position)
        self.assertIn('endTime 50e-6;', (TEMPLATE/'system/controlDict').read_text())

    def test_stream_reads_ascii_vectors_and_uniform_scalars(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'C';p.write_text('FoamFile { format ascii; }\ninternalField nonuniform List<vector>\n2\n(\n(1 2 3)\n(4 5 6)\n);\n')
            with patch('track1500_pilot.CELLS',2):self.assertEqual(list(field_rows(p,3)),[(1.,2.,3.),(4.,5.,6.)])
            p.write_text('FoamFile { format ascii; }\ninternalField uniform 1343.15;\n')
            with patch('track1500_pilot.CELLS',2):self.assertEqual(list(field_rows(p,1)),[(1343.15,),(1343.15,)])

    def test_stream_rejects_truncated_or_nonfinite_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'T'
            for body in ('1700\n','nan\n1800\n'):
                p.write_text('FoamFile { format ascii; }\ninternalField nonuniform List<scalar>\n2\n(\n'+body)
                with patch('track1500_pilot.CELLS',2),self.assertRaises(ValueError):list(field_rows(p,1))

    def test_pool_excludes_hot_gas_and_separates_disconnected_metal(self):
        points=[(45e-6,597e-6,3e-6),(51e-6,597e-6,3e-6),(57e-6,597e-6,3e-6),(300e-6,597e-6,3e-6)]
        def rows(p,width):
            return iter(points if p.name=='C' else [(1800,),(1800,),(5000,),(1800,)] if p.name=='T' else [(1,),(1,),(0,),(1,)])
        with patch('track1500_pilot.field_rows',side_effect=rows):r=pool_geometry(Path('unused'))
        self.assertEqual(r['solidus_connected_pool']['cells'],2)
        self.assertEqual(r['solidus_all_metal']['cells'],3)
        self.assertEqual(r['temperature_maxima_K']['gas'],5000)
        self.assertEqual(r['molten_metal_cells_outside_fine'],0)

    def test_generated_powder_preserves_packing_and_no_overlap(self):
        p=json.loads((TEMPLATE/'constant/powderManifest.json').read_text())
        self.assertEqual(p['particleCount'],330)
        self.assertTrue(p['preserveSampledPSD'])
        self.assertAlmostEqual(p['actualPackingFractionNominalLayer'],.58,places=3)
        self.assertGreaterEqual(p['minimumInterparticleGap_m'],-1e-12)

if __name__=='__main__':unittest.main()
