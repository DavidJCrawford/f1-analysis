---
type: Reference
title: Circuit Layout Registry
description: The hand-verified build artifact that binds a race to a circuit layout and a layout to a piece of geometry across F1DB, MultiViewer, OpenF1, bacinger and TUMFTM identifiers.
resource: https://github.com/f1db/f1db
tags:
  - entity-resolution
  - registry
  - build-artifact
  - f1db
  - identifiers
  - circuits
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: mv_index
    resource: https://api.multiviewer.app/api/v1/circuits
    title: MultiViewer circuits index
  - id: mv_silverstone_2026
    resource: https://api.multiviewer.app/api/v1/circuits/2/2026
    title: MultiViewer circuitKey 2, year path 2026 (returns 2022 data)
  - id: bacinger_repo
    resource: https://github.com/bacinger/f1-circuits
    title: bacinger/f1-circuits
  - id: bacinger_locations
    resource: https://raw.githubusercontent.com/bacinger/f1-circuits/master/f1-locations.json
    title: bacinger/f1-circuits f1-locations.json
  - id: tumftm_repo
    resource: https://github.com/TUMFTM/racetrack-database
    title: TUMFTM/racetrack-database
  - id: julesroy_svg
    resource: https://github.com/julesr0y/f1-circuits-svg
    title: julesr0y/f1-circuits-svg
  - id: openf1_docs
    resource: https://openf1.org/docs
    title: OpenF1 API documentation
status: stable
---

# Circuit Layout Registry

Five sources, five identifier schemes, and none of them agrees on what a
circuit *is*. `circuit-layout-registry.json` is the hand-verified build artifact
that resolves *"this race ran on this layout, whose geometry is this
centreline"*. It is named in [spec §6.3](../../../SPEC.md) as a first-class
artifact and in [spec §15](../../../SPEC.md) as risk 7.

## 1. Why this cannot be a join

The identifier schemes do not just differ in spelling. **They partition the
world differently.**

| Source | Key | Grain | Count |
| --- | --- | --- | ---: |
| F1DB | `circuitId` | circuit | **78** |
| F1DB | `layoutId` | **layout** | **~160** |
| MultiViewer | `circuitKey` (opaque int) + year path | circuit, frozen snapshot | **32** |
| OpenF1 | `circuit_short_name` (string) | circuit | 2023+ only |
| bacinger | `{iso2}-{year_opened}` | **circuit**, one geometry each | **40** |
| TUMFTM | track filename | circuit | 25, ~19 of them F1 |
| julesr0y | `id` + `layouts[]` | **layout** | 78 circuits, all evolutions |

The decisive mismatch: **F1DB has ~160 layouts, bacinger has 40 geometries and
one per circuit.** `gb-1948` is *a* Silverstone, not *the* Silverstone of any
given year. Silverstone, Bahrain, Yas Marina, Zandvoort, Albert Park, Spa,
Suzuka and Hockenheim have all been relaid within the championship era. Picking
one geometry per circuit silently misattributes lap records, corner numbering,
sector positions and circuit length — and does so invisibly, because the render
still looks like Silverstone.

**A circuit is an entity with a version history.** The registry's primary key is
the layout, never the circuit.

## 2. The identifier schemes in detail

### bacinger — `{ISO 3166-1 alpha-2}-{year opened}`

Not a layout ID: the year is when the *venue* opened, not when the layout was
introduced.

| ID | Circuit | ID | Circuit |
| --- | --- | --- | --- |
| `gb-1948` | Silverstone | `us-2012` | Circuit of the Americas |
| `be-1925` | Spa-Francorchamps | `us-2022` | Miami |
| `it-1922` | Monza | `us-2023` | Las Vegas |
| `it-1953` | Imola | `az-2016` | Baku |
| `mc-1929` | Monaco | `sa-2021` | Jeddah |
| `nl-1948` | Zandvoort | `qa-2004` | Losail |
| `jp-1962` | Suzuka | `sg-2008` | Marina Bay |
| `bh-2002` | Sakhir | `ae-2009` | Yas Marina |
| `br-1940` | Interlagos | `hu-1986` | Hungaroring |
| `at-1969` | Red Bull Ring | `mx-1962` | Hermanos Rodríguez |
| `ca-1978` | Gilles-Villeneuve | `cn-2004` | Shanghai |
| `au-1953` | Albert Park | `es-1991` | Barcelona-Catalunya |
| `es-2026` | Madring (Madrid) | | |

