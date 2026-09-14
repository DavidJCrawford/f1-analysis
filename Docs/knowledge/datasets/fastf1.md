---
type: Dataset
title: FastF1 3.8.3
description: The Python library that parses Formula 1's timing archive into laps, telemetry and results — its object model, exact column names, cache configuration and the 2018 coverage floor.
resource: https://pypi.org/project/fastf1/3.8.3/
tags: [fastf1, python, telemetry, laps, build-pipeline, ingest]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_pypi
    resource: https://pypi.org/pypi/fastf1/json
    title: FastF1 release metadata on PyPI
  - id: fastf1_core_docs
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API reference (Session, Laps, Telemetry, SessionResults)
  - id: fastf1_events_docs
    resource: https://docs.fastf1.dev/events.html
    title: FastF1 event schedule and supported seasons
  - id: fastf1_cache_docs
    resource: https://docs.fastf1.dev/api_reference/cache_and_rate_limits.html
    title: FastF1 cache and rate limits
  - id: fastf1_api_docs
    resource: https://docs.fastf1.dev/api.html
    title: fastf1.api — track status, weather and race control decoder tables
  - id: fastf1_req_source
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/req.py
    title: fastf1/req.py on master — Cache.configure deprecation of enable_cache
  - id: fastf1_discussion_116
    resource: https://github.com/theOehrly/Fast-F1/discussions/116
    title: Fast-F1 Discussion #116 — position data is a normalised track position
status: stable
---

# FastF1 3.8.3

FastF1 is the ingest tool for everything after 2018 on this site. It is **build-time
only** — it runs on a maintainer's machine, its output is committed as derived data,
and nothing it fetches is ever requested from a visitor's browser. The library is MIT;
the data it retrieves is not (see [F1 live-timing archive](f1-livetiming-archive.md)).

## Release facts

| Fact | Value |
| --- | --- |
| Version | 3.8.3, uploaded 2026-04-29T21:24:01Z |
| Licence | MIT — "Copyright (c) 2026 Philipp Schäfer" |
| Python | `>=3.10` |
| Install | `pip install fastf1` or `conda install -c conda-forge fastf1` |
| Docs | <https://docs.fastf1.dev/> |

Recent releases: 3.8.0 (2026-02-10), 3.8.1 (2026-02-11, 2026 pre-season testing
patches), 3.8.2 (2026-03-29), 3.8.3 (2026-04-29). 3.8.0 dropped Python 3.9, added
`pydantic`, introduced the `fastf1.exceptions` submodule, added auto-generation of
team name/colour constants from F1 API data as a fallback for future seasons, and
shipped preliminary 2026 team colours. Deprecated API is removed two minor releases
after deprecation.

Importing `NoLapDataError`, `DataNotLoadedError`, `InvalidSessionError` from
`fastf1.core`, or `RateLimitExceededError` from `fastf1`, is **deprecated** — import
all four from `fastf1.exceptions`.

Runtime dependencies, verbatim from `requires_dist`: `cryptography`,
`matplotlib<4.0.0,>=3.8.0`, `numpy<3.0.0,>=1.26.0`, `pandas<3.0.0,>=2.1.1`,
`platformdirs`, `pydantic`, `pyjwt`, `python-dateutil`, `rapidfuzz`,
`requests-cache>=1.0.0`, `requests>=2.30.0`, `scipy<2.0.0,>=1.11.0`, `signalrcore`,
`timple>=0.1.6`, `websockets>=10.3`.

## Entry points and backends

```python
fastf1.get_session(year, gp, identifier=None, *, backend=None, exact_match=False)
fastf1.get_testing_session(year, test_number, session_number, *, backend=None)
fastf1.get_event_schedule(year, *, include_testing=True, backend=None, force_ergast=False)
fastf1.get_event(...)          # single event
fastf1.get_events_remaining(...)
fastf1.get_testing_event(...)
```

`backend` is `Literal['fastf1', 'f1timing', 'ergast']`.

| Backend | Coverage | Notes |
| --- | --- | --- |
| `fastf1` | 2018 → now | Default, with automatic fallback |
| `f1timing` | 2018 → now | F1 live timing API; sessions without timing data are not listed |
| `ergast` | 1950 → now | No local session times, no `F1ApiSupport` flag. Always used for pre-2018 seasons |

