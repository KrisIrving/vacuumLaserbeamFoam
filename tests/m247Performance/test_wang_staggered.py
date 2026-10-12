import math
from pathlib import Path
import tempfile
import json
import unittest
from unittest.mock import patch
from wang_staggered import collect, package

class StaggeredTest(unittest.TestCase):
    def test_full_slope_correction_solves_isolated_mushy_enthalpy(self):
        cp,latent,solidus,width=735.,274000.,1697.,30.
        target=.35
        enthalpy=cp*(solidus+width*target)+latent*target
        def correct(epsilon,relaxation):
            temperature=(enthalpy-latent*epsilon)/cp
            return epsilon+relaxation*cp/(latent+cp*width)*(temperature-solidus-width*epsilon)
        full=correct(.2,1.)
        half=correct(.2,.5)
        self.assertAlmostEqual(full,target,places=12)
        self.assertAlmostEqual(abs(half-target),abs(.2-target)/2,places=12)

    def test_thermal_collect_uses_full_ray_candidate_without_stagger_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp)
            for name in ('rays1536','rays384'):
                p=work/'reference'/name;p.mkdir(parents=True)
                (p/'summary.json').write_text('{}')
            with patch('wang_staggered.summarize',return_value=dict(steps=2,thermal_gate=True)) as summary, patch('wang_staggered.compare_histories',return_value={}):
                collect(work,thermal_newton=True)
            summary.assert_called_once_with(work/'rays1536Newton')
            report=json.loads((work/'comparison.json').read_text())
            self.assertEqual(report['experiment'],'fullRayThermalNewton')
            self.assertTrue(report['candidate_thermal_gate'])
            self.assertFalse(report['production_approved'])

    def test_ring_phase_preserves_uniform_spacing_and_centroid(self):
        # Rotation changes spatial coverage but not annular Gaussian weights.
        # Each ring remains a closed, uniform quadrature with zero lateral moment.
        n=24
        for ring in range(16):
            angles=[2*math.pi*k/n+(2*math.pi/n)*((ring+.5)/16) for k in range(n)]
            gaps=[(angles[(k+1)%n]-angles[k])%(2*math.pi) for k in range(n)]
            self.assertTrue(all(abs(g-2*math.pi/n)<1e-14 for g in gaps))
            self.assertAlmostEqual(sum(math.cos(t) for t in angles),0,places=12)
            self.assertAlmostEqual(sum(math.sin(t) for t in angles),0,places=12)

    def test_ring_phases_cover_sector_without_shared_spokes(self):
        phases=[(i+.5)/16 for i in range(16)]
        self.assertEqual(len(set(phases)),16)
        self.assertTrue(all(0<p<1 for p in phases))
        self.assertAlmostEqual(sum(phases)/16,.5)

    def test_collect_rejects_missing_runtime_stagger_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp);case=work/'rays384Staggered';case.mkdir()
            (case/'log.vacuumLaserbeamFoam').write_text('End\n')
            with patch('wang_staggered.summarize',return_value=dict(steps=2)):
                with self.assertRaisesRegex(ValueError,'per-call'):collect(work)

    def test_failure_archive_contains_native_build_log(self):
        with tempfile.TemporaryDirectory() as tmp:
            work=Path(tmp)/'wang-staggered-test';work.mkdir()
            (work/'build.log').write_text('compile failure')
            package(work,1)
            report=json.loads((work/'manifest.json').read_text())
            self.assertFalse(report['complete'])
            self.assertIn('comparison.json',report['missing_files'])
            self.assertEqual(report['files'][0]['path'],'build.log')

if __name__=='__main__':unittest.main()
