---
type: Reference
title: Entity Resolution Across Five Sources
description: The five-source identifier problem — which joins are free, which are hand-built, and how the pipeline enforces that every foreign record resolves to an F1DB id before it can be published.
tags: [entity-resolution, joins, identifiers, crosswalk, build-pipeline, data-modelling]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_release
    resource: https://api.github.com/repos/f1db/f1db/releases/latest
    title: F1DB v2026.14.0 release metadata (published 2026-09-13)
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API reference — Session, Laps, Telemetry, SessionResults
  - id: jolpica_docs
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md
    title: jolpica-f1 endpoint documentation
  - id: openf1_docs
    resource: https://openf1.org/docs
    title: OpenF1 API documentation — 18 endpoints and their fields
  - id: mvapi_source
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/mvapi/api.py
    title: FastF1 MultiViewer API client (host, headers, route shape)
status: stable
---

# Entity Resolution Across Five Sources

Five sources, five identifier schemes, and no two of them agree on what a thing is
called. This document states the problem precisely, classifies the joins by how hard
they are, and fixes the resolution strategy that the other three documents in this
folder implement for [drivers and teams](drivers-and-teams.md),
[circuits](circuits-crosswalk.md) and [sessions and races](sessions-and-races.md).

The governing rule, from [SPEC §6.1](../../../SPEC.md): **every source is confined to a
declared role, and the boundary is enforced in the pipeline, not by good intentions.**
Entity resolution is where that rule is actually cashed out, because a join is the
moment one source's values enter another source's record.

## 1. The identifier inventory

| Source | Driver | Constructor | Circuit | Race / session | Key type |
| --- | --- | --- | --- | --- | --- |
| **F1DB** v2026.14.0 | `driverId` slug | `constructorId` slug | `circuitId` slug + `circuitLayoutId` | race `id`, `year`, `round`, `grandPrixId` | slug |
| **FastF1** 3.8.3 | `DriverId` (= Ergast `driverId`) | `TeamId` (= Ergast `constructorId`) | `session_info` circuit key (int) | `(year, gp, identifier)`, `api_path` | mixed |
| **jolpica-f1** | `driverId` | `constructorId` | `circuitId` | `season` + `round` | slug + ordinal |
| **OpenF1** | `driver_number` only | `team_name` string only | `circuit_key` (int) + `circuit_short_name` | `meeting_key`, `session_key` (int) | opaque int |
| **MultiViewer** | — | — | `circuitKey` (int) | `meetingKey`, `raceDate`, `round` | opaque int |
| **bacinger/f1-circuits** | — | — | `cc-year` slug | — | slug |
| **F1DB plotting/colour (FastF1 `constants.json`)** | — | lowercase display fragment | — | season string key | display name |

Two of those cells are the whole problem. **OpenF1 has no constructor identifier at
all** — a team is a free-text `team_name` plus a `team_colour` hex — and **MultiViewer
has no entity identifiers except an integer circuit key.** Everything that crosses
into those sources crosses on a name or an integer whose provenance nobody publishes.

## 2. The three join classes

### Class A — free joins (Ergast-style slugs)

FastF1's `SessionResults` documents `DriverId` as the "driverId that is used by the
Ergast API" and `TeamId` as the "constructorId that is used by the Ergast API".[^1]
Those are the same slugs jolpica serves and the same shape F1DB uses, so
FastF1 ↔ jolpica ↔ F1DB joins on driver and constructor are nearly free.

Nearly. The punctuation differs — jolpica writes `red_bull`, `rb`, `aston_martin`;
F1DB writes `red-bull`, `racing-bulls`, `aston-martin` — so even class A needs a
committed mapping table. See [drivers-and-teams](drivers-and-teams.md) §2.

### Class B — opaque integer joins

`circuit_key` is consistent across MultiViewer (`circuitKey`), OpenF1 (`circuit_key`)
and FastF1's `session_info`: **63 = Sakhir** in all three. That consistency is
observed, not documented, and it is the only bridge to MultiViewer geometry.
`meeting_key` and `session_key` are OpenF1-local integers with no external equivalent
at all and must be mapped positionally — by `(year, circuit_key, session_type,
date_start)`. See [sessions-and-races](sessions-and-races.md) §4.

### Class C — no key exists

Circuit **layouts** have no cross-source identifier. F1DB is the only source that
models them (`f1db-circuits-layouts.csv`, 160 rows, header
`id,circuitId,effective,length,turns` — no geometry). MultiViewer serves geometry
under a circuit key with **no layout discriminator whatsoever**, and ignores the year
in its own route. bacinger uses its own `cc-year` slugs. Binding *"this race ran on
this layout, whose geometry is this centreline"* is therefore hand work, once per
layout, and it is the single largest resolution cost in the project.

