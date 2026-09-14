---
type: Reference
title: Session Formats and Weekend Structure
description: The canonical enumeration of F1 session types, the five FastF1 EventFormat values and their three distinct sprint orderings, and the exact 2026 qualifying and sprint qualifying timings.
resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_08_-_2026-08-05_7.pdf
tags:
  - domain-model
  - sessions
  - sprint
  - qualifying
  - fastf1
  - schema
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fia_2026_section_b
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_08_-_2026-08-05_7.pdf
    title: FIA 2026 Formula 1 Regulations — Section B (Sporting), Issue 08, 5 August 2026
  - id: fastf1_events
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/events.py
    title: FastF1 fastf1/events.py — EventFormat detection and session ordering
  - id: openf1_sessions_2026
    resource: https://api.openf1.org/v1/sessions?year=2026
    title: OpenF1 /v1/sessions for the 2026 season
  - id: f1_sprint_calendar_2026
    resource: https://www.formula1.com/en/latest/article/formula-1-and-fia-announce-2026-sprint-calendar.3PyLPAazrBNe8kQIS3wOfY
    title: Formula 1 and FIA announce the 2026 Sprint calendar
status: stable
---

# Session Formats and Weekend Structure

A race weekend is not one shape. Between 2021 and 2026 the sprint weekend was
re-ordered twice, and the site's schema has to carry all three orderings plus
the conventional weekend plus testing. This document is the enumeration the
ingest pipeline and the page templates key on.

## 1. The two 2026 session superclasses

The 2026 rulebook abstracts every session into one of two classes, and most of
Section B's procedural articles are written against the class, not the session.

| Class | Expansion | Members | Classified by |
| --- | --- | --- | --- |
| **LTCS** | Lap Time Classified Session | FP1, FP2, FP3, Sprint Qualifying, Qualifying | best single lap time |
| **TTCS** | Total Time Classified Session | Sprint, Race | total elapsed time / laps covered |

The split is load-bearing elsewhere: penalties differ by class (B1.9.4 for an
LTCS, B1.9.5 for a TTCS — see
[Championship edge cases](championship-edge-cases.md)), parc fermé windows open
on LTCS entry and close at TTCS start, and the safety car / VSC articles
(B5.12–B5.15) apply to TTCS only.

Appendix B1 also defines the weekend itself: *"'Alternative Format Competition'
(or 'AFC') is any Competition where a Sprint is scheduled."* A weekend with no
Sprint is a **Standard Format Competition (SFC)**.

## 2. Session code enum

From FastF1's `_SESSION_TYPE_ABBREVIATIONS` in `fastf1/events.py` — these are
the canonical short codes and the only ones the library will resolve.

| Code | Session name |
| --- | --- |
| `FP1` | Practice 1 |
| `FP2` | Practice 2 |
| `FP3` | Practice 3 |
| `SQ` | Sprint Qualifying |
| `SS` | Sprint Shootout |
| `S` | Sprint |
| `Q` | Qualifying |
| `R` | Race |

OpenF1 uses a different, coarser pair. Observed live for 2026 on
`/v1/sessions?year=2026`, the complete set of `(session_type, session_name)`
pairs is:

```
('Practice',   'Day 1')  ('Practice',   'Day 2')  ('Practice', 'Day 3')
('Practice',   'Practice 1')  ('Practice', 'Practice 2')  ('Practice', 'Practice 3')
('Qualifying', 'Qualifying')  ('Qualifying', 'Sprint Qualifying')
('Race',       'Race')        ('Race',       'Sprint')
```

**Trap:** OpenF1's `session_type` is `'Race'` for *both* the Grand Prix and the
Sprint. Never filter on `session_type` alone — filter on `session_name`.

## 3. The EventFormat enum

`fastf1.events` assigns exactly five values. The detection predicates are
literal and worth recording, because they are what breaks if F1 renames a
session again.

| `EventFormat` | Years | Detection predicate |
| --- | --- | --- |
| `testing` | any | event name contains `'test'`; `RoundNumber` is set to 0 |
| `conventional` | ≤2020, and every non-sprint event since | default when no sprint predicate matches |
| `sprint` | 2021–2022 | `sessions[3]['Name'] == 'Sprint'` |
| `sprint_shootout` | 2023 only | `sessions[2]['Name'] == 'Sprint Shootout'` |
| `sprint_qualifying` | 2024 onward, incl. 2026 | `sessions[1]['Name'] == 'Sprint Qualifying'` |

