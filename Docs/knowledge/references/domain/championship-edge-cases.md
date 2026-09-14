---
type: Reference
title: Championship Edge Cases
description: The messy history most F1 schemas ignore — shared drives, half points, the Indianapolis 500 as a championship round, two-constructor seasons, countback ties, retroactive amendments, the 107% rule and the 90% classification threshold.
resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
tags:
  - domain-model
  - classification
  - history
  - schema
  - stewards
  - data-quality
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_release
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 CSV release
  - id: fia_2026_section_a
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_a_general_provisions_-_iss_03_-_2026-06-25.pdf
    title: FIA 2026 F1 Regulations — Section A (General Regulatory Provisions), Issue 03, 25 June 2026
  - id: fia_2026_section_b
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_08_-_2026-08-05_7.pdf
    title: FIA 2026 F1 Regulations — Section B (Sporting), Issue 08, 5 August 2026
  - id: fastf1_core
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/core.py
    title: FastF1 fastf1/core.py — SessionResults and the ClassifiedPosition enum
  - id: jolpica_differences
    resource: https://raw.githubusercontent.com/jolpica/jolpica-f1/main/docs/ergast_differences.md
    title: jolpica-f1 — documented divergences from Ergast
  - id: project_spec
    resource: ../../../SPEC.md
    title: F1 Analysis project specification
status: stable
---

# Championship Edge Cases

Seventy-seven seasons of F1 contain a set of structural oddities that most
schemas quietly drop — and dropping them is how a reference site ends up with
championship tables that do not match the record books. The project's schema
accommodates all of them from the start (SPEC §6.4).

## 1. Shared drives

Before 1958, two drivers could share one car during a race and the result
attaches to the **drive**, not cleanly to either driver.

**The modelling rule: a result row belongs to a (race, car, driver) triple, not
to a (race, driver) pair.** F1DB supports this directly — `f1db-races-race-
results.csv` carries a **`sharedCar`** column alongside `driverId` and
`constructorId`, so a shared drive produces multiple result rows that reference
the same car.

Consequences for aggregation:

- A naive `COUNT(*) GROUP BY driverId` over-counts starts for the shared-drive
  era.
- Points for a shared car were divided between the drivers, which is one of
  several sources of fractional values in the `points` column. **Read the
  applied value from F1DB rather than recomputing it** — the division convention
  varied and per-row truth is more reliable than a reconstructed rule.
- A driver page for that era must render the shared drive *as* a shared drive,
  with both names. Silently attributing it to one driver is the failure mode.

## 2. The Indianapolis 500 as a championship round, 1950–1960

For eleven seasons the Indianapolis 500 counted as a round of the Formula One
World Championship (SPEC §6.4). It is modelled in F1DB as a normal round of
those seasons.

This is not a trivia note; it changes several site behaviours.

| Effect | Consequence |
| --- | --- |
| Round count | 1950s seasons have one more round than the European calendar suggests |
| Entity population | The entrant and constructor sets for those rounds are largely disjoint from the rest of the season |
| Circuit pages | Indianapolis Motor Speedway is an F1 championship circuit, and its layout and era differ from every other circuit of the period |
| Drop-scores | The event counts towards "best *n* results" like any other round (see [Points systems](points-systems.md)) |
| Charts | A championship-swing chart that omits it produces wrong cumulative totals |

The honest editorial treatment is to include the round and say what it was,
rather than to filter it out for tidiness.

## 3. A driver scoring for two constructors in one season

Mid-season driver moves are ordinary, and the schema handles them because
`constructorId` lives on the **result row**, not on a season-level driver record.

Two derived rules follow:

- **Driver-team membership is keyed on `(season, round)` at minimum**, and on
  `(session)` where session data exists. A `(year) → team` map is wrong.
  Verified case: at the 2026 Spanish Grand Prix the live driver list had Liam
  Lawson at Red Bull and Yuki Tsunoda at Racing Bulls, both contradicting the
  declared season lineup, following Isack Hadjar's wrist injury from the Dutch
  Grand Prix onward.
