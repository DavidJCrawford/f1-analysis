---
type: Reference
title: OpenStreetMap Circuit Extraction
description: Working Overpass QL for raceway geometry, the tags that actually exist at an F1 venue, the multiple-layouts problem, and the ODbL position for a published static site.
resource: https://wiki.openstreetmap.org/wiki/Tag:highway%3Draceway
tags:
  - openstreetmap
  - overpass
  - odbl
  - licensing
  - geojson
  - raceway
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: osm_wiki_raceway
    resource: https://wiki.openstreetmap.org/wiki/Tag:highway%3Draceway
    title: OpenStreetMap wiki — Tag:highway=raceway
  - id: taginfo_raceway
    resource: https://taginfo.openstreetmap.org/api/4/tag/stats?key=highway&value=raceway
    title: taginfo — highway=raceway statistics (data_until 2026-09-13)
  - id: taginfo_raceway_values
    resource: https://taginfo.openstreetmap.org/api/4/key/values?key=raceway
    title: taginfo — values of the raceway key
  - id: overpass_api
    resource: https://overpass-api.de/api/interpreter
    title: Overpass API public instance
  - id: overpass_commons
    resource: https://dev.overpass-api.de/overpass-doc/en/preface/commons.html
    title: Overpass API — commons and usage limits
  - id: osm_copyright
    resource: https://www.openstreetmap.org/copyright
    title: OpenStreetMap copyright and licence
  - id: osmf_produced_work
    resource: https://osmfoundation.org/wiki/Licence/Community_Guidelines/Produced_Work_-_Guideline
    title: OSMF Community Guideline — Produced Work
  - id: osmf_attribution
    resource: https://osmfoundation.org/wiki/Licence/Attribution_Guidelines
    title: OSMF Attribution Guidelines
  - id: bacinger_readme
    resource: https://raw.githubusercontent.com/bacinger/f1-circuits/master/README.md
    title: bacinger/f1-circuits README
status: stable
---

# OpenStreetMap Circuit Extraction

OpenStreetMap is the only source of circuit geometry that is free, global,
current and legally legible. It is also the one that requires the most work per
circuit, because **no tag says "this is the Grand Prix layout"** and because
everything beyond the tarmac centreline is effectively unmapped.

## 1. The working query

Verified against the public instance: **HTTP 200, 123 404 bytes, 82 ways,
1579 node references (1475 distinct).**

```overpassql
[out:json][timeout:90];
way(around:2500, 52.0733, -1.0147)["highway"="raceway"]["sport"="motor"];
out geom;
```

```bash
curl -s --data-urlencode "data@query.ql" https://overpass-api.de/api/interpreter
```

Two mechanical details that cost an afternoon each:

- **Use `--data-urlencode`, not `-d @file`.** Plain `-d` intermittently returns
  400 or 504 from the public instance.
- **`out geom;` inlines the coordinates**, so no second node lookup is needed.

The bbox form also works, but Overpass orders bounds **(south, west, north,
east)**:

```overpassql
way["highway"="raceway"](52.055,-1.035,52.085,-1.000);
```

Reversed bounds return an HTML error page rather than JSON — parse failures
downstream, not a clean error. Validate the response's content type before
parsing.

Element shape:

```json
{"type":"way","id":3571477,
 "bounds":{"minlat":52.0781,"minlon":-1.0186,"maxlat":52.0790,"maxlon":-1.0152},
 "nodes":[...],
 "geometry":[{"lat":52.0786532,"lon":-1.0178209}, ...],
 "tags":{"highway":"raceway","name":"National Pit Straight",
         "oneway":"yes","sport":"motor","surface":"asphalt"}}
```

The cheapest way to locate the timing line geometrically — 343 such nodes exist
globally:

```overpassql
node["raceway"="start-finish"](around:2500, 52.0733, -1.0147);
out geom;
```

## 2. What tags actually exist

Global counts from taginfo, `data_until` 2026-09-13. `highway=raceway` appears
on **45 606 ways**, 134 nodes and 327 relations (46 067 objects).

| Co-occurring key | Ways | Notable values |
| --- | ---: | --- |
| `sport` | 39 148 | motor 19 584, motocross 9 062, karting 8 258 |
| `surface` | 16 186 | asphalt 7 117 |
| `oneway` | 10 159 | yes 9 688 |
| `name` | 9 356 | |
| `area` | 3 798 | |
| `lanes` | 1 370 | |
| **`width`** | **1 216** | 2.7% of raceway ways |

