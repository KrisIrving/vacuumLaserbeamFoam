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

class RegionAuditTests(unittest.TestCase):
    def fixture(self,times=(0.0001,)):
        lines=['M247_REGION_CONFIG schema=1 liquidus=1631 solidus=1537 alphaMin=0.01 metalMin=0.5 epsilonMin=0.01 fastSpeed=1 thermalThreshold=1368.15']
        for t in times:
            lines.append(f'M247_REGION_STATE schema=1 time={t} ranks=48 invalid=0 alphaBounds=0 epsilonBounds=0 metalTmax=4200 Tmax=4500 Umax=80 liquidVolume=1e-12')
            for r in range(6):
                lines.append(f'M247_REGION schema=1 time={t} region={r} cells={756000 if r==0 else 20} volume={5.16096e-10 if r==0 else 1e-12} xmin=-0.00052 xmax=0.00032 ymin=0 ymax=0.00096 zmin=-0.00032 zmax=0.00032')
        return '\n'.join(lines+['End'])
    def test_complete_snapshots_require_ordered_six_regions(self):
        from region_audit import read_regions
        self.assertEqual(len(read_regions(self.fixture(),[0.0001])),1)
        with self.assertRaisesRegex(ValueError,'ordering'):
            read_regions(self.fixture().replace('region=5','region=4'),[0.0001])
        with self.assertRaisesRegex(ValueError,'Missing'):
            read_regions('\n'.join(l for l in self.fixture().splitlines() if 'region=5' not in l),[0.0001])
    def test_wrong_times_ranks_material_and_incomplete_logs_rejected(self):
        from region_audit import read_regions
        for text in (self.fixture().replace('ranks=48','ranks=24'),self.fixture().replace('solidus=1537','solidus=1587'),self.fixture().replace('\nEnd','')):
            with self.assertRaises(ValueError): read_regions(text,[0.0001])
        with self.assertRaises(ValueError):read_regions(self.fixture(),[0.00012])
    def test_region_escape_nonfinite_and_invalid_mesh_rejected(self):
        from region_audit import read_regions
        for text in (self.fixture().replace('cells=756000','cells=755000'),self.fixture().replace('invalid=0','invalid=1'),self.fixture().replace('Tmax=4500','Tmax=1e999'),self.fixture().replace('region=5 cells=20 volume=1e-12 xmin=-0.00052','region=5 cells=20 volume=1e-12 xmin=-0.001')):
            with self.assertRaises(ValueError):read_regions(text,[0.0001])
    def test_empty_region_requires_zero_volume(self):
        from region_audit import read_regions
        text=self.fixture().replace('region=5 cells=20 volume=1e-12','region=5 cells=0 volume=1e-12')
        with self.assertRaisesRegex(ValueError,'Empty'):read_regions(text,[0.0001])
    def test_cost_reserves_time_and_distinguishes_assumptions(self):
        from region_audit import cost_scenarios
        summary=dict(job_wall_s=340,duration_us=2,ranks=48,sections={k:dict(mean_fraction=v) for k,v in (('alpha',.03),('momentum',.03),('pressure',.10),('laser',.50))})
        r=cost_scenarios(summary)
        four=r['central_spacing_scenarios'][1]
        self.assertEqual(four['assumed_work_multiplier'],16)
        self.assertAlmostEqual(four['pilot_2us_hours'],340*16/3600)
        self.assertAlmostEqual(four['max_us_in_19p2_hours']*170*16,19.2*3600)
        self.assertAlmostEqual(r['flow_only_elimination_ceiling'],1/.84)
    def test_keyhole_slope_uses_supported_every_10us_series(self):
        from region_audit import trend
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'depth.csv'
            header='time_s,keyhole_depth_um,surface_connected,bottom_support_vertices\n'
            data=''.join(f'{u*1e-6},{u*1.2},yes,20\n' for u in range(100,201,10))
            path.write_text(header+data)
            self.assertAlmostEqual(trend(path)['ols_150_200_um_per_us'],1.2)
            self.assertFalse(trend(path)['plateau_approved'])
            path.write_text((header+data).replace('yes','fallback',1))
            with self.assertRaisesRegex(ValueError,'Disconnected'):trend(path)
    def test_audit_reports_and_partial_build_packaged(self):
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)/'region-budget';work.mkdir()
            for name in ('build.log','auditInputs.json','sourceRegionAudit.log','regionAuditReview.json','regionEnvelopes.csv'):
                (work/name).write_text('data')
            output,m=package(work,exit_code=1)
            self.assertEqual(m['variants'],[])
            self.assertEqual(len(m['files']),5)
            self.assertEqual(m['wrapper_exit_code'],1)
            with tarfile.open(output) as archive:
                self.assertIn('region-budget_regionEnvelopes.csv',archive.getnames())
    def test_collection_preserves_failed_boundary_gate_and_checks_hashes(self):
        from region_audit import collect,sha,SOURCE_TIMES,PAIR_TIMES
        from package_results import FILES
        with tempfile.TemporaryDirectory() as directory:
            w=Path(directory);hashes={}
            for variant in ('rayImpactLegacy','rayImpactCorrected'):
                for relative in FILES:
                    if relative in ('capture.log','captureRun.json'):continue
                    p=w/variant/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('data')
                    hashes[f'{variant}/{relative}']=sha(p)
            (w/'sourceKeyholeDepth.csv').write_text('time_s,keyhole_depth_um,surface_connected,bottom_support_vertices\n'+''.join(f'{u*1e-6},{u},yes,20\n' for u in range(100,201,10)))
            (w/'sourceMoltenExtent.csv').write_text('reference')
            for name in ('sourceKeyholeDepth.csv','sourceMoltenExtent.csv'):hashes[name]=sha(w/name)
            (w/'auditInputs.json').write_text(json.dumps(dict(schema=1,read_only=True,source_times_s=SOURCE_TIMES,pair_times_s=PAIR_TIMES,reference_sha256=hashes)))
            for log,times in (('sourceRegionAudit.log',SOURCE_TIMES),('legacyRegionAudit.log',PAIR_TIMES),('correctedRegionAudit.log',PAIR_TIMES)):
                (w/log).write_text(self.fixture(times))
            summary=dict(job_wall_s=340,duration_us=2,ranks=48,sections={k:dict(mean_fraction=v) for k,v in (('alpha',.03),('momentum',.03),('pressure',.10),('laser',.50))})
            with patch('region_audit.read_pair',return_value=[({},summary,[]),({},summary,[])]):r=collect(w)
            self.assertTrue(r['execution_gate'])
            self.assertFalse(r['molten_snapshot_boundary_gate_80um'])
            self.assertFalse(r['production_approved'])
            self.assertEqual(r['fine_box_candidate']['clipped_axes'],['x','y','z'])
            self.assertTrue((w/'regionEnvelopes.csv').is_file())
            (w/'sourceMoltenExtent.csv').write_text('changed')
            with self.assertRaisesRegex(ValueError,'changed'):collect(w)
    def test_wrong_impact_modes_rejected_before_reference_copies(self):
        from region_audit import read_pair
        p=({},dict(),[])
        m=dict(variant='rayImpactLegacy',ranks=48,start_s=0.00018,end_s=0.000182,duration_us=2,cached_ray_traversal=False)
        with patch('region_audit.read_probe',return_value=(m,{},[])),patch('region_audit.compare'):
            with self.assertRaisesRegex(ValueError,'modes'):read_pair(Path('unused'))

