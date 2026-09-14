---
type: Reference
title: Chart archetypes
description: Every chart the site builds, with its exact encoding, axis treatment, construction formula and the coverage tier that unlocks it.
tags:
  - design
  - dataviz
  - charts
  - encodings
  - coverage-tiers
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: minisector_views_c
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/views_c.js
    title: lennyocbot/minisector — race trace and position chart
  - id: minisector_views_d
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/views_d.js
    title: lennyocbot/minisector — mini-sector dominance and telemetry panels
  - id: minisector_views_b
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/views_b.js
    title: lennyocbot/minisector — stint fitting
  - id: minisector_charts
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/charts.js
    title: lennyocbot/minisector — charts.js SVG kernel
  - id: fastf1_strategy
    resource: https://docs.fastf1.dev/gen_modules/examples_gallery/plot_strategy.html
    title: FastF1 — tyre strategy example
  - id: fastf1_corners
    resource: https://docs.fastf1.dev/gen_modules/examples_gallery/plot_annotate_corners.html
    title: FastF1 — annotate corners example
  - id: fastf1_api
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/_api.py
    title: FastF1 — track status code table
  - id: armchair_viz
    resource: https://raw.githubusercontent.com/Casper-Guo/Armchair-Strategist/main/f1_visualization/visualization.py
    title: Armchair Strategist — visualization.py
  - id: ft_visual_vocabulary
    resource: https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary
    title: FT Chart Doctor — Visual Vocabulary
  - id: ouseful_battlemaps
    resource: https://blog.ouseful.info/2015/01/31/rediscovering-formula-one-race-battlemaps/
    title: F1 Data Junkie — race battle maps
status: stable
---

# Chart archetypes

The set of useful motorsport chart types is small, stable and well-established.
That is what makes an in-house SVG kernel the right call rather than a charting
library: the archetypes are few, they are not going to change, and the
aesthetic bar cannot be met by overriding a library's tick density, label
placement and tooltip chrome. The nearest prior art's whole kernel is **225
lines**, and its entire `src/` is **3,726 lines** across ten files.

D3's scales and shape generators may be used as utilities, where their value is
highest and their visual footprint is zero.

## 1. The catalogue

Tier is the coverage tier from the project specification: **Archival**
(1950–1995), **Timing** (1996–2017, adds lap times and positions),
**Telemetry** (2018–2022), **Modern** (2023–2026). Tier is a first-class field
on every race record and it selects the template — an archival page does not
render an empty speed trace, it renders a different page.

| Chart | X | Y | Mark | Colour | Second channel | Tier |
| --- | --- | --- | --- | --- | --- | --- |
| Position (lap) chart | Lap | Position, inverted | Line | Team | Dash + end label | Timing |
| Race trace | Lap | Δ vs constant reference pace, s | Line | Team | Dash + end label | Timing |
| Gap to leader | Lap | Gap, s, **sqrt-compressed** | Line | Team | Dash + end label | Timing |
| Stint Gantt | Lap | Driver, ordered by finish | Stacked barh | Compound | Letter on block + hatch | Timing |
| Pit-stop table | — | — | Table | — | — | Timing |
| Tyre-degradation scatter | Tyre life | Fuel-corrected lap time | Points + fit | Compound | Marker shape | Timing |
| Lap-time scatter | Lap | Lap time | Points | Compound | Marker = fresh/used | Timing |
| Lap consistency | Driver | Lap time | Box | Team | Position on axis | Timing |
| Mini-sector dominance | Track distance | — | 27 segments + track path | Team of fastest | Corner ticks + table | Telemetry |
| Speed trace + delta | Distance, m | Speed km/h; Δ s | Line; line | Team | Dash | Telemetry |
| Throttle / brake / gear / RPM | Distance, m | Channel range | Line; **step** for brake and gear | Team | Dash | Telemetry |
| DRS / Overtake activation | Distance, m | One row per driver | Activation bars | Team | Row position | Telemetry (≤2025 for DRS) |
| Mini-sector heatmap | Mini-sector | Driver | Cell | Purple/green/yellow/white | Cell text | Telemetry |
| Small multiples | Lap | Lap time | Points | Compound | Facet = driver | Timing |
| Qualifying gap ladder | Δ to pole, s | Driver | Bar | Compound | Cut-lines | Timing |
| Battle map | Lap | Δ ms to neighbours | Rotated driver codes | Lap-offset class | Text is the mark | Timing |
| Race concordance | Accumulated Δ, s | Lap | Marker + code | Lap offset | Marker shape | Timing |
| Championship swing | Round | Cumulative points | Line | Constructor | End label | **Archival** |
| Constructor lineage | Year | Lineage row | Timeline bars | Constructor | Event markers | **Archival** |
| Entry-list table | — | — | Table | — | — | **Archival** |
| Reliability / DNF history | Season | DNF rate | Line or bar | Constructor | End label | **Archival** |

