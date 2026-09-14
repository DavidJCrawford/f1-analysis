---
type: Reference
title: Driver colour encoding
description: How twenty drivers are told apart without twenty colours — team colour, dash, direct labelling and selective emphasis, with the measured contrast and colour-vision evidence behind each rule.
tags:
  - design
  - colour
  - accessibility
  - dataviz
  - colour-blindness
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: fastf1_constants
    resource: https://raw.githubusercontent.com/theOehrly/Fast-F1/master/fastf1/plotting/constants.json
    title: FastF1 plotting constants (team and compound colours, 2018–2026)
  - id: fastf1_plotting
    resource: https://docs.fastf1.dev/plotting.html
    title: FastF1 plotting API documentation
  - id: minisector_core
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/core.js
    title: lennyocbot/minisector — core.js (luminance remap, dash assignment)
  - id: minisector_views_c
    resource: https://raw.githubusercontent.com/lennyocbot/minisector/main/tools/src/views_c.js
    title: lennyocbot/minisector — views_c.js (race trace, end-of-line labelling)
  - id: wcag_use_of_color
    resource: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
    title: WCAG 2.2 Understanding SC 1.4.1 Use of Color
  - id: daltonlens
    resource: https://daltonlens.org/opensource-cvd-simulation/
    title: DaltonLens — review of open-source CVD simulations
  - id: js_colorblind_sim
    resource: https://github.com/MaPePeR/jsColorblindSimulator
    title: MaPePeR/jsColorblindSimulator
status: stable
---

# Driver colour encoding

**Twenty drivers do not get twenty colours.** Twenty categorical colours cannot
be told apart at reading speed, they cannot survive colour-vision deficiency,
and — the point most often missed — the source data does not contain twenty
distinct colours in the first place. Two team-mates share a livery, and in 2026
two *teams* share very nearly a hue.

The library that solves this problem for the Python ecosystem abandoned
per-driver colours deliberately. Its stated rationale is worth quoting because
it is the whole argument: *"different colors for 20 drivers end up looking very
similar in a lot of cases. Therefore, it is not a good solution to use driver
specific colours."*

## 1. The four-channel scheme

Every chart on this site encodes driver identity through four channels at once.
No chart uses fewer.

| # | Channel | Carries | Rule |
| --- | --- | --- | --- |
| 1 | **Colour** | Team | Team hex passed through the per-theme ink derivation. Never the raw brand hex for a hairline. |
| 2 | **Dash** | Team-mate index | Car 0 solid; car 1 `stroke-dasharray: "6 3"`. Reserved for this and nothing else. |
| 3 | **Direct label** | Driver | Three-letter code at the end of the line, always. No colour-only legend anywhere. |
| 4 | **Emphasis** | Reading focus | 2–4 drivers in team colour, the rest receded to a single neutral. |

Channel 4 is the **primary reading mode**, not a filter. "All twenty at once"
is the fallback view, not the default. This follows directly from the
working-memory limit of roughly four items: a twenty-line chart asks the reader
to hold twenty identities, and they cannot.

Colour is never the sole encoding. That is SC 1.4.1 (Level A) — the lowest bar
in WCAG, and the one most motorsport data visualisation fails. The W3C's own
failure example for that criterion is a chart distinguished only by line
colour.

## 2. The 2026 palette, measured

Source of truth is FastF1's `fastf1/plotting/constants.json`, which carries
season keys 2018 through 2026 and, for each season, a `compound_colors` map and
a `teams` map with `short_name` plus an `official`/`fastf1` colour pair.

**Pin a specific commit SHA of that file, not `HEAD`.** It is edited through
the season, and a silent upstream change to a livery hex would alter published
charts retroactively.

Contrast measured with the WCAG ratio against `#fafaf8` (light) and `#0e0e10`
(dark). Those two grounds approximate our `--f1-paper` `oklch(97.8% 0 0)` and
`--f1-instrument` `oklch(24% 0 0)` respectively; they are the grounds the
measurement was actually taken on and are quoted as such.

