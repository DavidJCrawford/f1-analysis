---
type: Reference
title: Constructor Lineage and Identity
description: The F1DB constructor chronology chains, the rename and merge events they encode, the 2026 grid with its power unit groupings, and how lineage drives the site's permanent slug policy.
resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
tags:
  - constructors
  - identity
  - lineage
  - crosswalk
  - slugs
  - data-modelling
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_release
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 CSV release — f1db-constructors-chronology.csv and f1db-seasons-entrants-chassis.csv
  - id: jolpica_constructor_standings_2026
    resource: https://api.jolpi.ca/ergast/f1/2026/constructorstandings.json
    title: jolpica-f1 2026 constructor standings
  - id: fastf1_constants
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/plotting/constants.json
    title: FastF1 plotting constants — per-season team keys and colours
  - id: f1_teams
    resource: https://www.formula1.com/en/teams
    title: formula1.com team index
  - id: project_spec
    resource: ../../../SPEC.md
    title: F1 Analysis project specification
status: stable
---

# Constructor Lineage and Identity

A team page has to answer one question before it can render anything: **is
Racing Bulls forty years old, or two?** The answer determines the URL, the
history table, the record totals and the shape of the header.

The project takes the **continuity convention**: a constructor is a chain, and
the chain has one permanent identity. formula1.com uses the same convention —
its Mercedes team page states "First Team Entry 1970", meaning Tyrrell.

## 1. The source: `f1db-constructors-chronology.csv`

F1DB is the only open dataset that ships lineage as data rather than leaving it
to be inferred from names. Header, verbatim:

```csv
"parentConstructorId","positionDisplayOrder","constructorId","yearFrom","yearTo"
```

**217 data rows** (218 lines including the header). Against an entity population
of 214 constructors and 217 chronology rows (SPEC §4.1), this is the file that
feeds the lineage timeline.

The file's key structural property: **every member of a chain appears as its own
`parentConstructorId` key, pointing at the full chain.** A lookup keyed on any
historical name returns the complete lineage in one read, with no recursion and
no graph traversal.

```python
# lineage of any alias, in one lookup
chain = chronology[chronology.parentConstructorId == "force-india"]
# -> jordan, midland, spyker, force-india, racing-point, aston-martin
lineage_root = chain.sort_values("positionDisplayOrder").iloc[-1].constructorId
# -> 'aston-martin'
```

## 2. The chains

| Lineage root | Chain, with `yearFrom`–`yearTo` |
| --- | --- |
| **racing-bulls** | minardi 1985–2005 → toro-rosso 2006–2019 → alphatauri 2020–2023 → **rb 2024–2024** → racing-bulls 2025–present |
| **aston-martin** | jordan 1991–2005 → midland 2006 → spyker 2007 → force-india 2008–2018 → racing-point 2019–2020 → aston-martin 2021–present |
| **audi** | sauber 1993–2005 → bmw-sauber 2006–2010 → **sauber 2011–2018** → alfa-romeo 2019–2023 → kick-sauber 2024–2025 → audi 2026–present |
| **alpine** | toleman 1981–1985 → benetton 1986–2001 → **renault 2002–2011** → lotus-f1 2012–2015 → **renault 2016–2020** → alpine 2021–present |
| **mercedes** | tyrrell 1970–1998 → bar 1999–2005 → honda 2006–2008 → brawn 2009 → mercedes 2010–present |
| **red-bull** | stewart 1997–1999 → jaguar 2000–2004 → red-bull 2005–present |
| **manor** | virgin 2010–2011 → marussia 2012–2015 → manor 2016 |
| **caterham** | lotus-racing 2010–2011 → caterham 2012–2014 |

### Traps in this table

| Trap | Detail |
| --- | --- |
| **Non-contiguous ids** | `sauber` occupies **two disjoint ranges** — 1993–2005 and 2011–2018. A naive `MIN(yearFrom)`/`MAX(yearTo)` per id produces a 26-year span that includes the BMW period twice. |
| **One-season ids** | `rb` exists for exactly **2024**. A chart with a year axis must not drop a one-season era, and a label renderer must not assume eras are wide enough for text. |
| **Repeated names, different entities** | `renault` appears **twice** in the Alpine chain (2002–2011 and 2016–2020), with a Lotus era between. |
| **"Lotus" is three unrelated things** | Team Lotus; Lotus Racing → Caterham; and Lotus F1, which is a Renault-chain era. Three entities, one word. Never resolve a team by display name. |
| **Merges vs renames** | The chronology records succession, not corporate mechanism. A page that says "renamed" where a sale or merger occurred is imprecise; the neutral, accurate verb is that the entry **became** the next name. |