Values of the `raceway` key itself:

| Value | Uses |
| --- | ---: |
| `start-finish` | 343 |
| `start` | 146 |
| `finish` | 88 |
| `kerb` | 72 |
| `service` | 53 |
| `pitlane` | 47 |
| `gravel trap` | 39 |
| `pit_lane` | 26 |
| `runoff_area` | 20 |
| `turn` | 16 |
| `escape` | 11 |

`area:highway=raceway` exists on **207 objects worldwide**.

### The same counts at one venue

The 82 ways returned by the query in §1 carry, in total:

| Tag | Count |
| --- | ---: |
| `highway` | 82 |
| `sport` | 82 |
| `oneway` | 68 |
| `surface` | 46 |
| `name` | 37 |
| `note` | 6 |
| `raceway` | 2 |

**No `width`. No `kerb`. No `layer`. No `ele`.** Silverstone is one of the
best-mapped circuits in the world and it has a centreline, a surface type and a
direction of travel — nothing else. Against 45 606 raceway ways, 72 global uses
of `raceway=kerb` and 20 of `raceway=runoff_area` are statistical noise: no F1
circuit has complete kerb or run-off polygons.

That is why kerbs, run-off and barriers are generated procedurally from
curvature rather than extracted. See
[Centreline construction](centreline-construction.md) §10 and
[Banking and elevation](banking-and-elevation.md).

## 3. The multiple-layouts problem

The query returns **every layout at the venue**. At Silverstone the 82 ways span
the Grand Prix loop, the National circuit, the International loop and the Stowe
circuit, with named ways including *National Pit Straight*, *Hamilton Straight*,
*Copse*, *Maggotts*, *Chapel Curve*, *Hangar Straight*, *Stowe*, *Vale*,
*Club*, *The Loop*, *Aintree* and *Farm Curve*. Six carry `note=Estimate`.

There is no reliable tag that identifies the current F1 Grand Prix layout.
Assembling one closed ring requires:

1. Filter to `sport=motor`, discard `raceway=service`, `pitlane`, `pit_lane`.
2. Build a node-adjacency graph over the remaining ways.
3. Find the cycle whose total length is closest to the circuit's declared length
   and whose bbox diagonal is largest — the GP loop is the longest ring at
   almost every venue, and the National/International loops are proper subsets.
4. **Hand-verify the result against the F1DB layout SVG**, and record the way
   IDs in the registry so the curation survives an OSM edit.

Step 4 is not optional and does not scale to 160 layouts. This is precisely why
[bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) exists as a
hand-curated set, and why the pipeline prefers it — with the licence caveat in
§5 — and falls back to Overpass only for the circuits it lacks.

## 4. Public instance limits

| Limit | Value |
| --- | --- |
| Requests | ~10 000/day |
| Download | < 1 GB/day |
| Default timeout | 180 s (max 262 144) |
| Default maxsize | 512 MiB (max 12 GiB) |
| Rate limited | HTTP 429 |
| Would exceed half the remaining resources | HTTP 504 |

Mirrors: `gall.openstreetmap.de`, `lambert.openstreetmap.de`,
`overpass.kumi.systems`, `overpass.private.coffee`.

**Run Overpass once at build time and commit the GeoJSON.** Never call it from
the browser: it is a shared volunteer resource, the site is static, and per
[spec §12.2](../../../SPEC.md) the build must be reproducible from the
repository with no network access.

Barrier queries at permanent venues are worth trying and not worth depending on:
`barrier=*` coverage is patchy, and a Silverstone barrier query timed out twice
on the public instance.

## 5. What is and is not OSM-derived

This matters because the licence follows the provenance, and one widely
repeated assumption here is wrong.

| Asset | Actually derived from | Licence that attaches |
| --- | --- | --- |
| Direct Overpass output | OpenStreetMap | **ODbL 1.0** |
| bacinger/f1-circuits | **Google My Maps tracing + Wikipedia** | MIT wrapper; **Google Maps ToS question** |
| TUMFTM/racetrack-database | OpenStreetMap GPS points, smoothed | LGPL-3.0 **over a possible ODbL obligation** |
| F1DB circuit SVGs | F1DB's own assets | CC BY 4.0 |

