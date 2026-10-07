import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from collect_probe import SECTIONS, METRICS, compare, read_probe
from prepare_probe import prepare, snapshot_digest

def fixture(root, variant='baseline', scale=1):
    root.mkdir()
    metadata=dict(source='/reference',checkpoint='0.00018',start_s=0.00018,
                  end_s=0.000182,duration_us=2,ranks=48,variant=variant,
                  source_snapshot_sha256='same-input')
    (root/'probe.json').write_text(json.dumps(metadata))
    (root/'run.json').write_text(json.dumps(dict(returncode=0,wall_budget_stop=False,
        forced_stop=False,elapsed_wall_s=200*scale)))
    lines=[]
    for i in range(2):
        perf=dict(schema=2,startTime=0.00018+i*1e-6,time=0.000181+i*1e-6,
            ranks=48,steps=80,stepWall_s=13*scale,stepWallMax_s=15*scale,
            thermalCorrectors=160,thermalLimitHits=0,maxThermalCorrectors=2)
        perf.update({k+'_s':scale for k in SECTIONS})
        lines.append('PERF_DIAGNOSTICS '+' '.join(f'{k}={v:.12g}' for k,v in perf.items()))
        diag=dict(time=perf['time']);diag.update({k:10 for k in METRICS})
        lines.append('VACUUM_DIAGNOSTICS '+' '.join(f'{k}={v:.12g}' for k,v in diag.items()))
    (root/'log.vacuumLaserbeamFoam').write_text('\n'.join(lines)+'\nEnd\n')
    return root

class CollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.reference=fixture(self.root/'baseline')
        self.candidate=fixture(self.root/'candidate','noRayPaths',0.5)
    def tearDown(self):
        self.temp.cleanup()
    def test_matched_speedup(self):
        result,rows=compare(read_probe(self.reference),read_probe(self.candidate))
        self.assertTrue(result['diagnostic_pass'])
        self.assertEqual(result['solver_loop_speedup'],2)
        self.assertEqual(len(rows),2*len(METRICS))
    def test_changed_deposition_fails(self):
        p=self.candidate/'log.vacuumLaserbeamFoam'
        p.write_text(p.read_text().replace('depositedPower=10','depositedPower=10.1'))
        result,_=compare(read_probe(self.reference),read_probe(self.candidate))
        self.assertFalse(result['diagnostic_pass'])
    def test_thermal_limit_fails_gate(self):
        p=self.candidate/'log.vacuumLaserbeamFoam'
        p.write_text(p.read_text().replace('thermalLimitHits=0','thermalLimitHits=1'))
        result,_=compare(read_probe(self.reference),read_probe(self.candidate))
        self.assertFalse(result['thermal_limit_gate'])
    def test_truncated_run_rejected(self):
        p=self.candidate/'log.vacuumLaserbeamFoam';p.write_text(p.read_text().replace('End',''))
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            read_probe(self.candidate)
    def test_wall_stop_is_not_a_pass(self):
        p=self.candidate/'run.json';data=json.loads(p.read_text());data['wall_budget_stop']=True;p.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'Incomplete'):
            read_probe(self.candidate)
    def test_timing_gap_rejected(self):
        p=self.candidate/'log.vacuumLaserbeamFoam';p.write_text(p.read_text().replace('startTime=0.000181','startTime=0.0001805'))
        with self.assertRaisesRegex(ValueError,'overlap'):
            read_probe(self.candidate)
    def test_unmatched_snapshot_rejected(self):
        candidate=read_probe(self.candidate);candidate[0]['source_snapshot_sha256']='changed'
        with self.assertRaisesRegex(ValueError,'Unmatched'):
            compare(read_probe(self.reference),candidate)
    def test_non_additive_sections_rejected(self):
        p=self.candidate/'log.vacuumLaserbeamFoam';p.write_text(p.read_text().replace('alpha_s=0.5','alpha_s=1'))
        with self.assertRaisesRegex(ValueError,'reconcile'):
            read_probe(self.candidate)
    def test_missing_physics_rejected(self):
        p=self.candidate/'log.vacuumLaserbeamFoam';p.write_text(p.read_text().replace('Tmax=10','Tmax=nan'))
        with self.assertRaisesRegex(ValueError,'physical diagnostic'):
            read_probe(self.candidate)

class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name);self.source=self.root/'source';self.source.mkdir()
        (self.source/'log.vacuumLaserbeamFoam').write_text('End\n')
        (self.source/'constant').mkdir();(self.source/'system').mkdir()
        for name in ('vacuumProperties','LaserProperties'):
            (self.source/'constant'/name).write_text('original')
        for name in ('controlDict','fvSolution'):
            (self.source/'system'/name).write_text('original')
        (self.source/'constant/timeVsLaserPosition').write_text('( (0 (-0.0001 0.0009595 0)) (0.0002 (0.0001 0.0009595 0)) )')
        (self.source/'constant/timeVsLaserPower').write_text('( (0 350) (0.0002 350) )')
        for i in range(2):
            rank=self.source/f'processor{i}';(rank/'constant/polyMesh').mkdir(parents=True)
            (rank/'constant/polyMesh/points').write_text('mesh')
            state=rank/'0.00018';state.mkdir()
            for name in ('alpha.metal','T','U','p_rgh','epsilon1'):
                (state/name).write_text('restart')
    def tearDown(self):
        self.temp.cleanup()
    def test_copy_is_independent_and_source_unchanged(self):
        before=snapshot_digest(self.source)
        calls=[]
        with patch('prepare_probe.set_entry',side_effect=lambda *args:calls.append(args)):
            result=prepare(self.source,self.root/'probe',180,2,'noRayPaths')
        self.assertEqual(snapshot_digest(self.source),before)
        copied=self.root/'probe/processor0/0.00018/T';copied.write_text('different')
        self.assertEqual((self.source/'processor0/0.00018/T').read_text(),'restart')
        self.assertEqual(result['ranks'],2)
        self.assertIn((self.root/'probe/constant/LaserProperties','recordRayPaths','false'),calls)
    def test_existing_output_preserved(self):
        target=self.root/'probe';target.mkdir();(target/'keep').write_text('keep')
        with self.assertRaisesRegex(ValueError,'already exists'):
            prepare(self.source,target,180,2,'baseline')
        self.assertEqual((target/'keep').read_text(),'keep')
    def test_laser_clamp_rejected(self):
        with self.assertRaisesRegex(ValueError,'laser tables'):
            prepare(self.source,self.root/'probe',180,30,'baseline')
    def test_missing_phase_state_rejected(self):
        (self.source/'processor1/0.00018/epsilon1').unlink()
        with self.assertRaisesRegex(ValueError,'restart field missing'):
            prepare(self.source,self.root/'probe',180,2,'baseline')
    def test_overlapping_output_rejected(self):
        with self.assertRaisesRegex(ValueError,'outside'):
            prepare(self.source,self.source/'probe',180,2,'baseline')

if __name__=='__main__':
    unittest.main()
