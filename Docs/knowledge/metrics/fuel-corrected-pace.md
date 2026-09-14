---
type: Metric
title: Fuel-corrected pace
description: Normalising race lap times for the fuel the car has burned, using a per-circuit mass sensitivity in seconds per kilogram, so that pace and degradation can be read without the fuel-burn trend.
resource: /methods/fuel-corrected-pace/
tags: [fuel-correction, pace, normalisation, s-per-kg, lap-time, tumftm]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: tumftm_race_simulation
    resource: https://github.com/TUMFTM/race-simulation
    title: TUMFTM/race-simulation — Heilmeier et al. race simulation and calibrated parameter files
  - id: tumftm_pars_silverstone_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Silverstone_2019.ini
    title: pars_Silverstone_2019.ini — [TRACK_PARS] and [RACE_PARS] calibration
  - id: tumftm_calc_racetimes_basic
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim_basic/src/calc_racetimes_basic.py
    title: calc_racetimes_basic.py — vectorised additive lap-time construction
  - id: heilmeier_itsc_2018
    resource: https://doi.org/10.1109/itsc.2018.8570012
    title: Heilmeier et al., A Race Simulation for Strategy Decisions in Circuit Motorsports, IEEE ITSC 2018
  - id: f1pace_degradation
    resource: https://f1pace.com/p/2024-f1-season-tire-degradation-discussion-rounds-1-5/
    title: f1pace.com — tyre degradation method and flat 0.03 s/kg convention
  - id: j5t3313_strategy_sim
    resource: https://github.com/j5t3313/f1-strategy-sim
    title: j5t3313/f1-strategy-sim — 2026-era fuel mass assumption and stint fitting pipeline
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — Laps columns and selector methods
status: stable
---

# Fuel-corrected pace

A Formula 1 car starts a race heavy and finishes light, and the difference is
worth several seconds a lap. Any comparison of lap times taken at different
points in a race — a stint against a later stint, a driver who pitted early
against one who pitted late, a degradation slope against a flat line — is
measuring fuel burn unless fuel burn has been removed first. This metric
removes it.

Fuel correction is applied **unconditionally before** any degradation fit on
this site. That is a methodological commitment, not a default, and the reason
is in [Tyre degradation rate](tyre-degradation-rate.md): within a single stint,
fuel mass and tyre age are collinear, so an uncorrected slope silently blends
a positive degradation term with a negative fuel term and biases toward zero.

## Definition

Let

| Symbol | Meaning | Unit |
| --- | --- | --- |
| `t_obs(L)` | observed lap time on lap `L` | s |
| `k` | lap-time mass sensitivity, `t_lap_sens_mass` | s/kg |
| `m0` | fuel mass at the start of lap 1 | kg |
| `b` | fuel burned per lap, `b_fuel_perlap` | kg/lap |
| `m(L)` | fuel mass carried at the **start** of lap `L`, `= m0 − b·(L−1)` | kg |

Two directions of correction, and the site always states which one a chart uses:

```
zero-fuel reference   t_corr(L) = t_obs(L) − ( m0 − b·(L−1) ) · k
full-tank reference   t_norm(L) = t_obs(L) + b·(L−1) · k
```

The zero-fuel form answers *"what would this lap have been on an empty tank?"*
and produces the flattest series, which is what a degradation fit wants. The
full-tank form answers *"what would this lap have been at lap-1 fuel?"* and
keeps lap times near their real magnitude, which is what a reader wants on an
axis labelled in seconds. They differ by the constant `m0·k` and are otherwise
identical, so a slope fitted on one equals a slope fitted on the other.

### The evaluation convention

Fuel mass is evaluated at the **start** of the lap. That is not an arbitrary
choice — it is what the reference implementation does, and mixing conventions
introduces a half-lap bias of `b·k/2` (about 0.036 s at Silverstone 2019). The
vectorised form in `racesim_basic/src/calc_racetimes_basic.py` makes the
convention explicit through the zero-based `arange`:

