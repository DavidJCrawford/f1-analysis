---
type: Reference
title: Circuit Geometry Sources
description: Every usable source of F1 track outlines, centrelines, widths and SVG silhouettes — counts, licences, measured accuracy and provenance, with the gaps each one leaves.
tags: [circuits, geometry, geojson, svg, openstreetmap, licensing, 3d]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: bacinger
    resource: https://github.com/bacinger/f1-circuits
    title: bacinger/f1-circuits — F1 circuit GeoJSON
  - id: bacinger_silverstone
    resource: https://raw.githubusercontent.com/bacinger/f1-circuits/master/circuits/gb-1948.geojson
    title: bacinger/f1-circuits — gb-1948.geojson (schema sample)
  - id: tumftm
    resource: https://github.com/TUMFTM/racetrack-database
    title: TUMFTM/racetrack-database — centrelines and track widths
  - id: tumftm_readme
    resource: https://raw.githubusercontent.com/TUMFTM/racetrack-database/master/README.md
    title: TUMFTM/racetrack-database README — provenance and smoothing caveats
  - id: julesroy
    resource: https://github.com/julesr0y/f1-circuits-svg
    title: julesr0y/f1-circuits-svg — 78 circuits, all layout evolutions
  - id: osm_copyright
    resource: https://www.openstreetmap.org/copyright
    title: OpenStreetMap copyright and licence
  - id: osmf_produced_work
    resource: https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline
    title: OSMF Produced Work community guideline
  - id: taginfo_raceway
    resource: https://taginfo.openstreetmap.org/api/4/tag/stats?key=highway&value=raceway
    title: taginfo statistics for highway=raceway (data_until 2026-09-13)
status: stable
---

# Circuit Geometry Sources

Rendering a circuit in 3D needs four things: a **centreline**, a **width**, an
**elevation profile** and a **corner annotation**. No single source has all four, and
the best one for the centreline is [blocked](multiviewer-api.md). This document is the
inventory of what is actually available, what each source is licensed under, and how
accurate each one measured.

Elevation is handled separately — see [elevation and DEM sources](elevation-dem.md).

## Summary

| Source | Covers | Gives | Licence | Verdict |
| --- | --- | --- | --- | --- |
| [MultiViewer](multiviewer-api.md) | 32 circuits, 2019–2023 vintage | centreline, corners + distances, pit loss, some mini-sectors | **none published** | Best geometry; **blocked** |
| **bacinger/f1-circuits** | 40 circuits | closed outline LineStrings | MIT (but see provenance) | Primary fallback centreline |
| **TUMFTM/racetrack-database** | 25 tracks, ~19 F1 | centreline + **per-point width** | LGPL-3.0 (OSM underneath) | Only open width source; build-time width calibration |
| **F1DB circuit SVGs** | ~160 layouts | 2D silhouettes, 4 styles | CC BY 4.0 | Outline tier and thumbnails |
| **julesr0y/f1-circuits-svg** | 78 circuits, all layout evolutions | 2D silhouettes | CC BY 4.0 | Historic-layout silhouettes |
| **OpenStreetMap raceway** | global | raw ways | ODbL | Last resort; needs manual curation |
| FastF1 position telemetry | 2018+ sessions | one line + real Z | (F1 data) | Elevation and racing-line overlay |

## bacinger/f1-circuits

The primary redistributable outline source, and the geometry the site's 2D maps and
Standard-tier 3D ribbons are built from if MultiViewer stays blocked.

| Fact | Value |
| --- | --- |
| Circuits | **40** — `f1-circuits.geojson` contains exactly 40 features, all `LineString`, all closed (first coordinate equals last), and `circuits/` holds 40 files |
| Licence | MIT (`LICENSE.md`, © 2019–2025 Tomislav Bacinger) |
| Activity | 362 stars, last commit 2026-02-05T11:37:27Z |
| 2026 | `es-2026.geojson` present — Circuito de Madring, declared length 5474 m |

Files: `f1-circuits.geojson` (all circuits in one FeatureCollection),
`circuits/{cc}-{year}.geojson` (one per circuit), `f1-locations.geojson` and
`f1-locations.json` (centre points with a suggested zoom).

Schema, from `circuits/gb-1948.geojson`:

