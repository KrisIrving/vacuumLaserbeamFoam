import unittest,copy
from ray_sampling_review import normalized_settings,validate_ray_count,budget_passes,error_summary

class SamplingGatesTests(unittest.TestCase):
    def test_only_angular_discretization_differs(self):
        a='nRadial 16;\nnAngular 96;\nlaserRadius 43e-6;\n'
        self.assertEqual(normalized_settings(a),normalized_settings(a.replace('96','24')))
        self.assertNotEqual(normalized_settings(a),normalized_settings(a.replace('43e-6','44e-6')))
        for bad in ('',a+a):
            with self.assertRaises(ValueError):normalized_settings(bad)
    def test_actual_ray_totals_are_checked_for_both_modes(self):
        for rays in (1536,384):
            validate_ray_count(dict(counts=dict(initialRaysMean=834*rays)),834,rays)
            with self.assertRaises(ValueError):validate_ray_count(dict(counts=dict(initialRaysMean=834*1536+1)),834,rays)
    def test_extended_pair_uses_report_times_not_short_probe_times(self):
        inv=dict(reference=dict(liquid_volume_m3=1),candidate=dict(liquid_volume_m3=1))
        report=dict(sample_times_s=(.00019,.0002),measurement_quality_gate=True,
            field_comparisons={x:dict(inventories=inv) for x in ('mid','final')},
            keyhole_comparisons=[dict(time_s=t,reference_depth_um=100,depth_difference_um=1) for t in (.00019,.0002)],
            diagnostic_differences=[dict(time=t,metric='Tmax',relative_difference=.03) for t in (.00019,.0002)])
        result=error_summary(report)
        self.assertEqual([x['time_s'] for x in result['snapshots']],[.00019,.0002])
        self.assertTrue(result['agreed_error_budget_gate'])

    def test_both_samples_must_meet_user_budget_including_tmax(self):
        snapshots=[dict(keyhole_depth_difference_percent=5,liquid_volume_difference_percent=5,diagnostic_difference_percent=dict(Tmax=10)) for _ in range(2)]
        self.assertTrue(budget_passes(snapshots,True))
        self.assertFalse(budget_passes(snapshots,False))
        self.assertFalse(budget_passes(snapshots[:1],True))
        for metric in ('keyhole_depth_difference_percent','liquid_volume_difference_percent','Tmax'):
            for invalid in (10.01,None,float('nan')):
                s=copy.deepcopy(snapshots)
                if metric=='Tmax':s[0]['diagnostic_difference_percent'][metric]=invalid
                else:s[0][metric]=invalid
                self.assertFalse(budget_passes(s,True))

if __name__=='__main__':unittest.main()