**bacinger/f1-circuits is not OpenStreetMap-derived.** Its README's
Acknowledgment section credits a Google My Maps custom map and the Wikipedia
list of Formula One circuits — nothing else. The repo is MIT
(© 2019–2025 Tomislav Bacinger), 362 stars, last commit 2026-02-05, and contains
**40 circuits**, not 41 (the README's table has 41 rows because one of them is
the header). All 40 features are closed LineStrings.

So ODbL does not attach to it — but a Google Maps / Google Earth derivative-works
question does, and that question is open. It is recorded as a gating item
alongside the others in [spec §13](../../../SPEC.md).

**TUMFTM's position is the inverse and slightly worse than its label suggests.**
Its README states "The original center lines were fetched as GPS points from the
OpenStreetMap project." An LGPL-3.0 grant does not discharge an ODbL share-alike
obligation sitting underneath it.

Measured quality of the bacinger set against declared lengths: Silverstone
−0.113%, Monza −0.002%, Monaco −0.27%, Spa −0.255%, Madrid −0.687%. That is
publication-grade geometry whatever its provenance.

## 6. The ODbL position

OpenStreetMap is ODbL v1.0. From
[openstreetmap.org/copyright](https://www.openstreetmap.org/copyright): you are
free to copy, distribute, transmit and adapt the data "as long as you credit
OpenStreetMap and its contributors", and "If you alter or build upon our data,
you may distribute the result only under the same license."

The usual resolution is the **Produced Work / Derivative Database** distinction.
The ODbL definition the OSMF guideline cites is "a work (such as an image,
audiovisual material, text, or sounds) resulting from using the whole or a
Substantial part of the Contents", and its worked examples are PNG, JPG, PDF,
SVG images and printed maps. **It makes no mention of 3D models, meshes or WebGL
renderings.**

And its own test cuts against a browser 3D scene:

> If the published result of your project is intended for the extraction of the
> original data, then it is a database and not a Produced Work.

A three.js circuit necessarily ships vertex geometry to the client, where it is
trivially extractable — much closer to the database side of that line than a
rendered PNG is.

**The site's position:** treat the Produced Work classification of an
interactive WebGL scene as an **open question, not a settled one**, and do not
rely on it. Instead:

| Artifact | Treatment |
| --- | --- |
| Rendered SVG layout silhouette | Produced Work; attribution |
| `<canvas>` 3D scene | attribute **and** offer the geometry under ODbL |
| Any shipped `.geojson` / coordinate `.json` / quantised geometry buffer | Derivative Database; **published under ODbL** |

Publishing our OSM-derived coordinate files under ODbL costs a one-line note in
`/data/` and in the repository README, and removes the question entirely. That
is cheaper than being right about a guideline that does not address the case.

Note that this analysis is **moot for bacinger** (§5) and **live for TUMFTM and
for anything we extract ourselves**.

## 7. Attribution wording

Per the OSMF Attribution Guidelines, attribution "must be to 'OpenStreetMap'";
`© OpenStreetMap contributors` is the accepted form. For browsable or
interactive maps the credit "should typically appear in a corner of the map",
must be "legible and understandable", and must either link to
`https://www.openstreetmap.org/copyright` or otherwise provide a way to reach
the origin and licence information. It may be collapsed behind an info control
provided the licence information remains reachable.

The minimum credits block for this site, carried on `/data/` with the OSM line
also in the corner of any interactive geometry:

```
Circuit geometry © OpenStreetMap contributors, available under the Open
Database License (ODbL).
Circuit outlines derived from bacinger/f1-circuits (MIT).
Track widths from TUMFTM/racetrack-database (LGPL-3.0).
Elevation: © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018
provided under COPERNICUS by the European Union and ESA; all rights reserved.
Telemetry via FastF1 (MIT) / OpenF1.
```

And the trademark disclaimer, which follows bacinger's own pattern and appears
in the footer of every page:

> This repository is unofficial and is not associated in any way with the
> Formula 1 companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD
> CHAMPIONSHIP, GRAND PRIX, and related marks are trademarks of Formula One
> Licensing B.V.

**Unverified:** F1's own fan-site guidelines dictate specific disclaimer wording,
and the exact current text could not be located — both candidate URLs returned
404. The wording above is a community convention, not a compliance artifact, and
must be confirmed before launch per [spec §13.5](../../../SPEC.md).