Feature properties: `id`, `Location`, `Name`, `opened`, `firstgp`, `length`
(metres), `altitude` (metres at start/finish). Every feature and the
FeatureCollection carry a `bbox`.

```json
{"id":"gb-1948","Location":"Silverstone","Name":"Silverstone Circuit",
 "opened":1948,"firstgp":1950,"length":5891,"altitude":196}
```

`f1-locations.json` gives a centre point and a suggested zoom per circuit:
`{"lon":-97.633,"lat":30.135,"zoom":15,"location":"Austin",
"name":"Circuit of the Americas","id":"us-2012"}`.

The `altitude` property's provenance, per the README, is mainly a Formula1.com
feature article on elevation changes — not a survey. Use it as `H_datum` only
where telemetry Z is unavailable.

### MultiViewer — opaque integer key, frozen geometry

| Key | Circuit | Key | Circuit | Key | Circuit |
| ---: | --- | ---: | --- | ---: | --- |
| 2 | Silverstone | 34 | Hockenheim | 72 | Nürburgring |
| 4 | Hungaroring | 39 | Monza | 79 | Sochi |
| 6 | Imola | 46 | Suzuka | 144 | Baku |
| 7 | Spa | 49 | Shanghai | 146 | Mugello |
| 9 | Austin | 55 | Zandvoort | 147 | Algarve |
| 10 | Melbourne | 59 | Istanbul | 148 | Sakhir Outer |
| 14 | Interlagos | 61 | Singapore | 149 | Jeddah |
| 15 | Catalunya | 63 | Sakhir | 150 | Losail |
| 19 | Spielberg | 65 | Mexico City | 151 | Miami |
| 22 | Monte Carlo | 70 | Yas Marina | 152 | Las Vegas |
| 23 | Montreal | | | | |
| 28 | Paul Ricard | | | | |

**The year path parameter is silently ignored.** `/api/v1/circuits/2/2024`,
`/2025` and `/2026` all return byte-identical Silverstone data with
`"year": 2022` and `raceDate: 2022-07-03`. Spa (key 7) and Monza (key 39) return
2021 for every requested year. FastF1's `get_circuit_info()` passes the session
year straight through, so **a 2026 session silently receives 2021–2022 geometry
with no warning.**

Consequences for a site dated 2026: Madring is absent entirely (keys 153–157
return nothing; 152 is Las Vegas), and every layout change or resurfacing since
2022 is invisible. The registry therefore carries an explicit
`geometry_vintage_year` and the page renders a staleness note when it is more
than two seasons behind the race being displayed.

MultiViewer is **blocked pending contact** under
[spec §13.3](../../../SPEC.md) — it publishes no terms of use. The registry's
schema accommodates it so that the binding work is done and the geometry can be
switched on if permission arrives; until then `geometry.source` never resolves
to `multiviewer` in a published build, and the pipeline fails the build if it
does.

### F1DB — the spine

Layout IDs are the registry's primary key and the source of every slug
(`/circuits/monza/layouts/monza-1/`). Per
[spec §6.1](../../../SPEC.md), **F1DB's SVG assets are not in the release
zips**: they exist only in the git repository at

```
src/assets/circuits/{black,black-outline,white,white-outline}/<layoutId>.svg
```

A pipeline that downloads release artifacts gets zero SVGs. It must
sparse-checkout the repository or raw-fetch per layout ID, and the registry's
`svg` field records which variants were successfully fetched.

### OpenF1 — `circuit_short_name`

A display string, 2023+ only, with no stability guarantee. It is a
**cross-check key, never a join key**: matched to a layout by
`(year, round)` from the meeting, then asserted to agree with the registry. A
disagreement fails the build rather than silently preferring one side.

## 3. Schema

