---
type: Dataset
title: jolpica-f1
description: The Ergast successor API covering 1950–2026 — its endpoints, hard limits, CSV dumps, NonCommercial licence, and the status collapse that makes it unsafe for retirement-cause analysis in recent seasons.
resource: https://api.jolpi.ca/ergast/f1/
tags: [jolpica, ergast, historical, rest-api, rate-limits, cc-by-nc-sa]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: jolpica_docs
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/README.md
    title: jolpica-f1 API documentation
  - id: jolpica_rate_limits
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/rate_limits.md
    title: jolpica-f1 rate limits
  - id: jolpica_differences
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/ergast_differences.md
    title: jolpica-f1 — differences from Ergast
  - id: jolpica_dumps
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/database_dumps.md
    title: jolpica-f1 database dumps
  - id: jolpica_terms
    resource: https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md
    title: jolpica-f1 terms of use and licence
  - id: jolpica_dump_endpoint
    resource: https://api.jolpi.ca/data/dumps/download/
    title: Live dump manifest (fetched 2026-09-14)
status: stable
---

# jolpica-f1

jolpica-f1 is the maintained successor to the Ergast Motor Racing Developer API. On
this site its role is narrow and enforced: **build-time gap-fill only, never
redistributed** (SPEC §6.1). Its data is CC BY-**NC-SA** 4.0, and ShareAlike would
infect every JSON file the build emits.

| Fact | Value |
| --- | --- |
| Base URL | `https://api.jolpi.ca/ergast/f1/` |
| Migration from Ergast | a literal string swap of `ergast.com/api/f1/` → `api.jolpi.ca/ergast/f1/` |
| Coverage | 77 seasons, 1950–2026 |
| Formats | JSON only — **XML is not supported** |
| Licence | CC BY-NC-SA 4.0 |
| Response headers observed | `cache-control: max-age=600`, `server: cloudflare`, HTTP/2 |

## Ergast is dead, and its domain is hostile

The original Ergast API was updated through the end of the 2024 season and then shut
down. As of 2026-09-14, `ergast.com/api/…` returns **HTTP 404**, and `ergast.com/mrd/`
serves an Azerbaijani gambling-spam page with schema.org JSON-LD advertising betting
accounts.

**Never fetch, link or cite `ergast.com` anywhere on this site.** A citation in a
footer would point a reader at a casino SEO page. Attribution names "the Ergast Motor
Racing Developer API (2010–2024, discontinued)" in text, with no hyperlink, and links
jolpica instead.

FastF1 keeps the module `fastf1.ergast` and the class `Ergast` purely for
backwards compatibility; `fastf1/ergast/interface.py` sets
`BASE_URL = "https://api.jolpi.ca/ergast/f1"`.

## Endpoints

Thirteen Ergast-compatible routes. Every path must end with `/` or `.json`.

| Route | Notes |
| --- | --- |
| `/ergast/f1/circuits/` | |
| `/ergast/f1/constructors/` | |
| `/ergast/f1/{season}/constructorstandings/` | **season is required** |
| `/ergast/f1/drivers/` | |
| `/ergast/f1/{season}/driverstandings/` | **season is required** |
| `/ergast/f1/{season}/{round}/laps/` | |
| `/ergast/f1/{season}/{round}/pitstops/` | |
| `/ergast/f1/{season}/qualifying/` | |
| `/ergast/f1/races/` | |
| `/ergast/f1/results/` | |
| `/ergast/f1/seasons/` | |
| `/ergast/f1/sprint/` | |
| `/ergast/f1/status/` | Ordered by count, not by `statusId` |

Verified: `/ergast/f1/driverstandings/` returns **HTTP 400**;
`/ergast/f1/2026/driverstandings/` returns 200.

The response root is `MRData`, carrying `xmlns`, `series`, `url`, `limit`, `offset`,
`total` and one of `RaceTable` / `SeasonTable` / `StandingsTable` / etc.

## The `limit` cap is a silent clamp

`limit` defaults to 30 and is capped at **100**. Values above the cap are **silently
clamped** — no error, no warning, HTTP 200.

