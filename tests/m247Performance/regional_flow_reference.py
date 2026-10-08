"""Independent 1D open-boundary projection and source bookkeeping references.
Not a substitute for native OpenFOAM compilation or 3D pressure/VOF validation.
"""
import math


def project_line(predictor,conductance,outlet_pressure=0):
    """Left prescribed flux; right prescribed correction pressure.

    conductance is positive dt/rho * area/distance on internal/right faces.
    Exact recurrence solution of the 1D pressure Poisson system.
    """
    if len(predictor)<2 or len(conductance)!=len(predictor)-1:
        raise ValueError('Invalid line addressing')
    if any(not math.isfinite(x) for x in (*predictor,*conductance,outlet_pressure)) or min(conductance)<=0:
        raise ValueError('Invalid projection data')
    target=predictor[0];pressure=[0]*len(conductance)
    pressure[-1]=outlet_pressure+(target-predictor[-1])/conductance[-1]
    for i in range(len(pressure)-2,-1,-1):
        pressure[i]=pressure[i+1]-(predictor[i+1]-target)/conductance[i]
    corrected=[predictor[0]]
    for i in range(1,len(pressure)):
        corrected.append(predictor[i]-conductance[i-1]*(pressure[i]-pressure[i-1]))
    corrected.append(predictor[-1]-conductance[-1]*(outlet_pressure-pressure[-1]))
    return pressure,corrected


def source_delta(dt,laser,evaporation,radiation_loss,advection_gain,local_conduction,global_conduction,global_has_sources=False):
    if global_has_sources:raise ValueError('Global prediction must contain conduction only')
    if any(not math.isfinite(x) for x in (dt,laser,evaporation,radiation_loss,advection_gain,local_conduction,global_conduction)) or dt<=0 or min(laser,evaporation)<0:
        raise ValueError('Invalid source densities')
    result=dt*(laser-evaporation-radiation_loss+advection_gain+local_conduction-global_conduction)
    if not math.isfinite(result):raise ValueError('Source delta overflow')
    return result