| Team (key) | Official | Light | Dark |
| --- | --- | ---: | ---: |
| alpine | `#0093cc` | 3.32 | 5.55 |
| aston martin | `#229971` | 3.43 | 5.38 |
| audi | `#ff2d00` | 3.57 | 5.17 |
| cadillac | `#444444` | 9.32 | **1.98 fail** |
| ferrari | `#e80020` | 4.51 | 4.09 |
| haas | `#b6babd` | **1.87 fail** | 9.87 |
| mclaren | `#ff8000` | **2.41 fail** | 7.66 |
| mercedes | `#27f4d2` | **1.34 fail** | 13.74 |
| racing bulls | `#6692ff` | **2.82 fail** | 6.54 |
| red bull | `#3671c6` | 4.64 | 3.98 |
| williams | `#64c4ff` | **1.85 fail** | 9.99 |

Five fail 3:1 on the light ground; one fails on the dark one. The JSON key is
`racing bulls`, not `RB`.

### Derived ink tokens

Hue-preserving adjustments that reach the thresholds exactly:

| Team | `ink-light` @ 3:1 | `ink-light` @ 4.5:1 (text) | `ink-dark` |
| --- | --- | --- | --- |
| Haas | `#8c9297` | `#6e7479` | brand |
| McLaren | `#e37200` | `#b55b00` | brand |
| Mercedes | `#08a48b` | `#07826e` | brand |
| Racing Bulls | `#5e8cff` | `#2966ff` | brand |
| Williams | `#0096f3` | `#0078c1` | brand |
| Cadillac | brand | brand | `#5f5f5f` @ 3:1, `#7b7b7b` @ 4.5:1 |

### The `fastf1` variant is not an escape hatch

FastF1 ships a second colormap that diverges from brand truth to separate
rivals (Alpine → pink, Racing Bulls → yellow, Aston Martin → dark green,
Red Bull → `#0600ef`). It is tuned for separability on FastF1's own dark
matplotlib canvas, not for conformance, and **it fails just as often, merely on
different grounds**:

| Team | `fastf1` value | Light | Dark |
| --- | --- | ---: | ---: |
| alpine | `#ff87bc` | **2.13 fail** | 8.67 |
| aston martin | `#00665f` | 6.55 | **2.82 fail** |
| racing bulls | `#fcd700` | **1.35 fail** | 13.65 |
| red bull | `#0600ef` | 8.91 | **2.07 fail** |
| williams | `#00a0dd` | **2.84 fail** | 6.49 |

There is no shortcut. Per-theme ink values must be authored either way. Where
the official colours collide beyond repair we may adopt a `fastf1` hue and
**say so in a footnote on the chart**. We never silently fabricate a colour.

## 3. Colour-vision deficiency

Method: Machado, Oliveira & Fernandes (2009) severity-1.0 matrices applied in
**linear** RGB then re-encoded; distances measured as CIEDE2000 in CIELAB
(D65). One just-noticeable difference is about dE 2.3; anything under dE 10 is
a risk band.

### Deuteranopia — the red/orange collapse

| Pair | Normal | Deuteranopia |
| --- | ---: | ---: |
| Haas / Mercedes | 26.46 | **6.29** |
| Audi / Ferrari | 9.41 | **7.07** |
| Alpine / Racing Bulls | 14.32 | **7.48** |
| Audi / McLaren | 18.30 | **8.09** |
| Alpine / Red Bull | — | **9.49** |
| Racing Bulls / Williams | — | 11.87 |

Simulated appearances explain why: Ferrari `#e80020` → `#93830e`, Audi
`#ff2d00` → `#a89400`, McLaren `#ff8000` → `#c4ae00` — all three become the
same olive. Mercedes `#27f4d2` → `#d1d2d5` and Haas `#b6babd` → `#b8b9bd` —
both become the same light grey.

### Protanopia — different failures, one shared cluster

| Pair | Protanopia |
| --- | ---: |
| Alpine / Racing Bulls | **7.78** |
| Audi / Ferrari | **8.46** |
| Alpine / Red Bull | 10.16 |
| Haas / Mercedes | 14.60 (recovers) |
| Audi / McLaren | 17.17 (recovers) |

**This is the operative finding.** The red/orange collapse is
deuteranopia-specific and recovers under protanopia. The *blue* cluster —
Alpine, Racing Bulls, Red Bull, Williams — degrades under both. So the second
channel and the direct label matter **most on the blue teams**, which is the
opposite of where intuition points after looking at the Ferrari/Audi problem.

