---
type: Metric
title: Gap to leader
description: Each driver's cumulative time behind whoever leads on that lap, plotted on a square-root-compressed axis so the front of the field stays readable, with lapped cars annotated rather than plotted at a false gap.
resource: /methods/gap-to-leader/
tags: [visualisation, gap-to-leader, cumulative-time, axis-scale, lapped-cars, metric]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: multiviewer_race_trace
    resource: https://multiviewer.app/docs/usage/race-trace
    title: MultiViewer — Gap to Leader as a named trace mode
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core API — LapTime, LapNumber, Position, TrackStatus
  - id: f1db_release
    resource: https://github.com/f1db/f1db/releases/download/v2026.14.0/f1db-csv.zip
    title: F1DB v2026.14.0 — race results with gapLaps and intervalMillis
  - id: jolpica_ergast_differences
    resource: https://raw.githubusercontent.com/jolpica/jolpica-f1/main/docs/ergast_differences.md
    title: jolpica-f1 — documented divergences from Ergast, including status collapse
status: stable
---

# Gap to leader

The cumulative time each driver is behind whoever is leading on that lap:

```
D_d(L) = T_d(L) − min_d' T_d'(L)
```

where `T_d(L)` is cumulative race time as defined in
[Race trace](race-trace.md). The reference is not a fixed driver — it is the
minimum across the field on each lap, so it **switches whenever the lead
changes**, and the leader's line sits flat at zero by construction.

That switching is the chart's value and its difficulty. It shows the real
running order, but it also means a lead change appears as a discontinuity in
everyone else's line, and it means the axis has to span the leader (0 s) and
the last classified car (possibly two laps, i.e. 150+ s, down) simultaneously.

## The axis problem

On a linear axis sized to the tail of the field, the entire battle for the lead
occupies the top two percent of the plot. A 0.4 s gap and a 2.1 s gap — the
difference between a car being in DRS range and being out of reach — become
indistinguishable.

**This site uses a square-root-compressed y-axis.**

```
y(gap) = height × √(gap / gap_max)
```

Square root, not logarithmic, for three reasons:

1. **It is defined at zero.** The leader's line is a real point at `y = 0`, not
   an asymptote. A log axis needs an offset hack for the one value the chart
   most needs to show honestly.
2. **It compresses gently.** At `gap_max = 100 s`, a 1 s gap sits at 10% of the
   height and a 4 s gap at 20% — the front of the field gets an order of
   magnitude more room than linear, without the extreme distortion that makes a
   log axis unreadable to a non-technical audience.
3. **It is monotone and order-preserving.** Nothing about the running order is
   altered, only the spacing.

The cost is that **the axis is non-linear and must be declared**. Ticks are
placed at values a reader recognises — 0, 1, 2, 5, 10, 20, 50 s — not at even
pixel intervals, and the caption says the scale is compressed. An unlabelled
non-linear axis is a lie of omission, and it is exactly the kind of thing this
site's provenance principle exists to prevent.

Under `prefers-reduced-motion`, and in the `<table>` fallback, the underlying
values are the real seconds, uncompressed.

## Lapped cars

Once a driver is a lap down, their gap-to-leader in seconds is no longer a
racing gap. It is a lap time plus a racing gap, and plotting it as a single
number silently claims a comparison that does not exist: a car 74 s behind the
leader on the same lap and a car 74 s behind having been lapped are in
completely different races.

**Rule: a lapped car is annotated, not plotted at its raw time gap.**

```
if laps_completed(d, L) < laps_completed(leader, L):
    annotate the line at that lap with "+1L", "+2L", …
    and clamp or break the line rather than extending it into the tail
```

The annotation is rendered as a small monospace label at the point the driver
is first lapped, and the line's treatment changes — lighter weight, or a break
— so the reader can see the status change. This is the same discipline as the
`+N Laps` convention in classification tables, applied to a chart.

### Deriving lap-down status

| Source | Field | Coverage | Caveat |
| --- | --- | --- | --- |
| FastF1 | `LapNumber` per driver per lap | 2018+ reliably, 1996+ partially | Compare max completed lap against the leader's |
| F1DB `f1db-races-race-results.csv` | `gapLaps`, `positionText` | 1950–2026 | Canonical for the final classification |
| jolpica / Ergast schema | `status` | **1950–2023 only** for lap-down margin | See below |

**The jolpica trap.** From **2024** onward, the Ergast-schema status field
collapses the granular `+1 Lap` … `+N Laps` statuses into a single
**`Lapped` (statusId 143)**, and `Did not start` into statusId 142. The
documentation says the change applies "from the 2025 season"; the data shows
2024 is already collapsed (2024 returns exactly five distinct statuses:
Finished 287, Lapped 138, Retired 49, Did not start 3, Disqualified 2).

**Therefore lap-down margin for 2024–2026 must come from F1DB**, not from
jolpica. The same constraint governs retirement causes — see
[Reliability and DNF rate](reliability-dnf.md).

## Cautions and the compression artefact

Under a safety car the whole field runs at roughly **160%** of normal lap time,
and under VSC roughly **140%**. Because the leader slows too, gaps in *seconds*
collapse toward zero — a three-second lead becomes a car-length behind the
safety car train.

This is a real racing consequence and the chart should show it, but it must not
be mistaken for someone catching up. Caution laps are **shaded** from
`TrackStatus` (`'4'` SC, `'5'` red, `'6'` VSC deployed, `'7'` VSC ending), so
the collapse reads as a track condition rather than as pace.

The same applies to the leader pitting: the gap-to-leader reference jumps by
the full pit loss — 14.09 s to 24.59 s depending on circuit, per
[Pit loss time](pit-loss-time.md) — and every other line jumps with it. This is
the single most confusing feature of the chart for a new reader, and the
strongest argument for offering [Race trace](race-trace.md)'s fixed-reference
constructions alongside it.

## Construction

```python
laps = session.laps[["Driver", "LapNumber", "LapTime"]].dropna()
laps["T"] = laps.groupby("Driver")["LapTime"].cumsum().dt.total_seconds()
leader   = laps.groupby("LapNumber")["T"].transform("min")
laps["gap"] = laps["T"] - leader
```

Lap 1 must be present. If the source omits it, reconstruct it as
`(total race time) − Σ(all other lap times)` before the cumulative sum — see
[Race trace](race-trace.md).

## Coverage

**Timing tier and above (1996+).** Archival-era races have no lap-by-lap times
and therefore no gap-to-leader chart; those pages carry the final
classification with its `gapMillis` / `gapLaps` and say plainly that a
lap-by-lap gap does not exist for that race.

## Design

- Leader's line flat at zero, drawn at the same weight as everyone else. The
  leader is identified by position, not by emphasis.
- Direct end-of-line labelling; no colour-only legend.
- Teammates solid vs dashed (`stroke-dasharray: "6 3"`).
- `+1L` annotations in JetBrains Mono at small size, with
  `--f1-numeric: tabular-nums lining-nums`.
- Tick labels at recognisable second values, never at even pixel spacing.
- A caption stating the compression, e.g. "y-axis square-root compressed;
  gridlines at 0, 1, 2, 5, 10, 20, 50 s".
- A real `<table>` fallback carrying uncompressed seconds and lap-down status.

## Related

- [Race trace](race-trace.md) — the fixed-reference siblings of this chart.
- [Pit loss time](pit-loss-time.md) — the size of the jump when the leader pits.
- [Overtake detection](overtake-detection.md) — lapping and unlapping are the
  same events this chart annotates, and the same false positives an overtake
  counter must reject.
- [Position at corner](position-at-corner.md) — where sub-lap order comes from.
