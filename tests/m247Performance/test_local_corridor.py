"""Offline geometry and provenance checks for the local 50us comparison."""
from pathlib import Path
import re
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
from local_corridor_mesh import CELLS,local_mesh_dictionary
from local_corridor_compare import compare

ROOT=Path(__file__).resolve().parents[2]
MESH=ROOT/'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_track1500um6umV2/system/blockMeshDict'


def fixture(candidate=False):
    cells=CELLS if candidate else 3814272
    geometry=dict(solidus_connected_pool=dict(depth_from_original_surface_um=93,
                                            width_z_um=234,fine_margin_um=45),
                  liquidus_all_metal=dict(cells=6508),
                  temperature_maxima_K=dict(metal=3000,interface=4230,gas=4100),
                  molten_metal_cells_outside_fine=0)
    return {
        'track1500/probe.json':dict(start_s=0,end_s=50e-6,duration_us=50,
            ranks=48,rays=384,epsilon_tolerance=1e-4,
            phase_temperature_tolerance_K=.01,epsilon_relaxation=1,
            variant='track1500LocalCorridorDEM' if candidate else 'track1500PilotDEM',
            cells=cells),
        'environment':dict(WM_PROJECT_VERSION='v2512'),
        'solverCheck.json':dict(passed=True,solver_sha256='solver',
            laser_library_check=dict(laser_library_sha256='laser')),
        'pilotReport.json':dict(complete=True,thermal_gate=True,
            demHandoff=dict(archiveSha256='powder'),
            static_local_corridor_only=candidate,geometry=geometry,
            solver=dict(job_wall_s=6000 if candidate else 12348,
                        thermal_limit_hits=0,sections=dict(pressure=dict(mean_s=3000 if candidate else 6308)))),
        'inputHashes.json':dict(**{'system/blockMeshDict':'local' if candidate else 'full',
                                    'constant/LaserProperties':'same'}),
        'depositedPower_W':257,
        'T_linear_cap_count':1,
        'T_linear_above_tolerance_count':1,
    }


class LocalCorridorTest(unittest.TestCase):
    def test_mesh_transform_reduces_only_far_ahead_resolution(self):
        original=MESH.read_text(encoding='utf-8')
        changed=local_mesh_dictionary(original)
        blocks=re.findall(r'hex \([^)]+\) \((\d+) (\d+) (\d+)\)',changed)
        self.assertEqual(sum(int(x)*int(y)*int(z) for x,y,z in blocks),CELLS)
        self.assertEqual(changed.count('(0.00030 '),16)
        self.assertEqual(changed.count('(0.00168 '),0)
        self.assertIn('(0.00192 ',changed)
        self.assertEqual(MESH.read_text(encoding='utf-8'),original)
        with self.assertRaisesRegex(ValueError,'vertices'):
            local_mesh_dictionary(changed)

    def test_comparison_requires_only_mesh_change(self):
        baseline=fixture();candidate=fixture(True)
        report=compare(baseline,candidate,'baseline-sha')
        self.assertTrue(report['local_50us_screen_pass'])
        self.assertGreater(report['cost']['job_speedup'],2)
        self.assertFalse(report['full_track_ready'])
        candidate['inputHashes.json']['constant/LaserProperties']='changed'
        with self.assertRaisesRegex(ValueError,'Inputs changed beyond the mesh'):
            compare(baseline,candidate,'baseline-sha')


if __name__=='__main__':unittest.main()