```python
t_laps = np.ones(tot_no_laps) * t_base
t_laps += (m_fuel_init - b_fuel_perlap * np.arange(0, tot_no_laps)) * t_lap_sens_mass
t_laps[0] += t_loss_firstlap + (p_grid - 1) * t_loss_pergridpos
```

where the docstring defines `t_base` verbatim as `[s] base lap time
(= t_q + t_gap,racepace + t_car + t_driver)`.

## Mass sensitivity is per circuit, not a universal constant

The single most common error in amateur fuel correction is using one number
for every track. The TUMFTM 2019 calibration spans **0.019 to 0.038 s/kg** — a
factor of two. A stop-start, traction-limited circuit pays more for mass than
a fast, flowing one.

| Circuit | `t_lap_sens_mass` (s/kg) | | Circuit | `t_lap_sens_mass` (s/kg) |
| --- | ---: | --- | --- | ---: |
| Spielberg | 0.019 | | Sochi | 0.031 |
| Montreal | 0.022 | | Shanghai | 0.031 |
| Sakhir | 0.023 | | Catalunya | 0.033 |
| Mexico City | 0.026 | | Monte Carlo | 0.034 |
| Monza | 0.027 | | Silverstone | 0.034 |
| Budapest | 0.028 | | Hockenheim | 0.034 |
| Suzuka | 0.028 | | Yas Marina | 0.034 |
| Melbourne | 0.029 | | Le Castellet | 0.035 |
| Singapore | 0.030 | | Austin | 0.037 |
| Spa | 0.030 | | Baku | 0.038 |
| São Paulo | 0.030 | | | |

Source: `racesim/input/parameters/pars_<Circuit>_2019.ini`, key
`t_lap_sens_mass`, in [TUMFTM/race-simulation][tumftm]. Thirteen of the
twenty-one circuit files were independently re-read during verification with
zero discrepancies; the minimum (Spielberg 0.019) and maximum (Baku 0.038) were
both confirmed.

Competing conventions, recorded so that a chart built elsewhere can be read
correctly:

| Convention | `k` | Assumed start mass | Notes |
| --- | ---: | ---: | --- |
| TUMFTM 2019 | 0.019–0.038, per circuit | 110.0 kg | `b_fuel_perlap` 2.115 kg/lap |
| f1pace.com | 0.030 flat | 100 kg | Corrects "as if the car always carries 100 kg" |
| j5t3313 f1-strategy-sim | 0.030 flat | 92.5 kg gross, 89.5 kg usable | One full load ≈ 2.685 s |
| themotorsportmetrics | 0.025–0.040 band | — | 0.030–0.040 on stop-start layouts, 0.020–0.028 on short ones |

## Fuel load is an era parameter, and the 2019 numbers do not transfer

`m_fuel = 110.0` kg and `b_fuel_perlap = 2.115` kg/lap are a **2019**
calibration. The arithmetic is self-consistent — 110.0 / 2.115 = 52.0, exactly
the Silverstone 2019 race distance — and it is wrong for a modern page.

The 2026 regulations cut race fuel substantially and shift a large share of the
propulsive energy to the electrical side: total power unit output is about
**750 kW (400 kW ICE + 350 kW electrical)**, with a recharge limit of 8.5 MJ
per lap. The j5t3313 2026 simulator uses **92.5 kg** as the representative
start-of-race mass. Applying a 110 kg start to a 2026 race on a 0.034 s/kg
circuit **over-corrects the opening laps by roughly 0.5–0.6 s**, which is
larger than most of the effects the correction exists to expose.

Consequences for the pipeline:

- `m0` and `b` are stored per season (and per race where the distance is
  atypical), never hard-coded.
- `k` is stored per circuit-layout. For the six circuits that entered the
  calendar after the TUMFTM calibration window — Jeddah, Miami, Las Vegas,
  Losail, Zandvoort, Imola, and now Madring — there is **no published `k`**.
  Those pages either re-derive it or say so; they do not borrow a neighbour's
  number.
