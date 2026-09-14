---
type: Dataset
title: OpenF1
description: The 2023-onward REST API whose 18 endpoints add overtakes, team radio and pit-lane splits that FastF1 lacks — with its free/sponsor tier split, deprecated fields and NonCommercial licence.
resource: https://api.openf1.org/v1/
tags: [openf1, rest-api, telemetry, overtakes, rate-limits, cc-by-nc-sa]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: openf1_docs
    resource: https://openf1.org/docs
    title: OpenF1 API documentation
  - id: openf1_home
    resource: https://openf1.org/
    title: OpenF1 tiers, limits and licence statement
  - id: openf1_license
    resource: https://raw.githubusercontent.com/br-g/openf1/main/LICENSE
    title: OpenF1 repository LICENSE (CC BY-NC-SA 4.0)
  - id: openf1_sessions_2026
    resource: https://api.openf1.org/v1/sessions?year=2026
    title: Live coverage check, 2026 sessions (fetched 2026-09-14)
  - id: openf1_wayback
    resource: https://web.archive.org/cdx/search/cdx?url=openf1.org&from=2025&to=2026&output=json
    title: Wayback CDX index used to date the sponsor tier
status: stable
---

# OpenF1

OpenF1 is a REST API over the same Formula 1 timing feed that FastF1 parses, exposed as
plain JSON with query-string filtering. Its role here is **build-time cross-check
only** (SPEC §6.1): it is CC BY-**NC-SA** 4.0, so nothing it returns may be written into
a published artifact, but it is the cheapest way to sanity-check a derived figure
against an independent parse of the same feed — and it carries three or four things
FastF1 does not expose at all.

| Fact | Value |
| --- | --- |
| Base URL | `https://api.openf1.org/v1/{endpoint}` |
| Endpoints | 18 |
| Formats | JSON; append `csv=true` for CSV |
| Coverage floor | **2023** |
| Licence | CC BY-NC-SA 4.0 |
| Auth | None for historical data |

## Coverage is hard-floored at 2023

Verified empirically on 2026-09-14:

| Query | Result |
| --- | --- |
| `sessions?year=2018` | `{"detail":"No results found."}` |
| `sessions?year=2023` | 118 sessions; earliest `session_key` 9222, `meeting_key` 1140, "Day 1", 2023-02-23T07:00:00+00:00 |
| `sessions?year=2026` | 131 sessions, 25 of them Races, latest ending 2026-12-06T15:00:00+00:00 at Yas Marina |

OpenF1 can therefore never back a page before 2023. It is relevant only to the
**Modern** coverage tier (SPEC §4.2) — roughly 4 seasons of 77.

## Endpoints and fields

Field lists are literal.

