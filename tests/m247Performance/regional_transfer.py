#!/usr/bin/env python3
"""Reference conservative transfers for axis-aligned regional cell boxes.

This is an offline correctness reference, not a runtime solver or a general
polyhedral overlap algorithm. Inputs are (xmin,ymin,zmin,xmax,ymax,zmax).
"""
import itertools,math
from collections import defaultdict


def volume(box):
    if len(box)!=6 or any(not math.isfinite(x) for x in box) or any(box[d+3]<=box[d] for d in range(3)):
        raise ValueError('Finite positive cell box required')
    return math.prod(box[d+3]-box[d] for d in range(3))


def overlap(a,b):
    return math.prod(max(0,min(a[d+3],b[d+3])-max(a[d],b[d])) for d in range(3))


class Transfer:
    """Source/target cells must each form non-overlapping box partitions.

    Full target coverage is required; source may cover a larger global domain.
    Sparse overlaps are reused for coarse-to-local values and local-to-coarse
    integrated corrections. Supports serial reference data only.
    """
    def __init__(self,source,target):
        self.source=list(source);self.target=list(target)
        if not self.source or not self.target:raise ValueError('Both partitions required')
        self.source_volume=[volume(x) for x in self.source]
        self.target_volume=[volume(x) for x in self.target]
        # Bucket width is largest source edge: no replication on a fine global lattice.
        width=max(b[d+3]-b[d] for b in self.source for d in range(3))
        origin=[min(b[d] for b in self.source) for d in range(3)]
        def buckets(box):
            ranges=[range(math.floor((box[d]-origin[d])/width),math.floor((box[d+3]-origin[d])/width)+1) for d in range(3)]
            return itertools.product(*ranges)
        index=defaultdict(list)
        for i,box in enumerate(self.source):
            seen=set()
            for bucket in buckets(box):
                for other in index[bucket]:
                    if other not in seen and overlap(box,self.source[other])>0:raise ValueError('Overlapping source cells')
                    seen.add(other)
                index[bucket].append(i)
        target_index=defaultdict(list);self.weights=[]
        for box,v in zip(self.target,self.target_volume):
            candidates=set();seen=set()
            for bucket in buckets(box):
                candidates.update(index.get(bucket,()))
                for other in target_index[bucket]:
                    if other not in seen and overlap(box,self.target[other])>0:raise ValueError('Overlapping target cells')
                    seen.add(other)
            row=[(i,overlap(box,self.source[i])) for i in sorted(candidates) if overlap(box,self.source[i])>0]
            if not math.isclose(math.fsum(w for i,w in row),v,rel_tol=1e-10,abs_tol=0):raise ValueError('Target cell not fully covered by source')
            self.weights.append(row)
            j=len(self.weights)-1
            for bucket in buckets(box):target_index[bucket].append(j)

    def gather_density(self,source_density):
        """Piecewise constant source density -> target volume average."""
        self.validate(source_density,len(self.source))
        return [math.fsum(source_density[i]*w for i,w in row)/v for row,v in zip(self.weights,self.target_volume)]

    def scatter_integrated_correction(self,target_correction):
        """Integrated target delta (e.g. joules) -> source density increment.

        Caller supplies the local correction relative to its coarse prediction,
        not the absolute local energy, to avoid double-counting the global heat solve.
        """
        self.validate(target_correction,len(self.target));pieces=[[] for _ in self.source]
        for delta,v,row in zip(target_correction,self.target_volume,self.weights):
            for i,w in row:pieces[i].append(delta*w/v)
        result=[math.fsum(p)/v for p,v in zip(pieces,self.source_volume)]
        before=math.fsum(target_correction);after=math.fsum(x*v for x,v in zip(result,self.source_volume))
        scale=max(math.fsum(abs(x) for x in target_correction),1e-300)
        if abs(after-before)>1e-12*scale:raise ValueError('Integrated correction failed conservation')
        return result

    @staticmethod
    def validate(values,count):
        if len(values)!=count or any(not math.isfinite(x) for x in values):raise ValueError('Finite matching values required')