Despite the name, the `ergast` backend now resolves to jolpica —
`fastf1/ergast/interface.py` sets `BASE_URL = "https://api.jolpi.ca/ergast/f1"`. See
[jolpica-f1](jolpica-f1.md).

## What exists per season

This is the single fact that drives the site's four-tier coverage model (SPEC §4.2).

| Range | Schedule | Laps / sectors | Telemetry | Testing sessions |
| --- | --- | --- | --- | --- |
| 1950–2017 | via the ergast backend; **only the race date/time is real**, all other sessions back-calculated on a conventional Fri/Sat/Sun assumption — "These assumptions will be incorrect for certain events!" | no | no | no |
| 2018–2019 | FastF1's own schedule, exact session start times | yes | yes (X/Y/Z unit **not documented** for these seasons — only the 2020-onward 1/10 m statement exists; treat pre-2020 coordinates as unverified) | no |
| 2020 → | FastF1's own schedule | yes | yes (X/Y/Z in **1/10 m**) | yes |

`EventSchedule` columns: `RoundNumber` (int; testing = 0), `Country`, `Location`,
`OfficialEventName`, `EventName`, `EventDate`, `EventFormat`, `Session1`…`Session5`,
`Session1Date`…`Session5Date` (tz-aware local; **not available on the ergast
backend**), `Session1DateUtc`…`Session5DateUtc` (naive UTC), `F1ApiSupport` (bool —
this flag gates whether laps or telemetry can be loaded at all).

`EventFormat` vocabulary: `conventional`, `sprint` (2021–2022), `sprint_shootout`
(2023), `sprint_qualifying` (2024 →), `testing`.

## `Session.load()`

```python
Session.load(*, laps=True, telemetry=True, weather=True, messages=True, livedata=None)
```

All five parameters are keyword-only.

| Parameter | Loads | Consequence if `False` |
| --- | --- | --- |
| `laps` | lap data **and** session-status data | `session.laps` and `session.session_status` unavailable |
| `telemetry` | car data + position data | `car_data`, `pos_data`, `t0_date` unavailable |
| `weather` | per-minute weather samples | `weather_data` unavailable |
| `messages` | race control messages | `Laps.Deleted` / `Laps.DeletedReason` are absent |
| `livedata` | a `fastf1.livetiming.data.LiveTimingData` instance instead of the API | — |

Attributes populated on the `Session`:

| Attribute | Type | Notes |
| --- | --- | --- |
| `event` | `Event` | |
| `name` | str | e.g. `'Qualifying'` |
| `f1_api_support` | bool | |
| `date` | `pd.Datetime` | |
| `api_path` | str | the live-timing archive path for this session |
| `session_info` | dict | meeting/session/country/circuit names and key ids, incl. the circuit key |
| `drivers` | list[str] | driver numbers as strings |
| `results` | `SessionResults` | |
| `laps` | `Laps` | |
| `total_laps` | int | originally scheduled laps for race-like sessions |
| `weather_data` | DataFrame | |
| `car_data` | dict[str, `Telemetry`] | keyed by car number string |
| `pos_data` | dict[str, `Telemetry`] | keyed by car number string |
| `session_status` | DataFrame | |
| `track_status` | DataFrame | |
| `race_control_messages` | DataFrame | |
| `session_start_time` | Timedelta | |
| `t0_date` | Timestamp | session time zero; only after `telemetry=True` |

Methods: `get_driver(identifier)` → `DriverResult` (accepts `'VER'` or a driver number
as a string) and `get_circuit_info()` → `CircuitInfo | None` (see
[MultiViewer API](multiviewer-api.md)).

Documented accuracy caveat, verbatim: *"Expect an error of around ±10m when
overlapping telemetry data of different laps"* — the lap-time reference is
synchronised on whichever sector time was triggered with the lowest latency.

## `Laps` — 31 columns

`fastf1.core.Laps` is a DataFrame subclass with exactly 31 documented columns.

