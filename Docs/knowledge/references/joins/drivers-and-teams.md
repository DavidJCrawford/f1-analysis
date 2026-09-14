---
type: Reference
title: Driver and Team Identifier Joins
description: How DriverId and TeamId bind FastF1, jolpica and F1DB together, where the punctuation and lineage break the join, and why abbreviations, car numbers and team membership are all season- or session-scoped rather than identities.
tags: [drivers, constructors, joins, identifiers, lineage, crosswalk]
resource: https://raw.githubusercontent.com/f1db/f1db/main/README.md
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API reference — SessionResults column semantics
  - id: f1db_csv
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 CSV bundle (constructors, chronology, race results)
  - id: jolpica_standings
    resource: https://api.jolpi.ca/ergast/f1/2026/constructorstandings.json
    title: jolpica-f1 2026 constructor standings (round 14)
  - id: fastf1_constants
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/plotting/constants.json
    title: FastF1 plotting constants.json — per-season team colours, 2018–2026
  - id: openf1_drivers
    resource: https://api.openf1.org/v1/drivers?session_key=11369
    title: OpenF1 drivers for the 2026 Spanish Grand Prix race session
status: stable
---

# Driver and Team Identifier Joins

The good news, stated once so the rest of this document can be about the exceptions:
FastF1's `SessionResults.DriverId` is documented as the "driverId that is used by the
Ergast API" and `TeamId` as the "constructorId that is used by the Ergast API". Those
slugs are the same shape jolpica serves and the same shape F1DB uses. This is the one
join in the project that mostly works out of the box, and it is what lets a 2026
telemetry page and a 1961 results page talk about the same constructor.

Everything below is what goes wrong anyway. For the overall strategy see
[entity-resolution](entity-resolution.md).

## 1. Where each identifier lives

| Source | Driver key | Constructor key | Grain | Notes |
| --- | --- | --- | --- | --- |
| F1DB `f1db-races-race-results.csv` | `driverId` | `constructorId` + `engineManufacturerId` | per result row | 27,599 rows; also `tyreManufacturerId`, `sharedCar` |
| F1DB `f1db-constructors.csv` | — | `id` | per constructor | 188 rows, 22 career-total columns |
| F1DB `f1db-constructors-chronology.csv` | — | `parentConstructorId` → `constructorId` | per lineage segment | **217 data rows** |
| FastF1 `SessionResults` | `DriverId` | `TeamId` | per session entry | 22 columns, indexed by driver number |
| jolpica `/ergast/f1/{season}/constructorstandings/` | `driverId` | `constructorId` | per season-round | standings **require** a season (HTTP 400 without) |
| OpenF1 `/v1/drivers` | `driver_number` | — (`team_name` string) | per session | 12 fields; no constructor id exists |
| LiveTiming `DriverList.json` | `RacingNumber`, `Reference` | `TeamName` | per session | `Reference` e.g. `LANNOR01` |
| FastF1 `plotting/constants.json` | — | lowercase display fragment | per season | not an id space |
| formula1.com | driver ref e.g. `lannor01` | URL slug / Cloudinary slug | current | two different slug spaces |

`engineManufacturerId` is a fourth id space and it is the one that makes power-unit
analysis possible at all: it is present on every F1DB result row, so a
supplier-versus-customer rollup is a `GROUP BY` rather than a hand-maintained table.

## 2. The punctuation crosswalk

jolpica and F1DB disagree on separators for exactly the teams a modern site writes
about most. Verified against jolpica's 2026 constructor standings (11 constructors at
round 14) and F1DB v2026.14.0:

| jolpica `constructorId` | F1DB `constructorId` | formula1.com URL slug | formula1.com Cloudinary slug | FastF1 `constants.json` key |
| --- | --- | --- | --- | --- |
| `red_bull` | `red-bull` | `red-bull-racing` | `redbullracing` | `red bull` |
| `rb` | `racing-bulls` | `racing-bulls` | `racingbulls` | `racing bulls` |
| `aston_martin` | `aston-martin` | `aston-martin` | `astonmartin` | `aston martin` |
| `mercedes` | `mercedes` | `mercedes` | `mercedes` | `mercedes` |
| `ferrari` | `ferrari` | `ferrari` | `ferrari` | `ferrari` |
| `mclaren` | `mclaren` | `mclaren` | `mclaren` | `mclaren` |
| `alpine` | `alpine` | `alpine` | `alpine` | `alpine` |
| `haas` | `haas` | `haas` | `haasf1team` | `haas` |
| `williams` | `williams` | `williams` | `williams` | `williams` |
| `audi` | `audi` | `audi` | `audi` | `audi` |
| `cadillac` | `cadillac` | `cadillac` | `cadillac` | `cadillac` |

Note that jolpica's `rb` is a *display-name* problem as well as a punctuation one: it
returns the name "RB F1 Team" for 2026 while its own `url` field points at the Racing
Bulls article. Display names come from F1DB; foreign names are join material only.

A normalisation function gets you most of the way and then lies to you about the rest,
so it is a proposal step, not the mapping:

```python
# Proposes a mapping for human review. The reviewed output is committed JSON.
def propose_f1db_id(foreign_id: str) -> str:
    return foreign_id.strip().lower().replace("_", "-").replace(" ", "-")

# propose_f1db_id("red_bull")     -> "red-bull"      correct
# propose_f1db_id("aston_martin") -> "aston-martin"  correct
# propose_f1db_id("rb")           -> "rb"            WRONG: F1DB "rb" is the 2024 season only
```

That third case is the whole argument for a committed crosswalk. `rb` is a real F1DB
id — it is just not the id of the thing jolpica means by `rb` in 2026.

## 3. Lineage: the id is not the team

`f1db-constructors-chronology.csv` has header
`parentConstructorId,positionDisplayOrder,constructorId,yearFrom,yearTo` and **217 data
rows**. It is the only open dataset that encodes team continuity, and it resolves the
question a team page cannot avoid: is Racing Bulls forty years old or two?

| Lineage root | Chain (`constructorId` yearFrom–yearTo) |
| --- | --- |
| **Racing Bulls** | `minardi` 1985–2005 → `toro-rosso` 2006–2019 → `alphatauri` 2020–2023 → `rb` 2024–2024 → `racing-bulls` 2025– |
| **Aston Martin** | `jordan` 1991–2005 → `midland` 2006 → `spyker` 2007 → `force-india` 2008–2018 → `racing-point` 2019–2020 → `aston-martin` 2021– |
| **Audi** | `sauber` 1993–2005 → `bmw-sauber` 2006–2010 → `sauber` 2011–2018 → `alfa-romeo` 2019–2023 → `kick-sauber` 2024–2025 → `audi` 2026– |
| **Alpine** | `toleman` 1981–1985 → `benetton` 1986–2001 → `renault` 2002–2011 → `lotus-f1` 2012–2015 → `renault` 2016–2020 → `alpine` 2021– |
| **Mercedes** | `tyrrell` 1970–1998 → `bar` 1999–2005 → `honda` 2006–2008 → `brawn` 2009 → `mercedes` 2010– |
| **Red Bull** | `stewart` 1997–1999 → `jaguar` 2000–2004 → `red-bull` 2005– |
| **Manor** | `virgin` 2010–2011 → `marussia` 2012–2015 → `manor` 2016 |
| **Caterham** | `lotus-racing` 2010–2011 → `caterham` 2012–2014 |

The file is denormalised in a useful way: **every member of a chain appears as its own
`parentConstructorId` key pointing at the full chain**, so a lookup on any historical
name returns the whole lineage without recursion.

formula1.com uses the same convention — the Mercedes team page states "First Team
Entry 1970", i.e. Tyrrell — which is worth knowing because it means the site's lineage
model will not read as eccentric to a fan who cross-checks it.

### Lineage traps

| Trap | Detail | Consequence |
| --- | --- | --- |
| Non-contiguous id | `sauber` covers **1993–2005 and 2011–2018** | An id-only join merges two eras and silently attributes BMW-era results to the wrong segment |
| One-season id | `rb` is 2024 only | Any code that treats it as "the current Racing Bulls id" is wrong from 2025 |
| Repeated id in one chain | `renault` appears twice in the Alpine chain (2002–2011, 2016–2020) | `(id, year)` is the key, not `id` |
| Homonyms across chains | "Lotus" is three unrelated entities: Team Lotus, Lotus Racing → Caterham, and Lotus F1 (the Alpine chain) | Never resolve a constructor from a display name |