- **A team page renders its lineup as a timeline of driver stints with
  substitution markers**, not as a static two-driver card. That is both more
  accurate and more interesting. F1DB supports season granularity via
  `f1db-seasons-entrants-drivers.csv`; per-race granularity comes from the race
  results table.

Constructor-side attribution in the same season is symmetrical: a driver's
points split across two constructors count in full towards the drivers'
championship but towards two different constructors' totals.

## 4. Countback ties

Ties on points are **not** broken by a secondary numeric field. They are broken
by a comparison of the full result distribution.

Article A2.1.4c: most wins, then most second places, then most thirds, and so on
down the order. If still tied, the same criteria are applied to **qualifying
results**.

```python
def countback_key(results):
    """Sort key for a championship standings row. Higher is better,
    so negate for an ascending sort."""
    finishes = Counter(r.position for r in results if r.position is not None)
    quali    = Counter(r.grid_position for r in results if r.grid_position is not None)
    # positions 1..N in order: most wins first, then most 2nds, ...
    return (
        total_points(results),
        tuple(finishes[p] for p in range(1, MAX_POSITION + 1)),
        tuple(quali[p]    for p in range(1, MAX_POSITION + 1)),
    )
```

A standings table that sorts on points alone renders historically wrong orders.
The sort key above is implemented once and tested against known tied seasons as
a golden-file fixture (SPEC §12.3).

### Dead heats within one race

Article A2.2.3: *"Prizes and points awarded for F1 Cars that are tied for the
same position will be added together and shared equally."* The next position
awarded is the one after the tied pair. This is a second reason `points` is a
decimal column.

## 5. Half points and partial points

Covered in full in [Points systems](points-systems.md). The edge-case summary:

| Period | Rule |
| --- | --- |
| 1980–2021 | Binary — ≥2 laps to <75% of distance → **half points**; ≥75% → full |
| 2022–2025 | Graduated four-column table |
| 2026 | Graduated four-column table, **with different values in column 3** |

Every column, including full points, is gated by the same precondition: at least
two complete consecutive laps by the leader **without a Safety Car or Virtual
Safety Car procedure**.

The result is that "points scored" is not derivable from finishing position
alone for any shortened race in F1 history. Store `points_scale_applied` on the
result row.

## 6. Retroactive amendments

**Stewards amend results for days after a race.** This is not an exception; it
is normal operation, and it is the single largest correctness risk for a site
that publishes within hours of a chequered flag.

The project's position (SPEC §12.2):

1. **Every page carries a "data as of" stamp.**
2. **Races inside the amendment window render a "provisional classification"
   state** — a real designed state, not a tooltip.
3. **A human runs a local ingest after each race weekend**, because
   GitHub-hosted runners cannot reach the live-timing archive (datacenter IPs
   are blocked) and the free jolpica dump is 14 days delayed.
4. **Pages published within ~72 hours of a race may be factually wrong**, and
   the design says so rather than implying finality.

Schema:

```jsonc
{
  "classification_state": "provisional",   // provisional | final | amended
  "data_as_of": "2026-09-14T09:00:00Z",
  "amended_at": null,                      // set when a steward decision changes the result
  "amendment_note": null                   // short, factual, linked to the FIA document
}
```

An **amended** result keeps its history: the page states what changed and when,
because a permanent URL that silently mutates is the opposite of a reference.

## 7. The 107% rule

A qualifying-time threshold that produces an **"unclassified"** status, not a
ban. Article B2.4.3b, and identically B2.2.3b for Sprint Qualifying:

> Drivers will be considered to be "unclassified" in the following
> circumstances: i. If they got eliminated in Q1 and their best lap in Q1
> exceeded 107% of the fastest lap time set during Q1, unless the track was
> declared wet by the Race Director. ii. If they failed to set a lap time in Q1,
> or if all their lap times were deleted. iii. If they got disqualified by the
> Stewards.

