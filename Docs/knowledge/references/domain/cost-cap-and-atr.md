---
type: Reference
title: Cost Cap and Aerodynamic Testing Restrictions
description: The 2026 financial regulations and the aerodynamic testing restriction regime, with exact caps, breach thresholds, the six unequal testing periods, and the documented enforcement record.
resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_d_financial_-_f1_teams_-_iss_07_-_2026-06-25.pdf
tags:
  - cost-cap
  - atr
  - fia
  - regulations
  - budget-cap-era
  - constructors
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fia_2026_section_d
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_d_financial_-_f1_teams_-_iss_07_-_2026-06-25.pdf
    title: FIA 2026 F1 Regulations — Section D (Financial Regulations, F1 Teams), Issue 07, 25 June 2026
  - id: fia_2026_section_f
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_f_operational_-_iss_10_-_2026-08-05.pdf
    title: FIA 2026 F1 Regulations — Section F (Operational Regulations), Issue 10, 5 August 2026
  - id: fia_reg_index
    resource: https://www.fia.com/regulation/category/110
    title: FIA regulation index — Formula 1 (Section E, Issue 06, 25 June 2026)
  - id: racefans_redbull_penalty
    resource: https://www.racefans.net/2022/10/28/red-bull-f1-budget-cap-penalty/
    title: Red Bull's 2021 cost cap breach and penalty
  - id: the_race_atr_2026
    resource: https://www.the-race.com/formula-1/the-aero-restrictions-each-f1-team-will-face-in-2026/
    title: The aerodynamic restrictions each F1 team will face in 2026
  - id: racingnews365_atr_2026
    resource: https://racingnews365.com/f1-2026-teams-wind-tunnel-time
    title: 2026 F1 teams' wind tunnel allocations
status: stable
---

# Cost Cap and Aerodynamic Testing Restrictions

Two handicap systems now shape a modern constructor's performance more than any
other regulation: a hard spending ceiling, and a sliding scale that grants the
slowest teams the most development bandwidth. Both live in sections of the 2026
rulebook that a three-section model of the regulations does not contain.

| Regime | Section | Issue | Dated |
| --- | --- | ---: | --- |
| Team cost cap | **D** — Financial Regulations, F1 Teams | 07 | 2026-06-25 |
| PU manufacturer cost cap | **E** — Financial Regulations, PU Manufacturers | 06 | 2026-06-25 |
| Aerodynamic Testing Restrictions | **F** — Operational Regulations | 10 | 2026-08-05 |

The ATR moved for 2026: they were **Appendix 7 of the Sporting Regulations** and
are now **Article F4**. A grep of Section B for "aerodynamic testing" returns
nothing.

## 1. The team cost cap

**USD 215,000,000.** Article D4.1.2, verbatim:

> (a) in the event that 24 Competitions or fewer take place … US Dollars
> 215,000,000 adjusted, if applicable, for Indexation; or (b) in the event that
> more than 24 Competitions take place … US Dollars 215,000,000, increased by an
> amount equivalent to US Dollars 1,800,000 multiplied by 'X', where 'X' is
> equal to the number of Competitions … minus 24.

Article D4.1.3 gives the illustrative 2026 currency conversions, in thousands:

| USD | GBP | EUR | CHF |
| ---: | ---: | ---: | ---: |
| 215,000 | 170,090 | 198,663 | 189,992 |

**The cap does not fall when races are cancelled.** 2026 lost two Grands Prix
and still runs under the 24-or-fewer clause at the full USD 215,000,000. A page
that scales the cap by rounds held is wrong.

### 2026 accounting changes

These inflate the headline number relative to earlier seasons and must be noted
wherever the cap is compared year over year:

| Change | Effect |
| --- | --- |
| The separate **CapEx cap** (previously USD 36m over a rolling 4 years) was removed, and annual depreciation pulled **inside** the main cap | raises the effective figure |
| Any staff member spending time on the F1 programme must be **charged fully** to it | raises reported costs |
| **Newly excluded:** health and safety costs; catering at factories and events | lowers reported costs |
| **Still excluded:** driver salaries; the three highest-paid personnel; marketing; HR; legal; travel | unchanged |

## 2. The power unit manufacturer cap

Article E2.3.1, verbatim:

> (a) in each of a Power Unit Manufacturer's N-3, N-2 and N-1 Full Year
> Reporting Period, US Dollars 148,500,000, adjusted for Indexation; and (b) in
> the Full Year Reporting Period ending on 31 December in the year of a Power
> Unit Manufacturer's Inaugural Season and in each subsequent … US Dollars
> 190,000,000, adjusted for Indexation.

