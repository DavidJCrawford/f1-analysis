---
type: Reference
title: Track Status, Flags and Race Control
description: The FastF1 numeric track status enum, the marshalling-sector flag semantics, and the literal grammar of race control messages including the 2026 shift from DRS to Overtake.
resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
tags:
  - domain-model
  - track-status
  - flags
  - race-control
  - safety-car
  - fastf1
  - openf1
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_api
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
    title: FastF1 fastf1/_api.py — track_status_data() and race_control_messages()
  - id: fastf1_docs_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API reference
  - id: openf1_race_control
    resource: https://api.openf1.org/v1/race_control
    title: OpenF1 /v1/race_control
  - id: openf1_docs
    resource: https://openf1.org/docs
    title: OpenF1 API documentation
  - id: fia_2026_section_b
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_08_-_2026-08-05_7.pdf
    title: FIA 2026 Formula 1 Regulations — Section B (Sporting), Issue 08, 5 August 2026
status: stable
---

# Track Status, Flags and Race Control

Almost every lap-based metric on this site depends on knowing whether a lap was
run under green. Two independent channels carry that information — a numeric
**track status** interval series, and a typed **race control message** event
stream — and they disagree in useful ways.

## 1. The TrackStatus enum

Verbatim from `fastf1/_api.py`, `track_status_data()`:

| Code | Meaning | `Message` value |
| --- | --- | --- |
| `'1'` | Track clear — beginning of session, or the end of another status | `AllClear` |
| `'2'` | Yellow flag (sectors are unknown at this level) | `Yellow` |
| `'3'` | **Does not exist.** The docstring reads *"??? Never seen so far, does not exist?"* | — |
| `'4'` | Safety Car | `SCDeployed` |
| `'5'` | Red Flag | `Red` |
| `'6'` | Virtual Safety Car deployed | `VSCDeployed` |
| `'7'` | Virtual Safety Car ending — as shown on the steering wheel and on TV; status `'1'` marks the actual end | `VSCEnding` |

Returned channels: `Time` (`datetime.timedelta`, session timestamp), `Status`
(numeric code **as a string**), `Message` (the human word above).

**It is an interval series.** A value is emitted only on change, so a status
holds until the next record. Resampling it to per-lap or per-sample requires
forward-fill; `Telemetry.add_track_status()` does this and adds a per-sample
numeric `TrackStatus` channel.

### The concatenation trap

`Laps['TrackStatus']` is **not** one of the codes above. It is the
**concatenation of every code seen during that lap**, as a string.

| Value | Means |
| --- | --- |
| `'1'` | green for the whole lap |
| `'24'` | saw a yellow, then a safety car |
| `'241'` | yellow, safety car, then clear |
| `'146'` | clear, safety car, VSC deployed |

```python
# correct clean-lap filter
clean = laps[laps["TrackStatus"] == "1"]

# WRONG — silently returns nothing, the column is a string
clean = laps[laps["TrackStatus"] == 1]

# WRONG — '241' contains '1' and would pass
clean = laps[laps["TrackStatus"].str.contains("1")]
```

Every metric in [`/methods/`](../../metrics/index.md) that claims a "green-flag"
denominator uses the exact `== '1'` test, and the golden-file fixtures assert
it.

## 2. SC and VSC semantics

The 2026 articles are B5.12 (Virtual Safety Car), B5.13 (Safety Car), B5.14
(Suspension) and B5.15 (Resumption), all within B5 — Total Time Classified
Sessions, so they apply to the Race and the Sprint only.

Three consequences the data model must carry:

- **Points eligibility.** Article A2.2.1 requires two complete consecutive laps
  by the leader *"without a Safety Car or Virtual Safety Car procedure"* before
  any points are awarded. Laps behind the safety car do not count towards it.
  See [Points systems](points-systems.md).
- **Race distance.** If the formation lap starts behind the Safety Car, the
  scheduled lap count is reduced by *(safety car laps − 1)* — B2.5.2a and the
  identical B2.3.2 for the Sprint.
- **Overtake availability.** B7.2.2c disables Overtake when the Safety Car is
  deployed, and re-enables it **per car** after the SC returns to the pit lane.
  In 2026 this is visible in the message stream as `OVERTAKE DISABLED` /
  `OVERTAKE ENABLED` (see §5).

