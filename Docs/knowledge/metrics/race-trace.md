---
type: Metric
title: Race trace
description: Cumulative race time plotted as a delta against a constant reference pace, so that strategy, tyre state and caution periods become legible as shapes rather than as columns of lap times.
resource: /methods/race-trace/
tags: [visualisation, race-trace, cumulative-time, lap-chart, reference-pace, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: multiviewer_race_trace
    resource: https://multiviewer.app/docs/usage/race-trace
    title: MultiViewer — Gap to Leader, Delta to Average, Delta to Driver
  - id: sore_gapper
    resource: https://www.schoolofraceengineering.co.uk/blog/post/15991/build-your-own-race-strategy-gapper-tool/
    title: School of Race Engineering — building a race strategy gapper tool
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — LapTime, LapNumber, LapStartTime, Position, TrackStatus
  - id: tumftm_pars_silverstone_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Silverstone_2019.ini
    title: pars_Silverstone_2019.ini — caution lap-time multipliers
status: stable
---

# Race trace

The focal chart of a race page. Each driver is a line; the y-axis is cumulative
time relative to a reference; the x-axis is lap number. Strategy reads as
shape.

A race trace is the only chart on which a whole Grand Prix is visible at once
without being a table. Pit stops are vertical drops, overtakes are crossings,
safety cars compress the field toward the reference, and a tyre going off is a
line bending away. That is why the specification names it the one thing a race
page is *for*.

## Construction

Cumulative race time for driver `d` at lap `L`:

```
T_d(L) = Σ_{l = 1..L} t_d(l)
```

The trace plots

```
D_d(L) = T_d(L) − R(L)
```

for a reference `R(L)`. **The choice of `R` is the entire design decision** —
the same underlying data produces three quite different charts, each answering
a different question.

## The three reference constructions

| Name | `R(L)` | Reads as | Question it answers |
| --- | --- | --- | --- |
| **Delta to driver** | `T_ref(L)` for one chosen driver | Reference line flat at zero | "How did everyone do relative to the winner?" |
| **Gap to leader** | `min_d T_d(L)` | Reference switches whenever the lead changes | "What was the running order and how close was it?" |
| **Delta to average** | `L · t̄_ref` | A downward-sloping fan | "Where did the race time actually go?" |

`t̄_ref` is the reference driver's total race time divided by the number of
laps — a **constant** pace, which is what makes the third construction the
classic race trace.

These are the established names: MultiViewer implements exactly these three as
*Gap to Leader*, *Delta to Average* and *Delta to Driver*, and adopting its
vocabulary means a reader who knows one tool can read the other.

**Gap to leader gets its own page** — [Gap to leader](gap-to-leader.md) —
because its axis compression and lapped-car handling are substantial enough to
be a separate method.

### Why delta-to-average slopes downward

Because early laps are slower than the race average and late laps are faster.
The car is heavy at the start and light at the end: at Silverstone 2019 the
fuel term alone is 3.74 s on lap 1 and 0.07 s on lap 52. Plotted against a
constant average pace, every driver's line therefore descends across the race.
That characteristic fan is not a feature of the racing; it is fuel burn drawn
at scale.

Which leads to the version this site treats as the distinctive one.

## The fuel-corrected trace

Build the trace on [fuel-corrected](fuel-corrected-pace.md) lap times and the
fan flattens. What remains is strategy and tyre state — the two things the
chart exists to show.

```python
secs = laps["LapTime"].dt.total_seconds()
mass = m0 - b * (laps["LapNumber"] - 1)
corr = secs - mass * k                     # zero-fuel reference
T    = corr.groupby(laps["Driver"]).cumsum()
t_bar = T_ref.iloc[-1] / n_laps            # constant reference pace
D    = T - laps["LapNumber"] * t_bar
```

Two traces on the same page — raw and fuel-corrected, with a toggle — is the
editorially strong presentation, because the difference between them *is* the
fuel story and is worth seeing.

The chart must state which it is showing. A fuel-corrected trace with an
unlabelled axis in seconds is a chart of numbers that never existed.

## Reference selection, in practice

| Situation | Recommended reference |
| --- | --- |
| Standard race page | Winner, delta-to-average — the classic trace |
| Close title fight | Delta-to-driver against the championship rival |
| Heavily disrupted race (multiple SCs, red flag) | Gap-to-leader, because a constant average is meaningless when the field spent laps at 160% pace |
| Comparing a driver's two stints | Delta-to-driver against that driver's own pre-stop average |

One rule: **the reference is named on the chart**, always, in the axis label or
the caption. "Delta (s)" alone is not a labelled axis.

## Reading conventions

| Feature | Appearance | Approximate magnitude |
| --- | --- | --- |
| Pit stop | Vertical drop | The circuit's pit loss — 14.09 s (Spielberg) to 24.59 s (Singapore) |
| Overtake | Two lines crossing | — |
| Safety car | Whole field compresses toward the reference | SC laps run at ~160% of normal pace |
| Virtual safety car | Milder compression | ~140% |
| Tyre going off | Line bends progressively away | `k_1` per lap, typically 0.01–0.05 s/lap |
| Undercut | Attacker's line lifts relative to defender's across a 1–4 lap window | See [Undercut delta](undercut-delta.md) |

Caution laps are **shaded**, not left to be inferred from the compression, and
the shading comes from `TrackStatus`: `'4'` Safety Car, `'5'` Red Flag, `'6'`
VSC deployed, `'7'` VSC ending. Prefer `session.track_status` and
`session.race_control_messages` over `fastf1.api`, which is documented as
becoming private.

## Data mechanics

**Lap 1 is frequently missing.** Published lap-time sources often do not carry
it, and the standard reconstruction is

```
t_d(1) = (total race time for d) − Σ_{l = 2..N} t_d(l)
```

This is the mechanic that the School of Race Engineering's gapper-tool
walkthrough spells out for a spreadsheet build, and it is worth knowing because
a trace built without it starts every driver at the wrong offset and stays
wrong for the whole race.

**FastF1 fields.** `session.laps` carries `LapTime`, `LapNumber`,
`LapStartTime`, `Position` and `TrackStatus` — everything the construction
needs. `LapStartTime` is the field that lets a trace be drawn against session
clock rather than lap index, which matters for aligning a trace with radio or
race-control events.

**Source of truth for historical races.** The FIA's post-race *Race Lap
Analysis* and *Race History Chart* PDFs. Where this site's trace disagrees with
those documents, the documents win and the discrepancy is a bug.

**Retirements** end a line; they do not drop it to the bottom of the axis. A
retired driver's trace stops at their last completed lap, and the page says why
it stopped — see [Reliability and DNF rate](reliability-dnf.md).

## Coverage

The race trace requires lap-by-lap times, which begin in **1996** on this
site's tiering. It is a **Timing-tier and above** chart: 1996–2017 Timing,
2018–2022 Telemetry, 2023–2026 Modern. Archival-tier races (1950–1995) have no
trace, and their pages do not render an empty one.

## Design notes

Consistent with the site's restraint:

- Thin, constant-width strokes. No line weight encoding.
- Teammates separated by **solid vs dashed** (`stroke-dasharray: "6 3"` on the
  second car), never by a second hue. Twenty drivers do not get twenty colours.
- **Direct end-of-line labelling.** No colour-only legend.
- A zero rule, drawn at the same weight as the axis, not heavier.
- Selective emphasis as the primary reading mode: 2–4 drivers highlighted, the
  rest receded to a neutral. "All twenty at once" is the fallback view, not the
  default.
- Axis in seconds with `--f1-numeric: tabular-nums lining-nums` applied to
  every tick label.
- A real `<table>` fallback, per the site's accessibility commitment.

## Related

- [Gap to leader](gap-to-leader.md) — the reference-switching construction,
  with its own axis treatment.
- [Fuel-corrected pace](fuel-corrected-pace.md)
- [Pit loss time](pit-loss-time.md) — sets the expected size of a vertical drop.
- [Overtake detection](overtake-detection.md) — a line crossing is a candidate
  overtake, not a confirmed one.
- [Position at corner](position-at-corner.md) — the sub-lap resolution the race
  trace cannot reach.
