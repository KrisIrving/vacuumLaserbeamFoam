"""Pure V2 blockMesh dictionary transform for the 50us local corridor."""
import re

CELLS=1929312


def local_mesh_dictionary(text):
    """Shorten only the x fine corridor; retain V2 outer bounds and patches."""
    text,vertices=re.subn(r'(?m)^\(0\.00168 ', '(0.00030 ', text)
    if vertices!=16:
        raise ValueError(f'Expected 16 V2 x=1680um vertices; found {vertices}')
    counts={0:0,1:0,2:0}
    expected={0:12,1:320,2:12}
    replacement={0:12,1:90,2:72}
    pattern=r'(?m)^(hex \((\d+) [^)]*\) \()(\d+)( \d+ \d+\) simpleGrading \([^)]+\))$'
    def change(match):
        group=int(match.group(2))%4
        if group not in expected or int(match.group(3))!=expected[group]:
            raise ValueError('Unexpected V2 x block subdivision')
        counts[group]+=1
        return match.group(1)+str(replacement[group])+match.group(4)
    text=re.sub(pattern,change,text)
    if counts!={0:9,1:9,2:9}:
        raise ValueError(f'Expected 27 V2 blocks in 3 x slabs; found {counts}')
    blocks=re.findall(r'hex \([^)]+\) \((\d+) (\d+) (\d+)\)',text)
    if sum(int(x)*int(y)*int(z) for x,y,z in blocks)!=CELLS:
        raise ValueError('Local mesh cell count mismatch')
    return text