The join predicate is therefore always `constructorId = ? AND year BETWEEN yearFrom AND
yearTo`:

```sql
-- Resolve any historical constructorId to its lineage root for a given season.
SELECT c.parentConstructorId AS lineage_root
FROM   constructors_chronology c
WHERE  c.constructorId = :constructor_id
  AND  :year BETWEEN c.yearFrom AND COALESCE(c.yearTo, 9999);
```

`lineage_root` is what becomes the URL slug ([SPEC §5.1](../../../SPEC.md)); every
other member of the chain becomes an entry in `redirects.json`.

## 4. Abbreviations, numbers and membership are not identities

### 4.1 Three-letter abbreviations

The same concept appears as FastF1 `Abbreviation`, OpenF1 `name_acronym` and
LiveTiming `Tla` — all per-session broadcast labels emitted by the timing feed, not
entries in an identifier registry. 2026 alone carries `BOR` (Bortoleto), `BOT`
(Bottas) and `BEA` (Bearman), which is a fair illustration of how little headroom
three letters give across 881 drivers. Nothing in the sources consulted establishes
uniqueness across seasons, and no source publishes a historical TLA table — treat
long-run TLA uniqueness as **unverified** and never key on it. Use a TLA for display,
resolve on `DriverId`.

FastF1's `get_driver(identifier)` accepts either a three-letter code (`'VER'`) or a
driver number as a string, which is convenient interactively and precisely the habit
to avoid in pipeline code.

### 4.2 Car numbers

Car numbers are season-scoped, and 2026 shows both ways they move:

- **Lando Norris carries #1** as the reigning 2025 champion. #1 is a title flag, not
  a person.
- **Max Verstappen runs #3** in 2026.

FastF1's `SessionResults` is *indexed by driver number*. That index is a within-session
convenience and is not a stable cross-season key. Any code that uses
`results.loc['33']` or similar to mean a driver is wrong by construction.

### 4.3 Team membership

Driver-to-team membership is a **session** fact. OpenF1 `/v1/drivers?session_key=11369`
(2026 Spanish Grand Prix, race) returns 22 entries including:

| # | Acronym | `team_name` in that session |
| ---: | --- | --- |
| 30 | LAW | Red Bull Racing |
| 22 | TSU | Racing Bulls |
| 41 | LIN | Racing Bulls |
| 3 | VER | Red Bull Racing |

The declared 2026 lineup is Red Bull = Verstappen + Hadjar and Racing Bulls = Lawson +
Lindblad. The discrepancy is real: Isack Hadjar was ruled out from the Dutch Grand
Prix onward with a wrist injury, Liam Lawson was promoted to Red Bull, and Yuki
Tsunoda returned at Racing Bulls.

**Design consequence.** Key membership on `session_key`, or at minimum on
`(year, round)` — never on `(year)`. F1DB supports season granularity via
`f1db-seasons-entrants-drivers.csv`; per-race granularity comes from the race-results
table or from per-session `DriverList.json`. A team page's lineup widget should render
as a **timeline of driver stints with substitution markers**, which is both more
accurate and more interesting than a two-driver card — and it is the same Gantt
primitive the stint chart already uses
([chart archetypes](../../design/chart-archetypes.md)).

## 5. Colour is a fourth join, and its sources disagree

Three authorities, materially different values:

| Team (2026) | FastF1 `official` | FastF1 `fastf1` | LiveTiming `TeamColour` |
| --- | --- | --- | --- |
| McLaren | `#ff8000` | `#ff8000` | `F47600` |
| Ferrari | `#e80020` | `#e80020` | `ED1131` |
| Mercedes | `#27f4d2` | `#27f4d2` | `00D7B6` |
| Red Bull | `#3671c6` | `#0600ef` | `4781D7` |
| Racing Bulls | `#6692ff` | `#fcd700` | `6C98FF` |
| Aston Martin | `#229971` | `#00665f` | `229971` |
| Alpine | `#0093cc` | `#ff87bc` | `00A1E8` |
| Williams | `#64c4ff` | `#00a0dd` | `1868DB` |
| Audi | `#ff2d00` | `#ff2d00` | `F50537` |
| Haas | `#b6babd` | `#b6babd` | `9C9FA2` |
| Cadillac | `#444444` | `#444444` | `909090` |