### Session ordering per format

There are **three distinct sprint orderings**, not four — 2021 and 2022 share
both an ordering and an enum value.

| Format | Session order |
| --- | --- |
| `conventional` | Practice 1 → Practice 2 → Practice 3 → Qualifying → Race |
| `sprint` (2021–22) | Practice 1 → **Qualifying** → Practice 2 → Sprint → Race |
| `sprint_shootout` (2023) | Practice 1 → Qualifying → **Sprint Shootout** → Sprint → Race |
| `sprint_qualifying` (2024+) | Practice 1 → **Sprint Qualifying** → Sprint → **Qualifying** → Race |
| `testing` | Day 1 → Day 2 → Day 3 |

### What actually changed between 2021 and 2022

The ordering did not. Three things did, and all three are page-visible:

- In 2021 the API named the session **`'Sprint Qualifying'`**; FastF1 renames it
  to `'Sprint'` in place. A 2021 session lookup by the string `'Sprint
  Qualifying'` therefore hits the *2021 Sprint*, not a 2024-style SQ segment.
- 2021 sprint points were **3-2-1** to the top three; from 2022 they are
  **8-7-6-5-4-3-2-1** to the top eight. See
  [Points systems](points-systems.md).
- In 2021 the **sprint winner was credited with pole position**. From 2022 pole
  reverted to the fastest driver in Friday qualifying.

### What changed in 2023 and 2024

- **2023** (`sprint_shootout`): the Sprint became a standalone event with its own
  short qualifying, and the Sprint result **no longer set the Race grid**.
- **2024 onward** (`sprint_qualifying`): FP1 + SQ on Friday, Sprint + Q on
  Saturday, Race on Sunday. This is the 2026 arrangement, and F1's own wording
  for it is that *"Sprint Qualifying takes place on Friday following Free
  Practice 1, with the Sprint and Grand Prix Qualifying on Saturday."*

Consequence for the schema: the grid-source relationship is format-dependent.

| Format | Sets the Sprint grid | Sets the Race grid |
| --- | --- | --- |
| `sprint` (2021–22) | Friday Qualifying | Sprint result |
| `sprint_shootout` (2023) | Sprint Shootout | Qualifying |
| `sprint_qualifying` (2024+) | Sprint Qualifying | Qualifying |

## 4. 2026 Race Qualifying — exact timings

Article B2.4.2, Section B Issue 08. The figures below are the clean black text
of Issue 06 and Issue 08.[^redline]

| Segment | Duration | Cars in | Eliminated | Break after |
| --- | ---: | ---: | ---: | ---: |
| Q1 | **18 min** | 22 | slowest **6** | 7 min |
| Q2 | **15 min** | 16 | slowest **6** | 7 min |
| Q3 | **13 min** | 10 | — | — |

At the end of Q1 the lap times of the 16 remaining cars are deleted; at the end
of Q2 the times of the 10 remaining cars are deleted. Q3 therefore starts from
a clean sheet.

[^redline]: A widely-circulated reading of an 8-minute break and a 12-minute Q3
    comes from the Issue 05 *redline* PDF, in which `pdftotext` flattens
    strikethrough: the raw text reads "After a seven (7) minute an eight (8)
    minute break … for thirteen (13) twelve (12) minutes". The struck half is
    the 8/12 proposal. Seven and thirteen are the values in force.

## 5. 2026 Sprint Qualifying — exact timings

Article B2.2.2.

| Segment | Duration | Cars in | Eliminated | Break after |
| --- | ---: | ---: | ---: | ---: |
| SQ1 | **12 min** | 22 | slowest **6** | 7 min |
| SQ2 | **10 min** | 16 | slowest **6** | 7 min |
| SQ3 | **8 min** | 10 | — | — |

Sprint Qualifying carries its own mandatory compound rules (new medium in SQ1
and SQ2, soft in SQ3) — see [Tyre compounds](tyre-compounds.md).

## 6. The elimination count is computed, not constant

Article B2.2.3 closes with the scaling rule verbatim:

> The procedures detailed in Articles B2.2.2 and B2.2.3 are based upon
> twenty-two (22) F1 Cars being eligible to take part in the Competition. If
> twenty (20) F1 Cars are eligible, five (5) F1 Cars will be eliminated after
> SQ1 and SQ2. If twenty-four (24) F1 Cars are eligible, seven (7) F1 Cars will
> be eliminated after SQ1 and SQ2, and so on if more F1 Cars are eligible.

