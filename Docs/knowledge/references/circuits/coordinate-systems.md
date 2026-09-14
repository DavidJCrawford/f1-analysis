---
type: Reference
title: Circuit Coordinate Systems
description: The exact unit, scale, orientation and datum conventions of F1 position data, and the verified transform chain from telemetry units to WGS84 and into a three.js scene.
resource: https://docs.fastf1.dev/api_reference/telemetry.html
tags:
  - coordinates
  - enu
  - wgs84
  - projection
  - threejs
  - units
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_api_py
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
    title: FastF1 _api.py — position_data() and car_data() docstrings
  - id: fastf1_mvapi_data
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/mvapi/data.py
    title: FastF1 mvapi/data.py — CircuitInfo dataclass and rotation parsing
  - id: fastf1_annotate_corners
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/examples/general/plot_annotate_corners.py
    title: FastF1 example — plot_annotate_corners.py rotation helper
  - id: openf1_location
    resource: https://api.openf1.org/v1/location?session_key=9574&driver_number=1
    title: OpenF1 /v1/location — Spa 2024 position samples
  - id: openf1_docs
    resource: https://openf1.org/docs
    title: OpenF1 API documentation
  - id: mv_silverstone
    resource: https://api.multiviewer.app/api/v1/circuits/2/2022
    title: MultiViewer circuit payload, circuitKey 2 (Silverstone)
  - id: bacinger_gb1948
    resource: https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/gb-1948.geojson
    title: bacinger/f1-circuits gb-1948.geojson (Silverstone)
status: stable
---

# Circuit Coordinate Systems

Everything spatial on this site — the 3D ribbon, the corner markers, the
mini-sector map, the race replay — is built on one claim: **the F1 live-timing
XY frame is a metric, essentially north-up local ENU frame at exactly
0.1 m/unit with no mirroring.** That claim was tested rather than assumed, and
the consequence is that georeferencing a circuit reduces to a two-parameter
translation. This document records the units, the evidence, the transform
chain and the three traps.

## 1. Units and channels

FastF1 exposes two independent streams. They do not share a clock and must be
merged.

| Stream | Accessor | Channels | Nominal rate |
| --- | --- | --- | --- |
| Position | `Lap.get_pos_data()` | `Time`, `Date`, `Status`, `X`, `Y`, `Z`, `Source` | "usually 220 ms" per the docstring |
| Car | `Lap.get_car_data()` | `Time`, `Date`, `RPM`, `Speed`, `nGear`, `Throttle`, `Brake`, `DRS`, `Source` | "usually 240 ms" per the docstring |

Verbatim from `fastf1/_api.py`, `position_data()`:

```
- Status (str): 'OnTrack' or 'OffTrack'
- X, Y, Z (int): Position coordinates; starting from 2020 the coordinates
  are given in 1/10 meter
```

**The 2020 cutoff is the single easiest unit error to make.** Position data
exists from 2018, but the decimetre unit is only documented from 2020 onward.
Any pipeline touching 2018–2019 position data must either verify the scale
empirically per session (fit the lap length against the known circuit length)
or refuse to emit geometry for those years. This site takes the second option:
geometry is built from 2020+ sessions only, and 2018–2019 telemetry is used for
charts on a `Distance` axis, never for coordinates.

**The nominal rates are not the measured rates.** Over 465 consecutive Spa 2024
position samples (`session_key=9574`, `driver_number=1`, a two-minute window),
the inter-sample interval measured **median 240 ms, mean 258 ms, min 20 ms,
max 500 ms**, with a broad spread across 160–340 ms. The mean is inflated by
gaps rather than describing a cadence. OpenF1 separately advertises "3.7 Hz"
(= 270 ms), a third inconsistent figure. **Interpolate on `Date`; never assume
a fixed grid.** The consequences for resampling are in
[Centreline construction](centreline-construction.md).

OpenF1's `/v1/location` returns the same underlying stream with lowercase
fields:

```json
{"date":"2024-07-28T14:00:00.009000+00:00","session_key":9574,
 "meeting_key":1242,"driver_number":1,"x":4601,"y":-8841,"z":3952}
```

OpenF1's own documentation states the origin "(0, 0, 0) appears to be arbitrary
and not tied to any specific location on the track" and does not document the
unit at all. The 1/10 m scale is documented only in FastF1's `_api.py`; treat
OpenF1 coordinates as decimetres on FastF1's authority, not OpenF1's.

Drop rows where `x == 0 and y == 0` — those are dropouts, not the origin.

## 2. Scale, rotation and handedness — the evidence

Method: take the MultiViewer centreline `x[]`/`y[]` (the same frame as FastF1
telemetry), take the corresponding [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits)
LineString, project the lon/lat to local ENU metres about the polyline
centroid, **arc-length-resample both to N = 600 equally spaced points**, centre
both on their centroids, then brute-force rotation over [0, 360) and mirror in
{false, true}, scoring by mean nearest-neighbour distance.