| Request | `MRData.limit` returned | `MRData.total` |
| --- | --- | --- |
| `seasons.json?limit=101` | `"100"` | `"77"` |
| `seasons.json?limit=1000` | `"100"` | `"77"` |
| `2025/1/laps.json?limit=1000` | `"100"` | `"921"` |

Any paging code must read `MRData.total` and page on `offset`; code that trusts the
requested `limit` under-fetches without failing. A single race's lap times alone need
~10 paged requests.

## Rate limits

| Limit | Value |
| --- | --- |
| Burst | **4 requests per second** |
| Sustained | **500 requests per hour** |
| On exceeding | `HTTP 429 Too Many Requests`, "Request was throttled" |
| Token access | "currently in the process of implementing" — no published limits, pricing or signup |

Documented verbatim: "These limits are subject to change, and **will decrease** in the
future as we roll out token access and our new non-ergast compatible replacement API."

Arithmetic that decides the architecture: 500 req/hr against 77 seasons × ~20 rounds ×
several endpoints makes a cold full-history crawl a multi-hour job that would trip the
limit repeatedly. That is why [F1DB](f1db.md) is the spine and jolpica is reserved for
incremental in-season gap-fill.

jolpica's own mitigation advice is to cache results and to use efficient filtered
queries — `2024/12/laps.json?limit=100&offset=0` rather than lap-by-lap, and
`2024/drivers/hamilton/results.json` rather than one request per round.

### The User-Agent is policy, not enforcement

The docs say "We require a custom user agent to be set when using our API", with the
example form `MyGreatF1App/1.2.3 FastF1/1.2.2`. Measured behaviour: a request with
curl's default User-Agent returns **200**, and one with an explicitly empty User-Agent
also returns **200**. Nothing rejects a request for lacking one.

Send one anyway — it is how they identify and block a misbehaving app version — but do
not write code that expects a 4xx to surface a missing header in testing.

```python
fastf1.ergast.interface.HEADERS['User-Agent'] = (
    f"YourAppName/{version} " + fastf1.ergast.interface.HEADERS['User-Agent']
)
```

## The status collapse — a correctness trap

jolpica's documentation states that the retirement-status collapse begins with the 2025
season. The live API disagrees, and the API is what the pipeline talks to. Measured
distinct `status` values by season and round:

| Season / round | Distinct statuses returned |
| --- | --- |
| 1990 R10 | `+1 Lap`, `+2 Laps`, `+3 Laps`, `Brakes`, `Collision`, `Engine`, `Finished`, `Gearbox` |
| 2010 R10 | full Ergast granularity |
| 2020 R10 | full Ergast granularity |
| 2021 R5 | `+1 Lap`, `+3 Laps`, `Driveshaft`, `Finished`, `Wheel nut` |
| 2022 R10 | `Collision`, `Collision damage`, `Finished`, `Fuel pump`, `Gearbox` |
| **2023 R5** | `Finished`, `Lapped` |
| **2023 R10** | `Finished`, `Retired` |
| **2024 R10** | `Finished`, `Lapped` |
| **2025 R5 / R10** | `Finished`, `Lapped`, `Retired` |

Two things collapse together, from **2023 onward**:

1. Granular retirement and failure causes become a bare `Retired`.
2. Lap-down margins (`+1 Lap`, `+2 Laps`, …) flatten to a single `Lapped`.

The `/status/` endpoint still lists 136 distinct historical statuses, but they only
populate results **through 2022** — so the endpoint's existence is not evidence that
the data is there.

> **Pipeline rule.** Every retirement-cause and laps-down figure from 2023 onward comes
> from [F1DB](f1db.md) (`reasonRetired`, `gapLaps`). This is enforced in the ingest
> code, not by convention: a naive implementation produces confidently wrong
> reliability charts for four recent seasons with no error anywhere.

For 2018+ there is a second recovery path — FastF1's `SessionResults.Status`, derived
from the timing feed (see [FastF1](fastf1.md)) — but it is NC-encumbered by a different
route and is used only as a cross-check.

## Other documented differences from Ergast

