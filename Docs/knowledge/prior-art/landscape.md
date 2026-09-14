---
type: Reference
title: Prior-art landscape
description: The map of existing F1 data and visualisation work, the live-timing versus notebook split that divides it, and the precise gap this project occupies.
tags:
  - prior-art
  - competitive-analysis
  - positioning
  - f1
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1dash_repo
    resource: https://github.com/slowlydev/f1-dash
    title: slowlydev/f1-dash — repository
  - id: f1dash_site
    resource: https://f1-dash.com/
    title: f1-dash.com — sunset announcement
  - id: awesome_f1
    resource: https://github.com/subinium/awesome-f1
    title: subinium/awesome-f1 — curated motorsport resource list
  - id: pitwall
    resource: https://pitwall.app/
    title: Pitwall.app
  - id: f1cosmos
    resource: https://f1cosmos.com/
    title: F1 Cosmos
  - id: tracinginsights
    resource: https://tracinginsights.com/
    title: TracingInsights
  - id: armchair
    resource: https://github.com/Casper-Guo/Armchair-Strategist
    title: Casper-Guo/Armchair-Strategist
  - id: minisector_repo
    resource: https://github.com/lennyocbot/minisector
    title: lennyocbot/minisector
  - id: f1tml
    resource: https://github.com/yashyegare/F1TrackMetricsLab
    title: yashyegare/F1TrackMetricsLab
  - id: f1_guidelines
    resource: https://www.formula1.com/en/information/guidelines.4EOKE9RRqevL4niTK9kWyt
    title: Formula 1 — fan-site guidelines
  - id: gh_topic_f1telemetry
    resource: https://github.com/topics/f1-telemetry
    title: GitHub topic — f1-telemetry
status: stable
---

# Prior-art landscape

The F1 open-data visualisation space is crowded and lopsided. Counting projects
makes it look saturated; reading them shows almost every one sits at one of two
poles, and that the position this project takes is between them and empty.

## 1. The two poles

**Pole A — the live-timing dashboard.** Its unit of value is *now*. It exists to
be watched during a session: leaderboard, gaps, mini-sector colours, tyre chips,
a replay scrubber. It has no archive worth the name, no page per entity, no
prose, and no permanent URLs — the state is in a dropdown or a websocket, not in
the address bar. f1-dash, F1 Cosmos, F1ReplayTiming, Formula Live Pulse and
MultiViewer all live here.

**Pole B — the notebook surface.** Its unit of value is *the chart*. It is a
Python or R analysis pipeline given a web front end, usually Dash/Plotly or a
static image gallery. It is often methodologically excellent and visually
default: matplotlib chrome, library tick densities, a three-dropdown gate before
any content appears. FastF1's own example gallery, Armchair Strategist,
TracingInsights, The Field and F1 Data Junkie live here.

Both poles share a structural property that matters more than their aesthetics:
**nothing on either side is addressable**. You cannot link a friend to the 1976
Japanese Grand Prix, or to Monza, or to Tyrrell. The content is generated on
demand from a selector and evaporates.

## 2. The field, by class

| Class | Named members | Licence / stack where known | Has | Lacks |
| --- | --- | --- | --- | --- |
| Live timing | f1-dash; pitwall fork (ignaciohaffner); F1ReplayTiming; Formula Live Pulse; F1 Cosmos | f1-dash: **AGPL-3.0**, Rust + Next.js | Real-time feel, mini-sector colour, tyre chips | Archive, entity pages, 3D, prose |
| Analysis tools | [TracingInsights, Armchair Strategist, F1 Data Junkie, The Field](analysis-tools.md); gp-tempo; F1Dash (FraserTarbet); f1-viz | Armchair: **Apache-2.0**, Dash + Plotly + FastF1 | Chart breadth, published method | Static hosting, permanence, design |
| Reference / encyclopaedia | pitwall.app; formula1archive.com; bigdataf1.com; oldracingcars.com; f1metrics; formula1points.com; 4mula1stats.com | mostly closed | Coverage, entity page types | Design identity, 3D, analysis depth |
| Asset repositories | F1DB; julesr0y/f1-circuits-svg; bacinger/f1-circuits; TUMFTM/racetrack-database | CC BY 4.0 / MIT / LGPL-3.0 | Clean, redistributable data | They are not sites |
| 3D and data art | [F1TrackMetricsLab; F1-RACEREPLAY; webtrack; f1-sculptures](three-d-prior-art.md) | MIT where stated | Proof the geometry pipeline works | Adoption, polish, editorial framing |
| Static editorial | [lennyocbot/minisector](minisector.md) | 1 star, 6 weeks old at time of survey | Static GitHub Pages, zero dependencies, hand-rolled SVG | Editorial voice, entity pages, 3D |