The archival tier is not a subset of the modern one. Championship swing, entry
lists, constructor lineage and reliability history are *additional* design work
that exists so that a 1962 page is a designed page rather than a modern
template with eleven empty panels.

## 2. Axis treatment — one house style

Applied to every chart above.

| Property | Value |
| --- | --- |
| Axis and gridline stroke | 1px hairline at `--f1-rule` (8% ink alpha) |
| Plot frame | None. Despine top and right; left and bottom only where they carry a scale |
| Tick ladder | `[1, 2, 2.5, 5, 10] × 10^floor(log10(step))` |
| Default tick counts | 6 on y, 8 on x |
| Default margins | `mt 12 / mr 14 / mb 40 / ml 58` (`mb 26` with no x label) |
| Margin when end-labelled | `mr 46` |
| Tick and label type | 13px JetBrains Mono, `tabular-nums lining-nums` |
| Aspect | `preserveAspectRatio="xMidYMid meet"` on any geographic or track figure |
| Accessibility | `role="img"` with a real `label`; table fallback in the DOM |

A stretched circuit outline is an instant credibility failure, which is why the
aspect rule is absolute on track figures.

### The kernel's surface

The in-house kernel exposes, at minimum: `svgEl(tag, attrs, parent)`,
`niceTicks(lo, hi, n)`, a `Chart(container, opts)` factory taking
`{w, h, mt, mr, mb, ml, xd, yd, yflip, xticksArr, yticksArr, xlab, ylab, xfmt,
yfmt, label}` and returning `{svg, x, y, plot, ml, mt, iw, ih, xd}`, plus
`linePath`, `stepPath`, `spreadLabels(items, gap, lo, hi)`, `heatBg(v, vmax)`,
`tip`/`tipShow`/`tipHide`, `hoverMarks(nodes, html)`, `legend(container, items)`
and `dragZoom(ch, cb, onTap)`.

Pixel → domain mapping for any interaction:

```js
const value = ch.xd[0] + (px - ml) / iw * (ch.xd[1] - ch.xd[0]);
```

## 3. Shared preconditions

### The clean-lap predicate

Every pace chart, every degradation fit and every race-trace reference is built
on the same predicate. Implement once:

> timed **and** not an in-lap **and** not an out-lap **and** not deleted **and**
> fully green track status **and** flagged accurate by the source.

### Track status

`TrackStatus` is a string of concatenated digit codes covering the lap.

| Code | Meaning |
| --- | --- |
| `1` | Track clear — also what **closes** a neutralisation window |
| `2` | Yellow flag (sectors unknown) |
| `3` | Documented upstream as *"??? Never seen so far, does not exist?"* — handle as unknown, do not assume absent |
| `4` | Safety Car |
| `5` | Red flag |
| `6` | VSC deployed |
| `7` | VSC ending |

```js
function tsFlags(ts) {
  const s = String(ts || '1');
  return { yellow: s.includes('2'), sc: s.includes('4'), red: s.includes('5'),
           vsc: s.includes('6') || s.includes('7'), green: !/[24567]/.test(s) };
}
```

Neutralisation bands are taken from **the leader's lap** (`Position == 1`),
which is the correct reference on a lap-indexed x-axis, and extended from
`firstLap − 1` to `lastLap` — if the SC is out on laps 14, 15 and 16, the band
runs from 13 to 16. SC bands are a warm neutral fill; VSC is distinguished by a
hatch rather than by hue alone; red-flag suspensions are shaded separately.

