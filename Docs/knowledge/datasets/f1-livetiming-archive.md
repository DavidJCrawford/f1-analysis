---
type: Dataset
title: F1 Live-Timing Archive
description: Formula 1's post-session static stream archive — the raw source under FastF1, its exact filenames and measured sizes, its unauthenticated but datacentre-hostile access, and the rights position that caps what may be published.
resource: https://livetiming.formula1.com/static/
tags: [livetiming, raw-data, jsonstream, signalr, legal, build-pipeline]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_api_source
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
    title: fastf1/_api.py — base URLs, stream filename table, parsing rules
  - id: fastf1_livetiming_client
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/livetiming/client.py
    title: fastf1/livetiming/client.py — SignalR endpoints and topic list
  - id: fastf1_releases
    resource: https://api.github.com/repos/theOehrly/Fast-F1/releases
    title: Fast-F1 release notes (v3.7.0 live-timing endpoint change)
  - id: archive_measurement
    resource: https://livetiming.formula1.com/static/2024/2024-07-07_British_Grand_Prix/2024-07-07_Race/
    title: 2024 British Grand Prix race session (sizes measured 2026-09-14)
  - id: f1_legal_notices
    resource: https://www.formula1.com/en/information/legal-notices.7egvZU48hzrypubGBNcQKt
    title: Formula 1 Legal Notices
status: stable
---

# F1 Live-Timing Archive

This is the actual source of every lap time, sector, stint and telemetry sample on the
site from 2018 onward. [FastF1](fastf1.md) is a parser over it; this document describes
what it is parsing, because the pipeline reads these streams directly wherever
`fastf1.api` would otherwise be a dependency (that module is deprecated — see
[FastF1](fastf1.md)).

Two halves, and only one of them matters here: the **static archive**, which a static
site builds from, and the **live SignalR feed**, which is explicitly out of scope.

## The static archive

| Fact | Value |
| --- | --- |
| Base | `https://livetiming.formula1.com` |
| Mirror constant in FastF1 | `https://livetiming-mirror.fastf1.dev` |
| Auth | **None** for post-session data |
| Path shape | `/static/{YYYY}/{wdate}_{Weekend_Name}/{sdate}_{Session_Name}/` with spaces replaced by underscores |
| Built by | `fastf1.api.make_path(wname, wdate, sname, sdate)` |
| Directory index | `Index.json` returns **HTTP 403** — listing is blocked; individual named streams are served |

FastF1 carries hardcoded path fixups for sessions whose archive path does not match the
schedule, e.g. `2024-11-03_Qualifying` → `2024-11-02_Qualifying` (Brazil), and
pre-season testing `2025-02-26_Practice_1` → `2025-02-26_Day_1`,
`2026-02-11_Practice_1` → `2026-02-11_Day_1`. Any independent path builder needs the
same table.

The mirror should **not** be assumed complete: every stream of the 2024 British GP race
path tested returned 404 on the mirror while the primary returned 200. `fetch_page()`
falls back to the mirror when the primary returns status ≥ 400, which is a resilience
feature, not a second copy of the archive.

### Stream filenames

The complete `pages` dict from `fastf1/_api.py` (lines 24–56), 21 entries:

| Key | File |
| --- | --- |
| `session_data` | `SessionData.json` |
| `session_info` | `SessionInfo.jsonStream` |
| `archive_status` | `ArchiveStatus.json` |
| `heartbeat` | `Heartbeat.jsonStream` |
| `audio_streams` | `AudioStreams.jsonStream` |
| `driver_list` | `DriverList.jsonStream` |
| `extrapolated_clock` | `ExtrapolatedClock.jsonStream` |
| `race_control_messages` | `RaceControlMessages.jsonStream` |
| `session_status` | `SessionStatus.jsonStream` |
| `team_radio` | `TeamRadio.jsonStream` |
| `timing_app_data` | `TimingAppData.jsonStream` |
| `timing_stats` | `TimingStats.jsonStream` |
| `track_status` | `TrackStatus.jsonStream` |
| `weather_data` | `WeatherData.jsonStream` |
| `position` | `Position.z.jsonStream` |
| `car_data` | `CarData.z.jsonStream` |
| `content_streams` | `ContentStreams.jsonStream` |
| `timing_data` | `TimingData.jsonStream` |
| `lap_count` | `LapCount.jsonStream` |
| `championship_prediction` | `ChampionshipPrediction.jsonStream` |
| `index` | `Index.json` |

### Measured session volume

Measured 2026-09-14 with `curl -A "FastF1/3.8"` against the **2024 British Grand Prix,
Race** session. Every named stream returned HTTP 200 with no authentication.

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
| **Total** | **20,956,694** (≈ 21.0 MB) |

Extrapolated: one full season across ~24 rounds × 5 sessions is roughly **1.5–2 GB** of
raw stream data. Against a 1 GB GitHub Pages published-site cap and a 100 GB/month
bandwidth cap (SPEC §11.3), this settles the question outright:

> **Raw streams are never committed and never published.** The cache is local; the
> repository carries only derived, downsampled artifacts — per-lap aggregates, a
> decimated racing line, a compact race-progression series, the 2 Hz replay buffer.

### Parsing rules