One record per layout. Emitted as `circuit-layout-registry.json`, schema-validated
in CI per [spec §12.3](../../../SPEC.md).

```jsonc
{
  "layout_id": "silverstone-4",          // F1DB layoutId — PRIMARY KEY
  "circuit_id": "silverstone",           // F1DB circuitId
  "slug": "silverstone/layouts/silverstone-4",
  "active_years": [2011, 2026],          // inclusive; open-ended layouts use the current season
  "declared_length_m": 5891,
  "turns": 18,

  "identifiers": {
    "multiviewer_circuit_key": 2,        // null where absent
    "openf1_circuit_short_name": "Silverstone",
    "bacinger_id": "gb-1948",            // CIRCUIT-grain: see layout_fidelity
    "tumftm_track": "Silverstone",
    "julesroy_layout": "gb-1948-2011"
  },

  "geometry": {
    "source": "bacinger",                // bacinger | osm | tumftm | telemetry | multiviewer
    "layout_fidelity": "exact",          // exact | approximate | wrong-era
    "vintage_year": 2024,                // what the geometry actually depicts
    "measured_length_m": 5884.4,
    "length_error_pct": -0.113,
    "points": 1024,                      // after arc-length resampling
    "closed": true
  },

  "anchor": {                            // see coordinate-systems.md
    "lat0": 52.071824, "lon0": -1.016350,
    "tx_m": -294.5, "ty_m": -512.6,
    "k_east": 3928530.0, "k_north": 6375230.0,
    "fit_rotation_deg": -1.2,
    "fit_residual_m": 5.13,
    "valid_years": [2020, 2026]          // anchors are versioned; see §6
  },

  "elevation": {
    "z_source": "telemetry",             // telemetry | dem | flat
    "z_session": "2024-british-grand-prix-race",
    "h_datum_m": 155.2,
    "vertical_exaggeration": 1.0
  },

  "width": {
    "source": "tumftm",                  // tumftm | constant
    "mean_total_m": 13.82,
    "min_total_m": 11.27,
    "max_total_m": 17.84
  },

  "features": {
    "corners_source": "multiviewer",     // multiviewer | curvature | none
    "mini_sectors": null,                // integer, or null where unavailable
    "drs_zones_derived_from": "2024-british-grand-prix-race",
    "street_circuit": false
  },

  "tier_3d": "hero",                     // hero | standard | outline
  "svg": ["black", "black-outline", "white", "white-outline"],

  "provenance": {
    "verified_by": "human",
    "verified_at": "2026-09-14T00:00:00Z",
    "notes": "Arena layout; pre-2010 Silverstone is silverstone-3."
  }
}
```

`layout_fidelity` is the field that keeps the registry honest. It is the answer
to "does the geometry we have actually depict the layout this race ran on?":

| Value | Meaning | Page behaviour |
| --- | --- | --- |
| `exact` | Geometry depicts this layout | Full treatment |
| `approximate` | Same venue, minor differences (resurfacing, kerb changes, a re-profiled corner) | Rendered with a note |
| `wrong-era` | Only a different layout's geometry exists | **No 3D.** Outline tier, honest-absence copy |

`wrong-era` is the default for every historical layout, and that is the expected
majority: 40 circuit-grain geometries against ~160 layouts means most layouts
will never have their own geometry. That is not a gap to apologise for — it is
the [spec §4.2](../../../SPEC.md) coverage tiering applied to geometry.

## 4. Coverage, honestly

| Asset | Circuits covered | Against 78 circuits / ~160 layouts |
| --- | ---: | --- |
| F1DB layout SVG | 78 | complete, layout-grain |
| julesr0y SVG (CC BY 4.0) | 78, all evolutions 1950→now | complete, layout-grain; editorial 2D |
| bacinger GeoJSON | 40 | circuit-grain, current layouts only |
| TUMFTM width | ~19 F1 | circuit-grain, stale (Sochi, Sepang, Hockenheim present; Jeddah, Miami, Las Vegas, Losail, Imola, Baku, Singapore, Madrid absent) |
| MultiViewer corners | 32 | frozen 2021–2023; **blocked** |
| Telemetry Z | 2020+ sessions | layout-grain by construction |
| 1 m LiDAR | 6 venues | see [Banking and elevation](banking-and-elevation.md) §3 |