| Column | dtype | Meaning |
| --- | --- | --- |
| `Time` | Timedelta | Session time at which the lap time was set (i.e. end of lap) |
| `Driver` | str | Three-letter code |
| `DriverNumber` | str | |
| `LapTime` | Timedelta | |
| `LapNumber` | float | |
| `Stint` | float | |
| `PitOutTime` | Timedelta | |
| `PitInTime` | Timedelta | |
| `Sector1Time` / `Sector2Time` / `Sector3Time` | Timedelta | |
| `Sector1SessionTime` / `Sector2SessionTime` / `Sector3SessionTime` | Timedelta | Session-clock timestamps of each sector line |
| `SpeedI1` / `SpeedI2` / `SpeedFL` / `SpeedST` | float | km/h at the two intermediates, the finish line and the speed trap |
| `IsPersonalBest` | bool | |
| `Compound` | str | `SOFT`, `MEDIUM`, `HARD`, `INTERMEDIATE`, `WET`, `TEST_UNKNOWN`, `UNKNOWN` |
| `TyreLife` | float | Includes laps run in other sessions on a used set |
| `FreshTyre` | bool | |
| `Team` | str | |
| `LapStartTime` | Timedelta | |
| `LapStartDate` | Timestamp | |
| `TrackStatus` | str | Concatenated status digits seen during the lap |
| `Position` | float | **NaN** for FP1/FP2/FP3, Sprint Shootout, Qualifying, and crash laps |
| `Deleted` | Optional[bool] | Only when `messages=True` |
| `DeletedReason` | str | Only when `messages=True` |
| `FastF1Generated` | bool | Lap synthesised by FastF1 (e.g. a partial final lap for a retirement) |
| `IsAccurate` | bool | See criteria below |

Two traps worth stating plainly:

- **`Compound` never differentiates C1–C5.** The site can say "soft", never "C3".
  Any compound-hardness narrative needs an external mapping and is not in scope.
- **`Position` is NaN outside races.** Qualifying "position" charts must be derived
  from `SessionResults`, not from `Laps`.

`IsAccurate` is true only when the lap: is not an in- or out-lap; was set entirely
under green or yellow flag; is not the first lap after a safety car period; has a lap
time and all three sector times; and the sum of the sector times matches the lap time.
This is the correct default filter for any pace metric — see
[`knowledge/metrics/`](../metrics/index.md).

Selection methods on `Laps`: `pick_lap`, `pick_laps`, `pick_driver`, `pick_drivers`,
`pick_team`, `pick_teams`, `pick_fastest`, `pick_quicklaps`, `pick_tyre`,
`pick_compounds`, `pick_track_status`, `pick_wo_box`, `pick_box_laps`,
`pick_not_deleted`, `pick_accurate`, `split_qualifying_sessions`, `iterlaps`. Data
methods: `get_telemetry(*, frequency)`, `get_car_data(**kwargs)`,
`get_pos_data(**kwargs)`, `get_weather_data()`. The class attribute
`QUICKLAP_THRESHOLD` controls `pick_quicklaps`.

## `Telemetry` — channels and sample rates

`fastf1.core.Telemetry` merges two physically separate streams.

| Group | Channels |
| --- | --- |
| Car data | `Speed` (float, km/h), `RPM` (float), `nGear` (int), `Throttle` (float, 0–100 %), `Brake` (bool), `DRS` (int) |
| Position data | `X`, `Y`, `Z` (float, **units of 1/10 m from 2020 onward**), `Status` (str: `OnTrack` / `OffTrack`) |
| Shared | `Time` (Timedelta, 0 = start of slice), `SessionTime` (Timedelta since session start), `Date` (datetime), `Source` (str: `car`, `pos` or `interpolated`) |
| Computed | `DifferentialDistance`, `Distance`, `RelativeDistance`, `TrackStatus`, `DriverAhead`, `DistanceToDriverAhead` |

Computed channels must be requested explicitly: `add_differential_distance()`,
`add_distance()`, `add_relative_distance()`, `add_track_status()`,
`add_driver_ahead()`. Other methods: `slice_by_mask`, `slice_by_lap`, `slice_by_time`,
`merge_channels(other, frequency)`, `resample_channels(rule, new_date_ref)`,
`fill_missing()`, `register_new_channel(...)`, `get_first_non_zero_time_index()`,
`calculate_differential_distance()`, `integrate_distance()`,
`calculate_driver_ahead(return_reference)`. Class attribute
`TELEMETRY_FREQUENCY = 'original'` (the string `'original'` or an integer in Hz).

### Sample rate — the documented figure is nominal

