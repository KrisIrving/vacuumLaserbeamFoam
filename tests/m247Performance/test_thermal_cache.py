import copy
import unittest
from local_melt_pair import cache_equivalence_gate

class CacheAcceptanceTests(unittest.TestCase):
    def setUp(self):
        perf=dict(steps=834,thermal_correctors_per_step=14.5)
        self.report=dict(measurement_quality_gate=True,
            field_comparisons={label:dict(fields=dict(T=dict(max_abs=0),alpha=dict(max_abs=0))) for label in ('mid','final')},
            diagnostic_differences=[dict(absolute_difference=0)],
            fullMelt=dict(performance=copy.deepcopy(perf)),localMelt=dict(performance=copy.deepcopy(perf)))
    def test_identical_fields_iterations_and_diagnostics_pass(self):
        self.assertTrue(cache_equivalence_gate(self.report))
    def test_field_or_diagnostic_drift_is_not_approved(self):
        for kind in ('field','diagnostic'):
            r=copy.deepcopy(self.report)
            if kind=='field':r['field_comparisons']['mid']['fields']['T']['max_abs']=1e-12
            else:r['diagnostic_differences'][0]['absolute_difference']=1e-12
            self.assertFalse(cache_equivalence_gate(r))
    def test_changed_iteration_count_or_failed_measurement_is_rejected(self):
        for kind in ('iterations','steps','quality'):
            r=copy.deepcopy(self.report)
            if kind=='quality':r['measurement_quality_gate']=False
            else:r['localMelt']['performance']['thermal_correctors_per_step' if kind=='iterations' else 'steps']+=1
            self.assertFalse(cache_equivalence_gate(r))

if __name__=='__main__':unittest.main()
