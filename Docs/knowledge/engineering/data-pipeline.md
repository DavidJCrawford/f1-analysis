---
type: Reference
title: Data pipeline
description: The five-stage Python ingest that turns F1's live-timing archive, jolpica and F1DB into validated, reproducible, incrementally-rebuilt site data.
resource: https://docs.fastf1.dev/
tags: [fastf1, python, ingest, caching, incremental, validation, provenance, pydantic, pandera]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_pypi
    resource: https://pypi.org/pypi/fastf1/json
    title: FastF1 PyPI metadata
  - id: fastf1_api_src
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
    title: FastF1 fastf1/_api.py
  - id: fastf1_req_src
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/req.py
    title: FastF1 fastf1/req.py
  - id: fastf1_docs
    resource: https://docs.fastf1.dev/api.html
    title: FastF1 telemetry and API reference
  - id: livetiming_index_2018
    resource: https://livetiming.formula1.com/static/2018/Index.json
    title: F1 live timing season index (2018)
  - id: jolpica_limits
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/rate_limits.md
    title: jolpica-f1 rate limits
  - id: f1db
    resource: https://github.com/f1db/f1db
    title: F1DB repository and release format
  - id: pandera_pypi
    resource: https://pypi.org/pypi/pandera/json
    title: pandera PyPI metadata
  - id: pydantic_pypi
    resource: https://pypi.org/pypi/pydantic/json
    title: pydantic PyPI metadata
  - id: dvc_yaml
    resource: https://doc.dvc.org/user-guide/project-structure/dvcyaml-files
    title: DVC dvc.yaml reference
  - id: fullthrottle
    resource: https://github.com/Chiroyce1/FullThrottle
    title: Chiroyce1/FullThrottle README (FastF1 → Parquet → browser pipeline)
status: stable
---

# Data pipeline

Five stages, with the network boundary made explicit, because the boundary is the
architecture: **F1's live-timing servers block datacenter IP ranges, so ingest
cannot run in CI.** Everything else follows from that and from the licence roles
declared in the spec.

```
1 fetch      local / self-hosted, residential IP        needs F1 network
2 transform  anywhere, offline_mode(True)               no network
3 emit       anywhere                                    no network
4 verify     anywhere                                    no network
5 deploy     GitHub Actions                              no F1 network
```

Stages 2–5 need no F1 network access. That is what makes CI viable at all.

## 1. Toolchain

| Package | Pin | Notes |
| --- | --- | --- |
| Python | 3.12 | FastF1 requires ≥ 3.10 |
| `fastf1` | 3.8.3 | released 2026-04-29, MIT |
| `pyarrow` | 25.0.1 | Parquet writer |
| `pydantic` | 2.13.5 | released 2026-08-28, Python 3.9–3.14 |
| `pandera` | 0.33.1 | Python ≥ 3.10 |

FastF1 3.8.3's full `requires_dist` — worth recording because incomplete lists
circulate: `cryptography`, `matplotlib<4.0.0,>=3.8.0`, `numpy<3.0.0,>=1.26.0`,
`pandas<3.0.0,>=2.1.1`, `platformdirs`, `pydantic`, `pyjwt`, `python-dateutil`,
`rapidfuzz`, `requests-cache>=1.0.0`, `requests>=2.30.0`, `scipy<2.0.0,>=1.11.0`,
`signalrcore`, `timple>=0.1.6`, `websockets>=10.3`. Fifteen entries. Note
`pyjwt` and `cryptography`: neither appears in `fastf1/req.py`, so JWT handling
lives elsewhere — most likely the live-timing/SignalR path. Anything suggesting
F1's endpoints are moving toward authenticated access is a material risk to a
pipeline built on the static archive, and is worth watching.

Release line: 3.7.0 (2025-11-27, Python 3.14 support, new live-timing endpoints),
3.8.0 (2026-02-10, dropped Python 3.9, added pydantic, new `exceptions` submodule,
auto-generated team constants), 3.8.1 (2026-02-11), 3.8.2 (2026-03-29),
3.8.3 (2026-04-29).

## 2. Stage 1 — fetch

### The source

