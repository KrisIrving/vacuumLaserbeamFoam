# Deterministic powder-bed geometry generator

`generatePowderBed.py` converts a small JSON configuration into:

- an OpenFOAM `setFieldsDict`;
- a particle CSV with exact centres/radii;
- a JSON manifest with seed, PSD statistics, solid fraction and overlap checks.

## Packing algorithm

Particles are inserted sequentially. For every sampled diameter:

1. choose a random x-z location inside the requested footprint;
2. drop the particle vertically;
3. stop at the highest contact with the substrate or an existing sphere;
4. reject the particle if its top exceeds the layer-thickness limit.

The algorithm is deterministic for a fixed Python version, configuration and
seed. The exact generated particle CSV is retained as the authoritative
reproducibility record.

This is a geometrical deposition model, not DEM. It is intended to provide a
transparent and reproducible CFD initial condition. Experimental PSD/packing
inputs should be substituted explicitly when they are available.
