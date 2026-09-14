---
type: Reference
title: Race and Session Identity Joins
description: Binding a race to its sessions across F1DB, jolpica, FastF1 and OpenF1 — why season plus round is not a stable key, how meeting_key and session_key are mapped positionally, and where the 2026 calendar breaks naive schedule alignment.
tags: [races, sessions, schedule, joins, identifiers, timezones]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_csv
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 CSV bundle — f1db-races.csv (1,172 rows)
  - id: fastf1_events
    resource: https://docs.fastf1.dev/events.html
    title: FastF1 event schedule reference and supported seasons
  - id: fastf1_api_src
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
    title: FastF1 _api.py — base URLs, make_path, stream filename table
  - id: openf1_sessions_2026
    resource: https://api.openf1.org/v1/sessions?year=2026
    title: OpenF1 sessions for 2026 (session_key, is_cancelled)
  - id: jolpica_differences
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/ergast_differences.md
    title: jolpica-f1 documented divergences from Ergast
status: stable
---

# Race and Session Identity Joins

A race page needs one row from F1DB, some number of sessions from FastF1, and — for
2023 onward — an OpenF1 meeting and its sessions for cross-checking. Those three
sources identify the same weekend three different ways, and the obvious bridge,
`(season, round)`, is not stable. This document fixes the resolution order and
enumerates the places the 2026 calendar breaks it.

Entity strategy is in [entity-resolution](entity-resolution.md); the circuit half of
the join is in [circuits-crosswalk](circuits-crosswalk.md).

## 1. The key spaces

| Source | Race / weekend key | Session key | Grain |
| --- | --- | --- | --- |
| **F1DB** `f1db-races.csv` | `id`, plus `(year, round)` and `grandPrixId` | session columns on the race row | one row per Grand Prix (1,172) |
| **jolpica** | `(season, round)` | session named in the path (`laps`, `pitstops`, `qualifying`, `sprint`) | ordinal |
| **FastF1** | `(year, gp, identifier)`; `EventSchedule.RoundNumber` | `Session1`–`Session5` + `Session1Date`–`Session5Date` | event + 5 session slots |
| **FastF1** internals | `api_path` | path segment | live-timing archive directory |
| **OpenF1** | `meeting_key` (int) | `session_key` (int) | opaque, source-local |
| **LiveTiming** | `SessionInfo.json` `Meeting.Key`, `Meeting.Number` | directory path | per session |

F1DB models the whole weekend on **one wide row**. `f1db-races.csv` carries
`id, year, round, date, time, grandPrixId, officialName, qualifyingFormat,
sprintQualifyingFormat, circuitId, circuitLayoutId, circuitType, direction,
courseLength, turns, laps, distance, scheduledLaps, scheduledDistance,
driversChampionshipDecider, constructorsChampionshipDecider`, then date/time pairs for
`preQualifying`, `freePractice1`–`freePractice4`, `qualifying1`, `qualifying2`,
`qualifying`, `sprintQualifying`, `sprintRace` and `warmingUp`, plus
`sprintRaceLaps`, `sprintRaceDistance`, `sprintRaceScheduledLaps` and
`sprintRaceScheduledDistance`.

Two of those columns are editorially valuable and exist nowhere else:
`driversChampionshipDecider` and `constructorsChampionshipDecider` — which race
settled the title. `scheduledLaps` versus `laps` is the other: it is how a shortened
race is detectable without prose.

## 2. `(season, round)` is not a stable key

Round numbers are assigned by the source, and sources disagree when a round is
cancelled.

2026 had two rounds cancelled — OpenF1 meetings **1282** (Bahrain Grand Prix, Sakhir,
2026-04-10) and **1283** (Saudi Arabian Grand Prix, Jeddah, 2026-04-17). F1DB simply
omits them and renumbers: its 2026 season runs Australia, China, Japan, then **Miami
as round 4**. OpenF1 keeps them and flags them.

The reconciliation:

