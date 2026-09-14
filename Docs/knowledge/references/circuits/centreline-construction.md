---
type: Reference
title: Centreline Construction
description: How a usable circuit centreline is built from FastF1 position data and from the open geometry repositories — resampling, median aggregation, closure and arc-length parameterisation.
resource: https://docs.fastf1.dev/api_reference/telemetry.html
tags:
  - centreline
  - resampling
  - arc-length
  - fastf1
  - geometry
  - threejs
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_telemetry_docs
    resource: https://docs.fastf1.dev/api_reference/telemetry.html
    title: FastF1 Telemetry API reference
  - id: fastf1_disc_116
    resource: https://github.com/theOehrly/Fast-F1/discussions/116
    title: Fast-F1 Discussion #116 — normalized track position
  - id: mv_silverstone
    resource: https://api.multiviewer.app/api/v1/circuits/2/2022
    title: MultiViewer circuit payload, circuitKey 2 (Silverstone)
  - id: mv_spa
    resource: https://api.multiviewer.app/api/v1/circuits/7/2024
    title: MultiViewer circuit payload, circuitKey 7 (Spa)
  - id: bacinger_repo
    resource: https://github.com/bacinger/f1-circuits
    title: bacinger/f1-circuits
  - id: tumftm_silverstone
    resource: https://raw.githubusercontent.com/TUMFTM/racetrack-database/master/tracks/Silverstone.csv
    title: TUMFTM/racetrack-database Silverstone.csv
  - id: threejs_curve
    resource: https://raw.githubusercontent.com/mrdoob/three.js/dev/src/extras/core/Curve.js
    title: three.js src/extras/core/Curve.js
status: stable
---

# Centreline Construction

A circuit centreline is the spine every other piece of geometry hangs from:
the 3D ribbon, corner markers, mini-sector boundaries, DRS zones, the race
replay's distance axis. Getting it wrong is not a rendering artefact — it
shifts every derived distance on the page.

Three sources exist, none of them is a centreline as delivered, and the
correct answer is a hybrid.

## 1. The four candidate sources

| Source | What it actually is | Coverage | Z? | Licence |
| --- | --- | --- | --- | --- |
| MultiViewer `x[]`/`y[]` | One sampled lap (`candidateLap`), 2D | 32 circuits, frozen ~2021–2023 | no | **no published terms — blocked** |
| FastF1 / OpenF1 position | The racing line, sampled per lap | 2020+ (unit cutoff) | **yes** | build-time only |
| bacinger/f1-circuits | Hand-traced closed LineString | **40** circuits | no | MIT wrapper, traced from Google My Maps |
| TUMFTM/racetrack-database | Smoothed OSM centreline + widths | 25 tracks, ~19 F1 | no | LGPL-3.0 |

Two of those entries are traps.

**MultiViewer's centreline is a single lap, not a survey.** Silverstone's
`candidateLap` is `{"driverNumber":"5","lapNumber":2,"session":"FP1",
"lapTime":119.168}` from 2022. It apexes, and it is measurably short.

**TUMFTM's centreline is deliberately off-centre.** Its own README: "The center
lines were smoothed. Therefore, they do not lie perfectly in the middle of the
track anymore." Its widths are "extracted from satellite images using an image
processing algorithm" — estimates of unstated accuracy, not surveyed values.

## 2. Why a fast lap is not a centreline

`session.laps.pick_fastest().get_pos_data()` is what every FastF1 tutorial
shows. It is correct for a 2D silhouette and wrong for geometry: it sits on the
inside kerb at every apex, up to half a track width (6–9 m) from centre. The
error is systematic and measurable as a **length deficit**:

| Circuit | Traced LineString | MultiViewer (one lap) | Deficit |
| --- | ---: | ---: | ---: |
| Silverstone | 5884.4 m | 5834.6 m | −0.85% |
| Spa | 6986.2 m | 6961.7 m | −0.35% |
| Monaco | 3328.0 m | 3269.5 m | −1.76% |
| Monza | 5793.0 m | 5764.7 m | −0.49% |
| Zandvoort | 4260.2 m | 4222.2 m | −0.89% |

Monaco is the worst case, which is what you would expect: the most corner, the
least straight.

