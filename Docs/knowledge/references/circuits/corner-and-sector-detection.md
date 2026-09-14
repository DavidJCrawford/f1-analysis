---
type: Reference
title: Corner and Sector Detection
description: How corners, marshal sectors, timing sector lines, mini-sectors and DRS zones are located on a circuit centreline, and which of them are actually available per circuit.
resource: https://docs.fastf1.dev/circuit_info.html
tags:
  - corners
  - sectors
  - mini-sectors
  - drs
  - curvature
  - fastf1
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_circuit_info
    resource: https://docs.fastf1.dev/circuit_info.html
    title: FastF1 — Circuit Information
  - id: fastf1_mvapi_data
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/mvapi/data.py
    title: FastF1 mvapi/data.py — CircuitInfo and add_marker_distance
  - id: fastf1_api_py
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
    title: FastF1 _api.py — car_data() DRS channel docstring
  - id: mv_spa
    resource: https://api.multiviewer.app/api/v1/circuits/7/2024
    title: MultiViewer circuit payload, circuitKey 7 (Spa)
  - id: openf1_laps
    resource: https://api.openf1.org/v1/laps?session_key=9574&driver_number=4&lap_number=10
    title: OpenF1 /v1/laps — Spa 2024 segment arrays
  - id: openf1_docs
    resource: https://openf1.org/docs
    title: OpenF1 API documentation
status: stable
---

# Corner and Sector Detection

Four different things get called "sectors" in F1 data, and they are not
interchangeable:

| Thing | Count | Source | Positions available? |
| --- | ---: | --- | --- |
| **Timing sectors** | 3 | FastF1 `Sector{1,2,3}SessionTime` | only as times — must be converted |
| **Mini-sectors** (timing segments) | 21–28, per circuit | OpenF1 `segments_sector_*` lengths; MultiViewer `miniSectorsIndexes` | on ~half of circuits |
| **Marshal sectors** | 16 at Silverstone | `CircuitInfo.marshal_sectors` | yes, as X/Y |
| **Corners** | 18 at Silverstone | `CircuitInfo.corners` | yes, as X/Y + cumulative distance |

Conflating marshal sectors with timing mini-sectors is the common error. They
are different partitions with different counts serving different purposes
(flag control versus timing segments).

## 1. `Session.get_circuit_info()`

```python
@dataclass
class CircuitInfo:
    corners: pd.DataFrame
    marshal_lights: pd.DataFrame
    marshal_sectors: pd.DataFrame
    rotation: float
```

All three DataFrames share the same columns:

| Column | Type | Meaning |
| --- | --- | --- |
| `X`, `Y` | float | Position in the 1/10 m frame (see [Coordinate systems](coordinate-systems.md)) |
| `Number` | int | Corner / light / sector number |
| `Letter` | str | Optional suffix, e.g. the `A` in corner "2A" |
| `Angle` | float | Degrees; used to offset a marker outward, usually roughly orthogonal to the track |
| `Distance` | float | Metres from the start/finish line — **NaN unless telemetry is loaded** |

Signature: `fastf1.mvapi.get_circuit_info(*, year: int, circuit_key: int) -> CircuitInfo | None`.

FastF1's own caveat, verbatim: "This data has been manually created and is not
highly accurate but sufficient for visualization."

### `Distance` is lazy, and it does not have to be

`Distance` is set to `np.nan` at parse time and filled by
`CircuitInfo.add_marker_distance(reference_lap)`, which is a nearest-point
match, not an arc-length integral:

```python
tel = reference_lap.get_telemetry(frequency="original")
tel = tel[tel["Source"] == "pos"]
xy_ref = tel.loc[:, ("X", "Y")].to_numpy()
diff    = markers[:, None, :] - xy_ref[None, :, :]
e       = diff[..., 0] ** 2 + diff[..., 1] ** 2
indices = np.nanargmin(e, axis=1)
distance = tel.iloc[indices]["Distance"].to_numpy()
```

That requires a full session download. **The upstream API already carries the
answer.** Each corner object is

```json
{"angle": 98.4899241531774, "length": 4523.666100769043,
 "number": 1, "trackPosition": {"x": 1192.508, "y": 4503.826}}
```

`length` is cumulative distance from the start/finish line in 1/10 m. Silverstone
corner 1 (Abbey) = 4523.67 → **452.4 m**; corner 18 = 56799.17 → **5679.9 m**
against a 5891 m lap. FastF1 reads only `x`, `y`, `number`, `letter` and
`angle`, discards `length`, and then recomputes it from telemetry.

`trackPosition` is confirmed to be in the same 1/10 m frame as the centreline:
Silverstone corner X spans −2309…7776 against a centreline X span of
−2313…7788.

For a static site build this is a significant simplification — corner distances
with no session load and no telemetry download. It is gated on the licensing
question in [spec §13.3](../../../SPEC.md); the fallback is `add_marker_distance`
against our own centreline, reimplemented with the code above.

