#!/usr/bin/env python3
"""Geometry-corrected M247 1.5 mm pilot, retaining V1 for provenance."""
from pathlib import Path
import track1500_pilot as pilot

pilot.TEMPLATE=(Path(__file__).resolve().parents[2]/
    'tutorials/vacuumLaserbeamFoam/M247_0p6Pa_track1500um6umV2')
pilot.CELLS=3814272
pilot.FINE=((-240e-6,1680e-6),(180e-6,720e-6),(-192e-6,192e-6))

if __name__=='__main__':pilot.main()