And you cannot escape it by averaging drivers. The FastF1 maintainer's position
in [Discussion #116](https://github.com/theOehrly/Fast-F1/discussions/116) is
that the feed is a *normalised track position* driving the broadcast
driver-tracker graphic: "All coordinates show the same line. Minor deviations
are likely due to quantization inaccuracies", and "It's certainly not possible
to analyze drivers lines through a corner." OpenF1's documentation says the same
thing independently — the data "cannot distinguish whether cars are on the left
or right side of the track". **Twenty drivers give you one line, twenty times.**

## 3. Arc-length resampling — the mandatory first step

Every downstream operation (alignment, median aggregation, curvature, mesh
stations) assumes constant Δs. Nothing upstream provides it: MultiViewer
samples are time-uniform, so they bunch in slow corners; traced and OSM nodes
are placed by curvature.

Skipping this step is not a quality degradation, it is a failure. Centroid
alignment of Silverstone scored **RMS 67.3 m (max 301.9 m)** on raw vertices
and **4.6 m** after resampling — a 15× difference from one missing step.

```python
import numpy as np

def resample_closed(pts, n):
    """pts: (m, k) array of a CLOSED ring (first point not repeated).
    Returns n points at constant arc-length spacing."""
    ring = np.vstack([pts, pts[:1]])
    seg  = np.linalg.norm(np.diff(ring[:, :2], axis=0), axis=1)
    s    = np.concatenate([[0.0], np.cumsum(seg)])
    L    = s[-1]
    target = L * np.arange(n) / n              # note: /n, not /(n-1)
    return np.column_stack([np.interp(target, s, ring[:, j])
                            for j in range(pts.shape[1])]), L
```

Two details that bite:

- Arc length is measured in the **2D plane** for parameterisation. Including Z
  makes `s` the 3D path length, which is 0.1–0.5% longer at an elevation-heavy
  circuit and no longer matches FastF1's `Distance` channel or MultiViewer's
  corner `length` field.
- Use `L * i / n`, not `L * i / (n-1)`, for a closed ring. The latter duplicates
  the seam point and produces a zero-length final quad.

## 4. The median-lap pipeline (telemetry-only)

Used where no traced geometry exists, and always for the Z channel.

1. `session.load(telemetry=True)`; take `session.laps.pick_quicklaps()` and drop
   any lap with a pit in/out time.
2. Per lap: `tel = lap.get_telemetry(frequency="original")`, filter
   `tel["Source"] == "pos"` (this is exactly what FastF1 itself does in
   `CircuitInfo.add_marker_distance()`), drop `Status == "OffTrack"`, then
   `add_distance()` and `add_relative_distance()`.
3. Resample every lap onto a common grid of `M` stations in
   `RelativeDistance ∈ [0, 1)`. `M = ceil(lap_length_m / 2)` gives 2 m spacing —
   3481 stations for Spa, 2942 for Silverstone.
4. Take the per-station **median** of X, Y, Z across laps. Median, not mean: it
   rejects excursions and dropouts without a threshold to tune.
5. Smooth with a closed-form Savitzky–Golay or a small Gaussian (σ ≈ 3
   stations), **wrapping the window across the start/finish seam**. A
   non-wrapping filter leaves a visible kink exactly where the hero camera
   starts.
6. Force closure (§6).

What this yields is the **median racing line** — cleaner than one lap, still
not the geometric centre. It is the right input for a racing-line overlay and
for Z; it is not the right input for the track ribbon's spine.

## 5. The adopted hybrid

> **XY from the traced/OSM LineString. Z from telemetry. Width from TUMFTM
> where it exists, a constant elsewhere.**

The traced geometry is genuinely centred and accurate in length (Silverstone
−0.113%, Monza −0.002%, Monaco −0.27%, Spa −0.255%, Madrid −0.687% against
declared lengths). Telemetry Z resolves 0.1 m and follows the actual tarmac,
where a 30 m DEM cell is wider than the track.

Transfer procedure, per vertex of the XY centreline:

1. Align the two polylines using the translation anchors in
   [Coordinate systems](coordinate-systems.md) §5.
2. Find the k = 5 nearest telemetry samples by 2D distance — the same
   nearest-neighbour minimisation FastF1 uses in `add_marker_distance()`.
3. Take an inverse-distance-weighted mean of their Z.
4. Smooth the resulting Z profile along arc length (σ ≈ 3 stations), wrapping
   the seam.

Error bound: the horizontal disagreement between the two datasets is 2.8–5.2 m
RMS, so the Z error introduced is bounded by `5 m × local gradient` — **under
0.5 m even on Eau Rouge's ~17% gradient**, and far below that everywhere else.

## 6. Closure

A closed ring is required for `CatmullRomCurve3(points, true, …)`, for a
watertight ribbon, and for any modular arc-length lookup. Median aggregation and
smoothing both leave a seam.

```python
# Blend the last K stations toward the first point so the ring is watertight.
K = 20
gap = pts[0] - pts[-1]
for i in range(K):
    w = (i + 1) / K                      # 0 -> 1 across the blend window
    pts[-K + i] += gap * (w * w * (3 - 2 * w))   # smoothstep, C1 at both ends
```

Use a smoothstep rather than a linear ramp: a linear blend is C⁰ at the window
edges and produces a curvature discontinuity that a Catmull–Rom spline will
amplify into a visible wobble.

Acceptance checks before a centreline is written to the registry:

| Check | Threshold |
| --- | --- |
| `‖pts[0] − pts[-1]‖` after closure | < 0.01 m |
| Measured length vs declared circuit length | within 1.5% |
| Station spacing coefficient of variation | < 0.02 |
| Signed area sign vs source ring | identical (catches mirroring) |
| Max `|κ|` | < 1/6 m⁻¹ (no sub-6 m radius; Monaco's hairpin is ~8 m) |

## 7. Source resolution is not uniform

MultiViewer's vertex density varies by a factor of ~3.5 between circuits, so it
is not a mesh-ready curve as delivered:

| Circuit | Points | Centreline length | Mean vertex spacing |
| --- | ---: | ---: | ---: |
| Monaco | 683 | 3269.5 m | 4.79 m |
| Silverstone | 916 | 5834.6 m | 6.37 m |
| Spa | 1005 | 6961.7 m | 6.93 m |
| Monza | 752 | 5764.7 m | 7.67 m |
| Interlagos | 283 | — | ~15 m |
| Suzuka | 335 | — | ~17 m |

Other measured point counts: Catalunya 442, Singapore 544, Melbourne 618,
Sakhir 730, Miami 757. **A ribbon extruded directly on these vertices visibly
facets at Interlagos and Suzuka.** Resampling and splining is mandatory, not an
optimisation.

TUMFTM's spacing is close to uniform but not exact: Silverstone.csv has 1178
points at **mean 4.997 m, range 4.683–5.162 m**, closed length 5886.8 m. Treat
it as "resampled to approximately 5 m".

## 8. Splining and station count

```js
const curve = new THREE.CatmullRomCurve3(points, /*closed=*/true, 'centripetal');
```

`'centripetal'` is the parameterisation to use. `'chordal'` and `'catmullrom'`
overshoot and can self-intersect at tight radii — Monaco's Grand Hotel hairpin
is about 8 m, which is where the difference is visible rather than academic.

Station count at 2 m spacing, with 2 vertices and 6 indices per station:

| Circuit | Stations | Vertices | Indices |
| --- | ---: | ---: | ---: |
| Spa | 3481 | 6962 | ~20 880 |
| Silverstone | 2942 | 5884 | ~17 650 |

At 1 m spacing Spa is ~14 k vertices. Both are trivial for a single-circuit
page; the constraint is payload, not draw calls. Carry two per-vertex
attributes instead of extra geometry:

- `u` — arc-length fraction along the ribbon, for distance-based shading
  (speed, gear, mini-sector dominance).
- `v` — 0 at the left edge, 1 at the right, so kerb striping and a centre line
  are fragment-shader work rather than additional meshes.

Quantise the emitted buffer to 16-bit over the circuit bbox: ~6 KB per circuit
at ~0.03 m precision. See [Coordinate systems](coordinate-systems.md) §8.

## 9. Curvature

Signed curvature drives corner classification, kerb placement and the
detection fallback in
[Corner and sector detection](corner-and-sector-detection.md).

For three consecutive stations A, B, C:

```
kappa = 2 * cross2(B - A, C - B) / (|B - A| * |C - B| * |C - A|)
r     = 1 / |kappa|
```

`cross2(p, q) = p.x*q.y − p.y*q.x`. The sign gives turn direction. Classify a
station as cornering when `|kappa| > 1/300` (radius under 300 m). Compute it on
the **resampled** centreline — on raw time-uniform samples the denominator
collapses in slow corners and the result is noise.

## 10. What is not derivable

Kerbs, run-off, gravel traps and barriers are absent from every source. Global
OpenStreetMap counts: `raceway=kerb` 72 uses, `raceway=runoff_area` 20,
`raceway="gravel trap"` 39, `raceway=pitlane` 47 plus `raceway=pit_lane` 26,
`area:highway=raceway` 207 objects — against 45 606 `highway=raceway` ways.
That is statistical noise; no F1 circuit has complete kerb or run-off polygons.

They are generated procedurally from curvature, and the page says so. Per
[spec §9.1](../../../SPEC.md) the standard tier is labelled **"centreline +
modelled width"**, not presented as a survey. An under-detailed ribbon that is
geometrically truthful is the correct trade under the site's honesty principle;
a speculative kerb-and-gravel model that is subtly wrong everywhere is not.
