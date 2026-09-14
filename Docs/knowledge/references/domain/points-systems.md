---
type: Reference
title: Points Systems by Era
description: Every F1 championship points table from 1950 to 2026 with exact values and date ranges, including drop-scores, the fastest-lap point's two lives, sprint points, and the graduated partial-points scale.
resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_a_general_provisions_-_iss_03_-_2026-06-25.pdf
tags:
  - domain-model
  - points
  - championship
  - history
  - regulations
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fia_2026_section_a
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_a_general_provisions_-_iss_03_-_2026-06-25.pdf
    title: FIA 2026 Formula 1 Regulations — Section A (General Regulatory Provisions), Issue 03, 25 June 2026
  - id: wikipedia_points_systems
    resource: https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems
    title: List of Formula One World Championship points scoring systems
  - id: f1db_release
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 CSV release
status: stable
---

# Points Systems by Era

Raw championship points are **not comparable across eras**, and a site that
plots them on one axis from 1950 to 2026 is lying quietly. A win has been worth
8, 9, 10 and 25 points; for forty years only a driver's best *n* results
counted; for twenty-one years only a constructor's best-placed car scored. This
document is the lookup table that makes normalisation possible.

## 1. Drivers' Championship, by era

| Seasons | Points for P1…Pn | Fastest lap | Results counted |
| --- | --- | --- | --- |
| **1950–1959** | **8-6-4-3-2** (top **5**) | **+1** | best 4 (1950–53); best 5–6 (1954–59) |
| **1960** | 8-6-4-3-2-1 (top 6) | — | best 6 |
| **1961–1990** | **9-6-4-3-2-1** | — | drop-scores in force (e.g. best 11 of the season, 1982–90) |
| **1991–2002** | 10-6-4-3-2-1 | — | **all results count** — drop-scores abolished |
| **2003–2009** | 10-8-6-5-4-3-2-1 | — | all |
| **2010–2018** | 25-18-15-12-10-8-6-4-2-1 | — | all |
| **2019–2024** | 25-18-15-12-10-8-6-4-2-1 | **+1**, top-10 finishers only | all |
| **2025–** | 25-18-15-12-10-8-6-4-2-1 | — | all |

Two rows are where most published era tables go wrong:

- **Sixth place did not score before 1960.** From 1950 to 1959 the system paid
  the top *five* only, 8-6-4-3-2. A table that awards a point for sixth in, say,
  1955 produces wrong championship totals for six seasons.
- **A win was worth 9 points from 1961 to 1990**, uninterrupted. There is no
  10-8-6-5-4-3-2-1 era in the 1980s; that scale belongs to 2003–2009.

The canonical summary line is that *"Each Grand Prix winner tallied 8 points
from 1950 to 1960, 9 from 1961 to 1990, 10 between 1991 and 2009, and 25 since
2010."*

### One-off: 2014 double points

The final race of 2014 (Abu Dhabi) awarded **double points** — 50 for the win,
down to 2 for tenth. It applied to that single event and was never repeated.

## 2. The fastest-lap point has had two lives

| Period | Status | Condition |
| --- | --- | --- |
| 1950–1959 | awarded | 1 point to the driver setting the fastest lap |
| 1960–2018 | **not awarded** | — |
| 2019–2024 | awarded | 1 point, **only if the driver finished in the top 10** |
| 2025– | **abolished** | no fastest-lap bonus exists in the 2026 regulations |

The 2019–2024 top-10 condition is the detail that breaks naive recomputation: a
driver can hold the fastest lap of a race and score nothing for it.

There is no fastest-lap point anywhere in 2026 Article A2.2. The DHL Fastest Lap
Award still exists as a sponsor award with its own results page, but it carries
no championship points.

## 3. Constructors' Championship

The Constructors' Championship was **first awarded in 1958** — there is no
constructors' title for 1950–1957, and a lineage chart must render that period
as drivers-only.

Two structural rules separate it from the drivers' table:

- **Only the best-placed car of each constructor scored, through 1978.** From
  1958 to 1978 a 1–2 finish earned a constructor the same as a win-and-retire.
  Any "points per race" chart spanning 1958–2026 without normalisation
  systematically understates two-car strength in that period.
- **Dropped scores applied until 1990**, on the same principle as the drivers'
  championship though not always with the same limits.

1961 is a documented divergence: the drivers scored on 9-6-4-3-2-1 while the
**constructors scored on 8-6-4-3-2-1**. Per-season constructor scales and
drop-score limits between 1958 and 1990 are only medium-confidence in the
secondary literature; the project's practice is to trust **F1DB's per-race
`points` column** as the applied truth and treat the era table as documentation
of *why* a number looks the way it does, not as a recomputation engine.

## 4. Sprint points

| Seasons | Points | Positions paid |
| --- | --- | --- |
| **2021** | 3-2-1 | top 3 |
| **2022–2026** | **8-7-6-5-4-3-2-1** | top 8 |