### Tritanopia

Audi / Ferrari dE **3.58** — close to a single JND. Alpine / Racing Bulls 5.22.
Alpine / Aston Martin 6.99 (from 33.63 under normal vision).

### The 2026 Ferrari / Audi collision

Ferrari `#e80020` against Audi `#ff2d00` is a live, current collision. It is
narrow under normal vision (dE 9.41), poor under deuteranopia (7.07) and very
nearly invisible under tritanopia (3.58). No luminance remap fixes it — both
are mid-lightness saturated reds, so a remap moves them together. **The only
remedies that work are the non-colour channels**: dash, marker shape, direct
end-of-line label, and selective emphasis that rarely shows both cars in team
colour at once. The same applies to the 2019 Ferrari `#dc0000` /
Alfa Romeo `#9b0000` and 2023 Ferrari `#f91536` / Alfa Romeo `#c92d4b` pairs on
archival pages.

## 4. Okabe-Ito is not a free pass

Okabe & Ito (2002) is the most-cited colour-vision-safe categorical set, and it
is the obvious candidate for a CVD-safe mode. Measured against the same two
grounds:

| Colour | Hex | Light | Dark |
| --- | --- | ---: | ---: |
| Orange | `#E69F00` | **2.16 fail** | 8.56 |
| Sky blue | `#56B4E9` | **2.21 fail** | 8.36 |
| Bluish green | `#009E73` | 3.27 | 5.64 |
| Yellow | `#F0E442` | **1.27 fail** | 14.58 |
| Blue | `#0072B2` | 4.96 | 3.72 |
| Vermillion | `#D55E00` | 3.70 | 4.99 |
| Reddish purple | `#CC79A7` | **2.93 fail** | 6.30 |
| Black | `#000000` | 20.09 | **1.09 fail** |

**Four of the eight fail 3:1 on a light ground, and black fails on dark.** Its
hue separation does hold — the worst deuteranopia pair is orange/yellow at
dE 11.61, comfortably clear of the risk band, and protanopia's worst are
blue/reddish purple 12.3 and sky blue/reddish purple 14.1.

The conclusion: use Okabe-Ito as the **hue skeleton** for the CVD-safe mode,
then adjust lightness per ground so every swatch clears 3:1 (4.5:1 where it
carries text). Do not use it raw, in either theme.

## 5. Dash, marker and label mechanics

### Dash

```js
// Team-mate index within the team decides the dash. Nothing else does.
function drvDash(abbr, sid) {
  const d = HUB.driver(abbr, sid);
  return d && d.style === 1 ? '6 3' : null;
}
```

`stroke-dasharray: "6 3"` at `stroke-width: 1.7` is legible without reading as
a gridline. The legend chip mirrors it (`outline: 2px dashed <col>;
outline-offset: 1px`) so the legend teaches the encoding rather than merely
listing it.

Three constraints on dashing, in order of how often they are violated:

1. **Never double-encode.** Dash means team-mate index and nothing else. If a
   chart also wants to distinguish fresh from used tyres, that goes on a
   different channel.
2. **Dash loses legibility on steep, dense segments.** On a twenty-line race
   trace it is insufficient alone, which is why channel 3 is mandatory.
3. **On scatterplots there are no lines**, so the marker carries it instead.

Mirror the reference cycles so a Python prototype and the web build agree:

```python
stylers = {
    "linestyle": ["solid", "dashed", "dashdot", "dotted"],
    "marker":    ["x", "o", "^", "D"],
}
# idx = team.drivers.index(driver)
```

Beware one collision in the prior art: the same marker channel is elsewhere
used for tyre freshness (`True="o", False="X", Unknown="*"`). Pick one meaning
per chart and state it.

### Direct end-of-line labelling

```js
if (ch.W >= 520) {                       // below this, legend + hover carry it
  const endL = series.map(sr => {
    const last = sr.pts.filter(Boolean).at(-1);
    return last ? { y: ch.y(last[1]) + 3.5, x: ch.x(last[0]) + 5,
                    txt: sr.d.abbr, col: teamCol(sr.d.color) } : null;
  }).filter(Boolean);
  spreadLabels(endL, 11, ch.mt + 6, ch.mt + ch.ih);   // 11px minimum gap
  // … clamp x into the reserved right margin
}
```