Pit-stop loss under SC and VSC is **circuit-specific and spans roughly 12–82% of
green-flag loss** — the site never quotes a single global figure (SPEC §7).

## 3. Three kinds of "sector"

These are three different partitions of the same lap and they are routinely
conflated.

| Partition | Count | Used for |
| --- | --- | --- |
| **Timing sectors** | 3 | `Sector1Time`/`Sector2Time`/`Sector3Time`, purple/green sector times |
| **Marshalling sectors** | ~16–20 per circuit | **flag scope** — `YELLOW IN TRACK SECTOR 10` |
| **Mini-sectors** | ~20–30 | segment dominance colouring on a track map |

Flag messages are scoped to **marshalling sectors** (`scope: 'Sector'`, `sector:
10`), never to timing sectors. Bahrain has 18 marshalling sectors; Singapore has
16. Geometry for them comes from the MultiViewer circuit API's `marshalSectors[]`
array, alongside a separate equal-length `marshalLights[]` array — two distinct
keys, same shape. That API is **blocked pending terms clarification** (SPEC
§13.3), so marshalling-sector geometry is not currently renderable.

### The flag obligations, from B1.8.4

Supplementing ISC Appendix H Art. 2.5.5b:

| Flag | Obligation |
| --- | --- |
| **Single waved yellow** | *"must reduce their speed and be prepared to change direction … they are expected to have braked earlier and/or discernibly reduced speed in the relevant marshalling sector"* |
| **Double waved yellow** | *"must reduce speed significantly and be prepared to change direction or stop … it must be clear that the driver has not attempted to set a meaningful lap time on the relevant lap"* — and **in SQ or Q that lap time is deleted** |
| **Double waved yellow during SC/VSC** | *"must stay above the minimum time set by the FIA ECU in each marshalling sector concerned"* |

The automatic lap deletion under double yellow in qualifying is the reason a
qualifying page cannot simply take the driver's fastest recorded lap: deleted
laps are flagged in `Laps['Deleted']` with a `DeletedReason`, and must be
excluded.

## 4. The race control message model

| FastF1 field | OpenF1 field | Notes |
| --- | --- | --- |
| `Utc` | `date` | message timestamp |
| `Category` | `category` | see enum below |
| `Message` | `message` | the literal upper-case text |
| `Status` | — | e.g. `'DISABLED'` |
| `Flag` | `flag` | flag colour |
| `Scope` | `scope` | `Track`, `Sector`, `Driver` |
| `Sector` | `sector` | marshalling sector number |
| `RacingNumber` | `driver_number` | |
| `Lap` | `lap_number` | |
| — | `qualifying_phase` | **OpenF1 only**, values 1/2/3 — absent from FastF1's model |
| — | `meeting_key`, `session_key` | |

### The category enum has shrunk

Measured, not documented. Sampling six 2024 Races via OpenF1 `/v1/race_control`:

```
{Other: 194, Flag: 184, Drs: 17, SessionStatus: 14, SafetyCar: 14, CarEvent: 5}
```

Sampling **all 27 non-cancelled 2026 Race / Qualifying / Sprint sessions**:

```
{Flag: 1756, Other: 1035, SessionStatus: 110, SafetyCar: 47}
```

`Drs` and `CarEvent` are **gone**. FastF1's own docstring still lists
`'Other', 'Flag', 'Drs', 'CarEvent'` as the category set, so the library
documentation is ahead of nothing and behind the 2026 feed.

The 2026 replacement traffic — **29 `OVERTAKE ENABLED` and 19 `OVERTAKE
DISABLED`** messages across those sessions — is emitted under category
**`Other`**, with no dedicated category and no `Status` field. A parser that
looked for `Category == 'Drs'` to find overtaking-aid state transitions returns
an empty set for 2026.

| Enum | 2026 values observed |
| --- | --- |
| `category` | `Flag`, `Other`, `SessionStatus`, `SafetyCar` |
| `flag` | `GREEN`, `YELLOW`, `DOUBLE YELLOW`, `RED`, `CLEAR`, `CHEQUERED`, `BLUE`, `BLACK AND WHITE` |
| `scope` | `Track`, `Sector`, `Driver` |

## 5. Message grammar

