#!/usr/bin/env python3
"""Bundle small review files with explicit run/variant names; never copy fields."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import tarfile
from prepare_probe import VARIANTS
VARIANTS = VARIANTS+('movingCFD','fullMelt','localMelt')

FILES = {
    'log.vacuumLaserbeamFoam': 'solver.log',
    'probe.json': 'probe.json', 'run.json': 'run.json',
    'capture.log': 'capture.log', 'captureRun.json': 'captureRun.json',
    'system/fvSolution': 'fvSolution', 'system/controlDict': 'controlDict',
    'system/decomposeParDict': 'decomposeParDict',
    'constant/vacuumProperties': 'vacuumProperties',
    'constant/LaserProperties': 'LaserProperties',
    'constant/transportProperties': 'transportProperties',
}
BUILD_FILES = ('build.log', 'buildEnvironment.txt', 'solverCheck.json', 'cachedSearchTest.log', 'collection.log', 'partition.log', 'partitionWeight.json', 'initialPartitionCheck.json', 'frozenInputCheck.json', 'auditInputs.json', 'auditBinary.txt', 'sourceRegionAudit.log', 'legacyRegionAudit.log', 'correctedRegionAudit.log', 'sourceKeyholeDepth.csv', 'sourceMoltenExtent.csv', 'regionAuditReview.json', 'regionEnvelopes.csv')

BUILD_FILES += ('previewInputs.json','previewBinary.txt','localRefinementReview.json',
    'reconstructPreview.log','coarseMoments.log','coarseCheckMesh.log',
    'resumeInputs.json','resumeCoarseMoments.log','resumeCoarseCheckMesh.log') + tuple(
    f'localRefine{layers}_{suffix}' for layers in (4,10) for suffix in
    ('topoSetDict','selection.log','refinement.log','moments.log','checkMesh.log','concavity.log'))

BUILD_FILES += ('restartAuditInputs.json','localRestartReview.json') + tuple(
    f'{case}_{suffix}' for case in ('coarse','localRefine4','localRefine10')
    for suffix in ('restart.log','restartCheckMesh.log'))

BUILD_FILES += ('fluxPilotInputs.json','fluxPilotReview.json') + tuple(
    f'localProjected_{suffix}.log' for suffix in
    ('before','projection','after','decompose','pilot','reconstruct','final'))

LOCAL_OPTICS_VARIANTS=('localOpticsCoarse','localOpticsFine','localOpticsMapped')
LOCAL_OPTICS_INPUT_VARIANTS=('localOpticsAlphaMapped','localOpticsNormalMapped','localOpticsResistivityMapped')
BUILD_FILES += ('localOpticsInputReview.json',) + tuple(
    f'{case}_{suffix}.log' for case in LOCAL_OPTICS_INPUT_VARIANTS for suffix in ('decompose','traceJob'))
BUILD_FILES += ('localOpticsInputs.json','localOpticsReview.json','opticalMappingAudit.json') + tuple(
    f'{case}_{suffix}.log' for case in LOCAL_OPTICS_VARIANTS for suffix in
    ('decompose','captureJob','captureReconstruct','mapping','traceJob'))

BUILD_FILES += ('movingPilotStatus.json','movingLongPairStatus.json','movingLongCollectionInputs.json','movingLongInventory.json')
BUILD_FILES += tuple(f'{variant}Long{suffix}.json' for variant in ('reference','candidate') for suffix in ('Run','Probe'))
BUILD_FILES += tuple(f'{variant}Long{suffix}.log' for variant in ('reference','candidate') for suffix in ('Solver','Build','Collection','Decompose','Pilot'))

BUILD_FILES += ('movingProfileComparison.json','referenceProfiles.log','candidateProfiles.log')

BUILD_FILES += ('movingStepComparison.json','movingStepReference.json','movingStepCandidate.json')

BUILD_FILES += ('movingCFDReview.json','movingCFD_dynamicMeshDict','movingCFD_windowDict','movingCFD_decompose.log','movingCFD_pilot.log')

BUILD_FILES += ('movingWindowSmokeReview.json','movingWindowSmoke_blockMesh.log','movingWindowSmoke_updates.log')
BUILD_FILES += ('movingWindowReview.json','movingWindow_dynamicMeshDict','movingWindow_auditDict','movingWindow_updates.log') + tuple(
    f'movingWindow_step{step}_{suffix}.log' for step in range(1,9) for suffix in ('quality','concavity'))

BUILD_FILES += ('regionalAcceptance.json','regionalAcceptanceStatus.json','regionalBinary.txt')
BUILD_FILES += tuple(f'{variant}_{suffix}' for variant in ('regionalGain','regionalLoss','regionalFlow') for suffix in
    ('thermalRegion_blockMesh.log','flowRegion_blockMesh.log','setFields.log','serial.log',
     'decompose.log','parallel.log','inputHashes.json','parallelInputHashes.json','fixtureInputs.json'))

BUILD_FILES += ('localMeltAudit_help.log','localMelt_initializeCut.log','subsetMesh_help.log','localMeltPairReview.json','localMeltPairStatus.json','localMeltSourceHashes.json','localMelt_selectionDict','localMeltPairBinary.txt')
BUILD_FILES += tuple(f'{variant}_{stage}.log' for variant in ('fullMelt','localMelt') for stage in
    ('reconstructInitial','initial','select','subset','checkMesh','decompose','solver','reconstructFinal','mid','final','interface','keyhole'))
BUILD_FILES += ('fullMelt_keyhole.csv','localMelt_keyhole.csv')

def package(work, output=None, exit_code=None):
    work = Path(work).resolve()
    if not work.is_dir():
        raise ValueError(f'Run directory missing: {work}')
    tag = re.sub(r'[^A-Za-z0-9_.-]', '_', work.name)
    output = Path(output).resolve() if output else work.parent/f'M247_{tag}_review.tar.gz'
    if output.exists():
        raise ValueError(f'Archive already exists (never overwritten): {output}')
    entries, missing, found = [], [], []
    def add(relative, archive_name):
        path = work/relative
        resolved = path.resolve()
        if work not in resolved.parents:
            raise ValueError(f'Review file escapes run directory: {relative}')
        if not path.is_file():
            missing.append(relative)
            return
        data = path.read_bytes()
        entries.append((archive_name, data))
        found.append(dict(source=relative, archive_name=archive_name,
                          bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    variants = [v for v in VARIANTS+LOCAL_OPTICS_VARIANTS+LOCAL_OPTICS_INPUT_VARIANTS if (work/v).is_dir()]
    if not variants and not any((work/name).is_file() for name in BUILD_FILES):
        raise ValueError('No recognised probe variant directories or build/preflight files')
    for name in BUILD_FILES:
        if (work/name).is_file():
            add(name, f'{tag}_{name}')
    for variant in variants:
        for relative, suffix in FILES.items():
            if relative in ('capture.log','captureRun.json') and not (work/variant/relative).is_file():
                continue
            add(f'{variant}/{relative}', f'{tag}_{variant}_{suffix}')
        if (work/variant/'solverCheck.json').is_file():
            add(f'{variant}/solverCheck.json', f'{tag}_{variant}_solverCheck.json')
    for name in ('frozenLaserReview.json', 'rayPartitionReview.json', 'comparison.json', 'diagnosticComparison.csv', 'thermalValidation.json', 'fieldComparison.csv', 'fieldLocalization.json', 'fieldRegions.csv', 'worstCells.csv', 'phaseBlendReview.json', 'phaseBlendFields.csv', 'phaseBlendDiagnostics.csv', 'phaseBlendLocalization.json', 'phaseBlendRegions.csv', 'phaseBlendWorstCells.csv', 'rayTraversalReview.json', 'laserProfileReview.json', 'laserProfileStages.csv', 'laserProfileFields.csv', 'laserExchangeDetails.csv', 'laserRankWork.csv'):
        if (work/'comparison'/name).is_file():
            add(f'comparison/{name}', f'{tag}_comparison_{name}')
    if not entries:
        raise ValueError('No review files available')
    manifest = dict(schema=1, run_directory=str(work), run_tag=tag,
                    variants=variants, wrapper_exit_code=exit_code,
                    files=found, missing_files=missing,
                    note='Collection only; incomplete or failed runs are not a validation PASS.')
    entries.append(('manifest.json', (json.dumps(manifest,indent=2)+'\n').encode()))
    # Exclusive creation preserves existing archives. Errors may leave a partial
    # archive: never treat packaging failure as successful collection.
    with output.open('xb') as stream:
        with tarfile.open(fileobj=stream, mode='w:gz') as archive:
            for name, data in entries:
                info = tarfile.TarInfo(name)
                info.size, info.mode = len(data), 0o644
                archive.addfile(info, io.BytesIO(data))
    return output, manifest

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--exit-code', type=int)
    args = parser.parse_args()
    try:
        output, manifest = package(args.work, args.output, args.exit_code)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Packaging failed: {error}\n')
    print(f'Review archive: {output}', flush=True)
    print('Send this single .tar.gz file. Variant names are included in every file name.', flush=True)
    if manifest['missing_files']:
        print('Some review files are missing; see manifest.json. This archive may describe a failed/incomplete run.', flush=True)

if __name__ == '__main__':
    main()
