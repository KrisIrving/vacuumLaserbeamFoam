"""Validate source-hold diagnostics and reconcile actual optical update calls."""
from collect_probe import parse_records
from collect_laser_profile import summarize,validate_rank_rows

def validate_refresh(records,start,end,steps,interval):
    required=('schema','time','interval','refreshed','heldAge_s','preRefreshAge_s','maxAlphaChange','displacementCells')
    if len(records)!=steps or not records or any(any(k not in r for k in required) for r in records):
        raise ValueError('Incomplete per-step laser refresh diagnostics(single outer corrector required)')
    previous=start
    for r in records:
        if r['schema']!=1 or r['interval']!=interval or r['refreshed'] not in (0,1) or r['time']<=previous:
            raise ValueError('Invalid laser refresh mode/time')
        if any(r[k]<0 for k in required if k not in ('schema','time','interval')):
            raise ValueError('Negative laser refresh diagnostic')
        if r['refreshed']==1 and r['heldAge_s']!=0:raise ValueError('Fresh source reports held age')
        if not r['refreshed'] and (interval==1 or r['heldAge_s']>=25e-9*(1+1e-8) or r['maxAlphaChange']>=.1*(1+1e-8) or r['displacementCells']>=.25*(1+1e-8)):
            raise ValueError('Source hold exceeds experiment bounds')
        previous=r['time']
    if records[0]['refreshed']!=1 or abs(records[-1]['time']-end)>1e-12:
        raise ValueError('Missing first refresh or complete interval')
    for t in (start+(end-start)/2,end):
        matches=[r for r in records if abs(r['time']-t)<1e-12]
        if len(matches)!=1 or matches[0]['refreshed']!=1:raise ValueError('Output sample source is stale')
    updated=sum(int(r['refreshed']) for r in records)
    return dict(updates=updated,held_steps=steps-updated,update_fraction=updated/steps,max_held_age_s=max(r['heldAge_s'] for r in records),max_held_alpha_change=max((r['maxAlphaChange'] for r in records if not r['refreshed']),default=0),max_held_displacement_cells=max((r['displacementCells'] for r in records if not r['refreshed']),default=0),note='Bounds are experimental refresh triggers, not a physical acceptance guarantee.')

def collect_refresh(case,metadata,performance,interval):
    text=(case/'log.vacuumLaserbeamFoam').read_text()
    result=validate_refresh(parse_records(text,'LASER_REFRESH_DIAGNOSTICS'),metadata['start_s'],metadata['end_s'],performance['steps'],interval)
    records=parse_records(text,'LASER_PERF_DIAGNOSTICS');rank_rows=parse_records(text,'LASER_RANK_DIAGNOSTICS')
    times=[r['time'] for r in parse_records(text,'VACUUM_DIAGNOSTICS')]
    if len(records)!=len(times) or any(abs(r['time']-t)>1e-12 for r,t in zip(records,times)):
        raise ValueError('Missing optical profiling output samples')
    records=[dict(r,time=t) for r,t in zip(records,times)]
    result['optics']=summarize(records,times,metadata['ranks'],result['updates'])
    validate_rank_rows(rank_rows,records,metadata['ranks'])
    if result['optics']['counts']['callsMean']!=result['updates']:
        raise ValueError('Optical calls differ from refresh decisions')
    return result
