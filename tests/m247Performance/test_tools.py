import copy
import json
from pathlib import Path
import tempfile
import tarfile
import re
import unittest
from unittest.mock import patch

from collect_probe import SECTIONS, METRICS, compare, read_probe
from prepare_probe import prepare, snapshot_digest
from package_results import package
from collect_thermal_validation import read_field, collect as collect_validation
from localize_field_differences import localize, region
from collect_phase_blend import collect as collect_blend

class ThermalValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
    def tearDown(self):
        self.temp.cleanup()
    def test_ascii_vector_and_uniform_scalar(self):
        p = self.root/'field'
        p.write_text('FoamFile { format ascii; } internalField nonuniform List<vector> 2 ((1 2 3)(4 5 6));')
        self.assertEqual(read_field(p),([1,2,3,4,5,6],3,False))
        p.write_text('FoamFile { format ascii; } internalField uniform 0.5;')
        self.assertEqual(read_field(p),([0.5],1,True))
    def test_truncated_field_rejected(self):
        p = self.root/'field'
        p.write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 3 (1 2);')
        with self.assertRaisesRegex(ValueError,'Truncated'):
            read_field(p)
    def test_binary_format_rejected(self):
        p = self.root/'field'
        p.write_text('FoamFile { format binary; } internalField uniform 1;')
        with self.assertRaisesRegex(ValueError,'ASCII'):
            read_field(p)
    def make_pair(self):
        for variant in ('enthalpyStandard','enthalpyTight'):
            folder = fixture(self.root/variant,variant)
            p = folder/'probe.json'; meta=json.loads(p.read_text())
            meta.update(ranks=1,phase_temperature_tolerance_K=0.001 if variant=='enthalpyTight' else 0.01,
                        epsilon_tolerance=1e-5 if variant=='enthalpyTight' else 1e-4)
            p.write_text(json.dumps(meta))
            p=folder/'run.json'; run=json.loads(p.read_text());run['solver_sha256']='same';p.write_text(json.dumps(run))
            lines=[]
            for i in range(160):
                lines.append(f'THERMAL_RESIDUAL_DIAGNOSTICS time={0.00018+(i+1)*2e-6/160:.12g} boundedEnthalpy=1 phaseTemperatureChecked=1 maxResidual=1e-06 phaseTemperatureResidual_K=0.0005 aboveTolerance=0')
            p=folder/'log.vacuumLaserbeamFoam'
            p.write_text(p.read_text().replace('ranks=48','ranks=1').replace('End','\n'.join(lines)+'\nEnd'))
            state=folder/'processor0/0.000182';state.mkdir(parents=True)
            for name in ('T','epsilon1','alpha.metal','p_rgh'):
                values='1500 1600' if name=='T' else '0 1'
                if name=='T' and variant=='enthalpyStandard': values='1500.1 1600'
                (state/name).write_text(f'FoamFile {{ format ascii; }} internalField nonuniform List<scalar> 2 ({values});')
            (state/'U').write_text('FoamFile { format ascii; } internalField nonuniform List<vector> 2 ((0 0 0)(1 2 3));')
    def test_complete_validation_reports_field_sensitivity(self):
        self.make_pair()
        result = collect_validation(self.root)
        self.assertTrue(result['convergence_gate'])
        self.assertFalse(result['production_approved'])
        temperature=next(f for f in result['fields'] if f['field']=='T')
        self.assertAlmostEqual(temperature['max_abs_difference'],0.1)
        self.assertAlmostEqual(temperature['cell_unweighted_rms_difference'],0.1/(2**0.5))
        self.assertTrue((self.root/'comparison/thermalValidation.json').is_file())
    def test_missing_final_field_does_not_create_report(self):
        self.make_pair()
        (self.root/'enthalpyStandard/processor0/0.000182/U').unlink()
        with self.assertRaises(OSError):
            collect_validation(self.root)
        self.assertFalse((self.root/'comparison').exists())
    def test_localization_preserves_cell_identity_and_region(self):
        self.make_pair()
        result=localize(self.root,top=1)
        self.assertTrue(result['convergence_gate'])
        self.assertFalse(result['production_approved'])
        worst=next(r for r in result['worst_cells'] if r['field']=='T')
        self.assertEqual((worst['rank'],worst['local_cell'],worst['region']),(0,0,'gasBoth'))
        self.assertAlmostEqual(worst['absolute_difference'],0.1)
        self.assertEqual(result['cells'],2)
        counts=next(r for r in result['regions'] if r['region']=='gasBoth' and r['field']=='T')
        self.assertEqual(counts['threshold_counts']['1'],0)
    def test_changed_interface_not_misclassified_as_gas_or_metal(self):
        self.assertEqual(region(0.0,0.02),'interfaceOrChanged')
        self.assertEqual(region(1.0,0.98),'interfaceOrChanged')
        self.assertEqual(region(0.0,0.01),'gasBoth')
        self.assertEqual(region(0.99,1.0),'metalBoth')
    def make_blend_triplet(self):
        self.make_pair()
        import shutil
        for variant,width in (('enthalpyTight',0),('phaseBlendNarrow',0.005),('phaseBlendWide',0.01)):
            if variant!='enthalpyTight':
                shutil.copytree(self.root/'enthalpyTight',self.root/variant)
            folder=self.root/variant
            p=folder/'probe.json';meta=json.loads(p.read_text())
            meta.update(variant=variant,phase_temperature_blend_half_width=width)
            p.write_text(json.dumps(meta))
            p=folder/'log.vacuumLaserbeamFoam'
            text=re.sub(r' phaseBlendHalfWidth=[0-9.]+| phaseOverrideWeight=[0-9.]+','',p.read_text())
            p.write_text(text.replace('boundedEnthalpy=1',f'boundedEnthalpy=1 phaseBlendHalfWidth={width} phaseOverrideWeight=0.5'))
    def test_blend_collection_checks_widths_and_reports_no_approval(self):
        self.make_blend_triplet()
        result=collect_blend(self.root)
        self.assertTrue(result['convergence_gate'])
        self.assertFalse(result['production_approved'])
        self.assertEqual(len(result['comparisons']),2)
    def test_blend_collection_rejects_old_binary_diagnostics(self):
        self.make_blend_triplet()
        p=self.root/'phaseBlendNarrow/log.vacuumLaserbeamFoam'
        p.write_text(p.read_text().replace('phaseBlendHalfWidth=0.005','oldWidth=0.005'))
        with self.assertRaisesRegex(ValueError,'Rebuild'):
            collect_blend(self.root)
        self.assertFalse((self.root/'comparison').exists())