## 4. The lap-indexed race charts

Three distinct things get called "a race trace". State which one is on screen.

| Name | Definition |
| --- | --- |
| **Gap to leader** | `y = elapsed_driver(lap) − elapsed_leader(lap)` |
| **Race trace** (default) | `y = refPace × lap − elapsed_driver(lap)` |
| **Delta to a chosen driver** | That driver's line flat at zero |

### Race trace

```js
for (let lap = 1; lap <= total; lap++) {
  const e = endOf[d.abbr].get(lap);              // cumulative session time, end of lap
  pts.push(e == null ? null : [lap, (refAvg * lap - (e - raceStart)) / 1000]);
}
```

`refAvg` is the **winner's clean-lap median**, falling back to
`(winnerEnd − raceStart) / winnerLaps` when fewer than five clean laps exist.
Positive is ahead of reference pace; flat is exactly reference pace; a vertical
drop is a pit stop or a neutralisation. The caption states this in words:
*"vs a constant {lap} lap · flat = that pace, drops = pits/SC"*.

Y-domain clipping, because a long safety car squashes the racing into a sliver:

```js
const deepLo = quantile(ys, 0.01) - 4;
const yLo    = Math.max(deepLo, quantile(ys, 0.30) - 90);
// visible footnote when deepLo < yLo - 20
```

The pit-loss-distributed variant replaces each driver's cumulative time with
`meanLapTime × (lap − firstLap) + time[0]` before differencing, which removes
the pit steps and shows underlying pace. **Offer both**: the raw version shows
the race that happened, the distributed version shows the pace that produced
it.

Reliability guard: if the winner's clean laps have `q90 − q10 > 5000 ms`, or
the winner's total exceeds `refAvg × laps` by more than 420 s, the race is
"drifted" and the chart carries the note *"read vertical gaps, not slopes"*.

Pit stops are marked as **open donut circles** (`r 3.6`, fill the surface
colour, stroke the team colour at 2px) so they read as events rather than as
data points.

### Gap to leader

`d3.scaleSqrt().domain([0, maxGap]).range([0, innerHeight])`.

Square root rather than log, for two reasons: gap = 0 is a legitimate and
common value and breaks a log scale; and sqrt preserves ordering and the sign
of change while still giving roughly three times more pixel space per second
near zero than at 60 s. In a modern Grand Prix the raw range spans about 0–90 s
and is unbounded once cars are lapped, so a linear scale destroys the 0.2–2.0 s
battles that carry the whole story.

Ticks are placed **explicitly** — 0, 1, 2, 5, 10, 20, 40, 80 — because
automatic ticks on a sqrt scale are awkward. Lapped cars are annotated `+1L` /
`+2L` rather than plotted at their true gap. A dashed hairline sits at ±1 s.

A note on that hairline across the regulation change: from 2026, DRS no longer
exists and Overtake Mode takes its place, but the ±1 s threshold keeps its
meaning, so the reference line is valid on both sides of 2026. It is gated at a
**discrete detection point**, nominally the final corner — so the line is a
reference mark, not a continuous eligibility band, and must not be drawn as a
shaded region.

### Position chart

Y inverted (`ylim [20.5, 0.5]`), ticks at 1, 5, 10, 15, 20. Lines **truncate**
at retirement — never interpolate across a missing lap, never extend a line to
the end of the race for a car that stopped on lap 9.

## 5. Stint and tyre charts

### Stint Gantt

```python
stints = laps[["Driver", "Stint", "Compound", "LapNumber"]]
stints = (stints.groupby(["Driver", "Stint", "Compound"])
                .count().reset_index()
                .rename(columns={"LapNumber": "StintLength"}))

for driver in drivers:
    previous_stint_end = 0
    for _, row in stints.loc[stints["Driver"] == driver].iterrows():
        plt.barh(y=driver, width=row["StintLength"], left=previous_stint_end,
                 color=compound_color(row["Compound"]), edgecolor="black")
        previous_stint_end += row["StintLength"]
ax.invert_yaxis()
```