class LocalRefinementTests(unittest.TestCase):
    def test_moment_gate_detects_material_loss(self):
        from local_refinement import moments,compare_moments
        text='M247_MESH_MOMENTS schema=1 time=0.00018 cells=756000 volume=5e-10 metalVolume=3e-10 liquidVolume=8e-12 metalTemperatureMoment=4e-7 alphaMin=0 alphaMax=1 epsilonMin=0 epsilonMax=1 Tmin=1343 Tmax=4500\nEnd\n'
        before=moments(text);after=dict(before,cells=1000000)
        self.assertTrue(all(r['passed'] for r in compare_moments(before,after)))
        after['metalVolume']*=.99
        self.assertFalse(all(r['passed'] for r in compare_moments(before,after)))
        for invalid in (text.replace('alphaMax=1','alphaMax=1.1'),text.replace('volume=5e-10','volume=1e999'),text.replace('time=0.00018','time=0.0002')):
            with self.assertRaises(ValueError):moments(invalid)
    def test_selection_coverage_and_mesh_quality_required(self):
        from local_refinement import selected_count,mesh_ok
        text='\n'.join(f'cellSet refineCells now size {n}' for n in (100,200,400))+'\nEnd\n'
        self.assertEqual(selected_count(text),[100,200,400])
        with self.assertRaises(ValueError):selected_count(text.replace('400','150'))
        with self.assertRaises(ValueError):selected_count(text.replace('\nEnd',''))
        mesh_ok('Mesh OK.\nEnd\n')
        with self.assertRaises(ValueError):mesh_ok('Failed1mesh check\nEnd\n')
    def test_preview_failure_evidence_is_packaged(self):
        with tempfile.TemporaryDirectory() as directory:
            w=Path(directory)/'local-refinement';w.mkdir()
            for name in ('build.log','previewInputs.json','coarseMoments.log','localRefine4_topoSetDict','localRefine4_refinement.log'):(w/name).write_text('data')
            output,m=package(w,exit_code=1)
            self.assertEqual(len(m['files']),5)
            self.assertIn('localRefine4_refinement.log',[e['source'] for e in m['files']])

    def test_native_concavity_failure_is_not_waived(self):
        from local_refinement import mesh_summary
        text=' ***Concave cells (using face planes) found, number of cells: 15101\nFailed 1 mesh checks.\n\nEnd\n'
        self.assertEqual(mesh_summary(text),dict(passed=False,failed_checks=1,concave_cells=15101))
        self.assertTrue(mesh_summary('Mesh OK.\nEnd\n')['passed'])
        for invalid in (text.replace('End',''),text+'Mesh OK.\n','End\n'):
            with self.assertRaises(ValueError):mesh_summary(invalid)

    def test_concavity_diagnostic_requires_matching_native_set(self):
        from local_refinement import concavity_summary
        text='M247_MESH_CONCAVITY schema=1 count=15101 worstPlaneDistance=1e-20 maxRelativePlaneDistance=1e-15 aboveRelative1e9=0 xmin=-0.0002 xmax=0.0002 ymin=0.0001 ymax=0.0008 zmin=-0.0001 zmax=0.0001\nEnd\n'
        self.assertEqual(concavity_summary(text,15101)['aboveRelative1e9'],0)
        for invalid,count in ((text,15100),(text.replace('worstPlaneDistance=1e-20','worstPlaneDistance=nan'),15101),(text.replace('End',''),15101)):
            with self.assertRaises(ValueError):concavity_summary(invalid,count)

    def test_quality_failure_saves_report_and_continues_second_variant(self):
        import local_refinement as module
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'source';source.mkdir();work=root/'work'
            utility=root/'utility';utility.write_text('binary')
            def prepare_copy(source,coarse,*args,**kwargs):
                for relative in ('constant/polyMesh','system','0.00018'):(coarse/relative).mkdir(parents=True)
                return dict(ranks=48,checkpoint='0.00018')
            def native(work,command,name):
                if name.endswith('Moments') or name.endswith('_moments'):
                    cells=756000 if name=='coarseMoments' else 756700
                    text=f'M247_MESH_MOMENTS schema=1 time=0.00018 cells={cells} volume=5e-10 metalVolume=3e-10 liquidVolume=8e-12 metalTemperatureMoment=4e-7 alphaMin=0 alphaMax=1 epsilonMin=0 epsilonMax=1 Tmin=1343 Tmax=4500\nEnd\n'
                elif name.endswith('_selection'):
                    text='\n'.join(f'cellSet refineCells now size {n}' for n in (10,50,100))+'\nEnd\n'
                elif name=='localRefine4_checkMesh':text='Failed 1 mesh checks.\nEnd\n'
                elif name.endswith('CheckMesh') or name.endswith('_checkMesh'):text='Mesh OK.\nEnd\n'
                else:text='End\n'
                (work/(name+'.log')).write_text(text)
                return dict(command=command,elapsed_wall_s=1,log=name+'.log')
            with patch.object(module,'prepare',side_effect=prepare_copy),patch.object(module,'run',side_effect=native):
                result=module.preview(source,work,utility)
            self.assertTrue(result['complete']);self.assertFalse(result['geometry_mapping_gate'])
            self.assertEqual([v['status'] for v in result['variants']],['failed_mesh_quality','completed'])
            self.assertEqual(json.loads((work/'localRefinementReview.json').read_text()),result)

    def test_resume_copies_only_serial_restart_and_rejects_overlap(self):
        from local_refinement import copy_serial_restart
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);old=root/'old';old.mkdir();work=root/'new';work.mkdir()
            meta=dict(ranks=48,checkpoint='0.00018')
            (old/'previewInputs.json').write_text(json.dumps(dict(schema=1,preview_only=True,copied_restart=meta)))
            (old/'coarseMoments.log').write_text('M247_MESH_MOMENTS schema=1 time=0.00018 cells=756000 volume=5e-10 metalVolume=3e-10 liquidVolume=8e-12 metalTemperatureMoment=4e-7 alphaMin=0 alphaMax=1 epsilonMin=0 epsilonMax=1 Tmin=1343 Tmax=4500\nEnd\n')
            (old/'coarseCheckMesh.log').write_text('Mesh OK.\nEnd\n')
            for relative in ('constant/polyMesh','system','0.00018','processor0'):
                p=old/'coarse'/relative;p.mkdir(parents=True);(p/'data').write_text(relative)
            with self.assertRaises(ValueError):copy_serial_restart(old,old/'nested')
            copied,before=copy_serial_restart(old,work)
            self.assertEqual(copied,meta);self.assertEqual(before['cells'],756000)
            self.assertFalse((work/'coarse/processor0').exists())
            evidence=json.loads((work/'resumeInputs.json').read_text())
            self.assertTrue(evidence['copy_hash_gate']);self.assertEqual(len(evidence['copied_files_sha256']),3)

