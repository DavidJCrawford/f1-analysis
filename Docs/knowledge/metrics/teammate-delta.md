---
type: Metric
title: Teammate delta
description: The symmetric percent difference between two drivers in the same car, with explicit session-selection rules, because it is the only comparison in which machinery is held constant.
resource: /methods/teammate-delta/
tags: [teammate, driver-comparison, qualifying, percent-difference, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1pace_teammate_delta
    resource: https://f1pace.com/p/2025-f1-season-qualifying-delta-between-teammates-rounds-1-21/
    title: f1pace.com — symmetric percent difference and session-selection rules
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — split_qualifying_sessions, pick_fastest
  - id: f1_driver_ability
    resource: https://github.com/vietandang2512/f1-driver-ability
    title: vietandang2512/f1-driver-ability — pairwise teammate ridge regression and chained Elo
  - id: tumftm_pars_silverstone_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Silverstone_2019.ini
    title: pars_Silverstone_2019.ini — t_driver and t_car parameters
  - id: openf1_drivers
    resource: https://api.openf1.org/v1/drivers
    title: OpenF1 /v1/drivers — per-session driver-to-team mapping
status: stable
---

# Teammate delta

Two drivers, one car, one session. It is the only comparison in motorsport in
which the machinery is genuinely held constant, and it is therefore the
foundation on which every broader driver rating is built — including the ones
this site declines to publish without uncertainty, in
[Driver–car decomposition](driver-car-decomposition.md).

## The formula

**Symmetric percent difference**, as stated verbatim by f1pace.com:

```
spd = 100 × (value₁ − value₂) / ((value₁ + value₂) / 2)
```

Negative means driver 1 was faster. The property that matters is
**reversibility**: swapping the two drivers flips the sign and preserves the
magnitude exactly. The ordinary percent difference does not do this — it
divides by one driver's time, so `A vs B` and `B vs A` give different
magnitudes, and the ranking depends on which name you typed first.

### Why not raw seconds

0.1 s at a 65 s circuit and 0.1 s at Spa (~105 s) are not the same deficit. The
first is 0.154%; the second is 0.095%. A season-long head-to-head in raw
seconds is dominated by which circuits happened to be long, which is not a
property of either driver.

A worked comparison from the 2025 season, median over rounds 1–21:

| Pairing | Team | Median spd | Median seconds |
| --- | --- | ---: | ---: |
| Verstappen vs Tsunoda | Red Bull | 0.781% | 0.594 s |
| Albon vs Sainz | Williams | 0.029% | 0.041 s |
| Norris vs Piastri | McLaren | 0.027% | 0.025 s |
| Bortoleto vs Hülkenberg | Sauber | 0.023% | — |

Note the ordering flip between the two columns: Albon–Sainz is a larger gap
than Norris–Piastri in percentage terms (0.029% vs 0.027%) but the raw-second
figure makes it look nearly twice as large (0.041 s vs 0.025 s). Bortoleto–Hülkenberg
was the smallest by mean.

## Session-selection rules

These are as important as the formula, and they are the part most comparisons
get wrong.

**For qualifying:**

1. Use only the **highest qualifying segment in which both teammates set a
   time**. If one reached Q3 and the other was knocked out in Q2, compare their
   **Q2** times — not Q3 against Q2, which compares different fuel, different
   tyre state and different track evolution.
2. **Drop the session entirely** if one driver set no time while the other did.
   A missing time is not an infinite deficit; it is an absent observation, and
   imputing anything for it biases the median.

FastF1 implements both directly:

```python
q1, q2, q3 = session.laps.split_qualifying_sessions()
for seg in (q3, q2, q1):                      # highest first
    a = seg.pick_drivers(drv_a).pick_fastest()
    b = seg.pick_drivers(drv_b).pick_fastest()
    if a is not None and b is not None:
        break
else:
    skip_session()
```

`split_qualifying_sessions()` and `pick_fastest()` are exact `Laps` members.

**For race pace**, the comparison is between the two drivers' clean-air race
pace estimates, not their race times — see
[Clean-air race pace](clean-air-race-pace.md). Race classification is
contaminated by strategy, traffic, damage and team orders in ways that
qualifying is not, and a race-time head-to-head is measuring the pit wall as
much as the drivers.

## Reporting

- **Median, not mean.** One qualifying session ruined by a yellow flag moves a
  mean and barely moves a median.
- **Sample size, always.** "0.027%" over 21 sessions and "0.027%" over 4 are
  different claims. The site prints `n` beside every delta.
- **Session-by-session distribution, not only the headline.** A pairing with a
  0.1% median and a 0.6% spread is a different story from a 0.1% median with a
  0.05% spread, and the second is the one that supports a conclusion.
- **Which segment each comparison came from.** A season aggregate that silently
  mixes Q1, Q2 and Q3 comparisons is aggregating over different track
  conditions.

## Caveats — the ones that actually bite

**The cars are not identical.** The premise fails more often than it is
admitted. Mid-season upgrades are frequently available to one car first;
damage, a floor change, a different power-unit element age and a different
specification of a development part all break the assumption. A teammate delta
across an upgrade-staggered weekend is not a driver comparison.

**Team orders and roles.** Fuel loads, engine modes and run plans are not
symmetric in a team with a designated lead driver. The reference race
simulation carries an explicit `t_teamorder` term — a signed per-driver
time modifier added to the overtake threshold when the two cars in a battle are
teammates — precisely because this effect is real enough to model.

**The reference-driver convention.** In the TUMFTM `[DRIVER_PARS]` block,
`t_driver` ("time loss per lap due to driver abilities") is expressed
**relative to the team's lead driver**, so the lead driver's value is 0.0 by
construction. At Silverstone 2019: HAM 0.0, BOT 0.021, RIC 0.0, HUL 0.153, SAI
0.159, KVY 0.239, MAG 0.315, GAS 0.359, RAI 0.068, VET 0.486, STR 0.113, KUB
0.468, and 0.0 for PER, GRO, VER, GIO, LEC, NOR, ALB, RUS. A zero there means
"this driver is the team's reference", not "this driver has no deficit", and
reading the column as a cross-team ranking is a category error.

**Chaining across teams compounds error.** A teammate delta is a *local*
comparison. Turning a network of local comparisons into a global ranking
requires a model, and the model's assumptions — transitivity, stationarity of
driver skill, comparability of eras — are all questionable. The two standard
approaches:

*Pairwise ridge regression.* One row per teammate pairing per race, one column
per driver, entries +1/−1 for the two drivers in the pairing and 0 elsewhere;
target `y` is the millisecond gap. Closed form
`β = (XᵀX + αI)⁻¹ Xᵀy`, with `α` chosen by cross-validation specifically to
stop low-sample drivers acquiring extreme coefficients. One published
implementation uses F1DB data from 2014 onward: 260 race weekends, **1,071
usable race-pace comparisons and 2,569 usable qualifying comparisons**.

*Chained Elo.* All drivers start at 1500, `K = 24`,
`expected_A = 1 / (1 + 10^((R_B − R_A)/400))`,
`new_R_A = R_A + K·(actual_A − expected_A)`.

Both produce a single ranked list, and both hide the width of their own
uncertainty in doing so. This site's position on publishing such lists is in
[Driver–car decomposition](driver-car-decomposition.md): only with visible
uncertainty intervals and a named method, or not at all.

## Driver-to-team membership is a per-session fact

A teammate delta requires knowing who the teammates *were*, and that is not a
season-level attribute.

At the 2026 Spanish Grand Prix (session 11369), the live driver list had **Liam
Lawson at Red Bull Racing and Yuki Tsunoda at Racing Bulls** — contradicting
the declared season lineup of Red Bull = Verstappen + Hadjar, Racing Bulls =
Lawson + Lindblad. The explanation is ordinary: Isack Hadjar was ruled out from
the Dutch Grand Prix onward with a wrist injury, Lawson was promoted, and
Tsunoda returned at Racing Bulls.

**Therefore driver-team membership is keyed on `(session_key)`, or at minimum
`(year, round)` — never on `(year)`.** A pipeline that assumes season-level
lineups will compute deltas between drivers who were never teammates, and will
do so silently. F1DB supports season granularity via
`f1db-seasons-entrants-drivers.csv`; per-race granularity comes from the race
results table or from the per-session driver list.

The natural presentation that falls out of this is better than a static
two-driver card: a **timeline of driver stints with substitution markers**,
which is both more accurate and more interesting.

## Related

- [Clean-air race pace](clean-air-race-pace.md) — the race-side input.
- [Driver–car decomposition](driver-car-decomposition.md) — what happens when
  teammate deltas are chained, and why the result carries wide uncertainty.
- [Fuel-corrected pace](fuel-corrected-pace.md) — required before any race-pace
  teammate comparison.
