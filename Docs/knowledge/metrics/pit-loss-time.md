---
type: Metric
title: Pit loss time
description: The lap time a driver gives up to make a pit stop, decomposed into in-lap, out-lap and standstill terms, published per circuit under green, VSC and safety-car conditions with no single global figure.
resource: /methods/pit-loss-time/
tags: [pit-stop, strategy, circuit, safety-car, vsc, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: tumftm_pars_silverstone_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Silverstone_2019.ini
    title: pars_Silverstone_2019.ini — [TRACK_PARS] pit parameters
  - id: tumftm_pars_montecarlo_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_MonteCarlo_2019.ini
    title: pars_MonteCarlo_2019.ini — the pits_aft_finishline = false case
  - id: tumftm_race_simulation
    resource: https://github.com/TUMFTM/race-simulation
    title: TUMFTM/race-simulation
  - id: f1chronicle_pit_loss
    resource: https://f1chronicle.com/f1-pit-stop-time-loss-data/
    title: f1chronicle — 2,106 green-flag stops, dry races 2022–2026
  - id: pitwall
    resource: https://arxiv.org/abs/2607.06495
    title: Pitwall — calibrated sc_pit_factor and vsc_pit_factor
  - id: livetiming_pitstopseries
    resource: https://livetiming.formula1.com/static/2026/2026-09-13_Spanish_Grand_Prix/2026-09-13_Race/PitStopSeries.jsonStream
    title: F1 LiveTiming PitStopSeries.jsonStream — stationary and pit-lane time
  - id: openf1_pit
    resource: https://api.openf1.org/v1/pit
    title: OpenF1 /v1/pit endpoint
status: stable
---

# Pit loss time

The total lap time surrendered by making a pit stop, relative to staying out.
It is the currency of every strategy question on the site — the undercut, the
overcut, the stop count, the value of a caution period — and it is
**circuit-specific to a degree that makes any single global figure misleading**.

## Three terms, not one

Pit loss is not the time the car stands still. It decomposes into three
independently-sourced quantities:

| Term | `.ini` key | What it is | Typical |
| --- | --- | --- | ---: |
| In-lap loss | `t_pitdrive_inlap` | Time lost on the lap of entry, from the pit-entry point to the finish line | 0.13–18.02 s |
| Out-lap loss | `t_pitdrive_outlap` | Time lost driving through the pit lane on the out-lap | 2.35–18.05 s |
| Standstill | `t_pit_tirechange_min` + `t_pit_tirechange_add` | Stationary time in the box: a floor plus a team-specific adder | 1.9 s + 0.43–1.01 s |

`t_pit_tirechange_min = 1.9` s at **every** circuit in the 2019 files —
confirmed at all thirteen circuits re-read during verification. The variation
is in the team adder and the in-lap/out-lap split.

A fourth field decides where the standstill lands:

**`pits_aft_finishline` [bool]** — whether the pit box sits after the finish
line. It determines whether the standstill time is charged to the in-lap or the
out-lap. Verified `true` at Silverstone, Montreal, Singapore, Suzuka,
Spielberg, Baku, Austin, Monza, Sakhir, Shanghai, Catalunya and Sochi; verified
`false` at **Monte Carlo**, which is the only circuit in that set where the
in-lap (14.084 s) dwarfs the out-lap (2.347 s). Melbourne (14.090 / 3.763) and
Le Castellet (18.022 / 3.272) show the same inverted signature but were not
among the files re-verified — treat their flag as **unverified**. Any chart
that renders in-lap against out-lap must handle this case or the bars read
backwards.

## Green-flag pit loss, per circuit

Drive-through loss = `t_pitdrive_inlap` + `t_pitdrive_outlap`. Standstill is
additional.

| Circuit | In-lap | Out-lap | **Green total** |
| --- | ---: | ---: | ---: |
| Spielberg | 2.691 | 11.396 | **14.087** |
| Montreal | 3.960 | 12.132 | **16.092** |
| Spa | 3.406 | 12.798 | **16.204** |
| Monte Carlo | 14.084 | 2.347 | **16.431** |
| Silverstone | 0.131 | 16.902 | **17.033** |
| Baku | 3.012 | 14.121 | **17.133** |
| Austin | 0.377 | 16.900 | **17.277** |
| Budapest | 2.728 | 15.048 | **17.776** |
| Melbourne | 14.090 | 3.763 | **17.853** |
| Mexico City | 1.395 | 16.885 | **18.280** |
| São Paulo | 3.800 | 14.608 | **18.408** |
| Catalunya | 3.040 | 16.003 | **19.043** |
| Hockenheim | 4.557 | 14.902 | **19.459** |
| Suzuka | 2.418 | 17.060 | **19.478** |
| Yas Marina | 1.550 | 18.047 | **19.597** |
| Shanghai | 4.881 | 15.045 | **19.926** |
| Sakhir | 3.359 | 17.173 | **20.532** |
| Monza | 2.754 | 17.841 | **20.595** |
| Le Castellet | 18.022 | 3.272 | **21.294** |
| Sochi | 4.527 | 17.198 | **21.725** |
| Singapore | 7.287 | 17.305 | **24.592** |

Spread: **14.09 s to 24.59 s**, a 10.5 s range. A two-stop strategy costs 21 s
more at Singapore than at Spielberg before any tyre effect is considered. This
is why no page on this site quotes "a pit stop costs about 20 seconds".

## Under caution — the correction that matters most

`[TRACK_PARS]` carries separate parameters for full-course-yellow (VSC)
conditions — `t_pitdrive_inlap_fcy`, `t_pitdrive_outlap_fcy` — and for safety
car — `t_pitdrive_inlap_sc`, `t_pitdrive_outlap_sc`. The reference is the
already-slowed caution lap, so individual terms can be negative.

| Circuit | Green | VSC | SC | SC reduction vs green |
| --- | ---: | ---: | ---: | ---: |
| Spielberg | 14.087 | 4.02 | 2.494 | **82%** |
| Spa | 16.204 | 8.16 | 4.29 | **73%** |
| Silverstone | 17.033 | 7.20 | 5.414 | **68%** |
| Monza | 20.595 | 15.42 | 10.160 | **51%** |
| Budapest | 17.776 | 9.95 | 9.47 | **47%** |
| Austin | 17.277 | 11.02 | 9.261 | **46%** |
| Sakhir | 20.532 | 11.782 | 13.821 | **33%** |
| Monte Carlo | 16.431 | 9.294 | 11.913 | **28%** |
| Singapore | 24.592 | 18.019 | 20.260 | **18%** |
| Sochi | 21.725 | 16.610 | 19.060 | **12%** |

### The two things this table refutes

**"Pitting under a safety car saves 30–60% of the pit loss."** It does not. The
reduction spans roughly **12% to 82%**. It is largest at short-pit-lane
circuits (Spielberg 82%, Spa 73%) and smallest where the pit lane is long or
the speed limit bites hardest (Sochi 12%, Singapore 18%, Monaco 28%). A global
percentage is not a simplification of this table; it is a different, wrong
claim.

**"A safety car is always cheaper than a VSC."** Also false. At four of the ten
circuits above the SC value is *worse* than the VSC value: Sakhir (13.821 vs
11.782), Singapore (20.260 vs 18.019), Monte Carlo (11.913 vs 9.294) and Sochi
(19.060 vs 16.610).

On the negative-value claim, precisely: negative caution values occur for the
**in-lap** term at some circuits — Silverstone −5.387, Austin −1.283,
Spielberg −0.937, Catalunya −0.472, Baku SC −1.760, Suzuka SC −0.334 — while
Montreal, Monza, Sakhir, Shanghai, Sochi and Singapore all have positive FCY
in-lap values. Monte Carlo is the one circuit with a negative **out-lap** value
(−0.450), a direct consequence of `pits_aft_finishline = false`.

### Why the reduction exists at all

The field is slower under caution, so the time lost relative to the field
shrinks. TUMFTM applies uniform lap-time multipliers at every 2019 circuit:
`mult_t_lap_sc = 1.6` and `mult_t_lap_fcy = 1.4`. The code note is explicit:
"In case of a FCY the lap times of the drivers increase to about 140% of a
normal lap. However, when driving directly behind an SC the lap time is about
160%." `calc_racetimes_basic` falls back to `t_lap_fcy = t_base * 1.4` and
`t_lap_sc = t_base * 1.6` when values are not supplied.

Pitwall's independent calibration on 2018–2024 data (126 races, 2022 excluded)
parameterises the same effect as multiplicative factors on pit loss:
`sc_pit_factor` default **0.45**, range [0.20, 0.80]; `vsc_pit_factor` default
**0.65**, range [0.45, 0.85]; with `sc_pace_mult` 1.40 in [1.15, 1.70] and
`vsc_pace_mult` 1.22 in [1.10, 1.35], and `vsc_dur_max` 3.0 laps in [2.0, 4.0].
The width of those ranges is the same finding as the table above, expressed as
a prior.

## Modern empirical cross-check

The TUMFTM calibration stops at 2019. An independent measurement over
**2,106 green-flag stops in dry races, 2022–2026** (f1chronicle) defines pit
loss as (in-lap + out-lap) minus twice the driver's own median pace on clean
laps either side of the stop window, excluding SC/VSC/red-flag stops.

| | Value |
| --- | ---: |
| 2026 median, Miami | 19.74 s |
| 2026 median, Silverstone | 20.95 s |
| 2026 median, Austria | 21.48 s |
| 2026 median, Monaco | 22.01 s |
| 2026 median, Barcelona | 23.83 s |
| Era median, 2022 | 22.58 s |
| Era median, 2026 | 22.07 s |

Re-running that method with 2, 3 or 5 clean laps either side moves no circuit
median by more than 0.3 s — a useful robustness result, and the reason this
site uses the same window construction when re-deriving pit loss from FastF1
for circuits TUMFTM never covered (Jeddah, Miami, Las Vegas, Losail, Zandvoort,
Imola, Madring).

Note the two measurements are not identical: TUMFTM's is a simulation
parameter fitted per circuit-year; f1chronicle's is an observed median. They
agree in magnitude and ordering, not to the decimal.

## Standstill time variability

The standstill is not a constant. TUMFTM models it as a floor plus a
team-specific adder plus a draw from a Fisk (log-logistic) distribution,
`t_pit_var_fisk_pars = [c, loc, scale]`, with draws rejected above three times
the mean.

| Team (Silverstone 2019) | `t_pit_tirechange_add` (s) | Fisk `[c, loc, scale]` |
| --- | ---: | --- |
| Mercedes | +0.434 | [1.563, −0.046, 0.480] |
| Red Bull | +0.486 | [2.012, −0.091, 0.577] |
| Ferrari | — | [2.414, −0.153, 0.737] |
| Williams | +0.726 | — |
| McLaren | +0.745 | — |
| Renault | +1.014 | — |
| Sauber / Alfa Romeo | — | [5.827, −0.953, 2.327] |

The long right tail is the point: a bad stop is much worse than a good stop is
good, which is why the *median* stationary time is the fair team statistic and
the mean is not.

## Measuring it from data — three incompatible quantities

This trips up almost every chart that mixes sources. The same stop has three
different "times":

| Quantity | Magnitude | Source |
| --- | ---: | --- |
| **Stationary time** — wheels stopped in the box | ~2.0–2.5 s | LiveTiming `PitStopSeries.jsonStream`, field `PitStopTime` |
| **Pit-lane time** — entry loop to exit loop | ~20–32 s | LiveTiming `PitLaneTime`; OpenF1 `lane_duration` / `pit_duration` |
| **Ergast-convention duration** | ~13–25 s | Jolpica `/{season}/{round}/pitstops.json` `duration`; F1DB `f1db-races-pit-stops.csv` `timeMillis` |

A single verified record, 2026 Spanish GP, session 11369, car 3, lap 14:

```
01:22:18.361{"PitTimes":{"3":[{"Timestamp":"2026-09-13T13:28:08.8Z",
  "PitStop":{"RacingNumber":"3","PitStopTime":"2.4","PitLaneTime":"31.067","Lap":"14"}}]}}
```

`PitStopSeries.jsonStream` is the only free source carrying both quantities in
one record. OpenF1's `/v1/pit` exposes a `stop_duration` field that was **null
in every record sampled** across both 2024 (session 9472) and 2026 (session
11369); its `pit_duration` and `lane_duration` are identical to each other.
F1DB's pit-stops table carries only one time column and cannot supply
stationary time at all.

**None of these three is pit loss.** Pit loss is a lap-time differential
against a counterfactual of staying out; the three measurements above are
durations of physical events. A chart labelled "pit stop time" must say which.

Parsing note for the jsonStream: lines are `<HH:MM:SS.mmm><json>` with a UTF-8
BOM, and the first line's payload is a JSON **array** while subsequent delta
lines are **integer-keyed objects**. A parser must handle both shapes.

## Coverage and honesty

- Published TUMFTM values exist for 21 circuits, season 2019, re-verified at
  13 of them with zero discrepancies.
- For post-2019 circuits there is **no published calibration**. Those pages
  either carry a re-derivation with its own method note, or say the figure is
  not established. They do not inherit a neighbouring circuit's number.
- The site never renders a single global pit-loss figure, in prose or in a
  chart annotation.

## Related

- [Undercut delta](undercut-delta.md) — where the pit-loss differential enters
  the strategy arithmetic, and where it cancels.
- [Race trace](race-trace.md) — a pit stop reads as a vertical drop of roughly
  the pit-loss magnitude.
- [Tyre degradation rate](tyre-degradation-rate.md) — the term pit loss is
  traded against.