class RestartAuditTests(unittest.TestCase):
    def test_coplanar_qualification_is_narrow_and_keeps_native_failure(self):
        from restart_audit import geometry_qualification
        text='Face flatness (1 = flat, 0 = butterfly) : min = 0.99999999999999956 average = 1\n ***Concave cells (using face planes) found, number of cells: 15101\nFailed 1 mesh checks.\nEnd\n'
        diagnostic=dict(count=15101,worstPlaneDistance=8.7e-19,maxRelativePlaneDistance=1.1e-13,aboveRelative1e9=0)
        r=geometry_qualification(text,diagnostic)
        self.assertTrue(r['qualified']);self.assertFalse(r['native']['passed'])
        for altered,d in ((text,dict(diagnostic,worstPlaneDistance=1e-10)),
            (text,dict(diagnostic,maxRelativePlaneDistance=1e-5)),(text,dict(diagnostic,count=1)),
            (text,None),(text.replace('Failed 1','Failed 2'),diagnostic),
            (text.replace('0.99999999999999956','0.95'),diagnostic),
            (text.replace('End',' ***Zero volume\nEnd'),diagnostic)):
            self.assertFalse(geometry_qualification(altered,d)['qualified'])
    def test_flux_records_reject_nonfinite_and_inconsistent_counts(self):
        from restart_audit import flux_record
        text='M247_RESTART_FLUX schema=1 cells=756000 divL1=1 divRMS=2 divMax=3 netFlux=-1e-12 Umax=78 velocityFluxDifference=1e-5 velocityFluxAbs=1e-3 alphaFluxAbs=1e-3 internalFaces=100 zeroInternalFluxFaces=25\nEnd\n'
        self.assertEqual(flux_record(text)['netFlux'],-1e-12)
        for invalid in (text.replace('End',''),text.replace('divL1=1','divL1=nan'),
            text.replace('zeroInternalFluxFaces=25','zeroInternalFluxFaces=101'),text.replace('cells=756000','cells=1.1')):
            with self.assertRaises(ValueError):flux_record(invalid)
    def test_restart_audit_logs_are_packaged(self):
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)/'local-restart';work.mkdir()
            for name in ('restartAuditInputs.json','localRestartReview.json','localRefine4_restart.log','localRefine10_restartCheckMesh.log'):
                (work/name).write_text('evidence')
            _,manifest=package(work,exit_code=0)
            self.assertEqual(len(manifest['files']),4)

    def test_audit_keeps_flux_observations_separate_from_restart_approval(self):
        import restart_audit as module
        from local_refinement import moments
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);previous=root/'preview';previous.mkdir();utility=root/'utility';utility.write_text('binary')
            state='M247_MESH_MOMENTS schema=1 time=0.00018 cells=756000 volume=5e-10 metalVolume=3e-10 liquidVolume=8e-12 metalTemperatureMoment=4e-7 alphaMin=0 alphaMax=1 epsilonMin=0 epsilonMax=1 Tmin=1343 Tmax=4500\n'
            expected=moments(state+'End\n')
            preview=dict(schema=2,complete=True,production_approved=False,before=expected,
                variants=[dict(variant=v,moments=expected) for v in ('localRefine4','localRefine10')])
            (previous/'localRefinementReview.json').write_text(json.dumps(preview))
            for case in ('coarse','localRefine4','localRefine10'):
                for part in ('constant','system','0.00018'):
                    p=previous/case/part;p.mkdir(parents=True);(p/'field').write_text('unchanged')
            def native(work,command,name):
                if name.endswith('CheckMesh'):text='Mesh OK.\nEnd\n'
                else:
                    value=1 if name.startswith('coarse_') else 100
                    text=state+f'M247_RESTART_FLUX schema=1 cells=756000 divL1={value} divRMS={value} divMax={value} netFlux=0 Umax=78 velocityFluxDifference=0 velocityFluxAbs=1 alphaFluxAbs=1 internalFaces=100 zeroInternalFluxFaces=0\nEnd\n'
                (work/(name+'.log')).write_text(text)
                return dict(command=command,log=name+'.log',elapsed_wall_s=1)
            with patch.object(module,'run',side_effect=native):
                result=module.audit(previous,root/'audit',utility)
            self.assertTrue(result['complete']);self.assertTrue(result['geometry_qualification_gate'])
            self.assertFalse(result['restart_ready']);self.assertFalse(result['production_approved'])
            self.assertEqual(result['cases'][1]['continuity_change']['divL1']['ratio'],100)
            def changing(work,command,name):
                result=native(work,command,name)
                if name=='coarse_restart':(previous/'coarse/0.00018/field').write_text('changed')
                return result
            with patch.object(module,'run',side_effect=changing):
                with self.assertRaisesRegex(ValueError,'changed during read-only'):
                    module.audit(previous,root/'changed-audit',utility)

