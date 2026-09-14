---
type: Reference
title: The 2026 Regulation Reset
description: The six-section 2026 FIA rulebook with exact issue numbers and dates, the article map that replaces every legacy citation, and the power unit, aerodynamic, mass and tyre figures that changed.
resource: https://www.fia.com/regulation/category/110
tags:
  - 2026-regulations
  - power-unit
  - active-aero
  - overtake
  - regulations
  - article-map
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fia_reg_index
    resource: https://www.fia.com/regulation/category/110
    title: FIA regulation index — Formula 1
  - id: fia_2026_section_a
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_a_general_provisions_-_iss_03_-_2026-06-25.pdf
    title: FIA 2026 F1 Regulations — Section A (General Regulatory Provisions), Issue 03, 25 June 2026
  - id: fia_2026_section_b
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_b_sporting_-_iss_08_-_2026-08-05_7.pdf
    title: FIA 2026 F1 Regulations — Section B (Sporting), Issue 08, 5 August 2026
  - id: fia_2026_section_c
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_c_technical_-_iss_20_-_2026-08-05.pdf
    title: FIA 2026 F1 Regulations — Section C (Technical), Issue 20, 5 August 2026
  - id: fia_2026_section_d
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_d_financial_-_f1_teams_-_iss_07_-_2026-06-25.pdf
    title: FIA 2026 F1 Regulations — Section D (Financial, F1 Teams), Issue 07, 25 June 2026
  - id: fia_2026_section_f
    resource: https://www.fia.com/system/files/documents/fia_2026_f1_regulations_-_section_f_operational_-_iss_10_-_2026-08-05.pdf
    title: FIA 2026 F1 Regulations — Section F (Operational), Issue 10, 5 August 2026
status: stable
---

# The 2026 Regulation Reset

The 2026 rulebook was restructured into lettered sections with entirely new
article numbering. **Every pre-2026 article citation is dead.** "Article 6.5
points" and "Article 39 tyres" now point at nothing. This document is the map.

## 1. Six sections, not three

| Section | Title | Issue | Dated | WMSC |
| --- | --- | ---: | --- | --- |
| **A** | General Regulatory Provisions | **03** | 2026-06-25 | 2026-06-23 |
| **B** | Sporting Regulations | **08** | 2026-08-05 | 2026-08-03 |
| **C** | Technical Regulations | **20** | 2026-08-05 | — |
| **D** | Financial Regulations — F1 Teams | **07** | 2026-06-25 | 2026-06-23 |
| **E** | Financial Regulations — PU Manufacturers | **06** | 2026-06-25 | — |
| **F** | Operational Regulations | **10** | 2026-08-05 | — |

A model of the 2026 rulebook built from Sections A, B and C alone is missing
half of it — the cost cap (D), the PU manufacturers' cap (E) and the whole of
the aerodynamic testing restriction regime (F). Those are covered in
[Cost cap and ATR](cost-cap-and-atr.md).

**Sections are reissued several times per season**, with changes marked in pink
text. Issue numbers in this document are current as of 2026-09-14 and every
figure should be re-checked against the live PDF before it is published on a
page. Reading a **redline** PDF with `pdftotext` is specifically dangerous:
strikethrough is flattened, so deleted text and replacement text appear as one
run. That is the origin of the widely-repeated wrong 2026 Q3 timing (see
[Session formats](session-formats.md)).

**Ingest warning:** a 2027 Section C Technical is already published (Issue 01 of
25 June 2026 and Issue 02 of 5 August 2026). Any pipeline that globs the FIA
document directory for `section_c_technical` will pick up 2027 files alongside
2026 ones.

## 2. Article map

The citations the site actually needs, and where they now live.

| Topic | 2026 article |
| --- | --- |
| Championship points, partial points, dead heats | **A2.2** |
| Entries, titles, competition count, countback | **A2.1** |
| Super Licence penalty points | **A3.3.1b** |
| Penalties and incidents | **B1.9** |
| Pit lane, pit entry/exit, speed limit | **B1.6** |
| Driving standards and flag obligations | **B1.8** |
| Weekend formats, qualifying, sprint, race | **B2** |
| Scrutineering, weighing, parc fermé | **B3** (B3.5 pre-, B3.6 post-) |
| Lap Time Classified Sessions (LTCS) | **B4** |
| Total Time Classified Sessions (TTCS) | **B5** |
| VSC, Safety Car, suspension, resumption, finish | **B5.12 – B5.16** |
| Tyres | **B6** |
| Driver Adjustable Bodywork and Overtake | **B7** |
| Car and Power Unit component limits | **B8** (B8.2 = PU) |
| Definitions | **Appendix B1** |
| Parc fermé permitted works | **Appendix B2** |
| Wheelbase | **C2.3.3** |
| Front wing / rear wing adjustability | **C3.10.10 / C3.11.6** |
| Minimum mass, Heat Hazard mass | **C4.1 / C4.6 / C4.7** |
| ERS power, energy flow, recharge | **C5.2** |
| Tyre and rim dimensions | **C10.7.2** |
| Fuel | **C16** |
| Team cost cap and breach taxonomy | **D4 / D10 / D12** |
| PU manufacturer cost cap | **E2.3.1** |
| Aerodynamic Testing Restrictions | **F4** |

