#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, re
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--csv", type=Path, required=True)
ap.add_argument("--thresholds", type=Path, required=True)
args=ap.parse_args()

rows=list(csv.DictReader(args.csv.open()))
by={}
for r in rows:
    by[(r["label"], float(r["temperature_K"]))]=r

text=args.thresholds.read_text()
blocks={}
for label in ("0p6Pa","20p265Pa","1atm"):
    m=re.search(
        rf"===== {label} .*?=====\n(.*?)(?=====|\Z)",
        text, re.S
    )
    if not m:
        raise SystemExit(f"Missing threshold block for {label}")
    block=m.group(1)
    vals={}
    for key,pat in {
        "boiling":r"boilingTemperature\s*=\s*([0-9.eE+\-]+)",
        "activation":r"activationTemperature=\s*([0-9.eE+\-]+)",
        "Tk0":r"Tk0 \(Ma=0\.05\)\s*=\s*([0-9.eE+\-]+)",
        "Tk1":r"Tk1 \(Ma=1\)\s*=\s*([0-9.eE+\-]+)",
    }.items():
        mm=re.search(pat,block)
        if not mm:
            raise SystemExit(f"Missing {key} for {label}")
        vals[key]=float(mm.group(1))
    blocks[label]=vals

for key in ("boiling","activation","Tk0","Tk1"):
    a=blocks["0p6Pa"][key]
    b=blocks["20p265Pa"][key]
    c=blocks["1atm"][key]
    if not (a <= b <= c):
        raise SystemExit(f"Non-monotonic pressure trend for {key}: {a}, {b}, {c}")

for T in (3000.0,4000.0,5000.0):
    ps=[float(by[(lab,T)]["pSat_Pa"]) for lab in ("0p6Pa","20p265Pa","1atm")]
    span=max(ps)-min(ps)
    if span > 1e-8*max(ps):
        raise SystemExit(f"pSat must be chamber-pressure independent at {T} K: {ps}")

print("WANG_PRESSURE_TREND")
for lab in ("0p6Pa","20p265Pa","1atm"):
    v=blocks[lab]
    print(
        f"{lab}: boiling={v['boiling']:.6g} K "
        f"activation={v['activation']:.6g} K "
        f"Tk0={v['Tk0']:.6g} K Tk1={v['Tk1']:.6g} K"
    )

for T in (2200.0,3000.0,4000.0,5000.0):
    print(f"T={T:.0f} K")
    for lab in ("0p6Pa","20p265Pa","1atm"):
        r=by[(lab,T)]
        print(
            f"  {lab}: mDot={float(r['massFlux_kg_m2_s']):.6g} "
            f"recoil={float(r['recoil_Pa']):.6g} Pa "
            f"qEvap={float(r['qEvap_W_m2']):.6g} W/m2"
        )

print("PASS: Wang 304L pressure-trend constitutive sweep")
