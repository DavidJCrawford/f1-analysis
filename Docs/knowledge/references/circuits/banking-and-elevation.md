---
type: Reference
title: Banking and Elevation
description: What the telemetry Z channel actually measures, why banking cannot be derived from any open dataset and must be authored, and the frame the track ribbon is built on.
resource: https://github.com/theOehrly/Fast-F1/discussions/593
tags:
  - elevation
  - banking
  - camber
  - dem
  - lidar
  - threejs
  - frames
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_disc_593
    resource: https://github.com/theOehrly/Fast-F1/discussions/593
    title: Fast-F1 Discussion #593 — Track Elevation Data
  - id: fastf1_disc_116
    resource: https://github.com/theOehrly/Fast-F1/discussions/116
    title: Fast-F1 Discussion #116 — normalized track position
  - id: openf1_location
    resource: https://api.openf1.org/v1/location?session_key=9574&driver_number=1
    title: OpenF1 /v1/location — Spa 2024 position samples
  - id: copernicus_glo30
    resource: https://registry.opendata.aws/copernicus-dem/
    title: Copernicus DEM on the AWS Registry of Open Data
  - id: copernicus_handbook
    resource: https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf
    title: Copernicus DEM Product Handbook i5.0
  - id: joerd_formats
    resource: https://github.com/tilezen/joerd/blob/master/docs/formats.md
    title: Tilezen joerd — terrain tile formats
  - id: usgs_3dep
    resource: https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer
    title: USGS 3DEP Elevation ImageServer
  - id: threejs_curve
    resource: https://raw.githubusercontent.com/mrdoob/three.js/dev/src/extras/core/Curve.js
    title: three.js src/extras/core/Curve.js — computeFrenetFrames
  - id: f1_zandvoort_guide
    resource: https://www.formula1.com/en/latest/article/circuit-guide-everything-you-need-to-know-about-circuit-zandvoort.3yxmn4LiWkbNTKpad7IRSo
    title: Formula1.com circuit guide — Zandvoort
status: stable
---

# Banking and Elevation

Elevation and banking look like the same problem and are not. **Elevation is
measured and excellent. Banking is unmeasurable from any open source and must
be authored by hand.** Everything below follows from that split.

## 1. The Z channel is real elevation

