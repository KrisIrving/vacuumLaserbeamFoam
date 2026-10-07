#!/usr/bin/env python3
"""Copy one completed, uncollated restart state into a fresh probe directory."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

VARIANTS = ('baseline', 'noRayPaths', 'quietThermal', 'thermalLegacy', 'enthalpyBounded', 'enthalpyStandard', 'enthalpyTight', 'phaseBlendNarrow', 'phaseBlendWide', 'laserProfileOff', 'laserProfileOn', 'rayTraversalReference', 'rayTraversalCached', 'raySeedReference', 'raySeedCached', 'rayPartitionReference', 'rayPartitionWeighted', 'frozenLaserReference', 'frozenLaserWeighted', 'rayImpactLegacy', 'rayImpactCorrected')

def snapshot_digest(directory):
    digest = hashlib.sha256()
    for path in sorted(p for p in directory.rglob('*') if p.is_file()):
        digest.update(path.relative_to(directory).as_posix().encode()+b'\0')
        with path.open('rb') as stream:
            while True:
                block = stream.read(1024*1024)
                if not block:
                    break
                digest.update(block)
        digest.update(b'\0')
    return digest.hexdigest()

def set_entry(path, entry, value):
    subprocess.run(['foamDictionary', str(path), '-entry', entry, '-set', str(value)],
                   check=True, stdout=subprocess.DEVNULL)

def checkpoint(rank, time):
    candidates = []
    for child in rank.iterdir():
        if not child.is_dir():
            continue
        try:
            if abs(float(child.name) - time) <= 1e-12:
                candidates.append(child)
        except ValueError:
            pass
    if len(candidates) != 1:
        raise ValueError(f'{rank}: expected one checkpoint at {time:g} s')
    return candidates[0]

def prepare(source, output, start_us, duration_us, variant, corrected_rays=False):
    corrected_rays=corrected_rays or variant=='rayImpactCorrected'
    if corrected_rays and variant not in ('rayTraversalReference','rayTraversalCached','rayImpactCorrected'):
        raise ValueError('Corrected transient pair requires traversal variants')
    source, output = source.resolve(), output.resolve()
    if not all(math.isfinite(x) for x in (start_us, duration_us)):
        raise ValueError('Times must be finite')
    if start_us < 0 or duration_us <= 0:
        raise ValueError('Start must be non-negative and duration positive')
    if variant not in VARIANTS:
        raise ValueError('Unknown variant')
    if source == output or source in output.parents or output in source.parents:
        raise ValueError('Probe must be outside the source case and its parents')
    if output.exists():
        raise ValueError(f'Output already exists (never overwritten): {output}')
    log = source/'log.vacuumLaserbeamFoam'
    if not log.is_file() or not re.search(r'^End\s*$', log.read_text(errors='replace'), re.M):
        raise ValueError('Source solver log must show a completed End')
    ranks = sorted((p for p in source.iterdir() if re.fullmatch(r'processor\d+', p.name)
                    and p.is_dir()), key=lambda p: int(p.name[9:]))
    if not ranks or [p.name for p in ranks] != [f'processor{i}' for i in range(len(ranks))]:
        raise ValueError('Requires contiguous uncollated processor0..N directories')
    start, end = start_us*1e-6, (start_us+duration_us)*1e-6
    states = [checkpoint(rank, start) for rank in ranks]
    if len({p.name for p in states}) != 1:
        raise ValueError('Checkpoint directory names differ between ranks')
    for rank, state in zip(ranks, states):
        for field in ('alpha.metal', 'T', 'U', 'p_rgh', 'epsilon1'):
            if not (state/field).is_file() and not (state/(field+'.gz')).is_file():
                raise ValueError(f'Required restart field missing: {state/field}')
        if not (rank/'constant/polyMesh').is_dir() and not (state/'polyMesh').is_dir():
            raise ValueError(f'Mesh missing at constant or restart time: {rank}')
    # This first probe intentionally stays inside the original laser table.
    # Never silently hold a clamped laser at the end of its path.
    position = source/'constant/timeVsLaserPosition'
    path_times = [float(x) for x in re.findall(r'\(\s*([-+0-9.eE]+)\s+\(', position.read_text())]
    power = source/'constant/timeVsLaserPower'
    power_times = [float(x) for x in re.findall(r'\(\s*([-+0-9.eE]+)\s+[-+0-9.eE]+\s*\)', power.read_text())]
    if not path_times or not power_times or start < min(path_times)-1e-12 or end > min(max(path_times), max(power_times))+1e-12:
        raise ValueError('Probe interval exceeds supplied laser tables; choose e.g. 180–182 us')
    for relative in ('constant', 'system'):
        if not (source/relative).is_dir():
            raise ValueError(f'Missing {relative} directory')
    output.mkdir(parents=True)
    for relative in ('constant', 'system'):
        shutil.copytree(source/relative, output/relative)
    for rank, state in zip(ranks, states):
        destination = output/rank.name
        destination.mkdir()
        if (rank/'constant').is_dir():
            shutil.copytree(rank/'constant', destination/'constant')
        shutil.copytree(state, destination/state.name)
    source_snapshot_sha256 = snapshot_digest(output)
    control = output/'system/controlDict'
    set_entry(control, 'frozenLaserProbe', 'off')
    for key, value in {
        'startFrom':'startTime', 'startTime':f'{start:.12g}',
        'stopAt':'endTime', 'endTime':f'{end:.12g}',
        'writeControl':'adjustableRunTime',
        'writeInterval':f'{duration_us*1e-6/2:.12g}',
        'purgeWrite':0, 'runTimeModifiable':'yes',
    }.items():
        set_entry(control, key, value)
    set_entry(output/'constant/vacuumProperties', 'performanceDiagnostics', 'true')
    set_entry(output/'constant/vacuumProperties', 'writeDiagnostics', 'true')
    for key in ('preserveRayHandoffSample','consistentRayTermination'):
        set_entry(output/'constant/LaserProperties',key,'true' if corrected_rays else 'false')
    if corrected_rays or variant=='rayImpactLegacy':
        set_entry(control,'writePrecision',17)
        set_entry(control,'writeCompression','off')
    blend_variant = variant in ('phaseBlendNarrow','phaseBlendWide')
    seed_variant = variant in ('raySeedReference','raySeedCached')
    partition_variant = variant in ('rayPartitionReference','rayPartitionWeighted','frozenLaserReference','frozenLaserWeighted','rayImpactLegacy','rayImpactCorrected')
    traversal_variant = partition_variant or seed_variant or variant in ('rayTraversalReference','rayTraversalCached')
    laser_variant = traversal_variant or variant in ('laserProfileOff','laserProfileOn')
    tight_variant = blend_variant or laser_variant or variant=='enthalpyTight'
    blend_width = 0.005 if variant=='phaseBlendNarrow' else 0.01 if variant=='phaseBlendWide' else 0
    set_entry(output/'constant/LaserProperties', 'recordRayPaths',
              'false' if blend_variant or laser_variant or variant in ('noRayPaths', 'thermalLegacy', 'enthalpyBounded', 'enthalpyStandard', 'enthalpyTight') else 'true')
    set_entry(output/'constant/LaserProperties', 'laserPerformanceDiagnostics',
              'true' if traversal_variant or variant=='laserProfileOn' else 'false')
    set_entry(output/'constant/LaserProperties', 'cachedRayTraversal',
              'true' if partition_variant or seed_variant or variant=='rayTraversalCached' else 'false')
    set_entry(output/'constant/LaserProperties', 'cartesianRaySeedSearch',
              'true' if variant=='raySeedCached' else 'false')
    set_entry(output/'system/fvSolution', 'MELTING/thermalCorrectorLogging',
              'false' if variant == 'quietThermal' else 'true')
    set_entry(output/'system/fvSolution', 'MELTING/boundedEnthalpyCorrection',
              'true' if blend_variant or laser_variant or variant in ('enthalpyBounded', 'enthalpyStandard', 'enthalpyTight') else 'false')
    set_entry(output/'system/fvSolution', 'MELTING/thermalResidualDiagnostics',
              'true' if blend_variant or laser_variant or variant in ('thermalLegacy', 'enthalpyBounded', 'enthalpyStandard', 'enthalpyTight') else 'false')
    set_entry(output/'system/fvSolution', 'MELTING/phaseTemperatureBlendHalfWidth', str(blend_width))
    phase_tolerance = '0.001' if tight_variant else '0.01'
    set_entry(output/'system/fvSolution', 'MELTING/phaseTemperatureTolerance', phase_tolerance)
    if blend_variant or laser_variant or variant in ('enthalpyStandard', 'enthalpyTight'):
        set_entry(output/'system/fvSolution', 'MELTING/epsilonTolerance',
                  '1e-5' if tight_variant else '1e-4')
        # Keep the original binary restart readable; only new output is ASCII
        # so the review collector can compare fields without extra libraries.
        set_entry(control, 'writeFormat', 'ascii')
    metadata = dict(schema=1, source=str(source), variant=variant,
                    start_s=start, end_s=end, duration_us=duration_us,
                    ranks=len(ranks), checkpoint=states[0].name,
                    source_snapshot_sha256=source_snapshot_sha256,
                    phase_temperature_tolerance_K=float(phase_tolerance),
                    epsilon_tolerance=(1e-5 if tight_variant else 1e-4)
                        if blend_variant or laser_variant or variant in ('enthalpyBounded', 'enthalpyStandard', 'enthalpyTight') else None,
                    laser_performance_diagnostics=traversal_variant or variant=='laserProfileOn',
                    cached_ray_traversal=partition_variant or seed_variant or variant=='rayTraversalCached',
                    cartesian_ray_seed_search=variant=='raySeedCached',
                    preserve_ray_handoff_sample=corrected_rays,
                    consistent_ray_termination=corrected_rays,
                    phase_temperature_blend_half_width=blend_width,
                    purpose='mature-state performance and matched physics regression')
    (output/'probe.json').write_text(json.dumps(metadata, indent=2)+'\n')
    return metadata

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--start-us', type=float, default=180)
    parser.add_argument('--duration-us', type=float, default=2)
    parser.add_argument('--variant', choices=VARIANTS, default='baseline')
    parser.add_argument('--corrected-rays',action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.source, args.output, args.start_us,
                                 args.duration_us, args.variant,args.corrected_rays), indent=2))
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Preparation failed: {error}\n')

if __name__ == '__main__':
    main()