| Stream | Docstring | Measured |
| --- | --- | --- |
| Position | "usually 220 ms" | median **240 ms**, mean 258 ms, min 20 ms, max 500 ms over a 465-sample window (Spa 2024, session_key 9574, car 1); median **241.0 ms** on the 2024 British GP, mean 259.3 ms inflated by gaps |
| Car | ~240 ms | — |

The two streams **do not line up**; merging requires resampling or interpolation. Treat
the position stream as irregular and interpolate on `Date`, never on an assumed fixed
grid. This measurement is what sets the site's replay encoding at 2 Hz by default with
5 Hz on demand (SPEC §6.5) — 5 Hz is close to native, 2 Hz is a real reduction.

### DRS channel

The mapping is only partly understood, and FastF1's own docstring says so
("Odd DRS is Disabled, Even DRS is Enabled?" / "More Research Needed?").

| Value | Meaning |
| --- | --- |
| 0, 1 | Off |
| 2, 3 | unknown |
| 8 | Detected, eligible once in the activation zone (observed only sometimes) |
| 10, 12, 14 | On (distinction unknown) |

`DRS` and `nGear` are declared discrete channels in `core.py`
(`{"type": "discrete"}`), so merging forward-fills rather than interpolating — which is
the correct behaviour. Practical rule: `tel['DRS'].isin([10, 12, 14])` is "wing open".

### Position data is one line, not twenty

The maintainer describes the position feed as a *normalised track position* produced
for the broadcast driver-tracker graphic: all laps follow essentially the same line,
with deviations that are "likely due to quantization inaccuracies", and "it's certainly
not possible to analyze drivers lines through a corner." OpenF1's docs say the same
thing from the other side — the data "cannot distinguish whether cars are on the left
or right side of the track". Any feature premised on comparing two drivers' *lines* is
therefore prohibited; comparing their *speed at distance* is fine.

## `SessionResults` — 22 columns

Indexed by driver number, sorted by finishing position. "All dataframe columns will
always exist even if they are not relevant for the current session!"

`DriverNumber`, `BroadcastName`, `Abbreviation`, `DriverId`, `TeamName`, `TeamColor`,
`TeamId`, `FirstName`, `LastName`, `FullName`, `HeadshotUrl`, `CountryCode`,
`Position`, `ClassifiedPosition`, `GridPosition`, `Q1`, `Q2`, `Q3`, `Time`, `Status`,
`Points`, `Laps`.

There is **no `DriverColor` column**. Colour is derived from `TeamColor` (a hex string)
and then luminance-remapped per ground by our own encoding rules (SPEC §8.3).

| Column | Note |
| --- | --- |
| `DriverId` | "driverId that is used by the Ergast API" — the join key to jolpica and F1DB |
| `TeamId` | "constructorId that is used by the Ergast API" — same |
| `Position` | float; accounts for post-race penalties and disqualifications |
| `ClassifiedPosition` | str: an integer, or `R` retired, `D` disqualified, `E` excluded, `W` withdrawn, `F` failed to qualify, `N` not classified |
| `Time` | Total race time, present only if within one lap of the leader |
| `Status` | e.g. `Finished`, `+ 1 Lap`, `Crash`, `Gearbox` — a usable retirement cause where jolpica has collapsed its own |
| `Laps` | Added in v3.6.0 |
| `HeadshotUrl` | Points at F1's own CDN. Never hotlinked and never rehosted |

`DriverResult` is the single-driver `pandas.Series` equivalent and adds a `.dnf` bool
property.

## Cache — the build pipeline's most important knob

Caching is on by default. Directory precedence:

1. an explicit call to `Cache.enable_cache()`
2. the environment variable **`FASTF1_CACHE`**
3. an OS default — Windows `%LOCALAPPDATA%\Temp\fastf1`, macOS
   `~/Library/Caches/fastf1`, Linux `~/.cache/fastf1` (or `~/.fastf1`)

```python
Cache.enable_cache(cache_dir, ignore_version=False, force_renew=False,
                   use_requests_cache=True)
```

Two stages. **Stage 1** caches raw GET/POST through `requests-cache` into a SQLite
database with HTTP cache-control refresh. **Stage 2** pickles the *parsed* data, which
"saves a lot of time … as parsing of the data is computationally expensive", and only
applies to some API functions. The stage-2 cache is laid out by year/event/session, so
a single bad session can be deleted by hand.

