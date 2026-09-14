---
type: Reference
title: Circuit Identifier Crosswalk
description: How circuit identifiers map across F1DB, FastF1, OpenF1, MultiViewer and the open geometry repositories — and why the layout, not the circuit, is the key that actually has to resolve.
tags: [circuits, layouts, joins, geometry, crosswalk, registry]
resource: https://github.com/f1db/f1db
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_csv
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 CSV bundle — circuits and circuit layouts
  - id: mvapi_sakhir
    resource: https://api.multiviewer.app/api/v1/circuits/63/2025
    title: MultiViewer circuit payload for circuit_key 63 (Sakhir)
  - id: fastf1_circuitinfo
    resource: https://docs.fastf1.dev/circuit_info.html
    title: FastF1 CircuitInfo reference
  - id: openf1_meetings_2026
    resource: https://api.openf1.org/v1/meetings?year=2026
    title: OpenF1 meetings for 2026 (circuit_key, circuit_short_name)
  - id: f1db_svg
    resource: https://raw.githubusercontent.com/f1db/f1db/main/src/assets/circuits/black/monza-1.svg
    title: F1DB per-layout circuit SVG asset (git repo only)
status: stable
---

# Circuit Identifier Crosswalk

Circuits are the hard case, and nobody's default handles them. Drivers and teams share
an Ergast-descended slug space that mostly joins
([drivers-and-teams](drivers-and-teams.md)); circuits do not. Four sources use four
incompatible key types, the best geometry source has no layout discriminator at all,
and the entity everyone actually means — a specific configuration of tarmac, in a
specific period — exists in exactly one of them.

## 1. The key spaces

| Source | Key | Type | Example | Layout-aware? |
| --- | --- | --- | --- | --- |
| **F1DB** `f1db-circuits.csv` | `id` | slug | `monza`, `silverstone`, `sepang`, `madring`, `catalunya` | no (78 rows) |
| **F1DB** `f1db-circuits-layouts.csv` | `id` | slug-`n` | `monza-1`, `silverstone-3`, `silverstone-8` | **yes** (160 rows) |
| **F1DB** `f1db-races.csv` | `circuitId` + `circuitLayoutId` | slug pair | — | **yes** |
| **MultiViewer** | `circuitKey` | int | `63` = Sakhir | no |
| **OpenF1** | `circuit_key` + `circuit_short_name` | int + string | `63` / `Sakhir`; `153` / `Madring` | no |
| **FastF1** `session_info` | circuit key | int | `63` | no |
| **bacinger/f1-circuits** | `cc-year` slug | slug | country-code plus year, 40 circuits | partially, by accident |
| **TUMFTM/racetrack-database** | track name | string | 25 tracks, ~19 of them F1 | no |

`circuit_key` is consistent across MultiViewer, OpenF1 and FastF1 — **63 is Sakhir in
all three** — which is the only reason a geometry join is possible at all. That
consistency is observed rather than documented by any of the three, so it is a probe in
the test suite, not an assumption.

Nothing in that table joins to F1DB. The int-keyed sources carry no slug and the
slug-keyed source carries no int. The bridge is built by hand.

## 2. Layout is the real key

`f1db-circuits-layouts.csv` has header `id,circuitId,effective,length,turns` and 160
data rows against 78 circuits. `effective` is the date the configuration came into
use. `f1db-races.csv` carries both `circuitId` and `circuitLayoutId` per race, so F1DB
already answers "which configuration did this race run on" — and it is the only source
that does.

This matters because circuits are relaid. Silverstone, Bahrain, Yas Marina, Zandvoort,
Albert Park, Spa, Suzuka and Hockenheim have all changed configuration, some more than
once. **A circuit is an entity with a version history**
([SPEC §6.3](../../../SPEC.md)), and picking one layout per circuit silently
misattributes lap records and geometry — which is the specific failure the site is
least able to survive, because a lap record is exactly the kind of number a reader will
check.