class FluxPilotTests(unittest.TestCase):
    def test_failed_projection_never_launches_cfd(self):
        import flux_pilot as module
        from local_refinement import moments
        from restart_audit import case_fingerprint,flux_record
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);preview=root/'preview';preview.mkdir();audit=root/'audit';audit.mkdir()
            utility=root/'utility';utility.write_text('binary')
            state='M247_MESH_MOMENTS schema=1 time=0.00018 cells=2283911 volume=5e-10 metalVolume=3e-10 liquidVolume=8e-12 metalTemperatureMoment=4e-7 alphaMin=0 alphaMax=1 epsilonMin=0 epsilonMax=1 Tmin=1343 Tmax=4500\n'
            flux='M247_RESTART_FLUX schema=1 cells=2283911 divL1=88759 divRMS=516417 divMax=82984974 netFlux=0 Umax=78 velocityFluxDifference=1 velocityFluxAbs=1 alphaFluxAbs=0 internalFaces=100 zeroInternalFluxFaces=0\n'
            source=preview/'localRefine4'
            for part in ('constant','system','0.00018'):
                p=source/part;p.mkdir(parents=True);(p/'field').write_text('unchanged')
            (source/'0.00018/phi').write_text('old flux')
            (preview/'previewInputs.json').write_text(json.dumps(dict(copied_restart=dict(ranks=48))))
            row=dict(case='localRefine4',files_sha256=case_fingerprint(source),moments=moments(state+'End\n'),flux=flux_record(flux+'End\n'))
            record=dict(complete=True,geometry_qualification_gate=True,production_approved=False,
                inputs=dict(previous_work=str(preview)),cases=[row,dict(case='coarse',flux=dict(divL1=.0266,divRMS=12.45,divMax=12500))])
            (audit/'localRestartReview.json').write_text(json.dumps(record))
            calls=[]
            def native(work,command,name):
                calls.append(name);text=state+flux
                if name=='localProjected_projection':
                    (work/'rayTraversalCached/0.00018/phi').write_text('new but insufficient flux')
                    text+='M247_FLUX_PROJECTION schema=1 passes=5 fixedPressurePatches=1 wrotePhi=1 wroteU=0 advancedTime=0\n'
                (work/(name+'.log')).write_text(text+'End\n')
                return dict(command=command,log=name+'.log',elapsed_wall_s=1)
            with patch.object(module,'set_entry'),patch.object(module,'run',side_effect=native):
                with self.assertRaisesRegex(ValueError,'CFD not launched'):module.execute(audit,root/'work',utility)
            self.assertEqual(calls,['localProjected_before','localProjected_projection','localProjected_after'])
            result=json.loads((root/'work/fluxPilotReview.json').read_text())
            self.assertFalse(result['projection_gate']);self.assertFalse(result['complete'])
            self.assertEqual(case_fingerprint(source),row['files_sha256'])

    def test_continuity_screen_rejects_mapped_flux_amplification(self):
        from flux_pilot import projection_gate
        coarse=dict(divL1=.026644477,divRMS=12.4486,divMax=12498.04)
        self.assertFalse(projection_gate(dict(divL1=88759,divRMS=516417,divMax=82984974),coarse)['passed'])
        self.assertTrue(projection_gate(dict(divL1=.03,divRMS=13,divMax=13000),coarse)['passed'])
        self.assertFalse(projection_gate(dict(divL1=.03,divRMS=13,divMax=15001),coarse)['passed'])
    def test_projection_protects_velocity_material_and_mesh(self):
        from flux_pilot import unchanged_except_phi
        before={'0.00018/phi':'old','0.00018/U':'velocity','0.00018/alpha.metal':'material','constant/polyMesh/points':'mesh'}
        self.assertEqual(unchanged_except_phi(before,dict(before,**{'0.00018/phi':'new'})),['0.00018/phi'])
        for key in ('0.00018/U','0.00018/alpha.metal','constant/polyMesh/points'):
            with self.assertRaises(ValueError):unchanged_except_phi(before,dict(before,**{key:'changed'}))
    def test_post_pilot_snapshot_requires_expected_time(self):
        from local_refinement import moments
        text='M247_MESH_MOMENTS schema=1 time=0.0001802 cells=2283911 volume=5e-10 metalVolume=3e-10 liquidVolume=8e-12 metalTemperatureMoment=4e-7 alphaMin=0 alphaMax=1 epsilonMin=0 epsilonMax=1 Tmin=1343 Tmax=4500\nEnd\n'
        with self.assertRaises(ValueError):moments(text)
        self.assertEqual(moments(text,expected_time=.0001802)['cells'],2283911)