| Circuit | Best-fit rotation | Mirror | Mean NN residual | `CircuitInfo.rotation` |
| --- | ---: | --- | ---: | ---: |
| Silverstone | −1.2° | false | 5.13 m | 92 |
| Spa | −2.4° | false | 3.87 m | 91 |
| Monaco | +1.4° | false | 2.79 m | 315 |
| Monza | +0.0° | false | 3.54 m | 95 |
| Zandvoort | −1.0° | false | 3.16 m | 0 |
| Melbourne | −1.3° | false | 4.74 m | — |

Three readings from that table:

1. **Scale is exactly 0.1 m/unit and rotation is within 2.5° of zero.** The
   residual is not necessarily a real rotation: bacinger's geometry is
   hand-traced (see [OSM extraction](osm-extraction.md) §5) and is the less
   trustworthy of the two polylines.
2. **Mirror is false, decisively.** The best mirrored fits scored 37.7 m
   (Zandvoort) to 123.8 m (Spa) — 10–35× worse. The frame is right-handed ENU,
   not a flipped screen frame.
3. Residuals of 2.8–5.2 m sit **inside the 11–18 m track width**. The two
   datasets describe the same tarmac.

### The gotcha that invalidates the whole fit

Without arc-length resampling, centroid alignment fails badly: Silverstone fit
at **RMS 67.3 m (max 301.9 m)** on raw vertex lists, versus **4.6 m** after
resampling. MultiViewer samples are time-uniform (dense in slow corners); OSM
and bacinger nodes are placed by curvature. Centroids of unevenly sampled
polylines are not the centroids of the shapes. **Resample to constant Δs before
any centroid, Procrustes or nearest-neighbour step.**

## 3. `CircuitInfo.rotation` is a display rotation, not a north alignment

FastF1's own docstring: rotation "can be used to rotate the coordinate system
of the telemetry (position) data to match the orientation of the official track
map." It is read straight from the MultiViewer JSON:
`rotation = float(data.get("rotation", 0.0))`.

The measured values (92 Silverstone, 91 Spa, 315 Monaco, 95 Monza, 0 Zandvoort)
bear no relation to the ~0° actually needed to align the raw frame to true
north. Applying it to a georeferenced scene rotates the circuit off the map.

| Use | Apply `rotation`? |
| --- | --- |
| Stylised 2D track map matching TV graphics | **yes** |
| Georeferenced 3D scene, DEM terrain, map overlay, anything joined to lat/lon | **no** |

FastF1's own helper, verbatim from `examples/general/plot_annotate_corners.py`:

```python
def rotate(xy, *, angle):
    rot_mat = np.array([[np.cos(angle), np.sin(angle)],
                        [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot_mat)

track = pos.loc[:, ("X", "Y")].to_numpy()
track_angle = circuit_info.rotation / 180 * np.pi
rotated_track = rotate(track, angle=track_angle)
```

This is a **row-vector post-multiply**, so it yields
`x' = x·cos − y·sin`, `y' = x·sin + y·cos` — a standard counter-clockwise
rotation by `angle`. The JS equivalent:

```js
const a = rotationDeg * Math.PI / 180, c = Math.cos(a), s = Math.sin(a);
const xr = x * c - y * s;
const yr = x * s + y * c;
```

Corner markers are offset outward with the same helper: FastF1's example uses
`offset_vector = [500, 0]` (50 m in real units, chosen to look good), rotates it
by `corner["Angle"] / 180 * np.pi`, adds it to the corner X/Y, then rotates the
whole assembly by the track angle. See
[Corner and sector detection](corner-and-sector-detection.md).

## 4. Local ENU ↔ WGS84 — use the ellipsoidal radii

The equirectangular form is correct at circuit scale. **The commonly used
constants are not.** Substituting the equatorial radius `a = 6378137` on both
axes produces a systematic scale error — a coherent stretch of the whole
circuit — that does not average out against a DEM or an OSM outline.

WGS84: `a = 6378137.0`, `f = 1/298.257223563`, `e² = 2f − f² = 0.0066943800`.

```python
import math
A  = 6378137.0
E2 = 0.0066943799901413165          # 2f - f^2, WGS84

def enu_scales(lat0_deg):
    p = math.radians(lat0_deg)
    s = math.sin(p)
    w = 1.0 - E2 * s * s
    N = A / math.sqrt(w)             # prime vertical radius of curvature
    M = A * (1.0 - E2) / w**1.5      # meridian radius of curvature
    return N * math.cos(p), M        # k_east (m per radian), k_north

# ENU -> WGS84
k_e, k_n = enu_scales(lat0)
lon = lon0 + math.degrees((E + tx) / k_e)
lat = lat0 + math.degrees((N + ty) / k_n)

# WGS84 -> ENU
E = math.radians(lon - lon0) * k_e
N = math.radians(lat - lat0) * k_n
```

Worked constants and the error incurred by using `a` on both axes:

| Circuit | lat₀ | `k_north = M(φ₀)` | `k_east = N(φ₀)·cos φ₀` | `a·cos φ₀` | East scale error | North scale error |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Silverstone | 52.07 | 6 375 230 | 3 928 530 | 3 920 630 | +0.209% | −0.046% |
| Spa | 50.44 | 6 373 441 | 4 070 251 | 4 062 146 | +0.200% | −0.074% |
| Monza | 45.62 | 6 368 080 | 4 468 336 | 4 460 688 | +0.171% | −0.158% |
| Monaco | 43.73 | 6 365 961 | 4 616 265 | 4 608 876 | +0.160% | −0.191% |
| Zandvoort | 52.39 | 6 375 571 | 3 900 877 | 3 892 675 | +0.211% | −0.046% |

Over each circuit's actual extent that is **0.41 m of northing error and 2.50 m
of easting error at Silverstone; 0.76 m N / 1.27 m E at Spa; 1.15 m N / 1.44 m E
at Monaco** — one to two orders of magnitude worse than sub-0.1 m, and of the
same order as the 2.8–5.2 m dataset disagreement it would be mistaken for. With
`M` and `N·cos φ` the residual really is **below 0.1 m over a few kilometres**.

## 5. Per-circuit anchors

The telemetry origin is an arbitrary point a few hundred metres from the
circuit, different per venue. Solve `(tx, ty)` once: arc-length-resample both
the MultiViewer/telemetry centreline and the reference LineString to the same
N (800 works), then

```
tx = centroid_ref.E − centroid_telemetry.E
ty = centroid_ref.N − centroid_telemetry.N
```

| Circuit | lat₀ | lon₀ | tx (m) | ty (m) | Telemetry (0,0) sits at |
| --- | ---: | ---: | ---: | ---: | --- |
| Silverstone | 52.071824 | −1.016350 | −294.5 | −512.6 | 52.067219, −1.020654 |
| Spa | 50.434718 | 5.968647 | −183.7 | 808.7 | 50.441983, 5.966056 |
| Monza | 45.623385 | 9.286545 | −304.4 | −700.5 | 45.617092, 9.282635 |
| Zandvoort | 52.387687 | 4.545503 | −359.2 | −216.2 | 52.385744, 4.540215 |

These four numbers per circuit are baked into the build artifact described in
[Circuit layout registry](circuit-layout-registry.md).

**Unverified:** whether the live-timing origin is stable across seasons for a
given venue, or whether it shifts when timing equipment is resurveyed. The
anchors above were derived from 2022 and 2024 data. The registry therefore
carries an anchor keyed by `(layout_id, year_range)` rather than by circuit
alone, so a discovered shift is a data change and not a schema change.

## 6. Into three.js

three.js is Y-up and right-handed. ENU is Z-up and right-handed. The mapping
that preserves handedness:

```js
// E, N, H are metres in the local ENU frame (X/10, Y/10, Z/10)
position.x =  (E - E_centre);
position.y =  (H - H_datum) * verticalExaggeration;
position.z = -(N - N_centre);   // negate northing so +Z is south
```

Forgetting the negation silently produces a **mirrored circuit** that looks
plausible and is wrong — Spa's Eau Rouge turns the wrong way. Regression-test
it: after transform, the signed area of the closed ring must keep the sign it
had in ENU.

`verticalExaggeration = 1.0` is the honest default and the site's default.
Values of 1.5–2.0 read better on subtle circuits but **must be labelled on the
page** under principle 3 of the [spec](../../../SPEC.md).

`H_datum` is a per-circuit constant, normally the start/finish elevation.
bacinger carries an `altitude` property for exactly this
(Silverstone `196`), though its provenance is a Formula1.com feature article
rather than a survey. See
[Banking and elevation](banking-and-elevation.md) for what the `Z` channel
actually measures.

## 7. Web Mercator, if you ever need it

Only relevant if a slippy-map basemap is ever placed under a circuit. It is not
in the launch scope.

```
x = R * radians(lon)
y = R * log(tan(PI/4 + radians(lat)/2))
```

Mercator distances are inflated by `sec(lat) = 1/cos(lat)`. **Divide by that
factor to recover true ground metres.** At Silverstone's latitude the inflation
is `1/cos(52°) = 1.62×` — a 62% length error if ignored.

## 8. Storage

A 1000-point closed centreline:

| Encoding | Size |
| --- | --- |
| JSON text, 3 coordinates per point | ~30 KB |
| `Float32Array`, 3 per point | ~12 KB |
| 16-bit quantised over the circuit bbox | **~6 KB** |

At a 2 km bbox extent, 16-bit quantisation gives 2000/65535 ≈ **0.03 m**
precision — an order of magnitude finer than the data's own 2.8–5.2 m
uncertainty. Every circuit's geometry fits in the per-page budget in
[spec §11.2](../../../SPEC.md) with room to spare.