```json
{"type":"FeatureCollection","name":"gb-1948",
 "bbox":[-1.024286,52.063513,-1.009264,52.078936],
 "features":[{"type":"Feature",
   "properties":{"id":"gb-1948","Location":"Silverstone","Name":"Silverstone Circuit",
                 "opened":1948,"firstgp":1950,"length":5891,"altitude":196},
   "bbox":[...],
   "geometry":{"type":"LineString","coordinates":[[-1.015349,52.07879],[-1.01262,52.078936], ...]}}]}
```

Properties are `id`, `Location`, `Name`, `opened`, `firstgp`, `length` (metres) and
`altitude` (metres at start/finish). `f1-locations.json` entries look like
`{"lon": -97.633, "lat": 30.135, "zoom": 15, "location": "Austin", "name": "Circuit of the Americas", "id": "us-2012"}`.

The id scheme is `{ISO country}-{year opened}`: `gb-1948` Silverstone, `be-1925` Spa,
`it-1922` Monza, `mc-1929` Monaco, `nl-1948` Zandvoort, `us-2012` COTA, `us-2023` Las
Vegas, `us-2022` Miami, `az-2016` Baku, `sa-2021` Jeddah, `es-2026` Madrid, `qa-2004`
Losail, `sg-2008` Marina Bay, `jp-1962` Suzuka, `bh-2002` Sakhir, `br-1940` Interlagos,
`ae-2009` Yas Marina, `hu-1986` Hungaroring, `at-1969` Red Bull Ring, `mx-1962`
Hermanos Rodríguez, `ca-1978` Gilles-Villeneuve, `cn-2004` Shanghai, `it-1953` Imola,
`au-1953` Albert Park, `es-1991` Barcelona. **None of these match F1DB circuit ids**,
which is one of the joins the circuit-layout registry has to carry (SPEC §6.3).

### Measured accuracy

Summing great-circle segment lengths against each file's declared length:

| Circuit | Measured | Declared | Error |
| --- | ---: | ---: | ---: |
| Silverstone `gb-1948` | 5884.4 m | 5891 m | **−0.113%** |
| Monza `it-1922` | 5793.0 m | 5793 m | **−0.002%** |
| Monaco `mc-1929` | — | — | **−0.27%** |
| Spa `be-1925` | 6986.2 m | 7004 m | **−0.255%** |
| Madrid `es-2026` | — | 5474 m | **−0.687%** |

That is publication-grade for an outline.

### Provenance — not OpenStreetMap

The repository's "Acknowledgment" section credits a **Google My Maps** custom map plus
the Wikipedia *List of Formula One circuits*. It is hand-traced, not OSM-derived.

Two consequences:

1. **ODbL does not attach.** The share-alike analysis that would apply to OSM geometry
   is moot for this repository.
2. **A Google Maps terms-of-service question replaces it.** Tracing from Google Maps
   imagery raises a derivative-works question that the MIT wrapper does not answer, and
   it means the clean "OSM-derived, ODbL-attributed" provenance story cannot be told
   about this data at all.

The `altitude` property is a single figure at start/finish, sourced per the README
mainly from a formula1.com feature article on elevation changes, otherwise from
official sites, wikis, or the nearby city's altitude. It is a label, not a profile —
elevation comes from telemetry Z.

## TUMFTM/racetrack-database

The **only** open dataset giving per-point track width, from TU Munich's Chair of
Automotive Technology.

| Fact | Value |
| --- | --- |
| Licence | GNU **LGPL-3.0** |
| Tracks | 25, of which roughly **19 are F1** |
| Format | `tracks/*.csv`, header `# x_m,y_m,w_tr_right_m,w_tr_left_m` |
| Extras | `racelines/*.csv` (`x_m, y_m`, minimum-curvature optimised) and curvature-profile plots |

```
# x_m,y_m,w_tr_right_m,w_tr_left_m
3.439354,-0.495322,6.556,6.536
6.370784,3.555763,6.558,6.537
9.301950,7.606888,6.560,6.538
```

Measured on `Silverstone.csv`:

| Metric | Value |
| --- | --- |
| Points | 1178 |
| Closed centreline length | 5886.8 m |
| Point spacing | mean **4.997 m**, range 4.683–5.162 m (resampled to *approximately* 5 m, not exactly) |
| Total width (right + left) | 11.27 m – 17.84 m, mean **13.82 m** |

The width range is consistent with FIA guidance of a ~10 m minimum, preferably 12 m.

### Caveats the README states itself

- "The original center lines were fetched as GPS points from the **OpenStreetMap**
  project."