Ordering within the unclassified group: drivers from (i) and (ii) are placed
ahead of those from (iii), each group ordered by *"the last LTCS in which all
such Drivers participated during the relevant Competition"* — 2026 wording,
which replaces the older FP3 / FP1 references.

Participation is then a stewards' decision: *"The participation of unclassified
drivers in the remainder of the Competition will be determined in each case by
the Stewards, who may exceptionally consider parameters such as a suitable lap
time being set in another practice session, the general performance of the
driver in previous Competitions of the Championship, or the gravity of the
offence."* Permitted drivers start **behind all classified drivers**
(B2.5.4 / B2.3.4b(v)).

### Discontinuous history

| Period | Status |
| --- | --- |
| 1996–2002 | In force |
| 2003–2010 | **Absent** — single-lap, race-fuel qualifying made it meaningless |
| 2011– | Reinstated with the return of low-fuel Q1/Q2/Q3 and the new HRT/Virgin/Lotus entries; in force since |

A page that applies a 107% annotation to a 2006 qualifying session is wrong.
The rule's applicability is a per-season fact.

## 8. Race and Sprint classification — the 90% threshold

Articles B2.5.5 (Race) and B2.3.5 (Sprint):

> The F1 Car placed first will be the one having covered the scheduled distance
> in the shortest time, or, where appropriate, passed the Line in the lead at
> the end of two (2) hours… All F1 Cars will be classified taking into account
> the number of complete laps they have covered, and for those which have
> completed the same number of laps, the order in which they crossed the Line.

And the threshold:

> F1 Cars having covered less than 90% of the number of laps covered by the
> winner (rounded down to the nearest whole number of laps), will not be
> classified.

```python
def is_classified(laps_completed: int, winner_laps: int) -> bool:
    """Note: the floor applies to the THRESHOLD, not to the driver's laps."""
    return laps_completed >= math.floor(0.9 * winner_laps)
```

The rounding detail matters. With a 57-lap winner the threshold is
`floor(51.3) = 51` laps, not 52.

## 9. Result status codes — three incompatible vocabularies

### FastF1 `ClassifiedPosition`

Verbatim from `fastf1.core.SessionResults`: *"either an integer value if the
driver is officially classified or one of `"R"` (retired), `"D"` (disqualified),
`"E"` (excluded), `"W"` (withdrawn), `"F"` (failed to qualify) or `"N"` (not
classified)."*

Pair it with the free-text `Status` column (`Finished`, `+1 Lap`, `Accident`,
`Gearbox`, …). `SessionResults` has **22 columns**, and there is no
`DriverColor` among them.

### F1DB `positionText`

Non-numeric values across the whole 27,599-row results table:

| Code | Count | Meaning |
| --- | ---: | --- |
| `DNF` | 8,776 | did not finish |
| `DNQ` | 1,041 | did not qualify |
| `DNS` | 381 | did not start |
| `DNPQ` | 338 | did not pre-qualify |
| `NC` | 200 | not classified |
| `DSQ` | 161 | disqualified |
| `EX` | 15 | excluded |
| `DNP` | 5 | did not practise |

**Denominator rule for any rate metric:** exclude `DNQ`, `DNPQ`, `DNP` and `DNS`
from the starts denominator — those cars never started. Treat `DNF` and `NC` as
retirements. Track `DSQ` and `EX` separately as a compliance metric rather than
folding them into reliability.

### Ergast / jolpica `positionText`

jolpica uses **`R`** where Ergast used `N`. More seriously, its status
vocabulary collapses:

| Season | Distinct statuses returned |
| ---: | ---: |
| 2010 | 35 |
| 2018 | 28 |
| **2024** | **5** |
| 2025 | 5 |
| 2026 | 4 |

