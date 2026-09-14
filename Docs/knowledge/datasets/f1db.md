---
type: Dataset
title: F1DB v2026.14.0
description: The CC BY 4.0 bulk dataset covering 1950–2026 that forms this site's redistributable spine — release artifacts, table inventory, the in-repo-only circuit SVGs, and the provenance gap that makes its licence an assumption.
resource: https://github.com/f1db/f1db/releases/tag/v2026.14.0
tags: [f1db, bulk-download, csv, sqlite, cc-by, historical, spine]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_release_api
    resource: https://api.github.com/repos/f1db/f1db/releases/latest
    title: F1DB latest release metadata (GitHub API)
  - id: f1db_readme
    resource: https://raw.githubusercontent.com/f1db/f1db/main/README.md
    title: F1DB README and licence statement
  - id: f1db_schema
    resource: https://raw.githubusercontent.com/f1db/f1db/main/src/schema/current/single/f1db.schema.json
    title: F1DB JSON Schema (v6.5.0)
  - id: f1db_svg_assets
    resource: https://raw.githubusercontent.com/f1db/f1db/main/src/assets/circuits/black/monza-1.svg
    title: F1DB circuit SVG asset (in-repo path, verified 200)
status: stable
---

# F1DB v2026.14.0

F1DB is the **canonical spine**: it is the only comprehensive Formula 1 dataset under a
licence that permits redistribution, it covers 1950 to the current season, and it is
re-released after every race. Every entity page on this site is keyed off an F1DB
identifier, and every slug on the site derives from an F1DB canonical id rather than a
display name (SPEC §5.1).

| Fact | Value |
| --- | --- |
| Release | **v2026.14.0**, published 2026-09-13 |
| Licence | **CC BY 4.0** — "F1DB is licensed under a Creative Commons Attribution 4.0 International License" |
| Versioning | CalVer `YYYY.RR.MICRO`, where `RR` is the round number and `RR = 0` is pre-season |
| Cadence | "New releases will be available as soon as possible after every race." |
| Resolve latest | `GET https://api.github.com/repos/f1db/f1db/releases/latest` |
| Schema | `src/schema/current/single/f1db.schema.json`, currently **v6.5.0** |

## Release artifacts

The v2026.14.0 release carries exactly **13 assets**.

| Asset | Size (bytes) |
| --- | ---: |
| `f1db-csv.zip` | 4,482,718 |
| `f1db-json-single.zip` | 6,739,988 |
| `f1db-json-splitted.zip` | 5,908,479 |
| `f1db-sql-sqlite.zip` | 5,807,443 |
| `f1db-sqlite.zip` | 15,626,195 |
| `f1db-smile-single.zip` | — |
| `f1db-smile-splitted.zip` | — |
| `f1db-sql-mysql.zip` | — |
| `f1db-sql-mysql-single-inserts.zip` | — |
| `f1db-sql-postgresql.zip` | — |
| `f1db-sql-postgresql-single-inserts.zip` | — |
| `f1db-sql-sqlite-single-inserts.zip` | — |
| `checksums_sha256.txt` | — |

The pipeline takes `f1db-csv.zip` (one 4.5 MB download per build) and verifies it
against `checksums_sha256.txt`. `f1db-sqlite.zip` is the convenience artifact for
ad-hoc SQL while designing a page; it is not in the build path.

