---
type: Dataset
title: MultiViewer Circuit API
description: The undocumented endpoint behind FastF1's get_circuit_info() — the best available F1 track centreline, corner distances and pit-loss times, blocked from use on this site until terms are agreed.
resource: https://api.multiviewer.app/api/v1/circuits
tags: [multiviewer, circuit-info, centreline, corners, pit-loss, blocked, undocumented-api]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: mvapi_source
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/mvapi/api.py
    title: fastf1/mvapi/api.py — endpoint, host and headers
  - id: mvapi_data_source
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/mvapi/data.py
    title: fastf1/mvapi/data.py — CircuitInfo dataclass and JSON parsing
  - id: mv_silverstone
    resource: https://api.multiviewer.app/api/v1/circuits/2/2024
    title: MultiViewer circuit payload, circuitKey 2 (Silverstone)
  - id: mv_sakhir
    resource: https://api.multiviewer.app/api/v1/circuits/63/2025
    title: MultiViewer circuit payload, circuitKey 63 (Sakhir)
  - id: mv_index
    resource: https://api.multiviewer.app/api/v1/circuits
    title: MultiViewer circuit index
  - id: fastf1_circuit_info
    resource: https://docs.fastf1.dev/circuit_info.html
    title: FastF1 CircuitInfo documentation
status: stable
---

# MultiViewer Circuit API

**Status: BLOCKED pending terms.** MultiViewer publishes no terms of use, no rate
limits and no API documentation. Its geometry is genuinely the best available for an F1
track, and shipping it without permission is not acceptable. SPEC §13.3 records this as
a gating item: *contact the maintainers; blocked until resolved.* This document exists
so that the decision, when it comes, is made against real facts — and so the fallback
(see [circuit geometry sources](circuit-geometry-sources.md)) is scoped correctly if
the answer is no.

| Fact | Value |
| --- | --- |
| Endpoint | `GET https://api.multiviewer.app/api/v1/circuits/{circuitKey}/{year}` |
| Index | `GET https://api.multiviewer.app/api/v1/circuits` |
| Auth | None; a User-Agent header is expected — FastF1 sends `FastF1/{version}` |
| Used by | `fastf1.mvapi.get_circuit_info(*, year, circuit_key)`, i.e. `Session.get_circuit_info()` |
| Terms | **None published** |

FastF1's constants: `PROTO = "https"`, `HOST = "api.multiviewer.app"`,
`HEADERS = {"User-Agent": f"FastF1/{__version_short__}"}`.

## The full payload

Top-level keys for circuitKey 2 (Silverstone): `pitLoss`, `corners`, `marshalLights`,
`marshalSectors`, `candidateLap`, `circuitKey`, `circuitName`, `countryIocCode`,
`countryKey`, `countryName`, `location`, `meetingKey`, `meetingName`,
`meetingOfficialName`, `raceDate`, `rotation`, `round`, `trackPositionTime`, `x`, `y`,
`year`. Circuits that carry mini-sector data substitute `miniSectorsIndexes` for
`trackPositionTime`.

### What FastF1 surfaces

`Session.get_circuit_info()` returns exactly this dataclass:

```python
@dataclass
class CircuitInfo:
    corners: pd.DataFrame
    marshal_lights: pd.DataFrame
    marshal_sectors: pd.DataFrame
    rotation: float
```

All three DataFrames share the columns `X` (float), `Y` (float), `Number` (int),
`Letter` (str), `Angle` (float), `Distance` (float). `Distance` is **NaN unless
telemetry is loaded** — it is computed lazily by
`CircuitInfo.add_marker_distance(reference_lap)` as a nearest-point match, not an
arc-length integral:

```python
tel = reference_lap.get_telemetry(frequency="original")
tel = tel[tel["Source"] == "pos"]
xy_ref = tel.loc[:, ("X", "Y")].to_numpy()
e = diff[..., 0] ** 2 + diff[..., 1] ** 2
indices = np.nanargmin(e, axis=1)
distance = tel.iloc[indices]["Distance"]
```