- Under caution the car burns less: `mult_consumption_sc = 0.25` and
  `mult_consumption_fcy = 0.5`, and `auto_consumption_adjust` raises later
  consumption so the car still finishes on fumes. A race with long safety-car
  periods has a fuel profile that a linear burn misrepresents.

## Worked example — Silverstone 2019, lap 20

Silverstone 2019: `k = 0.034` s/kg, `m0 = 110.0` kg, `b = 2.115` kg/lap,
52 laps.

```
m(20)  = 110.0 − 2.115 × 19        = 69.815 kg
fuel penalty at lap 20             = 69.815 × 0.034 = 2.374 s
fuel penalty at lap 1              = 110.0  × 0.034 = 3.740 s
fuel penalty at lap 52             = 110.0 − 2.115×51 = 2.135 kg → 0.073 s
```

So the fuel term alone moves lap time by **3.667 s** across the race at
Silverstone. A driver whose raw lap times fall by three and a half seconds from
lap 1 to lap 52 has, to a first approximation, done nothing but burn fuel.

## Implementation against FastF1

```python
laps = session.laps.pick_drivers(drv).pick_wo_box().pick_accurate()
k  = circuit_params["t_lap_sens_mass"]      # s/kg, per circuit-layout
m0 = season_params["m_fuel_init"]           # kg, per season
b  = season_params["b_fuel_perlap"]         # kg/lap, per season-race

secs = laps["LapTime"].dt.total_seconds()
mass = m0 - b * (laps["LapNumber"] - 1)     # mass at START of the lap
laps["LapTimeFuelCorrected"] = secs - mass * k
```

`LapTime`, `LapNumber` and the `pick_*` selectors are exact
[FastF1 `Laps`][fastf1] members. Note `pick_wo_box()` drops in-laps and
out-laps, which must go before any correction: their times are dominated by the
pit lane, not by fuel.

## Known limitations — stated, not hidden

- **The model is linear in mass and reality is not.** Lift-and-coast, energy
  deployment maps and engine modes all interact with fuel state. The f1pace.com
  author says of this correction directly that it "is too basic and doesn't
  really represent real life".
- **`k` is fitted, not measured.** It is a regression coefficient from a race
  simulation calibrated against one season, and it absorbs whatever else
  correlates with race progress at that circuit.
- **Under-fuelling and fuel-saving are invisible to it.** A driver managing
  fuel is slow for a reason the mass term cannot see.
- **2026 energy deployment may dominate the mass effect entirely.** The Pitwall
  calibration side-steps the problem by clamping a generic `fuel_effect` to
  [0.00, 0.15] s/lap (default 0.05) rather than modelling mass at all — an
  admission that a per-kilogram term is not obviously the right shape for the
  current era.

## Display rules

These are binding on every pace chart on the site.

1. Every pace chart states **whether it is fuel-corrected**, and if so, to
   which reference (zero-fuel or full-tank).
2. Every fuel-corrected figure states the `k`, `m0` and `b` used, and links
   here.
3. Where `k` for a circuit-layout is not established, the chart is labelled
   uncorrected. It is not silently corrected with a borrowed constant — that is
   the [honest absence](../../SPEC.md) principle applied to a coefficient.

## Downstream

- [Tyre degradation rate](tyre-degradation-rate.md) — consumes corrected laps;
  will not fit on raw ones.
- [Clean-air race pace](clean-air-race-pace.md) — step 3 of its pipeline is
  this correction.
- [Race trace](race-trace.md) — a fuel-corrected trace flattens the
  characteristic fan and leaves only strategy and tyre state visible.
- [Undercut delta](undercut-delta.md) — the per-lap terms it sums must be on a
  common fuel footing.

[tumftm]: https://github.com/TUMFTM/race-simulation
[fastf1]: https://docs.fastf1.dev/core.html
