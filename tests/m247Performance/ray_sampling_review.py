"""Report explicit sampling error; no implicit acceptance tolerance."""
import re,math

def normalized_settings(text):
    pattern=r'(?m)^[ \t]*nAngular[ \t]+[0-9]+[ \t]*;'
    if len(re.findall(pattern,text))!=1:raise ValueError('Exactly one angular count required')
    return re.sub(pattern,'nAngular <variant>;',text)

def validate_ray_count(profile,updates,rays):
    if profile['counts']['initialRaysMean']!=updates*rays:
        raise ValueError('Actual emitted ray count differs from requested sampling')

def error_summary(report):
    snapshots=[]
    for label,time in (('mid',.000185),('final',.00019)):
        inventory=report['field_comparisons'][label]['inventories']
        a=inventory['reference']['liquid_volume_m3'];b=inventory['candidate']['liquid_volume_m3']
        depth=next(x for x in report['keyhole_comparisons'] if abs(x['time_s']-time)<1e-12)
        diagnostics=[x for x in report['diagnostic_differences'] if abs(x['time']-time)<1e-12]
        snapshots.append(dict(time_s=time,
            keyhole_depth_difference_um=depth['depth_difference_um'],
            keyhole_depth_difference_percent=100*abs(depth['depth_difference_um'])/abs(depth['reference_depth_um']) if depth['reference_depth_um'] else None,
            liquid_volume_difference_percent=100*abs(b-a)/abs(a) if a else None,
            diagnostic_difference_percent={x['metric']:100*x['relative_difference'] if x['relative_difference'] is not None else None for x in diagnostics}))
    return dict(reference_rays=1536,candidate_rays=384,angular_samples=(96,24),radial_samples=16,
        snapshots=snapshots,production_approved=False,error_budget=dict(keyhole_depth_percent=5,liquid_volume_percent=5,Tmax_percent=10),
        agreed_error_budget_gate=budget_passes(snapshots,report['measurement_quality_gate']),
        note='Same radial quadrature and nominal summed source power; coarser angular coverage changes local absorption. Relative agreement to8um baseline is not experimental accuracy.')

def budget_passes(snapshots,measurement_quality):
    if not measurement_quality or len(snapshots)!=2:return False
    for snapshot in snapshots:
        for value,limit in ((snapshot['keyhole_depth_difference_percent'],5),
            (snapshot['liquid_volume_difference_percent'],5),
            (snapshot['diagnostic_difference_percent'].get('Tmax'),10)):
            if value is None or not math.isfinite(value) or value<0 or value>limit:return False
    return True