Note the relocation in the last row: the ATR were **Appendix 7 of the Sporting
Regulations** before 2026. A grep of Section B for "aerodynamic testing" now
returns nothing.

## 3. The power unit

### Headline split

The 2026 power unit produces **roughly 750 kW in total** — approximately
**400 kW from the internal combustion engine** (down from ~630 kW) and
**350 kW electrical** (up from 120 kW). Total output is therefore broadly
unchanged from the 2014–2025 era; what changed is the ratio, to roughly
**47% electrical**.

> **The most common error about 2026 is that the cars make 400 kW in total.**
> 400 kW is the ICE figure alone. Related derived errors follow: the MGU-K
> increase from 120 kW to 350 kW is **2.92×**, i.e. about **192% more**, not
> "292% more".

The **MGU-H is deleted** entirely from the component list.

### Exact limits, Section C Article C5.2

| Article | Limit |
| --- | --- |
| C5.2.3 | Fuel energy flow must not exceed **3000 MJ/h** |
| C5.2.4 | Below 10,500 rpm: `EF(MJ/h) = 0.27 × N(rpm) + 165` |
| C5.2.7 | *"The absolute electrical DC power of the ERS-K may not exceed 350kW."* |
| C5.2.9 | ES state-of-charge swing **≤ 4 MJ** at any time the car is on track |
| C5.2.10 | Recharge **≤ 8.5 MJ per lap**, reducible to 7 MJ at some events and to no less than 4 MJ for SQ/Q; **+0.5 MJ** additional harvest per lap when Overtake is enabled and activated at the Line |
| C5.2.11 | MGU-K mechanical torque **≤ 500 Nm** |
| C5.2.12 | *"During a standing start from the grid the MGU-K may only be used once the car has reached 50 km/h."* |
| B7.2.1c | The extra-harvest provision is capped at a **maximum of 8 Competitions** per Championship |

The qualifying harvest limit was in fact cut from 8 MJ to 7 MJ during the 2026
season — an in-season change, and a good example of why issue numbers matter.

### The deployment curve is piecewise and has four branches

Article C5.2.8. This is the formula behind the best editorial graphic of the
2026 rules: a speed-versus-available-power chart.

```
(i)  Overtake NOT active
     P(kW) = 1800 −  5 × v(kph)      for v < 340
     P(kW) = 6900 − 20 × v(kph)      for 340 ≤ v < 345
     P     = 0                       for v ≥ 345

(ii) Overtake ACTIVE
     P(kW) = 7100 − 20 × v(kph)      for v < 355
     P     = 0                       for v ≥ 355

(iii) Race or Sprint, on specified circuit sectors, during a power-limited period
     P     = 250                     for v < 310
     P(kW) = 1800 −  5 × v(kph)      for 310 ≤ v < 340
     P(kW) = 6900 − 20 × v(kph)      for 340 ≤ v < 345
     P     = 0                       for v ≥ 345

(iv) Low Grip — separate curves, published in FIA-F1-DOC-111
```

Read off the curves, with the 350 kW cap from C5.2.7 applied:

| Speed | Overtake inactive | Overtake active |
| ---: | ---: | ---: |
| ≤ 290 kph | 350 kW (capped) | 350 kW (capped) |
| 300 kph | 300 kW | 350 kW (capped) |
| 337.5 kph | ~112 kW | 350 kW (capped) |
| 340 kph | 100 kW | 300 kW |
| 345 kph | **0** | 200 kW |
| 355 kph | 0 | **0** |

So full electrical power holds to 290 kph without Overtake and to 337.5 kph with
it. **Four curves, not two** — branch (iv) is published in a separate FIA
document that is not public, so a chart drawn from (i)–(iii) alone must say so.