Rows ordered by finishing position, top to bottom. Every block carries its
compound **letter**; used (non-fresh) sets carry a `///` hatch. Hover payload:
compound, tyre age at stint start, laps completed, pit-lane stationary time.
The near-white HARD colour needs the explicit edge stroke on paper.

### Tyre degradation

```js
function stintFit(st, sid) {
  const pts0 = st.laps
    .filter(l => isClean(l) && l.life != null)
    .filter(l => l.lap > st.from)              // drop the first lap of the stint
    .map(l => [l.life, fuelCorrWith(l, sid)]); // x = tyre life, y = fuel-corrected ms
  if (pts0.length < 4) return null;            // 4+ clean laps; consecutiveness not required
  let fit = linfit(pts0);
  const pts = pts0.filter(([x, y]) => Math.abs(y - (fit.a + fit.b * x)) < 1200);
  if (pts.length >= 4) fit = linfit(pts) || fit;   // refit without ±1.2 s outliers
  return fit;
}
```

**Fuel correction is applied unconditionally before the fit, never after and
never skipped.** Fuel burn produces a roughly linear downward trend against lap
number that is collinear with tyre age inside a stint; it does not cancel out
of a slope fitted against tyre life, it biases that slope toward zero. The
chart's own caption must not claim otherwise. Full definition and the two
published fuel models live in [`/metrics/`](../metrics/index.md).

The headline number is the slope in s/lap. A field-wide 2026 magnitude of
roughly 0.063–0.071 s/lap by compound is a reasonable axis default and a
sanity check on outputs. The fuel coefficient is exposed as a user-facing
control because the honest published range is wide.

Chart copy states the assumptions in situ: *"per-stint baseline removed · first
lap of stint dropped · traffic/SC laps excluded · fuel-corrected at {k} s/lap"*.

## 6. Telemetry charts

### Mini-sector dominance

Two methods exist and only one is correct. The common approach bins telemetry
by distance, takes **mean speed** per bin and picks the maximum — which is
wrong wherever a driver carries speed into a segment they entered slower. The
correct method compares **elapsed time through the segment**:

```js
const NSEG = 27;
for (let k = 0; k < NSEG; k++) {
  const r0 = k / NSEG, r1 = (k + 1) / NSEG;
  let wi = 0, wt = Infinity;
  ents.forEach((en, i) => {
    const dt = telAt(en.tel.t, r1) - telAt(en.tel.t, r0);   // elapsed time through segment
    if (dt < wt) { wt = dt; wi = i; }
  });
  domWinner.push(wi);
}
```

`telAt(t, r)` interpolates cumulative lap time at track-distance fraction `r`.
**This is the same function that drives the Δ-time panel**, which gives a
coherence property worth designing for deliberately: the dominance strip and
the delta curve can never contradict each other, and the per-segment deltas
must sum to the lap-time difference. Make that an automated test.

Outputs are three coordinated views: a linear dominance strip of 27 rounded
rects (`rx 3`, ~1.2px gap) with corner ticks and numbers beneath; the circuit
outline recoloured by the same winner array; and a table of mini-sectors won
and share per lap.

Two honesty notes that must appear in the UI: equal-length mini-sectors
**approximate but do not equal** F1's official mini-sectors; and a fixed
segment count means very different segment lengths at Spa (7.0 km) versus
Monaco (3.3 km). Whether to hold N fixed at 27 or hold segment length fixed at
about 250 m — giving roughly 13–28 segments — is an open decision.

### Telemetry panels

Fixed panel order. The conclusion first, then the causes in the order a driver
experiences them:

```js
const PANELS = [
  ['delta', 'Δ time'], ['v', 'Speed'], ['th', 'Throttle'], ['b', 'Brake'],
  ['g', 'Gear'],       ['n', 'RPM'],   ['d', 'DRS/OT'],
];
```

| Panel | Path type | Y range |
| --- | --- | --- |
| Δ time | line, zero hairline | auto |
| Speed | line | 0–380 km/h |
| Throttle | line | 0–100% |
| **Brake** | **step** | 0–100% |
| **Gear** | **step** | 1–8 |
| RPM | line | 0–15,000 |
| DRS / Overtake | **per-driver horizontal activation bars** (row height 15) against a grey baseline | one row per entrant |

