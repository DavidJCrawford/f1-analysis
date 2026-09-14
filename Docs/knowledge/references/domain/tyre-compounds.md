---
type: Reference
title: Tyre Compounds and Allocation
description: Why the C-number compound ladder never appears in the timing feed, how the relative SOFT/MEDIUM/HARD labels map back to it, and the 2026 allocation, usage and dimension rules.
resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_08_-_2026-08-05_7.pdf
tags:
  - domain-model
  - tyres
  - pirelli
  - regulations
  - strategy
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
  - id: fia_2026_section_c
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_c_technical_-_iss_20_-_2026-08-05.pdf
    title: FIA 2026 Formula 1 Regulations — Section C (Technical), Issue 20, 5 August 2026
  - id: pirelli_2026_range
    resource: https://press.pirelli.com/the-range-of-compounds-for-the-2026-season-has-been-set/
    title: Pirelli — the range of compounds for the 2026 season has been set
  - id: fastf1_core
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/core.py
    title: FastF1 fastf1/core.py — Laps.pick_compounds and the Compound value set
  - id: openf1_stints
    resource: https://api.openf1.org/v1/stints?meeting_key=1294
    title: OpenF1 /v1/stints for the 2026 Spanish Grand Prix meeting
status: stable
---

# Tyre Compounds and Allocation

The single most common factual error on an F1 data site is a stint chart
labelled "C3". **No timing feed has ever exposed a C-number.** The compound
naming problem has two layers and only one of them is in the data.

## 1. The two-layer naming problem

**Layer 1 — the absolute ladder.** Pirelli manufactures a numbered range of dry
compounds, C0 (hardest) through C6 (softest, when it exists). A C3 is the same
rubber at Monza as at Silverstone.

**Layer 2 — the relative label.** At each event the FIA and Pirelli nominate
**three** of those compounds, which are then relabelled *for that weekend* as
Hard, Medium and Soft. The soft at one round can be physically harder than the
hard at another.

Every timing feed, and therefore every downstream API, exposes only layer 2.

| Source | Field | Values |
| --- | --- | --- |
| FastF1 | `Laps['Compound']` | `SOFT`, `MEDIUM`, `HARD`, `INTERMEDIATE`, `WET`, `UNKNOWN`, `TEST_UNKNOWN` |
| OpenF1 | `/v1/stints` → `compound` | same relative labels |

Measured, not assumed: a full sweep of OpenF1 `/v1/stints` across the entire
2026 Madrid meeting (`meeting_key=1294`) returns exactly
`{SOFT: 245, MEDIUM: 113, HARD: 30}` — no C-numbers anywhere.

### Consequence: the nominations table is our problem

To say "this was the C3" the site must join against a table it maintains
itself, sourced from Pirelli's per-event press releases:

```jsonc
// tyre_nominations.json — keyed (season, round)
{
  "2026-14": { "hard": "C3", "medium": "C4", "soft": "C5" }
}
```

```python
# joining a stint to an absolute compound
nom = nominations[(season, round_no)]
absolute = nom[stint.compound.lower()]        # 'SOFT' -> nom['soft'] -> 'C5'
```

No public API exposes this mapping. It is hand-maintained or scraped, per
event, for every season since the C-range began. Until a round is populated, a
stint chart shows the relative label only — which is honest, and is the
behaviour required by SPEC principle 3.

## 2. The C-range has changed shape

| Season(s) | Dry range | Note |
| --- | --- | --- |
| 2019–2022 | C1–C5 | five compounds |
| 2023–2024 | **C0**–C5 | C0 added as a super-hard above C1 |
| 2025 | C0–**C6** | C6 added as a new softest |
| **2026** | **C1–C5** | C6 dropped; five compounds |

Pirelli's stated reason for dropping C6 for 2026 is that *"the time gap between
the C5 and C6 prototypes was too small compared to the others."* A compound-name
axis that assumes a fixed ladder will mis-order any chart spanning 2022 to 2026.

## 3. Colours and wet-weather compounds

| Label | Sidewall | Kind |
| --- | --- | --- |
| Hard | white | slick |
| Medium | yellow | slick |
| Soft | red | slick |
| Intermediate | green | crossover, patterned |
| Full Wet | blue | standing water |

Colour coding is unchanged for 2026, as are the intermediate and full-wet
patterns. Pirelli's published water-dispersal figures for the 18-inch wets
circulate in several forms; the commonly published figure for the intermediate
is ~30 litres/second at 300 km/h, and the full wet substantially more. **Treat
specific dispersal figures as unverified** unless sourced to a current Pirelli
technical page — they are not needed for any chart the site draws.

Article B6.1.1a requires the supplier to bring, per Competition, *"three (3)
specifications of dry-weather tyre, one (1) specification of intermediate tyre,
and one (1) specification of wet-weather tyre. Each of which must be visibly
distinguishable."*

## 4. 2026 dimensions

| Dimension | 2025 | 2026 | Change |
| --- | ---: | ---: | ---: |
| Front tread width | 305 mm | **280 mm** | −25 mm |
| Rear tread width | 405 mm | **375 mm** | −30 mm |
| Rim diameter | 18 in | **18 in** | unchanged |

Pirelli states the narrowing as 2.5 cm at the front and 3 cm at the rear. The
corresponding FIA figures are in Technical Article **C10.7.2**, which gives 2026
rim tyre-mounting widths of **315 mm front / 401.3 mm rear** and a rim diameter
of **462.5–463 mm** (i.e. 18 inches, unchanged). Note those are rim mounting
widths, not tread widths — do not present them as the same quantity.

