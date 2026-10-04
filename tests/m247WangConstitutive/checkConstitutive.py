#!/usr/bin/env python3
from __future__ import annotations
import argparse
import csv
import math
import re
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--csv", type=Path, required=True)
ap.add_argument("--thresholds", type=Path, required=True)
args=ap.parse_args()

rows=list(csv.DictReader(args.csv.open()))
by={(r["label"], float(r["temperature_K"])): r for r in rows}

expected={
    ("298K",1631.0):(1.267639680774108,0.000260195478385511,0.4110059392710327,1688.741125992766),
    ("298K",1800.0):(11.59186719060241,0.005276120144637797,5.971343147049936,34243.48927665647),
    ("298K",2000.0):(102.4081777317015,0.04675241725703203,55.70669905074164,303436.2097735836),
    ("hotGas",1631.0):(1.267639680774108,0.0003571667976840522,0.3211992665314272,2318.111997298196),
    ("hotGas",1800.0):(11.59186719060241,0.005388867926701672,5.773512270156979,34975.25378546792),
    ("hotGas",2000.0):(102.4081777317015,0.04675241725703203,55.70669905074164,303436.2097735836),
}

def close(actual, target, rtol=2e-7, atol=1e-11):
    return abs(actual-target) <= atol + rtol*max(abs(target),1.0)

for key, ref in expected.items():
    row=by[key]
    actual=tuple(float(row[name]) for name in (
        "pSat_Pa","massFlux_kg_m2_s","recoil_Pa","qEvap_W_m2"
    ))
    for name,a,e in zip(("pSat","mDot","recoil","qEvap"),actual,ref):
        if not close(a,e):
            raise SystemExit(f"{key} {name}: got {a}, expected {e}")

# Below liquidus the evaporation/recoil coupling must remain inactive.
for label in ("298K","hotGas"):
    for T in (1343.15,1537.0):
        row=by[(label,T)]
        if any(float(row[k]) != 0.0 for k in (
            "massFlux_kg_m2_s","recoil_Pa","qEvap_W_m2"
        )):
            raise SystemExit(f"{label} T={T}: expected inactive below liquidus")

text=args.thresholds.read_text()
expected_thresholds={
    "298K":(1580.3106780,1599.177413,1893.154185),
    "hotGas":(1580.3106780,1592.575405,1797.364470),
}
for label,(tb,tk0,tk1) in expected_thresholds.items():
    m=re.search(rf"===== {label} .*?=====\n(.*?)(?=====|\Z)",text,re.S)
    if not m:
        raise SystemExit(f"Missing threshold block {label}")
    block=m.group(1)
    vals=[]
    for pat in (
        r"boilingTemperature\s*=\s*([0-9.eE+\-]+)",
        r"Tk0 \(Ma=0\.05\)\s*=\s*([0-9.eE+\-]+)",
        r"Tk1 \(Ma=1\)\s*=\s*([0-9.eE+\-]+)",
    ):
        mm=re.search(pat,block)
        if not mm:
            raise SystemExit(f"Missing threshold in {label}")
        vals.append(float(mm.group(1)))
    for name,a,e in zip(("boiling","Tk0","Tk1"),vals,(tb,tk0,tk1)):
        if abs(a-e) > 0.05:
            raise SystemExit(f"{label} {name}: got {a}, expected about {e}")

# pSat depends only on T/composition; chamber gas temperature changes only
# the common-atmosphere transition state.
for T in (1631.0,1800.0,2000.0):
    a=float(by[("298K",T)]["pSat_Pa"])
    b=float(by[("hotGas",T)]["pSat_Pa"])
    if abs(a-b) > 1e-10*max(a,b,1.0):
        raise SystemExit(f"pSat changed with chamberTemperature at {T} K")

print("M247_WANG_CONSTITUTIVE")
print("298 K gas: Tb~1580.31 K, Tk0~1599.18 K, Tk1~1893.15 K")
print("1343.15 K gas: Tb~1580.31 K, Tk0~1592.58 K, Tk1~1797.36 K")
print("activationTemperature=1631 K in both cases because liquidus > Tb")
print("PASS: M247 Mondal-2023/Wang constitutive parity and chamber-temperature sensitivity")