Brake and gear are step paths because they are discrete states; a smoothed line
through a gear change is a drawing of something that did not happen. The
DRS/Overtake panel is an activation strip, **not** a step chart.

All panels share one distance axis. Tap pins a readout; drag zooms every panel
at once; double-tap resets; tapping the track map jumps all traces to that
distance fraction.

The panel is rendered conditionally on the channel existing (`if (S.telPanels.d
&& hasDrs)`), so it simply disappears for a session with no DRS channel rather
than rendering an empty axis. **That conditional pattern is the site's general
answer to honest absence** and is reused everywhere, not only here.

### Delta computation

Do **not** use `fastf1.utils.delta_time`. It has been deprecated since 3.0.0,
its own documentation says the approach is *"not actually very accurate"* with
notable differences against sector-time calculations, and it has already been
deleted from the library's master branch. Compute instead:

```
delta(r) = telAt(compare, r) − telAt(reference, r)
```

on a common normalised-distance axis. Axis label follows the documented
convention `<-- LEC ahead | HAM ahead -->`. Rising means the reference driver
is losing time; falling means gaining. **The terminal delta must equal the
actual lap-time difference** — that is the test.

### Corner annotation

Corners arrive as `Number`, `Letter`, `X`, `Y`, `Distance`, `Angle`, with a
circuit `rotation` in degrees.

```python
def rotate(xy, *, angle):
    rot = np.array([[ np.cos(angle), np.sin(angle)],
                    [-np.sin(angle), np.cos(angle)]])
    return np.matmul(xy, rot)

offset_vector = [500, 0]                      # ≈ 50 m; source X/Y are ~decimetres
offset_x, offset_y = rotate(offset_vector, angle=corner['Angle'] / 180 * np.pi)
text_x, text_y = rotate([corner['X'] + offset_x, corner['Y'] + offset_y], angle=track_angle)
```

Scale the 500-unit offset relative to the track bounding box rather than
hard-coding it, for responsive SVG. On a trace, corners are dotted grey
vertical lines at `corners['Distance']` with `f"{Number}{Letter}"` labels below
the axis and y limits `[v_min − 40, v_max + 20]`.

### Track ribbon rendering

Draw a thick dark backing stroke (16 units) first, then the coloured segment
collection (5 units) on top. Without the backing stroke, discrete segment
colours read as a chain of blobs rather than one ribbon. Nearest-point picking:
square-distance scan over the sampled path, reject taps further than
`bboxWidth / 7` from the line, return the distance fraction so every trace
scrubs in sync.

## 7. Sector timing colours

F1 has a universal four-colour convention. Reuse it verbatim rather than
inventing one.

| Colour | Meaning |
| --- | --- |
| Purple | Fastest in the session, outright |
| Green | Personal best for that driver this session |
| Yellow | Slower than that driver's own session best |
| White | No comparable timed reference set yet |

*"Green is personal, purple is universal."* The hex values are not published by
the governing bodies; we choose our own and they must satisfy two constraints:
purple and green must separate for deuteranopes at ~14px cell height by
**luminance**, not hue (e.g. a light purple ground with dark text against a
dark green ground with light text); and yellow on white needs an outline.

The chart copy carries the caveat the data forces: *a screen full of green does
not indicate competitive pace; it typically shows drivers improving as track
conditions evolve.*

## 8. Small multiples and driver-centric views

**Small multiples** are the canonical escape from the twenty-colour problem for
per-lap scatter data: five facets wide for a field view, four wide for a
team-mate comparison so team-mates sit side by side, shared x and y, facet
ordered by finishing position. Inside each facet colour carries compound,
marker shape carries tyre freshness, and the facet itself carries driver
identity. Only one facet carries a legend. Outlier control keeps laps within
110% of the fastest.

