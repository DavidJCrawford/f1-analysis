---
type: Metric
title: Tyre degradation rate
description: The per-stint rate at which lap time decays with tyre age, fitted robustly on fuel-corrected laps with a two-pass residual filter, a minimum stint length and an explicit compound offset.
resource: /methods/tyre-degradation-rate/
tags: [tyre, degradation, stint, robust-regression, compound-offset, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: tumftm_calc_tire_degradation
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/helper_funcs/src/calc_tire_degradation.py
    title: calc_tire_degradation.py — the four closed-form degradation models
  - id: tumftm_pars_silverstone_2019
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_Silverstone_2019.ini
    title: pars_Silverstone_2019.ini — fitted per-driver, per-compound coefficients
  - id: pitwall
    resource: https://arxiv.org/abs/2607.06495
    title: Pitwall — Monte Carlo race strategy engine with a piecewise-cliff degradation model
  - id: statespace_deg
    resource: https://arxiv.org/abs/2512.00640
    title: Bayesian state-space model of Formula 1 tyre degradation (December 2025)
  - id: f1pace_degradation
    resource: https://f1pace.com/p/2024-f1-season-tire-degradation-discussion-rounds-1-5/
    title: f1pace.com — robust linear fit per driver per compound, weighted aggregation
  - id: j5t3313_strategy_sim
    resource: https://github.com/j5t3313/f1-strategy-sim
    title: j5t3313/f1-strategy-sim — stint fitting pipeline and constants
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — Stint, Compound, TyreLife, FreshTyre
  - id: pirelli_compound_gaps
    resource: https://www.planetf1.com/news/pirelli-surprised-tyre-time-gaps
    title: Pirelli measured compound gaps at the 2022 Bahrain test
status: stable
---

# Tyre degradation rate

The rate at which a stint's lap time decays as the tyre ages, in seconds per
lap, fitted separately for every driver-stint. It is the single most requested
number in race analysis and the single easiest to compute wrongly.

Three decisions make the difference between a defensible slope and a plausible
one: fuel correction must come first, the fit must be robust, and the compound
offset must be separated from the slope.

## The model this site fits

Per stint, on fuel-corrected lap times, with tyre age as the covariate:

```
t_corr(a) = k_0 + k_1 · a + ε
```

where `a` is tyre age in laps (FastF1 `TyreLife`), `k_0` is the fresh-tyre
compound offset in seconds, `k_1` is **the degradation rate in s/lap**, and `ε`
is lap noise. The published figure is `k_1`, always with `k_0`, the compound,
the driver, the stint, the lap count and the fit's residual spread beside it.

This is the linear branch of the TUMFTM family, whose four closed forms are
given verbatim in `helper_funcs/src/calc_tire_degradation.py`:

```
linear model:       t_tire = k_0 + k_1_lin * age
quadratic model:    t_tire = k_0 + k_1_quad * age + k_2_quad * age**2
cubic model:        t_tire = k_0 + k_1_cub * age + k_2_cub * age**2 + k_3_cub * age**3
logarithmic model:  t_tire = k_0 + k_1_ln * ln(k_2_ln * age + 1)
```

Signature: `calc_tire_degradation(tire_age_start: int|float, stint_length: int,
compound: str, tire_pars: dict) -> np.ndarray|float`, branching on
`tire_pars['tire_deg_model'] in ['lin','quad','cub','ln']`, using `math` for a
single lap and `numpy` over `np.arange(tire_age_start, tire_age_start +
stint_length)` for a stint.

**Do not port the `numpy` `'cub'` branch verbatim.** It reuses `k_1_quad` and
`k_2_quad` in place of the cubic keys. This is a real bug in the upstream
source, confirmed on inspection, and copying it produces a cubic model that
silently evaluates as a quadratic.

### Why linear, given four choices

A race stint is 10–25 laps. Over that window a quadratic adds a parameter that
is rarely identifiable and frequently fits noise, and a cubic adds two. The
higher-order forms earn their place only where a cliff is genuinely present,
and the evidence for that is narrower than it looks — see *The cliff* below.
The site's default is linear; a non-linear form is used only where it clears an
explicit evidence gate, and the page says which form was used.

## The procedure

### 1. Segment into stints

FastF1's `Laps` carries `Stint` (an integer per driver), `Compound`,
`TyreLife` and `FreshTyre` directly. A stint boundary is a change in `Stint`;
it is not inferred from pit times.

### 2. Filter

```python
stint = (session.laps
         .pick_drivers(drv)
         .pick_wo_box()                       # drops in-laps and out-laps
         .pick_accurate()                     # IsAccurate
         .pick_not_deleted()                  # Deleted
         .pick_track_status('1', how='equals'))   # green flag only
stint = stint[stint["Stint"] == n]
```

Track-status codes are `'1'` clear, `'2'` yellow, `'4'` Safety Car, `'5'` Red
Flag, `'6'` VSC deployed, `'7'` VSC ending. Laps under `4`/`6`/`7` are run at
roughly 160% and 140% of a normal lap respectively and carry no degradation
signal; TUMFTM further scales the degradation those laps accrue by
`mult_tiredeg_sc = 0.25` and `mult_tiredeg_fcy = 0.5`.

**`pick_quicklaps()` is not used inside a stint filter.** It compares against
the fastest lap *in the `Laps` object it is called on*, not against the session
best — so chaining it after a driver, compound or stint filter silently
redefines the 107% reference to a per-driver or per-compound one. If a 107%
session gate is wanted, call it on the unfiltered `session.laps`, or compute
the reference lap explicitly. `Laps.QUICKLAP_THRESHOLD = 1.07`.

### 3. Fuel-correct — before fitting, always

See [Fuel-corrected pace](fuel-corrected-pace.md). This step is not optional
and not conditional.

The reason is collinearity. Within one stint, lap number and tyre age advance
together, so the fuel term (negative, roughly `−b·k` per lap) and the
degradation term (positive) are confounded. At Silverstone 2019 the fuel term
is `2.115 × 0.034 = 0.0719` s/lap of *improvement*; Hamilton's fitted A2
degradation is `0.0326` s/lap of *loss*. Fit an uncorrected stint and the
apparent slope is about `−0.039` s/lap: the tyre appears to be getting faster.
Uncorrected stint slopes at high-sensitivity circuits are not merely biased,
they can be sign-flipped.

### 4. Fit robustly, in two passes

Single lock-ups, traffic laps that survived the traffic filter, and one-off
errors are the normal case, not the exception. An ordinary least-squares fit
hands them disproportionate leverage at exactly the stint ends where leverage
matters most.

**Pass 1.** Fit `t_corr ~ a` over all surviving laps of the stint.

**Pass 2.** Compute residuals. Drop every lap with `|residual| > 1200 ms`.
Refit on what remains.

The ±1200 ms threshold is this project's convention, chosen to sit well outside
credible per-lap noise — the calibrated lap-noise range is 0.05–0.40 s with a
default of 0.18 s — while still catching a lock-up or a half-spin. It is stated
on the chart and it is tunable per circuit; it is not presented as a standard.

**Minimum stint length: 4 laps surviving the second pass.** A three-point fit
has one degree of freedom and no residual structure worth inspecting. Below
four, the stint is shown as points with no line and no published slope.

> A note on a figure that circulates: `MIN_STINT_LAPS = 5` in the
> j5t3313/f1-strategy-sim repository is the **shortest stint the strategy
> optimiser will consider**, not a fit-inclusion threshold. That pipeline's
> actual fitting minimum is 4 laps. The two are easy to conflate and filtering
> on the wrong one discards real stints.

Either an M-estimator (Huber) or the explicit two-pass trim above is
acceptable; the site uses the two-pass trim because it is reproducible by hand
from a published residual table, which matters for
[a published method page](../../SPEC.md).

### 5. Report with the compound offset attached

`k_0` **is** the compound offset — TUMFTM's own `[TIRESET_PARS]` comment
defines it as the "time offset of the compound for fresh tyres". A slope
without its intercept is uninterpretable across compounds.

The first lap of a new stint additionally carries a cold-tyre penalty,
`t_add_coldtires = 1.0` s at Silverstone 2019, which is a warm-up effect and
not degradation. It is either excluded from the fit or modelled as a separate
out-lap term; it is never allowed to become part of `k_1`.

## Real fitted coefficients

Silverstone 2019, per driver and per compound. Compounds in the TUMFTM files
are labelled A1–A5, hardest to softest within the weekend's allocation — not
Pirelli C-numbers and not the broadcast SOFT/MEDIUM/HARD.

| Driver | Compound | `k_0` (s) | `k_1_lin` (s/lap) | `k_1_quad` | `k_2_quad` (s/lap²) |
| --- | --- | ---: | ---: | ---: | ---: |
| HAM | A2 | 0.6096 | 0.0326 | 0.0144 | 0.0008 |
| HAM | A3 | 0.8682 | 0.0129 | 0.0051 | 0.0004 |
| HAM | A4 | 0.0000 | 0.5029 | 0.3583 | 0.0353 |
| RIC | A2 | 0.2863 | 0.0347 | — | — |
| RIC | A3 | 0.1675 | 0.0100 | — | — |
| RIC | A4 | 0.0000 | 0.0450 | — | — |
| VET | A2 | 0.7593 | 0.0100 | — | — |
| VET | A3 | 1.1045 | 0.0100 | — | — |
| VET | A4 | 0.0000 | 0.0470 | — | — |

Two things to read off this table. First, the coefficients are **per driver as
well as per compound** — the calibration absorbs tyre management into the
slope, so a "car" degradation figure derived from one driver is not the team's.
Second, the A4 rows have `k_0 = 0` by construction (A4 is the reference
compound in that file) and wildly different slopes, which is what a softer
compound looks like: no offset, steep decay.

## The cliff, and why it is not the default

The state of the art for non-linear degradation is a piecewise-linear knot
model ([Pitwall][pitwall], Eq. 1):

```
l(t, a) = f0^(t) + δ^(t)·a + 1[a > k^(t)] · s^(t) · (a − k^(t)) + ε,   ε ~ N(0, σ_lap²)
```

with `a` tyre age, `t` compound, `f0` compound base pace, `δ` the linear wear
slope, `k` the cliff knot age and `s` the extra rate past the cliff. Physically
plausible bands from that calibration: tyre-only wear in **[0, 0.22] s/lap**,
lap noise in **[0.05, 0.40] s** (default 0.18 s), generic fuel effect in
**[0.00, 0.15] s/lap** (default 0.05).

The important caveat is about coverage, not form. That work mines
**circuit-and-compound-specific** cliffs and applies only the **37** that pass
an evidence gate — at least a 25% reduction in sum of squared error against a
linear fit, on at least 300 laps. Everywhere else it falls back to linear. A
site that renders a cliff on every stint is claiming evidence that the source
of the model explicitly declines to claim.

Its calibration store is 126 races from 2018–2024 with **2022 excluded**
("its timing data does not load reliably"), held out on 2025–2026. Since 2022
is the first ground-effect season, nothing fitted on that store can be used to
argue about the 2022 regulation change.

## Other published forms, for reference

**Quadratic with AR(1) errors** (j5t3313/f1-strategy-sim): `μ = α + β·lap +
γ·lap²`; `ε₁ ~ N(0, σ)`, `ε_t ~ N(ρ·ε_{t−1}, σ·√(1 − ρ²))`. Parameters
`{α, β, γ, σ, ρ}` are compound-specific, fitted per circuit-compound pair by
MCMC (NUTS, 500 warmup / 1000 draws) on FP2 long runs from FastF1, out-laps and
in-laps removed, 4-lap minimum stint, fuel-corrected assuming ~60% of a 92.5 kg
load for FP2. `ρ` is estimated post hoc from residuals. The AR(1) term is the
honest part: consecutive lap times **are** correlated, and treating them as
independent understates the standard error on `k_1`.

**Bayesian state-space** ([arXiv:2512.00640][statespace], Hamilton at the 2025
Austrian GP via FastF1):

```
observation:  y_t     = α_t + γ·fuel_t + ε_t,                    ε_t ~ N(0, σ_ε²)
state:        α_{t+1} = (1 − I_pit,t)(α_t + ν) + I_pit,t·α_reset + η_t,   η_t ~ N(0, σ_η²)
priors:       σ_ε ~ N⁺(0.3, 0.1²)   σ_η ~ N⁺(0.1, 0.1²)
              ν   ~ N⁺(0.05, 0.1²)  α_reset ~ N(69, 0.1²)
```

with extensions for compound-specific `ν`, a time-varying accelerating `ν`, and
skewed-*t* observation errors for asymmetric driver mistakes. The benchmark was
ARIMA(2,1,2); the skewed-*t* state-space model beat it on predictive
performance.

Its estimates are the reason this page insists on uncertainty: **hard 0.054
s/lap (95% CI 0.004–0.133), medium 0.060 s/lap (95% CI 0.009–0.120)**. The
credible intervals overlap almost entirely — within a single race, the two
compounds' degradation rates were **not separable**. Any page that prints "the
hard degraded at 0.054 and the medium at 0.060" as a distinction is reporting
noise.

## Compound normalisation

Never compare medians across compounds. A soft long run reads 0.4–1.0 s/lap
faster than a hard one at the same circuit for reasons that have nothing to do
with the car or the driver.

Adjacent Pirelli dry compounds are commonly described as 0.3–0.6 s/lap apart,
but Pirelli's own measurement at the 2022 Bahrain test put it at **0.8–1.0 s**,
against an expectation of 0.5 s, with C4 and C5 near-identical there because C5
never reached its working range. Pirelli dropped C6 for 2026 because its gap to
C5 was too small. There is **no authoritative published table of per-circuit
C1–C5 offsets**; the site presents compound gaps as a fitted `k_0` per stint
with its uncertainty, or as a range, never as a constant.

A further identifier trap: FastF1's `Compound` column carries
`SOFT`/`MEDIUM`/`HARD`/`INTERMEDIATE`/`WET`, not the C-number. The mapping from
the weekend's nominated allocation to C-numbers is external data and must be
joined in; without it, "SOFT" in Bahrain and "SOFT" in Monza are different
rubber wearing the same label.

## Display rules

1. A degradation slope is never shown without its stint length, its compound
   and its `k_0`.
2. A slope fitted on fewer than 4 surviving laps is not shown as a line.
3. The scatter shows the trimmed points distinctly from the fitted points, so
   the reader can see what the residual filter removed.
4. Cross-compound comparison is offset-adjusted or not made.
5. The fitted form (linear / cliff) is labelled on the chart.

## Related

- [Fuel-corrected pace](fuel-corrected-pace.md) — the mandatory prior step.
- [Clean-air race pace](clean-air-race-pace.md) — shares steps 1–3 and takes
  the fit's intercept rather than its slope.
- [Undercut delta](undercut-delta.md) — consumes `k_0` and `k_1` directly.

[pitwall]: https://arxiv.org/abs/2607.06495
[statespace]: https://arxiv.org/abs/2512.00640