class LocalOpticsTests(unittest.TestCase):
    def test_single_input_contrasts_preserve_signed_nonlinear_effects(self):
        from local_optics_inputs import contrast,ROLES
        self.assertEqual(len(set(ROLES.values())),3)
        c=contrast('normal','frozenNormalInput',333,289,332)
        self.assertEqual(c['difference_from_fine_own_W'],44)
        self.assertGreater(c['depositedPower_W'],c['fine_all_mapped_W'])
        self.assertNotIn('passed',c)

    def test_single_input_roles_have_distinct_complete_archives(self):
        from package_results import LOCAL_OPTICS_INPUT_VARIANTS,FILES
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)/'inputs';work.mkdir()
            for name in LOCAL_OPTICS_INPUT_VARIANTS:
                for relative in FILES:
                    if relative.startswith('capture'):continue
                    p=work/name/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('evidence')
            (work/'localOpticsInputReview.json').write_text('{}')
            _,manifest=package(work,exit_code=0)
            self.assertEqual(manifest['variants'],list(LOCAL_OPTICS_INPUT_VARIANTS))
            self.assertEqual(manifest['missing_files'],[])

    def test_restore_only_byte_identical_flux_names(self):
        from local_optics import restore_unmapped_fluxes,case_fingerprint,mapping_guard
        with tempfile.TemporaryDirectory() as directory:
            case=Path(directory);time=case/'0.00018';time.mkdir()
            for name in ('phi','alphaPhi0.metal','T','frozenAlphaInput'):(time/name).write_text(name)
            before=case_fingerprint(case)
            for name in ('phi','alphaPhi0.metal'):(time/name).rename(time/(name+'.unmapped'))
            (time/'frozenAlphaInput').write_text('mapped optical data')
            restored=restore_unmapped_fluxes(case,before)
            self.assertEqual(len(restored),2)
            self.assertEqual(mapping_guard(before,case_fingerprint(case)),['0.00018/frozenAlphaInput'])
            self.assertEqual(restore_unmapped_fluxes(case,before),[])

    def test_flux_restore_rejects_bad_bytes_and_unrelated_changes_before_mutation(self):
        from local_optics import restore_unmapped_fluxes,case_fingerprint
        for fault in ('bad_flux','changed_T','extra_file','collision'):
            with tempfile.TemporaryDirectory() as directory:
                case=Path(directory);time=case/'0.00018';time.mkdir()
                (time/'phi').write_text('flux');(time/'T').write_text('temperature')
                before=case_fingerprint(case);(time/'phi').rename(time/'phi.unmapped')
                if fault=='bad_flux':(time/'phi.unmapped').write_text('changed')
                elif fault=='changed_T':(time/'T').write_text('changed')
                elif fault=='extra_file':(time/'unexpected').write_text('extra')
                else:(time/'phi').write_text('collision')
                state=case_fingerprint(case)
                with self.assertRaises(ValueError):restore_unmapped_fluxes(case,before)
                self.assertEqual(case_fingerprint(case),state)

    def test_mapping_audit_distinguishes_renames_from_changed_bytes(self):
        from audit_optical_mapping import differences
        before={'0.00018/phi':'flux','0.00018/T':'temperature','constant/polyMesh/points':'mesh'}
        after={'0.00018/phi.unmapped':'flux','0.00018/T':'changed','constant/polyMesh/points':'mesh'}
        rows,pairs=differences(before,after)
        self.assertEqual({r['path']:r['status'] for r in rows},
            {'0.00018/phi':'removed','0.00018/phi.unmapped':'added','0.00018/T':'modified'})
        self.assertEqual(pairs,[dict(source='0.00018/phi',target='0.00018/phi.unmapped',sha256='flux')])
        after['0.00018/phi.unmapped']='different bytes'
        self.assertEqual(differences(before,after)[1],[])

    def test_mapping_audit_is_packaged_without_fake_solver_jobs(self):
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)/'mapping-audit';work.mkdir()
            (work/'opticalMappingAudit.json').write_text('{"strict_mapping_gate":false}')
            _,manifest=package(work,exit_code=0)
            self.assertEqual(manifest['variants'],[])
            self.assertEqual(manifest['missing_files'],[])
            self.assertEqual(manifest['files'][0]['source'],'opticalMappingAudit.json')

    def test_mapping_is_restricted_to_three_frozen_inputs(self):
        from local_optics import mapping_guard
        before={'0.00018/T':'T','constant/polyMesh/points':'mesh','0.00018/frozenNormalInput':'old'}
        self.assertEqual(mapping_guard(before,dict(before,**{'0.00018/frozenNormalInput':'new'})),['0.00018/frozenNormalInput'])
        for key in ('0.00018/T','constant/polyMesh/points','0.00018/phi'):
            with self.assertRaises(ValueError):mapping_guard(before,dict(before,**{key:'changed'}))
    def test_capture_rejects_time_advancement_and_reports_contrasts(self):
        from local_optics import check_capture,contrasts
        text='FROZEN_LASER_CAPTURE schema=1 time=0.00018 calls=0\nEnd\n'
        check_capture(text)
        for invalid in (text+'Time = 0.0001801\n',text.replace('End',''),text.replace('calls=0','calls=1')):
            with self.assertRaises(ValueError):check_capture(invalid)
        results=contrasts([328,288,327])
        self.assertEqual([r['difference_W'] for r in results],[-40,-1,-39])
        self.assertNotIn('production_approved',results[0])
    def test_all_local_optical_roles_are_distinct_in_archive(self):
        from package_results import LOCAL_OPTICS_VARIANTS,FILES
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)/'local-optics';work.mkdir()
            for name in LOCAL_OPTICS_VARIANTS:
                for relative in FILES:
                    if relative.startswith('capture'):continue
                    p=work/name/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('evidence')
            _,manifest=package(work,exit_code=0)
            self.assertEqual(manifest['variants'],list(LOCAL_OPTICS_VARIANTS))
            self.assertEqual(manifest['missing_files'],[])

