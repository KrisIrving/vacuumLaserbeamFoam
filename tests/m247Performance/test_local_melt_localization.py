import unittest,tempfile,json,tarfile
from pathlib import Path
from local_melt_localization import localize,regions,align_output_times,optical_calls
from test_local_melt_pair import cell,write
from package_results import package

class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.bounds=dict(xmin=0,xmax=1,ymin=0,ymax=1,zmin=-1,zmax=1)
        self.a=self.root/'a.csv';self.b=self.root/'b.csv'
    def tearDown(self):self.temp.cleanup()
    def test_output_time_roundoff_is_allowed_but_missing_or_shifted_sample_rejected(self):
        r=[dict(time=.000185),dict(time=.00019)];t=[.00018500000000000002,.00019]
        self.assertEqual([x['time'] for x in align_output_times(r,t)],t)
        for wrong in ([.000184,.00019],[.000185]):
            with self.assertRaises(ValueError):align_output_times(r,wrong)

    def test_full_domain_has_no_artificial_cold_cut_region(self):
        a=dict(cell(.000001),y=.000001)
        self.assertIn('coldCutReservoir',regions(a,a,self.bounds))
        self.assertNotIn('coldCutReservoir',regions(a,a,dict(self.bounds,_has_cut=False)))
    def test_optical_counts_follow_actual_refreshes_not_cfd_steps(self):
        perf=dict(performance=dict(steps=834))
        self.assertEqual(optical_calls(perf),834)
        self.assertEqual(optical_calls(dict(perf,laser_refresh=dict(updates=418,held_steps=416))),418)
    def test_incomplete_refresh_counts_are_rejected(self):
        with self.assertRaises(ValueError):
            optical_calls(dict(performance=dict(steps=834),laser_refresh=dict(updates=418,held_steps=415)))

    def test_large_gas_phase_error_is_not_counted_as_liquid_metal(self):
        a=cell(.1,T=1000,alpha=0,epsilon=0);b=dict(a,T=1200,epsilon=1)
        write(self.a,[a]);write(self.b,[b]);r=localize(self.a,self.b,self.bounds)['regions']
        self.assertEqual(r['gasBoth']['fields']['T']['max_abs'],200)
        self.assertEqual(r['gasBoth']['phaseFlipCells'],1)
        self.assertEqual(r['liquidMetalEither']['cells'],0)
    def test_moving_interface_counts_either_run_and_vector_error(self):
        a=cell(.1,alpha=1,epsilon=0);b=dict(a,alpha=.9,epsilon=1,Ux=3,Uy=4)
        write(self.a,[a]);write(self.b,[b]);r=localize(self.a,self.b,self.bounds)['regions']
        self.assertEqual(r['liquidMetalEither']['cells'],1)
        self.assertEqual(r['interfaceEither']['cells'],1)
        self.assertEqual(r['metalEither']['fields']['U']['max_abs'],5)
    def test_missing_or_duplicate_candidate_is_rejected(self):
        a=cell(.1);write(self.a,[a,cell(.2)]);write(self.b,[a])
        with self.assertRaises(ValueError):localize(self.a,self.b,self.bounds)
        write(self.a,[a]);write(self.b,[a,a])
        with self.assertRaises(ValueError):localize(self.a,self.b,self.bounds)
    def test_volume_weighted_rms_uses_region_volume(self):
        a=cell(.1,T=1000,v=1);c=cell(.2,T=1000,v=3)
        write(self.a,[a,c]);write(self.b,[dict(a,T=1002),dict(c,T=1004)])
        r=localize(self.a,self.b,self.bounds)['regions']['all']['fields']['T']
        self.assertAlmostEqual(r['volume_weighted_rms'],13**.5)
    def test_identical_duplicate_solver_log_is_archived_once(self):
        work=self.root/'review';work.mkdir();(work/'fullMelt').mkdir()
        (work/'fullMelt_solver.log').write_text('same solver log')
        (work/'fullMelt/log.vacuumLaserbeamFoam').write_text('same solver log')
        archive,_=package(work,exit_code=1)
        with tarfile.open(archive) as t:
            names=t.getnames();self.assertEqual(len(names),len(set(names)))
    def test_conflicting_duplicate_solver_log_is_rejected(self):
        work=self.root/'review';work.mkdir();(work/'fullMelt').mkdir()
        (work/'fullMelt_solver.log').write_text('one')
        (work/'fullMelt/log.vacuumLaserbeamFoam').write_text('two')
        with self.assertRaises(ValueError):package(work,exit_code=1)

if __name__=='__main__':unittest.main()