`https://livetiming.formula1.com/static/{YYYY}/{YYYY-MM-DD_Event_Name}/{YYYY-MM-DD_Session}/`

The archive **begins in 2018**: `static/2017/Index.json` returns **403**;
2018 returns 200 at exactly 26,216 B; 2019 returns 200 at 27,747 B. Everything
earlier is results-only, from F1DB.

FastF1's constants, from `fastf1/_api.py`:

```python
base_url = "https://livetiming.formula1.com"
base_url_mirror = "https://livetiming-mirror.fastf1.dev"

headers: dict[str, str] = {
    "Connection": "close",
    "TE": "identity",
    "User-Agent": "BestHTTP",
    "Accept-Encoding": "gzip, identity",
}
```

The `pages` dict names every stream: `session_data`, `session_info`,
`archive_status`, `heartbeat`, `audio_streams`, `driver_list`,
`extrapolated_clock`, `race_control_messages`, `session_status`, `team_radio`,
`timing_app_data`, `timing_stats`, `track_status`, `weather_data`, `position`
(→ `Position.z.jsonStream`), `car_data` (→ `CarData.z.jsonStream`),
`content_streams`, `timing_data`, `lap_count`, `championship_prediction`, `index`.

### Measured volumes — 2024 British Grand Prix, race session

Downloaded and byte-counted directly, not estimated:

| File | Bytes on the wire |
| --- | ---: |
| `Position.z.jsonStream` | 7,914,755 |
| `CarData.z.jsonStream` | 7,302,595 |
| `TimingData.jsonStream` | 5,589,783 |
| `TimingAppData.jsonStream` | 87,867 |
| `Heartbeat.jsonStream` | 34,503 |
| `WeatherData.jsonStream` | 21,009 |
| `RaceControlMessages.jsonStream` | 19,620 |
| `Index.json` | 2,680 |
| `SessionInfo.jsonStream` | 490 |
| `TrackStatus.jsonStream` | 52 |
| **Total** | **20,973,354 (≈ 21.0 MB)** |

Decoded: `Position.z` inflates 7,914,755 → **37,388,903 B** of JSON (4.72×);
`CarData.z` inflates 7,302,595 → **42,712,714 B** (5.85×). Those two alone are
80.1 MB; adding the already-uncompressed `TimingData` and the rest brings the true
parsed-JSON total to **≈ 86 MB** for one race session.

Decoding recipe, per stream line: strip the 12-character `HH:MM:SS.mmm` timestamp
prefix and the surrounding quotes, then

```python
zlib.decompress(base64.b64decode(payload), -zlib.MAX_WBITS)
```

Position stream contents: 8,696 chunks → 33,899 distinct frames → **677,980
position samples** across 21 distinct car numbers over a 146.5-minute window
(2024-07-07T13:04:59.390Z → 15:31:29.973Z). Nineteen cars have 33,899 samples,
car #3 has 33,896, and **car #21 has only 3 samples — a spurious entry.** Any
per-car budget figure must divide by **20**, not 21, or it understates by 5%.

Coordinate extents at Silverstone (units 1/10 m): X −2,315..7,791,
Y −4,117..13,116, Z 0..2,075 — a 1,011 m × 1,723 m bounding box, comfortably
inside int16 at 1/10 m (±3,276.7 m). Every sample carried `Status == "OnTrack"`.

### Sampling rates

FastF1's docs say car data has a "sample rate of (usually) 240ms" and position
"usually 220ms". Measured on the real stream:

| Stream | Timestamps | Median interval | Mean interval |
| --- | ---: | ---: | ---: |
| Position | 33,899 over 8,791 s | **241.0 ms** | 259.3 ms |
| CarData | 33,181 | **240.0 ms** | 263.8 ms |

So position is ~240 ms in practice, not 220 ms, and the mean is inflated by gaps.
**Budget for ~260 ms effective.** The two streams run on independent clocks and do
not line up; `merge_channels()` interpolates and marks the result
`Source == 'interpolated'`.

### Channels

Car-data channel keys, from `fastf1/_api.py`:

```python
rpm      = entry["Cars"][drv]["Channels"]["0"]
speed    = entry["Cars"][drv]["Channels"]["2"]    # km/h
ngear    = entry["Cars"][drv]["Channels"]["3"]
throttle = entry["Cars"][drv]["Channels"]["4"]    # 0-100
brake    = entry["Cars"][drv]["Channels"]["5"]    # bool
drs      = entry["Cars"][drv]["Channels"].get("45", 0)
```

Two schema consequences:

- **`drs` must be nullable everywhere.** The FastF1 source carries an explicit
  note that DRS is no longer included in 2026, so the UI must not assume a DRS
  trace exists for the current season.
- **104 is an observed sentinel, not a documented one.** FastF1's docs describe
  `Throttle` only as "0-100 Throttle pedal pressure [%]"; 104 appears nowhere in
  them. It is real — in the 2024 British GP `CarData.z` stream, channels "4"
  (Throttle) and "5" (Brake) both carry 104 in the opening samples — so the
  validation check is worth having, described accurately as an observed sentinel.

Derived channels available from FastF1: `Distance` (m from first sample),
`RelativeDistance` (0.0–1.0), `DifferentialDistance`, `DriverAhead`,
`DistanceToDriverAhead`, `TrackStatus`. Methods: `slice_by_mask`, `slice_by_lap`,
`slice_by_time`, `merge_channels`, `resample_channels`, `fill_missing`, `join`,
`merge`, `add_distance`, `add_differential_distance`, `add_relative_distance`,
`add_driver_ahead`, `add_track_status`, `calculate_driver_ahead`,
`calculate_differential_distance`, `integrate_distance`, `register_new_channel`,
`get_first_non_zero_time_index`.

`add_driver_ahead()` carries an explicit warning to apply it only to single laps
or a few laps at a time "to reduce integration error" — never across a whole race.

**`RelativeDistance` (0.0–1.0) is the cross-driver and cross-season comparison
key**, not `Distance`, because lap length differs between layouts and even
between sessions.

Gate what gets fetched:
`Session.load(laps=True, telemetry=True, weather=True, messages=True, livedata=None)` —
telemetry is the expensive one, so load only what a given emit step needs.

### The IP block

FullThrottle — a production F1 telemetry site on exactly this stack (FastF1 →
Parquet → CDN → hyparquet in-browser) — states verbatim in its README:

> "F1's live timing servers block cloud/datacenter IP ranges (including
> GitHub-hosted Actions runners), so automated cron runs in the cloud return
> empty data."

Corroborating: FastF1 issue #615 reports
`https://livetiming.formula1.com/static/2022/.../SessionInfo.jsonStream` returning
403, and the maintainer labelled it *external*, not a FastF1 bug. Residential-IP
fetches of the same host return 200 for every stream, consistent with IP gating.

FastF1's in-library mitigation is the mirror: `_api.py` retries
`base_url_mirror` whenever the primary returns `status_code >= 400`. Three things
to know about it. It is **not** a 3.8.x feature — it is present in v3.6.0, v3.7.0
and v3.8.0 alike. It is **currently dead**: as of 2026-09-14 it returns HTTP 404
(a 27,150-byte HTML page) for every path tried, including a 2024 session path and
the 2026-09-13 Spanish GP race path that the primary serves with 200. So the
datacenter-IP problem has **no working in-library workaround today**, and the
local-extract / CI-build split stands.

FullThrottle is also not evidence that this corpus fits GitHub Pages: its frontend
is SvelteKit with D3, its data origin is a Hugging Face dataset, and its hosting
is Cloudflare, not Pages.

### Rate limiting

From `fastf1/req.py`: a `_MinIntervalLimitDelay(0.25)` floor (≥ 250 ms between
requests) applies to everything, plus **200 calls/hour for `jolpi.ca`** and
**500 calls/hour for other APIs**, enforced by `_CallsPerIntervalLimitRaise`,
which raises `RateLimitExceededError`. Cached requests do not count.

## 3. Caching

FastF1's cache is two-tier: an HTTP cache in SQLite (`fastf1_http_cache.sqlite`
in the cache root, 12-hour default cache-control expiry) and parsed data pickled
as `.ff1pkl` files in a `year/round/event/session` hierarchy.

