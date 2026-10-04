#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def load_data(path: Path):
    data = json.loads(path.read_text())
    total_w = sum(float(v["massFraction"]) for v in data["components"].values())
    if abs(total_w - 1.0) > 1.0e-10:
        raise SystemExit(f"Mass fractions must sum to 1; got {total_w:.12g}")
    return data


def mole_fractions(components):
    amounts = {
        name: float(c["massFraction"]) / float(c["molarMass_kg_mol"])
        for name, c in components.items()
    }
    total = sum(amounts.values())
    return {name: value / total for name, value in amounts.items()}


def pure_psat(component, temperature, pref, gas_constant):
    M = float(component["molarMass_kg_mol"])
    Tref = float(component["referenceTemperature_K"])
    Lv = float(component["latentHeatVap_J_kg"])
    return pref * math.exp(
        Lv * M / gas_constant * (1.0 / Tref - 1.0 / temperature)
    )


def mixture_state(data, x, temperature):
    pref = float(data["referencePressure_Pa"])
    gas_constant = float(data["gasConstant_J_mol_K"])
    components = data["components"]
    partial = {
        name: x[name] * pure_psat(c, temperature, pref, gas_constant)
        for name, c in components.items()
    }
    total = sum(partial.values())
    fractions = {name: value / total for name, value in partial.items()}
    vapor_molar_mass = sum(
        float(components[name]["molarMass_kg_mol"]) * partial[name]
        for name in components
    ) / total
    return total, vapor_molar_mass, partial, fractions


def boiling_temperature(data, x):
    target = float(data["chamberPressure_Pa"])
    lo, hi = 500.0, 7000.0

    def residual(T):
        return math.log(mixture_state(data, x, T)[0] / target)

    flo = residual(lo)
    if flo * residual(hi) > 0:
        raise RuntimeError("Could not bracket the mixture boiling temperature")

    for _ in range(250):
        mid = 0.5 * (lo + hi)
        fm = residual(mid)
        if abs(fm) < 1.0e-12 or hi - lo < 1.0e-9:
            return mid
        if flo * fm <= 0:
            hi = mid
        else:
            lo = mid
            flo = fm
    return 0.5 * (lo + hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).with_name("m247ProvisionalComposition.json"),
    )
    ap.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("m247VaporScreen.csv"),
    )
    args = ap.parse_args()

    data = load_data(args.data)
    components = data["components"]
    names = list(components)
    x = mole_fractions(components)

    rows = []
    for T in [float(v) for v in data["temperatures_K"]]:
        rows.append((T, *mixture_state(data, x, T)))

    for a, b in zip(rows[:-1], rows[1:]):
        if not b[1] > a[1]:
            raise SystemExit(f"Non-monotonic mixture pSat: {a[0]} -> {b[0]} K")

    Tb = boiling_temperature(data, x)
    Tliq = float(data["liquidusTemperature_K"])
    Tpre = float(data["initialMetalTemperature_K"])
    activation = max(Tb, Tliq)
    p_pre = mixture_state(data, x, Tpre)[0]
    p_liq = mixture_state(data, x, Tliq)[0]

    with args.output.open("w", newline="") as f:
        writer = csv.writer(f)
        header = ["temperature_K", "total_pSat_Pa", "vapor_molar_mass_kg_mol"]
        for name in names:
            header += [f"{name}_partial_Pa", f"{name}_vapor_fraction"]
        writer.writerow(header)
        for T, total, Mvap, partial, fractions in rows:
            line = [f"{T:.12g}", f"{total:.12g}", f"{Mvap:.12g}"]
            for name in names:
                line += [f"{partial[name]:.12g}", f"{fractions[name]:.12g}"]
            writer.writerow(line)

    print("M247_VAPOR_SCREEN")
    print(f"chamberPressure={float(data['chamberPressure_Pa']):.12g} Pa")
    print(f"initialMetalTemperature={Tpre:.6g} K")
    print(f"mixtureBoilingTemperature={Tb:.6g} K")
    print(f"liquidusTemperature={Tliq:.6g} K")
    print(f"activationTemperature={activation:.6g} K")
    print(f"pSat_at_preheat={p_pre:.6g} Pa")
    print(f"pSat_at_liquidus={p_liq:.6g} Pa")
    print("temperature_contributions:")
    for T, total, Mvap, partial, fractions in rows:
        ranked = sorted(fractions.items(), key=lambda item: item[1], reverse=True)
        top = ", ".join(
            f"{name}={100.0*fraction:.2f}%"
            for name, fraction in ranked[:4]
        )
        print(
            f"  T={T:.6g} K pSat={total:.6g} Pa "
            f"Mvap={Mvap:.6g} kg/mol top=[{top}]"
        )

    chamber = float(data["chamberPressure_Pa"])
    if not p_pre < chamber:
        raise SystemExit("Expected pSat(preheat) < chamberPressure")
    if not p_liq > chamber:
        raise SystemExit("Expected pSat(liquidus) > chamberPressure")

    print(f"Wrote {args.output}")
    print(
        "PASS: provisional M247 ideal-mixture vapor screen; "
        "not an activity/depletion validation"
    )


if __name__ == "__main__":
    main()