So it is **two figures, not one**: USD 148,500,000 in the three reporting
periods before a manufacturer's inaugural season, and USD 190,000,000 from the
inaugural season onward.

2026 conversions, in thousands:

| USD | GBP | EUR | JPY |
| ---: | ---: | ---: | ---: |
| 190,000 | 152,918 | 180,420 | 24,967,900 |

The widely-cited press figure of "$130m" is not the regulation value. Cite the
regulation.

## 3. Breach taxonomy and sanctions

| Article | Breach | Threshold |
| --- | --- | --- |
| D10.3.1 | **Minor Overspend Breach** | Relevant Costs exceed the cap by **less than 2%** |
| D10.3.3 | **Material Overspend Breach** | **2% or more** |
| — | **Procedural Breach** | a reporting or process failure, not an overspend |
| — | **Non-Submission Breach** | failure to file |

D10.3.4: a Material Overspend Breach **shall** attract a Constructors'
Championship points deduction under D12.1.1.c.i, plus a Financial Penalty.

> **The 2% threshold is the 2026 definition and cannot be applied
> retroactively.** The 2021 Financial Regulations defined a Minor Overspend
> Breach as **less than 5%** of the cap. Any page describing the 2021 cycle must
> use the 2021 threshold.

Sanction menu, Article D12.1.1:

| Tier | Available sanctions |
| --- | --- |
| **(a) Financial Penalty** | a fine |
| **(b) Minor Sporting Penalty** | public reprimand; Constructors' points deduction; Drivers' points deduction; suspension from parts of a Competition **excluding** the race or Sprint; limitations on aerodynamic or other testing; reduction of the Cost Cap |
| **(c) Material Sporting Penalty** | all of the above, plus suspension from an **entire** Competition including the race, and exclusion from the Championship for a specified period |

The mechanism for resolving a breach without adjudication is an **Accepted
Breach Agreement (ABA)**, offered by the Cost Cap Administration under Section
D. If accepted, the Cost Cap Adjudication Panel publishes the decision and its
grounds, minus Confidential Information — which makes enforcement outcomes a
small but genuinely citable dataset.

## 4. Enforcement record

Short, and worth getting exactly right.

| Cycle | Party | Finding | Sanction |
| --- | --- | --- | --- |
| 2021 | **Red Bull** | a **Procedural Breach** *and* a **Minor Overspend Breach** — Relevant Costs exceeded the cap by **£1.864m**, or **1.6%**, under the then-applicable **5%** Minor threshold | **USD 7,000,000** fine, payable within 30 days, plus a **10% reduction in aerodynamic testing allowance** for the 12 months from the ABA |
| 2021 | **Aston Martin** | Procedural breach of the 2021 regulations | **USD 450,000** fine |
| 2024 review | all 10 teams, all 5 PU manufacturers | No team or PU manufacturer exceeded the cap | — |

So the October 2022 enforcement round produced **at least three actions**, not
one — Red Bull's two findings and Aston Martin's separate procedural fine. An
earlier procedural-breach finding also applied to Alpine and to Honda as a PU
manufacturer.

The FIA recorded that Red Bull acted "in good faith", and the USD 7m fine is
commonly cited as among the largest financial penalties in F1 history.

**Marked unverified:** an Aston Martin procedural breach arising from the 2024
review, said to have been resolved by an Accepted Breach Agreement dated 29
September 2025, could not be corroborated from any reachable source. The 2024
review's published outcome is that no team exceeded the cap. Do not publish the
2024 Aston Martin matter without an independent source.

Figures that also could not be substantiated and are therefore **not used**: a
£118.036m 2021 cap figure for Red Bull; "over 75,000 line items audited"; "13
items incorrectly excluded totalling £5.607m". The documented finding is that
Red Bull were in breach on **13 points of non-compliance**.

## 5. Aerodynamic Testing Restrictions — Article F4

### Six periods per year, of unequal length

Article F4.1.4: *"There will be 6 ATPs in any year."*

| ATP | Length | Boundary |
| ---: | ---: | --- |
| 1 | ~9 weeks | starts 1 January, finishes at the end of week 9 |
| 2 | 8 weeks | |
| 3 | 8 weeks | **championship position refreshes at the end of this period** |
| 4 | 10 weeks | includes the summer shutdown |
| 5 | 8 weeks | |
| 6 | remainder | ends 31 December |

> This is the figure most often reported wrongly. The ATR are **not** two
> half-year periods, and the allowance is **not** an annual one. There are six
> Aerodynamic Testing Periods, and the limits below apply **per ATP** — so the
> annual allowance is six times the C=100% figures, not one or two.

### Limits at C = 100%, per ATP

Article F4.6.1:

