---
type: Policy
title: Editorial voice
description: Tense, person, number formatting, neutral incident description, the prohibited slop patterns, and the rules governing generated prose.
tags: [editorial, voice, copy, style, numbers, anti-patterns]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: impeccable_craft_floor
    resource: https://github.com/pbakaus/impeccable/blob/main/.claude/skills/impeccable/reference/craft-floor.md
    title: Impeccable craft-floor (Verify and Refuse lists)
  - id: impeccable_slop
    resource: https://impeccable.style/slop/
    title: Impeccable slop catalogue (67 patterns)
  - id: impeccable_distill
    resource: https://github.com/pbakaus/impeccable/blob/main/.claude/skills/impeccable/reference/distill.md
    title: Impeccable distill reference
  - id: butterick
    resource: https://practicaltypography.com/summary-of-key-rules.html
    title: Butterick, Summary of Key Rules
  - id: f1db_results_schema
    resource: https://raw.githubusercontent.com/f1db/f1db/main/README.md
    title: F1DB race-results schema (reasonRetired, gapLaps, timeMillis)
  - id: jolpica_diffs
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/ergast_differences.md
    title: jolpica-f1 documented differences from Ergast
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core object model (ClassifiedPosition, Status, IsAccurate)
status: stable
---

# Editorial voice

At the scale of ~2,400 pages, voice cannot be a matter of taste exercised per
page. It is a specification, and template copy is held to it as strictly as
hand-written prose. The site's value is being *right* about Formula 1 history
and *quiet* about it; both halves are editorial decisions.

## 1. Stance

| Dimension | Rule |
| --- | --- |
| Person | Third person. Never "we", never "our". The site does not refer to itself. |
| Address | Second person only inside interface copy that names an action ("Scrub to lap 34"). Never in prose. |
| Tense | Past for events. Present for enduring facts. Present perfect only for a record that still stands. |
| Mood | Declarative. No rhetorical questions, no exhortation, no imperative outside controls. |
| Register | Specific and unhurried. Assume the reader watched the race and wants to know why it went that way. |
| Hedging | Hedge only where the data hedges. "Probably" is a claim about uncertainty and needs a reason. |

**Tense, worked:**

- "Senna took pole by 1.427 s." — past; a completed event.
- "The circuit runs anticlockwise." — present; an enduring property.
- "The lap record has stood since 2004." — present perfect; still true.
- "Monza is the fastest circuit on the calendar." — present, but only if it is
  currently true; a superlative about a past season is past tense.

**Never** the historic present for drama ("Senna dives down the inside"). It is
the single most common tell of imitated sports writing, and it collides with
the site's permanence: a page written in the historic present reads as a live
report that has gone stale.

## 2. Numbers

Every figure on the site is a typographic object with a specified form. The
`--f1-numeric` utility — `font-variant-numeric: tabular-nums lining-nums` —
applies to every timing readout, table cell, axis label and telemetry value.
The reference stylesheet this project calibrates against contains no
`font-variant-numeric` anywhere; it does not need it, and we do. See
[design-tokens.md](../design/design-tokens.md).

| Quantity | Form | Example |
| --- | --- | --- |
| Lap or sector time | `M:SS.mmm`, always three decimals, trailing zeros kept | `1:12.909`, `1:30.100` |
| Time under one minute | `SS.mmm` | `28.400` |
| Gap to a car ahead | `+S.mmm` with an explicit sign | `+0.238` |
| Gap over a minute | `+M:SS.mmm` | `+1:04.500` |
| Laps down | `+1 lap`, `+2 laps` — lower case, never `+1L` in prose | `+2 laps` |
| Race duration | `H:MM:SS.mmm` | `1:26:04.001` |
| Speed | Integer km/h, unit stated once per table | `327 km/h` |
| Circuit length | Kilometres to three decimals | `3.337 km` |
| Race distance | Kilometres to three decimals | `260.286 km` |
| Delta in prose | Seconds to three decimals with the unit | `0.184 s` |
| Percentage | One decimal | `14.8%` |
| Fuel effect | Seconds per kilogram, three decimals | `0.031 s/kg` |
| Temperature | Integer °C, air and track labelled separately | `Air 24 °C, track 41 °C` |
| Date in prose | `12 September 2026` | |
| Date in data | ISO 8601 | `2026-09-12` |
| Session time | UTC with a visible label, plus local time where known | `13:00 UTC (15:00 local)` |
| Season | Four digits, never `'26` | `2026` |
| Ordinal position | Numeral plus suffix in prose, bare numeral in tables | `3rd`, `3` |

