# 304L / 0.6 Pa / 8 um moving-powder resolution companion

This case is a numerical-resolution probe, not a new physical calibration.

Configuration:
- domain 320 x 320 x 320 um;
- mesh 8 um, 40^3 = 64,000 cells;
- 48 MPI ranks;
- 0.6 Pa;
- frozen Wang evaporation closure;
- 260 W / 100 um Fe-Fresnel laser;
- engineering scan speed 2 m/s;
- x=-100 to +100 um over 100 us;
- deterministic 56-particle powder bed with seed 304006;
- 5 us binary writes.

Recommended sequence:

    ./Allclean
    ./Preflight
    ./Run_background
    ./Status

After completion:

    ./PostprocessTrack

The moving-depth post-process uses a 160 um trailing window to avoid the clipping observed in the first 8 um long-track metric.

The purpose is to determine whether the approximately 40-50 um moving-keyhole depth observed at 8 um changes materially for a strict companion comparison against the 4 um case.