Position data carries `Z` in the same 1/10 m unit as `X` and `Y`. The FastF1
maintainer confirms in
[Discussion #593](https://github.com/theOehrly/Fast-F1/discussions/593) that
"Z represents the elevation", and notes the usual failure mode is plotting it
into a 2D top-down chart.

Measured at Spa 2024 (`session_key=9574`, `driver_number=1`, a two-minute
window, 465 samples):

| Quantity | Value |
| --- | --- |
| Z minimum | 3655 raw → **365.5 m** |
| Z maximum | 4678 raw → **467.8 m** |
| Span | **102.3 m** |
| Distinct Z values | 358 of 465 samples |
| X span | 1265.0 m |
| Y span | 2031.1 m |

Spa's published elevation change is about 100 m, so the span alone is
corroborating. The stronger test is absolute agreement: sampling EU-DEM 25 m at
all 153 vertices of the Spa centreline gives min 364.7 m, max 471.9 m, range
107.1 m. **The floor agrees to 0.8 m and the ceiling to 4.1 m.** Z is genuine
orthometric elevation with essentially no offset, not merely a correctly scaled
relative profile — and the DEM's higher ceiling is what a surface model does
over the tree line at Blanchimont.

358 distinct values in 465 samples also rules out quantisation to a plane: this
is a real, resolved profile, not a synthetic one.

**Unverified:** the exact vertical datum of the F1 feed. Nothing documents it.
The evidence above bounds any systematic offset to a few metres at one circuit,
which is enough for a scene and not enough for a cross-source join. Resolving it
properly means least-squares fitting telemetry Z against 1 m LiDAR at
Silverstone or Zandvoort, where both datasets are precise.

### The datum zoo

Any elevation number joined from another source arrives on a different vertical
datum, and nothing warns you:

| Source | Vertical datum |
| --- | --- |
| F1 telemetry `Z` | **undocumented** |
| Copernicus GLO-30 | EGM2008 orthometric (EPSG:3855) — *documentation only, see §3* |
| USGS 3DEP | NAVD 88 |
| UK Environment Agency LiDAR | Ordnance Datum Newlyn, via OSTN'15 |
| AHN4 (Netherlands) | NAP |

These differ by metres. **Never mix elevation sources in one surface.** The
site's rule: the track ribbon takes Z from telemetry alone; distant terrain
takes Z from one DEM alone; the two are joined by fitting a single constant
offset per circuit so the terrain meets the track at the start/finish line, and
that offset is recorded in the registry.

## 2. The Z-noise problem

Z is accurate in aggregate and noisy per sample. Three causes, all of which
must be handled before the profile reaches a mesh:

1. **Quantisation.** 1/10 m is the unit, so a flat straight reads as a 0.1 m
   staircase. Rendered on a ribbon with a specular material, that staircase is
   visible as banding.
2. **Irregular sampling.** The interval measured median 240 ms, mean 258 ms,
   min 20 ms, max 500 ms. A 500 ms gap at 300 km/h is 42 m of unsampled track —
   straight-line interpolation across it flattens a crest.
3. **One line, not a surface.** The feed is a normalised track position: "All
   coordinates show the same line" ([Discussion #116](https://github.com/theOehrly/Fast-F1/discussions/116)).
   Averaging drivers reduces sampling noise, not line bias.

Treatment, applied in this order:

```
per-lap: filter Source == "pos", drop Status == "OffTrack", add_relative_distance()
resample every lap onto M common stations in s  (M = ceil(length_m / 2))
Z[station] = median over laps            # rejects dropouts without a threshold
Z = gaussian_filter1d(Z, sigma=3, mode="wrap")   # wrap the start/finish seam
```

Acceptance check: the gradient `dZ/ds` must stay within ±0.20 (20%). Eau Rouge
is about 17%, which is the steepest thing on the calendar; anything above 20% is
an artefact, not a hill.

## 3. DEMs cannot see the track

A 30 m DEM cell is wider than a 11–18 m F1 circuit. Cross-slope at that scale
is pure noise. This is the whole reason banking is unrecoverable, and it is
worth stating in units: to measure a 2° camber across a 14 m track you need to
resolve a 0.49 m height difference between the two edges. GLO-30 gives you one
cell containing both edges, a grandstand and a tree.

### Copernicus GLO-30 — for distant terrain only

```
https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{NS}{lat:02d}_00_{EW}{lon:03d}_00_DEM/Copernicus_DSM_COG_10_{NS}{lat:02d}_00_{EW}{lon:03d}_00_DEM.tif
```

The lat/lon in the name is the **south-west corner** of a 1°×1° tile, so
Silverstone at 52.07 N, 1.01 W is `N52` / `W002`, not `W001`. HEAD returns 200
with `Accept-Ranges: bytes`, so it is a COG and the window can be range-fetched.
Per-tile AUXFILES: EDM, FLM, HEM, WBM, ACM.kml. No key, no requester-pays.

Three caveats that a naive pipeline will hit:

- **The path is deterministic in form but not in availability.** The AWS
  Registry entry states that "a small subset of tiles covering specific
  countries are not yet released to the public." Of ten F1 venues tested,
  Silverstone, Spa, Monaco, Bahrain, Monza, Yas Marina, Interlagos, Jeddah and
  Losail return 200 — **Baku (`N40_E049`) returns HTTP 404.** Handle the 404 and
  fall back; do not assume computed means fetchable.
- **The COG carries no vertical CRS.** Range-fetching the first 200 KB of the
  Silverstone tile shows the only CRS string in the GeoTIFF header is `WGS 84`.
  EGM2008 / EPSG:3855 is an out-of-band fact from the product spec; GDAL and
  rasterio will report a 2D CRS and will not warn that the heights are geoid
  rather than ellipsoidal.
- **It is a surface model**, as the filename says (`Copernicus_DSM_`), with
  absolute vertical accuracy **< 4 m LE90**. Buildings, grandstands and trees
  are baked into the "terrain". Source is TanDEM-X, acquired 2011–2015, so any
  venue rebuilt since is wrong.

Attribution, required verbatim:

> © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided
> under COPERNICUS by the European Union and ESA; all rights reserved

### Tilezen terrarium tiles — for a browser terrain mesh

```
https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png
elevation_m = (red * 256 + green + blue / 256) - 32768
```

Verified 200 at z12–z15 and **404 at z16** — z15 is the ceiling. Sizes at
Silverstone: z12 100 797 B, z13 85 084 B, z14 54 689 B, z15 27 310 B. Decoding
`terrarium/15/16291/10812.png` with the formula above yields 155.19 m at
Silverstone, which is correct.

Do not confuse it with Mapbox Terrain-RGB v1, which uses a different formula
entirely and requires a token:

```
elevation_m = -10000 + ((R * 256 * 256 + G * 256 + B) * 0.1)
```

Ground resolution, `r = 156543.03392 · cos(lat) / 2^z` at 256 px tiles:

| Circuit | lat | z14 | z15 |
| --- | ---: | ---: | ---: |
| Silverstone | 52.08 | 5.88 m/px | **2.94 m/px** |
| Spa | 50.43 | 6.09 m/px | 3.04 m/px |
| Monza | 45.62 | 6.68 m/px | 3.34 m/px |
| Bahrain | 25.99 | 8.59 m/px | 4.29 m/px |

That is **tile** resolution, not source resolution. The underlying pixels at
Silverstone come from EU-DEM at 25 m or UK Environment Agency data, so z15 is
smoothly interpolated rather than genuinely 3 m. It is a good terrain mesh and
a bad measurement.

Terrarium attribution is a per-source mosaic list — Copernicus/EU-DEM, UK
Environment Agency (OGL), USGS (public domain), Geoscience Australia (CC BY
4.0), Kartverket, Austria DGM, Canada OGL, INEGI, LINZ, ArcticDEM. The full
list goes on `/data/`, not in a corner of the canvas.

### 1 m LiDAR — the only route to a measured camber

| Country | Product | Resolution | Licence | Vertical |
| --- | --- | --- | --- | --- |
| United States | USGS 3DEP | 1 m | public domain | NAVD 88 |
| England | EA LIDAR Composite DTM | 1 m, >95% of England | OGL v3 | OD Newlyn via OSTN'15, ±15 cm RMSE |
| Netherlands | AHN4 DSM + DTM | 0.5 m, 2020–2022 | CC0 | ~5 cm accuracy |

Discovering the covering US tile costs one request:

```
https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/identify
  ?geometry={"x":-97.6398,"y":30.1328,"spatialReference":{"wkid":4326}}
  &geometryType=esriGeometryPoint&returnGeometry=false&f=json
```

At COTA Turn 1 this returns `155.089` and names the 1 m source tile
`USGS_one_meter_x63y334_TX_Central_B1_2017.tif` under
`https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/`.

**Coverage reality check.** This covers Silverstone, Zandvoort, COTA, Miami,
Las Vegas and Indianapolis. It does **not** cover Spa, Monza, Monaco, Suzuka,
Bahrain, Jeddah, Singapore, Baku, Abu Dhabi, Qatar, Interlagos or Mexico. It is
a per-circuit enhancement, never a system-wide solution — and it misses five of
the eight first-wave hero circuits in [spec §9.1](../../../SPEC.md).

## 4. Why banking must be authored

Four independent reasons, each sufficient on its own:

1. **Telemetry is one curve.** A 1D line has no cross-section, so no camber.
   And per Discussion #116 you cannot even get two genuinely different lines
   from two drivers to interpolate a surface between — they are the same
   normalised line.
2. **MultiViewer gives `x[]`/`y[]` only.** There is no Z in the payload at all.
3. **30 m DEMs cannot resolve a 14 m track.** §3.
4. **OpenStreetMap has no camber tag in use on raceways.** `width` itself
   appears on only 1216 of 45 606 `highway=raceway` ways; superelevation on
   effectively none.

So banking is data the project authors, and the page says so. This is a direct
application of the honesty principle in [spec §3](../../../SPEC.md): a
hand-authored bank labelled as hand-authored is honest; a bank that emerges as a
side effect of a spline frame is a fabrication nobody chose.

### The authored table

Per circuit, a short table of `{corner_number, bank_degrees}` interpolated to 0°
between corners with a smoothstep over ~50 m of approach and exit.

| Circuit | Corner | Bank |
| --- | --- | ---: |
| Zandvoort | Hugenholtzbocht (T3) | **19°** |
| Zandvoort | Luyendijkbocht (final) | **18°** |
| Indianapolis (2000–07 road course) | oval turns | 9.2° |

Zandvoort T3 is *progressively* banked — a bowl, about 4.5° on the inside rising
to 19° on the outside — so a single constant is a simplification, and the hero
treatment models it as a cross-slope that varies with `v` across the ribbon.
**Almost every other modern F1 corner is flat or only mildly cambered.**
Zandvoort is the exception that makes the rule worth stating: the default entry
in the table is 0°, and a non-zero entry needs a citation.

### The geometry

Given a centreline point `P_i`, 2D unit tangent `T`, and bank angle `θ`
(positive = the left edge is higher):

```
N2D      = (-T.y,  T.x, 0)                 // left-hand horizontal normal
N_banked = N2D * cos(θ) + U * sin(θ)       // U = world up
left_i   = P_i + N_banked * w_left
right_i  = P_i − N_banked * w_right
```

And the inverse, where two edge elevations *are* available (the 1 m LiDAR case):

```
θ = atan2(z_left − z_right, w_left + w_right)
```

Face normals for lighting are computed per quad from the actual geometry —
`n = normalize(cross(T, right_i − left_i))` — not taken from a curve frame.

## 5. The frame the ribbon is built on

three.js 0.186.0 provides `Curve.computeFrenetFrames(segments, closed)`, and
`TubeGeometry` uses it. **The track ribbon does not.**

The commonly given reason — "Frenet normals flip at inflection points" — is
wrong about this implementation, and acting on a wrong reason leads to the wrong
fix. `computeFrenetFrames` is misnamed: reading
`src/extras/core/Curve.js`, after choosing an initial normal it runs a loop
commented "compute the slowly-varying normal and binormal vectors for each
segment", taking `vec = cross(tangent[i-1], tangent[i])` and
`theta = acos(dot(tangent[i-1], tangent[i]))` and rotating the *previous* normal
by that angle. It never touches the curvature or second-derivative vector, so
the classic binormal sign flip at an inflection does not occur. **It is already
a parallel-transport (rotation-minimising) frame.**

The real reasons to reject it for a road surface:

1. **The initial normal is arbitrary.** It is chosen as the axis "in the
   direction of the minimum tangent xyz component", so the starting roll of the
   ribbon is unpredictable and changes when the seam moves.
2. **Parallel transport conserves twist, not gravity.** A track built on it
   self-banks through elevation change and corners. Eau Rouge acquires a bank
   nobody authored.
3. **Closed curves get the error smeared everywhere.** With `closed === true`,
   three.js distributes a residual-twist correction evenly around the loop, so
   the roll error appears at every corner rather than only at the seam — harder
   to notice and harder to attribute.

A real circuit is near-flat in roll except where it is deliberately banked.
That is a statement about gravity, not about the curve, so the frame must be
defined by gravity:

```js
// per station i, three.js Y-up
const T = P[i + 1].clone().sub(P[i - 1]).normalize();  // central difference
const U = new THREE.Vector3(0, 1, 0);                   // world up
const R = new THREE.Vector3().crossVectors(T, U).normalize();  // horizontal right
const N = new THREE.Vector3().crossVectors(R, T);              // surface up

// apply authored banking by rotating R and N about T by theta
const Rb = R.clone().multiplyScalar(Math.cos(theta))
            .addScaledVector(N, -Math.sin(theta));

const left  = P[i].clone().addScaledVector(Rb, -halfWidthLeft);
const right = P[i].clone().addScaledVector(Rb,  halfWidthRight);
```

This is degenerate only where `T` is parallel to `U` — a vertical track, which
does not exist. Everything stays level unless the authored table says otherwise.

## 6. Width

The only open source of per-point width is TUMFTM/racetrack-database,
LGPL-3.0, `tracks/*.csv` with header `# x_m,y_m,w_tr_right_m,w_tr_left_m`.
Silverstone.csv: 1178 points, mean spacing 4.997 m (range 4.683–5.162), closed
length 5886.8 m, total width **11.27–17.84 m, mean 13.82 m**.

It covers 25 tracks of which roughly 19 are F1 (Brands Hatch, Moscow Raceway,
Norisring, Nürburgring, Oschersleben and Zandvoort are listed as DTM; IMS as
IndyCar), and about a third of the 2026 calendar is absent: Jeddah, Miami,
Las Vegas, Losail, Imola, Baku, Singapore, Zandvoort-in-its-F1-layout, Madrid,
Portimão. Its widths are image-processing estimates from satellite imagery, not
surveys.

Defaults where it is absent, per FIA Appendix O guidance of a 10 m minimum and
12 m preferred:

| Context | Width |
| --- | --- |
| Absolute minimum | 12 m |
| Typical modern F1 | 13–14 m |
| Main straight / pit straight | 15–18 m |

The safest use of TUMFTM under LGPL-3.0 — and under the possible ODbL
obligation underneath it, since its centrelines came from OpenStreetMap — is as
a **per-circuit calibration**: derive a mean width and a handful of
width-varying segments, attribute clearly, and default the rest. See
[OSM extraction](osm-extraction.md) §6 and the role table in
[spec §6.1](../../../SPEC.md).

## 7. Vertical exaggeration

`verticalExaggeration = 1.0` is the default and the honest choice. 1.5–2.0 reads
better on circuits whose elevation is subtle, and is permitted **only with a
visible label stating the factor**. Spa, Interlagos, Zandvoort, Spielberg and
Suzuka need no help; Sakhir and Yas Marina are where the temptation lives.
