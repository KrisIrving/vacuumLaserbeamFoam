import json
from pathlib import Path
import tarfile
import tempfile
import unittest
from unittest.mock import patch
from wang_ray_suite import crossing, interpolate, compare_histories, package, field_metrics

def fixture(scale=1,wall=100):
    diagnostics=[dict(time=t,Tmax=3000*scale,depositedPower=100*scale,
        evaporationPower=2*scale,recoilForceX=0,recoilForceY=.004*scale,recoilForceZ=0) for t in (2e-6,4e-6)]
    return dict(depth_history=[(2e-6,32*scale),(4e-6,136*scale)],
        liquid_volume=[dict(time_s=t,liquid_metal_volume_m3=scale*1e-12) for t in (2e-6,4e-6)],
        diagnostics=diagnostics,job_wall_s=wall,thermal_gate=True,growth_32_136_us=75*scale,
        recoil_history=[dict(time_s=t,full_recoil_force_y_signed_N=.004*scale,
        full_scalar_pressure_load_N=.005*scale) for t in (2e-6,4e-6)])

class WangSuiteTest(unittest.TestCase):
    def test_numeric_time_order_in_general_format_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            case=Path(tmp)
            for name in ('8e-05','0.00014'): (case/name).mkdir()
            with patch('wang_ray_suite.scalar_field',return_value=[1,.5]):
                rows=field_metrics(case)
            self.assertEqual([r['time_s'] for r in rows],[8e-5,.00014])

    def test_first_upward_crossing_does_not_use_later_oscillation(self):
        self.assertAlmostEqual(crossing([(0,0),(2,40),(3,10),(4,50)],32),1.6)
        self.assertIsNone(crossing([(0,0),(2,40)],136))

    def test_interpolation_refuses_unmeasured_time(self):
        with self.assertRaises(ValueError): interpolate([(1,1),(2,2)],3)

    def test_fast_but_inaccurate_candidate_rejected(self):
        report=compare_histories(fixture(),fixture(1.06,50))
        self.assertEqual(report['job_speedup'],2)
        self.assertFalse(report['eligible_for_M247_confirmation'])

    def test_pass_requires_thermal_convergence(self):
        a=fixture(1.01,60)
        self.assertTrue(compare_histories(fixture(),a)['eligible_for_M247_confirmation'])
        a['thermal_gate']=False
        self.assertFalse(compare_histories(fixture(),a)['eligible_for_M247_confirmation'])

    def test_failed_package_keeps_logs_and_excludes_mesh_and_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp)/'wang-test'; work.mkdir()
            (work/'rays384').mkdir()
            (work/'rays384/log.vacuumLaserbeamFoam').write_text('failure')
            (work/'rays384/0.00014').mkdir()
            (work/'rays384/0.00014/T').write_text('large field')
            package(work,1)
            manifest=json.loads((work/'manifest.json').read_text())
            self.assertEqual(manifest['exit_code'],1)
            with tarfile.open(work.parent/'M247_wang-test_review.tar.gz') as archive:
                self.assertTrue(any('log.vacuum' in n for n in archive.getnames()))
                self.assertFalse(any('/0.00014/' in n for n in archive.getnames()))

if __name__=='__main__': unittest.main()