| Source | 2026 count |
| --- | ---: |
| OpenF1 `/v1/sessions?year=2026` | 131 sessions, of which 25 are Races |
| of those race sessions | 2 carry `is_cancelled: true` |
| F1DB `f1db-races.csv` 2026 rows | 23 |

25 − 2 = 23. That arithmetic is a CI check, not a footnote.

**`is_cancelled` is only on `/v1/sessions`, not on `/v1/meetings`.** A pipeline that
reads the meetings endpoint alone silently treats Sakhir and Jeddah as real rounds.

### Resolution order for a race

1. `(year, grandPrixId)` from F1DB — stable across renumbering, and the basis of the
   URL slug.
2. Date — for cross-source matching, since every source carries one.
3. `(year, round)` — **only** within a single source, never across two.

`grandPrixId` is also what distinguishes the two 2026 Spanish rounds:
`barcelona-catalunya` (round 7) and `spain` (round 14). They are separate Grands Prix
that happen to share a country, and a country-keyed join merges them.

## 3. FastF1's event schedule

`fastf1.get_session(year, gp, identifier=None, *, backend=None, exact_match=False)`
takes `backend` as one of `'fastf1'`, `'f1timing'` or `'ergast'`:

| Backend | Coverage | Notes |
| --- | --- | --- |
| `fastf1` | 2018 → now | Default, with automatic fallback |
| `f1timing` | 2018 → now | Sessions without timing data are not listed |
| `ergast` | 1950 → now | No local times, no `F1ApiSupport` flag; **always used for seasons before 2018** |

`EventSchedule` columns: `RoundNumber` (int; **testing = 0**), `Country`, `Location`,
`OfficialEventName`, `EventName`, `EventDate`, `EventFormat`, `Session1`–`Session5`,
`Session1Date`–`Session5Date` (tz-aware local, **not available on the ergast
backend**), `Session1DateUtc`–`Session5DateUtc` (naive UTC), and `F1ApiSupport` (bool).

`EventFormat` takes one of `conventional`, `sprint`, `sprint_shootout`,
`sprint_qualifying`, `testing`. The format vocabulary has a history that is itself a
join hazard: `sprint` 2021–2022, `sprint_shootout` 2023, `sprint_qualifying` 2024
onward. jolpica renamed the same sessions on its own schedule — the 2023 Sprint
Shootout and the 2024-onward Sprint Qualifying were both previously labelled
`SecondPractice` in Ergast's vocabulary.

Two gates on this table matter operationally:

- **`F1ApiSupport` gates whether laps or telemetry can be loaded at all.** It is the
  mechanical input to the coverage tier ([SPEC §4.2](../../../SPEC.md)), alongside the
  1996 and 2018 year boundaries.
- **Pre-2018 session times are back-calculated.** FastF1 documents that only the race
  date and time are real for earlier seasons; every other session is derived assuming
  a conventional Friday/Saturday/Sunday weekend, and "these assumptions will be
  incorrect for certain events". Archival-tier pages therefore show a race date and
  **no session schedule**, because the alternative is publishing a fabricated
  timetable — a direct application of honest absence
  ([SPEC §3](../../../SPEC.md), principle 3).

Testing events are supported from 2020 only, and not at all on the ergast backend.

## 4. Mapping OpenF1 keys

`meeting_key` and `session_key` are OpenF1-local integers with no external equivalent.
They are mapped positionally on

```
(year, circuit_key, session_type, date_start)
```

and the result is committed as `session-key-map.json`
([entity-resolution](entity-resolution.md) §3). The mapping must be injective: two
session keys resolving to one F1DB race and session type is a bug unless the weekend
legitimately holds two sessions of that type.

Worked example — the 2026 Spanish Grand Prix at Madrid:

| Thing | Value |
| --- | --- |
| OpenF1 `meeting_key` | 1294 |
| OpenF1 race `session_key` | 11369 |
| OpenF1 qualifying `session_key` | 11365 |
| LiveTiming `Meeting.Key` / `Meeting.Number` | 1294 / 14 |
| LiveTiming `Circuit.Key` / `ShortName` | 153 / `Madring` |
| F1DB | round 14, `grandPrixId=spain`, `circuitId=madring` |