The site's route structure follows the data: `/circuits/monza/` for the entity,
`/circuits/monza/layouts/monza-1/` for a configuration
([SPEC §5.1](../../../SPEC.md)).

### What the layout table does not contain

No geometry. The header is the whole file — `id`, `circuitId`, `effective`, `length`,
`turns`. F1DB tells you *that* a layout exists and when; it never tells you what shape
it is. Geometry comes from elsewhere and must be bound to the layout by hand.

## 3. MultiViewer: best geometry, no layout key, ignores the year

The MultiViewer payload for `circuit_key` 63 (14,684 bytes) carries:

| Field | Content |
| --- | --- |
| `x`, `y` | parallel arrays of **730 integers** — the centreline polyline |
| `rotation` | `92` degrees, to align with the official track-map orientation |
| `corners` | 15 objects, each `{angle, length, number, trackPosition:{x,y}}` |
| `marshalLights`, `marshalSectors` | 18 objects each, same shape |
| `miniSectorsIndexes` | 28 ints indexing into `x`/`y` |
| `pitLoss` | `{normal: "23.96", sc: "15.18", vsc: "17.33"}` seconds |
| `candidateLap` | the reference lap the geometry was derived from |
| identity | `circuitKey`, `circuitName`, `countryIocCode`, `countryKey`, `countryName`, `location`, `meetingKey`, `meetingName`, `meetingOfficialName`, `raceDate`, `round`, `year` |

There is **no elevation** in the payload and **no layout identifier**.

The route is `/api/v1/circuits/{circuit_key}/{year}` and the year is not honoured.
Requesting `/circuits/63/2025` returns a body stamped `"year": 2022`, with
`candidateLap` `{driverNumber: '1', lapNumber: 3, lapStartDate: '2022-03-18T12:05:19.921000',
session: 'FP1', lapTime: 97.766}`. The geometry served is whatever reference lap
MultiViewer last captured, not the configuration that ran in the year you asked for.

Three consequences:

1. **Cache by circuit key, never by season.** A per-season cache key produces
   identical payloads under different names.
2. **MultiViewer cannot resolve layout versions.** Layout change is something the
   pipeline detects; the API will not tell you.
3. `miniSectorsIndexes` is **absent on roughly half of circuits** — including
   Silverstone, Monaco, Suzuka, Singapore, Miami, Imola, Montreal, Spielberg,
   Catalunya and Interlagos — so it cannot be the general recipe for sector
   boundaries ([SPEC §13.3](../../../SPEC.md)).

MultiViewer publishes no terms of use and is **blocked pending contact**
([SPEC §13.3](../../../SPEC.md)). It is documented here because the crosswalk has to
be designed for the world in which permission is granted and the world in which it is
not; the fallback stack is bacinger + TUMFTM + telemetry-derived centrelines, which
changes which sources the registry binds but not the shape of the registry.

### FastF1's sanctioned subset

`Session.get_circuit_info()` returns a `CircuitInfo` exposing `corners`,
`marshal_lights` and `marshal_sectors` as DataFrames with columns
`X, Y, Number, Letter, Angle, Distance` (`Distance` requires telemetry loaded), plus a
float `rotation`. **The `x`/`y` polyline is not exposed**, which is why the raw JSON is
worth fetching directly — and why a project that cannot use MultiViewer loses the
centreline but keeps the corner annotations.

## 4. Name traps

Never derive a circuit from a race name, or a country from a meeting name. 2026 makes
the point three times over:

| OpenF1 `meeting_key` | `meeting_name` | `location` | `country_name` | `circuit_short_name` | F1DB |
| ---: | --- | --- | --- | --- | --- |
| 1287 | Barcelona Grand Prix | Barcelona | Spain | Catalunya | round 7 · `grandPrixId=barcelona-catalunya` · `circuitId=catalunya` |
| 1294 | Spanish Grand Prix | **Madrid** | Spain | **Madring** | round 14 · `grandPrixId=spain` · `circuitId=madring` |
| 1308 | **Bahrain** Grand Prix | **Kuala Lumpur** | **Bahrain** | Kuala Lumpur | round 16 · 2026-10-04 · `grandPrixId=bahrain` · `circuitId=sepang` |

