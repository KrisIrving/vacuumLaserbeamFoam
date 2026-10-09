import csv
import json
import math
from pathlib import Path
import tempfile
import unittest
from local_melt_pair import compare_fields, plan_window, native_snapshot, active, subset_command
from package_results import package


def cell(x,T=1500,v=1,alpha=1,epsilon=0):
    return dict(x=x,y=.0005,z=0,volume=v,T=T,alpha=alpha,epsilon=epsilon,Ux=0,Uy=0,Uz=0,p_rgh=0)


def write(path,data):
    with path.open('w',encoding='utf-8',newline='') as stream:
        w=csv.DictWriter(stream,fieldnames=list(data[0]));w.writeheader();w.writerows(data)


class LocalMeltPairTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.bounds=dict(xmin=0,xmax=.0002,ymin=0,ymax=.001,zmin=-.001,zmax=.001)
        self.reference=self.root/'reference.csv';self.candidate=self.root/'candidate.csv'
    def tearDown(self):self.temp.cleanup()
    def test_subset_uses_control_time_without_unsupported_selection_flags(self):
        cmd=subset_command(self.root,'0.00018','-case dir -patch name -overwrite','startTime;','0.00018;')
        self.assertNotIn('-time',cmd);self.assertNotIn('-latestTime',cmd);self.assertNotIn('-resultTime',cmd)
        self.assertEqual(cmd[cmd.index('-patch')+1],'localCut')
    def test_subset_rejects_wrong_or_implicit_checkpoint_before_mutation(self):
        for mode,time in [('latestTime','0.00018'),('startTime','0'),('startTime','nan')]:
            with self.subTest(mode=mode,time=time),self.assertRaises(ValueError):
                subset_command(self.root,'0.00018','-case dir -patch name -overwrite',mode,time)
    def test_subset_requires_installed_options_with_exact_option_names(self):
        for help_text in ('-case dir -patches names -overwrite','-case dir -patch name','-patch name -overwrite'):
            with self.subTest(help=help_text),self.assertRaises(ValueError):
                subset_command(self.root,'0.00018',help_text,'startTime','0.00018')

    def test_coordinate_order_independent_initial_identity(self):
        data=[cell(.0001),cell(.0002),cell(.0003)]
        write(self.reference,data);write(self.candidate,data[:2][::-1])
        r=compare_fields(self.reference,self.candidate,self.bounds,True)
        self.assertEqual(r['cells'],2);self.assertEqual(r['fields']['T']['max_abs'],0)
    def test_volume_weighted_error_and_same_roi_inventory(self):
        a=[cell(.0001,1600,1),cell(.0002,1700,3),cell(.0003,4000,100)]
        b=[cell(.0001,1610,1),cell(.0002,1720,3)]
        write(self.reference,a);write(self.candidate,b)
        r=compare_fields(self.reference,self.candidate,self.bounds)
        self.assertAlmostEqual(r['fields']['T']['volume_weighted_rms'],math.sqrt(325))
        self.assertEqual(r['inventories']['reference']['metal_volume_m3'],4)
        self.assertEqual(r['inventories']['reference']['molten_cells'],1)
    def test_initial_internal_change_is_rejected(self):
        write(self.reference,[cell(.0001)]);write(self.candidate,[cell(.0001,1501)])
        with self.assertRaises(ValueError):compare_fields(self.reference,self.candidate,self.bounds,True)
    def test_missing_duplicate_extra_geometry_or_changed_volume_rejected(self):
        write(self.reference,[cell(.0001),cell(.0002)])
        for data in ([cell(.0001)],[cell(.0001),cell(.0001)],[cell(.0001),cell(.0002),cell(.0003)],[cell(.0001,v=2),cell(.0002)]):
            write(self.candidate,data)
            with self.subTest(data=data),self.assertRaises(ValueError):compare_fields(self.reference,self.candidate,self.bounds)
    def test_gas_numerical_phase_does_not_select_cold_powder(self):
        self.assertFalse(active(cell(0,300,alpha=.02,epsilon=1)))
        self.assertTrue(active(cell(0,1600,alpha=1,epsilon=.5)))
        r=cell(0,300,alpha=0,epsilon=1);r['Ux']=20;self.assertTrue(active(r))
    def test_selection_retains_height_laser_future_and_buffer(self):
        data=[cell(i*8e-6,1700 if 45<=i<=55 else 300,v=1e-15) for i in range(100)]
        write(self.reference,data)
        snapshot=dict(cells=100,xmin=0,xmax=.0008,ymin=0,ymax=.00096,zmin=-.00032,zmax=.00032)
        r=plan_window(self.reference,snapshot,[(.0004,.000959,0),(.0005,.000959,0)],halo=180e-6)
        self.assertEqual(r['bounds']['ymax'],.00096);self.assertLess(r['cell_fraction'],1)
        self.assertGreaterEqual(r['bounds']['xmax'],.0005+180e-6)
    def test_no_reduction_is_rejected(self):
        write(self.reference,[cell(i*8e-6,1700) for i in range(100)])
        snapshot=dict(cells=100,xmin=0,xmax=.0008,ymin=.00045,ymax=.001,zmin=-.00005,zmax=.00005)
        details={}
        with self.assertRaises(ValueError):plan_window(self.reference,snapshot,[(.0004,0,0)],details=details)
        self.assertEqual(details['selected_cells'],100)
        self.assertEqual(details['seed_categories']['thermal_phase']['cells'],100)
    def test_fast_spread_saturates_xz_but_cold_bottom_can_be_removed(self):
        data=[]
        for y in (.0001,.0002,.0003,.0004,.0005,.0006,.0007,.0008):
            for x in (-.00048,-.00024,0,.00024):
                for z in (-.00028,0,.00028):
                    r=cell(x,300,alpha=1);r['y']=y;r['z']=z
                    if y>=.0004:r['Ux']=2
                    data.append(r)
        write(self.reference,data)
        snapshot=dict(cells=96,xmin=-.00052,xmax=.00032,ymin=0,ymax=.00096,zmin=-.00032,zmax=.00032)
        plan=plan_window(self.reference,snapshot,[(.00008,.000959,0)])
        self.assertEqual(plan['bounds']['xmin'],snapshot['xmin'])
        self.assertEqual(plan['bounds']['zmax'],snapshot['zmax'])
        self.assertGreater(plan['bounds']['ymin'],0)
        self.assertEqual(plan['bounds']['ymax'],snapshot['ymax'])
        self.assertLess(plan['selected_cells'],96)
        for r in data:
            if active(r):self.assertGreaterEqual(r['y'],plan['bounds']['ymin']+96e-6-1e-15)

    def test_native_schema_requires_end_and_expected_time(self):
        text='M247_LOCAL_MELT_SNAPSHOT schema=1 time=.00018 cells=100 xmin=0 xmax=1 ymin=0 ymax=1 zmin=0 zmax=1 cutFaces=10 activeCutFaces=0 cutMetalTmax=300 cutMetalEpsilonMax=0 cutUmax=.1 productionApproved=0\nEnd\n'
        self.assertEqual(native_snapshot(text,.00018)['cells'],100)
        for bad in (text.replace('End',''),text.replace('schema=1','schema=2'),text.replace('time=.00018','time=.00019')):
            with self.assertRaises(ValueError):native_snapshot(bad,.00018)
    def test_partial_pair_is_packaged_with_unique_variant_names(self):
        work=self.root/'local-melt-pair-test';work.mkdir()
        (work/'localMeltPairReview.json').write_text(json.dumps(dict(complete=False,error='build failed')))
        (work/'build.log').write_text('fatal error')
        archive,manifest=package(work,exit_code=1)
        self.assertTrue(archive.exists());self.assertEqual(manifest['wrapper_exit_code'],1)
        self.assertIn('localMeltPairReview.json',[r['source'] for r in manifest['files']])
    def test_new_wrapper_lf_and_required_models_not_replaced(self):
        script=Path(__file__).with_name('RunLocalMeltPair').read_bytes()
        self.assertTrue(script.startswith(b'#!/bin/bash\n'));self.assertNotIn(b'\r',script)
        self.assertIn(b'check_solver.py --laser-profile',script)
        self.assertNotIn(b'regionalThermophysics',script)


if __name__=='__main__':unittest.main()