The `Message` field is free text in principle and a small set of templates in
practice. These are the real 2026 shapes, with `N` standing for a digit run and
`XXX` for a three-letter driver code. They are regex-parseable into structured
incident records.

### Flags and sectors

```
WAVED BLUE FLAG FOR CAR N (XXX) TIMED AT N:N:N
CLEAR IN TRACK SECTOR N
YELLOW IN TRACK SECTOR N
DOUBLE YELLOW IN TRACK SECTOR N
TRACK SURFACE SLIPPERY IN TRACK SECTOR N
TRACK CLEAR
RED FLAG
CHEQUERED FLAG
FIRST CAR TO TAKE THE FLAG - CAR N (XXX)
```

### Session and pit lane

```
SESSION STARTED
SESSION FINISHED
SESSION ABORTED
GREEN LIGHT - PIT EXIT OPEN
PIT EXIT CLOSED
PIT LANE ENTRY CLOSED
QN WILL START AT N:N
QN WILL RESUME AT N:N
RISK OF RAIN FOR THE F1 RACE IS N%
```

### Interventions

```
SAFETY CAR DEPLOYED
SAFETY CAR IN THIS LAP
VSC DEPLOYED
VSC ENDING
MEDICAL CAR DEPLOYED
MARSHALS ON TRACK AT TURN N
RECOVERY VEHICLE ON TRACK AT TURN N
OVERTAKE ENABLED
OVERTAKE DISABLED
```

### Lap deletions

```
CAR N (XXX) TIME N:N.N DELETED - TRACK LIMITS AT TURN N LAP N
```

### Stewards

Two families, both worth structuring:

```
FIA STEWARDS: [QN ]INCIDENT INVOLVING CAR N (XXX) {verdict} - {reason}
FIA STEWARDS: N SECOND TIME PENALTY FOR CAR N (XXX) - {reason}
FIA STEWARDS: STOP-AND-GO PENALTY FOR CAR N (XXX) - {reason}
FIA STEWARDS: PENALTY SERVED - ...
```

| Verdicts observed | Reasons observed |
| --- | --- |
| `NOTED` | `CAUSING A COLLISION` |
| `UNDER INVESTIGATION` | `TRACK LIMITS AT TURN N` |
| `WILL BE INVESTIGATED AFTER THE SESSION` | `DOUBLE YELLOW AT TURN N` |
| `REVIEWED NO FURTHER INVESTIGATION` | `UNSAFE CONDITION` |
| `NO FURTHER ACTION` | `STARTING PROCEDURE INFRINGEMENT` |
| `PENALTY SERVED` | `PIT LANE INFRINGEMENT` |
| | `FAILING TO FOLLOW RACE DIRECTORS INSTRUCTIONS - MAXIMUM DELTA TIME` |
| | `MOVING UNDER BRAKING` |

Neither list is closed. The parser stores the raw message alongside the parsed
fields and marks unrecognised shapes rather than dropping them — an incident
timeline that silently omits what it could not parse is the worst possible
failure mode for a reference site.

## 6. OpenF1 lap segment codes

Used for mini-sector colouring on `/v1/laps`:

| Code | Meaning |
| --- | --- |
| `0` | not available |
| `2048` | yellow sector |
| `2049` | green sector |
| `2051` | purple sector (session best) |
| `2064` | pit lane |
| `2050`, `2052`, `2068` | **undocumented** |

*"Segments are not available during races."* A live 2026 race lap returns only
`2048` and `2051`. The three undocumented values are an open question and are
rendered as "unknown" rather than guessed.

## 7. Practical notes on the feeds

- **OpenF1 rate-limits hard.** Rapid per-session fan-out returns HTTP 429. The
  free tier is 3 req/s and 30 req/min. Build-time ingest uses a limiter.
- **2026 sessions after roughly the Baku round return 404 rather than an empty
  array** on some endpoints — a 404 is not proof that a session had no messages.
- OpenF1 is a **build-time cross-check only** (CC BY-NC-SA; SPEC §6.1). Its
  values are never written to a published artifact.

## See also

- [Session formats](session-formats.md) — LTCS/TTCS, and which articles apply where
- [Points systems](points-systems.md) — the SC/VSC precondition on points
- [Championship edge cases](championship-edge-cases.md) — penalties, result codes, provisional classifications
- [The 2026 regulation reset](regulations-2026.md) — why DRS messages stopped