```
records = text.split("\r\n")
timestamp = record[:12]          # len('00:00:00:000')
payload   = json.loads(record[12:])
```

`.z.` streams (`Position.z`, `CarData.z`) are **DEFLATE-compressed base64** — FastF1
handles them as `parse(text, zipped=True)`. Everything else is plain JSON per record.

Because these are flat files with no schema endpoint, the decoder tables for track
status, weather, race control and the `timing_data` stream columns are documented in
[FastF1](fastf1.md#fastf1api--deprecated-but-the-only-decoder-ring). They exist nowhere
else.

### Access reality: it works, but not from CI

The measurements above were taken from a residential/edge origin (an AU Cloudflare
edge). **GitHub-hosted runners cannot ingest**: F1's live-timing archive blocks
datacentre IPs (SPEC §12.2). This is not a detail that can be worked around by a header
or a retry — it is the reason the project is structured as a weekly publication with a
human-run local ingest, and the reason CI never needs network access to F1.

Two related unknowns, marked as such:

- Whether the archive is additionally geo-restricted was **not established**. All test
  requests succeeded unauthenticated from one origin.
- Whether the archive is complete back to 2018 for every session — including cancelled
  and abandoned sessions — was **not verified end to end**.

Both should be tested from the actual ingest environment before a season is scheduled
around them.

## The live SignalR feed — out of scope

Recorded so that nobody re-discovers it as an option.

| Fact | Value |
| --- | --- |
| Connection | `wss://livetiming.formula1.com/signalrcore` |
| Negotiate | `https://livetiming.formula1.com/signalrcore/negotiate` |
| Changed in | FastF1 **v3.7.0**, published 2025-11-27 |
| Auth | Effectively requires an F1TV Access/Pro/Premium subscription |
| Escape hatch | `SignalRClient(no_auth=True)` — "may only work for some sessions or may only return empty or partial data" |
| Server disconnect | ~2 hours of recording |
| CLI | `python -m fastf1.livetiming save [--append] [--timeout TIMEOUT] file` |

From the v3.7.0 release notes: "The livetiming client now uses a new endpoint and
protocol. This follows changes by Formula 1, who have gradually phased out the old
endpoints", and "Authentication is only required when using the new live timing client,
since the new endpoints no longer allow unauthenticated access. This change has no
effect on the majority of users who only load data after a session has ended."

The client pre-negotiates with `requests.options()` to obtain an `AWSALBCORS` cookie,
then builds a signalrcore hub connection with
`access_token_factory = None if no_auth else get_auth_token`, and subscribes with
`self._connection.send("Subscribe", [self.topics], ...)`. The topic list:

```
Heartbeat, AudioStreams, DriverList, ExtrapolatedClock, RaceControlMessages,
SessionInfo, SessionStatus, TeamRadio, TimingAppData, TimingStats, TrackStatus,
WeatherData, Position.z, CarData.z, ContentStreams, SessionData, TimingData,
TopThree, RcmSeries, LapCount
```

Debug mode was removed (`if debug: raise ValueError("Debug mode is no longer
supported.")`), and the client cannot run in Google Colab or WASM/JupyterLite because
of the sign-in method.

**None of this is used.** Live timing is an explicit non-goal (SPEC §2), and the static
archive needs no authentication. The direction of travel — F1 progressively closing the
unauthenticated live endpoints — is the argument for mirroring what the site needs
rather than assuming the archive stays open.

## The legal position

This is the sharpest constraint on the whole project, and it applies to this source
specifically because this source is F1's own.

Quoted from Formula 1's Legal Notices:

- "all materials on this Site, including, but not limited to live timing data,
  historical race data, photographs, other images…are protected by copyrights,
  database rights, trademarks"
- "All results, timing data and certain other content are copyright Formula One World
  Championship Limited. All rights reserved."
- "The material and content provided on the Site is for your personal, non-commercial
  use only…you agree not…to distribute copy extract or commercially exploit such
  material or content."
- The trademark list names **Formula One Licensing BV** as proprietor of F1, FORMULA 1,
  FORMULA ONE, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks.

The mitigation posture, which is a risk-reduction stance assembled from published terms
and **not legal advice** (SPEC §13.1):

1. **Publish derived aggregates and visualisations, never bulk raw timing streams.**
   The 21 MB measured above never leaves the ingest machine in its original form.
2. Keep volumes modest — the 2 Hz replay default exists partly for this reason.
3. Carry a clear non-affiliation disclaimer in the footer of every page:
   *"[Site] is unofficial and is not associated in any way with the Formula 1
   companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND
   PRIX and related marks are trade marks of Formula One Licensing B.V."*
   This is the wording FastF1, OpenF1 and MultiViewer all use.
4. No F1 wordmark, no F1 logo, no official team logos, no official driver headshots —
   `HeadshotUrl` and `circuit_image` point at F1's own CDN and are neither hotlinked nor
   rehosted.
5. Keep the site strictly non-commercial: no ads, no sponsorship, no affiliate links,
   no paid tier. This also keeps the NC-licensed sources usable as build-time inputs.
6. Set an identifying User-Agent on every outbound request.
7. Be prepared to take material down.

The exact wording F1's fan-site guidelines require is **unverified** — both candidate
URLs returned 404 — and must be confirmed before launch (SPEC §13.5).