```python
fastf1.Cache.enable_cache(cache_dir, ignore_version=False,
                          force_renew=False, use_requests_cache=True)
fastf1.Cache.get_cache_info()      # -> (cache_path, size_bytes) or (None, None)
fastf1.Cache.offline_mode(enabled) # "no actual requests will be sent"
fastf1.Cache.clear_cache(cache_dir=None, deep=False)
fastf1.Cache.set_disabled() / set_enabled()
```

**Cache directory resolution order**, which matters for reproducibility:

1. the path passed to `enable_cache()`
2. the **`FASTF1_CACHE` environment variable**
3. the OS default (Linux `~/.cache/fastf1`, falling back to `~/.fastf1` if
   `~/.cache` is unavailable)

`FASTF1_CACHE` is the cleanest CI/reproducibility lever and should be set
explicitly rather than relying on an OS default.

Three operating rules:

- Keep the FastF1 cache **outside the repo and outside `actions/cache`**. The
  Actions cache quota is 10 GB per repository with 7-day eviction, and a full
  season of `.ff1pkl` is large enough to be a bad tenant. (The frequently quoted
  "20–50 MB per race, 3–8 GB per season" figures are **unverified** — they come
  from a docs mirror and no measurement method is stated. The measured *raw
  download* is 21 MB per race.)
- Run transform and emit under `Cache.offline_mode(True)` so the build is a pure
  function of the on-disk cache. Log `Cache.get_cache_info()` in the build log.
- Record `fastf1.__version__` alongside the cache. `ignore_version` defaults to
  `False` for a reason — reusing a cache written by a different FastF1 version is
  documented as "Not recommended — incompatible cached data may cause crashes or
  errors" — so a FastF1 bump silently invalidates every `.ff1pkl` you have.

## 4. The other two sources

**Ergast is dead** — it shut down at the start of 2025 and must not be referenced
anywhere in the codebase. `ergast.com/api/f1/2024/1/results.json` now returns 404.

**jolpica-f1** is the drop-in successor at `https://api.jolpi.ca/ergast/f1/`.
Documented limits: **burst 4 requests/second, sustained 500 requests/hour**
unauthenticated, with token access "currently in the process of being
implemented" — and the docs note the unauthenticated limits are likely to
*decrease* as tokens roll out, not rise. A custom User-Agent is **good practice,
not a requirement**: a request with an empty User-Agent returns 200. FastF1 sends
one anyway — `fastf1/ergast/interface.py` has
`BASE_URL = "https://api.jolpi.ca/ergast/f1"` and
`HEADERS = {"User-Agent": f"FastF1/{__version_short__}"}`.

Access is through `fastf1.ergast` (there is no `fastf1.jolpica` module): class
`Ergast(result_type=…, auto_cast=…, limit=…)`, returning `ErgastRawResponse`,
`ErgastSimpleResponse` (one DataFrame) or `ErgastMultiResponse`
(`.description` + `.content`), all mixing in `ErgastResponseMixin` for
`.is_complete`, `.total_results` and `.get_next_result_page()`.

**F1DB** is the spine. Releases ship CSV, JSON, JSON-splitted, Smile, SQL
(MySQL/PostgreSQL/SQLite dumps), SQL with single inserts, and a SQLite database,
versioned CalVer `YYYY.RR.MICRO(.MODIFIER)` where RR is the round number (0 =
pre-season), "available as soon as possible after every race". It publishes a
JSON Schema at
`https://raw.githubusercontent.com/f1db/f1db/main/src/schema/current/single/f1db.schema.json`
(splitted distributions have their own under `/splitted`), so the historical side
validates for free before ingest. Licence CC BY 4.0; explicitly no telemetry.

**One F1DB trap that breaks naive pipelines:** its circuit SVGs are **not in the
release zips.** They exist only in the git repo at
`src/assets/circuits/{black,black-outline,white,white-outline}/<layoutId>.svg`.
A pipeline that downloads release artifacts gets zero SVGs; it must sparse-checkout
or raw-fetch per layout ID.