Which circuit sectors carry the (iii) restriction, and at which events, is
**not public** — see Open questions below.

## 4. Aerodynamics: DRS is gone, and two systems replace it

DRS does not exist in 2026. Two **orthogonal** systems take its place, and
conflating them is the fastest way to get a circuit page wrong.

### (a) Driver Adjustable Bodywork — Article B7.1

Both the front wing profiles (C3.10.10) and the rear wing flap (C3.11.6) move
between two fixed positions.

| Regulatory term | Meaning |
| --- | --- |
| **Corner Mode** | high downforce |
| **Straight Mode** | low drag |

| State | Front wing | Rear flap |
| --- | --- | --- |
| Deactivated | Corner Mode | Corner Mode |
| **Partially** activated | Straight Mode | Corner Mode |
| **Fully** activated | Straight Mode | Straight Mode |

Critically: **Driver Adjustable Bodywork is not gap-gated.** Every driver may
use it inside an Activation Zone. The Race Director may downgrade full to
partial activation in low grip, using published **Low Grip Activation Zones**;
if it is disabled during an SQ or Q segment it stays disabled for that segment
and is re-enabled only with more than five minutes remaining.

The FIA provides the Activation Zones and Low Grip Activation Zones for a
circuit *"no less than four (4) weeks prior"*, and *"the start of each defined
Activation Zone shall be marked by signage on at least one (1) side of the
circuit."*

Rear flap mechanics, C3.11.6: maximum transition time **400 ms** between the two
fixed positions; **single actuator**; position sensor connected to the FIA
Standard ECU; *"failure of the system will result in RW Flap returning to its
Corner Mode position"*; deployable only when the car is stationary or fully
inside an Activation Zone.

> **Naming.** The regulations use **"Straight Mode"**, not "Straight-Line Mode",
> and **"Corner Mode"**. The "X-mode / Z-mode" terminology from the 2024 draft
> coverage is superseded. A schema keyed on either will not match FIA text.

### (b) Overtake — Article B7.2

The gap-gated aid, delivered as **extra ERS-K power**, not as aero.

> **Naming.** The regulation term is the bare word **"Overtake"** (B7.2;
> C5.2.8 reads *"When Overtake is active"* / *"not active"*). **"Overtake
> Override Mode" appears nowhere in Section B Issue 08 or Section C Issue 20** —
> zero occurrences of "Override" in either document. It was a 2024-era working
> name and is not a regulatory identifier.

Per-circuit parameters, published at least four weeks before an event
(B7.2.1b vii–ix):

| Parameter | Type |
| --- | --- |
| **Detection Gap** | a time value |
| **Detection Line** | a lap distance |
| **Activation Line** | a lap distance |

*"The location of the Detection Line and Activation Line shall be marked by a
solid yellow line crossing the circuit and by signage on at least one (1) side
of the circuit."* (B7.2.1f)

| Context | Behaviour |
| --- | --- |
| Any LTCS (practice, qualifying) | B7.2.3b(i) — active at all times when enabled |
| A TTCS (sprint, race) | B7.2.3c(i) — activates at the Activation Line if the car was **less than the Detection Gap** behind another car at the Detection Line |
| Before a start or resumption | B7.2.2b — disabled, then enabled once the leader crosses the Detection Line |
| Safety Car deployed | B7.2.2c — disabled; re-enabled **per car** after the SC returns to the pit lane |

### Schema consequence

A circuit record needs **both** geometries, because the site renders 2011–2025
pages and 2026 pages from the same entity:

```jsonc
{
  // 2011–2025
  "drs_zones": [ { "index": 1, "detection_point_m": 0, "zone_start_m": 0, "zone_end_m": 0 } ],

  // 2026+
  "activation_zones":          [ { "start_m": 0, "end_m": 0 } ],
  "low_grip_activation_zones": [ { "start_m": 0, "end_m": 0 } ],
  "detection_line_m":  null,
  "activation_line_m": null,
  "detection_gap_s":   null
}
```

The three 2026 scalars are currently **null for every circuit** — see Open
questions. Circuit pages for 2026 therefore describe the system in prose and do
not draw the geometry, rather than drawing a guess.

## 5. Chassis, mass and fuel