Other class methods: `clear_cache(cache_dir=None, deep=False)`, `get_cache_info()` →
`(path, size_bytes)` or `(None, None)`, `disabled()` (context manager),
`set_disabled()`, `set_enabled()`, `offline_mode(enabled)` (cache only, sends no
requests), `ci_mode(enabled)`, `requests_get(url, **kwargs)`, `requests_post`,
`delete_response(url)`, `api_request_wrapper(func)`.

**Requests served from cache do not count toward any rate limit**, so a warm cache
effectively raises the ceiling. On exceeding a limit FastF1 either throttles (soft) or
raises `fastf1.exceptions.RateLimitExceededError` (hard).

### Forward-compatibility warning

On master (3.9.0-dev) `enable_cache` carries `.. deprecated:: 3.9.0` and emits a
`FutureWarning`: "`.enable_cache` is deprecated and will be removed in a future
version. Use `.configure` instead." The replacement is keyword-only:

```python
Cache.configure(*, cache_dir=None, force_renew=False,
                ignore_version=False, use_requests_cache=True)
```

The pipeline pins FastF1 exactly and writes this call behind a thin wrapper so the 3.9
upgrade is a one-line change.

### Ingest recipe

```python
import fastf1
fastf1.Cache.enable_cache(os.environ["FASTF1_CACHE"])   # before any other FastF1 call
fastf1.Cache.offline_mode(True)                          # deterministic rebuild of a cached season
session = fastf1.get_session(2024, "British Grand Prix", "R")
session.load(laps=True, telemetry=True, weather=True, messages=True)
```

Ingest runs locally, not on a GitHub-hosted runner (SPEC §12.2); the cache is a local
directory, and the *derived* artifacts — not the cache — are what gets committed.

## `fastf1.api` — deprecated, but the only decoder ring

Every function in `fastf1.api` carries the warning that it "will be considered private
in future releases and potentially be removed or changed"; `fastf1/api.py` is now a
33-line shim over `fastf1._api` that emits a `UserWarning`. Its *documentation* is
still the only published description of these vocabularies, so they are recorded here
and the pipeline parses the streams itself rather than depending on the module.

**Track status** (`track_status_data`; columns `Time`, `Status`, `Message`):

| Code | Meaning |
| --- | --- |
| `1` | Track clear |
| `2` | Yellow flag (sectors unknown) |
| `3` | Never observed; may not exist |
| `4` | Safety Car |
| `5` | Red flag |
| `6` | Virtual Safety Car deployed |
| `7` | Virtual Safety Car ending (status `1` marks the actual end) |

**Weather** (`weather_data`, one sample per minute): `Time` (Timedelta), `AirTemp`
(°C), `Humidity` (%), `Pressure` (mbar), `Rainfall` (bool), `TrackTemp` (°C),
`WindDirection` (int, 0–359°), `WindSpeed` (m/s).

**Race control** (`race_control_messages`): always `Utc`, `Category` (`Other`, `Flag`,
`Drs`, `CarEvent`), `Message`; optionally `Status` (e.g. `DISABLED` for DRS), `Flag`
(`GREEN`, `RED`, `YELLOW`, `CLEAR`, `CHEQUERED`), `Scope` (`Track`, `Sector`,
`Driver`), `Sector` (int), `RacingNumber` (str), `Lap` (int).

**`timing_data`** returns `(laps_data, stream_data)`. `stream_data` columns are `Time`,
`Driver`, `Position` (int), `GapToLeader` (Timedelta), `IntervalToPositionAhead`
(Timedelta). This per-sample gap series is **not** in `session.laps` and is the natural
input for the gap-to-leader and race-trace archetypes (SPEC §10).

`driver_info` keys: `RacingNumber`, `BroadcastName`, `FullName`, `Tla`, `Line`,
`TeamName`, `TeamColour`, `FirstName`, `LastName`, `Reference`, `HeadshotUrl`,
`CountryCode`.

## Role boundary

FastF1 is MIT, but that licences the *code*, not the data it retrieves. Derived
aggregates and visualisations ship; raw streams do not. See
[F1 live-timing archive](f1-livetiming-archive.md) for the underlying rights position
and [F1DB](f1db.md) for the redistributable spine that carries the pre-2018 site.