Rules that follow:

- **Three decimals or none.** Timing is published to the thousandth. Rounding a
  lap time to `1:12.9` implies a precision the sport does not use and the data
  does not have. Where a source supplies milliseconds (`timeMillis`,
  `gapMillis`, `intervalMillis` in F1DB), render all three digits, including
  trailing zeros — jolpica's `Time.time` always carries exactly three decimals
  with trailing zeros for the same reason.
- **Never mix precisions in one column.** A column of gaps is three decimals
  throughout or it is not a column.
- **A derived figure states its method or does not appear.** See
  [provenance-and-staleness.md](provenance-and-staleness.md) §5.
- **Uncertainty is shown, not implied.** A driver-vs-car decomposition ships
  with a visible interval and a named method, or it does not ship.
- **No single global figure for a circuit-specific quantity.** Pit-stop loss
  under safety car spans roughly 12–82% of green-flag loss depending on the
  venue; the site quotes the venue, never an average.
- **Timezones are always labelled.** A session time without a visible timezone
  is a defect, not a style preference.

## 3. Describing an incident neutrally

This is where a data site most easily acquires an opinion it cannot defend.

| Do | Do not |
| --- | --- |
| "Verstappen and Hamilton made contact at turn 1." | "Verstappen took Hamilton out." |
| "Leclerc retired on lap 32. F1DB records the cause as `Gearbox`." | "Leclerc's Ferrari let him down again." |
| "The stewards issued a five-second penalty for causing a collision." | "Leclerc was robbed by a harsh penalty." |
| "He rejoined 14th and finished 6th." | "He fought back heroically to 6th." |
| "The car stopped on the pit straight." | "The car expired." |
| "No cause is recorded." | "The car presumably broke." |

Working rules:

1. **Name the manoeuvre, not the blame.** "Made contact", "collided with",
   "ran wide", "locked up", "went off at turn 4". These describe what the
   telemetry and the footage agree on.
2. **Fault is attributed only to a published stewards' decision**, and then it
   is attributed *to the stewards* and cited by document. "The stewards found
   that car 16 was wholly at fault" is reportable. "Car 16 was at fault" is an
   editorial verdict and is not.
3. **Retirement causes are quoted from the field, with the field named.** The
   site reports what the source says, not what the cause was. F1DB's
   `reasonRetired` is the source of record; where it is empty, the page says
   "no cause recorded" rather than inferring one.
4. **The passive voice is permitted where the agent is genuinely
   undetermined.** "The suspension failed" is honest. Reaching for the passive
   to soften an attributed finding is not.
5. **No counterfactuals as fact.** "Would have finished second" is a
   simulation result and appears only with its method and its assumptions
   stated, or not at all.
6. **Injuries and fatalities are reported plainly and once.** Date, session,
   circuit, outcome. No dramatisation, no lingering, no adjectives. The
   archival tier covers eras in which drivers died; the page states what
   happened and moves on.
7. **A classification is what the classification says.** `ClassifiedPosition`
   carries `R` (retired), `D` (disqualified), `E` (excluded), `W` (withdrawn),
   `F` (failed to qualify) and `N` (not classified). These are distinct states
   with distinct copy; collapsing them all to "DNF" is wrong.

## 4. Structural copy