The narrower tyres are part of the same package as the ~15% downforce reduction
and the shorter, narrower car; see
[The 2026 regulation reset](regulations-2026.md).

## 5. Allocation per driver — three columns, not two

Article B6.2.4, sets per driver per Competition. The third column is the one
most models miss.

| Specification | Standard Format | Alternative Format (Sprint) | Standard Format **with ICTT** |
| --- | ---: | ---: | ---: |
| Hard | 2 | 2 | 2 |
| Medium | 3 | 4 | 3 |
| Soft | **8** | **6** | **7** |
| *Dry total* | *13* | *12* | *12* |
| Intermediate | 5 | 6 | 5 |
| Wet | 2 | 2 | 2 |

Maximum sets **usable** per driver, Article B6.3.4 (dry excludes evaluation and
test specifications):

| Specification | Standard | Alternative | Standard + ICTT |
| --- | ---: | ---: | ---: |
| Dry | 13 | 12 | 12 |
| Intermediate | 5 | 5 | 5 |
| Wet | 2 | 2 | 2 |

A site modelling only two formats will mis-count sets at the **up to three ICTT
events** per season.

### ICTE and ICTT

| Acronym | Expansion | Rule |
| --- | --- | --- |
| **ICTE** | In-Competition Tyre Evaluation | B6.1.1b — one extra dry specification at certain Standard Format events |
| **ICTT** | In-Competition Tyre Testing | B6.1.1c — at a **maximum of two** Standard Format Competitions, extendable to a third if weather spoils one |

## 6. What the FIA publishes, and when

Article B6.1.2b — two weeks before each Competition:

| Item | Rule |
| --- | --- |
| Which specifications are available | the three nominated compounds |
| Mandatory dry-weather **Race** specification(s) | **up to a maximum of two** |
| Mandatory dry-weather **Q3** specification | *"always being the softest of the three (3) specifications made available"* — Standard Format Competitions |

The mandatory-Q3-compound rule is new for 2026 and is a **separate per-event
field** from the mandatory race compound(s). Article B6.3.8a(i) backs it: one
set of the mandatory Q3 specification may not be used nor returned before Q3.

## 7. Usage rules

| Article | Rule |
| --- | --- |
| B6.2.2 | *"A complete set of tyres will be deemed to comprise two (2) front and two (2) rear tyres all of which must be of the same specification."* |
| B6.3.2 | A set counts as **used** once the transponder shows the car left the pit lane with them fitted, or left its grid slot under its own power |
| B6.3.5 | In free practice, intermediates and wets may only be used **after the track has been declared wet by the Race Director** |
| B6.3.6 | At least **two different dry specifications** must be used in the Race, at least one of which is a mandatory Race specification — unless intermediates or wets were used |
| B6.3.6 | **Monaco additionally** requires at least **three sets** of any specification |
| B6.3.7 | Wets are compulsory when a formation lap starts behind the Safety Car, until the SC orange lights go out |
| B6.3.9a(iv) | Sprint weekends: in **SQ1 and SQ2**, up to one set each, and it must be a **new set of the medium** |
| B6.3.9a(v) | Sprint weekends: in **SQ3**, up to one set, and it must be a set of the **soft** |

### Breach consequences

| Breach | Consequence |
| --- | --- |
| B6.3.6 two-compound rule | **Disqualification** |
| …if the race is suspended and cannot restart | **+30 s** elapsed time |
| …Monaco, suspended and cannot restart | **+30 s**, and a further **+30 s** for a driver who used only one set |
| B6.3.7 wets behind the safety car | **Stop-and-Go Penalty** |

Note that Monaco's old two-stop requirement is replaced for 2026 by the
three-sets-of-any-specification rule — a strategy page for Monaco 2026 must not
reuse the 2025 copy.

## 8. Schema

```jsonc
// per event
{
  "season": 2026,
  "round": 14,
  "format": "standard",              // standard | alternative | standard_ictt
  "compounds": { "hard": "C3", "medium": "C4", "soft": "C5" },   // hand-maintained
  "mandatory_race_specs": ["medium", "hard"],   // up to two
  "mandatory_q3_spec": "soft",                  // SFC only; always the softest
  "allocation": { "hard": 2, "medium": 3, "soft": 8, "inter": 5, "wet": 2 }
}

// per stint (from FastF1 Laps / OpenF1 stints)
{
  "driver": "LEC", "stint_number": 2,
  "compound_label": "MEDIUM",        // what the feed actually said
  "compound_absolute": "C4",         // null until the nominations table is populated
  "lap_start": 15, "lap_end": 34,
  "tyre_age_at_start": 0, "fresh_tyre": true
}
```

`compound_absolute` is **nullable and rendered as absent, not as a guess.** A
stint Gantt legend that reads "MEDIUM" is correct; one that reads "C4" without a
populated nomination is fabrication.

## See also

- [Session formats](session-formats.md) — where SQ1/SQ2/SQ3 and Q3 sit in the weekend
- [The 2026 regulation reset](regulations-2026.md) — the rest of the 2026 technical package
- [Track status and flags](track-status-and-flags.md) — wet declarations arrive as race control messages
- [Championship edge cases](championship-edge-cases.md) — tyre-rule disqualifications in the result codes
