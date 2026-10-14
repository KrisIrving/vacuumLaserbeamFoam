import itertools
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import local_corridor_history as history


class HistoryTest(unittest.TestCase):
    def test_gas_depth_requires_connection_to_top(self):
        with patch.object(history,'SHAPE',(1,3,1)),patch.object(history,'ROI',((0,6e-6),(594e-6,612e-6),(0,6e-6))):
            alpha={(0,0,0):0.,(0,1,0):1.,(0,2,0):0.}
            self.assertEqual(history.gas_cavity_depth(alpha),0.)
            alpha[(0,1,0)]=0.
            self.assertAlmostEqual(history.gas_cavity_depth(alpha),3.)

    def test_volume_uses_liquid_fraction_and_metal_fraction(self):
        def rows(path,width):
            return iter([(0.8,),(1.,)] if path.name=='alpha.metal' else
                        [(1700.,),(1600.,)] if path.name=='T' else [(0.5,),(0.25,)])
        with patch.object(history,'final_state',return_value=Path('unused')), \
             patch.object(history.pilot,'field_rows',side_effect=rows):
            report,_=history.snapshot(Path('unused'),1e-5,2,{0:(0,69,0),1:(1,69,0)})
        self.assertAlmostEqual(report['roi_liquid_fraction_volume_m3']/history.DX**3,.65)
        self.assertAlmostEqual(report['roi_metal_volume_m3']/history.DX**3,1.8)

    def test_initial_match_is_position_based_and_not_volume_only(self):
        a={(0,0,0):(1.,1343.),(1,0,0):(0.,1343.)}
        b={(1,0,0):(1.,1343.),(0,0,0):(0.,1343.)}
        self.assertEqual(history.initial_difference(a,a)['max_alpha_difference'],0.)
        self.assertEqual(history.initial_difference(a,b)['max_alpha_difference'],1.)
        with self.assertRaisesRegex(ValueError,'cell sets'):
            history.initial_difference(a,{(0,0,0):(1.,1343.)})

    def test_fresh_case_uses_resolved_processor_links(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';target=Path(tmp)/'new'
            for name in ('system','constant','processor0'):(source/name).mkdir(parents=True)
            marker=source/'system/controlDict';marker.write_text('original')
            with patch.object(history,'setting'),patch.object(history,'run') as run, \
                 patch.object(Path,'symlink_to') as link:
                history.shadow_case(source,target)
            self.assertEqual(marker.read_text(),'original')
            link.assert_called_once_with((source/'processor0').resolve(),target_is_directory=True)
            self.assertTrue(all('vacuumLaserbeamFoam' not in map(str,call.args[2]) for call in run.call_args_list))
            self.assertEqual(run.call_args_list[0].args[2][0],'reconstructPar')

    def test_metadata_guard_detects_source_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'T';path.write_text('before')
            inventory={str(path):dict(size=path.stat().st_size,mtime_ns=path.stat().st_mtime_ns)}
            self.assertTrue(history.unchanged(inventory))
            path.write_text('changed')
            self.assertFalse(history.unchanged(inventory))

    def test_missing_processors_fails_before_native_commands(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,'48 processor'):
                history.source_inventory(Path(tmp))

    def test_mixed_native_command_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            project=Path(tmp)/'OpenFOAM-v2512';project.mkdir()
            appbin=project/'platforms/bin'
            env=dict(WM_PROJECT_VERSION='v2512',WM_PROJECT_DIR=str(project),FOAM_APPBIN=str(appbin))
            def which(tool):
                return str(project/'wmake/wmake' if tool=='wmake' else appbin/tool)
            with patch.dict(history.os.environ,env),patch.object(history.shutil,'which',side_effect=which):
                self.assertIn('reconstructPar',history.environment()['commands'])
            def mixed(tool):
                return str(Path(tmp)/'OpenFOAM-v2312/reconstructPar') if tool=='reconstructPar' else which(tool)
            with patch.dict(history.os.environ,env),patch.object(history.shutil,'which',side_effect=mixed):
                with self.assertRaisesRegex(ValueError,'mismatched v2512'):
                    history.environment()


if __name__=='__main__':unittest.main()