class MovingWindowTests(unittest.TestCase):
    def fixture(self):
        from moving_window import CENTRES
        lines=[]
        for step in range(9):
            r=dict(schema=1,step=step,physicalTime=.00018,auditTime=.00018+step*1e-9,
                centreX=CENTRES[0] if step==0 else CENTRES[(step-1)//2],changed=int(step>0),
                cells=756000 if step==0 else 1200000,fineCells=0 if step==0 else 400000,
                protectedCells=0,interiorCells=100,coveredCells=0 if step==0 else 100,
                updateWall_s=0 if step==0 else 2,volume=5e-10,metalVolume=3e-10,
                mappedMetalTemperature=4e-7,mappedLiquidVolume=8e-12,
                directMetalTemperature=4e-7,directLiquidVolume=8e-12,
                alphaMin=0,alphaMax=1,epsilonMin=0,epsilonMax=1,Tmin=1343,Tmax=4151)
            lines.append('M247_MOVING_WINDOW '+' '.join(f'{k}={v}' for k,v in r.items()))
        for step in range(1,9):
            lines.append(f'M247_MOVING_V0 schema=1 step={step} cells={756000 if step==1 else 1200000} ready=1 maxDifference=0 previousIndex={180000+step-1} currentIndex={180000+step}')
        return '\n'.join(lines)+'\nUnrefined from 1300000 to 1200000 cells.\nM247_MOVING_WINDOW_END schema=1 updates=8 advancedPhysics=0\nEnd\n'

    def test_old_volumes_required_for_every_update_with_correct_cell_count(self):
        from moving_window import collect
        for text in (self.fixture().replace('M247_MOVING_V0','WRONG_VOLUME_PREFIX'),
                     self.fixture().replace('ready=1','ready=0'),
                     self.fixture().replace('currentIndex=180001','currentIndex=180000'),
                     self.fixture().replace('previousIndex=180001','previousIndex=0'),
                     self.fixture().replace('maxDifference=0','maxDifference=1e-20'),
                     self.fixture().replace('M247_MOVING_V0 schema=1 step=1 cells=756000','M247_MOVING_V0 schema=1 step=1 cells=1')):
            with self.assertRaises(ValueError):collect(text)

    def test_small_mesh_preflight_uses_its_own_cell_count(self):
        from moving_window import collect
        text=self.fixture().replace('756000','2400').replace('1200000','4800').replace('1300000','5400').replace('fineCells=400000','fineCells=3200')
        self.assertTrue(collect(text,base_cells=2400)['coarsening_gate'])
        with self.assertRaises(ValueError):collect(text)

    def test_small_native_failure_preserves_evidence_and_stops(self):
        from moving_window import smoke
        import subprocess
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)
            with patch('moving_window.subprocess.run',side_effect=subprocess.CalledProcessError(1,['blockMesh'])) as command:
                with self.assertRaises(subprocess.CalledProcessError):smoke(work,Path('/native/tool'))
                self.assertEqual(command.call_count,1)
            report=json.loads((work/'movingWindowSmokeReview.json').read_text())
            self.assertFalse(report['passed'])
            self.assertEqual(report['failure_stage'],'small_mesh_preflight')
            self.assertEqual(report['error_type'],'CalledProcessError')
            self.assertFalse(report['large_case_started'])
            self.assertTrue(report['error'])
            self.assertTrue((work/'movingWindowSmoke_blockMesh.log').is_file())
            _,manifest=package(work,exit_code=1)
            self.assertIn('movingWindowSmokeReview.json',{f['source'] for f in manifest['files']})

    def test_complete_path_requires_coarsening_and_preserves_linear_moments(self):
        from moving_window import collect
        r=collect(self.fixture())
        self.assertTrue(r['linear_mapping_gate'] and r['coverage_gate'] and r['coarsening_gate'])
        self.assertEqual(r['coarsened_cell_reductions'],100000)
        self.assertEqual(r['update_wall_s'],16)
        r=collect(self.fixture().replace('Unrefined from 1300000 to 1200000 cells.',''))
        self.assertFalse(r['coarsening_gate'])

    def test_partial_overbudget_invalid_physics_and_wrong_path_rejected(self):
        from moving_window import collect
        for text in (self.fixture().replace('End\n',''),self.fixture().replace('cells=1200000','cells=2000001'),
                     self.fixture().replace('physicalTime=0.00018','physicalTime=0.000181'),
                     self.fixture().replace('alphaMax=1','alphaMax=1.1'),
                     self.fixture().replace('centreX=0.00016','centreX=0.00017')):
            with self.assertRaises(ValueError):collect(text)

    def test_nonlinear_drift_reported_separately_from_passive_proxy_conservation(self):
        from moving_window import collect
        text=self.fixture()
        text=text.replace('directMetalTemperature=4e-07','directMetalTemperature=4.1e-07',1)
        r=collect(text)
        self.assertTrue(r['linear_mapping_gate'])
        self.assertNotEqual(r['nonlinear_product_drift'][0]['relative_difference'],0)
        text=self.fixture().replace('mappedMetalTemperature=4e-07','mappedMetalTemperature=5e-07',1)
        self.assertFalse(collect(text)['linear_mapping_gate'])

    def protected_fixture(self):
        lines=self.fixture().splitlines()
        for i,line in enumerate(lines):
            if line.startswith('M247_MOVING_WINDOW '):
                step=int(line.split('step=')[1].split()[0])
                lines[i]+=f' directCellSelection=1 protectWake=1 wakeCells=100 wakeCoveredCells={0 if step==0 else 100} outsideWakeCells=40 mappedWakeVolume=1e-12'
        lines.extend(f'M247_MOVING_CANDIDATES schema=1 timeIndex={180000+step} cells={756000 if step==1 else 1200000} directCellSelection=1 requested=1000 selected=1000' for step in range(1,9))
        return '\n'.join(lines)+'\n'

    def test_protected_wake_requires_coverage_outside_window_and_marker_conservation(self):
        from moving_window import collect
        text=self.protected_fixture()
        self.assertTrue(collect(text,require_wake=True)['wake_gate'])
        for bad in (text.replace('wakeCoveredCells=100','wakeCoveredCells=99'),
                    text.replace('outsideWakeCells=40','outsideWakeCells=0'),
                    text.replace('mappedWakeVolume=1e-12','mappedWakeVolume=2e-12',1)):
            self.assertFalse(collect(bad,require_wake=True)['wake_gate'])
        for bad in (self.fixture(),text.replace('protectWake=1','protectWake=0'),
                    text.replace('wakeCells=100','wakeCells=nan'),
                    text.replace('mappedWakeVolume=1e-12','mappedWakeVolume=nan')):
            with self.assertRaises(ValueError):collect(bad,require_wake=True)

    def test_direct_selection_evidence_rejects_loss_wrong_index_and_nonbinary_mode(self):
        from moving_window import collect
        text=self.protected_fixture()
        for bad in (text.replace('M247_MOVING_CANDIDATES','OLD_CANDIDATES'),
                    text.replace('selected=1000','selected=999'),
                    text.replace('requested=1000','requested=nan'),
                    text.replace('timeIndex=180001','timeIndex=180002'),
                    text.replace('directCellSelection=1','directCellSelection=0')):
            with self.assertRaises(ValueError):collect(bad,require_wake=True)

    def test_archived_sparse_hot_column_cannot_be_approved(self):
        from moving_window import collect
        text=(Path(__file__).parent/'fixtures/moving-window-protected-162215-failed.log').read_text()
        report=collect(text,base_cells=2400)
        self.assertTrue(report['linear_mapping_gate'] and report['coverage_gate'] and report['coarsening_gate'])
        self.assertTrue(all(r['wakeCells']==48 and r['wakeCoveredCells']==0 for r in report['records']))
        with self.assertRaises(ValueError):collect(text,base_cells=2400,require_wake=True)

    def test_native_collection_failure_is_saved_before_large_case(self):
        from moving_window import smoke
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)
            with patch('moving_window.subprocess.run'), patch('moving_window.collect',side_effect=ValueError('Missing direct cell selection evidence')):
                with self.assertRaisesRegex(ValueError,'Missing direct'):smoke(work,'utility',True)
            report=json.loads((work/'movingWindowSmokeReview.json').read_text())
            self.assertFalse(report['complete'])
            self.assertFalse(report['passed'])
            self.assertFalse(report['large_case_started'])
            self.assertEqual(report['error'],'Missing direct cell selection evidence')

    def test_protected_smoke_uses_hot_column_and_zero_liquid_background(self):
        import subprocess
        from moving_window import smoke
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)
            with patch('moving_window.subprocess.run',side_effect=subprocess.CalledProcessError(1,['blockMesh'])):
                with self.assertRaises(subprocess.CalledProcessError):smoke(work,'utility',True)
            text=(work/'movingWindowSmoke/0.00018/T').read_text()
            self.assertEqual(text.count('\n1600\n'),48)
            self.assertIn('internalField uniform 0;', (work/'movingWindowSmoke/0.00018/epsilon1').read_text())
            self.assertIn('protectWake true;', (work/'movingWindowSmoke/system/movingWindowAuditDict').read_text())

    def test_moving_prototype_archive_contains_quality_and_partial_report(self):
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory)/'moving-window';work.mkdir()
            (work/'movingWindowReview.json').write_text('{"complete":false}')
            (work/'movingWindow_step1_quality.log').write_text('failure evidence')
            _,manifest=package(work,exit_code=1)
            self.assertEqual(manifest['missing_files'],[])
            self.assertEqual({f['source'] for f in manifest['files']},{'movingWindowReview.json','movingWindow_step1_quality.log'})