Hand-written prose is scoped to a finite set: the 8–12 hero circuits, the major
constructors, and a curated set of landmark races. Everything else is
data-driven and templated, and **template copy is written to be structural, not
pseudo-narrative.**

| Permitted in template copy | Forbidden in template copy |
| --- | --- |
| A caption naming what a chart shows and over what range | A sentence that imitates a human essay |
| A definition of a term, linked to its method page | An adjective about how exciting the race was |
| A statement of fact with its source | A transition sentence between sections |
| A stated absence ("No lap data exists for this race.") | Filler that exists to make the page feel written |
| A comparison the data supports ("Third of 78 circuits by length.") | A comparison the data does not support |

Template copy that imitates a human essay is exactly the flat, interchangeable
output the slop catalogue exists to detect. A page with nothing to say says
less, rather than saying it at greater length.

**Honest absence has designed copy, not an empty chart.** An archival-tier race
page does not render an axis with no series on it. It says what is missing and
why, once, in the place the chart would have been:

> Lap-by-lap timing begins in 1996. For this race the site has the
> classification, the grid, championship points and recorded retirement causes.

That sentence is a template with two variables. It is not apologetic, it does
not promise a future feature, and it does not appear more than once per page.

## 5. Prohibited patterns

### 5.1 Hard bans

These ship in no circumstance. The first eight are the ones named in the
project specification; the remainder are the copy-side patterns from the same
catalogue.

| Pattern | Why |
| --- | --- |
| Kicker or eyebrow above a heading | The one item the source catalogue calls an outright ban rather than a default. The heading carries its own weight |
| Italic serif pull-quotes | A familiar shortcut to an "editorial" look; it is the look, not the editing |
| Gradient text | Emphasis comes from weight or size |
| Emoji or Unicode glyphs as iconography | Icons are drawn, in one consistent stroke and weight |
| Status chips as a default decoration | A chip is a state, not an ornament |
| Centred body copy | Flush left, ragged right, everywhere |
| Purple-to-blue gradients; near-black with a neon accent | Named AI-default aesthetics, and the second is exactly the motorsport category default |
| "Powered by" | The colophon names what is used, in prose, once |
| Card grids as the default page layout | "Cards are the lazy container; nested cards are always wrong" |
| Unearned glassmorphism | Blur is a specific effect, not decoration |
| Justified body text | Rivers and hyphenation problems, for no gain |
| Em-dash in every other sentence | A recognisable machine-writing habit. Use it where the syntax needs it and count them |
| Marketing superlatives — "supercharge", "world-class", "enterprise-grade", "seamless", "game-changing" | Say the specific thing instead |
| Calling anything "theatre" | A machine-writing tell |
| Forced contrast — "Not a dashboard. A reference." | Rhetorical shape standing in for a claim |
| Aphoristic cadence — three short sentences in a row for rhythm | Same |
| Section numbers (01 / 02 / 03) in page chrome | Only where the sequence itself carries information |

### 5.2 Defaults to refuse unless argued in writing

Permitted only with a written reason in the commit, because each is a category
default rather than a mistake:

- **The hero-metric template** — a huge number, a small label, supporting
  stats, an accent. This is the single most tempting pattern for an F1 site and
  it must be earned, not assumed.
- **Sparklines.** Refused when standing in for content; sanctioned when
  carrying real per-lap data. The distinction is whether erasing the series
  would change what the reader learns.
- **Monospace.** Refused as a costume for "technical"; sanctioned for code,
  data and measurement — which is to say lap times, sector deltas and gaps, and
  nothing else.
- **Decorative grid-line backgrounds.** Refused as texture; sanctioned for
  canvases, maps and anything the reader measures against, which covers the
  track map and the telemetry plots.

### 5.3 Typographic floor

