"""Read existing full/local CSV snapshots; localize differences without CFD."""
import argparse,json,math,heapq
from pathlib import Path
from local_melt_pair import rows,key,inside,save
from collect_probe import parse_records
from collect_laser_profile import summarize,validate_rank_rows

METRICS=('T','alpha','epsilon','U','p_rgh')
REGIONS=('all','gasBoth','metalEither','interfaceEither','liquidMetalEither','coldCutReservoir')

def regions(a,b,bounds):
    result=['all']
    if max(a['alpha'],b['alpha'])<.01:result.append('gasBoth')
    if max(a['alpha'],b['alpha'])>=.5:result.append('metalEither')
    if any(.01<=x['alpha']<=.99 for x in (a,b)):result.append('interfaceEither')
    if any(x['alpha']>=.05 and x['epsilon']>=.05 for x in (a,b)):result.append('liquidMetalEither')
    if bounds.get('_has_cut', True) and a['y']<=bounds['ymin']+48e-6:result.append('coldCutReservoir')
    return result

def delta(a,b,m):
    return math.sqrt(sum((b[x]-a[x])**2 for x in ('Ux','Uy','Uz'))) if m=='U' else abs(b[m]-a[m])

def localize(reference,candidate,bounds):
    ref={key(x):x for x in rows(reference) if inside(x,bounds)}
    result={name:dict(cells=0,volume_m3=0,phaseFlipCells=0,fields={m:dict(max_abs=0,sum_squared_volume=0) for m in METRICS}) for name in REGIONS}
    worst={m:[] for m in METRICS};sequence=0
    for b in rows(candidate):
        k=key(b)
        if k not in ref:raise ValueError('Duplicate/unmatched candidate coordinate')
        a=ref.pop(k)
        if abs(a['volume']-b['volume'])>1e-10*a['volume']:raise ValueError('Cell volume mismatch')
        mask=regions(a,b,bounds);dv={m:delta(a,b,m) for m in METRICS}
        location=dict(x_um=a['x']*1e6,y_um=a['y']*1e6,z_um=a['z']*1e6,reference_alpha=a['alpha'],candidate_alpha=b['alpha'],reference_epsilon=a['epsilon'],candidate_epsilon=b['epsilon'],reference_T=a['T'],candidate_T=b['T'],regions=mask)
        for name in mask:
            bucket=result[name];bucket['cells']+=1;bucket['volume_m3']+=a['volume']
            bucket['phaseFlipCells']+=int((a['epsilon']>=.5)!=(b['epsilon']>=.5))
            for m in METRICS:
                stat=bucket['fields'][m];stat['sum_squared_volume']+=dv[m]**2*a['volume']
                if dv[m]>stat['max_abs']:stat.update(max_abs=dv[m],maximum_location=location)
        for m in METRICS:
            item=(dv[m],sequence,dict(metric=m,absolute_difference=dv[m],**location))
            if len(worst[m])<20:heapq.heappush(worst[m],item)
            elif dv[m]>worst[m][0][0]:heapq.heapreplace(worst[m],item)
        sequence+=1
    if ref:raise ValueError('Missing retained reference cells')
    for bucket in result.values():
        for stat in bucket['fields'].values():
            value=stat.pop('sum_squared_volume');stat['volume_weighted_rms']=math.sqrt(value/bucket['volume_m3']) if bucket['volume_m3'] else None
    return dict(regions=result,worst_cells={m:[x[2] for x in sorted(v,reverse=True)] for m,v in worst.items()},note='Overlapping descriptive regions, not acceptance thresholds. p_rgh differences include any pressure offset. Phase flips use epsilon>=0.5; liquid-metal mask uses alpha>=0.05 and epsilon>=0.05 in either run.')

def align_output_times(records,times):
    # Formatting round-off only; no nearest-time selection or interpolation.
    if len(records)!=len(times) or any(abs(r.get('time',-1)-t)>1e-12 for r,t in zip(records,times)):
        raise ValueError('Laser profile/output times differ beyond serialization round-off')
    return [dict(r,time=t) for r,t in zip(records,times)]

def optical_calls(variant_report):
    steps=variant_report['performance']['steps']
    refresh=variant_report.get('laser_refresh')
    if refresh is None:return steps
    updates=refresh['updates'];held=refresh['held_steps']
    if (not isinstance(updates,int) or not isinstance(held,int)
        or updates<1 or held<0 or updates+held!=steps):
        raise ValueError('Refresh update/hold counts do not cover CFD steps')
    return updates

def collect(source,work):
    source=Path(source).resolve();work=Path(work).resolve()
    if source==work or source in work.parents or work in source.parents:raise ValueError('Output overlaps existing run')
    report=json.loads((source/'localMeltPairReview.json').read_text())
    if not report.get('complete') or not report.get('source_unchanged'):raise ValueError('Completed matched pair required')
    work.mkdir(exist_ok=True)
    bounds=dict(report['window']['bounds'])
    bounds['_has_cut']=any(x.get('cutFaces',0)>0 for x in report['localMelt']['snapshots'])
    result=dict(schema=1,comparison_kind=report.get('comparison_kind','full/local mesh'),cold_cut_region_applicable=bounds['_has_cut'],complete=False,production_approved=False,source=str(source),cost=report['cost'],keyhole_comparisons=report['keyhole_comparisons'],measurement_quality_gate=report['measurement_quality_gate'],localization={},laser={})
    output=work/'localMeltLocalization.json'
    save(output,result)
    try:
        for label in ('mid','final'):
            print('Localizing existing snapshot:',label,flush=True)
            result['localization'][label]=localize(source/('fullMelt_'+label+'.csv'),source/('localMelt_'+label+'.csv'),bounds)
            save(output,result)
        for variant in ('fullMelt','localMelt'):
            text=(source/variant/'log.vacuumLaserbeamFoam').read_text()
            records=parse_records(text,'LASER_PERF_DIAGNOSTICS');rank_rows=parse_records(text,'LASER_RANK_DIAGNOSTICS')
            perf=report[variant]['performance'];times=[x['time'] for x in report[variant]['diagnostics']]
            records=align_output_times(records,times)
            profile=summarize(records,times,48,optical_calls(report[variant]));validate_rank_rows(rank_rows,records,48)
            totals=[dict(rank=i,trace_s=sum(x['trace_s'] for x in rank_rows if x['rank']==i),advances=sum(x['advances'] for x in rank_rows if x['rank']==i)) for i in range(48)]
            totals.sort(key=lambda x:x['trace_s'],reverse=True)
            profile['rank_totals']=totals
            profile['top_two_trace_fraction']=sum(x['trace_s'] for x in totals[:2])/sum(x['trace_s'] for x in totals)
            profile['interpretation']='Exchange includes waiting for imbalanced tracing; this profile does not isolate network transfer time. Interval maxima across stages must not be added as a critical path.'
            result['laser'][variant]=profile
        result['complete']=True;save(output,result)
    except BaseException as error:
        result['error']=str(error);save(output,result);raise
    print('Existing-result localization complete; no CFD advanced',flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,required=True);p.add_argument('--work',type=Path,required=True)
    a=p.parse_args();collect(a.source,a.work)
