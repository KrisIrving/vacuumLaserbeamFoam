#!/usr/bin/env python3
from pathlib import Path
import argparse
import csv
import re
import matplotlib.pyplot as plt

def read_csv(path):
    with Path(path).open(newline="") as f:
        return list(csv.DictReader(f))

def col(rows, name, scale=1.0):
    return [float(r[name])*scale for r in rows]

def save_all(path_no_ext):
    for ext in ("png", "svg"):
        plt.savefig(str(path_no_ext) + "." + ext, dpi=300, bbox_inches="tight")
    plt.close()

def parse_diag(path):
    rows = []
    pattern = re.compile(r"(\\w+)=([+\\-0-9.eE]+)")
    for line in Path(path).read_text(errors="ignore").splitlines():
        if not line.startswith("VACUUM_DIAGNOSTICS "):
            continue
        d = {k: float(v) for k, v in pattern.findall(line)}
        if "time" in d:
            rows.append(d)
    return rows

ap = argparse.ArgumentParser()
ap.add_argument("--baseline-depth", default="tutorials/vacuumLaserbeamFoam/wang2020_304L_nearVacuum/keyholeDepthSurface.csv")
ap.add_argument("--matched-depth", default="tests/run/wang304LMatchedReference/keyholeDepthSurface.csv")
ap.add_argument("--recoil", default="tests/run/wang304LMatchedReference/keyholeRecoilSurface.csv")
ap.add_argument("--log", default="tests/run/wang304LMatchedReference/log.vacuumLaserbeamFoam")
ap.add_argument("--out", default="paper/wang2020_validation/figures/full")
args = ap.parse_args()

out = Path(args.out)
out.mkdir(parents=True, exist_ok=True)

baseline = read_csv(args.baseline_depth)
matched = read_csv(args.matched_depth)
tb = col(baseline, "time_s", 1e6)
db = col(baseline, "keyhole_depth_um")
tm = col(matched, "time_s", 1e6)
dm = col(matched, "keyhole_depth_um")

plt.figure(figsize=(7.0, 4.8))
plt.plot(tb, db, label="Initial Drude-optics baseline")
plt.plot(tm, dm, label="Matched Fe-Fresnel case")
plt.axhline(32, linestyle="--", linewidth=1, label="32 um")
plt.axhline(136, linestyle=":", linewidth=1, label="136 um")
plt.xlabel("Simulation time (us)")
plt.ylabel("Connected-3D keyhole depth (um)")
plt.legend()
plt.tight_layout()
save_all(out / "fig_keyhole_depth_history")

recoil = read_csv(args.recoil)
tr = col(recoil, "time_s", 1e6)
face = col(recoil, "face_p_recoil_max_atm")
p99 = col(recoil, "face_p_recoil_area_p99_atm")

plt.figure(figsize=(7.0, 4.8))
plt.plot(tr, p99, label="Area-weighted p99")
plt.plot(tr, face, label="Single-face maximum")
plt.axhline(5.0, linestyle="--", linewidth=1, label="Wang reported ~5 atm")
plt.xlabel("Simulation time (us)")
plt.ylabel("Keyhole-surface recoil pressure (atm)")
plt.legend()
plt.tight_layout()
save_all(out / "fig_recoil_pressure_history")

scalar = col(recoil, "full_scalar_pressure_load_N", 1e3)
normal_proj = col(recoil, "full_recoil_force_y_abs_sum_N", 1e3)

plt.figure(figsize=(7.0, 4.8))
plt.plot(tr, scalar, label="Full surface integral(p dS)")
plt.plot(tr, normal_proj, label="Full surface integral(p|n_y| dS)")
plt.axhline(4.0, linestyle="--", linewidth=1, label="Wang reported ~4 mN")
plt.xlabel("Simulation time (us)")
plt.ylabel("Recoil load (mN)")
plt.legend()
plt.tight_layout()
save_all(out / "fig_recoil_load_history")

diag = parse_diag(args.log)
td = [r["time"]*1e6 for r in diag]
deposited = [r.get("depositedPower", float("nan")) for r in diag]
evap = [r.get("evaporationPower", float("nan")) for r in diag]
rad = [r.get("radiationPower", float("nan")) for r in diag]

plt.figure(figsize=(7.0, 4.8))
plt.plot(td, deposited, label="Deposited laser power")
plt.plot(td, evap, label="Evaporation heat loss")
plt.plot(td, rad, label="Radiation heat loss")
plt.xlabel("Simulation time (us)")
plt.ylabel("Power (W)")
plt.legend()
plt.tight_layout()
save_all(out / "fig_energy_budget_history")

print(f"Wrote full Wang validation figures to {out}")