## 3. Slug policy

From SPEC §5.1, and this document is what implements it.

1. **Slugs derive from F1DB canonical IDs, never from display names.** Ferrari
   is `/teams/ferrari/` forever.
2. **A renamed entity resolves to its lineage root.** `/teams/aston-martin/` is
   the canonical URL for the Jordan–Midland–Spyker–Force India–Racing Point
   chain.
3. **Every historical name is a redirect alias.** `/teams/force-india/` →
   `/teams/aston-martin/`.
4. A **`redirects.json`** is generated at build time from the chronology file
   and emitted as Astro redirects. It is generated, not hand-maintained, so a
   new chronology row automatically produces a working alias.

```python
# build-time: every alias -> lineage root
redirects = {}
for root, chain in chronology.groupby("parentConstructorId"):
    canonical = chain.sort_values("positionDisplayOrder").iloc[-1].constructorId
    for member in chain.constructorId:
        if member != canonical:
            redirects[f"/teams/{member}/"] = f"/teams/{canonical}/"
```

The 2026 arrivals **Audi** and **Cadillac** are the live test of this: Audi is
the current head of the Sauber chain and inherits its aliases, while Cadillac is
a genuinely new entry with no chain behind it.

A team page header renders the chain as a **lineage ribbon** of era badges, each
in that era's own period colour, with the current name as the anchor. The ribbon
is the one place on the site where a team's full identity is visible at once.

## 4. The 2026 grid

Eleven constructors, twenty-two cars, five power unit suppliers. Entrant,
constructor, engine and chassis verbatim from
`f1db-seasons-entrants-chassis.csv`:

| Entrant | `constructorId` | `engineManufacturerId` | Chassis |
| --- | --- | --- | --- |
| aston-martin-aramco-formula-one-team | `aston-martin` | `honda` | aston-martin-amr26 |
| atlassian-williams-f1-team | `williams` | `mercedes` | williams-fw48 |
| audi-revolut-f1-team | `audi` | `audi` | audi-r26 |
| bwt-alpine-formula-one-team | `alpine` | `mercedes` | alpine-a526 |
| cadillac-formula-1-team | `cadillac` | `ferrari` | cadillac-ca01 |
| mclaren-mastercard-f1-team | `mclaren` | `mercedes` | mclaren-mcl40 |
| mercedes-amg-petronas-formula-one-team | `mercedes` | `mercedes` | mercedes-f1-w17 |
| oracle-red-bull-racing | `red-bull` | `red-bull-ford` | red-bull-rb22 |
| scuderia-ferrari-hp | `ferrari` | `ferrari` | ferrari-sf-26 |
| tgr-haas-f1-team | `haas` | `ferrari` | haas-vf-26 |
| visa-cash-app-racing-bulls-formula-one-team | `racing-bulls` | `red-bull-ford` | racing-bulls-vcarb-03 |

### Power unit groupings

| Supplier | Teams | Cars |
| --- | --- | ---: |
| **Mercedes** | Mercedes, McLaren, Williams, Alpine | 8 |
| **Ferrari** | Ferrari, Haas, Cadillac | 6 |
| **Red Bull Ford** | Red Bull, Racing Bulls | 4 |
| **Audi** | Audi (works, ex-Sauber) | 2 |
| **Honda** | Aston Martin | 2 |

Two consequences for analysis:

- **A single-customer supplier is inseparable from its team.** Honda supplies
  only Aston Martin in 2026, so "Honda PU reliability" and "Aston Martin
  reliability" are the same number. The page must say so rather than presenting
  them as independent evidence.
- **A supplier-level number can be dominated by one customer.** Across 2026
  rounds 1–14, the Ferrari power unit records 15 non-accident retirements from
  84 starts (17.9%) — of which **11 are Cadillac** (from 28 starts) and **1** is
  the works team (from 28). The supplier aggregate is misleading without the
  constructor split, and the site always shows both.