OpenF1's `sessions` endpoint carries `session_key, session_type, session_name,
date_start, date_end, meeting_key, circuit_key, circuit_short_name, country_key,
country_code, country_name, location, gmt_offset, year, is_cancelled` — enough to do
the positional match without touching any other endpoint.

### OpenF1 quirks that bite a resolver

- **`starting_grid` is keyed to the qualifying session.** Querying it with the race
  `session_key` 11369 returns 404; querying by `meeting_key` 1294 works.
- **An unsupported `limit` parameter returns 404, not a clean error.**
  `/v1/stints?session_key=11369&limit=1` returns "No results found" while the same URL
  without `limit` returns data. Do not add pagination parameters speculatively.
- `meeting_key` and `session_key` both accept the literal value `latest` — useful
  interactively, never in a build.
- OpenF1 has **no standings endpoint**: `/v1/constructor_standings`,
  `/v1/championship_standings` and `/v1/standings` all 404. Standings come from F1DB,
  with jolpica for the current-season ribbon.

OpenF1 covers 2023 onward only — `?year=2018` returns `{"detail":"No results found."}`
— so it can never back a pre-2023 page, and its role is
[SPEC §6.1](../../../SPEC.md) cross-check at build time.

## 5. The live-timing archive path

FastF1 constructs the archive directory from the event and session names:

```
/static/{YYYY}/{wdate}_{Weekend_Name}/{sdate}_{Session_Name}/
```

with spaces replaced by underscores, against `base_url = "https://livetiming.formula1.com"`.
This is a **name-derived path**, which makes it the most fragile join in the stack: it
breaks whenever F1's own naming or dating of a session differs from the schedule. FastF1
carries hardcoded fixups for exactly that reason, including Brazil
`2024-11-03_Qualifying` → `2024-11-02_Qualifying`, and pre-season testing
`2025-02-26_Practice_1` → `2025-02-26_Day_1` and `2026-02-11_Practice_1` →
`2026-02-11_Day_1`.

The directory index is blocked — `Index.json` returns 403 — but every individual named
stream returns 200 without authentication. Measured on the 2024 British Grand Prix
race session:

| Stream | Bytes |
| --- | ---: |
| `Position.z.jsonStream` | 7,914,755 |
| `CarData.z.jsonStream` | 7,302,595 |
| `TimingData.jsonStream` | 5,589,783 |
| `TimingAppData.jsonStream` | 87,867 |
| `WeatherData.jsonStream` | 21,009 |
| `RaceControlMessages.jsonStream` | 19,620 |
| `DriverList.jsonStream` | 12,697 |
| `TeamRadio.jsonStream` | 6,031 |
| `LapCount.jsonStream` | 1,621 |
| `SessionInfo.jsonStream` | 490 |
| `SessionStatus.jsonStream` | 174 |
| `TrackStatus.jsonStream` | 52 |

≈ 21.0 MB per race session, roughly 1.5–2 GB for a full season across all sessions.
Raw streams are never committed ([SPEC §6.5](../../../SPEC.md)); only derived,
downsampled artifacts are.

`SessionInfo.jsonStream` is the cheapest authoritative join probe on the archive at
490 bytes: it carries `Meeting.Key`, `Meeting.Number`, `Circuit.Key` and
`Circuit.ShortName` for the session whose directory you just constructed, so a
successful fetch both validates the path and yields the integer keys.

## 6. jolpica's race and session shape

Base `https://api.jolpi.ca/ergast/f1/`, with `(season, round)` in the path:
`/{season}/{round}/laps/`, `/{season}/{round}/pitstops/`, `/{season}/qualifying/`,
`/{season}/{round}/results/`.