| Area | Change |
| --- | --- |
| All endpoints | XML responses are not supported |
| All endpoints | Duplicate filters: jolpica ignores all but the **last**; Ergast returned HTTP 400 |
| Results | `positionText` uses `R`, not `N` (confirmed on 2025 R1) |
| Results | `Time.time` always carries exactly 3 decimal places, with trailing zeros |
| Standings | A season parameter is now **required** |
| Races | 2023: the Sprint Shootout was renamed from `SecondPractice` |
| Races | 2024 onward: Sprint Qualifying was renamed from `SecondPractice` |
| Status | Ordered by count instead of `statusId`, "for database independence" |

## Bulk database dumps

`GET https://api.jolpi.ca/data/dumps/download/` returns a manifest rather than a file.
Live response, 2026-09-14:

```json
{
  "available_types": ["csv"],
  "latest_dumps": {"csv": {
    "dump_type": "csv",
    "file_hash": "686bff789ce87c68b4529a033e19f7d3c159a442682138c67644c9420e216828",
    "file_size": 14446682,
    "uploaded_at": "2026-09-13T19:47:04.577942Z",
    "download_url": "https://api.jolpi.ca/data/dumps/download/latest/?dump_type=csv"}},
  "delayed_dumps": {"csv": {
    "file_size": 14343826,
    "uploaded_at": "2026-08-23T16:58:55.431783Z",
    "download_url": "https://api.jolpi.ca/data/dumps/download/delayed/?dump_type=csv"}},
  "delay_days": 14
}
```

Each dump object carries `dump_type`, `file_hash` (SHA-256), `file_size` (bytes),
`uploaded_at` (ISO 8601) and `download_url`.

| Tier | What you get |
| --- | --- |
| **Free** | Dumps 14 days after upload; non-commercial use; no authentication |
| **Supporter** | Latest dumps immediately; a commercial-use licence; API key required |

The whole historical dataset is a single ~14.4 MB CSV bundle refreshed within a day of
the last race. Two warnings from the docs: address CSV columns **by name**, because
"we make no guarantees that their order will stay consistent"; and the integer
enumerations (`SessionEntry.status`, `PointSystem`, `ChampionshipScheme`,
`ChampionshipAdjustmentType`, `TeamDriver.role`) are documented only in the Django
model source, not in the dump. The schema mirrors those models, not Ergast's.

The **14-day delay on the free tier** is one of the three facts that make this a weekly
publication rather than a build (SPEC §12.2). The dumps are not a route around the
post-race ingest.

> The exact table and column layout of the dump bundle is **unverified** here — the
> manifest was read but the archive was not unzipped. Before anything depends on it,
> read <https://dbdocs.io/jolpica/jolpica-f1> and the Django model source.

## Licence, stability and role

TERMS.md (last updated 27 Aug 2025): "The API is freely available for
**non-commercial use**. The data is licensed under Creative Commons
Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) … For
commercial usage, please contact us via admin@jolpi.ca." It adds that the project is
"volunteer-run, donation-supported", that "we **do not guarantee uptime,
availability, or correctness**", and that "We reserve the right to change these terms".
The README puts hosting costs at "around $45 USD per month" against a fundraising goal
"to break-even during the 2026 season" — i.e. not yet met.

ShareAlike is the operative clause. Any dataset this site publishes that is derived
from jolpica would itself have to be released under CC BY-NC-SA 4.0, which would infect
the repository's data directory and contaminate the F1DB-derived spine. Hence the role
boundary, enforced in the pipeline: **NC-SA sources are build-time inputs whose values
are never written to a published artifact** (SPEC §13.4).

There is **no published deprecation date** for the `/ergast/` URL path. The README
describes it as "backwards compatible endpoints for the soon to be deprecated Ergast
API" and the rate-limit doc references "our new non-ergast compatible replacement API",
but no date, schema or preview URL is published; `https://api.jolpi.ca/schema/` returns
404 and the OpenAPI docs at `https://api.jolpi.ca/docs/` cover only the dumps endpoint.
Treat the path as able to break without notice, and prefer F1DB wherever a question can
be answered from it.