Decision rule: **F1DB = identity, results, standings, circuit SVG** (one versioned
download instead of ~1,100 rate-limited API calls, schema-validated);
**jolpica = gap-fill and cross-check only**, never redistributed;
**FastF1/livetiming = telemetry, 2018+**. The licence roles behind that split are
in the spec, and the correctness trap — jolpica collapsing retirement causes from
2024 onward — means all retirement-cause and laps-down analysis for 2024–2026
must come from F1DB.

## 5. Stage 2 — transform

Merge and resample onto **one uniform time grid for the whole session**, defined
once, rather than calling `resample_channels()` per driver. A single grid keeps
the binary layout rectangular and the manifest trivial. The grid choice, the
quantisation and the measured error are in
[Telemetry encoding](telemetry-encoding.md).

Validate the DataFrames coming out of FastF1 with pandera before anything is
written:

```python
import pandera.pandas as pa
from pandera.typing import Series

class LapsSchema(pa.DataFrameModel):
    Driver: Series[str]                     = pa.Field(str_length={'min_value': 3, 'max_value': 3})
    LapNumber: Series[float]                = pa.Field(ge=1)
    LapTime: Series['timedelta64[ns]']      = pa.Field(nullable=True)
    Compound: Series[str]                   = pa.Field(isin=['SOFT','MEDIUM','HARD','INTERMEDIATE','WET','UNKNOWN'])
    IsAccurate: Series[bool]

    @pa.check('LapTime')
    def plausible(cls, s):
        return s.isna() | ((s.dt.total_seconds() > 50) & (s.dt.total_seconds() < 300))
```

What this is actually catching, all observed upstream behaviours: `NaT` lap times,
a driver missing from a session, the 104 throttle/brake sentinel, negative
`TyreLife`.

Parquet writing, with the pyarrow setting that actually matters:

```python
pq.write_table(tbl, 'position.parquet',
    compression='zstd', compression_level=9,
    use_dictionary=False,                       # REQUIRED
    column_encoding={'t_ms': 'DELTA_BINARY_PACKED',
                     'x': 'DELTA_BINARY_PACKED',
                     'y': 'DELTA_BINARY_PACKED',
                     'z': 'DELTA_BINARY_PACKED'},
    sorting_columns=…, store_schema=True, write_page_index=True)
```

`version='2.6'` is **already the default** in pyarrow 25.0.1, so passing it
changes nothing. Only `use_dictionary=False` is required, and the failure is
loud rather than silent: `pyarrow/_parquet.pyx` raises
`ValueError("To use 'column_encoding' set 'use_dictionary' to False")`. One more
documented constraint: `column_encoding` **cannot be combined with
`use_byte_stream_split`** — pick one mechanism. Supported `column_encoding`
values are exactly `{'PLAIN', 'BYTE_STREAM_SPLIT', 'DELTA_BINARY_PACKED',
'DELTA_LENGTH_BYTE_ARRAY', 'DELTA_BYTE_ARRAY'}`; `'RLE'` raises
`OSError: RLE only supports BOOLEAN`.

## 6. Stage 3 — emit

Directory contract the site builds against, with measured sizes:

```
site/data/
  index.json                         # seasons, events, circuits, teams        ~50 KB
  circuits/<slug>.json               # metadata + RDP centreline (eps 0.25 m)  ~4 KB
  teams/<slug>.json                  # season-by-season aggregates             ~10 KB
  races/<year>-<slug>/
    race.json                        # results, grid, pits, RC messages        ~20 KB gz
    laps.json                        # columnar laps table                     ~15 KB gz
    replay.bin                       # int16 planar delta XY, 2 Hz default     623 KB
    replay.json                      # manifest: quantum, origin, t0, step,
                                     #   drivers[], byteOffsets{}, sha256      ~2 KB
    telemetry/<driver>.parquet       # per-driver full channels, on demand     ~100 KB each
  schema/<entity>.schema.json        # pydantic-generated JSON Schema
```

Initial race-page load at the 2 Hz default is **≈ 660 kB**; at 5 Hz it is
**≈ 1.4 MB**. The spec's default is 2 Hz, with 5 Hz fetched on demand when the
reader opens corner-level analysis.