**Battle map** — x = lap, y = delta in ms to the cars ahead (positive) and
behind (negative), with a dashed rule at ±1000 ms. The marks are not points but
**three-letter driver codes rotated 45°**, so identity is read directly. Colour
separates cars adjacent in *race* position from cars physically interposed on
track on a different lap. The distinction it encodes — track position versus
race position — is the thing every other chart erases. Cap labelled neighbours
at four to six per lap or it becomes a wall of type.

**Race concordance** — y = lap, x = accumulated lap-time delta relative to the
focus driver. Colour encodes **lap offset**, not identity: same lap; ahead on a
subsequent lap (blue-flag situations); progressively lapped backmarkers.
Horizontal rules mark the focus driver's pit laps. Underlying computation is a
self-join on accumulated time within a ±W window:

```sql
SELECT l1.code,
       l1.acctime - l2.acctime AS acctimedelta,
       l2.lap - l1.lap         AS lapdelta,
       l2.lap                  AS focuslap
FROM lapTimes AS l1 JOIN lapTimes AS l2
WHERE l1.acctime < l2.acctime + W AND l1.acctime > l2.acctime - W
```

W of 20–30 s captures the meaningful traffic. Accumulated time is one cumulative
sum; the windowed join is O(n·k) and is precomputed at build time into
per-driver JSON so the page does no work at runtime.

## 9. Choosing a chart

The FT Visual Vocabulary's nine relationship categories are the selection tool:
**Deviation, Correlation, Ranking, Distribution, Change over Time,
Part-to-whole, Magnitude, Spatial, Flow.** Mapped onto this site:

| Question | Category | Form |
| --- | --- | --- |
| Gap to leader | Deviation | Surplus/deficit line from a reference |
| Team-mate qualifying delta | Deviation | Diverging bar |
| Pace vs tyre age | Correlation | Scatter + fit |
| Championship progression | Ranking | Bump / cumulative line |
| Stint lap-time spread | Distribution | Dot strip or box |
| Stint timeline | Change over Time | Gantt |
| Sector time share | Part-to-whole | Stacked bar |
| Circuit geometry | Spatial | Map |
| Undercut / pit flow | Flow | Sankey |

Position on a common scale beats angle and area — the Cleveland & McGill
graphical-perception ranking is the reason there are no pie charts here.

**Licensing note:** the Visual Vocabulary repository is MIT for the *software
only*. The poster and PDFs are FT content, all rights reserved, and cannot be
republished. Use it as a reference; do not redistribute it.

## 10. Honesty rules

- **Never smooth or interpolate away a missing lap.** Truncate the line.
- **Never render an empty axis.** A missing dataset produces designed copy
  explaining what is missing and why. The conditional-panel pattern in §6 is
  the mechanism.
- **Every derived figure states its assumptions in situ** — fuel coefficient,
  reference lap, excluded laps, mini-sector count — as a small note in the
  caption style, linking to the method page.
- **Lie Factor** = (size of effect shown) / (size of effect in data). Below 0.95
  or above 1.05 indicates substantial distortion. Truncated axes, sqrt
  compression and clipped domains all move this number, which is why each one
  above is labelled on the chart rather than applied silently.
- **Data-ink as a default, not a law.** Maximise the proportion of ink that
  responds to variation in the numbers; erase non-data ink and redundant data
  ink — both "within reason". The empirical literature on chartjunk does not
  support treating it as an absolute.

## 11. Do not build

- 3D bar charts, or any 3D chart.
- Pie charts and donut charts of anything.
- Rainbow or viridis/plasma ramps applied to **categorical** data. A sequential
  ramp for a continuous quantity (speed, gear, elapsed time) is correct; a
  perceptually-uniform ramp for twenty drivers is not.
- Charts that animate on load by default.
- Gradient fills, glows or drop shadows on data marks.
- Twenty-entry legends.
- A DRS band chart for 2026 or later. That archetype is season-conditioned and
  valid only through 2025.
- The hero-metric layout — one huge number, a small label and supporting stats.
  It is the single most tempting pattern for a motorsport site and it is a
  named category default; it has to be argued for in writing before it ships.
- Sparklines or progress rings **standing in for content**. A sparkline that
  carries real per-lap data is exactly the sanctioned use; one used as visual
  filler is not.