### Marker placement

FastF1's example offsets a corner label outward by rotating a fixed vector by
the corner's own `Angle`:

```python
offset_vector = [500, 0]                      # 50 m in real units
offset_angle  = corner['Angle'] / 180 * np.pi
offset_x, offset_y = rotate(offset_vector, angle=offset_angle)
text_x = corner['X'] + offset_x
text_y = corner['Y'] + offset_y
```

50 m is "chosen to look good", not derived. For a typographic layout at our
scale, treat it as a starting value and collision-resolve against the ribbon
outline rather than trusting it.

## 2. Timing sector lines

### Method A — geometric, where it exists

MultiViewer's `miniSectorsIndexes` is a list of indices into the centreline
`x[]`/`y[]` arrays. OpenF1's `/v1/laps` returns `segments_sector_1/2/3`, whose
**lengths** give the per-sector mini-sector counts. Combining them:

```python
s1, s2, s3 = (len(lap["segments_sector_1"]),
              len(lap["segments_sector_2"]),
              len(lap["segments_sector_3"]))
sector1_end_index = mini_sectors[s1 - 1]
sector2_end_index = mini_sectors[s1 + s2 - 1]
```

Worked at Spa 2024 (`session_key=9574`, driver 4, lap 10: 8 + 12 + 7 = 27
segments; `miniSectorsIndexes` has 27 entries):

```
[40,100,138,168,192,219,246,284,311,349,379,413,450,484,521,553,
 586,625,661,703,749,770,798,831,866,954,1004]
```

| Boundary | Index | Arc length on the 6961.7 m centreline | Fraction | Lands at |
| --- | ---: | ---: | ---: | --- |
| S1 / S2 | 284 | 2242.9 m | 32.2% | just past Les Combes/Malmedy |
| S2 / S3 | 703 | 5057.6 m | 72.6% | Stavelot–Blanchimont |
| Lap end | 1004 | 6961.7 m | 100% | start/finish |

Both land where Spa's real sector lines are. The lap's own sector durations
agree in shape: 31.0 s / 50.007 s / 29.327 s against a 110.334 s lap.

### This method does not generalise

**`miniSectorsIndexes` is absent on roughly half the calendar.** Surveyed
across 18 circuit keys:

| Present | Mini-sector count |
| --- | ---: |
| Austin (9) | 21 |
| Melbourne (10) | 22 |
| Zandvoort (55) | 23 |
| Yas Marina (70) | 23 |
| Jeddah (149) | 24 |
| Monza (39) | 25 |
| Spa (7) | 27 |
| Sakhir (63) | 28 |

**Absent** — these return `trackPositionTime` instead: Silverstone (2),
Imola (6), Interlagos (14), Catalunya (15), Spielberg (19), Monte Carlo (22),
Montreal (23), Suzuka (46), Singapore (61), Miami (151).

Two consequences. The count is **per-circuit, in the range 21–28**; there is no
universal 27. And because the field is missing at Silverstone, Monaco, Suzuka
and Singapore — four of the eight hero circuits named in
[spec §9.1](../../../SPEC.md) — Method A cannot be the general recipe.

**Unverified:** that MultiViewer index *k* corresponds positionally to OpenF1
segment *k*. The count agreement at Spa is suggestive; neither API asserts the
correspondence, and it has not been tested at a circuit where the two disagree.
Treat Method A's output as an aid to placing sector lines, corroborated against
Method B, not as an authority on its own.

### Method B — temporal, always available

`Session.laps` carries `Sector1SessionTime`, `Sector2SessionTime`,
`Sector3SessionTime` (`timedelta64[ns]`) alongside `Sector1Time`/`2`/`3`.
Interpolate the lap's merged telemetry `Distance` at each session time:

```python
tel = lap.get_telemetry()          # merged, interpolated
t   = tel["SessionTime"].dt.total_seconds().to_numpy()
d   = tel["Distance"].to_numpy()
s1_distance = np.interp(lap["Sector1SessionTime"].total_seconds(), t, d)
s2_distance = np.interp(lap["Sector2SessionTime"].total_seconds(), t, d)
```

This is the site's primary method. Run it over every clean lap of a session and
take the **median** boundary distance: a single lap's crossing is quantised by
the ~240 ms sample interval, which at 250 km/h is **~17 m of distance
uncertainty**. Fifty laps reduce that to noise.

### Mini-sector segment status codes

`segments_sector_*` values, **medium confidence** — community-derived from
OpenF1's documentation, not specified:

| Value | Meaning |
| ---: | --- |
| 2048 | yellow |
| 2049 | green |
| 2051 | purple |
| 2064 | pitlane |
| 2068 | unknown |

Only 2048 and 2049 appeared in the race lap tested. OpenF1 itself notes that
segments are largely unavailable during races and may not match the TV colours.
The mini-sector dominance chart in [spec §10](../../../SPEC.md) therefore
derives dominance from telemetry within our own segment boundaries rather than
from these codes.

