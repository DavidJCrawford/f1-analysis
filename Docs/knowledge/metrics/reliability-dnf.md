---
type: Metric
title: Reliability and DNF rate
description: Era-normalised finish rates and retirement-cause classification, with the hard constraint that all 2024-onward retirement causes must come from F1DB because the Ergast-schema status field is collapsed.
resource: /methods/reliability-dnf/
tags: [reliability, dnf, retirement, constructors, power-unit, era-normalisation, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_release
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 — race results, reasonRetired, positionText
  - id: jolpica_ergast_differences
    resource: https://raw.githubusercontent.com/jolpica/jolpica-f1/main/docs/ergast_differences.md
    title: jolpica-f1 — documented divergences from Ergast including the status collapse
  - id: jolpica_status_2024
    resource: https://api.jolpi.ca/ergast/f1/2024/status.json
    title: jolpica /2024/status.json — empirical evidence of the collapse
  - id: tumftm_pars_mcs
    resource: https://raw.githubusercontent.com/TUMFTM/race-simulation/master/racesim/input/parameters/pars_mcs.ini
    title: pars_mcs.ini — per-team failure and per-driver accident probabilities
  - id: pitwall
    resource: https://arxiv.org/abs/2607.06495
    title: Pitwall — dnf_prob calibration bounds
status: stable
---

# Reliability and DNF rate

The share of starts a car fails to finish, and why. It is one of the few
metrics on this site that spans the entire 1950–2026 range, and it is
completely uninterpretable without era normalisation: a 90% finish rate in 1988
is exceptional and the same number in 2024 is poor.

## The source constraint — read this first

**All retirement-cause and laps-down analysis for 2024–2026 must come from
F1DB.** Not from jolpica, not from any Ergast-schema source.

The Ergast-schema status field collapses every retirement to a single
`Retired` status. The documentation says this applies "From the 2025 season";
the data says otherwise. Empirically, by year, counting non-Finished,
non-lap-down statuses:

| Year | Distinct statuses returned | Detail |
| --- | ---: | --- |
| 2010 | 26 | Collision 25, Hydraulics 19, Accident 17, Engine 13, Gearbox 9, Suspension 6, Wheel 5, Brakes 3, Retired 3, Spun off 2, … |
| 2018 | 24 | Collision 19, Engine 13, Accident 7, Brakes 7, Collision damage 5, … |
| **2024** | **4** | **Lapped 138, Retired 49, Did not start 3, Disqualified 2 — already collapsed** |
| 2025 | 4 | Lapped 89, Retired 51, Disqualified 6, Did not start 3 |
| 2026 | 3 | Lapped 101, Retired 57, Did not start 7 |

Two things are lost, not one:

1. **Retirement cause** — everything becomes `Retired`.
2. **Lap-down margin** — the granular `+1 Lap` … `+N Laps` statuses collapse
   into a single `Lapped` (statusId 143), and `Did not start` into statusId
   142.

F1DB retains full granularity over exactly the years the other source loses it.
Distinct non-empty retirement causes among DNF/NC rows: **2024 = 15, 2025 = 14,
2026 = 20**. Only 2 of the 2026 DNF rows have an empty `reasonRetired`.

This is a correctness trap that would silently produce wrong reliability charts
for three recent seasons, and it is enforced in the pipeline rather than by
convention.

The global Ergast status table remains the canonical taxonomy for **pre-2024**
work: 136 statuses, headed by Finished 8147, +1 Lap 3850, Engine 2011, +2 Laps
1593, Accident 1047, Collision 833, Gearbox 805, Spun off 792, Suspension 431,
Lapped 398, Transmission 321, Electrical 315, Retired 305, Brakes 250, Withdrew
246, Clutch 214, Not classified 172, Fuel system 155, Disqualified 153, Turbo
146, Hydraulics 138, Power Unit 41, ERS 5.

## Denominator rules

The classification codes in F1DB's `positionText`, with whole-dataset counts:

| Code | Meaning | Count | In starts? | A retirement? |
| --- | --- | ---: | --- | --- |
| `DNF` | Did not finish | 8,776 | yes | **yes** |
| `NC` | Not classified | 200 | yes | **yes** |
| `DSQ` | Disqualified | 161 | yes | no — compliance |
| `EX` | Excluded | 15 | yes | no — compliance |
| `DNS` | Did not start | 381 | **no** | n/a |
| `DNQ` | Did not qualify | 1,041 | **no** | n/a |
| `DNPQ` | Did not pre-qualify | 338 | **no** | n/a |
| `DNP` | Did not practise | 5 | **no** | n/a |

Rules:

- **Exclude DNQ, DNPQ, DNP and DNS from the denominator.** Those cars never
  started; counting them as failed finishes makes 1980s pre-qualifying grids
  look catastrophically unreliable when the effect is entry-list size.
- **Treat DNF and NC as retirements.**
- **Do not count DSQ/EX as retirements.** Track them separately as a compliance
  metric. A disqualification for illegal skid-block wear is not a reliability
  event, and conflating them produces a reliability chart that moves when the
  stewards do.

`reasonRetired` is populated on **10,112 of 27,599** result rows. Sparse
population in early seasons is a real limit, and it is stated wherever an early
decade's cause breakdown is shown.

## Era normalisation

Computed directly from F1DB `f1db-races-race-results.csv` (v2026.14.0),
excluding DNS/DNQ/DNPQ/DNP from starts, counting DNF+NC as retirements,
classifying `{Accident, Collision, Spun off, Collision damage, Accident damage,
Fatal accident, Spin}` as accident-caused:

| Decade | Starts | DNFs | DNF % | Non-accident | Accident | Accident share of DNFs |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1950 | 1,924 | 739 | 38.4% | 641 | 98 | 13.3% |
| 1960 | 1,923 | 848 | 44.1% | 740 | 108 | 12.7% |
| 1970 | 3,432 | 1,527 | 44.5% | 1,145 | 382 | 25.0% |
| 1980 | 3,920 | 1,992 | **50.8%** | 1,527 | 465 | 23.3% |
| 1990 | 3,859 | 1,760 | 45.6% | 1,139 | 621 | 35.3% |
| 2000 | 3,610 | 1,041 | 28.8% | 655 | 386 | 37.1% |
| 2010 | 4,264 | 722 | 16.9% | 429 | 293 | 40.6% |
| 2020 | 2,902 | 347 | **12.0%** | 182 | 165 | **47.6%** |

Two stories in one table. Cars stopped breaking — 50.8% to 12.0% — and as they
did, the *composition* of retirements inverted: accidents went from 13% of
DNFs to 48%, not because there are more accidents, but because there is
almost nothing else left.

**Caveat, stated on every chart that uses these figures:** the 1950s and 1960s
accident share is understated, because `reasonRetired` is sparse in early
seasons and unclassified retirements fall into the non-accident bucket by
default. These figures are reproducible from a pinned F1DB release and should
be preferred over the round numbers that circulate on secondary sites.

**The design consequence:** a team's finish rate is always plotted against its
own era baseline, never on an absolute axis. The small-multiple dot plot — one
dot per team per season, against the era median line — is the archetype.

## Cause bucketing

`reasonRetired` mixes mechanical failure, driver error and technical
infringement in one free-text field, so a project must define its own buckets
and publish them. This site's buckets, with member strings:

| Bucket | Members |
| --- | --- |
| **Accident** | Accident, Collision, Spun off, Collision damage, Accident damage, Spin, Fatal accident, Accident on formation lap, Accident in practice |
| **Power unit** | Engine, Turbo, ERS, Power Unit, Power loss, Battery, Injection, Ignition, Alternator, Exhaust, Overheating, Radiator, Water leak, Water pump, Oil leak, Oil pressure, Oil pump, Oil pipe, Fuel system, Fuel pump, Fuel pressure, Fuel leak, Fuel pipe, Out of fuel |
| **Drivetrain** | Gearbox, Transmission, Clutch, Driveshaft, Halfshaft, Differential, Axle |
| **Chassis / running gear** | Suspension, Steering, Brakes, Wheel, Wheel bearing, Wheel nut, Chassis, Undertray, Front wing, Rear wing, Broken wing, Handling, Vibrations |
| **Tyre** | Tyre, Puncture |
| **Electrical / hydraulic** | Electrical, Electronics, Hydraulics, Pneumatics, Throttle |
| **Human / other** | Withdrew, Physical, Injury, Driver unwell, Push start |
| **Compliance** | Disqualified, Excluded, Car underweight, Illegal skid block wear, Technical infringements |

The top `reasonRetired` values across the whole dataset, for scale: Engine
2023, Accident 929, Collision 922, Gearbox 841, Spun off 682, Suspension 452,
Electrical 337, Transmission 319, Brakes 276, Clutch 216, Collision damage 204,
Hydraulics 162, Fuel system 156, Turbo 147, Overheating 136, Ignition 130, Oil
leak 127, Throttle 114, Out of fuel 101, Halfshaft 100.

Modern additions such as "Illegal skid block wear" (2025, ×4) and "Car
underweight" are the reason the Compliance bucket exists separately — they are
neither mechanical failures nor accidents.

## Power unit versus chassis attribution

Grouping by `engineManufacturerId`, which F1DB carries on **every result row**,
produces a PU-reliability view. It must be read with the constructor split
beside it, because the aggregate hides the interesting structure.

2026, rounds 1–14, F1DB v2026.14.0, excluding DNS/DNQ. By constructor:

| Constructor | Starts | Technical DNFs | Accident DNFs | Finish rate |
| --- | ---: | ---: | ---: | ---: |
| Alpine | 28 | 0 | 1 | 96.4% |
| Racing Bulls | 27 | 1 | 0 | 96.3% |
| Mercedes | 28 | 1 | 1 | 92.9% |
| Ferrari | 28 | 1 | 2 | 89.3% |
| Audi | 26 | 3 | 0 | 88.5% |
| McLaren | 25 | 3 | 0 | 88.0% |
| Haas | 28 | 3 | 1 | 85.7% |
| Red Bull | 28 | 3 | 2 | 82.1% |
| Williams | 27 | 2 | 3 | 81.5% |
| Cadillac | 28 | 11 | 0 | 60.7% |
| Aston Martin | 28 | 13 | 2 | **46.4%** |

By engine manufacturer:

| Engine | Starts | Non-accident DNFs | Rate |
| --- | ---: | ---: | ---: |
| Mercedes | 108 | 6 | **5.6%** |
| Red Bull Ford | 55 | 4 | 7.3% |
| Audi | 26 | 3 | 11.5% |
| Ferrari | 84 | 15 | 17.9% |
| Honda | 28 | 13 | **46.4%** |

**Two readings the aggregate would hide.** Ferrari's 17.9% is driven almost
entirely by Cadillac (11 technical DNFs in 28 starts) rather than by the works
team (1 in 28) — a customer-versus-works integration story, not a power-unit
story. And Honda's 46.4% is a single-team figure, because Aston Martin is
Honda's only 2026 customer: **"Honda PU reliability" and "Aston Martin
reliability" are not separable in 2026**, and the page says so rather than
labelling the number as one or the other.

2026 supplier groupings: Mercedes → Mercedes, McLaren, Williams, Alpine;
Ferrari → Ferrari, Haas, Cadillac; Red Bull Ford → Red Bull, Racing Bulls;
Audi → Audi only; Honda → Aston Martin only.

The 2026 cause mix skews mechanical in a way not seen since around 2010,
consistent with a first-year-of-new-regulations effect: Accident 8, Gearbox 7,
Engine 6, Hydraulics 6, Brakes 6, Electrical 5, Collision damage 4, Mechanical
3, Battery 3, Collision 3, Suspension 3, Overheating 2. The appearance of
**Battery** as a recurring cause is a direct artefact of the 350 kW electrical
side of the 2026 power unit — total output about 750 kW (400 kW ICE + 350 kW
electrical).

## Published failure and accident priors

For simulation and for expressing a season's reliability as a rate rather than
a count, TUMFTM's Monte Carlo parameter file carries per-team failure and
per-driver accident probabilities per race. 2019 examples: **team failure** —
Mercedes 0.041, Alfa Romeo 0.056, Racing Point 0.056, McLaren 0.117;
**driver accident** — Hamilton 0.045, Verstappen 0.058, Russell 0.072,
Grosjean 0.072. Pitwall's independently calibrated generic `dnf_prob` is 0.07
in [0.00, 0.15], which brackets the team-specific figures well.

## Reconciliation warning

Team-page DNF counters disagree across sources and must not be shown side by
side unreconciled. For 2026 Mercedes: formula1.com reports **3 DNFs** across 14
races; F1DB v2026.14.0 gives **28 starts with 2 DNF/NC rows** (1 technical, 1
accident) after excluding DNS. The gap is almost certainly a DNS or a
classified-but-not-finished car counted differently. The site publishes the
F1DB-derived figure with its denominator rules stated, and does not quote the
other number as corroboration.

Note also that F1DB can lag the live season by one round — for 2026 at round 14,
F1DB gave Mercedes 468 points against 503 from the live standings source.

## Related

- [Driver–car decomposition](driver-car-decomposition.md) — DNF inclusion or
  exclusion changes the published variance split materially, and is the single
  largest specification choice in that literature.
- [Clean-air race pace](clean-air-race-pace.md) — the pace half of the same
  team-performance picture.
- [Pit loss time](pit-loss-time.md)
