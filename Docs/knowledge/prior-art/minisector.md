---
type: Reference
title: minisector
description: The nearest prior art by brief — a static, dependency-free GitHub Pages F1 analysis site — with its architecture, exact line counts, borrowable techniques and what it does not attempt.
resource: https://github.com/lennyocbot/minisector
tags:
  - prior-art
  - static-site
  - svg
  - charting
  - reference-implementation
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: minisector_api
    resource: https://api.github.com/repos/lennyocbot/minisector
    title: GitHub API — lennyocbot/minisector repository metadata
  - id: minisector_readme
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/README.md
    title: minisector — README
  - id: minisector_charts
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/charts.js
    title: minisector — charts.js
  - id: minisector_core
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/core.js
    title: minisector — core.js
  - id: minisector_views_b
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/views_b.js
    title: minisector — views_b.js (stints, long runs, degradation)
  - id: minisector_views_c
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/views_c.js
    title: minisector — views_c.js (race trace, position chart)
  - id: minisector_views_d
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/views_d.js
    title: minisector — views_d.js (dominance, telemetry panels)
  - id: minisector_template
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/template.html
    title: minisector — tools/template.html
status: stable
---

# minisector

`lennyocbot/minisector` is the closest thing in the field to this project's
brief: a **static, dependency-free, SVG-rendered F1 analysis site published on
GitHub Pages**, built by a Python extraction step from FastF1 and assembled into
a single page with no runtime libraries at all. It is the benchmark to clear on
charting, and its source is the most directly readable implementation of the
archetypes in [Chart archetypes](../design/chart-archetypes.md).

It is also a solo, essentially undiscovered project. Its conventions carry the
authority of one author's judgement, not of a community standard.

## 1. Repository facts

| Fact | Value |
| --- | --- |
| Created | 2026-07-08 |
| Last pushed | 2026-09-13 |
| Stars | 1 |
| Primary language | HTML |
| Repository size | ~731 MB, dominated by `data/` (per-session `.json.gz` back to 2018) |
| Runtime dependencies | none — `tools/template.html` loads only inlined `{{CSS}}` and `{{JS}}`; `index.html` references no CDN or external script |
| Licence | **not established by the survey** — treat as a design and method reference until confirmed; do not vendor code |

The size figure is the operationally interesting one. 731 MB of committed
session data in a single repository is exactly the failure mode this project
avoids by splitting site and data — see
[SPEC §11.3](../../SPEC.md) on the 1 GB GitHub Pages cap.

## 2. Architecture

```
index.html                     fetches per-session .json.gz from data/<year>/<round>-<slug>/
manifest.json                  root-level index of available sessions
tools/extract.py               FastF1 -> compact session JSON
tools/build.py --site          assembles template.html + src/ into the single page
tools/template.html            shell with {{CSS}} / {{JS}} substitution points
.github/workflows/f1-data.yml  picks up new sessions ~1-3 hours after F1 publishes
```

The shape is a build-time extraction into compressed per-session JSON, an
index, and a single self-contained page. That is the same shape as this
project's pipeline, with one deliberate divergence: minisector ships **one app
that loads any session**, this project ships **one prerendered page per
entity**. See [Data pipeline](../engineering/data-pipeline.md) and
[Site architecture](../engineering/site-architecture.md).

The workflow cadence is the other divergence. minisector's Action picks up
sessions automatically 1–3 hours after publication. This project cannot: F1's
live-timing archive blocks datacenter IPs, so ingest is a local human step
([SPEC §12.2](../../SPEC.md)).

## 3. Line counts

The whole `src/` is **3,726 lines** across ten files.

| File | Lines | Covers |
| --- | ---: | --- |
| `app.js` | 437 | shell, routing between tabs, state |
| `charts.js` | **225** | the entire SVG charting kernel |
| `core.js` | 306 | data access, colour, flags, clean-lap predicate |
| `views_a.js` | 464 | overview, lap chart |
| `views_b.js` | 489 | pace, long runs, tyres and degradation |
| `views_c.js` | 358 | race trace, position chart |
| `views_d.js` | 686 | mini-sector dominance, telemetry panels |
| `views_e.js` | 286 | qualifying |
| `views_f.js` | 159 | straights / speed traps |
| `views_g.js` | 316 | weather |
| **Total** | **3,726** | |

**225 lines is the number that decides the charting question for this project.**
Every archetype below is produced by that kernel. A charting library would be
larger, would impose its own tick density, label placement and tooltip chrome,
and would then need overriding — which is why the in-house SVG kernel is the
adopted approach.

## 4. The charting kernel

`charts.js` exports:

```
svgEl, cvar, drawHelmet, drawFaceOrHelmet, niceTicks, Chart,
linePath, stepPath, spreadLabels, heatBg,
tip / tipShow / tipHide, hoverMarks, legend, dragZoom
```

`Chart(container, o)` takes
`{w, h, mt, mr, mb, ml, xd, yd, yflip, xticksArr, yticksArr, xlab, ylab, xfmt, yfmt, label}`
and returns `{svg, x, y, plot, ml, mt, iw, ih, xd}`.

Defaults worth adopting wholesale:

| Parameter | Value |
| --- | --- |
| Margins | `mt 12`, `mr 14`, `mb 40` (26 with no x label), `ml 58` |
| Ticks | 6 on y, 8 on x |
| Tick ladder | `[1, 2, 2.5, 5, 10] × 10^floor(log10(step))` |
| Accessibility | every chart SVG carries `role="img"` and an accessible `label` |

Pixel → domain mapping for interaction: `xd[0] + (px − ml) / iw * (xd[1] − xd[0])`.

## 5. Techniques worth borrowing

### 5.1 Race trace formula

```js
for (let lap = 1; lap <= total; lap++) {
  const e = endOf[d.abbr].get(lap);          // cumulative session time at end of lap
  pts.push(e == null ? null : [lap, (refAvg * lap - (e - raceStart)) / 1000]);
}
```

`refAvg` is the winner's clean-lap median, with a documented fallback:

```js
refAvg = wClean.length >= 5 ? median(wClean)
       : (winner && wEnd != null ? (wEnd - raceStart) / wLaps : 95000);
```

Flat = reference pace, a vertical drop = a pit stop or SC lap. The y-domain clip
that stops one safety car squashing the racing into a sliver:

```js
const deepLo = quantile(ys, 0.01) - 4;
const yLo    = Math.max(deepLo, quantile(ys, 0.30) - 90);
```

with a visible footnote when `deepLo < yLo - 20`. Specified for this project in
[Race trace](../metrics/race-trace.md).

### 5.2 Mini-sector dominance by elapsed time, not mean speed

```js
const NSEG = 27;
for (let k = 0; k < NSEG; k++) {
  const r0 = k / NSEG, r1 = (k + 1) / NSEG;
  let wi = 0, wt = Infinity;
  ents.forEach((en, i) => {
    const dt = telAt(en.tel.t, r1) - telAt(en.tel.t, r0);   // elapsed time through segment
    if (dt < wt) { wt = dt; wi = i; }
  });
  domWinner.push(wi); counts[wi]++;
}
```

The common blog method — bin by distance, take mean `Speed`, `groupby().idxmax()`
— is wrong wherever a driver carries speed into a segment they entered slower.
The elapsed-time method also shares `telAt` with the Δ-time panel, so the
dominance strip and the delta curve **cannot contradict each other**, and the
per-segment deltas must sum to the lap-time difference. That summation is a good
automated test.

### 5.3 Per-stint degradation fit

```js
function stintFit(st, sid) {
  const pts0 = st.laps.filter(l => isClean(l) && l.life != null)
    .filter(l => l.lap > st.from)                   // drop first lap of stint
    .map(l => [l.life, fuelCorrWith(l, sid)]);      // x = TyreLife, y = fuel-corrected ms
  if (pts0.length < 4) return null;                 // 4+ clean points, no consecutiveness test
  let fit = linfit(pts0);
  const pts = pts0.filter(([x, y]) => Math.abs(y - (fit.a + fit.b * x)) < 1200);
  if (pts.length >= 4) fit = linfit(pts) || fit;    // refit without outliers
  return fit;
}
```

The important structural fact: `fuelCorrWith` is applied **before** the fit, and
the neighbouring comment in the source marks it as always on for race-session
degradation analysis. Fuel load is collinear with tyre age within a stint and
biases the slope toward zero; it does not cancel out. This is the reasoning
behind the unconditional fuel correction in
[Tyre degradation rate](../metrics/tyre-degradation-rate.md) and
[Fuel-corrected pace](../metrics/fuel-corrected-pace.md).

### 5.4 Luminance-adaptive team colour

```js
function teamCol(hex) {
  let h = hex;
  if (isDark()) { let n = 0; while (lum(h) < 0.10 && n++ < 6) h = mix(h, "#ffffff", 0.22); }
  else          { let n = 0; while (lum(h) > 0.62 && n++ < 6) h = mix(h, "#0a0d12", 0.18); }
  return h;
}
```

`lum` is verbatim WCAG relative luminance. Thresholds: floor **0.10** on a dark
ground, ceiling **0.62** on a light one; mix steps **0.22** toward white and
**0.18** toward `#0a0d12`; a hard cap of **6** iterations so a pathological
colour terminates rather than washing out; `if (!hex) return '#888'` as the null
guard. It solves the real problem that Haas `#b6babd` and HARD-compound
`#f0f0ec` vanish on paper while Red Bull `#0600ef` and Cadillac `#444444` vanish
on an instrument panel.

**Our refinement:** do the mixing in OKLCH, adjusting L only and preserving C and
H, because sRGB channel lerping toward white drifts hue on saturated reds. See
[Colour system](../design/color-system.md).

### 5.5 Teammate distinction by dash

```js
function drvDash(abbr, sid) {
  const d = HUB.driver(abbr, sid);
  return d && d.style === 1 ? "6 3" : null;
}
```

Applied at four line-drawing sites — the lap chart, long runs, the race trace and
the position chart — always as `p.setAttribute("stroke-dasharray", "6 3")`.
Legend chips mirror it with `outline: 2px dashed <col>; outline-offset: 1px`, so
the legend teaches the encoding. `6 3` at `stroke-width: 1.7` is legible without
reading as a grid line. Adopted in
[Driver colour encoding](../design/driver-color-encoding.md); the binding rule
there is that dash is reserved for teammates and never double-encodes.