| Constraint | Behaviour |
| --- | --- |
| `limit` | default 30, **maximum 100**, larger values **silently clamped** with HTTP 200 |
| Paging | read `MRData.total`, never the requested limit |
| Standings | **require a season** — `/ergast/f1/driverstandings/` returns HTTP 400, `/ergast/f1/2026/driverstandings/` returns 200 |
| Duplicate filters | last one wins, where Ergast returned 400 |
| Format | JSON only; XML unsupported |
| Path suffix | documented as requiring `/` or `.json`; in practice a bare path also resolves |
| User-Agent | a documented policy request, not enforced — requests without a custom UA return 200 |
| Rate limits | 4 req/s burst, 500 req/hr sustained, documented as likely to **decrease** |

The paging arithmetic is why bulk history does not come from the live API: a single
race's `laps` endpoint reports `total = 921`, i.e. ~10 paged requests for one race's
lap times, against a 500 req/hr ceiling. jolpica is a volunteer project with an
explicit no-uptime-and-no-correctness disclaimer; it belongs behind a cache, at build
time, for the current season only ([SPEC §6.1](../../../SPEC.md)).

## 7. Time

Session times are stored as **UTC with an explicit circuit timezone** and always
rendered with a visible label ([SPEC §12.3](../../../SPEC.md)). Otherwise every
schedule on the site is subtly wrong, and the failure is invisible until a reader in
another hemisphere notices.

The inputs are inconsistent enough to force the policy:

- FastF1 gives both `SessionNDate` (tz-aware local) and `SessionNDateUtc` (naive UTC),
  and **the local column is absent on the ergast backend**.
- OpenF1 gives `date_start` / `date_end` plus a `gmt_offset` string.
- F1DB gives separate `date` and `time` columns per session.
- LiveTiming timestamps inside `jsonStream` records are session-relative:
  each line is a 12-character `HH:MM:SS.mmm` prefix followed by JSON.

Store UTC; keep the offset as data, not as a formatting side effect.

## 8. Tier assignment

Coverage tier is a first-class field on every race record and it selects the page
template ([SPEC §4.2](../../../SPEC.md)). It is derived during this join, from what
actually resolved rather than from the year alone:

| Tier | Years | Resolution requirement |
| --- | --- | --- |
| Archival | 1950–1995 | F1DB race row only |
| Timing | 1996–2017 | + lap-by-lap times and positions, pit stops |
| Telemetry | 2018–2022 | + a FastF1 session with `F1ApiSupport` true and a resolvable `api_path` |
| Modern | 2023–2026 | + a mapped OpenF1 `session_key` |

A 2019 race whose archive path does not resolve is a **timing-tier** page, not a
broken telemetry-tier page. Degrading the tier is the correct response to a failed
join on an optional source; failing the build is the correct response to a failed join
on a required one.

## 9. Freshness and the amendment window

The ingest is a weekly human-run publication, not a build
([SPEC §12.2](../../../SPEC.md)): GitHub-hosted runners cannot reach the live-timing
archive, the free jolpica dump is 14 days delayed, and stewards retroactively amend
results for days after a race. F1DB can also lag the live season by a round — at 2026
round 14, jolpica had Mercedes on 503 points while the then-current F1DB release had
468.

Three fields fall out of that and are carried on the race record:

| Field | Meaning |
| --- | --- |
| `data_as_of` | timestamp of the ingest that produced the page's numbers |
| `provisional` | true inside the amendment window — renders a designed "provisional classification" state |
| `sources_used` | which source supplied which block, for the per-page provenance line |

## 10. Probes

| Probe | Expected |
| --- | --- |
| OpenF1 2026 race sessions | 25, of which 2 have `is_cancelled: true` |
| F1DB 2026 race rows | 23 |
| OpenF1 meeting 1294 | maps to F1DB 2026 round 14, `grandPrixId=spain` |
| OpenF1 session 11369 | session_type Race, `circuit_key` 153 |
| `/ergast/f1/driverstandings/` | HTTP 400 |
| `/ergast/f1/2026/driverstandings/` | HTTP 200 |
| Every F1DB race 2018+ | either a resolvable FastF1 `api_path` or an explicit tier downgrade |
| `session-key-map.json` | injective |