Meeting 1308 is named for Bahrain, attributed to country Bahrain, and physically held
at Sepang in Malaysia. F1DB's `officialName` for it reads "Formula 1 Gulf Air Bahrain
Grand Prix in Malaysia 2026". OpenF1's `circuit_short_name` is "Kuala Lumpur"; F1DB's
`circuitId` is `sepang`. **A crosswalk keyed on names would resolve this row three
different ways and be wrong at least twice.**

The FIA's own `SessionInfo.json` for the Madrid race agrees with none of the informal
readings and is itself worth quoting as the join anchor:

```json
{"Meeting":{"Key":1294,"Name":"Spanish Grand Prix",
  "OfficialName":"FORMULA 1 TAG HEUER GRAN PREMIO DE ESPAÑA 2026",
  "Location":"Madrid","Number":14,
  "Country":{"Key":1,"Code":"ESP","Name":"Spain"},
  "Circuit":{"Key":153,"ShortName":"Madring"}}}
```

`Circuit.Key` 153 is the integer that joins to OpenF1 `circuit_key` and to MultiViewer
`circuitKey`. `ShortName` is a label.

## 5. `circuit-layout-registry.json`

The registry is the project's answer, named in [SPEC §6.3](../../../SPEC.md) as a
first-class build artifact: hand-verified once per layout, regression-tested, and the
only place geometry is bound to identity.

One row per F1DB `circuitLayoutId`:

| Field | Source | Notes |
| --- | --- | --- |
| `layout_id` | F1DB `f1db-circuits-layouts.csv` `id` | primary key, e.g. `monza-1` |
| `circuit_id` | F1DB | e.g. `monza` |
| `effective` | F1DB | date the configuration came in |
| `declared_length_m`, `turns` | F1DB | the figures the site quotes |
| `circuit_key` | observed, shared by MultiViewer / OpenF1 / FastF1 | int; null for circuits that never ran in the int-keyed era |
| `svg_assets` | F1DB git repo | four style variants, see §6 |
| `geometry_source` | registry decision | which of bacinger / TUMFTM / telemetry-derived / MultiViewer supplies the centreline |
| `geometry_ref` | that source's own key | e.g. a bacinger `cc-year` slug or a TUMFTM track name |
| `three_d_tier` | registry decision | `hero` / `standard` / `outline` ([SPEC §9.1](../../../SPEC.md)) |
| `verified_by`, `verified_at` | human | the registry is the one hand-checked artifact; it carries its own provenance |

The registry is populated for all ~160 layouts, but `geometry_source` is null for most
of them — only about 40 circuits have any open centreline at all (bacinger 40, TUMFTM
~19 F1 tracks, overlapping), which is the data-side reason the 3D tiering in
[SPEC §9.1](../../../SPEC.md) lands where it does. A layout with no geometry gets the
outline tier and designed copy saying so, not an empty canvas.

## 6. SVG assets: in the repo, not in the release

F1DB ships per-layout circuit diagrams in four styles at

```
src/assets/circuits/{black,black-outline,white,white-outline}/<layoutId>.svg
```

for example
`https://raw.githubusercontent.com/f1db/f1db/main/src/assets/circuits/black/monza-1.svg`.

**They are not in the release zips.** The v2026.14.0 release has 13 assets — a
checksums file plus CSV, JSON, Smile, SQLite and SQL bundles — and no SVG archive;
`f1db-svg.zip` returns HTTP 404. A pipeline that downloads release artifacts gets
zero diagrams and must sparse-checkout the repo or raw-fetch per layout id.