The 3D tier assignment in `tier_3d` follows directly: **hero** requires
`layout_fidelity == "exact"`, a telemetry Z source, a width source and an
authored banking table; **standard** requires exact or approximate geometry and
any width; everything else is **outline**.

## 5. Resolution order

For a race, in this order, stopping at the first hit:

1. `(year, round)` → F1DB race record → `layoutId`. **Authoritative.** Never
   resolved by circuit name.
2. `layoutId` → registry record.
3. Geometry by `geometry.source`, in preference order: `bacinger` →
   `osm` → `telemetry` → `tumftm`. `multiviewer` is excluded from published
   builds (§2).
4. Corners: `multiviewer` where licensed, otherwise curvature detection per
   [Corner and sector detection](corner-and-sector-detection.md) §4.
5. Z: telemetry for 2020+ sessions at this venue, otherwise flat.

Every step is a dictionary lookup against a committed artifact. **No step does
fuzzy name matching at build time.** Name matching happens once, by a human,
when a registry row is created.

## 6. Anchors are versioned

`anchor.valid_years` exists because of an open question rather than a known
problem: it is **unverified** whether the live-timing origin is stable across
seasons for a given venue, or whether it moves when timing equipment is
resurveyed. The anchors currently recorded were derived from 2022 and 2024 data.

Carrying the year range means a discovered shift is a data change, not a schema
migration. The regression test in §7 is what would discover it.

## 7. Regression tests

CI blocks on all of these.

| Test | Assertion |
| --- | --- |
| **Completeness** | Every F1DB `layoutId` referenced by any race has a registry row |
| **Uniqueness** | `layout_id` unique; `(multiviewer_circuit_key, vintage_year)` unique where non-null |
| **Length** | `abs(length_error_pct) < 1.5` for `layout_fidelity == "exact"` |
| **Closure** | First and last centreline points within 0.01 m |
| **Chirality** | Signed ring area sign matches the source ring (catches the ENU→three.js mirror bug) |
| **Anchor round-trip** | ENU → WGS84 → ENU over 800 stations, max residual < 0.10 m |
| **Anchor drift** | Re-fit each anchor against the latest available session; flag any shift > 5 m |
| **Corner distances** | Corner `Distance` values monotonic and within `[0, declared_length_m]` |
| **Licence boundary** | No published artifact carries `geometry.source == "multiviewer"`, and no NC-SA-sourced value appears in any emitted file |
| **Tier consistency** | `tier_3d == "hero"` implies exact fidelity + telemetry Z + a width source + a banking table |

The licence-boundary test is the mechanism referred to in
[spec §13.4](../../../SPEC.md): the role boundary between sources is enforced in
the pipeline, not by good intentions.

## 8. Build order

```
1.  F1DB release zip        -> circuits, layouts, races        (CC BY 4.0 spine)
2.  F1DB git sparse-checkout-> src/assets/circuits/**/*.svg     (not in the zip)
3.  bacinger raw fetch      -> 40 GeoJSON rings
4.  Overpass, once          -> rings for circuits bacinger lacks   (commit output)
5.  TUMFTM raw fetch        -> width profiles for ~19 circuits
6.  FastF1 local ingest     -> median Z profile per venue, 2020+   (never on CI)
7.  Arc-length resample     -> uniform stations, closure forced
8.  Anchor fit              -> lat0/lon0/tx/ty/k_east/k_north per layout
9.  Human verification      -> layout_fidelity, banking table, tier_3d
10. Emit + validate         -> circuit-layout-registry.json + per-layout geometry
```

Steps 3–5 run once and their output is committed, so the site is buildable from
the repository alone with no network access — the constraint in
[spec §12.2](../../../SPEC.md). Step 6 must run on a human's machine: F1's
live-timing archive blocks datacenter IPs, so GitHub-hosted runners cannot
ingest.

Step 9 is the one that does not automate. It is roughly 160 judgements made
once, each recorded with a `provenance.notes` line explaining the call — which
is what makes the registry auditable rather than merely present.
