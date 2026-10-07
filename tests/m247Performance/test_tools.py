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
from check_solver import inspect_solver, inspect_laser_library, MARKERS
from collect_laser_profile import collect as collect_laser, summarize as summarize_laser, validate_rank_rows, RANK_COUNTS, STAGES
from localize_phase_blend import inspect as inspect_blend

class SolverPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.binary = self.root/'vacuumLaserbeamFoam'
    def tearDown(self):
        self.temp.cleanup()
    def test_old_solver_rejected(self):
        self.binary.write_bytes(b'old executable')
        result = inspect_solver(self.binary, self.root)
        self.assertFalse(result['passed'])
        self.assertEqual(len(result['missing_markers']), 2)
    def test_new_solver_markers_and_build_target(self):
        self.binary.write_bytes(b'\x00'.join(MARKERS))
        result = inspect_solver(self.binary, self.root)
        self.assertTrue(result['passed'])
        self.assertEqual(result['solver'], str(self.binary.resolve()))
    def test_shadowed_solver_and_missing_environment_rejected(self):
        self.binary.write_bytes(b'\x00'.join(MARKERS))
        self.assertFalse(inspect_solver(self.binary, self.root/'other')['passed'])
        self.assertFalse(inspect_solver(self.binary, None)['passed'])
    def test_failed_preflight_packaged_without_any_cfd(self):
        self.binary.write_bytes(b'old executable')
        (self.root/'solverCheck.json').write_text(json.dumps(inspect_solver(self.binary,self.root)))
        output, manifest = package(self.root, self.root.parent/(self.root.name+'.tar.gz'), 1)
        try:
            self.assertEqual(manifest['variants'], [])
            self.assertEqual(manifest['wrapper_exit_code'], 1)
            with tarfile.open(output) as archive:
                result = json.load(archive.extractfile(self.root.name+'_solverCheck.json'))
                self.assertFalse(result['passed'])
        finally:
            output.unlink()
    def test_loader_shadow_and_old_laser_library_are_rejected(self):
        import subprocess
        library=self.root/'liblaserHeatSource.so'
        markers=b'LASER_PERF_DIAGNOSTICS schema=2 time=\x00LASER_RANK_DIAGNOSTICS schema=2 time=\x00RAY_TRAVERSAL_DIAGNOSTICS schema=1 cached='
        library.write_bytes(markers)
        resolved=str(library.resolve())
        with patch('check_solver.subprocess.run',return_value=subprocess.CompletedProcess([],0,'liblaserHeatSource.so => '+resolved,'')):
            self.assertTrue(inspect_laser_library(self.binary,self.root)['passed'])
            self.assertFalse(inspect_laser_library(self.binary,self.root,seed_search=True)['passed'])
            library.write_bytes(markers+b'\x00CARTESIAN_SEED_DIAGNOSTICS schema=1 enabled=')
            self.assertTrue(inspect_laser_library(self.binary,self.root,seed_search=True)['passed'])
            library.write_bytes(b'LASER_PERF_DIAGNOSTICS schema=1 time=')
            self.assertFalse(inspect_laser_library(self.binary,self.root)['passed'])
        library.write_bytes(markers)
        with patch('check_solver.subprocess.run',return_value=subprocess.CompletedProcess([],0,'liblaserHeatSource.so => /different/liblaserHeatSource.so','')):
            self.assertFalse(inspect_laser_library(self.binary,self.root)['passed'])

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
    def test_phase_localization_reports_both_pairs_and_preserves_outputs(self):
        self.make_blend_triplet()
        field=self.root/'phaseBlendWide/processor0/0.000182/T'
        field.write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (1501 1600);')
        result=inspect_blend(self.root)
        self.assertTrue(result['convergence_gate'])
        self.assertFalse(result['production_approved'])
        self.assertEqual(len(result['comparisons']),2)
        worst=next(r for r in result['comparisons'][1]['worst_cells'] if r['field']=='T')
        self.assertEqual((worst['rank'],worst['local_cell'],worst['region']),(0,0,'gasBoth'))
        self.assertAlmostEqual(worst['absolute_difference'],1)
        report=self.root/'comparison/phaseBlendLocalization.json'
        before=report.read_bytes()
        with self.assertRaisesRegex(ValueError,'already exist'): inspect_blend(self.root)
        self.assertEqual(report.read_bytes(),before)
        archive,manifest=package(self.root,self.root.parent/(self.root.name+'.tar.gz'),0)
        try:
            self.assertTrue(any(x['source']=='comparison/phaseBlendLocalization.json' for x in manifest['files']))
        finally:
            archive.unlink()
    def test_phase_localization_rejects_runtime_width_mismatch_before_report(self):
        self.make_blend_triplet()
        log=self.root/'phaseBlendWide/log.vacuumLaserbeamFoam'
        log.write_text(log.read_text().replace('phaseBlendHalfWidth=0.01','phaseBlendHalfWidth=0'))
        with self.assertRaisesRegex(ValueError,'runtime phase'): inspect_blend(self.root)
        self.assertFalse((self.root/'comparison').exists())
    def make_laser_pair(self):
        self.make_pair()
        import shutil
        rows=[]
        for time in (0.000181,0.000182):
            row=dict(schema=2,time=time,ranks=1,total_s=0.4,totalMax_s=0.4,
                traceSearchSampleSum_s=0.001,traceSearchSamplesSum=1,searchSampleStride=128,
                callsMean=80,initialRaysMean=80,exchangeRoundsMean=80,ownershipChecksSum=80,
                localSegmentsSum=80,advancesSum=80,traceSearchCallsSum=160,interfaceEventsSum=10,bulkEventsSum=2,
                mergeCallsSum=1,mergeXRaysSum=40,mergeYRaysSum=40,mergeAppendsSum=20)
            row.update({k+s:0.05 for k in STAGES for s in ('_s','Max_s')})
            row.update({k+s:v for k,v in (('exchangeCopy',0.01),('gather',0.03),('broadcast',0.005),('merge',0.02)) for s in ('_s','Max_s')})
            rows.append(row)
        for variant,enabled in (('laserProfileOff',False),('laserProfileOn',True)):
            folder=self.root/variant
            shutil.copytree(self.root/'enthalpyTight',folder)
            p=folder/'probe.json';meta=json.loads(p.read_text())
            meta.update(variant=variant,phase_temperature_blend_half_width=0,laser_performance_diagnostics=enabled)
            p.write_text(json.dumps(meta))
            p=folder/'run.json';run=json.loads(p.read_text());run['laser_library_sha256']='same-lib';p.write_text(json.dumps(run))
            p=folder/'log.vacuumLaserbeamFoam'
            text=p.read_text().replace('boundedEnthalpy=1','boundedEnthalpy=1 phaseBlendHalfWidth=0')
            if enabled:
                records=[]
                for row in rows:
                    rank=dict(schema=2,time=row['time'],rank=0,calls=80,rounds=80)
                    rank.update({k:row[k] for k in ('trace_s','ownership_s','exchange_s','exchangeCopy_s','gather_s','broadcast_s','merge_s')})
                    rank.update({k:row[aggregate] for k,aggregate in RANK_COUNTS.items()})
                    records.extend(prefix+' '+' '.join(f'{k}={v}' for k,v in data.items())
                                   for prefix,data in (('LASER_PERF_DIAGNOSTICS',row),('LASER_RANK_DIAGNOSTICS',rank)))
                text=text.replace('End','\n'.join(records)+'\nEnd')
            p.write_text(text)
        return rows
    def test_laser_profile_coverage_equivalence_and_archive(self):
        self.make_laser_pair()
        result=collect_laser(self.root)
        self.assertTrue(result['regression_gate'])
        self.assertFalse(result['production_approved'])
        self.assertEqual(result['laser_profile']['counts']['traceSearchCallsSum'],320)
        self.assertEqual(result['laser_profile']['rank_totals'][0]['searches'],320)
        self.assertAlmostEqual(sum(r['mean_s'] for r in result['laser_profile']['exchange_details']),0.13)
        self.assertAlmostEqual(sum(r['mean_fraction'] for r in result['laser_profile']['stages']),1)
        archive,manifest=package(self.root,self.root.parent/(self.root.name+'.tar.gz'),0)
        try:
            self.assertTrue(any(x['source']=='comparison/laserProfileReview.json' for x in manifest['files']))
            for name in ('laserRankWork.csv','laserExchangeDetails.csv'):
                self.assertTrue(any(x['source']=='comparison/'+name for x in manifest['files']))
        finally: archive.unlink()
    def test_profile_field_change_fails_equivalence(self):
        self.make_laser_pair()
        (self.root/'laserProfileOn/processor0/0.000182/T').write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (1501 1600);')
        result=collect_laser(self.root)
        self.assertFalse(result['regression_gate'])
    def test_incomplete_or_nonadditive_laser_records_rejected(self):
        rows=self.make_laser_pair()
        for change in ({'trace_s':0.5},{'totalMax_s':0.1},{'traceSearchCallsSum':159},{'schema':1},
                       {'gather_s':0.06},{'merge_s':0.04},{'mergeMax_s':0.001},{'mergeAppendsSum':41}):
            edited=copy.deepcopy(rows);edited[0].update(change)
            with self.assertRaises(ValueError): summarize_laser(edited,[0.000181,0.000182],1,160)
        with self.assertRaisesRegex(ValueError,'cover'): summarize_laser(rows[:1],[0.000181,0.000182],1,160)
        with self.assertRaisesRegex(ValueError,'all solver steps'): summarize_laser(rows,[0.000181,0.000182],1,161)
    def test_missing_rank_records_rejected_before_output(self):
        self.make_laser_pair()
        log=self.root/'laserProfileOn/log.vacuumLaserbeamFoam'
        log.write_text('\n'.join(line for line in log.read_text().splitlines() if not line.startswith('LASER_RANK_DIAGNOSTICS')))
        with self.assertRaisesRegex(ValueError,'Incomplete laser rank'): collect_laser(self.root)
        self.assertFalse((self.root/'comparison').exists())
    def make_traversal_pair(self):
        self.make_laser_pair()
        (self.root/'cachedSearchTest.log').write_text('CACHED_SEARCH_TEST checks=100 mismatches=0\n')
        import shutil
        for name,enabled in (('rayTraversalReference',False),('rayTraversalCached',True)):
            case=self.root/name
            shutil.copytree(self.root/'laserProfileOn',case)
            p=case/'probe.json';meta=json.loads(p.read_text())
            meta.update(variant=name,cached_ray_traversal=enabled)
            p.write_text(json.dumps(meta))
            p=case/'log.vacuumLaserbeamFoam'
            p.write_text(f'RAY_TRAVERSAL_DIAGNOSTICS schema=1 cached={int(enabled)}\n'+p.read_text())
            for field in ('Deposition','rayQ','rayNumber'):
                (case/'processor0/0.000182'/field).write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (0 1);')
    def test_traversal_equivalence_and_no_unmeasured_speedup(self):
        self.make_traversal_pair()
        result=collect_laser(self.root,traversal=True)
        self.assertTrue(result['regression_gate'])
        self.assertTrue(result['work_counter_gate'])
        self.assertFalse(result['performance_gate'])
        self.assertEqual(len(result['fields']),8)
        archive,manifest=package(self.root,self.root.parent/(self.root.name+'.tar.gz'),0)
        try:
            self.assertTrue(any(x['source']=='comparison/rayTraversalReview.json' for x in manifest['files']))
            self.assertIn('rayTraversalCached',manifest['variants'])
        finally: archive.unlink()
    def test_broader_traversal_validation_accepts_matched_two_us(self):
        self.make_traversal_pair()
        result=collect_laser(self.root,traversal=True,validation=True)
        self.assertTrue(result['regression_gate'])
        self.assertEqual(result['validation_scope'],'180-182us')
        self.assertFalse(result['production_approved'])
    def test_broader_validation_rejects_short_probe_metadata(self):
        self.make_traversal_pair()
        for name in ('rayTraversalReference','rayTraversalCached'):
            p=self.root/name/'probe.json'
            meta=json.loads(p.read_text());meta['duration_us']=0.2
            p.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError,'exactly 180'):
            collect_laser(self.root,traversal=True,validation=True)
        self.assertFalse((self.root/'comparison').exists())
    def test_broader_validation_requires_traversal_pair(self):
        with self.assertRaisesRegex(ValueError,'requires the paired traversal'):
            collect_laser(self.root,validation=True)
    def make_seed_pair(self):
        self.make_traversal_pair()
        (self.root/'cachedSearchTest.log').write_text('CACHED_SEARCH_TEST checks=200 mismatches=0 cartesianChecks=100 fastAccepts=25 eligibleCells=2\n')
        for old,new,enabled in (('rayTraversalReference','raySeedReference',False),('rayTraversalCached','raySeedCached',True)):
            case=self.root/old;case.rename(self.root/new);case=self.root/new
            p=case/'probe.json';meta=json.loads(p.read_text())
            meta.update(variant=new,cached_ray_traversal=True,cartesian_ray_seed_search=enabled)
            p.write_text(json.dumps(meta))
            p=case/'log.vacuumLaserbeamFoam'
            p.write_text(f'CARTESIAN_SEED_DIAGNOSTICS schema=1 enabled={int(enabled)}\n'+p.read_text().replace('schema=1 cached=0','schema=1 cached=1'))
    def test_seed_pair_preserves_field_and_work_gates(self):
        self.make_seed_pair()
        result=collect_laser(self.root,traversal=True,validation=True,seed_search=True)
        self.assertTrue(result['regression_gate'])
        self.assertTrue(result['work_counter_gate'])
        self.assertFalse(result['performance_gate'])
        self.assertEqual(result['optimization'],'cartesian seed interior')
        self.assertFalse(result['production_approved'])
    def test_seed_pair_rejects_wrong_runtime_and_unexercised_shortcut(self):
        self.make_seed_pair()
        p=self.root/'raySeedCached/log.vacuumLaserbeamFoam';original=p.read_text()
        p.write_text(original.replace('schema=1 enabled=1','schema=1 enabled=0'))
        with self.assertRaisesRegex(ValueError,'Cartesian seed search mode'):
            collect_laser(self.root,traversal=True,seed_search=True)
        p.write_text(original)
        (self.root/'cachedSearchTest.log').write_text('CACHED_SEARCH_TEST checks=200 mismatches=0 cartesianChecks=100 fastAccepts=0 eligibleCells=2\n')
        with self.assertRaisesRegex(ValueError,'not exercised'):
            collect_laser(self.root,traversal=True,seed_search=True)
        self.assertFalse((self.root/'comparison').exists())
    def test_traversal_mode_rejects_old_runtime(self):
        self.make_traversal_pair()
        p=self.root/'rayTraversalCached/log.vacuumLaserbeamFoam'
        p.write_text(p.read_text().replace('cached=1','cached=0'))
        with self.assertRaisesRegex(ValueError,'runtime cached traversal'): collect_laser(self.root,traversal=True)
        self.assertFalse((self.root/'comparison').exists())
    def make_partition_pair(self):
        import shutil
        from ray_partition import NAMES, FIELDS, require_initial_equal
        self.make_seed_pair()
        for index,(old,new) in enumerate(zip(('raySeedReference','raySeedCached'),NAMES)):
            case=self.root/old;case.rename(self.root/new);case=self.root/new
            p=case/'probe.json';meta=json.loads(p.read_text());meta.update(variant=new,ranks=48,cartesian_ray_seed_search=False)
            p.write_text(json.dumps(meta))
            mesh=case/'constant/polyMesh';mesh.mkdir(parents=True)
            for part in ('points','faces','owner','neighbour','boundary'): (mesh/part).write_text('same global mesh '+part)
            for time in ('0.00018','0.000182'):
                folder=case/time;folder.mkdir()
                for name in FIELDS: shutil.copyfile(case/'processor0/0.000182'/name,folder/name)
            p=case/'log.vacuumLaserbeamFoam';lines=[]
            for line in p.read_text().splitlines():
                if line.startswith('LASER_PERF_DIAGNOSTICS '):
                    row=parse_records_for_test(line,'LASER_PERF_DIAGNOSTICS')
                    row['ranks']=48;row['initialRaysMean']=row['callsMean']*1536
                    for key in RANK_COUNTS.values(): row[key]*=48
                    row['ownershipChecksSum']*=48
                    lines.append('LASER_PERF_DIAGNOSTICS '+' '.join(f'{k}={v}' for k,v in row.items()))
                elif line.startswith('LASER_RANK_DIAGNOSTICS '):
                    row=parse_records_for_test(line,'LASER_RANK_DIAGNOSTICS')
                    for rank in range(48):
                        data=dict(row,rank=rank)
                        if index and rank<2:
                            change=2 if rank==0 else -2
                            data['advances']+=change;data['searches']+=change
                        lines.append('LASER_RANK_DIAGNOSTICS '+' '.join(f'{k}={v}' for k,v in data.items()))
                else: lines.append(line.replace('enabled=1','enabled=0').replace('ranks=1 ','ranks=48 '))
            p.write_text('\n'.join(lines)+'\n')
        (self.root/'initialPartitionCheck.json').write_text(json.dumps(require_initial_equal(*(self.root/n for n in NAMES))))
    def test_partition_compares_global_fields_without_equal_rank_work(self):
        from ray_partition import collect
        self.make_partition_pair()
        result=collect(self.root)
        self.assertTrue(result['regression_gate'])
        self.assertFalse(result['performance_gate'])
        self.assertEqual(len(result['fields']),7)
        self.assertNotEqual(result['reference_laser_profile']['rank_totals'][0]['searches'],result['laser_profile']['rank_totals'][0]['searches'])
        archive,manifest=package(self.root,self.root.parent/(self.root.name+'.tar.gz'))
        try:
            self.assertIn('rayPartitionWeighted',manifest['variants'])
            self.assertTrue(any(e['source']=='comparison/rayPartitionReview.json' for e in manifest['files']))
        finally: archive.unlink()
    def make_corrected_transient_pair(self,impact=False):
        import shutil
        self.make_partition_pair()
        names=('rayImpactLegacy','rayImpactCorrected') if impact else ('rayTraversalReference','rayTraversalCached')
        common=(self.root/'rayPartitionReference/log.vacuumLaserbeamFoam').read_text()
        work='RAY_HANDOFF_DIAGNOSTICS schema=1 enabled=1\nRAY_TERMINATION_DIAGNOSTICS schema=1 enabled=1\n'
        for i in range(160):
            time=.00018+(i+1)*2e-6/160
            work+=f'RAY_HANDOFF_WORK schema=1 time={time:.15g} crossings=10 resumed=9\n'
            work+=f'RAY_TERMINATION_WORK schema=1 time={time:.15g} threshold=1e-6 cutoffRays=10 discardedPower=5e-6\n'
        for index,(old,new) in enumerate(zip(('rayPartitionReference','rayPartitionWeighted'),names)):
            case=self.root/old;case.rename(self.root/new);case=self.root/new
            enabled=bool(index) if impact else True
            p=case/'probe.json';meta=json.loads(p.read_text());meta.update(variant=new,cached_ray_traversal=True if impact else bool(index),preserve_ray_handoff_sample=enabled,consistent_ray_termination=enabled);p.write_text(json.dumps(meta))
            correction=work if enabled else 'RAY_HANDOFF_DIAGNOSTICS schema=1 enabled=0\nRAY_TERMINATION_DIAGNOSTICS schema=1 enabled=0\n'
            (case/'log.vacuumLaserbeamFoam').write_text(common.replace('cached=1',f'cached={1 if impact else index}')+correction)
            for rank in range(1,48): shutil.copytree(case/'processor0',case/f'processor{rank}')
        (self.root/'cachedSearchTest.log').write_text('CACHED_SEARCH_TEST checks=100 mismatches=0\nRAY_PACKET_TEST schema=1 failures=0\n')
    def test_corrected_transient_collection_accepts_complete_matched_pair(self):
        self.make_corrected_transient_pair()
        result=collect_laser(self.root,traversal=True,validation=True,corrected_rays=True)
        self.assertTrue(result['regression_gate'] and result['corrected_ray_work_gate'])
        self.assertFalse(result['production_approved'])
    def test_physics_impact_keeps_equality_failure_and_localizes_differences(self):
        self.make_corrected_transient_pair(impact=True)
        (self.root/'rayImpactCorrected/processor0/0.000182/T').write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (100 102);')
        result=collect_laser(self.root,traversal=True,validation=True,physics_impact=True)
        self.assertTrue(result['execution_gate'])
        self.assertFalse(result['legacy_equivalence_gate'])
        self.assertFalse(result['production_approved'])
        self.assertIsNone(result['performance_gate'])
        self.assertTrue((self.root/'comparison/fieldLocalization.json').is_file())
    def test_partition_global_field_change_fails_regression(self):
        from ray_partition import collect
        self.make_partition_pair()
        (self.root/'rayPartitionWeighted/0.000182/rayQ').write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (0 2);')
        self.assertFalse(collect(self.root)['regression_gate'])
    def test_partition_initial_field_and_mesh_changes_rejected(self):
        from ray_partition import require_initial_equal, NAMES
        self.make_partition_pair();cases=[self.root/n for n in NAMES]
        p=cases[1]/'0.00018/T';original=p.read_text();p.write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (100 200);')
        with self.assertRaisesRegex(ValueError,'initial fields'): require_initial_equal(*cases)
        p.write_text(original);(cases[1]/'constant/polyMesh/points').write_text('changed order')
        with self.assertRaisesRegex(ValueError,'mesh/order'): require_initial_equal(*cases)
    def make_frozen_pair(self):
        import shutil
        from frozen_laser import NAMES, INPUTS, check_inputs
        from collect_probe import parse_records
        self.make_partition_pair()
        for old,new in zip(('rayPartitionReference','rayPartitionWeighted'),NAMES):
            case=self.root/old;case.rename(self.root/new);case=self.root/new
            p=case/'probe.json';meta=json.loads(p.read_text());meta.update(variant=new,frozen_optics=True,frozen_time_s=.00018)
            p.write_text(json.dumps(meta))
            for name,original in zip(INPUTS,('alpha.metal','U','T')):
                shutil.copyfile(case/'0.00018'/original,case/'0.00018'/name)
            p=case/'log.vacuumLaserbeamFoam';text=p.read_text()
            record=parse_records(text,'LASER_PERF_DIAGNOSTICS')[0]
            record.update(time=.00018,callsMean=1,initialRaysMean=1536)
            lines=['RAY_TRAVERSAL_DIAGNOSTICS schema=1 cached=1','CARTESIAN_SEED_DIAGNOSTICS schema=1 enabled=0',
                'LASER_PERF_DIAGNOSTICS '+' '.join(f'{k}={v}' for k,v in record.items())]
            for row in parse_records(text,'LASER_RANK_DIAGNOSTICS')[:48]:
                row.update(time=.00018,calls=1)
                lines.append('LASER_RANK_DIAGNOSTICS '+' '.join(f'{k}={v}' for k,v in row.items()))
            lines+=['FROZEN_LASER_DIAGNOSTICS schema=1 time=0.00018 calls=1 advancedTime=0 Tchange=0 alphaChange=0 epsilonChange=0 Uchange=0 depositedPower=327','End']
            p.write_text('\n'.join(lines)+'\n')
        (self.root/'frozenInputCheck.json').write_text(json.dumps(check_inputs(*(self.root/n for n in NAMES))))
        reference=self.root/NAMES[0]
        (reference/'capture.log').write_text('FROZEN_LASER_CAPTURE schema=1 time=0.00018 calls=0\nEnd\n')
        shutil.copyfile(reference/'run.json',reference/'captureRun.json')
    def test_frozen_optics_accepts_shared_inputs_and_packages_distinct_evidence(self):
        from frozen_laser import collect
        self.make_frozen_pair();result=collect(self.root)
        self.assertTrue(result['optical_partition_gate'])
        self.assertEqual(result['transient_steps'],0)
        archive,manifest=package(self.root,self.root.parent/(self.root.name+'.tar.gz'))
        try:
            self.assertIn('frozenLaserWeighted',manifest['variants'])
            self.assertTrue(any(e['source']=='comparison/frozenLaserReview.json' for e in manifest['files']))
        finally: archive.unlink()
    def test_frozen_optics_rejects_field_evolution(self):
        from frozen_laser import collect
        self.make_frozen_pair();p=self.root/'frozenLaserWeighted/log.vacuumLaserbeamFoam'
        p.write_text(p.read_text().replace('Tchange=0','Tchange=1'))
        with self.assertRaisesRegex(ValueError,'state evolved'): collect(self.root)
    def test_frozen_optics_rejects_unequal_inputs_before_interpreting_outputs(self):
        from frozen_laser import collect
        self.make_frozen_pair();p=self.root/'frozenLaserWeighted/0.00018/frozenAlphaInput'
        p.write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (0 2);')
        with self.assertRaisesRegex(ValueError,'inputs changed'): collect(self.root)
    def test_frozen_optics_reports_spatial_failure_even_with_equal_power(self):
        from frozen_laser import collect
        self.make_frozen_pair();p=self.root/'frozenLaserWeighted/0.00018/rayQ'
        p.write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (0 2);')
        result=collect(self.root)
        self.assertEqual(result['power_absolute_difference_W'],0)
        self.assertFalse(result['optical_partition_gate'])
    def test_frozen_optics_rejects_capture_that_advanced_time(self):
        from frozen_laser import collect
        self.make_frozen_pair();p=self.root/'frozenLaserReference/capture.log'
        p.write_text(p.read_text()+'Time = 0.000181\n')
        with self.assertRaisesRegex(ValueError,'input capture'): collect(self.root)
    def test_handoff_probe_requires_runtime_mode_and_resumed_samples(self):
        from frozen_laser import read_trace
        self.make_frozen_pair();case=self.root/'frozenLaserReference'
        p=case/'probe.json';meta=json.loads(p.read_text());meta['preserve_ray_handoff_sample']=True;p.write_text(json.dumps(meta))
        with self.assertRaisesRegex(ValueError,'correction mode'): read_trace(case,'frozenLaserReference')
        log=case/'log.vacuumLaserbeamFoam';base=log.read_text()+'RAY_HANDOFF_DIAGNOSTICS schema=1 enabled=1\n'
        log.write_text(base+'RAY_HANDOFF_WORK schema=1 time=0.00018 crossings=10 resumed=0\n')
        with self.assertRaisesRegex(ValueError,'handoff work'): read_trace(case,'frozenLaserReference')
        log.write_text(base+'RAY_HANDOFF_WORK schema=1 time=0.00018 crossings=10 resumed=9\n')
        read_trace(case,'frozenLaserReference')
    def test_termination_probe_checks_mode_and_discarded_power_bound(self):
        from frozen_laser import read_trace
        self.make_frozen_pair();case=self.root/'frozenLaserReference'
        p=case/'probe.json';meta=json.loads(p.read_text());meta.update(preserve_ray_handoff_sample=True,consistent_ray_termination=True);p.write_text(json.dumps(meta))
        log=case/'log.vacuumLaserbeamFoam';base=log.read_text()+'RAY_HANDOFF_DIAGNOSTICS schema=1 enabled=1\nRAY_HANDOFF_WORK schema=1 time=0.00018 crossings=10 resumed=9\n'
        log.write_text(base)
        with self.assertRaisesRegex(ValueError,'termination mode'): read_trace(case,'frozenLaserReference')
        base+='RAY_TERMINATION_DIAGNOSTICS schema=1 enabled=1\n'
        log.write_text(base+'RAY_TERMINATION_WORK schema=1 time=0.00018 threshold=1e-6 cutoffRays=10 discardedPower=1\n')
        with self.assertRaisesRegex(ValueError,'power accounting'): read_trace(case,'frozenLaserReference')
        log.write_text(base+'RAY_TERMINATION_WORK schema=1 time=0.00018 threshold=1e-6 cutoffRays=10 discardedPower=5e-6\n')
        read_trace(case,'frozenLaserReference')
    def test_non_debug_ray_number_is_optional_with_explicit_report(self):
        self.make_traversal_pair()
        for name in ('rayTraversalReference','rayTraversalCached'):
            (self.root/name/'processor0/0.000182/rayNumber').unlink()
        result=collect_laser(self.root,traversal=True)
        self.assertTrue(result['regression_gate'])
        self.assertEqual(len(result['fields']),7)
        self.assertEqual(result['ray_number_comparison']['status'],'not_written')
    def test_partial_ray_number_output_rejected(self):
        self.make_traversal_pair()
        (self.root/'rayTraversalCached/processor0/0.000182/rayNumber').unlink()
        with self.assertRaisesRegex(ValueError,'Partially available rayNumber'): collect_laser(self.root,traversal=True)
        self.assertFalse((self.root/'comparison').exists())
    def test_traversal_deposition_field_change_fails(self):
        self.make_traversal_pair()
        (self.root/'rayTraversalCached/processor0/0.000182/Deposition').write_text('FoamFile { format ascii; } internalField nonuniform List<scalar> 2 (0 2);')
        self.assertFalse(collect_laser(self.root,traversal=True)['regression_gate'])
    def test_traversal_search_parity_failure_rejected(self):
        self.make_traversal_pair()
        (self.root/'cachedSearchTest.log').write_text('CACHED_SEARCH_TEST checks=100 mismatches=1\n')
        with self.assertRaisesRegex(ValueError,'parity test'): collect_laser(self.root,traversal=True)
        self.assertFalse((self.root/'comparison').exists())
    def test_changed_ray_work_fails_even_with_equal_fields(self):
        self.make_traversal_pair()
        p=self.root/'rayTraversalCached/log.vacuumLaserbeamFoam'
        p.write_text(p.read_text().replace('ownershipChecksSum=80','ownershipChecksSum=81'))
        self.assertFalse(collect_laser(self.root,traversal=True)['regression_gate'])
    def test_rank_counter_mismatch_rejected_before_output(self):
        self.make_laser_pair()
        log=self.root/'laserProfileOn/log.vacuumLaserbeamFoam'
        log.write_text(log.read_text().replace('mergeXRays=40','mergeXRays=41'))
        with self.assertRaisesRegex(ValueError,'Rank counters disagree'): collect_laser(self.root)
        self.assertFalse((self.root/'comparison').exists())
    def test_rank_order_and_duplicate_ids(self):
        rows=self.make_laser_pair()
        from collect_probe import parse_records
        local=parse_records((self.root/'laserProfileOn/log.vacuumLaserbeamFoam').read_text(),'LASER_RANK_DIAGNOSTICS')[:1]
        rank0=local[0]; rank1=copy.deepcopy(rank0);rank1.update(rank=1)
        for key in RANK_COUNTS: rank1[key]*=2
        global_row=copy.deepcopy(rows[0]);global_row['ranks']=2
        for key,aggregate in RANK_COUNTS.items(): global_row[aggregate]=rank0[key]+rank1[key]
        totals=validate_rank_rows([rank1,rank0],[global_row],2)
        self.assertEqual([r['searches'] for r in totals],[160,320])
        with self.assertRaisesRegex(ValueError,'Duplicate/missing'):
            validate_rank_rows([rank0,rank0],[global_row],2)

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
    def test_seed_pair_archives_both_logs_provenance_and_dictionaries(self):
        from package_results import FILES
        work=self.root/'seed-pair'
        for variant in ('raySeedReference','raySeedCached'):
            for relative in FILES:
                path=work/variant/relative;path.parent.mkdir(parents=True,exist_ok=True)
                path.write_text(variant+' '+relative)
            path=work/variant/'processor0/T';path.parent.mkdir();path.write_text('exclude fields')
        output,manifest=package(work)
        self.assertEqual(manifest['variants'],['raySeedReference','raySeedCached'])
        self.assertFalse(manifest['missing_files'])
        self.assertIsNone(manifest['wrapper_exit_code'])
        with tarfile.open(output) as archive:
            for variant in manifest['variants']:
                for suffix in FILES.values():
                    self.assertIn('seed-pair_'+variant+'_'+suffix,archive.getnames())
            self.assertFalse(any('processor' in name for name in archive.getnames()))
    def test_empty_run_rejected(self):
        empty = self.root/'empty'
        empty.mkdir()
        with self.assertRaisesRegex(ValueError,'recognised'):
            package(empty)

