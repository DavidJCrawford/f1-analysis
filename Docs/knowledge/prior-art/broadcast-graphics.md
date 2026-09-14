---
type: Reference
title: Broadcast graphics
description: F1 Insights powered by AWS and the official circuit pages — which metrics a mainstream audience already recognises, what can defensibly be cited, and why every visual property of broadcast graphics should be inverted here.
tags:
  - prior-art
  - broadcast
  - aws
  - f1-insights
  - design-reference
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: aws_f1
    resource: https://aws.amazon.com/sports/f1
    title: AWS — Formula 1 Insights
  - id: f1_braking
    resource: https://www.formula1.com/en/latest/article/braking-performance-first-of-six-new-f1-insights-powered-by-aws-graphics-set.5Ko3cyGoOoqkbgWVO5T1Nb
    title: Formula 1 — Braking Performance, first of six new F1 Insights graphics
  - id: svg_strategy_insight
    resource: https://www.sportsvideo.org/2026/07/24/f1-launches-strategy-insight-graphic-powered-by-aws-at-hungarian-grand-prix/
    title: SVG — F1 launches Strategy Insight graphic at the Hungarian Grand Prix
  - id: f1_strategy_insight
    resource: https://www.formula1.com/en/latest/article/f1-to-launch-new-strategy-insight-graphic-powered-by-aws-at-hungarian-grand-prix.3h211Yy2IaW04biHGRY4EM
    title: Formula 1 — Strategy Insight graphic announcement
  - id: f1_monaco_circuit
    resource: https://www.formula1.com/en/racing/2026/monaco/circuit
    title: formula1.com — Monaco circuit page
  - id: vizrt_sky
    resource: https://www.vizrt.com/demos/sky-germany-f1-ar-in-the-fast-lane/
    title: Vizrt — Sky Germany F1 AR
  - id: tata
    resource: https://www.tatacommunications.com/sports/powering-f1
    title: Tata Communications — powering F1
  - id: svg_sky
    resource: https://www.sportsvideo.org/2026/07/28/a-new-way-to-watch-how-formula-1-and-sky-sports-are-pushing-race-coverage-into-a-new-era/
    title: SVG — how Formula 1 and Sky Sports are pushing race coverage into a new era
status: stable
---

# Broadcast graphics

Broadcast is where most of the audience learns what an F1 metric *is*. That makes
it the most important vocabulary reference in this knowledge base and the worst
visual reference in it. The rule that follows is simple and holds throughout:
**reuse the metric definitions, invert every visual property.**

## 1. F1 Insights powered by AWS — the defensible list

AWS's own Formula 1 page names **16 insights**. That is the number to cite. Larger
counts circulate and could not be substantiated.

| # | Insight | Group |
| ---: | --- | --- |
| 1 | Battle Forecast | Race situation |
| 2 | Pit Strategy Battle | Strategy |
| 3 | Pit Window | Strategy |
| 4 | Predicted Pit Stop Strategy | Strategy |
| 5 | Undercut Threat | Strategy |
| 6 | Car Analysis / Car Development | Car |
| 7 | Close to the Wall | Car |
| 8 | Car Performance Scores | Car |
| 9 | Driver Performance | Driver |
| 10 | Driver Season Performance | Driver |
| 11 | Pit Lane Performance | Team execution |
| 12 | Braking Performance | Driver technique |
| 13 | Corner Analysis | Driver technique |
| 14 | Exit Speed | Driver technique |
| 15 | Tyre Performance | Tyres |
| 16 | AWS Lap Comparison | Comparison |

**Projected Knockout Time** is listed separately on the same page rather than
inside that set.

**Strategy Insight** was launched at the **2026 Hungarian Grand Prix** and is
documented in F1's and SVG's announcements rather than on the AWS insights page.
It is built on live timing, telemetry and predictive models and surfaces the
reasoning behind pit-wall decisions — tyre performance, pit windows, safety-car
risk and rival behaviour — calling out moments such as extending a stint or
answering an undercut threat.

### What cannot be cited

Three graphic names circulate in secondary write-ups and **do not appear on the
AWS page**: *Car Exploitation*, *Energy Usage* and *Alternative Strategy*. Their
descriptions could not be substantiated either. They are recorded here only so
that nobody reintroduces them as fact.

One description also needs correcting at source. Braking Performance is described
by AWS as **how a driver's braking style through a corner delivers an advantage on
exit** — not as a readout of braking points, speed at brake application, hardest
brakers, speed-decrease deltas and maximum g-forces. Those five quantities are all
computable from telemetry; they are simply not what that graphic is.

## 2. Which of these we implement, and where

The value of the list is that these metrics are **already understood by the
audience**, so a page that computes one honestly does not have to teach it from
scratch. The launch set maps as follows.

