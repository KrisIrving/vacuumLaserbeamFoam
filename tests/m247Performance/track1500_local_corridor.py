#!/usr/bin/env python3
"""DEM 50us local-fine-corridor experiment; never a full-track case."""
from pathlib import Path
import track1500_pilot_v2 as v2
from local_corridor_mesh import CELLS, local_mesh_dictionary

pilot=v2.pilot
pilot.CELLS=CELLS
pilot.FINE=((-240e-6,300e-6),(180e-6,720e-6),(-192e-6,192e-6))
pilot.PILOT_VARIANT='track1500LocalCorridorDEM'
pilot.STATIC_LOCAL_CORRIDOR=True
original_prepare=v2.prepare_case


def prepare_case(case,work):
    original_prepare(case,work)
    mesh=case/'system/blockMeshDict'
    mesh.write_text(local_mesh_dictionary(mesh.read_text(encoding='utf-8')),
                    encoding='utf-8',newline='\n')


pilot.PREPARE_CASE=prepare_case

if __name__=='__main__':
    pilot.main()

