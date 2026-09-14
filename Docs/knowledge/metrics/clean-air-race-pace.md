---
type: Metric
title: Clean-air race pace
description: A driver's or team's underlying race pace estimated from green-flag, non-pit, traffic-free laps after fuel correction, with the traffic threshold declared as a tunable parameter rather than a consensus constant.
resource: /methods/clean-air-race-pace/
tags: [pace, clean-air, traffic, dirty-air, filtering, robust-regression, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — Laps selectors and columns
  - id: fastf1_telemetry
    resource: https://docs.fastf1.dev/api_reference/telemetry.html
    title: FastF1 telemetry API — add_driver_ahead, DistanceToDriverAhead
  - id: f1pace_degradation
    resource: https://f1pace.com/p/2024-f1-season-tire-degradation-discussion-rounds-1-5/
    title: f1pace.com — robust linear model per driver per compound, weighted aggregation
  - id: pitwall
    resource: https://arxiv.org/abs/2607.06495
    title: Pitwall — calibrated dirty-air window and loss parameters
  - id: tumftm_race_py
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/src/race.py
    title: race.py — min_t_dist hard minimum gap enforcement
  - id: dirty_air_causal
    resource: https://arxiv.org/abs/2608.03192
    title: The Persistence of the Dirty Air Penalty — causal analysis of the 2022 ground-effect regulations
  - id: j5t3313_strategy_sim
    resource: https://github.com/j5t3313/f1-strategy-sim
    title: j5t3313/f1-strategy-sim — stint fitting pipeline
status: stable
---

# Clean-air race pace

What a car was capable of when nothing was in its way. It is the number that
answers *"who actually had the quicker car on Sunday?"* — as distinct from who
finished ahead, which is a question about track position, strategy and luck.

The metric is a filtered, fuel-corrected, compound-normalised estimate of lap
time in free air. Every word in that sentence is a filter, and the whole value
of the metric is in whether the filters are applied honestly and declared.

## Pipeline

```
session.laps
  → 1. lap filtering        green flag, no pit, accurate, not deleted, not lap 1
  → 2. traffic exclusion    drop laps spent behind another car
  → 3. fuel correction      t_corr = t_obs − m(L)·k
  → 4. robust fit per       t_corr ~ TyreLife, per driver per compound
       driver per compound  → intercept = clean-air pace, slope = degradation
  → 5. compound offset      put compounds on a common footing before comparing
  → 6. aggregation          lap-weighted across stints; median, not mean
```

Steps 3 and 4's slope are documented separately in
[Fuel-corrected pace](fuel-corrected-pace.md) and
[Tyre degradation rate](tyre-degradation-rate.md). This page owns steps 1, 2, 5
and 6.

## Step 1 — lap filtering

```python
laps = (session.laps
        .pick_wo_box()                            # drop in-laps and out-laps
        .pick_accurate()                          # IsAccurate == True
        .pick_not_deleted()                       # Deleted == False
        .pick_track_status('1', how='equals'))    # green flag only
laps = laps[laps["LapNumber"] > 1]                # drop the standing start
```

| Exclusion | Reason | Field |
| --- | --- | --- |
| In-lap / out-lap | dominated by pit-lane time, not pace | `PitInTime`, `PitOutTime` |
| Lap 1 | standing start, grid position handicap, first-corner chaos | `LapNumber` |
| Non-green laps | SC ≈ 160% and VSC ≈ 140% of a normal lap | `TrackStatus` |
| Deleted laps | track-limits deletions | `Deleted`, `DeletedReason` |
| Inaccurate laps | FastF1's own timing-integrity flag | `IsAccurate` |

Track-status codes: `'1'` clear, `'2'` yellow, `'4'` Safety Car, `'5'` Red
Flag, `'6'` VSC deployed, `'7'` VSC ending. Prefer `session.track_status` and
`session.race_control_messages`; `fastf1.api` is documented as becoming private
in a future release.

Lap-1 exclusion is not just noise removal. The standing start is separately
modelled and separately interesting: `t_loss_firstlap` ranges from **1.378 s**
(Suzuka) to **5.919 s** (Hockenheim), and `t_loss_pergridpos` from **0.113
s/position** (Monza) to **0.178** (Monte Carlo). That belongs on a start
analysis, not in a pace average.

On the `pick_quicklaps()` trap — it takes its 107% reference from the fastest
lap *in the object it is called on*, not from the session best. Chained after
driver or compound filters it becomes a per-driver 107%, which is not what the
name suggests. `Laps.QUICKLAP_THRESHOLD = 1.07`. Either call it on the
unfiltered `session.laps` or compute the reference lap explicitly.

## Step 2 — traffic exclusion, and the threshold problem

This is the step most analyses omit, and it is the largest single source of
bias in the result. A car stuck two seconds behind a slower one is not slow; it
is blocked.

### How to measure following distance

FastF1's `Telemetry.add_driver_ahead()` adds two channels: `DriverAhead`
(driver number, as a string) and `DistanceToDriverAhead` (metres). Two caveats
from the documentation and from practice:

- It accumulates integration error over more than one or two laps. **Apply it
  per lap and concatenate.** For whole-session work `fastf1.legacy.inject_driver_ahead()`
  has no integration error and is the better tool.
- **Cars in the pit lane are not excluded** and will appear as "ahead" on the
  pit straight. A naive filter throws away clean laps because a car in the pits
  was geometrically in front.

A cheaper approximation that needs no telemetry, and therefore works across the
whole Timing tier (1996+): the cumulative-race-time gap to the car classified
ahead on the same lap. It is coarser — it is a lap-boundary measurement, not a
continuous one — but it is available for three decades of races where
`DistanceToDriverAhead` does not exist.

### The threshold is a parameter, not a constant

There is **no consensus value** for what counts as clean air, and this site
does not pretend otherwise. Published values span a factor of five:

| Source | Value | What it is |
| --- | ---: | --- |
| TUMFTM `min_t_dist` | 0.5 s | A *hard floor* in a simulation — the trailing car's lap time is inflated so the gap can never fall below it. Not a filter threshold. |
| TUMFTM `min_t_dist_sc` | 0.8 s | The same floor under safety car. |
| Pitwall `dirty_air_window` | 1.2 s default, range [0.4, 2.5] | A calibrated penalty window: a car inside it loses `dirty_air_loss`, default 0.35 s/lap, range [0.0, 0.8]. |
| Common analyst practice | 1.5–2.0 s | Reported convention, no single citable definition. |

A frequently repeated rule — "exclude a lap if the driver spent more than about
33% of it within 2.0 s of any car ahead" — is **not a sourced or consensus
standard**, and nothing found in the literature establishes it. It is a
reasonable-sounding recipe that circulates without provenance. If this project
uses a duty-cycle rule of that shape, it declares it as its own choice with its
own numbers, not as established practice.

**Project convention.** The threshold is a named, tunable parameter of the
analysis, stored with the result and rendered on the chart:

```yaml
clean_air:
  gap_threshold_s: 1.2        # default; from the Pitwall calibrated window
  duty_cycle_max: 0.33        # fraction of the lap permitted inside the threshold
  min_clean_laps: 4           # below this, no pace figure is published
```

Every clean-air pace figure on the site is accompanied by the threshold that
produced it, because **rankings are sensitive to it** — at 0.5 s a great many
laps survive that would not at 2.0 s, and the teams most affected are precisely
the midfield cars that spend the race in each other's wake.

### What the penalty actually costs

The best current causal estimate, from
[arXiv:2608.03192][dirty_air] — 100,486 racing laps over 2021–2025 pulled via
FastF1, with a compound-specific physics correction for fuel and tyre wear, OLS
with clustered standard errors plus Causal Forest / Double-ML:

- Causal-forest mean effect **0.019 s per second of following distance** in
  2021 and **0.018 s** in 2022–2025.
- The pooled 2022–2025 vs 2021 OLS interaction term is **β = −0.0025,
  p = 0.803** — no statistically significant change across the ground-effect
  regulation reset.

Aerodynamic context, from F1/FIA CFD as reported by The Race: a following car
retains about 55% of clean-air downforce at 10 m under 2019 rules, ~85% at the
2022 baseline, ~65% with 2025 cars; at 20 m, 65% / 95% / ~80%.

The practical reading: the penalty is real, it is roughly linear in proximity,
and it did not go away in 2022. That is why the filter exists.

## Step 5 — compound normalisation

A soft long run looks 0.4–1.0 s/lap faster than a hard one at the same circuit.
Medians are never compared across compounds.

The fit in step 4 produces a per-compound intercept `k_0`; putting drivers on a
common footing means offsetting by it, or comparing only within compound. The
size of the offset is genuinely uncertain — Pirelli's measured gap between
adjacent dry compounds at the 2022 Bahrain test was **0.8–1.0 s**, against
their own expectation of 0.5 s, and C4/C5 were near-identical there because C5
never reached its working range. See
[Tyre degradation rate](tyre-degradation-rate.md) for the full treatment.

## Step 6 — aggregation

- **Fit per driver per compound**, then aggregate to driver and team using a
  **lap-weighted average** — "more weight to stints with more laps and less
  weight to stints with fewer laps", in f1pace.com's phrasing. A 3-lap sample
  and a 22-lap sample are not equal evidence.
- Use the **median**, not the mean, of a driver's filtered laps when reporting
  a raw distribution. Lap-time distributions are right-skewed by definition:
  there is a floor and no ceiling.
- **Circuit-normalise before comparing races.** Express the result as a
  percentage of a reference — the session-fastest team's normalised pace — so
  that a 0.5% deficit means the same thing at Monaco (a ~70 s lap) as at Spa
  (~105 s). Raw seconds per lap are not portable between circuits.
- Report the **sample size** with every figure. A team page that says "0.31%
  off the pace" over nine surviving laps is saying much less than it appears
  to.

The season-long form of this metric is the development-trajectory chart: "%
off the fastest team's normalised race pace" on the y-axis, one line per
constructor, one point per round. That single chart carries the upgrade story
better than any table.

## Robust fit, not a mean

f1pace.com's stated reason for using a robust linear model is that it can
"deal properly with outliers, which is one of the biggest weaknesses that the
traditional linear model has". The same two-pass residual procedure documented
in [Tyre degradation rate](tyre-degradation-rate.md) applies here: fit, drop
laps with |residual| > 1200 ms, refit. What changes is which coefficient is
published — the **intercept** is clean-air pace, the slope is degradation.

## Honest-absence cases

This metric declines to produce a number, with designed copy explaining why,
when:

- fewer than 4 clean laps survive for a driver;
- the race ran wet or mixed, so compound normalisation has no meaning;
- a driver's entire race was run in traffic (which is itself the finding, and
  is stated as one);
- the circuit-layout has no established `t_lap_sens_mass`, so step 3 cannot
  run — the figure is then labelled uncorrected, or withheld.

## Related

- [Fuel-corrected pace](fuel-corrected-pace.md)
- [Tyre degradation rate](tyre-degradation-rate.md)
- [Teammate delta](teammate-delta.md) — the one comparison that holds the car
  constant and therefore needs none of this machinery.
- [Driver–car decomposition](driver-car-decomposition.md)

[dirty_air]: https://arxiv.org/abs/2608.03192