2024 already returns only `Finished / Lapped / Retired / Did not start /
Disqualified`. The documentation says the collapse begins in 2025; **the data
says 2024**. The granular `+1 Lap` … `+N Laps` statuses are also flattened into
a single `Lapped`, so lap-down margin is lost over the same range.

**Therefore all retirement-cause and laps-down analysis for 2024–2026 comes from
F1DB**, whose `reasonRetired` field retains 15 / 14 / 20 distinct causes for
2024 / 2025 / 2026 respectively (SPEC §6.2).

## 10. Penalties that change a classification after the flag

Penalties are a closed enum in Article B1.9.5 for a TTCS: 5-Second Penalty;
10-Second Penalty; Drive-Through Penalty; Stop-and-Go Penalty (10 s stationary);
a time penalty; a driver reprimand; a competitor reprimand; a drop of any number
of grid positions for the next Sprint or Race within twelve months;
disqualification; suspension from the next Competition.

The conversions in B1.9.6 are what actually mutate a results table:

| Unserved penalty | Added to elapsed time |
| --- | ---: |
| 5-Second Penalty | **+5 s** |
| 10-Second Penalty | **+10 s** |
| Drive-Through Penalty | **+20 s** |
| Stop-and-Go Penalty | **+30 s** |
| Any outstanding penalty when a session is suspended and cannot restart | **+30 s** |

A Drive-Through or Stop-and-Go must be served within two crossings of the Line
from notification; if imposed in the last three laps, the driver may cross the
Line three times and the time addition applies instead.

Reprimand escalation (B1.9.5f): the **fifth** reprimand in a Championship, at
least four of them for driving infringements, triggers a **ten-place grid
penalty** for the Race at that Competition.

Super Licence points (A3.3.1b): **12 points in a rolling 12 months** suspends a
driver for the next Competition, after which 12 points are removed; points
otherwise expire on their 12-month anniversary.

No appeal lies against B1.9.5(a)–(h), grid drops under B8.2, penalties under
B1.9.4, or grid-formation decisions under B2.3.4 / B2.5.4.

## 11. Grid formation is an algorithm, not subtraction

Article B2.5.4b (Race) and the identical B2.3.4b (Sprint). Five steps, in order,
starting from a nominally empty grid:

1. Classified drivers with **15 or fewer** cumulative unserved grid penalties
   imposed in the previous twelve months get a **temporary** grid position equal
   to their qualifying classification **plus** the sum of their unserved
   penalties. Ties on a temporary position are resolved by qualifying
   classification, with the slowest driver keeping the position and the others
   placed immediately ahead.
2. Unpenalised classified drivers are allocated any unoccupied grid position, in
   qualifying order.
3. Penalised drivers with a temporary position are **moved up** to fill any
   unoccupied position.
4. Classified drivers with **more than 15** cumulative unserved grid penalties
   start **behind every other classified driver**, ordered by qualifying
   classification.
5. Unclassified drivers permitted to participate are placed behind all
   classified drivers.

Power-unit grid penalties (B8.2.8): **ten places** the first time an additional
element of each type is used, **five places** each subsequent time, cumulative.

Publication timings: provisional grid at least **2 hours** before the scheduled
formation lap; a competitor unable to start must notify the stewards no later
than **1¼ hours** before; the final grid is published **1 hour** before.
Withdrawals before the deadline **close the grid up**; withdrawals after it
**leave the slot vacant** — which is why a grid can have gaps, and why a grid
render must handle a missing position rather than re-indexing.

## See also

- [Points systems](points-systems.md) — drop-scores, the partial-points table, countback values
- [Session formats](session-formats.md) — qualifying segment structure and classification mapping
- [Track status and flags](track-status-and-flags.md) — the steward message grammar that announces these penalties
- [The 2026 regulation reset](regulations-2026.md) — where these article numbers now live
- [Constructor lineage](team-lineage.md) — attribution across renames and mid-season changes
