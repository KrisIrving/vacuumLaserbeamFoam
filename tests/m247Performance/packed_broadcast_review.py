"""Strict gates for packed optical payload; no physics tolerance relaxation."""
import math,re
from collect_probe import parse_records
from collect_laser_profile import summarize,validate_rank_rows

def normalized_optical_settings(text):
    pattern=r'(?m)^[ \t]*packedRayBroadcast[ \t]+(?:true|false|on|off|0|1)[ \t]*;'
    if len(re.findall(pattern,text))!=1:
        raise ValueError('Exactly one packedRayBroadcast setting required')
    return re.sub(pattern,'packedRayBroadcast <variant>;',text)

def validate_mode(text,enabled):
    if parse_records(text,'PACKED_RAY_BROADCAST')!=[dict(schema=1,enabled=int(enabled))]:
        raise ValueError('Wrong packed ray broadcast runtime mode')

def frozen_trace(text,enabled):
    validate_mode(text,enabled)
    if not re.search(r'^End\s*$',text,re.M) or re.search(r'^Time\s*=',text,re.M):
        raise ValueError('Frozen optical job incomplete or advanced time')
    records=parse_records(text,'FROZEN_LASER_DIAGNOSTICS')
    if len(records)!=1:raise ValueError('Exactly one frozen trace required')
    row=records[0]
    if row.get('schema')!=1 or row.get('calls')!=1 or abs(row.get('time',-1)-.00018)>1e-12:
        raise ValueError('Wrong frozen trace checkpoint/call count')
    if any(row.get(x)!=0 for x in ('advancedTime','Tchange','alphaChange','epsilonChange','Uchange')):
        raise ValueError('Frozen non-optical state evolved')
    power=row.get('depositedPower',float('nan'))
    if not math.isfinite(power) or power<=0:raise ValueError('Invalid frozen deposited power')
    perf=parse_records(text,'LASER_PERF_DIAGNOSTICS')
    profile=summarize(perf,[.00018],48,1)
    validate_rank_rows(parse_records(text,'LASER_RANK_DIAGNOSTICS'),perf,48)
    return dict(diagnostics=row,profile=profile)

def require_exact_fields(fields):
    if not fields or any(x['max_abs_difference']!=0 for x in fields):
        raise ValueError('Packed transport changed frozen optical inputs/outputs')

def require_same_work(reference,candidate):
    if reference['counts']!=candidate['counts']:
        raise ValueError('Packed transport changed optical work/ray counts')