### The dashboard that is leaving the browser

f1-dash is the dominant open-source entry — **1,909 stars, 264 forks, 24 open
issues, 1,186 commits**, AGPL-3.0, a Rust + Next.js monorepo whose top-level
folders are `.github`, `.k8s`, `api`, `dashboard`, `realtime`, `shared`,
`signalr`, `simulator`. Its README tagline: "A real-time F1 dashboard that shows
the leader board, tires, gaps, laps, mini sectors and much more."

Two precise facts about its status, because the obvious reading is wrong. The
repository is **not archived and carries no deprecation notice**; the sunset
announcement lives only on f1-dash.com, and it says the project "remains
available as open source for self-hosting" with maintenance and security updates
continuing. What is retiring is the *hosted web service*, in favour of a
cross-platform desktop app, Nitrous — which has no public repository on the
maintainer's profile. The strategic reading is therefore not "the leader is
dying" but **"the leader is vacating the browser"**, which is where this project
lives.

Its licence is the operative constraint for us: AGPL-3.0 is a network copyleft.
Nothing from it may be copied into this codebase. See
[Reference materials](reference-materials.md#4-reuse-posture-by-source).

## 3. The four-axis scorecard

Four properties define the position. Every competitor was scored against them.

- **(a) Static and permanently linkable** — prerendered HTML, URLs that never
  break, no server.
- **(b) A page per circuit *and* per team *and* per race** — entity pages, not a
  query interface.
- **(c) Real 3D geometry** — a track built from measured centreline and
  elevation, not a silhouette.
- **(d) An authored editorial design system** — one point of view, carried by
  typography.

| Project / class | a | b | c | d | Score |
| --- | :-: | :-: | :-: | :-: | --- |
| f1-dash · Nitrous · Formula Live Pulse · F1 Cosmos | — | — | — | — | **0 / 4** |
| TracingInsights · Armchair Strategist · gp-tempo · F1Dash · f1-viz | — | — | — | — | **0 / 4** |
| pitwall.app | partial | ✓ | — | — | **1.5 / 4** |
| F1TrackMetricsLab | — | partial | ✓ | — | **1.5 / 4** |
| f1-circuits-svg · F1DB | ✓ | partial | — | — | **1.5 / 4** (asset repos, not sites) |
| lennyocbot/minisector | ✓ | — | — | — | **1 / 4** |
| formula1.com official | — | ✓ | — | ✓ | **2 / 4**, deliberately shallow |

Nobody exceeds 2 of 4, and the two that reach it do so on disjoint axes.

**Caveat on pitwall.app.** It is the closest thing to an encyclopaedia: page
types Home, Seasons, Races, Drivers, Teams, Circuits, Records and Analysis;
results 1950–2026; lap-level data from 1996. It also carries the *full* required
F1 trademark disclaimer, not the short form — a useful precedent that a
comparable fan site complies with the complete string from the fan-site
guidelines. Its Circuits section is a stats listing, not an analysis page.

## 4. The gap, stated

> A fully prerendered static site on GitHub Pages where every circuit, every team
> and every race is a permanent URL and a designed page; where the circuit page's
> focal moment is a real three.js track at declared scale; where the charts are
> bespoke reimplementations of proven idioms rather than library defaults; and
> where restraint is the differentiator, because every competitor is a dark
> dashboard with a theme switcher.

Three things make this defensible rather than merely unoccupied.

1. **Static is a moat, not a compromise.** Every tool in the analysis class needs
   a live Python server. A precomputed site is faster, free to host, permanently
   linkable, and cannot go down when the maintainer stops paying.
2. **Compliance is part of the moat.** F1's fan-site guidelines permit
   "individual pieces of the data ... incidentally within editorial material to
   genuinely inform" but not reproduction of "substantial pieces". An editorial
   site with derived analysis is better positioned than a bulk data mirror, and
   the licence discipline in [Source roles](../policies/source-roles.md) is what
   keeps it there.
3. **The archival tier is the real differentiator.** Roughly 85% of races have no
   telemetry. Every competitor either starts at 2018 (FastF1's boundary) or 2023
   (OpenF1's), or shows tables for the rest. Being genuinely good at 1962 is the
   part nobody has attempted — see [SPEC §4.2](../../SPEC.md).

## 5. Anti-patterns, each tied to an observed behaviour

| Prohibited | Because it was observed at |
| --- | --- |
| Theme switcher | TracingInsights ships four themes (Default, Luxury, Dim, Synthwave) — a site with four looks has no view |
| Dropdown gate before any content | TracingInsights, gp-tempo: year → event → session before a pixel of data |
| Dark-by-default dashboard | Every competitor in the live and analysis classes |
| Neon gradients, glow, sweeping motion | Broadcast AR overlays — see [Broadcast graphics](broadcast-graphics.md) |
| Reproducing the FastF1 gallery plots in default styling | The single strongest "seen it before" signal in the field |
| Configurable widget layouts | F1 Cosmos: "resizable widgets and customizable layouts" |
| Command palette as a headline feature | F1TrackMetricsLab leads with ⌘K |

These are enforced editorially in [Editorial voice](../policies/editorial-voice.md)
and visually in [Chart archetypes](../design/chart-archetypes.md).

## 6. Benchmarks to clear

Positioning is not a licence to be worse at the things the field is good at.

| Benchmark | Held by | Bar |
| --- | --- | --- |
| Chart breadth | TracingInsights | 30+ named analyses |
| Published taxonomy | The Field | ~30 archetypes with axes and encodings specified |
| Charting in plain SVG | minisector | 225-line kernel, 3,726-line `src/`, zero runtime dependencies |
| Method transparency | Armchair Strategist | Documented `SCHEMA.md`, named fuel model |
| Historical coverage | pitwall.app | 1950–2026 results, lap data 1996+ |
| Geometry pipeline | F1TrackMetricsLab | OpenF1 telemetry → 3D ribbon, 40 circuits, end to end |

## 7. Monitoring, and what the monitoring is worth

`subinium/awesome-f1` is the only curated index found. Treat it as one useful
pointer list, not an authority: it has **38 stars**, is recently started, and is
**not F1-specific** — F1 is section 1 of 14, alongside F2/F3, Formula E,
WEC/IMSA, WRC, MotoGP, NASCAR, IndyCar, sim racing and media. Its F1 subsections
include APIs and Libraries; Datasets and Telemetry Archives; Live Timing;
Dashboards and Analytics (Web Platforms vs Open Source); Historical and
Statistics; Archived Projects; Junior and Feeder Series Media; Official Session
Sources. Its *Archived Projects* section is the most useful part — RaceControl,
f1viewer and f1ml are all dead — because it shows which categories churn.

Second monitoring target: the migration of f1-dash's audience to a desktop app.
That migration vacates the browser.

## 8. Honesty about the negative claim

The strong form of the finding — "no credible, polished three.js F1 circuit
project exists" — **is not provable from the evidence gathered**. The GitHub
`f1-telemetry` topic is effectively unused, so absence there is not evidence of
absence generally, and the survey's search budget was exhausted before a broad
sweep could run. What *is* established is narrower and still sufficient: every
3D F1 project actually located is hobby-scale, game-shaped, or renders offline.
See [3D prior art](three-d-prior-art.md), which states that in detail.

The same discipline applies to two data-art references (Nicolas Penco's poster
series, and a G-force "sculpture" repository) that could not be retrieved: they
are recorded as unverified and are not used as evidence for anything.

## Related

- [minisector](minisector.md) — the nearest neighbour by brief, in detail
- [3D prior art](three-d-prior-art.md)
- [Analysis tools](analysis-tools.md)
- [Broadcast graphics](broadcast-graphics.md)
- [Reference materials](reference-materials.md)
- [Data licensing](../policies/data-licensing.md)
- [Site architecture](../engineering/site-architecture.md)