class MovingCFDPilotTests(unittest.TestCase):
    def fixture(self):
        lines=[]
        for time in (.0001801,.0001802):
            row=dict(schema=1,time=time,cells=1400000,changed=1,centreX=-100e-6+time,centreZ=0,
                requested=10000,wakeBefore=20000,wakeAfter=160000,wakeMissed=0,
                metalBefore=3e-10,metalAfter=3e-10,thermalProxyBefore=5,thermalProxyAfter=5)
            lines.append('M247_MOVING_CFD '+' '.join(f'{k}={v}' for k,v in row.items()))
        return '\n'.join(lines)

    def test_full_solver_mapping_screen_rejects_drift_and_missing_wake(self):
        from moving_cfd import mapping_gate
        good=mapping_gate(self.fixture())
        self.assertTrue(good['coverage_gate'] and good['topology_gate'] and good['mapping_screen'])
        self.assertFalse(mapping_gate(self.fixture().replace('wakeMissed=0','wakeMissed=1'))['coverage_gate'])
        self.assertFalse(mapping_gate(self.fixture().replace('thermalProxyAfter=5','thermalProxyAfter=5.01'))['mapping_screen'])
        self.assertFalse(mapping_gate(self.fixture().replace('changed=1','changed=0'))['topology_gate'])
        for bad in ('',self.fixture().replace('cells=1400000','cells=2000001'),
                    self.fixture().replace('centreZ=0','centreZ=1e-5'),
                    self.fixture().replace('thermalProxyAfter=5','thermalProxyAfter=nan')):
            with self.assertRaises(ValueError):mapping_gate(bad)

    def test_full_solver_state_requires_every_step_and_bounds(self):
        from moving_cfd import mapping_gate,state_gate
        mapping=mapping_gate(self.fixture())
        text='\n'.join('M247_MOVING_CFD_STATE schema=1 time='+str(r['time'])+
            ' alphaMin=0 alphaMax=1 epsilonMin=0 epsilonMax=1 Tmin=1300 Tmax=4100 Umax=78 divL1=0.01 divMax=100 invalid=0' for r in mapping['records'])
        self.assertTrue(state_gate(text,mapping)['continuity_screen'])
        self.assertFalse(state_gate(text.replace('divL1=0.01','divL1=0.1'),mapping)['continuity_screen'])
        for bad in ('',text.replace('alphaMax=1','alphaMax=1.1'),text.replace('invalid=0','invalid=1')):
            with self.assertRaises(ValueError):state_gate(bad,mapping)

    def test_failed_full_solver_pilot_packages_named_solver_log(self):
        with tempfile.TemporaryDirectory() as directory:
            work=Path(directory);case=work/'movingCFD';case.mkdir()
            (case/'log.vacuumLaserbeamFoam').write_text('failed native topology evidence')
            (work/'movingCFDReview.json').write_text('{"complete":false}')
            _,manifest=package(work,exit_code=1)
            self.assertIn('movingCFD/log.vacuumLaserbeamFoam',{f['source'] for f in manifest['files']})
            self.assertIn('movingCFDReview.json',{f['source'] for f in manifest['files']})