- "The center lines were smoothed. Therefore, they **do not lie perfectly in the middle
  of the track** anymore."
- "The track widths were extracted from satellite images using an image processing
  algorithm" — i.e. estimates of unstated accuracy, not surveyed values.
- "The quality of the source data … varies greatly depending on the location."

The first of those is a licence problem, not just a provenance note: because the
geometry originates in OSM, the LGPL-3.0 grant may sit on top of an **ODbL share-alike
obligation that LGPL does not discharge**. That is arguably a worse position than the
LGPL label alone suggests.

Practical posture, matching SPEC §6.1: use TUMFTM as a **build-time width
calibration** — derive a per-circuit mean width and a small number of width-varying
segments — attribute clearly, track the LGPL obligation, and default everything else to
a constant.

### Coverage and the gap

Included F1 venues: Austin, Budapest, Catalunya, Hockenheim, Melbourne, Mexico City,
Montreal, Monza, Sakhir, São Paulo, Sepang, Shanghai, Silverstone, Sochi, Spa,
Spielberg, Suzuka, Yas Marina, Zandvoort. Also present as DTM/IndyCar tracks: Brands
Hatch, Indianapolis, Moscow Raceway, Norisring, Nürburgring, Oschersleben.

**Missing for a 2026 site:** Jeddah, Miami, Las Vegas, Losail, Imola, Baku, Singapore,
Monaco, Portimão, Madrid — roughly a third of the current calendar. Meanwhile the set
still carries Sochi, Sepang, Hockenheim and Moscow. This is the ~12-circuit width gap
that SPEC §9.1 prices into the 3D tiering.

Defaults where width is unavailable: **12 m minimum** (FIA guidance is a minimum of
10 m, preferably 12 m), 13–14 m typical for a modern circuit, 15–18 m on main and pit
straights.

## SVG silhouettes