FastF1's `plotting/constants.json` is the only source with **per-season history**,
keyed `'2018'` through `'2026'`, each team entry shaped
`{short_name, colors: {official, fastf1}}` — where `official` means "as used by F1 in
official graphics and in the TV broadcast" and `fastf1` means the team's own web brand
colour. That history matters for period-correct pages: Mercedes was `#00d2be` in 2018
and `#27f4d2` in 2026; Williams's official colour in 2018 was `#ffffff`.

Two join hazards specific to this file:

- **Its keys are lowercase display fragments, not constructor ids** — `racing bulls`,
  `red bull`, `kick sauber`, `aston martin`. They join to nothing directly and need
  their own column in the crosswalk.
- **`short_name` for `racing bulls` is `RB`**, not "Racing Bulls" — a label-rendering
  trap if you pipe `short_name` straight into a chart.

The project's rule, following [SPEC §8.3](../../../SPEC.md): pick one source, state it
on `/data/`, and then **luminance-remap every value** so brand hues hold ≥3:1 contrast
on both paper and instrument surfaces. Raw brand hex is not shippable — Haas
`#b6babd`, Cadillac `#444444` and Williams `#64c4ff` all fail against at least one of
the project's two grounds. Colour is never the sole encoding
([design tokens](../../design/design-tokens.md)).

## 6. Worked join

Given a FastF1 session and an F1DB release, produce per-entry rows keyed on F1DB ids:

```python
res = session.results          # 22 columns, indexed by driver number
entries = [
    {
        "driver_id":      CROSSWALK_DRIVERS[row.DriverId],       # Ergast slug -> F1DB id
        "constructor_id": CROSSWALK_TEAMS[row.TeamId],           # Ergast slug -> F1DB id
        "lineage_root":   resolve_lineage(CROSSWALK_TEAMS[row.TeamId], session.event.year),
        "car_number":     row.DriverNumber,   # season-scoped label
        "tla":            row.Abbreviation,   # display only
        "classified":     row.ClassifiedPosition,  # int, or R/D/E/W/F/N
    }
    for row in res.itertuples()
]
assert_resolved(entries, "constructor_id", F1DB_CONSTRUCTORS, context="session entries")
```

`ClassifiedPosition` is a string with a documented code set — an integer, or `R`
retired, `D` disqualified, `E` excluded, `W` withdrawn, `F` failed to qualify, `N` not
classified. F1DB's parallel field is `positionText`, whose non-numeric values across
the whole dataset are `DNF` 8,776, `DNQ` 1,041, `DNS` 381, `DNPQ` 338, `NC` 200, `DSQ`
161, `EX` 15, `DNP` 5. The two vocabularies are not the same and must not be unioned:
reconcile them into the project's own classification enum in the adapter, and record
that mapping alongside the reliability metric definition
([metrics](../../metrics/index.md)).

## 7. What the join cannot give you

- **OpenF1 has no constructor id.** The only bridge is `team_name` per session, which
  means the OpenF1 → F1DB team join is a per-season name mapping and needs review each
  time a team renames. Prefer to avoid needing it: OpenF1's role is
  [SPEC §6.1](../../../SPEC.md) cross-check only, and its NC-SA licence keeps its
  values out of published artifacts regardless.
- **No open source of team principals or technical directors over time.**
  formula1.com gives only the current Team Chief and Technical Chief. A historical
  leadership timeline would be hand-curated, and the research identified no
  authoritative machine-readable source — so it is either an editorial artifact with a
  named author or it does not ship.
- **Driver career totals across a rename** are a lineage question, not a join
  question, and the answer depends on the convention the site declares. State it on
  the page rather than letting the query decide silently
  ([editorial voice](../../policies/editorial-voice.md)).
