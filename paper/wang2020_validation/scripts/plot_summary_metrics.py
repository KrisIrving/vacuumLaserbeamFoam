#!/usr/bin/env python3
from pathlib import Path
import csv
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
rows = list(csv.DictReader((ROOT/"data"/"summary_metrics.csv").open()))
OUT = ROOT/"figures"
OUT.mkdir(parents=True, exist_ok=True)

def vals(metric):
    r=[x for x in rows if x["metric"]==metric]
    return [x["series"] for x in r], [float(x["value"]) for x in r]

labels, values = vals("keyhole_growth_32_136")
plt.figure(figsize=(7.0,4.6))
bars=plt.bar(labels, values)
plt.ylabel("32-136 um growth interval (us)")
plt.xticks(rotation=18, ha="right")
plt.ylim(0,max(values)*1.18)
for b,v in zip(bars,values):
    plt.text(b.get_x()+b.get_width()/2,v+1.2,f"{v:.2f}",ha="center")
plt.tight_layout()
for ext in ("png","svg"):
    plt.savefig(OUT/f"fig_keyhole_growth_validation.{ext}",dpi=300,bbox_inches="tight")
plt.close()

labels, values = vals("early_deposited_power")
plt.figure(figsize=(6.6,4.5))
bars=plt.bar(labels, values)
plt.ylabel("Deposited laser power (W)")
plt.xticks(rotation=15,ha="right")
plt.ylim(0,max(values)*1.20)
for b,v in zip(bars,values):
    plt.text(b.get_x()+b.get_width()/2,v+2,f"{v:.2f}",ha="center")
plt.tight_layout()
for ext in ("png","svg"):
    plt.savefig(OUT/f"fig_optical_closure_check.{ext}",dpi=300,bbox_inches="tight")
plt.close()

labels, values = vals("recoil_load")
plt.figure(figsize=(6.6,4.5))
bars=plt.bar(labels, values)
plt.ylabel("Surface recoil load (mN)")
plt.xticks(rotation=15,ha="right")
plt.ylim(0,max(values)*1.22)
for b,v in zip(bars,values):
    plt.text(b.get_x()+b.get_width()/2,v+0.08,f"{v:.2f}",ha="center")
plt.tight_layout()
for ext in ("png","svg"):
    plt.savefig(OUT/f"fig_recoil_load_validation.{ext}",dpi=300,bbox_inches="tight")
plt.close()
