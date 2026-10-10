import unittest
from unittest.mock import patch
from packed_broadcast_review import normalized_optical_settings,validate_mode,require_exact_fields,require_same_work,frozen_trace

class PackedGatesTests(unittest.TestCase):
    def test_only_transport_switch_can_differ(self):
        a='power 350;\npackedRayBroadcast false;\n'
        b='power 350;\npackedRayBroadcast true;\n'
        self.assertEqual(normalized_optical_settings(a),normalized_optical_settings(b))
        self.assertNotEqual(normalized_optical_settings(a),normalized_optical_settings(b.replace('350','349')))
        for invalid in ('power 350;',a+a):
            with self.assertRaises(ValueError):normalized_optical_settings(invalid)
    def test_wrong_or_duplicate_mode_is_rejected(self):
        text='PACKED_RAY_BROADCAST schema=1 enabled=1\n'
        validate_mode(text,True)
        for wrong in (text,text+text,''):
            with self.assertRaises(ValueError):validate_mode(wrong,False)
    def test_exact_output_and_work_gates_reject_any_drift(self):
        require_exact_fields([dict(max_abs_difference=0)])
        for wrong in ([],[dict(max_abs_difference=1e-15)]):
            with self.assertRaises(ValueError):require_exact_fields(wrong)
        require_same_work(dict(counts=dict(advancesSum=5)),dict(counts=dict(advancesSum=5)))
        with self.assertRaises(ValueError):require_same_work(dict(counts=dict(advancesSum=5)),dict(counts=dict(advancesSum=4)))
    def test_frozen_state_gate_rejects_time_or_state_advancement(self):
        text='PACKED_RAY_BROADCAST schema=1 enabled=1\nFROZEN_LASER_DIAGNOSTICS schema=1 time=0.00018 calls=1 advancedTime=0 Tchange=0 alphaChange=0 epsilonChange=0 Uchange=0 depositedPower=326\nEnd\n'
        with patch('packed_broadcast_review.summarize',return_value={}),patch('packed_broadcast_review.validate_rank_rows'):
            self.assertEqual(frozen_trace(text,True)['diagnostics']['depositedPower'],326)
            for wrong in (text+'Time = 0.000181\n',text.replace('Tchange=0','Tchange=1e-9'),text.replace('End','')):
                with self.assertRaises(ValueError):frozen_trace(wrong,True)

if __name__=='__main__':unittest.main()
