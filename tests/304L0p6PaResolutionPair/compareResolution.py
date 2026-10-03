#!/usr/bin/env python3
import argparse
import csv
import math
from pathlib import Path


def read(path):
    with path.open(newline="") as f:
        return {float(r["time_s"]): r for r in csv.DictReader(f)}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--coarse", type=Path, required=True)
    ap.add_argument("--fine", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args=ap.parse_args()

    a=read(args.coarse)
    b=read(args.fine)
    times=sorted(set(a)&set(b))
    if not times:
        raise SystemExit("No common output times")

    rows=[]
    for t in times:
        d8=float(a[t]["keyhole_depth_um"])
        d4=float(b[t]["keyhole_depth_um"])
        dx8=float(a[t]["bottom_dx_from_laser_um"])
        dx4=float(b[t]["bottom_dx_from_laser_um"])
        rows.append((t,d8,d4,d4-d8,dx8,dx4,dx4-dx8))

    with args.output.open("w",newline="") as f:
        w=csv.writer(f)
        w.writerow([
            "time_s","depth_8um_um","depth_4um_um","depth_4minus8_um",
            "dx_8um_um","dx_4um_um","dx_4minus8_um"
        ])
        for r in rows:
            w.writerow([f"{r[0]:.12g}"]+[f"{x:.8g}" for x in r[1:]])

    post=[r for r in rows if r[0] >= 50e-6]
    diffs=[abs(r[3]) for r in post]
    signed=[r[3] for r in post]
    d8=[r[1] for r in post]
    d4=[r[2] for r in post]
    print("RESOLUTION_COMPARISON")
    print(f"common_times={len(rows)}")
    print(f"post50us_mean_depth_8um={sum(d8)/len(d8):.6g} um")
    print(f"post50us_mean_depth_4um={sum(d4)/len(d4):.6g} um")
    print(f"post50us_mean_signed_4minus8={sum(signed)/len(signed):.6g} um")
    print(f"post50us_mean_abs_4minus8={sum(diffs)/len(diffs):.6g} um")
    print(f"post50us_max_abs_4minus8={max(diffs):.6g} um")
    print(f"Wrote {args.output}")


if __name__=="__main__":
    main()