Lap and results tables are so small that the only real decision is layout.
Measured on a realistic 1,040-row × 25-column laps table:

| Layout | Raw | gzip-9 |
| --- | ---: | ---: |
| Array of objects | 453,917 B | 31,840 B |
| Columnar `{col: [...]}` | 142,265 B | **15,276 B** |

Columnar wins three ways: 2.1× smaller gzipped, it is what charts want
(`Float64Array.from(data.LapTime)`), and it **diffs far better in git** — an
amended lap time changes one line of one array instead of shifting an object.
GitHub Pages gzips `application/json` on the wire automatically, so ship the
uncompressed `.json` and never commit a `.gz`.

Validate the emitted JSON with pydantic 2.13.5, and publish the schema as part of
the build output: `Model.model_json_schema()` → `site/data/schema/<entity>.schema.json`.
That single artifact does three jobs — it ships alongside the data, it generates
the front-end TypeScript types, and it is what CI re-validates against.

## 7. Stage 4 — verify

Four classes of assertion, because no single tool covers all of them.

1. **JSON** — `check-jsonschema` over every emitted file against the published
   schemas.
2. **Binary** — schema libraries cover none of this:
   - int16 deltas never saturate (real-data max |Δx| was **1,503** of 32,767);
   - `len(bin) == cars * channels * samples * 2`;
   - every manifest byte offset is **even** (an `Int16Array` view throws on a
     misaligned offset);
   - the recorded `sha256` per binary re-verifies at the end of the build.
3. **Metrics** — golden-file tests for every derived metric against hand-verified
   reference races. See [Build and release](build-and-release.md).
4. **Size** — total `site/` measured against the 1 GB Pages cap, failing well
   below it. See [GitHub Pages constraints](github-pages-constraints.md).

## 8. Reproducibility

Four cheap habits, each closing a specific hole.

**Toolchain.** Commit `uv.lock`; run CI with `uv sync --frozen`. `uv lock` is
deterministic across platforms and `uv export` produces `requirements.txt` or a
PEP 751 `pylock.toml`; `uv pip compile --generate-hashes` gives
`pip install --require-hashes` compatibility if belt-and-braces is wanted.

**Data.** Transform and emit run under `fastf1.Cache.offline_mode(True)`, so the
build is a pure function of the cache.

**Canonical output.** `json.dumps(obj, sort_keys=True, separators=(',', ':'),
ensure_ascii=False)` plus a fixed float-rounding step, so rebuilding an unchanged
race produces a byte-identical file and git shows no diff. Honour
`SOURCE_DATE_EPOCH` for any embedded timestamp. For Parquet, `store_schema=True`
and explicit `sorting_columns` keep the file self-describing.

**Provenance.** Every emitted JSON carries a `_provenance` object and every binary
a parallel `.meta.json`:

```json
{"source": "livetiming.formula1.com",
 "source_path": "/static/2024/2024-07-07_British_Grand_Prix/2024-07-07_Race/",
 "source_sha256": {"Position.z.jsonStream": "…", "CarData.z.jsonStream": "…"},
 "fastf1_version": "3.8.3", "pyarrow_version": "25.0.1",
 "pipeline_commit": "<git rev-parse HEAD>",
 "extracted_at": "2026-09-14T09:47:00Z",
 "grid": {"hz": 2, "quantum_m": 0.5, "t0_ms": 0},
 "encoding": "int16-delta-planar-xy"}
```

**Hashing the raw upstream bytes is the non-negotiable part.** Stewards amend
results after the fact — penalties, deleted laps, reinstated classifications —
and a changed `source_sha256` is the only reliable signal that a *past* race needs
rebuilding.

## 9. Orchestration and the incremental rule

**Plain Make plus a JSON manifest of content hashes.** The target graph maps
one-to-one onto the entity graph
(`site/data/races/%/replay.bin: data/interim/%/position.parquet`) and there are no
dependencies to install. Make's weakness is that it compares mtimes, not content,
so a fresh `git clone` or a cache restore makes everything look stale. Fix with
hash sentinels: write `build/.stamp/<target>.sha256` and have the rule `cmp` it
before rebuilding.

