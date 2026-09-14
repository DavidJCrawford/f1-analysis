# SPEC — F1 Analysis

**A static, editorial, permanently-linkable encyclopaedia of Formula 1, in which
every circuit, every team and every race is a designed essay with real data and
a real 3D track.**

- **Status:** Draft 1 — grounded in the research recorded in
  [`knowledge/`](knowledge/index.md), which was fact-checked adversarially
  (83 of ~252 initial research claims required correction; the corrected values
  are what appear here).
- **Date:** 2026-09-14
- **Deployment target:** GitHub Pages, personal account.
- **Aesthetic reference:** [impeccable.style](https://impeccable.style)
- **3D:** [three.js](https://github.com/mrdoob/three.js) r186

---

## 1. The promise

One sentence, used to accept and reject every feature:

> **Every race, circuit and team in Formula 1 history gets one beautiful,
> permanent, honest page — and the modern ones let you fly the lap.**

Four words in that sentence are load-bearing.

- **Permanent** — URLs never break. This is an encyclopaedia, not a dashboard.
  It is the opposite of a live-timing app, and that is the deliberate position.
- **Honest** — where data does not exist, the page says so in designed language
  rather than rendering an empty chart. Provenance and staleness are visible.
- **Beautiful** — the visual treatment is the product, not the wrapper.
- **Fly the lap** — 3D is a focal moment, not decoration sprayed on every page.

### Why this can exist

The research surveyed the field (see
[`knowledge/prior-art/`](knowledge/prior-art/index.md)). The space is crowded
but lopsided: nearly all prior art is either a **real-time live-timing
dashboard** (f1-dash, Monaco, F1 Cosmos) or a **notebook-grade analysis
surface** (FastF1's gallery, TracingInsights, Armchair Strategist, F1 Data
Junkie). Almost nothing is a static, editorial, permanently-linkable reference
with a designed page per entity.

3D is the thinnest area of all. The only three.js F1 work found is hobby-scale
(0–2 stars) or game-shaped. No polished editorial 3D circuit renderer exists.
The one serious FastF1→GIS→3D pipeline found
([lohithburra01/F1-3D-VISUALIZATION](https://github.com/lohithburra01/F1-3D-VISUALIZATION))
is Blender + Unreal, rendered offline — it validates the data half of the
pipeline and says nothing about the browser.

The nearest neighbour by brief is
[lennyocbot/minisector](https://github.com/lennyocbot/minisector) — a static
GitHub Pages SVG/vanilla-JS F1 app, ~3,700 lines, no dependencies. It is worth
studying closely and is the benchmark to clear on charting, but it is not
editorial and has no 3D.

---

## 2. Audience and stance

Primary: **the engaged fan who wants to understand, not the professional
analyst and not the casual viewer.** Someone who watched the race and wants to
know *why* it happened that way, and who will notice — and care — that the page
is beautiful.

This choice resolves the default-view question: **a race page opens on a
narrative with charts embedded in it, not on a grid of charts.** The chart grid
exists, one scroll down, for people who want it.

Secondary: the design and data-visualisation audience, who will arrive for the
craft and stay for the data. They are why the visual bar is set where it is.

**Explicit non-goals.** Live timing. Predictions and betting. Fantasy F1.
Real-time anything. Accounts, comments, personalisation. A mobile app.
Anything that needs a server.

---

## 3. Design principles

1. **Calm by default.** Adapted from the reference site's own stated principle.
   The page is quiet until you engage it. No autoplay, no idle animation, no
   attention-seeking.
2. **The data is the ornament.** There is no decorative layer. Everything on
   screen either carries information or creates the space that makes
   information legible.
3. **Honest absence.** A missing dataset produces designed copy explaining what
   is missing and why — never an empty axis, a zero, or a spinner that never
   resolves.
4. **One focal moment per page.** Each page has exactly one thing it is *for*.
   On a circuit page that is the 3D track. On a race page it is the race trace.
   Everything else is subordinate.
5. **Typography carries the hierarchy.** Not colour, not boxes, not shadows.
   Colour is reserved for data encoding and a very small amount of interface
   meaning.
6. **Every number is traceable.** Every derived figure links to the method that
   produced it. This is what the knowledge base is *for*, and it is the
   difference between a reference and a blog.
7. **No AI tells.** The reference site names a category of machine-generated
   default it calls "slop" and catalogues 67 of them. The relevant ones are
   prohibited outright in
   [`knowledge/policies/editorial-voice.md`](knowledge/policies/editorial-voice.md):
   italic-serif pull-quotes, gradient hero text, emoji as iconography, status
   chips everywhere, centred body copy, purple-blue gradients, "Powered by",
   card grids as a default layout, and unearned glassmorphism.

---

## 4. Scope

### 4.1 Entities

Counts verified against the current F1DB release (v2026.14.0, 13 Sep 2026) and
jolpica:

| Entity | Count | Page? |
| --- | ---: | --- |
| Seasons | 77 | yes |
| Races (Grands Prix held) | 1,172 | yes |
| Circuits | 78 | yes |
| Circuit **layouts** | ~160 | section within circuit page |
| Constructors | 214 | yes |
| Constructor chronology rows | 217 | feeds lineage timeline |
| Drivers | 881 | phase 2 |

That is roughly **2,400 pages at launch** and up to ~6,000 with driver pages
and season-by-team cross-sections. This scale is the single biggest driver of
the architecture decisions in §6 and §11.

### 4.2 Coverage tiers — the most important structural decision

Telemetry begins in **2018**. Roughly **85% of race pages have no telemetry, no
position data, no 3D replay, no speed traces and no mini-sector map.** A 1976
page and a 2026 page cannot share a template, and if the older pages are just
the modern template with eleven empty panels, the site reads as broken.

So coverage is an explicit, designed, four-tier system. **Tier is a first-class
field on every race record** and it selects the page template.

| Tier | Years | Available | Page character |
| --- | --- | --- | --- |
| **Archival** | 1950–1995 | Results, grid, championship points, retirement causes | Editorial essay, entry-list table, championship-swing chart, constructor lineage. No charts that need lap data. |
| **Timing** | 1996–2017 | + lap-by-lap times and positions, pit stops | Adds lap chart, race trace, gap-to-leader, stint Gantt, pit-stop table. |
| **Telemetry** | 2018–2022 | + car & position telemetry at ~240 ms | Adds speed traces, mini-sector dominance, 3D replay, corner-by-corner order. |
| **Modern** | 2023–2026 | + OpenF1 cross-source, richer race control | Full treatment. |

Archival-era pages need their own chart set — championship swing, entry lists,
constructor lineage, reliability history — which is *additional* design work,
not a subset. This is scoped, not hand-waved.

**Corollary:** the site must be genuinely good at 1962 before it is allowed to
be spectacular at 2026. The archival tier ships first (§16).

---

## 5. Information architecture

### 5.1 Routes

```
/                                   Home — current season, latest race, entry points
/seasons/                           Index of 77 seasons
/seasons/2026/                      Season: calendar, standings evolution, form guide
/races/                             Index, filterable
/races/2026/singapore/              Race page
/circuits/                          Index — the 3D gallery
/circuits/monza/                    Circuit page (hero 3D)
/circuits/monza/layouts/monza-1/    A specific layout
/teams/                             Index
/teams/ferrari/                     Team page (full lineage)
/teams/ferrari/2026/                Team-season cross-section
/drivers/hamilton/                  Phase 2
/methods/                           The knowledge base, published
/methods/fuel-corrected-pace/       One method, with formula and worked example
/about/  /data/  /colophon/
```

**Slug policy.** Slugs derive from F1DB canonical IDs, never from display
names. Ferrari stays `/teams/ferrari/` forever. Entities that renamed —
Toro Rosso → AlphaTauri → RB → Racing Bulls, Force India → Racing Point →
Aston Martin, and the 2026 arrivals Audi and Cadillac — resolve to their
**lineage root** with historical names as redirect aliases. A
`redirects.json` is generated at build time and emitted as Astro redirects.

**Publishing `/methods/`** is deliberate. The knowledge base is not internal
documentation; it is a section of the site. Every derived number links to its
method page. This is principle 6 made structural.

### 5.2 Search

At ~2,400–6,000 pages, browse-only navigation is unusable.
**[Pagefind](https://pagefind.app/)** is the answer: it advertises full-text
search on a 10,000-page site with a **total network payload under 300 kB
including the library**, and chunks its index — which suits GitHub Pages,
since that host *does* support HTTP `Range` requests (verified: returns `206`
with `content-range`).

---

## 6. Data architecture

### 6.1 Sources and their assigned roles

The licence chain is the sharpest constraint on this project, and the
discipline that resolves it is: **every source is confined to a declared role,
and the boundary is enforced in the pipeline, not by good intentions.**

| Source | Version/state | Licence | **Role** |
| --- | --- | --- | --- |
| **F1DB** | v2026.14.0 | CC BY 4.0 | **Canonical spine — redistributable.** Entities, results, standings, 1950–2026. |
| **FastF1** | 3.8.3 (MIT, Py ≥3.10) | MIT tool; data from F1 archive | **Build-time only.** Telemetry, laps, position. Derived aggregates ship; raw streams do not. |
| **jolpica-f1** | live | CC BY-**NC-SA** 4.0 | **Build-time gap-fill only. Never redistributed.** NC-SA would infect the site. |
| **OpenF1** | 2023+ | CC BY-**NC-SA** 4.0 | Cross-check, **and published geometry** for circuits the MultiViewer dataset lacks. Non-commercial and share-alike accepted for this project. |
| **MultiViewer** | undocumented API | **no terms published** | **Primary geometry, start/finish and official corner positions** for 31 circuits. No terms are published; accepted for this project. |
| **bacinger/f1-circuits** | 40 circuits | MIT | Circuit outlines — redistributable. |
| **TUMFTM/racetrack-database** | 24 tracks (19 used) | **LGPL-3.0 over ODbL** | Centreline + width, **redistributed** as derived outlines for 19 circuits. OSM-derived, so OSM attribution and onward ODbL apply. |
| **F1DB circuit SVGs** | in-repo only | CC BY 4.0 | 2D layout diagrams. |
| **Copernicus GLO-30 DEM** | — | free, attribution | Distant terrain only. |

Two corrections from verification that change the plan:

- **F1DB's SVGs are not in the release zips.** They exist only in the git repo
  at `src/assets/circuits/{black,black-outline,white,white-outline}/<layoutId>.svg`.
  A pipeline that downloads release artifacts gets zero SVGs; it must
  sparse-checkout or raw-fetch per layout ID.
- **bacinger/f1-circuits is not OpenStreetMap-derived.** Its README names
  Google My Maps tracing plus Wikipedia. That removes the ODbL share-alike
  concern but introduces a Google Maps ToS question instead, and means the
  "OSM-derived" provenance story cannot be told. Measured length error vs
  declared: Silverstone −0.113%, Monza −0.002%, Monaco −0.27%, Spa −0.255%.

### 6.2 Data that must NOT come from jolpica

Verification established that **jolpica collapses retirement causes from 2024
onward**, not 2025 as its docs state — 2024 already returns only
`Finished / Lapped / Retired / Did not start / Disqualified`. Lap-down margins
are flattened from `+N Laps` to a single `Lapped` over the same range.

**Therefore: all retirement-cause and laps-down analysis for 2024–2026 must
come from F1DB.** This is a correctness trap that would silently produce wrong
reliability charts for three recent seasons.

### 6.3 Entity resolution — the unowned hard problem

Five sources, five identifier schemes. `DriverId`/`TeamId` join FastF1 to
jolpica. **Circuits are the hard case and nobody's default handles them:**

- F1DB: 78 circuits, ~160 **layouts**
- MultiViewer: opaque `circuit_key` + year
- OpenF1: `circuit_short_name`
- bacinger: its own `cc-year` slugs

Binding *"this race ran on this layout, whose geometry is this centreline"* is
a first-class build artifact: **`circuit-layout-registry.json`**, hand-verified
once per layout and regression-tested.

Circuits change. Silverstone, Bahrain, Yas Marina, Zandvoort, Albert Park, Spa,
Suzuka and Hockenheim have all been relaid. **A circuit is an entity with a
version history**, and picking one layout per circuit silently misattributes
lap records and geometry.

### 6.4 Messy history the schema must model

F1DB models these and most schemas ignore them: shared drives (pre-1958), half
points, the Indianapolis 500 as a championship round 1950–60, drivers scoring
for two constructors in one season, ties broken on countback, and
retroactively amended classifications. The schema accommodates all of them from
the start.

### 6.5 Payload strategy

Measured figures for one race of 20-car position data:

| Encoding | Size |
| --- | --- |
| 5 Hz, int16 delta-encoded, planar, gzipped | **1.31 MB** (~65 KB/car) |
| 2 Hz, same | **623 KB** |
| float32 naive | gzips only ~6% — unusable |

**Decision: 2 Hz for the default replay (623 KB), 5 Hz fetched on demand** when
the user opens corner-level analysis. Position data is natively ~240 ms
(measured median 241.0 ms on the 2024 British GP; the "220 ms" in FastF1's docs
is nominal, and the mean of 259.3 ms is inflated by gaps), so 5 Hz is close to
native and 2 Hz is a real reduction.

Browser Parquet via **hyparquet** (18.4 KiB min+gzip, zero deps) is viable
because GitHub Pages supports Range requests. **duckdb-wasm is disqualified**:
its wasm binaries measure 35–41 MB, not the 6–18 MB commonly quoted.

GitHub Pages serves **gzip only, never brotli** — verified by request. Emitting
`.br` siblings is dead weight that counts against the 1 GB cap.

---

## 7. The analysis layer

Every metric is specified, implemented once, tested against a hand-verified
fixture, and published at `/methods/<slug>/`. Full definitions live in
[`knowledge/metrics/`](knowledge/metrics/index.md).

**Launch set:**

- Fuel-corrected pace
- Tyre degradation rate (per stint, robust linear fit)
- Clean-air race pace
- Undercut/overcut delta
- Pit loss time (per circuit, green vs SC vs VSC)
- Gap to leader / race trace
- Position at lap **and position at corner** (see §8.3)
- Overtake count
- Teammate delta
- Reliability / DNF rate

**Three methodological commitments, each from a correction:**

1. **Fuel load does not cancel out of a degradation slope.** It is collinear
   with tyre age within a stint and biases the slope toward zero. Fuel
   correction is applied *unconditionally before* fitting degradation.
2. **Overtake counting uses the published definition**, not a naive diff of the
   position column. From de Groote (2021), *Overtaking in Formula 1 during the
   Pirelli era*, [doi:10.3233/JSA-200466](https://doi.org/10.3233/JSA-200466):
   a manoeuvre takes place "during complete flying laps (so not on the opening
   lap) and is then maintained all the way to the lap's finish line. Position
   changes due to major mechanical problems or lapping/unlapping are not
   counted." **Lapping/unlapping is the single largest source of false
   positives** in a naive implementation.
3. **Pit-stop loss under SC/VSC is circuit-specific, spanning roughly 12–82%
   of green-flag loss** — not the 30–60% commonly quoted. It is smallest at
   long-pitlane/low-limit circuits (Sochi 12%, Singapore 18%, Monaco 28%) and
   largest at Spielberg (82%) and Spa (73%). The site never quotes a single
   global figure.

**Stance on speculative metrics.** Driver-vs-car decomposition (Elo-like
ratings, "true pace" tables) has uncertainty that often exceeds its signal, and
the literature does not agree: Bell et al. (2016),
[JQAS 12(2):99–112](https://doi.org/10.1515/jqas-2015-0050), is a multilevel
model over 1950–2014 and produces **no** constructor-share percentage; the
widely-repeated "64%" comes from a different paper using time-decayed ridge
regression, and is specifically its DNF-excluded model. **Such metrics are
published only with visible uncertainty intervals and a named method, or not at
all.**

---

## 8. Visual design system

Full token extraction, read directly from the reference site's compiled CSS, is
in [`knowledge/design/design-tokens.md`](knowledge/design/design-tokens.md).
This section states what *we* do.

### 8.1 Foundations

- **Colour space: OKLCH throughout.** Non-negotiable — it is what makes a
  perceptually-even categorical palette possible.
- **Neutrals at chroma 0.** Paper `oklch(97.8% 0 0)`, ink `oklch(13% 0 0)`,
  body text `oklch(22% 0 0)`.
- **Two interface accents only:** gold `oklch(84% .19 80.46)` and patina
  `oklch(70% .12 188)`. Vermilion `oklch(52% .16 35)` is reserved for alarm.
  **Interface accents are never used to encode data.**
- **Instrument surfaces**, `oklch(24% 0 0)` and family, for dark panels set
  into the light page. The reference site has **no dark theme** — it has
  instrument panels, each declaring `color-scheme: dark` via scoped token
  remapping. We adopt exactly this, and it is what lets a dark WebGL canvas sit
  on a light page without a theme switch. A full dark theme is a **phase-2
  decision**, not a launch requirement.
- **Radii:** `3px` default, `8px` cards only.
- **Grid:** 12 columns, `1320px` max; prose measure `65–75ch`.

### 8.2 Typography

Albert Sans (text), Alumni Sans (display), JetBrains Mono (data), self-hosted
and subset via **Astro's Fonts API** — no third-party font request, no FOUT.

The reference's inverted weight relationship is adopted: **display at weight
200–300, small titles at 600.** Large type whispers; small type asserts.

**Our required addition:** the reference stylesheet contains no
`font-variant-numeric` anywhere. It doesn't need it. We do.

```css
--f1-numeric: tabular-nums lining-nums;
```

applied to every timing readout, table cell, axis label and telemetry value.
Verified tabular-by-default candidates if Albert Sans proves inadequate for
figures: IBM Plex Sans, Chivo, Asap, Noto Sans, Open Sans, Radio Canada.

### 8.3 Encoding drivers — the 20-colour problem

**Twenty drivers do not get twenty colours.** Two colours cannot be
distinguished at speed, and team colours collide outright — in 2026 Ferrari
`#e80020` against Audi `#ff2d00`.

The adopted scheme, following FastF1's canonical answer and minisector's
refinement:

1. **Team colour identifies the team**, luminance-remapped per ground so brand
   hues hold ≥3:1 contrast on both paper and instrument surfaces.
2. **Line style separates teammates** — car 2 gets `stroke-dasharray: "6 3"`.
3. **Direct end-of-line labelling**, always. No colour-only legend anywhere.
4. **Selective emphasis** — 2–4 highlighted, the rest receded to a neutral.
   This is the primary reading mode; "all 20 at once" is a fallback.

Colour is **never the sole encoding**. Checked under deuteranopia and
protanopia. Note the Okabe-Ito palette is not a free pass: **four of its eight
colours fail 3:1** on a light ground (orange 2.16, sky blue 2.21, yellow 1.27,
reddish purple 2.93), and black fails on dark — hence per-theme re-toning.

### 8.4 Motion

Every transition on the reference site sits between **0.12s and 0.18s** on one
easing curve, `cubic-bezier(.2, .8, .2, 1)`. A camera flying Spa cannot obey
that, so motion is split and the split is a policy:

- **Chrome motion** — buttons, panels, tooltips, page transitions — obeys the
  0.18 s ceiling absolutely.
- **Content motion** — camera moves, car animation, scrubbing — is exempt, but
  must be **user-initiated or user-scrubbable, never idle-looping**, and must
  collapse to a meaningful static frame under `prefers-reduced-motion`.

---

## 9. 3D art direction

### 9.1 The scope trap, and the tiered answer

Banking must be hand-authored per corner. Kerbs and run-off must be
procedurally generated. Widths are missing for roughly 12 circuits. Elevation
is only trustworthy where telemetry exists (2018+). Multiplied across 78
circuits and ~160 layouts, **a polished 3D track is affordable for perhaps
8–12 circuits, not for all of them.**

So 3D is tiered, and the tier is stated on the page:

| Tier | Count | Treatment |
| --- | --- | --- |
| **Hero** | 8–12 | Hand-authored banking, real elevation, kerbs, run-off, custom camera choreography. Monza, Spa, Monaco, Suzuka, Silverstone, Interlagos, Zandvoort, Singapore first. |
| **Standard** | ~40 | Procedural from centreline + width, flat or DEM-approximated, generic kerbs. |
| **Outline** | remainder | 2D SVG layout only, from F1DB assets. No 3D. |

### 9.2 Technical baseline (verified against r186)

- **three.js 0.186.0** (r186, published 2026-09-08). Cadence is 8–11 weeks, so
  r187 lands ~Nov 2026 — which is when `postprocessing`'s `< 0.187.0` peer
  bound bites. Pin exactly; `^` ranges are unsafe on `0.x` semver.
- **WebGLRenderer** at launch. WebGPU/TSL is tracked, not shipped.
- **Track ribbon**: custom `BufferGeometry` on a **fixed world-up frame**, not
  `computeFrenetFrames`. The reason matters: three.js's `computeFrenetFrames`
  is misnamed — it is *already* a parallel-transport frame. The real problems
  are that its initial normal is chosen arbitrarily (unpredictable starting
  roll), that parallel transport conserves twist rather than gravity (so a
  track built on it self-banks through elevation change), and that closed
  curves get a residual-twist correction smeared along the whole loop. A real
  circuit is near-flat in roll except where deliberately banked, so banking is
  authored data, not a side effect of the frame.
- **Cars**: `InstancedMesh` with per-instance colour.
- **Post-processing**: `RenderPipeline` (renamed from `PostProcessing` in
  **r183**, not r185).
- **Shadows**: `PCFShadowMap`. `PCFSoftShadowMap` is deprecated-with-warning in
  r186.
- **Timer**: `import { Timer } from 'three'` — it moved to core at ~r179/r180.
  The addon path `three/addons/misc/Timer.js` is **404**.
- **Meshopt**: `three/addons/libs/meshopt_decoder.module.js` — **not** under
  `loaders/`, which 404s. Only `DRACOLoader` and `KTX2Loader` live there.
- **Textures**: KTX2/Basis. ETC1S is ~0.3–3 bpp on the wire, transcoding to
  4 bpp on GPU; UASTC LDR 4×4 is 8 bpp on GPU.

### 9.3 Coordinate handling

FastF1 position `X`/`Y`/`Z` are in **1/10 metre from 2020 onward** — the unit
has a date cutoff that is easy to miss.

For local ENU ↔ WGS84, the naive equirectangular constant is wrong: using the
equatorial radius `a = 6378137` on both axes gives **0.4–2.5 m of systematic
scale error** at F1 latitudes. Use the ellipsoidal radii —
`k_east = N(φ₀)·cos(φ₀)`, `k_north = M(φ₀)` — which brings residual below
0.1 m over a few km.

Copernicus GLO-30 tile paths are deterministic in *form* but not in
*availability* — some tiles are withheld and at least one F1 venue (Baku)
returns 404. Always handle the 404. It is a surface model at <4 m LE90, so it
is for **distant terrain only**, never the track surface.

### 9.4 What the 3D is *for*

An honest answer, because it decides placement. The 3D is **scene-setting and
spatial comprehension** — it answers *"what is this place actually like?"*,
which no 2D map conveys. It is therefore **once per circuit page, as the focal
moment**. The race-page replay is a *different, smaller* component: a top-down
or low-angle scrub of car positions, in service of an analytical question.

`<canvas>` is never the LCP element. The page renders complete, then the scene
mounts via `client:visible` behind a static poster frame.

---

## 10. Chart archetypes

Specified in [`knowledge/design/chart-archetypes.md`](knowledge/design/chart-archetypes.md).

| Chart | Encoding | Tier |
| --- | --- | --- |
| Lap/position chart | inverted y, one line per driver, direct labels | Timing+ |
| Race trace | cumulative delta vs constant reference pace | Timing+ |
| Gap to leader | **sqrt-compressed** y so leaders stay readable; `+1L` annotations | Timing+ |
| Stint Gantt | stacked horizontal bars, compound colour | Timing+ |
| Mini-sector dominance | track segments coloured by fastest | Telemetry |
| Speed trace + delta | shared distance axis, delta panel below | Telemetry |
| Throttle/brake/gear | **step** paths for brake and gear; DRS as per-driver activation bars, not a step chart | Telemetry |
| Tyre deg scatter | per-stint robust fit, ±1200 ms residual filter, 4-point minimum | Timing+ |
| Championship swing | cumulative points, one line per contender | All |
| Constructor lineage | timeline with rename/merge events | All |

**Charting implementation: a small in-house SVG kernel**, not a charting
library. minisector's equivalent is 225 lines and its whole `src/` is ~3,700.
The aesthetic bar here cannot be met by restyling a library, and the archetypes
are few and stable. D3 scales/shape may be used as utilities; Observable Plot
is rejected for this reason (and note it is dual-published ESM+UMD with d3 as a
regular dependency — the "ESM-only, d3 as peer" characterisation is wrong, but
it is moot).

---

## 11. Accessibility and performance

### 11.1 Accessibility — targets

- **WCAG 2.2 AA.** Text 4.5:1, large text and **graphical objects 3:1**
  (SC 1.4.11) — this binds every chart line, axis and marker.
- **SC 2.4.11 Focus Not Obscured (AA)** is required. SC 2.4.13 Focus
  Appearance is **AAA** and aspirational — the two are not one requirement.
- **SC 2.5.8 Target Size (AA)**: at least 24×24 CSS px.
- **Every chart has a real `<table>` fallback**, following the W3C complex-image
  pattern (which sanctions **three** approaches, not four): `<figure
  role="group">` containing the visual with a short `alt` pointing to the long
  description, plus a `<figcaption>` with prose and the data table.
- **The 3D scene is keyboard-operable** and has a text alternative describing
  the circuit. If `OrbitControls.listenToKeyEvents` is attached to the canvas
  rather than `window`, that is a **deliberate deviation** from three.js's
  documented recommendation, taken to avoid swallowing page arrow keys — and
  documented as such.
- `prefers-reduced-motion` collapses all content motion to static frames.

### 11.2 Performance budgets

| Metric | Target |
| --- | --- |
| LCP (all pages) | < 2.0 s on 4G |
| INP | < 200 ms |
| CLS | < 0.1 |
| JS on a non-3D page | < 40 kB gzip |
| Initial data per race page | < 250 kB |
| 3D chunk (lazy) | < 350 kB gzip |
| Replay payload (2 Hz) | ~623 kB on demand |
| Search | < 300 kB total |

A long task is **50 ms or longer**. `scheduler.yield()` is **not Baseline** —
feature-detect with `globalThis.scheduler?.yield` and fall back to
`setTimeout(r, 0)`.

**Canvas limits:** the often-cited "224 MB iOS canvas cap" is wrong — that was
`ramSize()/4` on a ~1 GB device. Current WebKit enforces a **per-canvas area**
limit: 8192×8192 on iOS, 16384×16384 elsewhere. Budget texture memory from an
actual inventory and device-tier testing.

### 11.3 GitHub Pages platform limits

| Limit | Value |
| --- | --- |
| Published site | ≤ 1 GB |
| Source repo | ≤ 1 GB recommended |
| Bandwidth | 100 GB/month **soft** |
| Builds | 10/hour soft |
| Deploy timeout | 10 minutes |
| Compression | **gzip only, never brotli** |
| Caching | `max-age=600` on *every* file, including content-hashed assets |
| Range requests | **supported** (206) |
| CORS | `access-control-allow-origin: *` |

The `max-age=600`-on-everything behaviour means long-lived immutable caching is
impossible; the site depends on Fastly edge caching and ETag 304s.

**The 1 GB cap and the 100 GB/month bandwidth cap together are the binding
constraint on how much telemetry ships.** One viral link is an outage. A CDN
fallback path is designed **before** launch, and telemetry lives in a separate
data repository released via GitHub Releases if the cap is approached.

---

## 12. Build and operations

### 12.1 Stack

| Layer | Choice |
| --- | --- |
| Site | **Astro 7** (7.3.2; 7.0 shipped 2026-06-22 on Vite 8/Rolldown, Rust compiler). Node 22+. |
| Language | TypeScript, strict |
| 3D | three.js r186, lazy island |
| Charts | in-house SVG kernel |
| Search | Pagefind |
| Ingest | Python 3.12 + FastF1 3.8.3 |
| Validation | pydantic + pandera |
| CI/CD | GitHub Actions → `actions/deploy-pages` |

Astro is chosen on evidence, not taste: it is zero-JS by default, its
`client:visible` / `client:only` directives isolate three.js into lazy chunks
naturally, and **`experimental.incrementalBuild` (7.2) with a `cacheKey` on
`getStaticPaths()`** skips re-rendering unchanged pages — which is what makes a
2,400–6,000 page site rebuild inside a 10-minute deploy window. It is also what
the reference site itself is built with.

### 12.2 This is a weekly publication, not a build

The operational reality nobody would discover until it hurt:

- **GitHub-hosted runners cannot ingest.** F1's live-timing archive blocks
  datacenter IPs.
- **The free jolpica dump is 14 days delayed.**
- **Stewards retroactively amend results for days after a race.**

Therefore: **a human runs a local ingest after each race weekend, and pages
published within ~72 hours of a race may be factually wrong.**

That is a design requirement, not just an ops note:

- Every page carries a **"data as of"** stamp.
- Races inside the amendment window render a **"provisional classification"**
  state — a real designed state, not a tooltip.
- A **runbook** lives at [RUNBOOK.md](RUNBOOK.md) covering the post-race ingest,
  triple-headers, and what to do when the maintainer is away.
- Ingest output is committed as data, so the site is always buildable from the
  repo alone and CI never needs network access to F1.

### 12.3 Quality gates

Given that adversarial verification corrected 83 of ~252 research claims, the
probability of shipping confidently-presented wrong numbers is the main
correctness risk. CI blocks on:

- **Golden-file tests** for every derived metric against hand-verified
  reference races (a known lap chart, a known pit-stop table).
- **Link checking** across all pages — dense cross-linking at this scale rots
  silently.
- **axe** accessibility checks and **Lighthouse CI** budgets.
- **Visual regression** on a representative page per tier.
- **Schema validation** of all emitted JSON.

**Timezones:** session times are stored as UTC with an explicit circuit
timezone and always rendered with a visible label. Otherwise every schedule on
the site is subtly wrong.

---

## 13. Legal, licensing and attribution

This section is a **gating item**, not boilerplate. It is the project's largest
non-technical risk.

1. **F1's own Legal Notices assert copyright and database rights over timing
   data and restrict use to personal, non-commercial purposes.** The plan to
   publish derived telemetry runs against this. **Mitigation: publish derived
   aggregates and visualisations, never bulk raw timing streams**, keep volumes
   modest, carry a clear non-affiliation disclaimer, and be prepared to take
   material down.
2. **F1DB's CC BY 4.0 is a claim by a compiler about data he did not create.**
   Its README documents **no upstream provenance at all** — no sources, no
   third-party attribution, no trademark disclaimer despite using "Formula 1®".
   If any of it descends from Ergast (CC BY-**NC-SA** 3.0), the permissive
   relicensing is not effective downstream and the clean-licence spine is an
   assumption. **Action: ask the maintainer directly before F1DB becomes
   load-bearing.**
3. **MultiViewer publishes no terms of use.** Its API carries a ~730-point
   centreline plus corners and marshal sectors, and is genuinely the best
   geometry available — but shipping it without permission is not acceptable.
   **Action: contact maintainers. Blocked until resolved.** Also note
   `miniSectorsIndexes` is absent on roughly half of circuits (including
   Silverstone, Monaco, Suzuka, Singapore, Miami, Imola, Montreal, Spielberg,
   Catalunya and Interlagos), so it cannot be the general recipe for sector
   boundaries anyway.
4. **The licence stack must reconcile as a whole.** LGPL-3.0 (TUMFTM), ODbL
   (any OSM-derived geometry), CC BY-NC-SA (jolpica, OpenF1) and CC BY 4.0
   (F1DB) cannot coexist in one redistributed bundle. The §6.1 role boundary is
   the mechanism, and it is enforced in the pipeline: **NC-SA sources are
   build-time inputs whose values are never written to a published artifact.**
5. **Trademark.** The site name, domain and page titles must not imply official
   status. A disclaimer appears in the footer of every page. F1's fan-site
   guidelines dictate specific wording — **the exact current wording is
   unverified (both candidate URLs 404) and must be confirmed before launch.**
6. **There is no free, legal F1 photo corpus.** Getty/LAT/Motorsport Images are
   uniformly rights-managed. **The design system is therefore built to work
   entirely without photography** — which is a compositional constraint, not a
   limitation to work around later. Typography, data, the 3D renders and the
   F1DB circuit SVGs are the visual material.
7. **Attribution page** at `/data/` names every source, its licence, and its
   role.

---

## 14. Editorial

The gap the research itself exposed: eight dimensions produced deep findings
about rendering and zero about **who writes the words**. At this scale a
designed essay per entity is ~1,500 pieces of prose.

**Position:**

- **Hand-written prose is scoped to a small, finite set** — the 8–12 hero
  circuits, the major constructors, and a curated set of landmark races. These
  get real essays.
- **Every other page is data-driven and templated**, and its copy is written to
  be *structural*, not pseudo-narrative: captions, definitions, and honest
  statements of fact. Template copy that imitates a human essay is exactly the
  flat, interchangeable output the slop catalogue exists to detect, and it is
  prohibited.
- **LLM-drafted prose, if used at all, is treated as a first draft requiring
  human fact-checking before publication**, and pages containing it are marked
  in the source. On a site whose entire value is being *right* about F1
  history, unreviewed generated prose is an unacceptable risk.
- A **voice specification** — tense, person, number formatting, how to describe
  an incident neutrally — lives at
  [`knowledge/policies/editorial-voice.md`](knowledge/policies/editorial-voice.md).

---

## 15. Risks

| # | Risk | Severity | Mitigation |
| --- | --- | --- | --- |
| 1 | F1 asserts rights over published telemetry | **High** | Derived aggregates only; disclaimer; takedown readiness (§13.1) |
| 2 | F1DB licence chain unsound | **High** | Contact maintainer before it is load-bearing (§13.2) |
| 3 | 3D scope explodes across 160 layouts | **High** | Hard tiering, 8–12 hero circuits (§9.1) |
| 4 | Editorial volume unachievable | **High** | Finite hand-written set; structural copy elsewhere (§14) |
| 5 | Bandwidth/size caps breached | Medium | 2 Hz default, separate data repo, CDN fallback designed pre-launch |
| 6 | Wrong numbers shipped confidently | Medium | Golden-file fixtures, published methods (§12.3) |
| 7 | Circuit-layout resolution wrong | Medium | Hand-verified registry, regression tests (§6.3) |
| 8 | Post-race ingest depends on one human | Medium | Runbook; provisional state; site buildable from repo alone |
| 9 | MultiViewer geometry unusable | Medium | Fall back to bacinger + TUMFTM + telemetry-derived centrelines |
| 10 | Build exceeds 10-minute deploy window | Low | `experimental.incrementalBuild`; split data repo |

---

## 16. Roadmap

**Phase 0 — Foundations.** Resolve §13 gating items (F1DB provenance,
MultiViewer terms, disclaimer wording). Build the circuit-layout registry.
Stand up the ingest pipeline and the design system in isolation.

**Phase 1 — The archival site.** All 77 seasons, all 1,172 races at *archival
tier*, all 78 circuits with 2D SVG layouts, all 214 constructors with lineage.
No telemetry, no 3D. **Ship this.** It is a complete, useful, beautiful
reference on its own, and it proves the site is good at 1962.

**Phase 2 — Timing era.** Lap charts, race traces, stint Gantts, pit analysis
for 1996+.

**Phase 3 — Telemetry and the first hero circuit.** 2018+ telemetry charts.
**One** hero circuit in full 3D — Monza — built end to end to prove the
pipeline before it is repeated.

**Phase 4 — 3D at tier.** Remaining hero circuits; procedural standard tier.

**Phase 5 — Drivers, search, comparison tools.**

---

## 17. Decisions needed

These are genuinely the user's call and are not assumed:

1. **Domain and name.** Drives the trademark posture in §13.5.
2. **Repository layout** — single repo, or site + data split? Recommendation:
   **split**, from the start, because of the 1 GB cap.
3. **Is the dark theme in scope for launch,** or is the instrument-panel
   approach sufficient? Recommendation: **instrument panels only at launch.**
4. **How much hand-written prose is realistic?** This sets the hero-circuit
   count and therefore most of the 3D scope.
5. **Is a CDN fallback (Cloudflare in front of Pages) acceptable,** or must it
   stay pure GitHub Pages? This decides how much telemetry can ship.

---

## Appendix — corrections carried into this spec

Facts that a reasonable person would have got wrong, caught during
verification. Recorded so they are not silently re-introduced:

- 2026 power units produce **~750 kW total** (400 kW ICE + 350 kW electrical),
  not 400 kW total. Downforce reduction is ~15%.
- The 2026 aero modes are **"Straight mode"** and **"Corner mode"**; the ERS
  boost is just **"Overtake"** (B7.2). "Overtake Override Mode" appears nowhere
  in the regulations.
- 2026 qualifying is Q1 18 min / 7 min break / Q2 15 min / 7 min break /
  **Q3 13 min** — a redline PDF makes the opposite reading look correct.
- The 2026 regulations are **six** sections (A–F), not three.
- Points: **1950–59 was 8-6-4-3-2 for the top five** plus a fastest-lap point;
  **1961–90 was 9-6-4-3-2-1**. The fastest-lap point returned in 2019 and was
  abolished again from 2025.
- The cost cap is **USD 215,000,000** (Section D **Issue 07**, 25 June 2026).
- Aerodynamic testing runs on **six unequal ATPs per year**, not two half-year
  periods; championship position refreshes once, after ATP 3.
- **jolpica collapses retirement causes from 2024**, not 2025.
- jolpica's custom User-Agent is a **policy request, not a technical
  requirement** — requests without one return 200.
- `session.results` has **22** columns, and there is no `DriverColor`.
- three.js: `RenderPipeline` renamed in **r183**; `Timer` is in **core**;
  `MeshoptDecoder` is in **`addons/libs/`**; `PCFSoftShadowMap` is deprecated.
- **Four** of Okabe-Ito's eight colours fail 3:1 on a light ground, not five.
- The W3C complex-image tutorial sanctions **three** approaches, not four.
- duckdb-wasm is **35–41 MB**, not 6–18 MB.
- The FT Visual Vocabulary is **MIT for the software only**; the poster is FT
  content, all rights reserved — it cannot be republished.