The filename *is* the layout id, which makes this the one place where the crosswalk is
free: if `circuitLayoutId` resolves, the asset path resolves.

Since the site ships without photography ([SPEC §13.6](../../../SPEC.md)), these
diagrams plus typography plus the 3D renders are the visual material for every circuit
page. They are CC BY 4.0, so they are redistributable.

## 7. Open geometry sources and what binds them

| Source | Coverage | Licence | Key | Role |
| --- | --- | --- | --- | --- |
| bacinger/f1-circuits | 40 circuits | MIT | `cc-year` slug | Redistributable outlines |
| TUMFTM/racetrack-database | 25 tracks, ~19 F1 | **LGPL-3.0** | track name | Centreline + width, build-time; obligations tracked |
| FastF1 position telemetry | 2018+ sessions | MIT tool, F1 archive data | session | Elevation and telemetry-derived centrelines |
| Copernicus GLO-30 DEM | global | free, attribution | tile path | Distant terrain only |

bacinger is **not** OpenStreetMap-derived — its README names Google My Maps tracing
plus Wikipedia. That removes the ODbL share-alike concern and replaces it with a
Google Maps terms question, and it means the "OSM-derived" provenance story cannot be
told ([SPEC §6.1](../../../SPEC.md)).

Its accuracy is good enough to be useful as a check on the resolution itself. Measured
length against declared length:

| Circuit | Error |
| --- | ---: |
| Monza | −0.002% |
| Silverstone | −0.113% |
| Spa | −0.255% |
| Monaco | −0.27% |

Which gives a cheap regression test: **for every layout with bound geometry, the
measured centreline length must agree with F1DB's declared `length` to within a stated
tolerance.** A resolution error that binds the wrong layout to a circuit will usually
blow that tolerance, because relayed configurations change length. This is the single
highest-value automated guard on the registry.

Copernicus tile paths are deterministic in *form* but not in *availability* — some
tiles are withheld, and at least one F1 venue (Baku) returns 404. Handle the 404. It
is a surface model at <4 m LE90, so it is for distant terrain only, never the track
surface ([SPEC §9.3](../../../SPEC.md)).

## 8. Coordinates

Two unit traps sit immediately downstream of a successful circuit join, both recorded
in [SPEC §9.3](../../../SPEC.md) and repeated here because they are where a correct
join still produces a wrong track:

- FastF1 position `X`/`Y`/`Z` are in **1/10 metre from 2020 onward**. The unit has a
  date cutoff.
- For local ENU ↔ WGS84, using the equatorial radius `a = 6378137` on both axes gives
  0.4–2.5 m of systematic scale error at F1 latitudes. Use the ellipsoidal radii
  `k_east = N(φ₀)·cos(φ₀)` and `k_north = M(φ₀)`, which brings residual below 0.1 m
  over a few km.

MultiViewer `x`/`y` are integers in their own arbitrary frame with a `rotation` to
align them to the official map; they are not metres and not geographic.

## 9. Probes

| Probe | Expected |
| --- | --- |
| `circuit_key` 63 | `sakhir` in F1DB; `Sakhir` as OpenF1 `circuit_short_name`; same key in FastF1 `session_info` |
| `circuit_key` 153 | `madring`; OpenF1 `circuit_short_name` `Madring` |
| F1DB 2026 round 16 | `grandPrixId=bahrain`, `circuitId=sepang`, date 2026-10-04 |
| F1DB 2026 round 7 vs 14 | two distinct Spanish rounds, `catalunya` and `madring` |
| Every F1DB race row | resolves to exactly one `circuitLayoutId` present in the registry |
| Every registry row with geometry | measured length within tolerance of declared `length` |
| Every registry row | its four SVG style paths return 200 |

The last one is worth running on a schedule rather than only in CI: the SVGs live on
`main` in a repository that releases weekly, and a renamed layout id is a broken image
on a page that has no photography to fall back on.
