---
type: Metric
title: Undercut delta
description: The seconds gained or lost by pitting earlier than a rival, decomposed into the pit-loss differential, the fresh-tyre advantage and the out-lap warm-up penalty, with the overcut as its mirror.
resource: /methods/undercut-delta/
tags: [strategy, undercut, overcut, pit-stop, tyre, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: tumftm_pars_silverstone_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Silverstone_2019.ini
    title: pars_Silverstone_2019.ini — tyre coefficients, t_add_coldtires, pit parameters
  - id: pitwall
    resource: https://arxiv.org/abs/2607.06495
    title: Pitwall — delta_in / delta_out pit model and calibration bounds
  - id: f1chronicle_pit_loss
    resource: https://f1chronicle.com/f1-pit-stop-time-loss-data/
    title: f1chronicle — empirical pit-loss medians 2022–2026
  - id: bilstm_pitstop
    resource: https://pmc.ncbi.nlm.nih.gov/articles/PMC12626961/
    title: Bi-LSTM pit-stop timing model, 99,928 laps 2020–2024
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — Stint, Compound, TyreLife, PitInTime, PitOutTime
status: stable
---

# Undercut delta

The net time an attacker gains on a defender by stopping first. Positive means
the undercut worked; negative means the defender was better off staying out,
which is the overcut.

**There is no single canonical published formula for this.** What follows is
assembled from components that are each individually sourced, and the page says
so rather than implying a standard exists.

## Construction

Let **A** be the attacker, who pits at the end of lap `L`. Let **B** be the
defender, who pits `n` laps later, at the end of lap `L + n`. Over the window
of `n` laps, the undercut gain to A is

```
G_undercut = Σ_{j=0..n−1} [ t_B(L+j) − t_A(L+j) ]  −  [ P_A − P_B ]
```

where `t_X(·)` are the two drivers' lap times over the window and `P_X` is each
driver's own total pit loss — in-lap plus out-lap plus standstill. See
[Pit loss time](pit-loss-time.md).

The second bracket is what most explanations get wrong in both directions.
**`P_A − P_B` cancels to zero when both drivers stop under the same track
conditions**, which is the normal case: same circuit, same green-flag
conditions, similar crews. The circuit's pit loss therefore does *not* enter a
same-conditions undercut calculation, and the whole thing reduces to the tyre
delta. The term becomes large and decisive exactly when conditions differ —
when B's stop falls under a safety car or VSC, at which point `P_B` may be
12–82% smaller than `P_A` depending on the circuit, and no amount of out-lap
pace recovers it.

## Decomposing the per-lap term

For each lap `j` of the window, with `comp_X` the compound each driver is on
and `age_B(L+j)` the defender's tyre age:

```
t_B(L+j) − t_A(L+j) =  [ k_0(comp_B) + k_1(comp_B)·age_B(L+j) ]
                     − [ k_0(comp_A) + k_1(comp_A)·j ]
                     − ( j == 0 ? t_add_coldtires : 0 )
```

Read left to right, that is: the defender's degraded-tyre penalty, minus the
attacker's fresh-tyre state, minus a cold-tyre penalty charged to the
attacker's out-lap. `k_0` and `k_1` come from
[Tyre degradation rate](tyre-degradation-rate.md); both drivers' lap times must
be on a common fuel footing first, per
[Fuel-corrected pace](fuel-corrected-pace.md).

### Component values

| Component | Value | Source |
| --- | --- | --- |
| Cold-tyre penalty, first lap of a stint | `t_add_coldtires = 1.0` s | TUMFTM, Silverstone 2019 |
| Out-lap warm-up penalty | `delta_out`, calibrated; defaults to 0 until freed | Pitwall pit model |
| In-lap overhead | `delta_in`, calibrated; defaults to 0 until freed | Pitwall pit model |
| Standstill floor | 1.9 s at every 2019 circuit | TUMFTM `t_pit_tirechange_min` |
| Team standstill adder | +0.434 (Mercedes) to +1.014 s (Renault) | TUMFTM Silverstone 2019 |
| Standstill variability | Fisk (log-logistic), per-team `[c, loc, scale]` | TUMFTM |
| Fresh-vs-worn out-lap advantage | commonly 1.0–2.0 s/lap | multiple analyst sources; not a single citable measurement |

The out-lap advantage is the **dominant single term**. An undercut is, in
essence, a bet that one lap of fresh rubber beats one lap of the defender's
worn rubber by more than the cold-tyre penalty costs.

## Worked example — Silverstone 2019

Hamilton's fitted A2 parameters: `k_0 = 0.6096` s, `k_1_lin = 0.0326` s/lap.

A 20-lap-old A2 carries

```
wear      = 0.0326 × 20 = 0.652 s
offset    = 0.6096 s
total     = 1.262 s slower than the same compound fresh
```

Set that against a 1.0 s cold-tyre penalty on the attacker's out-lap and the
single-lap undercut gain is about **0.26 s** — real, but small enough that one
traffic-compromised out-lap erases it. Over a three-lap window with the
defender's tyre continuing to age, the accumulated gain grows roughly linearly
at `k_1` per lap, which is why an undercut at a high-degradation circuit is
worth several seconds and an undercut at a low-degradation one is worth almost
nothing.

## The overcut is the same equation with the sign flipped

```
G_overcut = Σ over the extra laps of [ out-lap penalty(B) + cold-tyre(B) − degradation(A) ]
```

It pays when the out-lap penalty and tyre warm-up cost exceed the leader's
degradation — historically at Monaco, at Hungary, and in cold conditions, all
places where tyres take a long time to switch on and degrade slowly once they
have.

## Where undercuts work, and where they cannot

Three circuit parameters decide it, and they do not always point the same way.

1. **Pit loss** ([Pit loss time](pit-loss-time.md)) — 14.09 s at Spielberg to
   24.59 s at Singapore. Relevant only when the two stops happen under
   different conditions, but decisive then.
2. **Degradation** — the `k_1` at that circuit for the compounds in play.
   High degradation makes the defender's tyre worse every lap, which is the
   undercut's fuel.
3. **Overtaking difficulty**, `t_gap_overtake` — the pace advantage in seconds
   a driver needs to complete a pass. Suzuka **1.26 s**; Silverstone 1.35;
   Sakhir 1.38; Shanghai 1.50; Hockenheim 1.56; Baku 1.62; Le Castellet 1.635;
   Monza 1.755; Spa 1.83; Austin 1.83; Spielberg 2.01; São Paulo 2.025;
   Mexico City 2.055; Yas Marina 2.07; Sochi 2.13; Catalunya 2.31; Budapest
   2.415; Melbourne 2.70; **Monte Carlo, Montreal and Singapore 3.75** — a
   ceiling sentinel meaning "effectively impossible".

   At a 3.75 s circuit, track position is decisive regardless of tyre state,
   and the undercut is the *only* passing mechanism available. That is the
   opposite of the naive reading, in which high pit loss should discourage
   stopping.

The effective threshold in the reference implementation is
`t_gap_overtake_tot = t_gap_overtake + t_gap_overtake_vel·(vel_max_behind −
vel_max_ahead) + t_teamorder`, where `t_gap_overtake_vel` is a per-circuit
adaptation in s/(km/h) and `vel_max` is each driver's maximum qualifying
velocity. The overtaken driver then pays `t_overtake_loser = 0.3` s, and both
cars in a battle pay `t_duel = 0.3` s once per lap.

## A shippable per-circuit index

"Undercut power", computed per race from FastF1 stint data:

```
undercut_power = (mean degradation slope over the last 5 laps of a stint)
                 × (laps of tyre advantage)
                 − (pit-loss differential)
```

It is an index, not a measurement, and it is labelled as one. Its value is
comparative: it ranks circuits and races against each other, and it should
never be presented with a unit that implies it predicts a specific gain.

## Detecting undercut attempts in data

The pit-cycle structure is recoverable from `session.laps` alone:

```python
stops = laps[laps["PitInTime"].notna()][["Driver", "LapNumber", "Stint", "Compound"]]
# an undercut attempt: A stops on lap L, B (within N positions and M seconds
# on the lap before) stops on lap L+n with 1 <= n <= 4
```

The window `n` matters. Beyond about four laps the two stops are separate
strategic decisions, not a reaction.

One directly citable reaction statistic, from a Bi-LSTM pit-timing model over
**99,928 laps, 2020–2024** (features `Driver`, `DriverNumber`, `Team`,
`Position`, `LapNumber`, `Stint`, `TyreLife`, `TrackStatus`, `Compound`,
`EventName`, `LapTime`, plus engineered `delta_laptime`,
`race_progress_fraction`, and `DriverAheadPit` / `DriverBehindPit` binaries):
**a driver's probability of pitting rises from 2.6% to 5.7% on the lap after
the car ahead pits.** Model performance: precision 0.77, recall 0.86, F1 0.81,
balanced accuracy 0.93, ROC-AUC 0.988 with a 256→128→64 architecture, dropout
0.2/0.3/0.3, sequence length 10.

That number is the cleanest available evidence that the undercut is a *reactive*
phenomenon and not merely a scheduling artefact.

## Reporting rules

1. An undercut delta is reported with the window `n`, both compounds, both tyre
   ages, and whether either stop fell under a caution.
2. When the two stops occurred under different track conditions, the pit-loss
   differential is shown as its own term — never folded into "tyre advantage".
3. The out-lap is shown separately from the rest of the window. It carries the
   cold-tyre penalty and usually most of the gain, and averaging it into the
   window hides the mechanism.
4. Traffic on the out-lap is checked before the delta is published. An out-lap
   spent behind a lapped car measures traffic, not strategy — see
   [Clean-air race pace](clean-air-race-pace.md).

## Related

- [Pit loss time](pit-loss-time.md)
- [Tyre degradation rate](tyre-degradation-rate.md)
- [Fuel-corrected pace](fuel-corrected-pace.md)
- [Race trace](race-trace.md) — the chart on which an undercut is legible as
  two converging lines around a pair of vertical drops.
