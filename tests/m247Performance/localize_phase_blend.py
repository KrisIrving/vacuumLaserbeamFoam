#!/usr/bin/env python3
"""Locate phase-closure/width differences from saved fields; no CFD."""
import argparse
import csv
import json
from pathlib import Path
from localize_field_differences import localize

PAIRS=(('enthalpyTight','phaseBlendNarrow'),('phaseBlendNarrow','phaseBlendWide'))
NAMES=('phaseBlendLocalization.json','phaseBlendRegions.csv','phaseBlendWorstCells.csv')

def inspect(work):
    work=Path(work)
    output=work/'comparison'
    if any((output/name).exists() for name in NAMES):
        raise ValueError('Phase localization outputs already exist; preserve them')
    results=[]
    for reference,candidate in PAIRS:
        result=localize(work,reference_variant=reference,candidate_variant=candidate)
        result['comparison']=reference+'_vs_'+candidate
        results.append(result)
    result=dict(schema=1,convergence_gate=all(r['convergence_gate'] for r in results),
                production_approved=False,comparisons=results,
                note='Offline region/worst-cell localization; pressure differences are raw p_rgh, not gauge-aligned. No energy validation or new CFD.')
    output.mkdir(exist_ok=True)
    with (output/NAMES[0]).open('x') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    for name,key in ((NAMES[1],'regions'),(NAMES[2],'worst_cells')):
        rows=[dict(comparison=r['comparison'],**row) for r in results for row in r[key]]
        with (output/name).open('x',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader();writer.writerows(rows)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--work',type=Path,required=True)
    args=parser.parse_args()
    try:
        result=inspect(args.work)
    except (OSError,ValueError,KeyError) as error:
        parser.exit(1,f'Phase localization failed: {error}\n')
    for comparison in result['comparisons']:
        print(comparison['comparison'])
        for row in comparison['regions']:
            print(f"  {row['region']} {row['field']}: max={row['max_abs_difference']}, RMS={row['cell_unweighted_rms_difference']}")
    print('Saved localization reports. No CFD or rebuild was performed.')

if __name__=='__main__': main()