| Source | Count | Licence | Freshness | Notes |
| --- | --- | --- | --- | --- |
| **F1DB** `src/assets/circuits/` | ~160 layouts × 4 styles | CC BY 4.0 | tracks releases | In-repo only — see [F1DB](f1db.md#circuit-svgs-exist-only-in-the-git-repo) |
| **julesr0y/f1-circuits-svg** | 78 circuits, all layout evolutions 1950 → now | CC BY 4.0 | last push 2026-08-19, 68 stars | `circuits.json` index with `id`/`name`/`length`/`layouts`; a detailed style with start line and track direction for 2026 layouts |
| f1laps/f1-track-vectors | all F1 tracks | MIT | **stale** — last push 2024-06-17 | |
| MasterPlay007/F1-Track-Layouts-SVG | 2026 season | — | — | |

F1DB's set is the default because it is already in the pipeline and its filenames are
F1DB layout ids, which removes a join. julesr0y's is the better source when a page needs
a *historic* layout that F1DB's asset set does not cover, and its per-layout coverage is
the deeper of the two. Both are CC BY 4.0 and both are redistributable.

Given that there is no free, legal F1 photo corpus (SPEC §13.6), these silhouettes plus
typography plus the 3D renders are the site's entire visual material.

## OpenStreetMap, directly

Only worth it when nothing curated exists for a venue.

Working query — verified HTTP 200, 123,404 bytes, **82 ways**, 1,579 node references
(1,475 distinct):

```
[out:json][timeout:90];
way(around:2500, 52.0733, -1.0147)["highway"="raceway"]["sport"="motor"];
out geom;
```

POST it as `curl -s --data-urlencode "data@query.ql" https://overpass-api.de/api/interpreter`.
The `--data-urlencode` form matters — plain `-d @file` intermittently returns 400 or 504
on the public instance. The bbox form is `(south, west, north, east)`; reversed bounds
silently return an HTML error page rather than JSON. `out geom;` inlines coordinates, so
no second node lookup is needed.

### Tag statistics (taginfo, data_until 2026-09-13)

`highway=raceway` appears on **45,606 ways**, 134 nodes and 327 relations. Co-occurring
keys: `sport` 39,148 (`motor` 19,584, `motocross` 9,062, `karting` 8,258), `surface`
16,186 (`asphalt` 7,117), `oneway` 10,159, `name` 9,356, `area` 3,798, `lanes` 1,370,
**`width` only 1,216**.

Values of the `raceway` key: `start-finish` 343, `start` 146, `finish` 88, `kerb` 72,
`service` 53, `pitlane` 47, `gravel trap` 39, `pit_lane` 26, `runoff_area` 20, `turn`
16, `escape` 11. `area:highway=raceway` exists on 207 objects worldwide.

Against 45,606 raceway ways, the kerb and run-off counts are statistical noise: **no F1
circuit has complete kerb or run-off polygons in OSM.** Those features must be generated
procedurally from the centreline and a curvature heuristic, and the page must say so —
"centreline + modelled width", never "survey".

The 343 `raceway=start-finish` nodes are the one genuinely cheap win: it is the least
effortful way to locate a timing line geometrically.

### The multiple-layouts problem

The Silverstone query returns the GP loop *and* the National circuit *and* the
International loop *and* the Stowe circuit, with named ways like "National Pit
Straight", "Hamilton Straight", "Copse", "Maggotts", "Chapel Curve", "Hangar Straight",
"Stowe", "Vale", "Club", "The Loop", "Aintree", "Farm Curve". Six carry `note=Estimate`.
Tag counts for that result: `highway` 82, `sport` 82, `oneway` 68, `surface` 46, `name`
37, `note` 6, `raceway` 2 — **no width, no kerb, no layer, no elevation**.

There is no tag that identifies the current F1 Grand Prix layout. Manual curation is
unavoidable, which is exactly why bacinger/f1-circuits exists — prefer it over raw
Overpass.

Public Overpass limits: ~10,000 requests/day, <1 GB/day download, default timeout 180 s
(max 262,144), default maxsize 512 MiB (max 12 GiB), HTTP 429 on rate limit, HTTP 504 if
a request would exceed half the remaining resources. Mirrors: `gall.openstreetmap.de`,
`lambert.openstreetmap.de`, `overpass.kumi.systems`, `overpass.private.coffee`. Run it
once at build time and commit the GeoJSON; never call it from a browser.

### ODbL — an open question, not a settled one

OSM data is under ODbL v1.0: "You are free to copy, distribute, transmit and adapt our
data, as long as you credit OpenStreetMap and its contributors" and "If you alter or
build upon our data, you may distribute the result only under the same license."

A common shortcut says a rendered 3D scene is a "Produced Work" needing attribution
only. That is **not established**. The ODbL definition the OSMF guideline cites is "a
work (such as an image, audiovisual material, text, or sounds) resulting from using the
whole or a Substantial part of the Contents", and its worked examples are PNG, JPG,
PDF, SVG and printed maps — it says nothing about 3D models, meshes or WebGL. Its own
test cuts the other way for a browser scene: "If the published result of your project
is intended for the extraction of the original data, then it is a database and not a
Produced Work." A WebGL scene necessarily ships vertex geometry to the client, where it
is trivially extractable.

Safest posture: attribute OpenStreetMap contributors prominently **and** offer any
shipped coordinate file under ODbL, rather than relying on Produced Work status.

Attribution must be to "OpenStreetMap" — "© OpenStreetMap contributors" is the accepted
form — appear in a corner of an interactive map, be legible and understandable, and
either link to <https://www.openstreetmap.org/copyright> or otherwise give access to
origin and licence information. It may sit behind an info control provided the licence
remains reachable.

## Credits block

The minimum credits for `/data/`, per source actually used on a given page:

```
Circuit outlines derived from bacinger/f1-circuits (MIT), traced from public map
  sources and Wikipedia.
Circuit layout diagrams from F1DB (CC BY 4.0) and julesr0y/f1-circuits-svg (CC BY 4.0).
Track widths from TUMFTM/racetrack-database (LGPL-3.0).
Where OpenStreetMap data is used: © OpenStreetMap contributors, ODbL.
Elevation: © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided
  under COPERNICUS by the European Union and ESA; all rights reserved.
Telemetry via FastF1 (MIT).
This site is unofficial and is not associated in any way with the Formula 1 companies.
  F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and
  related marks are trade marks of Formula One Licensing B.V.
```

## What still has to be authored

No source in this document provides **banking**. Telemetry gives one line, so there is
no cross-section to measure; MultiViewer has no Z; 30 m DEM cells are wider than the
track; and OSM has effectively no camber tagging on raceways. Banking is hand-authored
per corner and labelled as such — which is one of the reasons a polished 3D track is
affordable for 8–12 circuits rather than 78 (SPEC §9.1).