| Endpoint | Fields |
| --- | --- |
| `car_data` (~3.7 Hz) | `brake`, `date`, `driver_number`, `drs`, `meeting_key`, `n_gear`, `rpm`, `session_key`, `speed`, `throttle` |
| `championship_drivers` *(beta, race sessions only)* | `driver_number`, `meeting_key`, `points_current`, `points_start`, `position_current`, `position_start`, `session_key` |
| `championship_teams` *(beta)* | `meeting_key`, `points_current`, `points_start`, `position_current`, `position_start`, `session_key`, `team_name` |
| `drivers` | `broadcast_name`, `country_code`, `driver_number`, `first_name`, `full_name`, `headshot_url`, `last_name`, `meeting_key`, `name_acronym`, `session_key`, `team_colour`, `team_name` — **12 fields** |
| `intervals` | `date`, `driver_number`, `gap_to_leader`, `interval`, `meeting_key`, `session_key` |
| `laps` | `date_start`, `driver_number`, `duration_sector_1/2/3`, `i1_speed`, `i2_speed`, `is_pit_out_lap`, `lap_duration`, `lap_number`, `meeting_key`, `segments_sector_1/2/3`, `session_key`, `st_speed` |
| `location` (~3.7 Hz) | `date`, `driver_number`, `meeting_key`, `session_key`, `x`, `y`, `z` |
| `meetings` | `circuit_image`, `circuit_info_url`, `circuit_key`, `circuit_short_name`, `circuit_type`, `country_code`, `country_flag`, `country_key`, `country_name`, `date_end`, `date_start`, `gmt_offset`, `is_cancelled`, `location`, `meeting_key`, `meeting_name`, `meeting_official_name`, `year` |
| `overtakes` | `date`, `meeting_key`, `overtaken_driver_number`, `overtaking_driver_number`, `position`, `session_key` |
| `pit` | `date`, `driver_number`, `lane_duration`, `lap_number`, `meeting_key`, `pit_duration`, `session_key`, `stop_duration` |
| `position` | `date`, `driver_number`, `meeting_key`, `position`, `session_key` |
| `race_control` | `category`, `date`, `driver_number`, `flag`, `lap_number`, `meeting_key`, `message`, `qualifying_phase`, `scope`, `sector`, `session_key` |
| `sessions` | `circuit_key`, `circuit_short_name`, `country_code`, `country_key`, `country_name`, `date_end`, `date_start`, `gmt_offset`, `is_cancelled`, `location`, `meeting_key`, `session_key`, `session_name`, `session_type`, `year` |
| `session_result` | `dnf`, `dns`, `driver_number`, `dsq`, `duration`, `gap_to_leader`, `meeting_key`, `number_of_laps`, `position`, `session_key` |
| `starting_grid` | `driver_number`, `lap_duration`, `meeting_key`, `position`, `session_key` |
| `stints` | `compound`, `driver_number`, `lap_end`, `lap_start`, `meeting_key`, `session_key`, `stint_number`, `tyre_age_at_start` |
| `team_radio` | `date`, `driver_number`, `meeting_key`, `recording_url`, `session_key` |
| `weather` | `air_temperature`, `date`, `humidity`, `meeting_key`, `pressure`, `rainfall`, `session_key`, `track_temperature`, `wind_direction`, `wind_speed` |

## What OpenF1 has that FastF1 does not

| Capability | Where |
| --- | --- |
| Overtakes as discrete events, with both driver numbers and the position taken | `overtakes` |
| Pit **lane** time vs **stop** time as separate quantities | `pit.lane_duration` vs `pit.stop_duration` |
| Explicit DNF / DNS / DSQ flags | `session_result.dnf/dns/dsq` |
| Starting grid as its own table | `starting_grid` |
| Team radio audio | `team_radio.recording_url` |
| Circuit artwork and info links | `meetings.circuit_image`, `meetings.circuit_info_url` |

The `overtakes` endpoint is a cross-check, not a source: this site counts overtakes by
the published de Groote (2021) definition, implemented once and tested against a golden
fixture (SPEC §7). An independent count is useful precisely because it will sometimes
disagree — that disagreement is a signal about lapping/unlapping handling.

`meetings.circuit_image` and `drivers.headshot_url` sit on F1's own CDN. Neither is
hotlinked nor rehosted.

## Deprecations with hard expiry

| Field | Status |
| --- | --- |
| `drivers.country_code` | Deprecated — "This field will be removed at the end of the 2026 season." |
| `pit.pit_duration` | Deprecated — same wording |
| `championship_drivers`, `championship_teams` | Flagged **beta** |

`pit_duration` is the obvious field for a pit-stop visualisation and has a dated
expiry, so any pit chart is built on `lane_duration` and `stop_duration` instead.
`country_code` must not back a nationality-flag feature.

## Mini-sector segment codes

The `segments_sector_1/2/3` arrays carry integer status codes per mini-sector.

| Code | Meaning |
| --- | --- |
| 0 | not available |
| 2048 | yellow sector |
| 2049 | green sector |
| 2050 | unknown |
| 2051 | purple sector |
| 2052 | unknown |
| 2064 | pitlane |
| 2068 | unknown |

