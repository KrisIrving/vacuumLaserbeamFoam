#!/usr/bin/env python3
"""Geometry-corrected M247 1.5 mm pilot, retaining V1 for provenance."""
from pathlib import Path
import json
import shutil
import track1500_pilot as pilot

pilot.TEMPLATE=(Path(__file__).resolve().parents[2]/
    'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_track1500um6umV2')
pilot.CELLS=3814272
pilot.FINE=((-240e-6,1680e-6),(180e-6,720e-6),(-192e-6,192e-6))
pilot.PILOT_VARIANT='track1500PilotDEM'

original_execute=pilot.execute

def prepare_case(case,work):
    stage=work/'dem'
    handoff=json.loads((stage/'handoff.json').read_text())
    if not handoff.get('pilotOnly') or handoff.get('productionApproved'):
        raise ValueError('Expected verified pilot-only DEM handoff')
    shutil.copy2(stage/'powderManifest.json',case/'constant/powderManifest.json')
    shutil.copy2(stage/'powderParticles.csv',case/'constant/powderParticles.csv')
    shutil.copy2(stage/'setFieldsDict',case/'system/setFieldsDict')
    shutil.copy2(stage/'handoff.json',case/'demHandoff.json')

def powder_gate(manifest):
    from m247_dem_handoff import validate_manifest
    validate_manifest(manifest)

pilot.PREPARE_CASE=prepare_case
pilot.POWDER_GATE=powder_gate

def execute_with_dem_gate(work):
    if not (work/'dem/handoff.json').is_file():
        raise ValueError('V2 requires a verified DEM review archive; no CFD launched')
    original_execute(work)

pilot.execute=execute_with_dem_gate

if __name__=='__main__':pilot.main()

