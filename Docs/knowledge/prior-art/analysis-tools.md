---
type: Reference
title: Analysis tools
description: The four analysis surfaces that set the substance bar — TracingInsights, Armchair Strategist, F1 Data Junkie and The Field — plus FastF1's sixteen-example gallery and why reproducing it is the field's strongest cliché.
tags:
  - prior-art
  - analysis
  - charts
  - fastf1
  - methodology
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: tracinginsights
    resource: https://tracinginsights.com/
    title: TracingInsights
  - id: tracinginsights_archive
    resource: https://github.com/TracingInsights-Archive
    title: TracingInsights-Archive — season telemetry CSV archives
  - id: tracinginsights_hf
    resource: https://huggingface.co/datasets/tracinginsights/RaceData
    title: tracinginsights/RaceData — Hugging Face dataset
  - id: armchair_repo
    resource: https://github.com/Casper-Guo/Armchair-Strategist
    title: Casper-Guo/Armchair-Strategist
  - id: armchair_viz
    resource: https://raw.githubusercontent.com/Casper-Guo/Armchair-Strategist/main/f1_visualization/visualization.py
    title: Armchair Strategist — visualization.py
  - id: armchair_pre
    resource: https://raw.githubusercontent.com/Casper-Guo/Armchair-Strategist/main/f1_visualization/preprocess.py
    title: Armchair Strategist — preprocess.py
  - id: ouseful_battlemaps
    resource: https://blog.ouseful.info/2015/01/31/rediscovering-formula-one-race-battlemaps/
    title: F1 Data Junkie — rediscovering Formula One race battlemaps
  - id: ouseful_concordance
    resource: https://blog.ouseful.info/2017/05/01/track-concordance-charts/
    title: F1 Data Junkie — track concordance charts
  - id: thefield_charts
    resource: https://www.thefieldf1.com/charts
    title: The Field — chart guide
  - id: thefield_sectors
    resource: https://www.thefieldf1.com/charts/sector-colours
    title: The Field — sector colours
  - id: fastf1_gallery
    resource: https://docs.fastf1.dev/examples/index.html
    title: FastF1 — examples gallery
status: stable
---

# Analysis tools

These are the projects that set the *substance* bar. None is a competitor on
design, permanence or 3D; all are ahead on breadth of analysis, and two publish
methodology precise enough to reimplement. The discipline this document
enforces: **borrow the method, never the look.**

## 1. TracingInsights — the breadth benchmark

The most feature-complete free F1 analysis site found. **30+ named analyses**,
free, funded through GitHub Sponsors, localised into English, French, Spanish,
Indonesian, Portuguese and Kannada. Charts are explicitly downloadable, editable
and shareable with no attribution required.

Named analyses observed: Lap Time Heatmap · Lap Chart · Stint Analysis · Sector
Analysis · Position Changes · Race Trace · Race Pace · lap-time delta · corner
analysis · downforce configurations · GG plots (lateral vs longitudinal
acceleration scatter) · ideal lap comparison · tyre degradation · tyre strategy ·
peak G forces · longitudinal/lateral acceleration · max throttle · top speed at
speed trap · overtakes · Drivers In Traffic · fan ratings · fastest lap analysis ·
pit stop data · penalty points · race launch performance ratings · Championship
Standings · Heat Map · Track Temperature.

### The one thing worth copying verbatim

Its published lap-alignment method, which is more careful than most:

> Split each lap into S1/S2/S3 using official sector times. Within each sector,
> scale compare-lap distance onto the reference (first selected) lap and
> interpolate time

with the honest caveat that **"Only sector endpoints are exact; shape within a
sector is estimated."** That caveat is the model for how this site states the
limits of a derived figure in situ.

### What it tells us not to do

Four themes named Default, Luxury, Dim and Synthwave. A site that ships four
looks has no point of view — the theme switcher *is* the tell. Content is gated
behind a mandatory year → event → session selection, so nothing is linkable or
browsable as a document: no circuit page, no team page, no prose. Charts populate
roughly 30 minutes after a session ends; before that the UI shows "no data
available", which is exactly the empty-state failure the honest-absence principle
exists to prevent.

It also publishes open data — season-by-season telemetry CSV archives on GitHub
and an Ergast-schema mirror on Hugging Face auto-updated within three hours.
Neither is used here; source roles are fixed in
[Source roles](../policies/source-roles.md).