| Property | Value |
| --- | --- |
| Prose measure | 65–75 ch |
| Data tables | may run to 120 ch and beyond |
| Body size | from 16 px / 1 rem |
| Body line height | ~1.5 at 16 px, tuned inversely with measure |
| Alignment | flush left, ragged right |
| Paragraph rhythm | paragraph spacing **or** first-line indent, never both |
| All-caps and small-caps | 5–12% extra letterspacing |
| Tracking floor | −0.04 em |
| Display size ceiling | 6 rem |
| Quotation marks | curly, always |
| Sentence spacing | single |

## 6. Terminology

| Use | Not |
| --- | --- |
| Grand Prix (capitalised, as part of the event name) | grand prix |
| constructor (in a championship context) | team, when points are meant |
| team (in a sporting/operational context) | constructor, when people are meant |
| tyre | tire |
| pit lane (two words); pit stop (two words); pitwall (one) | pitlane in prose |
| safety car; virtual safety car; abbreviate to SC / VSC only after first use | full caps on first mention |
| qualifying; Q1, Q2, Q3 | quali |
| sprint qualifying (2024 onward); sprint shootout (2023 only) | using one name across both eras |
| retired | DNF, in prose |
| classified / not classified | "officially finished" |
| lap record — state whether race or all-time, and the layout it was set on | bare "lap record" |

Two era-sensitive cases that template copy gets wrong by default:

- **Points systems changed.** 1950–59 awarded 8-6-4-3-2 for the top five plus a
  point for fastest lap; 1961–90 awarded 9-6-4-3-2-1. The fastest-lap point
  returned in 2019 and was abolished again from 2025. Copy that says "points
  finish" without qualification is wrong for most of the sport's history; a
  template that compares raw point totals across eras is wrong always.
- **Messy history is described, not smoothed.** Shared drives before 1958, half
  points, the Indianapolis 500 as a championship round from 1950 to 1960,
  drivers scoring for two constructors in one season, ties broken on countback,
  and retroactively amended classifications all exist and are modelled in the
  schema. Copy names them where they apply ("points shared between two drivers
  for a shared drive") rather than presenting a tidy number.

## 7. Generated prose

The research that produced this knowledge base was adversarially fact-checked
and 83 of roughly 252 claims required correction. That is the empirical base
rate this policy is calibrated against.

1. **LLM-drafted prose is a first draft.** It is never published without a
   human fact-check against the source of record.
2. **Pages containing it are marked in the source.** The page's frontmatter
   carries `prose: generated | reviewed | authored` and a `reviewedBy` /
   `reviewedAt` pair. `generated` never reaches a build. CI fails a page whose
   `prose` field is `generated`.
3. **Generated prose may not introduce a fact.** It may restate a figure that
   already exists in the emitted data, with a link to that figure's method. A
   sentence containing a number that does not appear in the page's data payload
   is a defect.
4. **No generated prose in the archival tier's factual claims.** Pre-1996 pages
   have the thinnest data and the highest risk of confident invention; their
   prose is authored or it is absent.
5. **The slop detectors run in CI.** A source scan and a rendered-page scan run
   against the built site, and a rule hit is a build failure, not a warning.

The underlying position: on a site whose entire value is being right about
Formula 1 history, unreviewed generated prose is an unacceptable risk, and the
scale argument ("1,500 pages need words") is the reason the templated pages get
*structural* copy rather than the reason they get generated essays.

## 8. Review checklist

Run against a built page, not a draft.

- [ ] No first person, no second person outside controls.
- [ ] Tense correct per §1; no historic present.
- [ ] Every figure matches a row in §2, including trailing zeros.
- [ ] Every derived figure links to its method page.
- [ ] Every incident description survives §3 — no blame not attributed to a
      published decision.
- [ ] Missing data has designed copy, once, in the right place.
- [ ] No pattern from §5.1 present anywhere on the page.
- [ ] Any §5.2 default has a written justification in the commit.
- [ ] Measure within 65–75 ch at every breakpoint with real copy.
- [ ] `--f1-numeric` applied to every numeric cell, axis tick and readout.
- [ ] Em-dash count per 1,000 words is defensible.
- [ ] `prose` frontmatter is `reviewed` or `authored`.