## 3. Resolution strategy

Four rules, in force order.

1. **F1DB is the identity spine.** Every entity that gets a page has an F1DB id, and
   that id is the URL slug ([SPEC §5.1](../../../SPEC.md) slug policy). No other
   source's identifier ever reaches a route.
2. **Every foreign source gets an adapter that emits F1DB ids.** Adapters are the
   only code permitted to see a foreign identifier. Downstream stages see F1DB ids or
   nothing. This is also what keeps the NC-SA licence boundary enforceable: an
   adapter that maps jolpica rows into F1DB ids is also the chokepoint where you
   assert that no jolpica *value* is written to a published artifact.
3. **Crosswalks are committed data, never runtime inference.** Fuzzy matching at
   build time is allowed only to *propose* a mapping for human review; the reviewed
   result is a checked-in JSON file. Nothing in the published site does string
   similarity.
4. **An unresolved key fails the build.** Not a warning, not a null. A row whose
   foreign key does not resolve to an F1DB id stops the pipeline, because the
   alternative — a silently dropped or silently misattributed record — is exactly the
   class of error that the [quality gates](../../../SPEC.md) exist to catch.

### Build artifacts

| Artifact | Grain | Provenance | Verification |
| --- | --- | --- | --- |
| `circuit-layout-registry.json` | one row per F1DB `circuitLayoutId` | hand-verified once per layout | regression-tested; named in [SPEC §6.3](../../../SPEC.md) |
| `constructor-id-crosswalk.json` | one row per F1DB `constructorId` | derived + reviewed | every 2026 entrant resolves in all sources |
| `driver-id-crosswalk.json` | one row per F1DB `driverId` | derived + reviewed | number and TLA held per season, not per driver |
| `session-key-map.json` | one row per OpenF1 `session_key` (2023+) | derived from `(year, circuit_key, session_type, date_start)` | round-trips to an F1DB race id |
| `redirects.json` | one row per historical slug | derived from lineage | emitted as Astro redirects ([SPEC §5.1](../../../SPEC.md)) |

The last one is not strictly a join artifact but it is produced by the same lineage
resolution, so it is generated in the same pass.

## 4. Field-level source authority

Resolution is not only "which row matches which row" — it is also "when two matched
rows disagree, who wins". Disagreements are real and routine.

| Field | Authority | Why |
| --- | --- | --- |
| Entity identity, names, lineage | F1DB | Only CC BY 4.0 comprehensive source; only one modelling layouts and chronology |
| Results, grid, points, standings 1950–2026 | F1DB | Redistributable; models shared drives, half points, countback |
| Retirement cause, laps-down margin, 2024–2026 | **F1DB only** | jolpica returns only `Finished / Lapped / Retired / Did not start / Disqualified` for these seasons; F1DB keeps 20 distinct causes in 2026 |
| Lap times, sectors, stints, tyres, track status 2018+ | FastF1 | Parsed from the F1 timing archive |
| Car and position telemetry 2018+ | FastF1 | Only source |
| Track centreline geometry | MultiViewer (**blocked**, [SPEC §13.3](../../../SPEC.md)) → bacinger + TUMFTM + telemetry | Best available is not cleared for use |
| Stationary pit time | LiveTiming `PitStopSeries.jsonStream` | Only free source carrying stationary *and* lane time in one record |
| Team colour | one source, declared once | The three sources disagree; see [drivers-and-teams](drivers-and-teams.md) §5 |
| Current-season standings ribbon | jolpica (build-time) | F1DB can lag the live season by a round |

The retirement-cause row is a correctness trap, not a preference. jolpica's own docs
describe the collapse as beginning with the 2025 season; the live API is already
collapsed for 2024, and spot checks of individual 2023 rounds return the same reduced
set. Treat **2023 onward as unusable from jolpica for cause-of-retirement and
laps-down**, and take both fields from F1DB `reasonRetired` / `gapLaps`. The global
`/status/` endpoint still enumerates 136 historical statuses, but they only populate
results through 2022.

## 5. Failure modes this design is built against