### 5.6 End-of-line labelling with collision avoidance

```js
if (ch.W >= 520) {
  const endL = series.map(sr => { /* last point of each series */ }).filter(Boolean);
  spreadLabels(endL, 11, ch.mt + 6, ch.mt + ch.ih);   // 11px minimum gap, clamped to plot band
  for (const L of endL)
    svgEl("text", { x: Math.min(L.x, ch.ml + ch.iw + 4), y: L.y, "font-size": 10,
                    "font-weight": 700, fill: L.col, class: "num" }, ch.svg).textContent = L.txt;
}
```

Parameters: a **520 px** width breakpoint below which it falls back to legend
plus hover; **11 px** minimum vertical gap; **10 px bold** labels coloured to the
line; `mr: 46` reserved on that chart for the labels. The label text is the
three-letter abbreviation — the only F1 identifier short enough to sit at the end
of twenty lines.

Related devices in the same file: pit stops drawn as open donuts
(`r: 3.6, fill: var(--surface), stroke: col, stroke-width: 2`) so they read as
events rather than data points, and a synchronised crosshair reporting lap number
plus every visible driver's gap at that lap.

### 5.7 Track-status decoding and the clean-lap predicate

```js
function tsFlags(ts) {
  const s = String(ts || "1");
  return { yellow: s.includes("2"), sc: s.includes("4"), red: s.includes("5"),
           vsc: s.includes("6") || s.includes("7"), green: !/[24567]/.test(s) };
}
```

Clean lap: `l.t != null && !l.in && !l.out && !l.del && tsFlags(l.ts).green && l.acc`
— timed, not an in- or out-lap, not deleted, fully green, and FastF1-accurate.
Every pace chart, degradation fit and race-trace reference is built on that one
predicate, which is why it is defined once here and reused everywhere in
[Clean-air race pace](../metrics/clean-air-race-pace.md).

Note FastF1's full status table has seven codes, not five: `1` track clear (which
is what closes a neutralisation window), `2` yellow, `3` documented as possibly
non-existent, `4` safety car, `5` red flag, `6` VSC deployed, `7` VSC ending.

### 5.8 Conditional panels instead of empty axes

The telemetry DRS panel is labelled `DRS/OT` in the `PANELS` array and is
rendered only when a `hasDrs` flag is set (`if (S.telPanels.d && hasDrs)`), so it
**disappears** for sessions with no DRS channel rather than drawing an empty
axis. That is precisely the pattern this project's honest-absence principle
needs across a 1950–2026 archive where channels appear and vanish by era.

One correction to a plausible misreading of the same file: `stepPath` is applied
to **brake** and **gear**. The DRS panel is not a step chart at all — it is one
horizontal activation row per driver at `rh = 15`, drawn as line segments against
a grey baseline, panel height `ents.length * rh + 26`. A Gantt-style activation
strip. That distinction is carried into
[Chart archetypes](../design/chart-archetypes.md).

## 6. Feature surface

Tabs: Overview, Pace, Tyres & Deg, Long Runs, Qualifying, Race, Straights,
Telemetry, Weather. Two go beyond the field's normal scope: a **race replay
reconstructed from telemetry**, and a **"why the slower lap is slower"
decomposition** that attributes the total lap-time gap to named corner entries,
exits and straights that sum to the measured delta. The README summarises its
user-facing conventions as "deleted laps flagged, personal bests ringed, second
cars dashed".

## 7. What it lacks

| Missing | Consequence for our positioning |
| --- | --- |
| Entity pages | One app that loads any session. No permanent URL for Monza, Ferrari, or the 1976 Japanese GP |
| Editorial voice | No prose. Labels and captions only |
| 3D | None. The track map is 2D SVG |
| Pre-2018 coverage | Data starts at FastF1's telemetry boundary, so ~85% of F1 history is absent |
| Design identity | Functional, theme-switchable, tool-shaped |
| Adoption | 1 star, six weeks old at survey |

It scores **1 / 4** on the axes in [Landscape](landscape.md#3-the-four-axis-scorecard):
static and permanent, and nothing else.

## 8. Reuse posture

- **Borrow:** the formulas, thresholds, predicates and parameter choices recorded
  above. They are method, and the method is sound.
- **Borrow in spirit:** the 225-line kernel's shape — a `Chart` factory, a tick
  ladder, `spreadLabels`, `dragZoom` — reimplemented to our own tokens.
- **Do not vendor:** no licence was established for the repository. Until one is,
  no code is copied. See [Reuse posture by source](reference-materials.md#4-reuse-posture-by-source).

## Related

- [Landscape](landscape.md)
- [Chart archetypes](../design/chart-archetypes.md)
- [Driver colour encoding](../design/driver-color-encoding.md)
- [Race trace](../metrics/race-trace.md) · [Tyre degradation rate](../metrics/tyre-degradation-rate.md)
- [Analysis tools](analysis-tools.md)