| Parameter | Value |
| --- | --- |
| Width breakpoint for direct labels | 520 px |
| Minimum vertical gap after de-collision | 11 px |
| Right margin reserved for labels | 46 px |
| Label text | Three-letter driver code — the only F1 identifier short enough |
| Label colour | Matches the line |

Our label size is 13px JetBrains Mono 500 rather than the 10px bold of the
prior art, to stay above the 12px chart-text floor — see
[Typography](typography.md) §6.

**A twenty-entry legend is banned.** Below the 520 px breakpoint the fallback
is a legend *plus* hover, not a legend alone.

### Selective emphasis

Default state: 2–4 drivers at full team colour and full stroke weight; the rest
at `--f1-text-mute-deep` with reduced opacity and no label. Hover or focus
promotes any receded line to full emphasis. This is the primary mode because it
is the only one that respects the ≤4-item working-memory limit, and because a
chart of twenty equally-weighted lines is the visual-noise-floor failure:
everything has the same weight, so nothing stands out.

## 6. Tyre compounds

The 2026 compound colours, with contrast measured on the light ground:

| Compound | Hex | Light | Requirement |
| --- | --- | ---: | --- |
| SOFT | `#da291c` | 4.66 | — |
| MEDIUM | `#ffd12e` | **1.39** | Outline + letter |
| HARD | `#f0f0ec` | **1.09** | Outline + letter |
| INTERMEDIATE | `#43b02a` | **2.69** | Outline + letter |
| WET | `#0067ad` | 5.67 | Letter |
| UNKNOWN | `#00ffff` | — | Letter |
| TEST-UNKNOWN | `#434649` | — | Letter |

**Every compound block carries its letter — S / M / H / I / W — printed on the
block.** Colour alone fails SC 1.4.1 here for exactly the reason the criterion
exists. HARD `#f0f0ec` is near-white and disappears on paper without a stroke;
the reference implementations all draw it with an explicit `edgecolor`.

Absolute-compound palette, for C1–C6 views: C1 `#00a2f3`, C2 `#f0f0ec`,
C3 `#ffd12e`, C4 `#da291c`, C5 `#b14ca8`, C6 `#feb4c3`, plus C0 `#fe813f` for
2023–24.

## 7. Eras without a palette

FastF1's constants cover **2018–2026 only**. The site has 1,172 races and 214
constructors, the overwhelming majority of them outside that window, and
pre-1990s constructors have no canonical brand hex at all.

This is an open decision recorded honestly rather than papered over: either
era-appropriate livery colours, curated per constructor and cited, or a neutral
archival palette in which colour encodes nothing and identity is carried
entirely by direct labelling. The archival tier ships first, so the decision is
needed early. Whichever is chosen, the rule that colour is never the sole
encoding does not relax.

## 8. Validation, in CI

The palette is a build artifact and is gated like one. The assertions:

1. Every categorical swatch clears **3.0:1** against both grounds.
2. Any swatch that carries text clears **4.5:1**.
3. Every pair of swatches that can appear in the same chart exceeds
   **CIEDE2000 dE 15** under normal vision and **dE 10** under each of
   protanopia, deuteranopia and tritanopia at severity 1.0.
4. A failing build prints the table of offending pairs, not a boolean.

Where assertion 3 cannot be met — Ferrari/Audi is the standing example — the
escape hatch is explicit and recorded on the chart: keep the brand hex for
large fills and chips, substitute the ink token for strokes and text, and add
the non-colour channel. **The pair is never shipped on hue alone.**

Manual cross-checks: MaPePeR's jsColorblindSimulator (runs locally; images
never leave the machine), Coblis, and Viz Palette. DaltonLens documents which
open-source simulation implementations are actually correct — check there
before trusting a simulator.

A note the W3C now concedes itself: the current WCAG 3 Working Draft states
that *"a separate requirement may be needed if red/green color vision
deficiency (CVD) is not accounted for within the contrast algorithm."* That is
precisely the gap measured above — Ferrari, Audi and McLaren all pass WCAG 2
contrast on paper and all collapse to the same olive under deuteranopia.
Contrast conformance is not colour-vision conformance, and this site tests both.