| Resource | Limit at C = 100% |
| --- | ---: |
| Restricted Wind Tunnel Testing (RWTT) runs | **320** |
| 3D new Restricted Aerodynamic Test Geometries (RATGs) | **2,000** |
| RWTT Wind On Time | **80 hours** |
| RWTT Occupancy | **400 hours** |
| CFD compute | **6 MAUh** |

The last three are routinely omitted from press summaries and are real
constraints — a team can exhaust occupancy hours without exhausting runs.

### The sliding scale

C = 100% is pegged to the **seventh-placed** constructor. The scale runs in 5%
steps, and **5% is worth 16 RWTT runs and 100 RATGs**.

| Championship position `P` | C |
| ---: | ---: |
| 1 | 70% |
| 2 | 75% |
| 3 | 80% |
| 4 | 85% |
| 5 | 90% |
| 6 | 95% |
| **7** | **100%** |
| 8 | 105% |
| 9 | 110% |
| 10 and below, and new entrants | 115% |

Article F4.6.1.a sets `P`: the **previous year's final** Constructors' position
for the first three ATPs, and the **current standing at the end of the last day
of the 3rd ATP** for the last three. The handicap therefore changes **once**
mid-season, not on calendar half-years.

### Carry-back for over-use

Article F4.6.9: a team that runs, say, **325** restricted wind tunnel runs
against a maximum of 320 in an ATP is permitted only **270** runs in the next
ATP — a penalty larger than the overrun.

### 2026 allocations, ATPs 1–3

Set by the final 2025 Constructors' standings.

| P | Team | C | RWTT runs | 3D new RATGs |
| ---: | --- | ---: | ---: | ---: |
| 1 | McLaren | 70% | 224 | 1,400 |
| 2 | Mercedes | 75% | 240 | 1,500 |
| 3 | Red Bull | 80% | 256 | 1,600 |
| 4 | Ferrari | 85% | 272 | 1,700 |
| 5 | Williams | 90% | 288 | 1,800 |
| 6 | Racing Bulls | 95% | 304 | 1,900 |
| 7 | Aston Martin | 100% | 320 | 2,000 |
| 8 | Haas | 105% | 336 | 2,100 |
| 9 | Audi | 110% | 352 | 2,200 |
| 10 | Alpine | 115% | 368 | 2,300 |
| — | **Cadillac** | 115% | 368 | 2,300 |

A new entrant receives the same allocation as the last-placed team. Note the
Audi row: the position is inherited from Sauber's 2025 finish, which is the
lineage rule from [Constructor lineage](team-lineage.md) showing up in the
regulations themselves.

The arithmetic is independently corroborated: Haas gaining 10% is reported as
"32 more windtunnel runs and 200 more CFD items", and a 5% loss as "16 fewer
windtunnel runs and 100 fewer CFD items" — both consistent with a 320 / 2,000
baseline.

### The 2026-car development gate

The FIA formalised a ban on any aerodynamic testing or CFD work on
2026-regulation cars before **1 January 2025**, with a further staged gate
around 1 July, specifically to prevent an early-mover advantage on the new
rules.

## 6. Where the two regimes meet

A 10% ATR reduction — Red Bull's 2023 penalty — is worth roughly **32 wind
tunnel runs and 200 RATGs per ATP**. Over six periods that is a substantial
development deficit, and it is a *sporting* penalty delivered through a
*financial* enforcement process.

For a development-trajectory chart, **ATR allocation is the best available proxy
for a team's permitted development bandwidth**, and it explains part of the
mid-season convergence pattern: the teams with the most bandwidth are, by
construction, the ones furthest behind.

The honest caveat on such a chart is that ATR is *permitted* bandwidth, not
*used* bandwidth. Actual usage is not published. The chart plots the constraint,
and the caption says so.

## 7. Caveats on these figures

- Every figure here is read from a **specific issue** of a document that is
  reissued several times per season. Re-verify against the live PDF before
  publication (see [The 2026 regulation reset](regulations-2026.md)).
- The ATR article numbers and structure are read from **Section F Issue 10**.
  The **percentage-to-team mapping** for 2026 is corroborated by two independent
  press sources rather than by a published FIA allocation table, and is
  consistent with the 2025 final standings.
- Currency conversions in D4.1.3 and E2.3.1 are **illustrative** figures printed
  in the regulations, not live exchange rates. Render them as published values
  with their date, never as a converted number.

## See also

- [Constructor lineage](team-lineage.md) — the 2026 grid and which teams these allocations belong to
- [The 2026 regulation reset](regulations-2026.md) — the six-section rulebook and the article map
- [Points systems](points-systems.md) — what a Constructors' points deduction acts on
- [Championship edge cases](championship-edge-cases.md) — sporting penalties and retroactive amendments