Alpine is the case that makes the engine column non-obvious: Renault is a
committed 2026 power unit manufacturer in the regulatory sense, but Alpine races
as a **Mercedes customer**, which is why five suppliers appear on the grid rather
than six.

## 5. The ID crosswalk

Five sources, five identifier schemes for the same eleven teams. This is a
committed JSON file, not a runtime inference.

| Team | F1DB | jolpica | FastF1 `constants.json` key | f1.com URL slug |
| --- | --- | --- | --- | --- |
| Red Bull | `red-bull` | `red_bull` | `red bull` | `red-bull-racing` |
| Racing Bulls | `racing-bulls` | `rb` | `racing bulls` | `racing-bulls` |
| Aston Martin | `aston-martin` | `aston_martin` | `aston martin` | `aston-martin` |
| Mercedes | `mercedes` | `mercedes` | `mercedes` | `mercedes` |
| Ferrari | `ferrari` | `ferrari` | `ferrari` | `ferrari` |
| McLaren | `mclaren` | `mclaren` | `mclaren` | `mclaren` |
| Alpine | `alpine` | `alpine` | `alpine` | `alpine` |
| Haas | `haas` | `haas` | `haas` | `haas` |
| Williams | `williams` | `williams` | `williams` | `williams` |
| Audi | `audi` | `audi` | `audi` | `audi` |
| Cadillac | `cadillac` | `cadillac` | `cadillac` | `cadillac` |

Notes on each scheme:

- **FastF1's keys are lowercase display-name fragments, not ids** — `racing
  bulls`, `red bull`, `kick sauber`. They are also **not stable across seasons**:
  the 2025 block has `kick sauber` where 2026 has `audi`.
- **FastF1's `short_name` for Racing Bulls is `RB`**, not "Racing Bulls" — a
  label renderer that trusts it will print the 2024-only name for 2026.
- **jolpica display names go stale.** Its 2026 entry for `rb` is named "RB F1
  Team" while its own `url` field points at the Racing Bulls Wikipedia article.
  Use the id, take the display name from F1DB.
- **formula1.com slugs are case-sensitive**: `/en/teams/mercedes` returns 200,
  `/en/teams/Mercedes` returns 404.

## 6. Data freshness across sources

F1DB can lag the live season by **one round**. Measured at 2026 round 14: F1DB
`f1db-seasons-constructor-standings.csv` gives Mercedes 468 points where jolpica
gives 503.

The project's rule: **jolpica for the current standings ribbon, F1DB for
everything historical and everything redistributed.** jolpica is CC BY-NC-SA and
is a build-time gap-fill only — its values are never written to a published
artifact (SPEC §6.1).

Similarly, per-team counters disagree across sources and are not shown side by
side without reconciliation. formula1.com's Mercedes page reports 3 DNFs for
2026 where F1DB gives 2 DNF/NC rows from 28 starts after excluding DNS — almost
certainly a difference in how a DNS or a classified-but-not-finished car is
counted. See [Championship edge cases](championship-edge-cases.md) for the
denominator rules the site uses.

## 7. What the site renders from lineage

| Element | Source |
| --- | --- |
| Lineage ribbon on a team page | chronology chain, one badge per era |
| Constructor lineage timeline chart | chronology + season standings, all coverage tiers |
| Permanent URL and redirect aliases | chronology, via `redirects.json` |
| Era-correct team colour | FastF1 `constants.json`, keyed by season (2018–2026 only) |
| Pre-2018 era colour | derived; there is no per-season source before 2018 |

Colour is a per-season fact, and the historical shifts are large enough to change
a chart's meaning — Mercedes' official colour moves from `#00d2be` in 2018 to
`#27f4d2` in 2026, and Williams' 2018 official colour was `#ffffff`. A page about
2018 uses 2018's colours.

Note also that team colours **collide across teams** in 2026 — Ferrari `#e80020`
against Audi `#ff2d00` — which is exactly why team colour alone never encodes a
driver on this site (SPEC §8.3).

## See also

- [Championship edge cases](championship-edge-cases.md) — two-constructor seasons, result-code denominators
- [Points systems](points-systems.md) — why constructor points are not comparable across eras
- [Cost cap and ATR](cost-cap-and-atr.md) — the modern constraints that shape these teams' performance
- [The 2026 regulation reset](regulations-2026.md) — the rules behind the 2026 grid's spread