## 2. Armchair Strategist — the method benchmark

Apache-2.0, **85 stars**, Dash + Plotly + FastF1, coverage from the 2018 season
(FastF1's telemetry boundary). Permissively licensed and readable, which makes it
the safest source to learn from in the whole field.

Named visualisations: Pit Stop Strategies · Position Changes · Point Finishers
Race Pace · Fuel-adjusted Lap Times · Podium Finishers Gap to Winner · Race Trace
to Winner Average Pace · Teammate Pace Comparisons (boxplot and violinplot) ·
Driver Pace Comparison · Team Pace Ranking · Tyre Degradation (lineplot and
distribution).

### Two constructions worth taking

**Fuel-adjusted lap time**, fully specified:

```python
FuelAdjLapTime = LapTime + 0.03 * (110.0 / final_lap_number * (LapNumber - 1))
```

Initial fuel 110 kg, 0.03 s/lap per kg; sprints use `110/3` kg, with `is_sprint`
detected when the median race length is under 30 laps. Our treatment, including
the honest 0.03–0.08 s/kg coefficient range and why the correction runs
unconditionally before any degradation fit, is in
[Fuel-corrected pace](../metrics/fuel-corrected-pace.md).

**Pit-loss-distributed gap.** `add_gap(driver, distribute_pit_loss=True)`
replaces a driver's `Time` series with
`mean_lap_time * (LapNumber - first_lap) + Time[0]`, then computes
`GapTo{DRIVER}Pace = (Time - {DRIVER}Time).dt.total_seconds()`. Without the flag
the same function yields the raw `GapTo{DRIVER}` with pit-stop steps intact.
**Both variants are worth offering:** the raw gap shows the race that happened,
the distributed one shows the underlying pace. See
[Race trace](../metrics/race-trace.md) and
[Gap to leader](../metrics/gap-to-leader.md).

### Track-status decoding

```python
def _lap_filter_sc(row):   # 4 = safety car
    return "4" in row.loc["TrackStatus"] and row.loc["Position"] == 1

def _lap_filter_vsc(row):  # 6 = VSC deployed, 7 = VSC ending
    return (("6" in row.loc["TrackStatus"]) or ("7" in row.loc["TrackStatus"])) \
           and ("4" not in row.loc["TrackStatus"] and row.loc["Position"] == 1)
```

Filtering on `Position == 1` makes the *leader's* lap define the neutralisation
window, which is the correct reference on a lap-indexed x-axis; shading runs from
`firstLap - 1` to `lastLap`, `alpha=0.5, color="orange"`, with `hatch="xx"`
distinguishing VSC from SC.

### Small multiples as the escape from twenty colours

`driver_stats_scatterplot` facets one panel per driver on shared axes — **five
facets wide for a field view, four for teammate comparison** so teammates sit
side by side in a row. Inside each facet, colour carries compound, marker shape
carries tyre freshness, and the facet itself carries driver identity; only one
facet draws a legend; facet titles are set in the driver's colour. Outlier
control keeps laps with `PctFromFastest < 10`. This is the canonical answer for
per-lap scatter data and is adopted in
[Driver colour encoding](../design/driver-color-encoding.md).

### Its class limitation

Dash/Plotly default chrome, server-side Python rendering, modal-heavy selection,
zero prose, no circuit or team pages. Every peer in this class — F1Dash
(FraserTarbet), f1-viz (jessbuildsthings), f1stuff/f1-live-data,
PiotrMajor/F1-Data-Visualization — shares one constraint: **they need a live
Python server.** A precomputed static site is therefore a structural
differentiator, not a stylistic one.

## 3. F1 Data Junkie — the richest idioms, the poorest execution

Tony Hirst's blog is intellectually the strongest prior art in the space and
visually the weakest: raw ggplot2 output, static PNGs, sporadically updated. Two
of its idioms are precisely specified and, as far as the survey found, have never
been built for the web.

### Battle map

| Element | Specification |
| --- | --- |
| x | Lap number |
| y | Time delta in **milliseconds** to the selected driver; `y > 0` = cars ahead, `y < 0` = cars behind |
| Marks | **Rotated three-letter driver codes**, not points — the marks *are* the identities |
| Black | The car one place ahead or behind in race position |
| Aqua | A car on a different lap sitting ahead on track between them |
| Orange | A lapped car similarly interposed |
| Reference | **Dashed horizontal rule at ±1000 ms** |

The R implementation is `battlemap_core_chart()`, built on `geom_text()` with
`aes_string()`, `geom_hline()` for the threshold and `scale_color_discrete()` for
an Ahead/Behind legend. The author's stated purpose: the battle maps
"can help search for stories amidst the runners."

The ±1 s rule is the element that makes the idiom legible at a glance, and it
keeps its meaning across the 2026 regulation change — it now marks the Overtake
Mode threshold rather than the DRS one, read at a discrete detection point rather
than as a rolling eligibility band. The distinction it encodes — **track position
versus race position** — is the thing every other chart erases.

### Race concordance chart

y = lap number; x = accumulated lap-time delta relative to the focus driver, so
each row is a horizontal slice of the traffic around that car. Colour encodes
**lap offset, not identity**: light blue = same lap; blue→green = cars ahead on a
subsequent lap (blue-flag situations); orange→red = backmarkers progressively
further behind. Horizontal rules mark the focus driver's pit laps; vertical bars
mark pit windows.

The underlying computation is a self-join on accumulated time:

```sql
SELECT l1.code, l1.acctime - l2.acctime AS acctimedelta,
       l2.lap - l1.lap AS lapdelta, l2.lap AS focuslap
FROM lapTimes AS l1 JOIN lapTimes AS l2
WHERE l1.acctime < l2.acctime + W AND l1.acctime > l2.acctime - W
```

`W` of 20–30 s captures the meaningful traffic. Accumulated time is one cumulative
sum and the windowed join is O(n·k), so the whole thing precomputes at build time
into per-driver JSON and the page does no work at runtime.

Hirst also wrote *Wrangling F1 Data With R* and *Wrangling F1 Data With Python*.

## 4. The Field — the published taxonomy

`thefieldf1.com/charts` documents roughly **30 archetypes grouped by session
type, each with axes and encodings stated**. It is directly usable as a build
checklist, and it is the closest thing the field has to a specification.

| Session | Archetypes |
| --- | --- |
| Race | Lap Time Chart (pit-out laps marked distinctly) · Lap Consistency (box plots, SC and pit-out excluded) · Position Chart · Gap to Leader · Tire Strategy Timeline · Pit Strategy Table · Tire Degradation · Sector Time Distribution by Compound |
| Qualifying | Qualifying Lap Times (inter-phase gaps compressed) · Qualifying Gap Chart (pole at zero, bar colour = compound) · Qualifying Position Chart (lines drop at elimination cut-lines) · Mini-Sector Heatmap · Track Sector Map · Sector Time Comparison |
| Practice | Practice Pace Chart · Session Timeline · Long Run Chart (stints of 5+ consecutive laps only) |
| Team | Team Lap Time Distribution · Theoretical Best Team Lap · Speed Fingerprint (ridge-line speed density, split at 220 km/h into corner and straight zones) · Speed Trap Ratios (I1 vs I2 ratio scatter with dashed field-average lines) · Speed Trap Evolution |
| Season | Championship Points Progression |

**Documented verbatim, and adopted:**

- Gap to Leader — "The vertical scale uses square-root compression so small gaps
  between frontrunners remain readable even when a lapped car is a minute
  behind", and "Lapped drivers are annotated with a +1L or +2L label when the
  timing gap becomes a lapped interval."
- Position Chart — "Each coloured line represents one driver in their
  constructor's team colour."
- Delta panel reading — "Rising sections show reference driver slower; falling
  shows faster."
- Sector colours — purple = fastest in session, green = personal best, yellow =
  slower than own best, white = no reference yet, grey = pit-lane passage, with
  the caveat that **"A screen full of green doesn't indicate competitive pace; it
  typically shows drivers improving as track conditions evolve."**

*Not* documented, despite being a reasonable assumption: the colour encoding of
the Gap to Leader lines. The constructor-colour statement applies to the Position
Chart only.

**Two licensing facts it carries that matter here.** Its footer states "Race data
provided by OpenF1 under the CC BY 4.0 licence", and its data guide says charts
are built from OpenF1 post-session data for seasons up to 2025 and from F1's
official live timing archive for 2026 onwards. Our own register records OpenF1
differently and confines it to build-time use — see
[Data licensing](../policies/data-licensing.md) and
[Source roles](../policies/source-roles.md), which govern here. The second half
is the useful operational warning: **a 2026-capable build cannot assume one
source spans current and historical seasons.**

It also flags that DRS was abolished from 2026, making the DRS band chart a
historical-seasons-only archetype — conditioned on season, never rendered empty.

## 5. FastF1's sixteen-example gallery — the look to avoid

FastF1's documentation ships **exactly 16 examples**, and they are the single
strongest "seen it before" signal available. TracingInsights, Armchair
Strategist, countless Medium posts and Kaggle notebooks reproduce them
near-identically. Producing any of them in default matplotlib styling marks the
site as one more notebook export.

| Group | Examples |
| --- | --- |
| Plot styling | Driver specific plot styling · Draw a track map with numbered corners |
| Lap time analysis | Driver Laptimes Scatterplot · Driver Laptimes Distribution Visualization |
| Strategy and results | Position changes during a race · Team Pace Comparison · Tyre strategies during a race · Qualifying results overview |
| Standings | Who can still win the drivers WDC? · Plot driver standings in a heatmap · Season Summary Visualization |
| Telemetry | Overlaying speed traces of two laps · Gear shifts on track · Plot speed traces with corner annotations · Speed visualization on track map · Grid Average Speed Trace: 2025 vs 2026 |

The gallery also surfaces a `Using the Fast-F1 signalr client?` entry; the
verified figure is **16 examples**, at `/examples/index.html` —
`/examples_gallery/index.html` returns HTTP 404.

**Version note:** the live documentation site serves **3.6.1**, while the current
PyPI release is **3.8.3**. The docs build lags the package, so behaviour read
from docs.fastf1.dev is not necessarily the behaviour of the installed library.
See [FastF1](../datasets/fastf1.md).

### Two structural ideas worth keeping

1. **"Draw a track map with numbered corners"** — corner numbering from
   `circuit_info`, with labels placed by rotating a fixed offset vector by each
   corner's `Angle` and drawing a leader line back to the track point.
2. **"Plot speed traces with corner annotations"** — a distance-domain trace with
   corner marks as vertical rules, so a reader can locate a loss at a named
   corner.

Both are structure. Neither requires the matplotlib look.

### One API to design away from

`fastf1.utils.delta_time(reference_lap, compare_lap)` is deprecated since 3.0.0,
its own documentation calls the approach "not actually very accurate" with
"notable differences" against sector-time calculations, and it **has already been
removed on master** — `fastf1/utils.py` there is a 104-line shim containing only
`recursive_dict_get`, `to_timedelta` and `to_datetime`, all newly marked
deprecated as of 3.9.0. The distance-resampled replacement,
`delta(r) = telAt(compare, r) - telAt(reference, r)` on a common normalised
distance axis, is not merely more accurate — it is the only option that survives
the next release. Specified in
[Chart archetypes](../design/chart-archetypes.md).

## 6. What the whole class lacks

| Property | TracingInsights | Armchair | F1 Data Junkie | The Field | FastF1 gallery |
| --- | :-: | :-: | :-: | :-: | :-: |
| Static, permanent URLs | — | — | partial (blog posts) | — | — (docs pages) |
| Page per circuit / team / race | — | — | — | — | — |
| 3D | — | — | — | — | — |
| Authored design system | — | — | — | — | — |
| Prose | — | — | yes | partial | — |
| Pre-2018 coverage | — | — | yes | — | — |

The last row is the one that matters. Every tool in this class begins at 2018 or
2023 because that is where telemetry begins. The archival tier is the part of the
sport none of them touch.

## Related

- [Chart archetypes](../design/chart-archetypes.md)
- [Fuel-corrected pace](../metrics/fuel-corrected-pace.md) · [Race trace](../metrics/race-trace.md) · [Gap to leader](../metrics/gap-to-leader.md) · [Tyre degradation rate](../metrics/tyre-degradation-rate.md)
- [minisector](minisector.md) — the same archetypes, implemented in static SVG
- [Reference materials](reference-materials.md)
- [FastF1](../datasets/fastf1.md) · [OpenF1](../datasets/openf1.md)