Confidence on this mapping is **medium** — it comes from OpenF1's docs plus community
reverse-engineering, only 2048 and 2049 appeared in the race lap sampled, and OpenF1
itself notes that segments "are not available during races" and may not match the TV
colours. The array *lengths*, however, are reliable and useful: they give the
mini-sector count per timing sector, which is the input to the sector-boundary
derivation described in [MultiViewer API](multiviewer-api.md).

## The `location` endpoint is not a geometry source

OpenF1's own docs state the origin `(0, 0, 0)` "appears to be arbitrary and not tied to
any specific location on the track", that the data "lacks details about lateral
placement", and that it "cannot distinguish whether cars are on the left or right side
of the track". The 1/10 m scale is an *empirical* finding, documented on FastF1's side
but not on OpenF1's.

Measured, Spa 2024 (`session_key=9574`, `driver_number=1`, a two-minute window, 465
samples): `z` spans 3655 → 4678 raw units = **365.5 m → 467.8 m**, a 102.3 m delta
matching Spa's real elevation change, with 358 distinct `z` values. Inter-sample
spacing is median 0.24 s, min 0.02 s, max 0.50 s — **not uniform**, so resample before
use. See [elevation and DEM sources](elevation-dem.md) for how that Z is used.

Query form (encode `>` and `<` as `%3E` / `%3C`):

```
GET https://api.openf1.org/v1/location?session_key=9574&driver_number=1
    &date>2024-07-28T14:00:00&date<2024-07-28T14:02:00
```

## Filtering

Any non-array attribute is filterable in the query string, including comparison
operators:

```
?session_key=9222&driver_number=55&is_pit_out_lap=true&lap_duration>=120
?date_start>=2023-09-01&date_end<=2023-09-30
```

Date values accept anything `dateutil.parser.parse` handles. `meeting_key` and
`session_key` both accept the literal value `latest`. Append `csv=true` for CSV.

## Tiers, limits and the live paywall

| Tier | Price | Limits | Includes |
| --- | --- | --- | --- |
| **Community** | €0/month, forever | 3 req/s, 30 req/min | All 18 endpoints, all historical sessions since 2023, JSON and CSV, "No API keys, no credit cards, and no signup required" |
| **Sponsor** | €9.90/month, personal use | 6 req/s, 60 req/min, up to 10 concurrent MQTT/WebSocket connections | Live data during sessions via REST, MQTT and WebSocket |

"Data is considered live from 30 minutes before a session starts until 30 minutes after
it ends. Outside of this window, data is classified as historical and is free to
access." Live latency is stated as "about 3 seconds after live events".

A build that runs more than 30 minutes after the chequered flag pays nothing — and this
site's ingest runs hours later, by design. The paywall is therefore irrelevant to the
project, which is worth stating because it is the first thing a reader assumes is a
blocker.

The sponsor tier launched between **2026-01-17 and 2026-02-11**: Wayback snapshots of
openf1.org at 20250611, 20251006, 20251214 and 20260117 contain no occurrence of "9.90"
or "Sponsor"; the 20260211162339 snapshot is the first that does. It is recorded here as
evidence of the direction of travel — assume more of the surface may move behind a tier.

## Licence

The repository LICENSE file is verbatim "Attribution-NonCommercial-ShareAlike 4.0
International"; the site footer reads "Licensed under CC BY-NC-SA 4.0"; the FAQ states
OpenF1 "is intended for educational purposes, personal learning projects, research, and
non-commercial fan engagement."

Same consequence as [jolpica-f1](jolpica-f1.md): ShareAlike would infect any published
dataset derived from it, so OpenF1 values never reach a build artifact. The boundary is
enforced in the pipeline — an OpenF1 response may be compared against a computed figure
and may cause a build to fail, but it may not be the figure.