class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.work = self.root/'thermal-test'
        for variant in ('thermalLegacy','enthalpyBounded'):
            folder = self.work/variant
            folder.mkdir(parents=True)
            (folder/'log.vacuumLaserbeamFoam').write_text(variant+'\nEnd\n')
            (folder/'probe.json').write_text('{}')
            (folder/'run.json').write_text('{}')
            (folder/'processor0').mkdir()
            (folder/'processor0/T').write_text('large fields excluded')
    def tearDown(self):
        self.temp.cleanup()
    def test_variant_names_and_manifest_preserve_identity(self):
        output, manifest = package(self.work,exit_code=2)
        with tarfile.open(output) as archive:
            names = archive.getnames()
            self.assertIn('thermal-test_thermalLegacy_solver.log',names)
            self.assertIn('thermal-test_enthalpyBounded_solver.log',names)
            self.assertFalse(any('processor' in n for n in names))
            info = json.load(archive.extractfile('manifest.json'))
            self.assertEqual(info['wrapper_exit_code'],2)
            self.assertTrue(info['missing_files'])
            self.assertEqual(archive.extractfile('thermal-test_thermalLegacy_solver.log').read(),
                             (self.work/'thermalLegacy/log.vacuumLaserbeamFoam').read_bytes())
    def test_existing_archive_is_not_overwritten(self):
        output, _ = package(self.work)
        before = output.read_bytes()
        with self.assertRaisesRegex(ValueError,'already exists'):
            package(self.work)
        self.assertEqual(before,output.read_bytes())
    def test_empty_run_rejected(self):
        empty = self.root/'empty'
        empty.mkdir()
        with self.assertRaisesRegex(ValueError,'recognised'):
            package(empty)

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