| Item | Article | 2026 value |
| --- | --- | --- |
| Minimum Mass, most sessions | C4.1 | **724 kg** + Nominal Tyre Mass |
| Minimum Mass, SQ and Q | C4.1 | **726 kg** + Nominal Tyre Mass |
| Nominal Tyre Mass | C4.7 | derived from new production dry-weather tyres; re-derived if the specification changes mid-championship |
| Heat Hazard Mass Increase, declared | C4.6(a)/(b) | **+5 kg** for a TTCS with a declared Heat Hazard, and a 5 kg minimum for driver equipment + cooling system |
| Heat Hazard Mass Increase, undeclared | C4.6(c)/(d) | **+2 kg** for any LTCS or TTCS *without* a declaration at a Competition where a Heat Hazard was declared for **any** session, cooling system no less than 2 kg |
| Wheelbase | C2.3.3 | **≤ 3400 mm** (down from 3600 mm) |
| Overall width | widely reported | 1900 mm (down from 2000 mm) |
| Fuel | C16.3 | **100% Advanced Sustainable**, certified AS components only, with a limited non-sustainable additive/denaturant package |

"Car Mass" is defined as *"the mass of the car, including tyres, plus Mass of
the Driver and Driver Ballast"*.

**768 kg is not a 2026 figure.** It was the 2024 launch-announcement number and
appears nowhere in the current regulations.

**Downforce reduction is approximately 15%**, not 30%. The ~30% figure was the
original draft target; the FIA revised it in October 2024 from a draft that had
exceeded 40%, on the basis that the cars would be roughly two seconds a lap
slower rather than four. Drag reduction targets around 55% are widely reported
and are secondary-source figures.

## 6. Sporting changes worth carrying

| Change | Detail |
| --- | --- |
| Entry | 11 teams, 22 cars → **six eliminated** per qualifying segment, computed as `(n − 10) / 2` (B2.2.3) |
| Qualifying | Q1 18 min / 7 min / Q2 15 min / 7 min / **Q3 13 min** |
| Tyres | up to **two** mandatory Race specifications; a mandatory **Q3** specification, always the softest |
| Monaco | the two-stop requirement is replaced by a **three sets of any specification** rule |
| Parc fermé | B3.5.5 — **six** times per Championship a team may request approval for replacement parts of *different design* (front wing, rear wing, rear bodywork or floor bodywork) on a demonstrated parts shortage, provided the specification was previously run |
| Parc fermé windows | B3.5.1 — two separate windows: SQ→Sprint, and Q→Race. Teams may re-set up the car between the Sprint and Qualifying |
| Pit lane | B1.6 — **80 km/h** throughout the whole Competition |
| PU allocation | B8.2.2 — per driver: 3 ICE, 3 turbochargers, 3 exhaust sets, 2 energy stores, 2 control electronics, 2 MGU-K, 5 PU ancillaries; **B8.2.3 grants one extra of each** in 2026, and again to any PU Manufacturer in its first year of supply |
| Gearbox | Section B Article B8 contains only B8.1 and B8.2 — **no gearbox article**, so gearbox grid penalties appear to have been dropped. A stale cross-reference to "B8.3" survives at B1.7, which suggests deletion rather than relocation. **Unconfirmed** — no FIA statement located. |

## 7. Open questions

Recorded rather than papered over, because each one blocks a specific page
feature.

- **Per-circuit Overtake geometry.** B7.2.1b says the FIA publishes the
  Detection Gap, Detection Line and Activation Line to Competitors at least four
  weeks before each event, and in a championship-wide document by 30 June of the
  preceding year. No public machine-readable source was found. Without it, 2026
  circuit pages cannot draw the Overtake geometry the way DRS zones were drawn.
- **The telemetry `DRS` channel in 2026.** FastF1's enum (0/1 off, 8 eligible,
  10/12/14 on) is flagged as uncertain by its own authors, and its 2026 meaning
  — Driver Adjustable Bodywork position, Overtake availability, or both — is
  **unverified against 2026 car data**.
- **C5.2.8(iii) sector assignments.** Which circuits and which sectors carry the
  250 kW restriction, and how many of the 8 permitted Competitions have used it,
  are not public.
- **Gearbox limits.** Whether gearbox component limits were genuinely abolished
  for 2026, per §6 above.

## See also

- [Session formats](session-formats.md) — the 2026 qualifying and sprint timings in full
- [Points systems](points-systems.md) — Article A2.2
- [Tyre compounds](tyre-compounds.md) — Article B6 in full
- [Track status and flags](track-status-and-flags.md) — how the Overtake state appears in the message stream
- [Cost cap and ATR](cost-cap-and-atr.md) — Sections D, E and F
- [Constructor lineage](team-lineage.md) — the 2026 grid and its five PU suppliers
