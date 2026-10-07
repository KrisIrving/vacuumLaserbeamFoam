#!/usr/bin/env python3
"""Report closure response and width sensitivity, never production approval."""
import argparse
import csv
import json
from pathlib import Path
from collect_probe import read_probe, compare, parse_records
from collect_thermal_validation import residual_gate, field_differences

WIDTHS = {'enthalpyTight':0.0,'phaseBlendNarrow':0.005,'phaseBlendWide':0.01}

def collect(work):
    probes={}
    provenance=[]
    converged=True
    for variant,width in WIDTHS.items():
        case=work/variant
        probe=read_probe(case)
        meta,summary,_=probe
        if meta['variant']!=variant or meta.get('phase_temperature_blend_half_width')!=width:
            raise ValueError('Probe variant/width mismatch')
        if meta.get('epsilon_tolerance')!=1e-5 or meta.get('phase_temperature_tolerance_K')!=0.001:
            raise ValueError('Phase probe requires matched tight thermal tolerances')
        if (case/'constant/dynamicMeshDict').exists():
            raise ValueError('Only fixed M247 mesh supported')
        for rank in range(meta['ranks']):
            for folder in (case/f'processor{rank}').iterdir():
                if (folder/'polyMesh').is_dir():
                    try: time=float(folder.name)
                    except ValueError: continue
                    if time>meta['start_s']+1e-12: raise ValueError('Mesh changed in phase probe')
        run=json.loads((case/'run.json').read_text())
        if not run.get('solver_sha256'): raise ValueError('Missing binary provenance')
        provenance.append((run['solver_sha256'],run.get('laser_library_sha256')))
        records=parse_records((case/'log.vacuumLaserbeamFoam').read_text(),'THERMAL_RESIDUAL_DIAGNOSTICS')
        if any('phaseBlendHalfWidth' not in r or abs(r['phaseBlendHalfWidth']-width)>1e-12
               or 'phaseOverrideWeight' not in r or not 0<=r['phaseOverrideWeight']<=1 for r in records):
            raise ValueError('Rebuild required: missing/mismatched phase-blend diagnostics')
        converged = residual_gate(case,meta,summary['steps']) and summary['thermal_limit_hits']==0 and converged
        probes[variant]=probe
    if len(set(provenance))!=1: raise ValueError('Solver/library provenance mismatch')
    comparisons=[];field_rows=[];diagnostic_rows=[]
    for reference,candidate in (('enthalpyTight','phaseBlendNarrow'),('phaseBlendNarrow','phaseBlendWide')):
        summary,rows=compare(probes[reference],probes[candidate])
        label=reference+'_vs_'+candidate
        fields=field_differences(work/reference,work/candidate,probes[reference][0]['ranks'],probes[reference][0]['end_s'])
        comparisons.append(dict(name=label,diagnostic_summary=summary,fields=fields))
        field_rows.extend(dict(comparison=label,**r) for r in fields)
        for row in rows:
            row['relative_difference']=row['absolute_difference']/abs(row['reference']) if row['reference'] else None
            diagnostic_rows.append(dict(comparison=label,**row))
    result=dict(schema=1,convergence_gate=converged,production_approved=False,
        variants={v:p[1] for v,p in probes.items()},comparisons=comparisons,
        note='Modified interface closure and restart response, then transition-width sensitivity. Strict diagnostic equality is descriptive, not a physical acceptance gate. Internal cells only; RMS not volume weighted. Restart fields are retained, so transient enthalpy adjustment is expected and must be reviewed. No energy-conservation or long-track approval is implied.')
    output=work/'comparison'
    if output.exists(): raise ValueError('Comparison directory already exists')
    output.mkdir()
    (output/'phaseBlendReview.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,rows in (('phaseBlendFields.csv',field_rows),('phaseBlendDiagnostics.csv',diagnostic_rows)):
        with (output/name).open('w',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    try: result=collect(args.work)
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,f'Phase probe collection failed: {error}\n')
    print(f"All thermal convergence gates: {result['convergence_gate']}")
    for name,row in result['variants'].items():
        print(f"{name}: wall={row['job_wall_s']:.2f} s; correctors/step={row['thermal_correctors_per_step']:.2f}; cap hits={row['thermal_limit_hits']}")
    print('Closure-response and width-sensitivity summaries saved; production approval remains pending.')
    if not result['convergence_gate']: parser.exit(2,'Thermal convergence failed.\n')

if __name__=='__main__': main()