class EnthalpyModelTests(unittest.TestCase):
    def test_smooth_phase_override_limits_and_threshold_continuity(self):
        def temperatures(alpha,width):
            weight=(1 if alpha>0.05 else 0) if width==0 else max(0,min(1,(alpha-(0.05-width))/(2*width)))
            if width: weight=weight*weight*(3-2*weight)
            return [(1-weight)*(alpha*m+(1-alpha)*g)+weight*m for m,g in ((1537,1),(1631,10))]
        for width in (0.005,0.01):
            for alpha in (0,0.01,0.04,0.06,1):
                self.assertEqual(temperatures(alpha,width),temperatures(alpha,0))
            below,above=[temperatures(a,width) for a in (0.05-1e-9,0.05+1e-9)]
            self.assertLess(abs(above[0]-below[0]),0.001)
            for i in range(101):
                solidus,liquidus=temperatures(i/100,width)
                self.assertGreater(liquidus,solidus)
        self.assertGreater(temperatures(0.05+1e-9,0)[0]-temperatures(0.05-1e-9,0)[0],1400)
    def test_interface_scalar_model_converges_without_clipped_two_cycle(self):
        # Analytical isolated-cell model, not a CFD regression test.
        cp, latent, span, solidus = 540.0, 9001.0, 94.0, 1537.0
        enthalpy = cp*solidus + 0.5*(latent + cp*span)
        outcomes = []
        for bounded in (False, True):
            fraction = 0.2
            for _ in range(151):
                temperature = (enthalpy-latent*fraction)/cp
                denominator = latent + cp*span if bounded else latent
                fraction = max(0.0,min(1.0,fraction+0.5*cp/denominator*(temperature-solidus-span*fraction)))
            outcomes.append(fraction)
        self.assertIn(outcomes[0],(0.0,1.0))
        self.assertAlmostEqual(outcomes[1],0.5,places=12)

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
    def test_validation_tolerances_and_output_controls_match(self):
        variants = {}
        hashes = []
        for variant in ('enthalpyStandard','enthalpyTight'):
            entries = {}
            with patch('prepare_probe.set_entry',side_effect=lambda path,key,value:entries.update({key:value})):
                meta=prepare(self.source,self.root/variant,180,2,variant)
            variants[variant]=entries
            hashes.append(meta['source_snapshot_sha256'])
            self.assertEqual(entries['writeFormat'],'ascii')
            self.assertEqual(entries['recordRayPaths'],'false')
            self.assertEqual(entries['MELTING/boundedEnthalpyCorrection'],'true')
        self.assertEqual(hashes[0],hashes[1])
        differing={k for k in variants['enthalpyStandard'] if variants['enthalpyStandard'][k]!=variants['enthalpyTight'][k]}
        self.assertEqual(differing,{'MELTING/epsilonTolerance','MELTING/phaseTemperatureTolerance'})
    def test_blend_variants_change_width_only(self):
        variants={};hashes=[]
        for variant in ('enthalpyTight','phaseBlendNarrow','phaseBlendWide'):
            entries={}
            with patch('prepare_probe.set_entry',side_effect=lambda path,key,value:entries.update({key:value})):
                meta=prepare(self.source,self.root/variant,180,0.2,variant)
            variants[variant]=entries;hashes.append(meta['source_snapshot_sha256'])
            self.assertEqual(entries['MELTING/epsilonTolerance'],'1e-5')
            self.assertEqual(entries['MELTING/phaseTemperatureTolerance'],'0.001')
            self.assertEqual(entries['writeFormat'],'ascii')
        self.assertEqual(len(set(hashes)),1)
        differences={k for k in variants['enthalpyTight'] if variants['enthalpyTight'][k]!=variants['phaseBlendNarrow'][k]}
        self.assertEqual(differences,{'MELTING/phaseTemperatureBlendHalfWidth'})
    def test_thermal_probe_changes_only_candidate_correction(self):
        calls = {}
        digests = []
        for variant in ('thermalLegacy', 'enthalpyBounded'):
            entries = {}
            with patch('prepare_probe.set_entry', side_effect=lambda path,key,value:entries.update({key:value})):
                meta = prepare(self.source,self.root/variant,180,0.2,variant)
            calls[variant] = entries
            digests.append(meta['source_snapshot_sha256'])
            self.assertEqual(entries['recordRayPaths'],'false')
            self.assertEqual(entries['MELTING/thermalResidualDiagnostics'],'true')
            self.assertEqual(entries['MELTING/phaseTemperatureTolerance'],'0.01')
        self.assertEqual(digests[0],digests[1])
        differing = [k for k in calls['thermalLegacy'] if calls['thermalLegacy'][k] != calls['enthalpyBounded'][k]]
        self.assertEqual(differing,['MELTING/boundedEnthalpyCorrection'])
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