Article A2.2.2 adds the distance gate, verbatim: *"If the leader has completed
two laps but less than 50% of the Scheduled Sprint Distance, no points will be
awarded."* At or above 50% the full 8-point scale applies — there is **no
graduated sprint scale**, only the single column.

In 2021 the sprint winner was also credited with **pole position**; from 2022
pole reverted to Friday qualifying. See
[Session formats](session-formats.md).

## 5. Shortened races

### 1980–2021: the binary half-points rule

If the leader completed at least two laps but less than **75%** of the scheduled
distance, **half points** were awarded; at 75% or more, full points.

The rule died at the **2021 Belgian Grand Prix**, where a single racing lap was
completed behind the safety car and half points were awarded on it. The
graduated table below replaced it from 2022.

### 2022 onward: the graduated table

The 2026 scale, verbatim from Article A2.2.1 (Section A Issue 03). Columns are
keyed on the percentage of the Scheduled Race Distance completed **by the
leader**.

| Position | ≥2 laps, <25% | 25% – <50% | 50% – <75% | ≥75% |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 6 | 13 | 19 | 25 |
| 2 | 4 | 10 | 14 | 18 |
| 3 | 3 | 8 | 12 | 15 |
| 4 | 2 | 6 | 10 | 12 |
| 5 | 1 | 5 | 8 | 10 |
| 6 | – | 4 | 6 | 8 |
| 7 | – | 3 | 4 | 6 |
| 8 | – | 2 | 3 | 4 |
| 9 | – | 1 | 2 | 2 |
| 10 | – | – | 1 | 1 |

**The 2026 table is not the 2022–2025 table.** Column 3 (50–75%) was changed:
P3–P8 now read **12-10-8-6-4-3** where the 2022–2025 version read
**12-9-8-6-5-3**. A single hardcoded graduated table applied across 2022–2026
will produce wrong numbers for any shortened race in one half of that range.
Store the scale per season.

### The precondition, which applies to every column

Article A2.2.1 opens: *"no points will be awarded unless a minimum of two
complete and consecutive laps have been completed by the leader without a Safety
Car or Virtual Safety Car procedure."* Two laps behind a safety car is not two
laps. The same precondition governs the Sprint under A2.2.2.

Note also that from 2023 the rule applies whenever the distance from start to
the end-of-session signal is less than scheduled, **regardless of whether there
was a red flag or a restart**.

## 6. Dead heats

Article A2.2.3, verbatim:

> Prizes and points awarded for F1 Cars that are tied for the same position
> will be added together and shared equally.

So two cars tied for 3rd in a full-distance race take (15 + 12) / 2 = 13.5 each,
and 5th place is then the next position awarded. This is why `points` must be
stored as a decimal, not an integer — half points from both this rule and the
pre-2022 shortened-race rule are real values in the historical record.

## 7. Championship tiebreak — countback

Article A2.1.4c: ties on total points are broken by **most wins**, then most
second places, then most thirds, and so on down the order. If drivers are still
tied, the same criteria are applied to their **qualifying results**.

This is a sort key, not a points adjustment, and it has to be implemented as one
— a standings table that sorts on points alone will render historically wrong
orders. See [Championship edge cases](championship-edge-cases.md).

## 8. Entry limits worth carrying

| Article | Rule |
| --- | --- |
| A2.1.2 | Maximum **24** Competitions, minimum **8**, in a Championship |
| A2.1.3 | No more than **24** F1 Cars, **two per team** |

2026 runs 23 rounds with 11 teams and 22 cars.

## 9. Schema

```jsonc
// on every race result row
{
  "points": 13.5,                       // decimal — dead heats and half points exist
  "points_scale_applied": "col3",       // full | col3 | col2 | col1 | half_legacy | none
  "scheduled_distance_pct_completed": 0.62,
  "fastest_lap_point_awarded": false    // only ever true 1950–59 and 2019–24
}
```

`points_scale_applied` is stored, not derived at render time. It is the field a
race page reads to print an honest caption — "half points" and "points awarded
on the 50–75% scale" are different statements about different regulations, and a
page that says only "shortened race" is hiding the interesting part.

**Normalisation for cross-era charts.** Raw points are never plotted against a
1950–2026 axis. Use one of:

- points as a **share of the total points available** that season;
- **rank-based** metrics — win rate, podium rate, average finishing position;
- **per-start** rates, with the denominator excluding non-starts (see
  [Championship edge cases](championship-edge-cases.md) for the positionText
  codes that must be excluded).

## See also

- [Session formats](session-formats.md) — sprint formats and what sets which grid
- [Championship edge cases](championship-edge-cases.md) — countback, half points in practice, shared drives
- [The 2026 regulation reset](regulations-2026.md) — where A2.2 sits in the six-section rulebook
- [Constructor lineage](team-lineage.md) — whose points these are, across renames