**DVC is the upgrade path**, adopted only when the raw cache outgrows git and a
`dvc remote` is wanted. Its `foreach` is exactly the right shape for a per-race
pipeline, and `dvc repro` decides by **content hash** recorded in `dvc.lock`
rather than mtime:

```yaml
stages:
  race:
    foreach: ${races}
    do:
      cmd: python -m pipeline.race ${item.year} ${item.round}
      deps:
        - pipeline/race.py
        - data/interim/${item.year}/${item.round}
      outs:
        - site/data/races/${item.year}-${item.round}
```

Stage keys accept `cmd`, `deps`, `outs`, `params`, `metrics`, `frozen`,
`always_changed`, `cache: false`, `persist`; each item expands to its own stage
(`race@2024-britain`). DVC's acknowledged gap is scheduling and error recovery.

**Prefect 3.8.5** (`>=3.10,<3.15`) runs flows locally with no server and buys
retries, conditional execution, concurrency limits and observability against a
flaky rate-limited API — but it has no content-addressed caching of file outputs,
so it cannot answer "is this race already built?". If API flakiness becomes a
problem, wrap only the **fetch** stage in it (or just `tenacity` plus the 250 ms
floor), and keep transform/emit declarative.

### Discovery and the rebuild predicate

The per-season `Index.json` is the incremental trigger — one small request:

| Season | Bytes | Meetings | Race-type sessions | Sessions |
| --- | ---: | ---: | ---: | ---: |
| 2018 | 26,216 | 20 | 20 | 100 |
| 2019 | 27,747 | 21 | 21 | 105 |
| 2020 | 22,151 | 17 | 17 | 83 |
| 2021 | 57,112 | — | — | — |
| 2023 | 30,500 | 23 | 30 | 116 |
| 2025 | 32,940 | 25 | 30 | 123 |
| 2026 (at 2026-09-14) | 20,415 | 16 | **14 named "Race"** | 76 |

Shape:

```json
{"Year":2018,"Meetings":[{"Sessions":[{"Key":5075,"Type":"Practice","Number":1,"Name":"Practice 1",
  "StartDate":"2018-04-06T14:00:00","EndDate":"2018-04-06T15:30:00","GmtOffset":"03:00:00"}]}]}
```

Two handling notes. **2022 returned a 111-byte body** on one fetch — retry and
handle it. And the 2026 gap between 16 meetings and 14 Race sessions is the two
pre-season test meetings: **any incremental build keyed on meetings rather than
Race sessions will double-count them.**

Total corpus is roughly **180–200 race sessions and ~870 sessions of all types
across 2018–2026** — small enough that a full rebuild is a weekend job and an
incremental one is minutes.

**A race is rebuilt if and only if:**

1. any entry in its `source_sha256` set changed, **or**
2. the pipeline commit touched a file in its dependency closure, **or**
3. the emitted manifest's `sha256` does not match the file on disk.

Otherwise it is skipped. For a normal race weekend that is one race directory out
of ~190.

**Fail loudly when stage 1's manifest is stale.** The failure mode to design
against is CI silently publishing an empty or half-built race, not CI erroring.

## Open items

- Whether the FastF1 mirror ever serves from a GitHub-hosted runner is
  **untested from CI**; it is 404 from everywhere tried today. A throwaway
  workflow would settle whether the local-extract constraint is permanent.
- The real X/Y extents of the largest circuits (Spa, Baku, Jeddah, Las Vegas) are
  **unmeasured**. Silverstone's 1,011 × 1,723 m fits int16 at 1/10 m easily, but a
  circuit exceeding 3.2 km on one axis would force per-circuit origin translation
  or int32.
- The actual on-disk size of the `.ff1pkl` parsed cache per session is
  **unverified**; it decides whether the cache can live on a laptop.
- How often F1 retroactively amends archive files is **uncharacterised**. The
  provenance design assumes `source_sha256` changes are rare signals; if files are
  rewritten on every stewards' decision, the pipeline churns.
- Whether qualifying and sprint sessions get replays is **undecided**. The size
  projection covers ~190 race sessions; all ~870 sessions at 2 Hz would be roughly
  540 MB and would force the data onto a separate repo or Releases.