| Broadcast metric | Our equivalent | Status |
| --- | --- | --- |
| Undercut Threat | [Undercut / overcut delta](../metrics/undercut-delta.md) | In the launch set |
| Pit Lane Performance | [Pit loss time](../metrics/pit-loss-time.md) | In the launch set, per circuit |
| Tyre Performance | [Tyre degradation rate](../metrics/tyre-degradation-rate.md) | In the launch set |
| AWS Lap Comparison | Speed trace + delta panel | Telemetry tier |
| Corner Analysis, Exit Speed | Corner-by-corner order, mini-sector dominance | Telemetry tier |
| Battle Forecast, Predicted Pit Stop Strategy | — | **Not built.** Prediction is an explicit non-goal |
| Car Performance Scores, Driver Performance | — | **Not built** without visible uncertainty intervals and a named method |

The last two rows are the position on driver-versus-car decomposition stated in
[SPEC §7](../../SPEC.md): such metrics ship only with uncertainty made visible
and a named method, or not at all.

The one structural idea worth borrowing wholesale is **counterfactual framing** —
Strategy Insight and Pit Strategy Battle both answer "what would the other choice
have produced?". On a static page that becomes a designed comparison rather than
a live prediction: the stop that happened, against the stop the data says was
available, with the assumptions stated.

## 3. The official circuit page — the benchmark is low

`formula1.com/en/racing/2026/monaco/circuit` is the clearest demonstration that a
deep per-circuit page is unoccupied. The entire data payload is six facts:

| Field | Value |
| --- | --- |
| Circuit Length | 3.337 km |
| Number of Laps | 78 |
| Race Distance | 260.286 km |
| First Grand Prix | 1950 |
| Fastest Lap Record | 1:12.909, Lewis Hamilton (2021) |

The track map is a **static raster** — the asset is literally
`2026trackmontecarlodetailed.png`. An overhead illustration: not vector, not
interactive, not georeferenced, with no elevation and no sector or DRS annotation
in the graphic itself. The surrounding copy is short marketing prose.

Absent entirely: lap-record history, layout-evolution timeline, corner-by-corner
analysis, any speed trace, any comparison to other circuits, and any link from the
circuit to its own race archive. Each of those is a section of our circuit page.

## 4. Broadcast technical context

Two facts about the production chain are worth carrying because they bound what
the official position feed can possibly mean.

**Timing loops.** Vizrt AR drives Sky Germany's on-track graphics from timing data
produced by **40 timing loops placed at roughly 200 m intervals** around each
circuit. That spacing is the real resolution limit of the official
marshalling-sector position feed — useful whenever a claim about "where a car was"
is derived from loop crossings rather than from position telemetry.

**Connectivity.** Tata Communications has been the official broadcast connectivity
provider since 2012, moving 125+ video feeds and 250 audio channels to Biggin Hill
at sub-200 ms latency.

None of this output reaches the web as a durable artefact. It evaporates when the
broadcast ends, and F1 and Sky are pushing *harder* into AR and live data volume,
which deepens the asymmetry rather than closing it. The permanent, linkable,
still version of the same analysis is the opening.

## 5. The inversion table

Broadcast graphics are optimised for roughly four seconds of screen time against
moving footage. Every property that follows from that constraint is wrong for a
page you can sit with.

| Property | Broadcast | This site |
| --- | --- | --- |
| Lifetime | ~4 seconds, then gone | Permanent URL |
| Pacing | The director's | The reader's |
| Ground | Dark, over video | Light editorial paper, with dark instrument panels set into it |
| Colour | Gradients, glows, brand washes | Flat ink; colour reserved for data encoding |
| Motion | Sweeping entrances, constant animation | Chrome motion capped at 0.18 s; content motion user-initiated only |
| Type | Condensed, animated, all-caps | Typographic hierarchy carries the structure |
| Uncertainty | Hidden — a single confident number | Stated, with the method linked |
| Provenance | None on screen | Every derived figure links to its method page |
| Absence | Never shown | Designed copy explaining what is missing and why |

The motion split is a policy, not a preference — see
[Motion policy](../policies/motion-policy.md). The prohibition on gradient,
glow and status-chip treatments is enforced in
[Editorial voice](../policies/editorial-voice.md), which lists them among the
machine-generated defaults the site refuses.

## 6. What the audience already knows, and what that buys

The practical consequence of the 16-insight list is a vocabulary budget. Terms
like **undercut**, **pit window**, **tyre deg**, **pit-lane loss** and
**exit speed** need no glossary — a mainstream viewer has met them on screen.
Terms the broadcast does *not* use — clean-air race pace, fuel-corrected pace,
teammate delta — do need one, and they get a
[method page](../metrics/clean-air-race-pace.md) at `/methods/<slug>/` with the
formula and a worked example.

That is the trade this section exists to make explicit: **the broadcast has
already done the teaching, so the page can spend its words on the argument.**

## Related

- [Landscape](landscape.md)
- [Analysis tools](analysis-tools.md)
- [Undercut delta](../metrics/undercut-delta.md) · [Pit loss time](../metrics/pit-loss-time.md) · [Tyre degradation rate](../metrics/tyre-degradation-rate.md)
- [Motion policy](../policies/motion-policy.md) · [Editorial voice](../policies/editorial-voice.md)
- [Chart archetypes](../design/chart-archetypes.md)
