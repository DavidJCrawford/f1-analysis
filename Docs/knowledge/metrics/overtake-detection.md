---
type: Metric
title: Overtake detection
description: Counting on-track overtakes using the published de Groote (2021) definition rather than a naive diff of the position column, with lapping and unlapping identified as the largest source of false positives.
resource: /methods/overtake-detection/
tags: [overtaking, position, definition, false-positives, lapping, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: degroote_2021
    resource: https://doi.org/10.3233/JSA-200466
    title: de Groote, Overtaking in Formula 1 during the Pirelli era — a driver-level analysis, Journal of Sports Analytics
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — Position, PitInTime, PitOutTime, TrackStatus
  - id: openf1_overtakes
    resource: https://api.openf1.org/v1/overtakes
    title: OpenF1 /v1/overtakes endpoint
  - id: pitwall
    resource: https://arxiv.org/abs/2607.06495
    title: Pitwall — logistic pass model over 131,000 adjacent-car battles
  - id: tumftm_pars_suzuka_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Suzuka_2019.ini
    title: pars_Suzuka_2019.ini — t_gap_overtake and t_gap_overtake_vel
status: stable
---

# Overtake detection

Counting overtakes is deceptively hard. A position column changes for many
reasons, most of which are not overtakes, and a naive `diff()` over it produces
a number that is wrong by a large and *systematically biased* margin — biased
upward, and biased most at exactly the races people most want counted.

This site uses a published definition and states it.

## The definition

From de Groote (2021), *Overtaking in Formula 1 during the Pirelli era: A
driver-level analysis*, **Journal of Sports Analytics**,
[doi:10.3233/JSA-200466](https://doi.org/10.3233/JSA-200466), an overtaking
manoeuvre is one that

> takes place during complete flying laps (so not on the opening lap) and is
> then maintained all the way to the lap's finish line. Position changes due to
> major mechanical problems or lapping/unlapping are not counted.

Four exclusions are carried by that sentence:

1. **Not the opening lap.** Lap 1 is a start, not a race.
2. **Must be maintained to the finish line.** A pass made and lost within the
   same lap does not count.
3. **Not major mechanical problems.** A car slowing with a failure is not being
   overtaken in any meaningful sense.
4. **Not lapping or unlapping.** This is the one everyone forgets, and it is
   the largest single source of false positives.

Secondary accounts of the Clip The Apex *Formula One Overtaking Database* —
the human-curated dataset de Groote's work draws on — give the exclusions as
first-lap overtaking, overtaking backmarkers, and position changes resulting
from pit stops.

Two cautions about provenance. A frequently repeated fifth criterion — "a
position change caused by a driver yielding the place without a fight" — could
**not be substantiated** in any published statement of the definition, and this
site does not implement or cite it. And the Clip The Apex database's own URL
(`cliptheapex.com/overtaking/`) now returns **HTTP 404**; it is cited here as
the origin of the convention, not as a live source.

## Why lapping is the dominant false positive

Consider a leader closing on a car two seconds a lap slower. When the leader
passes, the backmarker's `Position` value increases by one and the leader's is
unchanged — or, depending on how the timing feed resolves the lap, both values
shift. A `diff()` over positions records an event. But nothing was raced for:
the two cars are not on the same lap and are not competing for the same place.

The magnitude of the problem scales with field spread. At a race with a wide
pace range, the leaders lap the tail several times each, and a naive counter
can inflate the total by tens of events. Those are precisely the processional
races where "how many overtakes were there?" is being asked most pointedly, so
the error lands where it does most damage.

## Implementation recipe

A correct implementation needs **four** tests, not one. Detect candidate swaps,
then reject.

### Step 1 — candidate detection

```python
# Position per driver per lap, from session.laps
pos = laps.pivot(index="LapNumber", columns="Driver", values="Position")

# For each adjacent pair on lap L-1, a candidate is an order flip on lap L
for L in range(2, n_laps + 1):
    for (a, b) in adjacent_pairs(pos.loc[L - 1]):
        if pos.loc[L, a] > pos.loc[L, b] and pos.loc[L - 1, a] < pos.loc[L - 1, b]:
            candidates.append((L, a, b))
```

Adjacency on the previous lap, not any pair: a two-position swing in one lap is
two events or a retirement, and should be decomposed rather than counted once.

### Step 2 — reject on lap number

`L == 1` → reject. Lap 1 position changes belong to
[the start analysis](#the-start-is-a-separate-metric), not here.

### Step 3 — reject on pit involvement

Two tests, because one is not enough.

```python
# (a) direct pit-lap test
if not_null(laps[a, L-1].PitInTime) or not_null(laps[a, L].PitOutTime): reject
if not_null(laps[b, L-1].PitInTime) or not_null(laps[b, L].PitOutTime): reject

# (b) pit-cycle window test
if any_stop(a, L-W .. L+W) or any_stop(b, L-W .. L+W): reject   # W ≈ 3
```

Test (b) is the one usually missing. A pit-lap-only rule does **not** catch a
swap that resolves over a multi-lap cycle: if A stops on lap `L` and B on lap
`L+3`, the order flips on a lap where neither driver has a `PitInTime` or
`PitOutTime`. The window `W` is a declared parameter of the analysis. This is
the mechanism of [Undercut delta](undercut-delta.md), and it is a strategic
gain, not an on-track pass.

### Step 4 — reject on lapped status

```python
if laps_completed(a, L) != laps_completed(b, L): reject
```

Compare completed lap count, or equivalently cumulative race time against the
leader's. The two drivers must be on the same lap for the swap to be a contest
for the same position. This is the test whose absence causes the bias described
above.

### Step 5 — reject on track status and on retirement

```python
ts = laps[a, L].TrackStatus
if any(c in ts for c in "4567"): reject      # SC, red, VSC deployed, VSC ending
if retired_this_lap(a) or retired_this_lap(b): reject
if mechanical_slowdown(a, L) or mechanical_slowdown(b, L): reject
```

Overtaking is prohibited under safety car, VSC and red flag, so any swap on
those laps is an artefact of the timing feed or of a car stopping. Track-status
codes: `'1'` clear, `'2'` yellow, `'4'` Safety Car, `'5'` Red Flag, `'6'` VSC
deployed, `'7'` VSC ending. Use `session.track_status` and
`session.race_control_messages` in preference to `fastf1.api`, which is
documented as becoming private.

`mechanical_slowdown` is the hardest test to automate. A workable proxy: the
overtaken driver's lap time on lap `L` exceeds their own trailing-5-lap median
by more than a stated threshold, *and* they retire or lose further places over
the following laps. Whatever proxy is used, it is declared with its threshold —
it is not a consensus rule.

## The site's position on reconciliation

An automatic detector will disagree with a human-curated count. It will
disagree on judgement calls — a pass completed off-track and handed back, a
position conceded under team orders, a pass into a pit entry.

**The site publishes its own automatic count with the rules stated, and does
not claim to reproduce any curated database.** Every overtake figure links
here, and the page names the parameters in force: the pit-cycle window `W`, the
mechanical-slowdown threshold, and the inclusion or exclusion of sprint
sessions.

Where OpenF1's `/v1/overtakes` endpoint is available (2023+), it is used as a
**cross-check only** — its fields are `meeting_key`, `session_key`,
`overtaking_driver_number`, `overtaken_driver_number`, `date`, `position`, and
its own definition is not published in a form this site can cite. A divergence
between the two counts is reported as a divergence, not resolved silently.

## The start is a separate metric

Lap-1 position changes are excluded from the overtake count and reported
separately as **positions gained on the opening lap**. They have their own
model and their own published constants:

| Parameter | Meaning | Range (2019 calibration) |
| --- | --- | --- |
| `t_loss_firstlap` | Standing-start penalty on lap 1 | 1.378 s (Suzuka) to 5.919 s (Hockenheim) |
| `t_loss_pergridpos` | Handicap per grid position on lap 1 | 0.113 s/pos (Monza) to 0.178 (Monte Carlo) |
| `t_startperf` | Per-driver start performance, `{mean, sigma}` | e.g. Hamilton {−0.052, 0.098}; Sainz {−0.097, 0.126}; Räikkönen {+0.088, 0.245}; unknown {0.0, 0.146} |

A negative mean is a gain. These are directly publishable as a "race start
performance" panel, and they explain most of what a lap-1 position change
actually measures.

## How hard is a pass, anyway — context for the count

An overtake count without circuit context is close to meaningless: Monaco and
Monza are not the same event. The per-circuit pace advantage required to
complete a pass, `t_gap_overtake`, spans

**1.26 s (Suzuka)** → Silverstone 1.35 → Sakhir 1.38 → Shanghai 1.50 →
Hockenheim 1.56 → Baku 1.62 → Le Castellet 1.635 → Monza 1.755 → Spa 1.83 →
Austin 1.83 → Spielberg 2.01 → São Paulo 2.025 → Mexico City 2.055 → Yas Marina
2.07 → Sochi 2.13 → Catalunya 2.31 → Budapest 2.415 → Melbourne 2.70 →
**Monte Carlo, Montreal and Singapore 3.75**, a ceiling sentinel meaning
"effectively impossible".

A companion coefficient, `t_gap_overtake_vel` [s/(km/h)], adjusts the threshold
for the difference in the two cars' maximum qualifying velocity. Its magnitude
is smallest at Montreal (−0.009) and Monte Carlo (−0.015) and largest at
Singapore (−0.061).

A data-driven counterpart, from a logistic regression over **131,000
adjacent-car battles**:

```
P(pass) = sigmoid( A_gp + k_p·Δpace + k_t·Δtyre_age )
k_p = +0.87   (standardised pace delta)
k_t = +0.46   (tyre age delta)
A_gp = per-circuit additive offset
```

Task-level Brier 0.0275 against a 0.0298 baseline; passes-per-race MAE 8.9. A
useful caution from the same work: its overtaking sub-model scored 0.0757 at
field level against a 0.0745 threshold baseline and was **shelved** — explicit
overtake modelling made the calibrated probability output worse, not better.

## Coverage

Overtake detection needs lap-by-lap position, so it is a **Timing-tier and
above (1996+)** metric. Archival pages report grid-to-finish position change
only, labelled as such, with no claim that it counts passes.

## Related

- [Gap to leader](gap-to-leader.md) — where lapping and unlapping are annotated
  on the chart.
- [Undercut delta](undercut-delta.md) — the strategic position changes this
  metric deliberately excludes.
- [Race trace](race-trace.md) — a line crossing is a *candidate*, and the trace
  is where candidates are inspected by eye.
- [Position at corner](position-at-corner.md) — sub-lap order, which is where a
  "maintained to the finish line" test can finally be checked against what
  actually happened on track.