## 3. DRS zones

**No public geometry exists for DRS zones.** They must be derived empirically.

DRS channel values, verbatim from `fastf1/_api.py`:

```
- DRS (int): 0-14 (Odd DRS is Disabled, Even DRS is Enabled?)
  (More Research Needed?)
  - 0 =  Off
  - 1 =  Off
  - 2 =  (?)
  - 3 =  (?)
  - 8 =  Detected, Eligible once in Activation Zone (Noted Sometimes)
  - 10 = On (Unknown Distinction)
  - 12 = On (Unknown Distinction)
  - 14 = On (Unknown Distinction)
```

OpenF1's documentation gives the same table (0, 1 off; 8 detected/eligible;
10, 12, 14 on; 2, 3, 9 unknown). The distinction between 10, 12 and 14 is
**unverified** — FastF1's own docstring says "More Research Needed?".

In FastF1, `DRS` is declared discrete (`"DRS": {"type": "discrete"}` in
`core.py`), so channel merging forward-fills rather than interpolating. That is
the correct behaviour for a state flag and means a merged telemetry frame can be
used directly.

### Derivation, run end to end

Validated on Spa 2024 (`session_key=9574`, driver 4, 13:20–13:30 UTC) against
the raw OpenF1 endpoints:

1. `GET /v1/car_data?session_key=…&driver_number=…&date>…&date<…` → 2236 samples.
2. `GET /v1/location` with the same filters → 2307 samples.
3. Drop location rows where `x == 0 and y == 0` (dropouts).
4. Sort both by parsed `date`; for each car-data row, bisect into the location
   timestamps and accept the match only if `|Δt| ≤ 0.3 s`.
5. `drs ∈ {10, 12, 14}` → **open**.

Result: 80 open samples, 2013 closed. Distinct open values observed: 10 and 14.
Max speed with DRS open: 340 km/h. The open samples formed a single coherent
spatial cluster, bbox x −183…787 m, y −984…342 m.

URL-encode the comparison operators: `date%3E` and `date%3C`.

### Turning samples into a publishable zone

Run the above over **all drivers and all racing laps of a dry race**, project
every open sample onto the centreline to get `Distance`, histogram over
distance at ~10 m bins, and take contiguous runs where the open fraction
exceeds ~0.2.

- The **zone start** is the activation line. It has a sharp leading edge
  because the rules make it one, and it is authoritative.
- The **zone end** is where drivers lift, not a line. It is approximate and
  must be rendered and captioned as approximate.
- **Detection points cannot be derived at all.** The `8` value is sparse and
  unreliable. Detection points are published only in per-race FIA Event Notes
  PDFs and would have to be transcribed by hand. Until they are, the site shows
  activation zones and says nothing about detection.

Secondary signal: `Session.race_control_messages` has `Category == "Drs"` with
`DRS ENABLED` / `DRS DISABLED` messages. That tells you **when** DRS was live,
not where — useful for annotating a race trace, useless for geometry.

## 4. Curvature-based corner detection

The fallback where no corner table exists — pre-2018 layouts, circuits absent
from the MultiViewer index, and any layout changed since its frozen snapshot.

```python
def signed_curvature(P):
    """P: (n, 2) resampled closed centreline. Returns kappa per station."""
    A, B, C = np.roll(P, 1, axis=0), P, np.roll(P, -1, axis=0)
    ab, bc, ac = B - A, C - B, C - A
    cross = ab[:, 0] * bc[:, 1] - ab[:, 1] * bc[:, 0]
    denom = (np.linalg.norm(ab, axis=1) *
             np.linalg.norm(bc, axis=1) *
             np.linalg.norm(ac, axis=1))
    return 2.0 * cross / denom
```

Pipeline:

1. Resample to constant Δs (2 m) — see
   [Centreline construction](centreline-construction.md) §3. On time-uniform
   samples the denominator collapses in slow corners and κ is noise.
2. Smooth κ with a wrapping Gaussian, σ ≈ 3 stations.
3. Mark stations where `|κ| > 1/300` (radius under 300 m) as cornering.
4. Group contiguous runs of the same sign; discard runs shorter than ~15 m.
5. The **apex** is the station of maximum `|κ|` within the run; corner entry
   and exit are the run boundaries.
6. Merge runs separated by under ~25 m of straight — this is what keeps
   Maggotts–Becketts from fragmenting into six "corners".

This reproduces the corner *count* well and the official *numbering* poorly:
the FIA's numbering is a convention, not a geometric fact (Silverstone's Abbey
and Farm are numbered separately; Spa's Eau Rouge and Raidillon are one number
or two depending on who is asking). **Derived corners are labelled by distance,
never by an invented corner number.** Where an official numbering exists it comes
from the corner table and is carried in the registry; where it does not, the
page says the corners are geometric.