| # | Failure | How it shows up | Guard |
| --- | --- | --- | --- |
| 1 | Identifier reuse | F1DB `sauber` covers 1993–2005 **and** 2011–2018; a naive id-keyed join merges two eras | Join on `(constructorId, year)` against the chronology, never on id alone |
| 2 | One-season identifiers | F1DB `rb` exists for 2024 only | Lineage resolution before page generation |
| 3 | Name ≠ place | 2026 meeting 1308 is named *Bahrain Grand Prix*, `country_name` *Bahrain*, held at Sepang, Kuala Lumpur | Never derive a circuit from a race name or a country from a meeting name |
| 4 | Ordinal drift | Round numbers shift when rounds are cancelled | Resolve races by `(year, grandPrixId)` or by date, not by round |
| 5 | Silent clamping | jolpica clamps `limit` above 100 with HTTP 200 and no error | Page on `MRData.total`, never on the requested limit |
| 6 | Stale display names | jolpica returns constructor name "RB F1 Team" for 2026 while its own `url` points at the Racing Bulls article | Display names come from F1DB; foreign names are join material only |
| 7 | Ignored route parameters | MultiViewer `/circuits/63/2025` returns a payload stamped `year: 2022` | Cache by circuit key; detect layout change yourself |
| 8 | Session-scoped membership | Driver-to-team is not a season fact | Key membership on session, or at minimum `(year, round)` |
| 9 | Deprecated fields | OpenF1 `drivers.country_code` and `pit.pit_duration` are documented as removed at the end of the 2026 season | No feature depends on a field with an announced expiry |

## 6. The resolution pass, in order

```text
1. load F1DB release (pinned tag)          -> the id universe
2. resolve constructor lineage             -> lineage roots + redirects.json
3. build constructor / driver crosswalks   -> reviewed JSON, committed
4. resolve circuit layouts                 -> circuit-layout-registry.json
5. map OpenF1 meeting/session keys         -> session-key-map.json
6. adapt FastF1 sessions onto F1DB races   -> per-race derived artifacts
7. assert: zero unresolved foreign keys    -> else fail the build
```

Steps 3 and 4 are the ones with a human in the loop. Everything else is mechanical
and must stay mechanical, because a pipeline that needs judgement every week is a
pipeline that will be skipped in the 72-hour window after a race
([SPEC §12.2](../../../SPEC.md)).

### The assertion in step 7

```python
def assert_resolved(rows, key, crosswalk, *, context):
    """Fail loudly. A join miss is a correctness bug, not a data gap."""
    missing = sorted({r[key] for r in rows if r[key] not in crosswalk})
    if missing:
        raise SystemExit(
            f"{context}: {len(missing)} unresolved {key} value(s): "
            + ", ".join(missing[:20])
        )
```

The distinction that matters: **an unresolved key is different from an absent
value.** "This 1961 race has no lap data" is honest absence and gets designed copy
([SPEC §3](../../../SPEC.md), principle 3). "This constructor id matched nothing" is a
bug and gets a red build.

## 7. Testing

- **Golden fixtures.** One hand-verified race per coverage tier, with the expected
  resolved ids for every driver, constructor, circuit, layout and session written out
  by hand. Any change to a crosswalk that moves a fixture fails CI.
- **Totality.** Every F1DB race row resolves to a circuit layout; every F1DB result
  row resolves to a constructor lineage root; every 2023+ OpenF1 session resolves to
  an F1DB race or is explicitly listed as cancelled.
- **Bijectivity where claimed.** `session-key-map.json` must be injective —
  two OpenF1 session keys mapping to one F1DB race is a mapping bug unless the race
  legitimately has two sessions of that type.
- **Known-answer probes.** `circuit_key 63 → sakhir`; `circuit_key 153 → madring`;
  F1DB 2026 round 16 `grandPrixId=bahrain` resolves to `circuitId=sepang`.

Cross-source count reconciliations are cheap and catch a surprising amount. For 2026:
OpenF1 lists 25 race sessions, two of which carry `is_cancelled: true`; F1DB carries
23 race rows for the same season. 25 − 2 = 23 is the check.

## 8. What this costs

Class A joins are an afternoon. Class B is a day plus a cache. Class C — the circuit
layout registry — is the one genuinely expensive item, roughly 160 hand verifications,
and it is why [SPEC §16](../../../SPEC.md) puts "build the circuit-layout registry" in
Phase 0 rather than leaving it to the phase that needs the geometry. The registry is
also the artifact most likely to rot: circuits get relaid, and a relay that is not
noticed silently misattributes lap records to the wrong geometry. It carries its own
regression tests for that reason.

[^1]: FastF1 `SessionResults` has **22** always-present columns, indexed by driver
number: `DriverNumber, BroadcastName, Abbreviation, DriverId, TeamName, TeamColor,
TeamId, FirstName, LastName, FullName, HeadshotUrl, CountryCode, Position,
ClassifiedPosition, GridPosition, Q1, Q2, Q3, Time, Status, Points, Laps`. There is no
`DriverColor` column — older write-ups that list 23 columns are counting one that does
not exist. Source: [`fastf1.core`](https://docs.fastf1.dev/core.html).