class MovingCFDCollectionRegressionTests(unittest.TestCase):
    fixture=Path(__file__).parent/'fixtures/moving-cfd-172613'

    def test_actual_40_step_collection_recovers_explicit_tolerances(self):
        from moving_cfd import collect_case
        before=(self.fixture/'probe.json').read_bytes()
        run=json.loads((self.fixture/'run.json').read_text())
        report=collect_case(self.fixture,run['solver_sha256'])
        self.assertTrue(report['pilot_gate'])
        self.assertEqual(report['pilot']['steps'],40)
        self.assertEqual(report['metadata_used']['epsilon_tolerance'],1e-5)
        self.assertEqual(report['metadata_used']['phase_temperature_tolerance_K'],.001)
        self.assertEqual(before,(self.fixture/'probe.json').read_bytes())

    def test_missing_and_conflicting_controls_rejected(self):
        from moving_cfd import thermal_metadata
        with self.assertRaisesRegex(ValueError,'differs'):
            thermal_metadata(self.fixture,{'epsilon_tolerance':1e-4})
        with tempfile.TemporaryDirectory() as directory:
            case=Path(directory);(case/'system').mkdir()
            text=(self.fixture/'system/fvSolution').read_text()
            for bad in (text.replace('epsilonTolerance','absentTolerance'),text.replace('1e-05','0')):
                (case/'system/fvSolution').write_text(bad)
                with self.assertRaises(ValueError):thermal_metadata(case,{})

    def test_resume_recollects_without_subprocess_and_rejects_changed_input(self):
        import shutil
        from moving_cfd import resume
        from restart_audit import case_fingerprint
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); previous=root/'moving-cfd-pilot-original';previous.mkdir()
            shutil.copytree(self.fixture,previous/'movingCFD')
            source=root/'source';(source/'system').mkdir(parents=True)
            (source/'system/controlDict').write_text('original')
            solver=json.loads((self.fixture/'run.json').read_text())['solver_sha256']
            prior=dict(source_case=str(source),source_sha256=case_fingerprint(source),solver_sha256=solver,
                complete=False,pilot_gate=False,error='epsilon_tolerance',error_type='KeyError',commands=[])
            (previous/'movingCFDReview.json').write_text(json.dumps(prior))
            package(previous,exit_code=1)
            before={p.relative_to(previous):p.read_bytes() for p in previous.rglob('*') if p.is_file()}
            with patch('moving_cfd.subprocess.run',side_effect=AssertionError('CFD must not run')):
                result=resume(previous,root/'moving-cfd-collection')
            self.assertTrue(result['pilot_gate'] and result['no_cfd_advanced'] and result['collection_only'])
            self.assertNotIn('error',result)
            self.assertEqual(before,{p.relative_to(previous):p.read_bytes() for p in previous.rglob('*') if p.is_file()})
            _,manifest=package(root/'moving-cfd-collection',exit_code=0)
            self.assertEqual(manifest['wrapper_exit_code'],0)
            (previous/'movingCFD/probe.json').write_text('{}')
            with self.assertRaisesRegex(ValueError,'changed'):resume(previous,root/'other')

class MovingMeshCostTests(unittest.TestCase):
    def test_cost_requires_complete_nonnegative_matched_times(self):
        from moving_cfd import mesh_cost
        mapping={'records':[{'time':.0001802}]}
        line='M247_MOVING_MESH_COST schema=1 time=0.0001802 topologyWallMax=2 preparationWallMax=1 auditWallMax=0.5 updateWallMax=3.5'
        self.assertEqual(mesh_cost(line,mapping,True)['wall_s']['topologyWallMax'],2)
        self.assertFalse(mesh_cost('',mapping)['available'])
        for bad in ('',line.replace('topologyWallMax=2','topologyWallMax=-1'),line.replace('updateWallMax=3.5','updateWallMax=1'),line.replace('time=0.0001802','time=0.0001801')):
            with self.assertRaises(ValueError):mesh_cost(bad,mapping,True)

class MovingPilotTimeStepTests(unittest.TestCase):
    def test_invalid_timestep_rejected_before_source_access(self):
        from moving_cfd import execute
        for ns in (0,1,20):
            with self.assertRaisesRegex(ValueError,'5 or 10'):execute('missing','missing','missing',ns)

class MovingStepComparisonTests(unittest.TestCase):
    def test_provenance_and_physical_times_are_required(self):
        from compare_moving_steps import compare
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);a=root/'a.json';b=root/'b.json'
            r=dict(complete=True,pilot_gate=True,source_case='source',source_sha256={'T':'hash'},
                original_protected_review_sha256='hash',solver_sha256='binary',duration_us=.2,ranks=48,
                pilot=dict(job_wall_s=2,interval_rank_max_sum_s=2,steps=40),physical_diagnostics=[dict(time=.0001802,Umax=100)])
            a.write_text(json.dumps(r));r['pilot']=dict(job_wall_s=1,interval_rank_max_sum_s=1,steps=33)
            b.write_text(json.dumps(r));self.assertEqual(compare(a,b)['job_speedup'],2)
            r['solver_sha256']='different';b.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'provenance'):compare(a,b)

class MovingProfileTests(unittest.TestCase):
    def fixture(self):
        volume=840e-6*960e-6*640e-6
        lines=['M247_PROFILE_STATE schema=1 time=0.0001802 ranks=48 cells=1400000 invalid=0']
        for d,(n,lo,hi) in enumerate(((53,-520e-6,320e-6),(60,0,960e-6),(40,-320e-6,320e-6))):
            for j in range(n):
                v=volume/n
                row=dict(schema=1,time=.0001802,axis=d,bin=j,low=lo+(hi-lo)*j/n,high=lo+(hi-lo)*(j+1)/n,
                    volume=v,metal=v/2,liquid=v/4,metalT=v*1000,metalUx=v,metalUy=0,metalUz=0)
                lines.append('M247_PROFILE '+' '.join(f'{k}={x}' for k,x in row.items()))
        return '\n'.join(lines)+'\nEnd\n'

    def test_profiles_close_all_axis_integrals_and_reject_incomplete_input(self):
        from moving_profiles import collect
        self.assertEqual(len(collect(self.fixture())['rows']),153)
        for bad in (self.fixture().replace('End',''),self.fixture().replace('ranks=48','ranks=1'),self.fixture().replace('invalid=0','invalid=1'),self.fixture().replace('metalUy=0','metalUy=nan')):
            with self.assertRaises(ValueError):collect(bad)

    def test_profile_output_cannot_overlap_original_run(self):
        from moving_profiles import execute
        with self.assertRaisesRegex(ValueError,'overlaps'):execute(Path('/case'),Path('/other'),Path('/case/audit'),Path('/utility'))

class MovingLongPilotTests(unittest.TestCase):
    def test_invalid_duration_rejected_before_source_access(self):
        from moving_cfd import execute
        with self.assertRaisesRegex(ValueError,'duration'):execute('missing','missing','missing',5,1)

    def test_mapping_screen_uses_requested_horizon(self):
        from moving_cfd import mapping_gate
        text=MovingCFDPilotTests().fixture().replace('0.0001802','0.0001804').replace('centreX=8.02e-05','centreX=8.04e-05')
        # Construct centre exactly to avoid dependence on Python float spelling.
        lines=text.splitlines();parts=lines[-1].split();parts=[('centreX='+str(-100e-6+.0001804)) if x.startswith('centreX=') else x for x in parts];lines[-1]=' '.join(parts);text='\n'.join(lines)
        with self.assertRaises(ValueError):mapping_gate(text)
        self.assertTrue(mapping_gate(text,.0001804)['coverage_gate'])

if __name__=='__main__':
    unittest.main()
