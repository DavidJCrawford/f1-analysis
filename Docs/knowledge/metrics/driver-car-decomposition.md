---
type: Metric
title: Driver–car decomposition
description: The statistical families that attempt to separate driver skill from machinery, their correctly attributed findings, the disputed constructor variance share, and the site policy of publishing such figures only with visible uncertainty.
resource: /methods/driver-car-decomposition/
tags: [driver-rating, variance-decomposition, multilevel-model, ridge-regression, elo, uncertainty, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: bell_2016
    resource: https://doi.org/10.1515/jqas-2015-0050
    title: Bell, Smith, Sabel & Jones (2016), Formula for success — multilevel modelling of F1 driver and constructor performance 1950–2014, JQAS 12(2):99–112
  - id: bell_2016_eprint
    resource: https://eprints.whiterose.ac.uk/96995/
    title: White Rose eprint of Bell et al. (2016)
  - id: rapm_2508
    resource: https://arxiv.org/abs/2508.00200
    title: Predicting Formula 1 Race Outcomes — decomposing the roles of drivers and constructors through linear modeling
  - id: bayesian_2203
    resource: https://arxiv.org/abs/2203.08489
    title: Bayesian disentangling of driver skill and constructor advantage
  - id: timerank_2312
    resource: https://arxiv.org/abs/2312.14637
    title: Time–rank duality in Formula 1 results modelling
  - id: f1_driver_ability
    resource: https://github.com/vietandang2512/f1-driver-ability
    title: vietandang2512/f1-driver-ability — pairwise ridge and chained Elo implementation
  - id: f1metrics_model
    resource: https://f1metrics.wordpress.com/2019/09/10/a-new-f1metrics-model/
    title: f1metrics — the 2019 revision of the sigmoid scoring-rate model
  - id: tumftm_pars_silverstone_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Silverstone_2019.ini
    title: pars_Silverstone_2019.ini — t_car and t_driver
status: stable
---

# Driver–car decomposition

How much of a result belongs to the driver and how much to the car. It is the
most-asked question in Formula 1 and the one where the gap between public
confidence and statistical confidence is widest.

**Site policy, stated before any method:** metrics of this kind are published
only with **visible uncertainty intervals and a named method**, or not at all.
No ranked list of drivers appears on this site without the interval on every
row and the sample size behind every comparison.

## The foundational constraint

The only comparison in which car quality is genuinely held constant is **two
teammates in the same race in the same car** — see
[Teammate delta](teammate-delta.md). Everything else is an attempt to chain
those local comparisons across the grid and across eras, and every method below
is a different way of doing that chaining. The chaining is where the
uncertainty comes from, and it is not small.

## The variance split is disputed, not settled

This is the single most misattributed result in public F1 analysis, so it is
worth separating carefully.

| Claim | Source | Method | Period | Specification |
| --- | --- | --- | --- | --- |
| **No percentage split at all** | Bell, Smith, Sabel & Jones (2016), *JQAS* 12(2):99–112, [doi:10.1515/jqas-2015-0050][bell] | Cross-classified multilevel model | 1950–2014 | Partitions variance across team, team-year and driver levels; reports no headline constructor share |
| **Constructors ≈ 64.0%** | [arXiv:2508.00200][rapm] | Time-decayed ridge regression (RAPM-style) with LOESS smoothing | 2014–2024 | **DNF-excluded** model |
| **Constructors ≈ 88%** | [arXiv:2203.08489][bayes] | Bayesian multilevel rank-ordered logit on finishing positions | — | Cited by the 64% paper as prior work it contrasts against |

Three things follow.

**Bell et al. is not the source of the 64% figure.** It covers 1950–2014, which
predates the hybrid era almost entirely, and it produces no constructor-share
percentage. Attaching the number to that paper — a common error — attributes a
ridge-regression result to a multilevel model over a different period.

**The 64.0% figure is specification-dependent.** It is the DNF-excluded model
in its own paper. Whether retirements count is not a detail: it is the
difference between measuring pace and measuring pace-plus-reliability, and
reliability is overwhelmingly a constructor property — see
[Reliability and DNF rate](reliability-dnf.md).

**The literature does not converge.** The 64% paper explicitly contrasts its
result against the ~88% reported by earlier work. A 24-point spread between two
serious published estimates is the finding. Any page that prints one number as
*the* split is asserting a consensus that does not exist.

The site's presentation: when a constructor share is quoted at all, it is
quoted **as a range with both methods named**, or not quoted.

### What Bell et al. actually found

The findings that *are* attributable to it, and which are more interesting than
a percentage:

- The response is **points scored in a race**, standardised across seasons and
  normalised — necessary because points systems changed repeatedly (1950–59 was
  8-6-4-3-2 for the top five plus a fastest-lap point; 1961–90 was 9-6-4-3-2-1;
  the fastest-lap point returned in 2019 and was abolished again from 2025).
- Variance is partitioned across **team, team-year and driver** levels, with
  complex variance functions letting effects vary by **year, track type and
  weather**.
- **Fangio ranks first.**
- **Team effects exceed driver effects and grow over time** — but team
  dominance is **reduced in wet weather and on street circuits**.

That last finding is the editorially valuable one, because it is conditional
and testable rather than a single number, and because it says something a fan
can check against their own memory of wet races.

## The five method families

### 1. Symmetric percent difference — the local comparison

`spd = 100 × (v₁ − v₂) / ((v₁ + v₂) / 2)`, teammate against teammate, with the
session-selection rules and the reversibility property documented in
[Teammate delta](teammate-delta.md). The only method here with no chaining and
therefore no chaining error.

### 2. Pairwise teammate ridge regression

Design matrix: one row per teammate pairing per race, one column per driver,
entries **+1/−1** for the two drivers in the pairing and 0 elsewhere. Target
`y` = millisecond gap between teammates.

```
β = (XᵀX + αI)⁻¹ Xᵀ y
```

`α` is chosen by cross-validation, and its explicit purpose is to **stop
low-sample drivers acquiring extreme coefficients**. That is the honest part of
ridge: the shrinkage is a statement that a driver with three teammate
comparisons is not known as well as one with three hundred. It is also why the
coefficients must be published *with* the shrinkage acknowledged — a shrunk
estimate is not an unbiased one.

One published implementation over F1DB data from 2014 onward: 260 race
weekends, **1,071 usable race-pace comparisons, 2,569 usable qualifying
comparisons**.

### 3. Chained Elo on teammate pairs

```
all drivers start at 1500
K = 24
expected_A = 1 / (1 + 10^((R_B − R_A) / 400))
new_R_A    = R_A + K·(actual_A − expected_A)
```

Simple, order-dependent, and volatile. Elo's rating is path-dependent — the
sequence in which comparisons arrive changes the answer — and its implied
uncertainty is never reported by the algorithm itself. If shown, it is shown
with its volatility band, and the band is computed, not asserted.

### 4. Multilevel and RAPM-style regression

The two papers in the table above. The RAPM approach is adapted from basketball
and hockey regularised adjusted plus-minus: time-decayed ridge regression with
LOESS smoothing over 2014–2024. Two of its secondary findings are more robust
than the headline and worth carrying:

- Constructor importance **rises** within a rank-agnostic cohort (top-10 points
  finishers).
- Constructor importance **falls in qualifying** — which is exactly what the
  teammate-delta literature would predict, since qualifying is the session in
  which strategy, reliability and traffic contribute least.

A further relevant strand is the **time–rank duality** work
([arXiv:2312.14637][timerank]), on the relationship between modelling finishing
*times* and finishing *ranks* — which is a question about the response
variable, and therefore upstream of every split quoted above.

### 5. f1metrics sigmoid scoring-rate model

```
Performance  = Driver + Team + Season + Age + Experience + Customer + variation
Scoring rate = S(Performance)                    # S is a sigmoid link
```

Response is points per race on a 0–10 normalised scale. Specification details
that matter because each is a modelling choice with a defensible alternative:

- Age curve fitted at **3-year knots from 20 to 47**, with a plateau at roughly
  **26–35**.
- Experience uses "number of previous four seasons in F1".
- A customer-car penalty averaging about **0.2** for 1950–1980 non-works
  entries.
- **Non-driver mechanical DNFs are excluded entirely**; driver-caused crashes
  score zero.
- The extended points system decays by a factor of **10 per 7 places**, and
  each driver's best and worst season are down-weighted to 50%.

That DNF handling is the same lever as the 64%/88% divergence, showing up in a
third method. It is the single most consequential specification choice in this
whole literature.

## A decomposition that is not a rating

One route avoids ranked lists entirely and is the one this site prefers.

The additive lap-time model used in race simulation exposes car and driver as
separate scalar seconds-per-lap terms, published per race:

- **`t_car`** — "time loss per lap due to car abilities". Silverstone 2019:
  Ferrari 0.033, Mercedes 0.042, Red Bull 0.224, McLaren 0.845, Renault 0.914,
  Alfa Romeo 0.954, Haas F1 Team 1.022, Toro Rosso 1.026, Racing Point 1.259,
  Williams 2.276.
- **`t_driver`** — "time loss per lap due to driver abilities", **relative to
  the team's lead driver**. Silverstone 2019: HAM 0.0, BOT 0.021, RAI 0.068,
  STR 0.113, HUL 0.153, SAI 0.159, KVY 0.239, MAG 0.315, GAS 0.359, KUB 0.468,
  VET 0.486; RIC, PER, GRO, VER, GIO, LEC, NOR, ALB and RUS are 0.0 as their
  teams' references.

Two readings that are easy to get wrong:

**`t_car` is an absolute time loss against a notional reference, not a delta
against the fastest car.** The fastest car at Silverstone 2019 is **Ferrari at
0.033**, not Mercedes at 0.042. The correct slowest-versus-fastest figure is
therefore **2.243 s/lap** (Williams against Ferrari), not 2.234 s/lap (Williams
against Mercedes).

**A `t_driver` of 0.0 means "this driver is the team's reference", not "this
driver has no deficit".** The column is not a cross-team ranking and cannot be
sorted into one.

Because `t_q`, `t_gap_racepace`, `t_car`, `t_driver`, the fuel term and the
tyre term are **additive and all published**, a team page can render an exact
waterfall:

```
qualifying benchmark  t_q
  + race-pace de-rate t_gap_racepace     1.812 s (Shanghai) … 6.084 s (Singapore)
  + car deficit       t_car              0.033 … 2.276 s at Silverstone 2019
  + driver deficit    t_driver           0.0 … 0.486 s
  + fuel load         m(L) · k           see fuel-corrected-pace
  + tyre state        k_0 + k_1·age      see tyre-degradation-rate
  = actual lap time
```

This is a decomposition of **one race** into named, sourced, additive
components — not a claim about a driver's career. It is derivable from public
data, it is checkable term by term, and it is a defensible editorial graphic in
a way that a ranked driver list is not.

Its own limitation, stated: the parameters are calibrated **per race-year** and
must not be transplanted across seasons, and the published calibration stops at
2019.

## Publication rules

1. Never a single ranked list without intervals on every row.
2. Always the sample size behind each teammate pairing.
3. Always the specification — in particular **whether DNFs are included**,
   since that choice alone spans much of the literature's disagreement.
4. Where two published methods disagree, **show the range and name both**.
5. Prefer the conditional findings (team dominance falls in the wet and on
   street circuits; constructor share falls in qualifying) over the
   unconditional percentage, because they are more robust and more interesting.
6. A per-race additive waterfall is preferred over any career rating.

The reason this is a policy and not a preference: such metrics are
high-engagement and low-confidence. With published constructor shares spanning
64% to 88%, a cross-team driver ranking built on top of them carries
uncertainty that frequently exceeds the differences it purports to show. On a
site whose entire value is being right, that is not a chart — it is a liability
with a legend.

## Related

- [Teammate delta](teammate-delta.md) — the only comparison that holds the car
  constant.
- [Clean-air race pace](clean-air-race-pace.md) — the pace input.
- [Reliability and DNF rate](reliability-dnf.md) — the DNF-inclusion question
  in its own right.
- [Fuel-corrected pace](fuel-corrected-pace.md) and
  [Tyre degradation rate](tyre-degradation-rate.md) — two of the waterfall's
  terms.

[bell]: https://doi.org/10.1515/jqas-2015-0050
[rapm]: https://arxiv.org/abs/2508.00200
[bayes]: https://arxiv.org/abs/2203.08489
[timerank]: https://arxiv.org/abs/2312.14637
