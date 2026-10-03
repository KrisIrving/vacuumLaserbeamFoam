# Publication figure style — Acta-like materials-science format

## Intent

All new manuscript figures should use a restrained, print-oriented style
consistent with high-level materials-science journals such as Acta Materialia.

This is an internal house style, not a claim that Acta Materialia mandates a
specific color palette.

## Figure sizes

Design at final print size:
- single column: 90 mm;
- 1.5 column: 140 mm;
- double column: 190 mm.

Use vector output for graphs whenever possible:
- PDF;
- SVG for editing/archive;
- EPS if required at submission.

For raster/field images:
- halftone/color: >=300 dpi;
- mixed line + raster: >=500 dpi;
- pure line art if rasterized: >=1000 dpi.

## Typography

Preferred:
- Arial / Helvetica;
- normal final-size text approximately 7-8 pt;
- panel labels approximately 8-9 pt bold.

Rules:
- no oversized figure titles inside plots;
- captions belong in the manuscript;
- axis labels use concise variable + units;
- use true Greek/math symbols where possible;
- keep terminology identical to the manuscript.

## Axes

- white background;
- no decorative grid by default;
- thin black/graphite axes;
- inward ticks;
- minor ticks where useful;
- top/right ticks may be retained for technical plots;
- scientific notation formatted consistently;
- avoid excessive decimal places.

Typical final-width line weight:
- axes: 0.6-0.8 pt;
- data lines: 1.0-1.3 pt;
- secondary/reference lines: 0.7-1.0 pt.

## Palette

Primary muted materials-science palette:

- graphite: #303030
- navy:     #1F4E79
- brick:    #B55243
- teal:     #3F7F6F
- ochre:    #C7952D
- purple:   #6B5B95
- gray:     #7A7A7A

Usage:
- use black/graphite for experimental/reference data when appropriate;
- use navy as the default simulation series;
- use brick for a second physically important comparison;
- use teal/ochre/purple only when additional series are necessary;
- avoid rainbow palettes for line plots;
- avoid saturated red/green pairs as the only differentiator;
- combine color with line style/marker for grayscale robustness.

For scalar contour fields:
- sequential positive field: cividis/viridis;
- temperature/intensity when visual emphasis is desired: inferno/magma;
- signed deviations: a balanced diverging map centered at zero;
- never use jet/rainbow.

## Markers and line styles

- use markers only when they encode discrete samples;
- avoid a marker at every dense time-history point;
- marker size approximately 3-4.5 pt at final size;
- open markers are preferred when lines overlap;
- reference/experimental: black symbols;
- simulation: colored line;
- alternate models: dashed/dash-dot, not only different colors.

## Multi-panel figures

Panel labels:
- (a), (b), (c), ...;
- upper-left;
- aligned across panels;
- consistent size/offset.

Share axes where possible.
Avoid repeating legends in every panel.

## Legends

- frameless;
- short labels;
- place in unused white space;
- avoid covering data;
- for many related panels, consider one shared legend.

## Error/uncertainty display

Prefer:
- error bars for sparse points;
- transparent confidence/sensitivity bands for dense curves;
- avoid opaque shaded regions that obscure neighboring curves.

## 3-D / VOF interface images

- use identical camera, crop and scale across comparison panels;
- include a scale bar;
- use the same scalar range across directly compared fields;
- annotate laser direction and scan direction;
- avoid perspective distortion when quantitative geometry is being compared;
- record the ParaView state or scripted rendering settings.

## Output rule

Every final figure must have:
- vector version when applicable;
- high-resolution preview;
- source data path;
- plotting script;
- git commit;
- caption draft;
- final width designation: 90 / 140 / 190 mm.

## Current figure policy

The earlier large colored summary bar charts are development figures only and
are not the target manuscript style.

For the Wang validation, prefer:
- compact line/marker comparison;
- direct numerical annotation only where necessary;
- experimental/reference data in black/gray;
- matched solver in navy;
- initial/baseline model in muted brick;
- no decorative color blocks.

For the 0.6-Pa moving-powder study, use the same palette and typography so the
entire paper reads as one figure system.