FastF1's own caveat, verbatim: *"This data has been manually created and is not highly
accurate but sufficient for visualization. A big thanks to MultiViewer
(https://multiviewer.app/) for providing this data to FastF1."*

### What FastF1 discards — the valuable half

| Field | Content |
| --- | --- |
| `x[]` / `y[]` | The **full track centreline polyline**, parallel integer arrays, in the same 1/10 m frame as position telemetry. Silverstone 916 points, Spa 1005, Sakhir 730 |
| `corners[].length` | Cumulative distance from the start/finish line in 1/10 m. Silverstone corner 1 = 4523.67 → **452.4 m** (Abbey); corner 18 = 56799.17 → 5679.9 m against a 5891 m lap |
| `miniSectorsIndexes` | Integer indices into `x[]`/`y[]` marking timing mini-sector boundaries — present on roughly half of circuits |
| `pitLoss` | `{normal, sc, vsc}` in seconds |
| `candidateLap` | The reference lap the geometry was derived from: `{driverNumber, lapNumber, lapStartDate, lapStartSessionTime, lapTime, session, sessionStartTime}` |

`corners[].length` deserves emphasis: it gives corner-by-corner distance along the lap
**with no telemetry load and no session download**, which FastF1 throws away and then
laboriously recomputes by nearest-neighbour search. Corner `trackPosition` is in the
same 1/10 m frame as the centreline (Silverstone corner x range −2309…7776 against
centreline x range −2313…7788).

Corner/marshal objects are shaped
`{"angle": float, "length": float, "number": int, "trackPosition": {"x": float, "y": float}, "letter"?: str}`.
Silverstone corner 1 verbatim:

```json
{"angle": 98.4899241531774, "length": 4523.666100769043, "number": 1,
 "trackPosition": {"x": 1192.508, "y": 4503.826}}
```

### `pitLoss` — directly useful, and the reason the 30–60% rule of thumb fails

| Circuit | normal (s) | SC (s) | VSC (s) |
| --- | ---: | ---: | ---: |
| Silverstone | 20.93 | 13.26 | 15.14 |
| Spa | 19.07 | 12.08 | 13.80 |
| Imola | 28.01 | 17.75 | 20.26 |
| Sakhir | 23.96 | 15.18 | 17.33 |

These feed the pit-loss metric, where the site's position is that the SC/VSC saving is
circuit-specific and spans roughly 12–82% of green-flag loss, never a single global
figure (SPEC §7). If MultiViewer stays blocked, pit loss must be measured from lap data
instead.

## Hard limits nobody documents

### 1. The `year` path parameter is ignored

`/circuits/2/2024`, `/2025` and `/2026` return **byte-identical** Silverstone payloads
stamped `"year": 2022`, `raceDate` 2022-07-03. Spa (key 7) returns year 2021,
raceDate 2021-08-29 for every requested year. Monza (39) returns year 2021. Sakhir (63)
requested for 2025 returns a payload stamped 2022 with
`candidateLap = {"driverNumber": "1", "lapNumber": 3, "lapStartDate": "2022-03-18T12:05:19.921000", "session": "FP1", "lapTime": 97.766}`.

Because FastF1 passes the session year straight through, **a 2026 session silently
receives 2021/2022 geometry with no warning.** Any layout change or resurfacing since
2022 is invisible. Cache by `circuitKey`, never by season, and detect layout changes
yourself against [F1DB](f1db.md)'s `circuits-layouts.effective` dates.

### 2. Only 32 circuits, and no 2026 venues

The index returns a dict keyed by `circuitKey` with
`{name, country, years, circuitKey, countryKey, iocCountryCode, pitLoss}`. Observed
keys, with the vintage actually served:

| Key | Circuit | Year served |
| ---: | --- | ---: |
| 2 | Silverstone | 2022 |
| 4 | Hungaroring | 2021 |
| 6 | Imola | 2022 |
| 7 | Spa | 2021 |
| 9 | Austin | 2021 |
| 10 | Melbourne | 2022 |
| 14 | Interlagos | 2023 |
| 15 | Catalunya | 2023 |
| 19 | Spielberg | 2022 |
| 22 | Monte Carlo | 2022 |
| 23 | Montreal | 2022 |
| 28 | Paul Ricard | 2022 |
| 34 | Hockenheim | 2019 |
| 39 | Monza | 2021 |
| 46 | Suzuka | 2025 |
| 49 | Shanghai | 2019 |
| 55 | Zandvoort | 2021 |
| 59 | Istanbul | 2021 |
| 61 | Singapore | 2023 |
| 63 | Sakhir | 2022 |
| 65 | Mexico City | 2021 |
| 70 | Yas Marina | 2021 |
| 72 | Nürburgring | 2020 |
| 79 | Sochi | 2021 |
| 144 | Baku | 2022 |
| 146 | Mugello | 2020 |
| 147 | Algarve | 2021 |
| 148 | Sakhir Outer | 2020 |
| 149 | Jeddah | 2022 |
| 150 | Losail | 2023 |
| 151 | Miami | 2022 |
| 152 | Las Vegas | 2023 |

**Madrid / Madring is absent entirely** (keys 153–157 return nothing; 152 is Las
Vegas). Treat the whole index as a static 2019–2023-era snapshot, not a live feed.

### 3. Vertex spacing varies by a factor of ~3.5

| Circuit | Points | Approx. mean vertex spacing |
| --- | ---: | --- |
| Interlagos | 283 | ~15 m |
| Suzuka | 335 | ~17 m |
| Catalunya | 442 | |
| Singapore | 544 | |
| Melbourne | 618 | |
| Monte Carlo | 683 | |
| Sakhir | 730 | |
| Monza | 752 | |
| Miami | 757 | |
| Silverstone | 916 | ~6.4 m |
| Spa | 1005 | |

A 3D extrusion built directly on these vertices visibly facets at Interlagos and
Suzuka. **Resampling and splining are mandatory, not optional** — the centreline is a
control polygon, not a mesh-ready curve.

### 4. `miniSectorsIndexes` is absent on roughly half the calendar

Present, with per-circuit counts: Austin 21, Melbourne 22, Zandvoort 23, Yas Marina 23,
Jeddah 24, Monza 25, Spa 27, Sakhir 28. **Absent** on Silverstone, Imola, Interlagos,
Catalunya, Spielberg, Monte Carlo, Montreal, Suzuka, Singapore and Miami — those return
`trackPositionTime` instead.

So the mini-sector count is **per-circuit (21–28 observed), not a universal 27**, and
this cannot be the general recipe for sector boundaries. The Spa cross-check that makes
it look like one is real but narrow: OpenF1's `segments_sector_1/2/3` for Spa 2024 have
lengths 8 + 12 + 7 = 27, matching the 27-element `miniSectorsIndexes`, and converting
those indices to arc length along the 6961.7 m centreline puts index 284 at 2242.9 m
(32.2%, the S1/S2 line past Les Combes) and index 703 at 5057.6 m (72.6%, the S2/S3 line
in the Stavelot–Blanchimont region) — both where Spa's real sector lines are. But that
is a **count** match; positional correspondence between MultiViewer index *k* and
OpenF1 segment *k* is an untested inference, and nothing in either API asserts it.

The general method for sector boundaries is therefore the temporal one: FastF1's
`Sector1SessionTime` / `Sector2SessionTime` / `Sector3SessionTime`, interpolated against
the lap's telemetry `Distance`.

### 5. `rotation` is a display rotation, not north

`rotation` is read straight from the JSON as `float(data.get("rotation", 0.0))`, and
FastF1's docstring describes it as being "used to rotate the coordinate system of the
telemetry (position) data to match the orientation of the official track map."

Observed values — Silverstone 92, Spa 91, Monaco 315, Monza 95, Zandvoort 0 — bear no
relation to the near-zero rotation actually needed to align the raw XY frame to true
north. **Apply it for a stylised 2D map matching TV graphics; never for a georeferenced
3D scene, a map overlay, or anything joined to DEM data.**

## What is blocked, and what a "no" costs

| If MultiViewer is permitted | If not |
| --- | --- |
| ~730-point centreline in the telemetry frame, free | Centreline from [bacinger/f1-circuits](circuit-geometry-sources.md) (40 circuits) or median-aggregated telemetry |
| Corner numbers, angles and distances with no session load | Corner markers via FastF1 `CircuitInfo` — same upstream data, so equally blocked; otherwise hand-authored |
| Pit loss under green/SC/VSC per circuit | Measured from lap data per circuit |
| Mini-sector geometry on ~half the calendar | Temporal sector boundaries from FastF1 sector session times |

Note that FastF1's `CircuitInfo` is **not** an independent fallback — it is the same
API, fetched by a different client. A permission answer covers both.

Operational rules if it is ever unblocked: fetch once at build time, cache to disk
permanently, snapshot the result into the repository, never hotlink from a browser, and
send an identifying User-Agent.