**There is no SVG asset.** `f1db-svg.zip` returns HTTP 404 — see
[Circuit SVGs](#circuit-svgs-exist-only-in-the-git-repo) below.

## Entity counts

Counts as carried into SPEC §4.1, which is where the site's ~2,400-page launch scale
comes from.

| Entity | Count | Source table |
| --- | ---: | --- |
| Seasons | 77 | `f1db-seasons.csv` |
| Races (Grands Prix held) | 1,172 | `f1db-races.csv` |
| Circuits | 78 | `f1db-circuits.csv` |
| Circuit layouts | 160 | `f1db-circuits-layouts.csv` |
| Constructors | 214 | `f1db-constructors.csv` |
| Constructor chronology rows | 217 | `f1db-constructors-chronology.csv` |
| Drivers | 881 | `f1db-drivers.csv` |
| Race results | 27,599 | `f1db-races-race-results.csv` |
| Pit stops | 22,515 | `f1db-races-pit-stops.csv` |
| Fastest laps | 17,148 | `f1db-races-fastest-laps.csv` |

## Table inventory

The CSV bundle contains **47 files**. Verified headers for the tables that drive the
site's three main page types:

```
f1db-circuits.csv          (78 rows)
id,name,fullName,previousNames,type,direction,placeName,countryId,latitude,longitude,length,turns,totalRacesHeld

f1db-circuits-layouts.csv  (160 rows)
id,circuitId,effective,length,turns

f1db-races.csv             (1,172 rows)
id,year,round,date,time,grandPrixId,officialName,qualifyingFormat,sprintQualifyingFormat,
circuitId,circuitLayoutId,circuitType,direction,courseLength,turns,laps,distance,
scheduledLaps,scheduledDistance,driversChampionshipDecider,constructorsChampionshipDecider,
preQualifyingDate/Time,freePractice1..4Date/Time,qualifying1/2Date/Time,qualifyingDate/Time,
sprintQualifyingDate/Time,sprintRaceDate/Time,sprintRaceLaps,sprintRaceDistance,
sprintRaceScheduledLaps,sprintRaceScheduledDistance,warmingUpDate/Time

f1db-races-race-results.csv (27,599 rows) — includes
positionDisplayOrder,positionNumber,positionText,driverNumber,driverId,constructorId,
engineManufacturerId,tyreManufacturerId,sharedCar,laps,time,timeMillis,timePenalty,
gap,gapMillis,gapLaps,interval,intervalMillis,reasonRetired,points,polePosition,
qualificationPositionNumber,gridPositionNumber,positionsGained,pitStops,fastestLap,
driverOfTheDay,grandSlam
```

**`f1db-circuits-layouts.csv` carries no geometry** — its only columns are
`id,circuitId,effective,length,turns`. Layout geometry comes from
[circuit geometry sources](circuit-geometry-sources.md), not from F1DB.

Remaining table families: `chassis`, `constructors`, `constructors-chronology`,
`continents`, `countries`, `drivers`, `drivers-family-relationships`,
`engine-manufacturers`, `engines`, `entrants`, `grands-prix`, `tyre-manufacturers`; the
per-session result tables (`free-practice-1..4`, `pre-qualifying`, `qualifying-1/2`,
`qualifying`, `sprint-qualifying`, `sprint-race`, `sprint-starting-grid`,
`starting-grid`, `warming-up`, `driver-of-the-day`); and the per-race and per-season
standings tables.

## Fields that exist nowhere else

These are the reason F1DB is the spine rather than a fallback.

| Field | Table | Why it matters |
| --- | --- | --- |
| `reasonRetired` | races-race-results | The only redistributable source of granular retirement causes for recent seasons. jolpica has collapsed its own — see [jolpica-f1](jolpica-f1.md) |
| `gapLaps` | races-race-results | Real lap-down margins, where jolpica now returns a single flattened value |
| `driversChampionshipDecider` / `constructorsChampionshipDecider` | races | Which race settled a title — a first-class editorial hook on every season page |
| `sharedCar` | races-race-results | Pre-1958 shared drives, which most schemas silently drop (SPEC §6.4) |
| `grandSlam`, `polePosition`, `fastestLap`, `driverOfTheDay` | races-race-results | Pre-computed, so no derivation risk |
| `positionsGained` | races-race-results | Saves a grid-to-finish join |
| `positionText` | races-race-results | Carries the non-numeric classifications the site must render honestly |
| `effective` | circuits-layouts | The date a layout came into use — the field that makes "a circuit is an entity with a version history" (SPEC §6.3) representable at all |
| `previousNames` | circuits | Redirect aliases for renamed venues |
| `scheduledLaps` vs `laps`, `scheduledDistance` vs `distance` | races | Shortened races render as shortened races |

Schema history worth knowing: **v2026.0.1 (schema v6.4.0)** introduced `CircuitLayout`
and `Race.circuitLayoutId`; **v2026.8.2** added `sprintRaceLaps`,
`sprintRaceDistance`, `sprintRaceScheduledLaps` and `sprintRaceScheduledDistance`.

## Circuit SVGs exist only in the git repo

This is the single most expensive thing to get wrong about F1DB, because a pipeline
that downloads release artifacts and looks for SVGs finds nothing and fails silently.

- Introduced in **v2026.0.1** (schema v6.4.0).
- **Not bundled in any release zip.** They live only in the repository tree at
  `src/assets/circuits/{black,black-outline,white,white-outline}/<layoutId>.svg`.
- Fetch per layout id, e.g.
  `https://raw.githubusercontent.com/f1db/f1db/main/src/assets/circuits/black/monza-1.svg`
  (verified 200, as are `.../white-outline/monza-1.svg` and
  `.../black-outline/silverstone-3.svg`).
- The filename is the **layout** id, not the circuit id — which is why the
  circuit-layout registry (SPEC §6.3) has to exist before the outline tier can render.

The pipeline therefore either sparse-checks-out `src/assets/circuits/` or raw-fetches
one file per layout id, and caches the result in the repo. These four styles are the
entire visual material for the **Outline** 3D tier (SPEC §9.1) and for circuit index
thumbnails, and — given that there is no legally usable F1 photo corpus (SPEC §13.6) —
a significant fraction of the site's imagery overall.

## Licence and the provenance gap

The LICENSE file is "Attribution 4.0 International" — CC BY 4.0. Attribution is
required; commercial use is permitted; there is no ShareAlike clause. That is what
makes F1DB the only source whose values may be written into published artifacts.

**But the licence is a claim by a compiler about data he did not create.** The README
documents **no upstream provenance at all**: no source list, no third-party
attribution, and no trademark disclaimer despite the use of "Formula 1®". If any
substantial part of the compilation descends from Ergast (which was CC BY-**NC-SA**
3.0), the permissive relicensing would not be effective downstream, and the site's
clean-licence spine is an assumption rather than a fact.

This is a **gating item**, not a footnote. SPEC §13.2 and risk #2 both record it:
*ask the maintainer directly before F1DB becomes load-bearing.* Until that is resolved,
the exposure is recorded honestly on `/data/` rather than papered over.

Attribution line for the footer and `/data/`:

```
Historical data from F1DB (https://github.com/f1db/f1db), licensed CC BY 4.0.
```

## Role in the pipeline

| Question | Answered by F1DB? |
| --- | --- |
| Results, grids, standings, points, 1950–2026 | Yes — sole source |
| Retirement causes and laps-down, all seasons | Yes — sole source for recent seasons |
| Circuit and layout identity, dates, lengths, turns | Yes |
| 2D layout diagrams | Yes, via the in-repo SVGs |
| Lap times, sectors, stints, tyres | No — [FastF1](fastf1.md), 2018+ |
| Telemetry and position | No — [FastF1](fastf1.md) / [live-timing archive](f1-livetiming-archive.md), 2018+ |
| Track centreline geometry | No — [circuit geometry sources](circuit-geometry-sources.md) |

Because F1DB is a plain GitHub release with no rate limit, no authentication and no
service dependency, it is also the **most stable** source in the stack. A build that
can reach GitHub can always rebuild the entire archival-tier site (SPEC phase 1) from
F1DB alone.