class RayPartitionWeightTests(unittest.TestCase):
    def test_corrected_transient_work_requires_complete_calls_and_power_bounds(self):
        from collect_laser_profile import corrected_work
        meta=dict(start_s=.00018,end_s=.000182,preserve_ray_handoff_sample=True,consistent_ray_termination=True)
        base='RAY_HANDOFF_DIAGNOSTICS schema=1 enabled=1\nRAY_TERMINATION_DIAGNOSTICS schema=1 enabled=1\n'
        work=''
        for time in (.000181,.000182):
            work+=f'RAY_HANDOFF_WORK schema=1 time={time} crossings=10 resumed=9\n'
            work+=f'RAY_TERMINATION_WORK schema=1 time={time} threshold=1e-6 cutoffRays=10 discardedPower=5e-6\n'
        corrected_work(base+work,meta,2)
        with self.assertRaisesRegex(ValueError,'cover all'): corrected_work(base+work,meta,3)
        with self.assertRaisesRegex(ValueError,'accounting'): corrected_work(base+work.replace('discardedPower=5e-6','discardedPower=1'),meta,2)
        with self.assertRaisesRegex(ValueError,'runtime mode'): corrected_work(work,meta,2)
        with self.assertRaisesRegex(ValueError,'time'): corrected_work(base+work.replace('time=0.000181','time=0.00018'),meta,2)
    def test_weights_balance_base_cost_and_nonuniform_ray_proxy(self):
        from ray_partition import weights
        values,stats=weights([0,0,1,3])
        self.assertEqual(values,[1,1,2,4])
        self.assertEqual(stats['mean_weight'],2)
        for invalid in ([],[0,0],[-1,2],[float('nan')],[float('inf')]):
            with self.assertRaises(ValueError): weights(invalid)

