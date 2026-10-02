# 304L / 0.6 Pa overnight moving single-track — 8 um

This is an engineering long-duration integration run, not yet the final experiment-matched production case.

Purpose:
- long-time stability of the frozen Wang evaporation closure at 0.6 Pa;
- deterministic generated powder over a longer track;
- continuous moving-laser ray tracing and multiple reflections;
- time histories for moving-keyhole and energy diagnostics.

Run configuration:
- domain: 800 x 320 x 320 um;
- mesh: 8 um, 100 x 40 x 40 = 160000 cells;
- MPI ranks: 48;
- target time: 300 us;
- write interval: 5 us, binary;
- track: x=-300 to +300 um;
- track length: 600 um;
- engineering scan speed: 2 m/s;
- laser: 260 W, 100 um, Fe fixed-complex-index Fresnel;
- chamber pressure: 0.6 Pa.

Powder configuration:
- seed 304006;
- footprint 760 x 280 um;
- layer limit 60 um;
- uniform engineering diameter support 24-44 um;
- target geometrical solid fraction 0.22;
- expected deterministic particle count: 144.

The powder and scan parameters remain engineering integration inputs and must not be presented as experimental inputs.

Recommended launch sequence:

    ./Allclean
    ./Preflight
    ./Run_background
    ./Status

Resume after interruption:

    ./Resume_background

After completion:

    ./PostprocessTrack

The moving-keyhole extractor follows the laser using a local window:
- trailing distance: 100 um;
- forward distance: 60 um;
- transverse half-width: 75 um;
- reference surface: original substrate y=200 um.

This prevents the deepest point in an old scanned region from being reported as the current moving keyhole.