```python
def eliminated_per_segment(cars_eligible: int) -> int:
    """Q3/SQ3 always holds ten cars; the rest are split evenly over two cuts."""
    return (cars_eligible - 10) // 2
```

With 11 teams and 22 cars, 2026 eliminates **six** per segment. Any page that
hardcodes five is wrong for the whole of 2026.

## 7. Segment-to-position mapping

Articles B2.4.3a (Qualifying) and B2.2.3a (Sprint Qualifying), for a 22-car
entry:

| Positions | Determined by |
| --- | --- |
| P1–P10 | Q3 / SQ3 times |
| P11–P16 | Q2 / SQ2 times |
| P17–P22 | Q1 / SQ1 times |

Identical times give priority to whoever set it first. Drivers who reach Q2 or
Q3 but set no time are ordered in three groups — (A) attempted a flying lap,
(B) failed to start a flying lap, (C) failed to leave the pits — each group
ordered by the previous segment's classification.

Drivers who end up "unclassified" (including via the 107% rule) are handled in
[Championship edge cases](championship-edge-cases.md).

## 8. Practice, and the intervals between sessions

Article B2.1 and the session-start articles B2.2.1 / B2.4.1, as recorded during
the research pass. These interval figures should be re-checked against the
current issue before they appear on a schedule page.

| Item | Standard Format | Alternative Format |
| --- | --- | --- |
| Practice sessions | FP1, FP2, FP3 | FP1 only |
| FP duration | 1 hour (1.5 hours when ICTT tyres are supplied) | 1 hour |
| FP1 → FP2 gap | 2–3 hours, same day | — |
| FP2 → FP3 gap | not less than 18 hours | — |
| Sprint Qualifying start | — | 2.5–3.5 hours after FP1 |
| Qualifying start | 2–3 hours after FP3 | 3–4 hours after the Sprint |

## 9. Distance and duration caps

| Session | Scheduled distance | Time cap | Extended cap with suspensions |
| --- | --- | --- | --- |
| Race | least whole number of laps exceeding **305 km** | 2 hours | 3 hours total |
| Race, Monaco | least whole number of laps exceeding **260 km** | 2 hours | 3 hours total |
| Sprint | least whole number of laps exceeding **100 km** | 1 hour | 1.5 hours total |

Articles B2.5.2 / B2.5.3 (Race) and B2.3.2 / B2.3.3 (Sprint). Both distance
articles carry the same reduction: if the formation lap started behind the
Safety Car, *"the number of Race laps will be reduced by the number of laps
carried out by the Safety Car minus one."*

The 2-hour signal is shown at the end of the lap *following* the lap during
which the two-hour period ended — so a race that hits the cap runs marginally
past it.

## 10. Schema recommendation

```jsonc
{
  "session_id": "2026-14-R",          // (season, round, session code)
  "event_format": "conventional",      // the five-value enum, stored per event
  "session_code": "R",                 // FastF1 abbreviation, not a display name
  "session_class": "TTCS",             // derived: LTCS | TTCS
  "is_alternative_format": false,      // derived: a Sprint is scheduled
  "cars_eligible": 22,                 // drives eliminated_per_segment()
  "scheduled_distance_km": 305,        // 260 at Monaco, 100 for a Sprint
  "start_utc": "2026-09-13T13:00:00Z", // always UTC…
  "circuit_tz": "Europe/Madrid",       // …with an explicit circuit timezone
  "is_cancelled": false                // OpenF1 carries this; two 2026 rounds need it
}
```

Three rules the pipeline enforces:

1. **`event_format` is stored, never inferred at render time.** The detection
   predicates depend on session *ordering*, which is only available from the
   event schedule, not from a single session record.
2. **Times are stored as UTC with an explicit circuit timezone** and always
   rendered with a visible label (SPEC §12.3). A schedule without a zone label
   is wrong for most of its readers.
3. **`cars_eligible` is per season**, and elimination counts derive from it.

## See also

- [Points systems](points-systems.md) — sprint and race scoring per era
- [Tyre compounds](tyre-compounds.md) — the SQ and Q3 mandatory-compound rules
- [Championship edge cases](championship-edge-cases.md) — classification, 107%, grid formation
- [The 2026 regulation reset](regulations-2026.md) — where these article numbers come from