def parse_records_for_test(line,prefix):
    from collect_probe import parse_records
    return parse_records(line,prefix)[0]

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
    def test_laser_variants_change_profiling_only(self):
        variants={};hashes=[]
        for variant in ('laserProfileOff','laserProfileOn'):
            entries={}
            with patch('prepare_probe.set_entry',side_effect=lambda path,key,value:entries.update({(path.name,key):value})):
                meta=prepare(self.source,self.root/variant,180,0.2,variant)
            variants[variant]=entries;hashes.append(meta['source_snapshot_sha256'])
            self.assertEqual(entries['fvSolution','MELTING/phaseTemperatureBlendHalfWidth'],'0')
            self.assertEqual(entries['fvSolution','MELTING/epsilonTolerance'],'1e-5')
            self.assertEqual(entries['LaserProperties','recordRayPaths'],'false')
        self.assertEqual(len(set(hashes)),1)
        self.assertEqual({k for k in variants['laserProfileOff'] if variants['laserProfileOff'][k]!=variants['laserProfileOn'][k]},
                         {('LaserProperties','laserPerformanceDiagnostics')})
    def test_traversal_variants_change_cache_only(self):
        variants={};hashes=[]
        for variant in ('rayTraversalReference','rayTraversalCached'):
            entries={}
            with patch('prepare_probe.set_entry',side_effect=lambda path,key,value:entries.update({(path.name,key):value})):
                meta=prepare(self.source,self.root/variant,180,0.2,variant)
            variants[variant]=entries;hashes.append(meta['source_snapshot_sha256'])
            self.assertTrue(meta['laser_performance_diagnostics'])
            self.assertEqual(entries['fvSolution','MELTING/epsilonTolerance'],'1e-5')
        self.assertEqual(len(set(hashes)),1)
        self.assertEqual({k for k in variants['rayTraversalReference'] if variants['rayTraversalReference'][k]!=variants['rayTraversalCached'][k]},
                         {('LaserProperties','cachedRayTraversal')})
    def test_seed_variants_keep_validated_cache_enabled_and_change_seed_only(self):
        variants={};hashes=[]
        for variant in ('raySeedReference','raySeedCached'):
            entries={}
            with patch('prepare_probe.set_entry',side_effect=lambda path,key,value:entries.update({(path.name,key):value})):
                meta=prepare(self.source,self.root/variant,180,2,variant)
            variants[variant]=entries;hashes.append(meta['source_snapshot_sha256'])
            self.assertTrue(meta['cached_ray_traversal'])
            self.assertEqual(entries['LaserProperties','cachedRayTraversal'],'true')
            self.assertEqual(entries['fvSolution','MELTING/epsilonTolerance'],'1e-5')
        self.assertEqual(len(set(hashes)),1)
        self.assertEqual({k for k in variants['raySeedReference'] if variants['raySeedReference'][k]!=variants['raySeedCached'][k]},
                         {('LaserProperties','cartesianRaySeedSearch')})
    def test_corrected_pair_changes_cache_only_and_disables_frozen_mode(self):
        variants={}
        for variant in ('rayTraversalReference','rayTraversalCached'):
            entries={}
            with patch('prepare_probe.set_entry',side_effect=lambda path,key,value:entries.update({(path.name,key):value})):
                meta=prepare(self.source,self.root/variant,180,2,variant,corrected_rays=True)
            self.assertTrue(meta['consistent_ray_termination'] and meta['preserve_ray_handoff_sample'])
            self.assertEqual(entries['controlDict','frozenLaserProbe'],'off')
            self.assertEqual(entries['LaserProperties','consistentRayTermination'],'true')
            variants[variant]=entries
        self.assertEqual({k for k in variants['rayTraversalReference'] if variants['rayTraversalReference'][k]!=variants['rayTraversalCached'][k]},
                         {('LaserProperties','cachedRayTraversal')})
    def test_impact_pair_changes_only_two_correction_switches(self):
        variants={};digests=[]
        for variant in ('rayImpactLegacy','rayImpactCorrected'):
            entries={}
            with patch('prepare_probe.set_entry',side_effect=lambda path,key,value:entries.update({(path.name,key):value})):
                meta=prepare(self.source,self.root/variant,180,2,variant)
            self.assertTrue(meta['cached_ray_traversal'])
            self.assertEqual(entries['controlDict','frozenLaserProbe'],'off')
            self.assertEqual(entries['controlDict','writePrecision'],17)
            variants[variant]=entries;digests.append(meta['source_snapshot_sha256'])
        self.assertEqual(digests[0],digests[1])
        self.assertEqual({k for k in variants['rayImpactLegacy'] if variants['rayImpactLegacy'][k]!=variants['rayImpactCorrected'][k]},
            {('LaserProperties','preserveRayHandoffSample'),('LaserProperties','consistentRayTermination')})
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
