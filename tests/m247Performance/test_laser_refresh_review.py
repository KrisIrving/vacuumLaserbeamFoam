import unittest,copy
from laser_refresh_review import validate_refresh

class RefreshReviewTests(unittest.TestCase):
    def records(self,interval):
        return [dict(schema=1,time=i*1e-8,interval=interval,refreshed=1,heldAge_s=0,preRefreshAge_s=0,maxAlphaChange=0,displacementCells=0) for i in range(1,5)]
    def test_baseline_requires_every_step_refresh(self):
        r=self.records(1);self.assertEqual(validate_refresh(r,0,4e-8,4,1)['updates'],4)
        r[2].update(refreshed=0,heldAge_s=1e-8)
        with self.assertRaises(ValueError):validate_refresh(r,0,4e-8,4,1)
    def test_guarded_candidate_counts_updates_and_skips(self):
        r=self.records(2);r[2].update(refreshed=0,heldAge_s=1e-8,preRefreshAge_s=1e-8,maxAlphaChange=.02,displacementCells=.1)
        result=validate_refresh(r,0,4e-8,4,2)
        self.assertEqual(result['held_steps'],1);self.assertEqual(result['updates'],3)
    def test_age_alpha_and_motion_bounds_each_reject_unsafe_hold(self):
        for key,value in [('heldAge_s',26e-9),('maxAlphaChange',.101),('displacementCells',.251)]:
            r=self.records(2);r[2].update(refreshed=0,heldAge_s=1e-8);r[2][key]=value
            with self.assertRaises(ValueError):validate_refresh(r,0,4e-8,4,2)
    def test_first_and_output_samples_must_be_fresh(self):
        for index in (0,1,3):
            r=self.records(2);r[index].update(refreshed=0,heldAge_s=1e-8)
            with self.assertRaises(ValueError):validate_refresh(r,0,4e-8,4,2)
    def test_incomplete_wrong_mode_or_nonmonotonic_log_rejected(self):
        for change in ('missing','mode','time'):
            r=self.records(2)
            if change=='missing':r.pop()
            elif change=='mode':r[2]['interval']=1
            else:r[2]['time']=r[1]['time']
            with self.assertRaises(ValueError):validate_refresh(r,0,4e-8,4,2)

if __name__=='__main__':unittest.main()
