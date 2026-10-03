# M247 material-port and 2 mm track plan

## Goal

Port the validated near-vacuum/powder/moving-laser framework from 304L to the
actual M247 powder used in the experiment, then simulate a single melt track of
approximately 2 mm length.

This is a **material port**, not a new evaporation-model derivation.

The Wang evaporation equations remain frozen. What changes are the
material-specific thermodynamic, optical and transport inputs.

---

## 1. Exact alloy identity must be frozen first

"M247" is not sufficiently specific for a publication-grade input deck.

The authoritative source should be, in order of preference:
1. powder supplier certificate / actual heat chemistry;
2. experimental characterization of the powder;
3. nominal specification of the exact alloy variant;
4. literature nominal MAR-M247 only as a documented fallback.

MAR-M247 literature commonly contains major additions of Cr, Co, W, Al, Ta,
Ti, Mo and Hf with Ni balance. CM247LC and individual heats are not assumed to
be identical.

Create a versioned composition table in wt.% before any final M247 simulation.

---

## 2. Evaporation-model port

The current nearVacuumWang implementation already supports an arbitrary list
of alloy components through:
- mass fraction;
- molar mass;
- pure-component reference pressure;
- reference temperature;
- latent heat of vaporization.

Therefore **no new evaporation-model API is required to represent M247**.

Required M247 work:
1. collect pure-component vapor-pressure references for relevant volatile
   species;
2. convert nominal/actual wt.% to the model's molar-fraction mixture treatment;
3. determine whether an alloy-level vapor-pressure anchor is available or
   defensible;
4. compute the predicted vapor composition versus temperature;
5. identify which components actually dominate vapor pressure in the
   0.6-Pa/LPBF temperature range;
6. run constitutive pressure/temperature regressions before CFD.

Likely first active set should be selected from:
- Ni;
- Al;
- Cr;
- Co;
- Ti;
with W, Ta, Mo, Hf evaluated quantitatively before deciding whether their
vapor-pressure contribution is negligible.

Do not blindly include or exclude a species based only on its bulk wt.%.

### Preferential depletion limitation

The current alloy model evaluates vapor composition from a fixed bulk
composition. It does **not** transport composition or deplete volatile species
locally.

For a first geometry/melt-track study this may be acceptable if the target
observable is melt-pool/keyhole/track morphology.

If Al loss, chemistry change, mass loss or property evolution is a target
observable, preferential evaporation/composition transport becomes a separate
required physics extension.

---

## 3. M247 thermophysical property set

Required, preferably temperature dependent:
- density;
- solidus;
- liquidus;
- heat capacity;
- thermal conductivity;
- dynamic viscosity;
- latent heat of fusion;
- latent heat of evaporation;
- surface tension;
- d(sigma)/dT;
- emissivity.

Each property must have:
- value/function;
- units;
- temperature range;
- source;
- uncertainty/range if known;
- exact OpenFOAM configuration location.

Do not silently reuse 304L properties.

---

## 4. M247 optical closure

The Fe fixed-complex-index data used for the Wang 304L benchmark must **not**
be reused as an M247 material constant.

Required priority:
1. measured M247 reflectivity/complex index at the experimental wavelength;
2. literature M247/Ni-superalloy optical data;
3. defensible Ni-based surrogate with sensitivity bounds;
4. calibrated absorptivity only if independently supported by experiment.

The ray-tracing/multiple-reflection algorithm is reusable unchanged.

The material Fresnel constants are material-specific inputs.

---

## 5. Powder-bed inputs

Required from the actual experiment:
- PSD, preferably D10/D50/D90 plus full distribution if available;
- nominal layer thickness;
- particle morphology/sphericity;
- powder apparent/tap/bed density if available;
- packing/solid-fraction target;
- substrate condition;
- preheat temperature;
- powder chemistry certificate.

The existing deterministic sphere generator is suitable as the first
reproducible powder-bed representation.

A final publication study should use multiple fixed seeds to quantify geometric
stochasticity.

---

## 6. 2 mm track computational strategy

A 2-mm moving track is substantially longer than the current 600-um engineering
track.

The production strategy depends on the running 8-um/4-um resolution pair.

### If 8 um is acceptable for screening/full-track geometry

Recommended:
- full approximately 2 mm track at 8 um;
- 4 um short-track/key-region verification;
- 4 um selected publication cases if practical.

A domain of roughly 2.3-2.5 mm in scan direction with approximately
0.32-0.48 mm transverse/vertical extent is computationally plausible at 8 um.

### If 4 um is required globally

A full 2-mm global 4-um domain will be expensive.

Then evaluate:
- a shorter 4-um validation segment plus 8-um full track;
- local/static refinement around the track;
- a moving computational/refinement window;
- segmented restart strategy only if it preserves thermal/history fields.

Do not choose the final production strategy before T13b completes.

---

## 7. Validation sequence for M247

M247 should not jump directly to the 2-mm powder run.

Recommended gates:

### M1 — material dictionary audit
All M247 inputs and references recorded.

### M2 — constitutive evaporation curves
At 0.6 Pa and 1 atm:
- pSat(T);
- vapor composition;
- mDot(T);
- recoil(T);
- qEvap(T);
- boiling/activation/Tk0/Tk1.

### M3 — flat/bare-plate optical and thermal smoke
Check deposited power and stable activation.

### M4 — short powder moving-track smoke
Use actual M247 PSD/layer/laser inputs.

### M5 — short-track 8/4 um comparison
Confirm the mesh policy transfers from 304L to M247.

### M6 — full 2-mm track
Run the experiment-matched case.

### M7 — seed/sensitivity set
At least a small deterministic powder ensemble for publication-quality
uncertainty.

---

## 8. Current readiness statement

The **solver architecture is ready for an M247 powder bed**.

The **M247 material model is not yet ready**, because material-specific
evaporation, optics and thermophysical inputs have not yet been frozen and
validated.

This distinction should be maintained in code documentation and in any paper.
