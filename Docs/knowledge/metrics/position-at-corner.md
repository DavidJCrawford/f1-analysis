---
type: Metric
title: Position at corner
description: Deriving the race order at any point on track — not just at the finish line — by projecting car position telemetry onto the circuit centreline and ordering drivers by total distance travelled.
resource: /methods/position-at-corner/
tags: [telemetry, position, centreline, arc-length, corner, race-order, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_telemetry
    resource: https://docs.fastf1.dev/api_reference/telemetry.html
    title: FastF1 telemetry API — position channels, add_distance, slice_by_lap
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — Session.pos_data, get_circuit_info, CircuitInfo.corners
  - id: tumftm_racetrack_database
    resource: https://github.com/TUMFTM/racetrack-database
    title: TUMFTM/racetrack-database — centreline and track width, LGPL-3.0
  - id: bacinger_f1_circuits
    resource: https://github.com/bacinger/f1-circuits
    title: bacinger/f1-circuits — 40 circuit outlines, MIT
  - id: f1_3d_visualization
    resource: https://github.com/lohithburra01/F1-3D-VISUALIZATION
    title: lohithburra01/F1-3D-VISUALIZATION — FastF1 to GIS to 3D pipeline
status: stable
---

# Position at corner

Lap charts tell you the order at the finish line. This metric tells you the
order **anywhere** — at the apex of Eau Rouge, at the braking point for
Turn 1, at the exit of the Parabolica — for every lap of every race from 2018
onward.

It is the headline analytical capability of the site, and it is what makes the
3D replay an analysis instrument rather than an animation: a car's place in the
race becomes a function of where it is on the track, not of where the timing
loop happens to be.

## What the data gives us

FastF1's `Session.pos_data` carries, per driver, a position stream with
channels **`X`, `Y`, `Z`** and **`Status`**, alongside `Time`, `SessionTime`,
`Date` and `Source`. `Session.get_circuit_info()` returns a `CircuitInfo`
object whose `corners` DataFrame has columns **`X`, `Y`, `Number`, `Letter`,
`Angle`, `Distance`** — plus `marshal_lights`, `marshal_sectors` and
`rotation` (degrees).

That `Distance` column is the hinge of the whole method. It is the corner's
position measured **along the track**, in the same arc-length parameterisation
that `Telemetry.add_distance()` produces. Corner geometry and car position can
therefore be expressed in one shared coordinate: distance from the start line.

### Two unit traps, both dated

**Position coordinates are in 1/10 metre from 2020 onward.** The unit has a
date cutoff, it is not announced in the column name, and a pipeline that
applies one scale factor to the whole telemetry era produces a track ten times
too large or too small for part of it. Scale is resolved per season, and the
resolution is regression-tested against a known circuit length.

**The sample rate is ~240 ms, not the documented 220 ms.** Measured median
interval on the 2024 British Grand Prix: **241.0 ms**. The mean of 259.3 ms is
inflated by dropouts and is the wrong statistic to quote. `Telemetry.TELEMETRY_FREQUENCY`
defaults to `'original'`, which is what this method uses — resampling before
projection throws away the only resolution there is.

The `Status` channel exists on the position stream, and pit-lane and off-track
samples must be handled before projection. **The exact vocabulary of its values
is not established by this project's research and is marked unverified**; the
pipeline determines it empirically per season and records what it found.

## The method

### Step 1 — establish a centreline

A polyline `C = {(x_i, y_i)}` around the circuit with a cumulative arc length
`s_i` at each vertex, and total lap length `S`.

| Source | Coverage | Licence | Role |
| --- | --- | --- | --- |
| TUMFTM/racetrack-database | 25 tracks (~19 F1) | **LGPL-3.0** | Centreline + width. Build-time only; obligations tracked. |
| bacinger/f1-circuits | 40 circuits | MIT | Redistributable outlines. Traced from Google My Maps + Wikipedia — **not** OSM-derived. |
| MultiViewer API | ~730-point centreline + corners + marshal sectors | **no terms published** | Best geometry available, **blocked pending contact**. |
| Telemetry-derived | any circuit with 2018+ data | — | Median of many fast laps' position traces. |

Measured length error against declared circuit length for the bacinger set:
Silverstone −0.113%, Monza −0.002%, Monaco −0.27%, Spa −0.255%. That is good
enough for ordering and not good enough for a lap record.

The telemetry-derived fallback matters because it is the only universal one: a
centreline can always be recovered from the position streams themselves by
taking a robust central path across many clean laps. It is also the only one
guaranteed to be in the same coordinate frame as the data being projected,
which removes an entire class of registration error.

Where an external centreline is used, the local ENU ↔ WGS84 conversion must use
the **ellipsoidal** radii — `k_east = N(φ₀)·cos(φ₀)`, `k_north = M(φ₀)`. The
naive equirectangular approximation using the equatorial radius `a = 6378137`
on both axes introduces **0.4–2.5 m of systematic scale error** at F1
latitudes; the ellipsoidal form keeps residuals below 0.1 m over a few
kilometres.

### Step 2 — project each sample onto the centreline

For a car sample `p = (x, y)`, find the segment `[C_i, C_{i+1}]` minimising
perpendicular distance, and the parameter `t ∈ [0,1]` of the foot of the
perpendicular:

```
d  = C_{i+1} − C_i
t  = clamp( ((p − C_i) · d) / (d · d), 0, 1 )
s  = s_i + t · |d|
e  = | (p − C_i) − t·d |          # lateral offset from the centreline
```

`s` is the along-track distance; `e` is how far off the centreline the car is,
and it is useful in its own right (racing line, off-track excursions, pit lane
detection).

**Two implementation requirements.**

*Spatial index.* A naive nearest-segment search over a 730-point centreline for
every sample of every car for a whole race is millions of distance evaluations.
Build a uniform grid or k-d tree over the centreline once per circuit and
search locally.

*Continuity constraint.* Do not search globally on every sample. Seed the
search from the previous sample's segment and search a window forward. This
matters at hairpins and at any point where the track doubles back on itself —
Monaco's Grand Hotel, Zandvoort's banking, the Bahrain infield — where the
geometrically nearest centreline point can be on the *other* side of the
corner. Without the continuity constraint, `s` jumps backwards by hundreds of
metres and the derived order is nonsense for the rest of the lap.

### Step 3 — total distance

```
D_d(t) = (laps_completed_d(t) − 1) · S + s_d(t)
```

`laps_completed` comes from the lap table (`LapNumber` transitions on
`session.laps`), not from counting `s` wraparounds — a wraparound counter
double-counts on any sample noise near the start line and loses a lap on any
dropout across it.

`D_d(t)` is monotone non-decreasing in `t` for a moving car, which is what
makes everything after this step well behaved.

### Step 4a — order at a point on track (the primary construction)

"Who was ahead at Turn 3 on lap 27?" is a question about **crossing times**,
not about positions at an instant.

```
s_corner = circuit_info.corners.loc[corner_number, "Distance"]
target   = (lap − 1) · S + s_corner

for each driver d:
    find t_d such that D_d(t_d) = target      # monotone → single root
order drivers by ascending t_d
```

Solving `D_d(t) = target` is a one-dimensional root find on a monotone
function. Linear interpolation between the two bracketing samples is adequate;
monotone cubic (PCHIP) interpolation is better and cannot overshoot.

This formulation is robust for a reason worth stating: it interpolates **time**
rather than **position**, and the interpolation error in time scales with the
car's speed variation over one sample interval, which is small, rather than
with its speed, which is large.

### Step 4b — order at an instant (for a replay scrub)

For the 3D replay, the question is inverted: at session time `t`, order all
cars by `D_d(t)`. This needs each car's `D` interpolated to a common clock,
which is the less robust direction, and it is used for the visual replay rather
than for published orderings.

## Accuracy limits — stated plainly

This is where the metric earns or loses trust.

| Source of error | Magnitude | Notes |
| --- | ---: | --- |
| Native sample interval | 241.0 ms (median, 2024 British GP) | At 70 m/s that is **16.9 m** between samples |
| Shipped 5 Hz replay | 200 ms | 14.0 m at 70 m/s |
| Shipped 2 Hz replay | 500 ms | 35.0 m at 70 m/s |
| Centreline length error | −0.002% to −0.27% (bacinger set) | 0.1–14 m over a lap, mostly a constant offset |
| ENU projection, ellipsoidal | < 0.1 m | Over a few km |
| ENU projection, naive equirectangular | 0.4–2.5 m | Do not use |
| Lateral offset at a wide corner | up to half the track width | Projection maps all lines to one `s` |

**What this means for a published ordering.** Two cars whose crossing times at
a corner differ by less than roughly one interpolation interval are **not
distinguishable** by this method. At 5 Hz with monotone interpolation, the
practical resolution on crossing time is of order **50–100 ms**; below that, the
order shown is the order of the interpolant, not a measurement.

**So the site does not render a hard ordering below its own resolution.** Where
two cars are within the uncertainty band, they are drawn as a contested pair —
a shared marker, or both labels on one row — and the caption says so. This is
the same honesty discipline as the [honest absence](../../SPEC.md) principle,
applied to precision rather than to coverage.

**The lateral collapse is the other structural limit.** Projection maps a car
on the inside line and a car on the outside line at the same `s` to the same
along-track distance, even though one may be a full car-width ahead in the
direction of travel. At a wide, fast corner this is a real ambiguity and no
amount of interpolation resolves it — it is a limitation of the one-dimensional
model, and `e` (the lateral offset from step 2) is the field that exposes it.

## Payload

Position data is the heaviest thing the site ships. Measured, for one race of
20-car position data:

| Encoding | Size |
| --- | ---: |
| 5 Hz, int16 delta-encoded, planar, gzipped | **1.31 MB** (~65 KB/car) |
| 2 Hz, same | **623 KB** |
| float32, naive | gzips only ~6% — unusable |

The decision: **2 Hz for the default replay, 5 Hz fetched on demand** when the
reader opens corner-level analysis. Delta-encoding and planar layout (all X,
then all Y) are what make gzip work at all; naive float32 is effectively
incompressible because the low mantissa bits are noise.

GitHub Pages serves **gzip only, never brotli**, so `.br` siblings are dead
weight against the 1 GB cap.

## Coverage

**Telemetry tier and above — 2018 onward.** Roughly 85% of race pages have no
position data at all, and those pages do not carry a corner-order panel, a
degraded version of one, or a placeholder.

Within the telemetry era, coverage is still per-race: dropouts in the position
stream are normal, and a lap with a gap spanning the corner of interest has no
answer for that corner. The panel says which laps it could not resolve.

## Related

- [Gap to leader](gap-to-leader.md) — finish-line order, from which this metric
  is the sub-lap generalisation.
- [Overtake detection](overtake-detection.md) — the "maintained to the lap's
  finish line" clause of the published definition becomes checkable once
  sub-lap order exists.
- [Clean-air race pace](clean-air-race-pace.md) — shares the
  `DistanceToDriverAhead` machinery for traffic detection.
- [Race trace](race-trace.md) — the lap-resolution view of the same ordering.
