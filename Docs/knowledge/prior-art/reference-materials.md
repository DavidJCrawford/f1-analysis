---
type: Reference
title: Design and chart-vocabulary reference materials
description: The external design canon this project draws on — Tufte, the Swiss school, Rams and the FT Visual Vocabulary — with the licence position on each, including the one that cannot be republished.
tags:
  - design-canon
  - data-visualisation
  - chart-selection
  - typography
  - licensing
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: ft_chart_doctor
    resource: https://github.com/Financial-Times/chart-doctor/tree/main/visual-vocabulary
    title: Financial-Times/chart-doctor — Visual Vocabulary
  - id: ft_vv_web
    resource: http://ft-interactive.github.io/visual-vocabulary/
    title: FT Visual Vocabulary — web version
  - id: vitsoe_rams
    resource: https://www.vitsoe.com/gb/about/good-design
    title: Vitsœ — Dieter Rams' ten principles for good design
  - id: its_wikipedia
    resource: https://en.wikipedia.org/wiki/International_Typographic_Style
    title: International Typographic Style
  - id: mb_grid
    resource: https://en.wikipedia.org/wiki/Josef_M%C3%BCller-Brockmann
    title: Josef Müller-Brockmann
  - id: chartjunk_study
    resource: https://arxiv.org/abs/2009.02634
    title: Evaluating 'Graphical Perception' with CNNs / chartjunk counter-evidence
status: stable
---

# Design and chart-vocabulary reference materials

The external canon behind the chart and page layer. This document exists for
two reasons: to name the sources so the design decisions in
[chart-archetypes](../design/chart-archetypes.md) and
[layout-and-grid](../design/layout-and-grid.md) are not arbitrary, and to
record the **licence position** on each, because one of the most useful items
here cannot legally be republished.

## Licence summary — read this first

| Material | Licence | May we reproduce it? |
| --- | --- | --- |
| FT Visual Vocabulary **poster/PDFs** | **FT content, all rights reserved** | **No** |
| FT `chart-doctor` **code** | MIT | Yes, with attribution |
| Tufte's principles | Ideas, not copyrightable; text is | Paraphrase and short quotes only |
| Rams' ten principles | Vitsœ publishes the text | Short quotes with attribution |
| Swiss-style canon | Historical; specific texts in copyright | Paraphrase |

### The FT Visual Vocabulary trap

The Visual Vocabulary is the most directly useful chart-selection reference in
existence, and it is **commonly and wrongly described as CC-licensed** — this
project's own first-pass research made exactly that error.

The truth, from the repository's root README: the MIT licence "includes only
the software, and does not cover any FT content made available using the
software, which is copyright © The Financial Times Limited, all rights
reserved."

The poster is FT content. **It may be used as a private reference and it may be
linked. It may not be reproduced, redistributed, adapted into our own poster,
or embedded in the site.** Republishing requires contacting FT syndication.

What we *can* take is the **taxonomy** — the idea that charts sort into
relationship categories is not itself ownable, and we can build our own
selection guide on the same logic in our own words and our own visual language.

## 1. The FT taxonomy, and how our charts map to it

Nine categories, from the repository's section headings: **Deviation,
Correlation, Ranking, Distribution, Change over Time, Part-to-whole, Magnitude,
Spatial, Flow** — with further sections on Uncertainty, Animation,
Interactivity, Map projections and Colour.

Mapping our archetypes onto it is a useful check that we have not left a
relationship type unserved:

| Our chart | FT category | Note |
| --- | --- | --- |
| Gap to leader | Deviation | Reference point is the leader, not zero |
| Race trace | Deviation | Reference is a constant notional lap |
| Qualifying teammate delta | Deviation | Classic diverging bar |
| Lap/position chart | Ranking + Change over Time | Rare genuine hybrid |
| Stint Gantt | Change over Time + Part-to-whole | |
| Tyre degradation scatter | Correlation | With an explicit fitted model |
| Championship swing | Change over Time | |
| Mini-sector dominance | Spatial | Our only true spatial encoding in 2D |
| Pit-loss by circuit | Magnitude | |
| Reliability / DNF causes | Part-to-whole | Constrained by the 2024+ source problem |
| Constructor lineage | Flow | Merges and renames as a flow over time |

Two gaps this exposes and we accept: we have no **Distribution** chart at
launch (lap-time distributions are a natural phase-2 addition), and our
**Uncertainty** story is deliberately thin — see
[driver-car-decomposition](../metrics/driver-car-decomposition.md), where the
policy is to publish only with visible intervals or not at all.

## 2. Tufte — the quantitative canon

The operative definitions, for use in review:

- **Data-ink** — "the non-erasable core of a graphic, the non-redundant ink
  arranged in response to variation in the numbers represented."
- **Data-ink ratio** = data-ink ÷ total ink; equivalently `1 −` the proportion
  of the graphic that can be erased without losing data-information.
- **The five principles** (*The Visual Display of Quantitative Information*,
  1983): above all else show data; maximize the data-ink ratio; erase non-data
  ink; erase redundant data-ink; revise and edit. Both erasing principles are
  qualified **"within reason"** — that qualification is Tufte's own and is
  routinely dropped by people quoting him.
- **Chartjunk** — "ink that does not tell the viewer anything new."
- **Lie Factor** = (size of effect shown in graphic) ÷ (size of effect in
  data). Tufte's honest band is **0.95 to 1.05**. His canonical example is a
  53% numerical change drawn as a 783% graphical change — Lie Factor 14.8.
- **Small multiples** — "illustrations of postage-stamp size … indexed by
  category or a label, sequenced over time like the frames of a movie, or
  ordered by a quantitative variable not used in the single image itself."
- **Sparklines** — "datawords: data-intense, design-simple, word-sized
  graphics."

### Applying it as a default, not a law

There is real counter-evidence. Empirical work has found that memorable,
lightly-embellished charts can outperform maximally-austere ones on recall,
and practitioner surveys are not uniformly on Tufte's side. We therefore treat
data-ink as **a strong default with a burden of proof to depart from it**, not
a rule — which is also the honest position given that this project's entire
aesthetic is austere by choice, and we should know that is a choice.

Where Tufte binds us concretely:

- Axes and gridlines are **1px hairlines at 8–12% ink opacity**.
- **No boxed plot frames.** Despine left and bottom.
- No gradient fills on data marks, no glow, no drop shadows on data.
- **Lie Factor 1.0 is mandatory**: no truncated bar-chart baselines, ever. The
  one sanctioned non-linear axis on the site is the **sqrt compression on
  gap-to-leader**, which is declared in the caption every time it is used.

## 3. The Swiss school — the structural canon

From the International Typographic Style: designs begin with "a mathematical
grid, because a grid is the 'most legible and harmonious means for structuring
information.'" Layouts are asymmetric; text is set **flush left, ragged
right**; sans-serif is preferred. Canonical faces are Akzidenz-Grotesk, Univers
(1950s), and Neue Haas Grotesk — renamed Helvetica by Max Miedinger and Eduard
Hoffmann.

Its notion of **objective photography** — imagery "meant to present information
clearly, and without any of the persuading influences of propaganda or
commercial advertising" — is worth noting precisely because
[data-licensing](../policies/data-licensing.md) establishes that **we will have
no photography at all**. The Swiss answer to a page without images is grid,
rule and type doing the work, which is exactly the constraint we are under.

**A sourcing caution.** Müller-Brockmann's *Grid Systems in Graphic Design*
(Niggli, 1981, ISBN 3721201450) is frequently cited for a specific "8 to 32
fields" range. That figure is **not** in the encyclopaedia articles usually
given as the source for it. If we use it, cite the book directly — do not
repeat it second-hand.

His caveat is the quotable one, and it applies directly to a design system:

> The grid system is an aid, not a guarantee.

## 4. Rams — the restraint argument

Ten principles, published by Vitsœ. Three bear directly on decisions this
project faces:

- **Good design is unobtrusive** — "their design should therefore be both
  neutral and restrained, to leave room for the user's self-expression." This
  is the argument for reserving colour for data and refusing it to interface
  decoration.
- **Good design is honest** — "it does not make a product more innovative,
  powerful or valuable than it really is." This is the argument behind
  [provenance-and-staleness](../policies/provenance-and-staleness.md): a
  provisional classification says so, and a missing dataset is stated rather
  than disguised.
- **Good design is long-lasting** — "it avoids being fashionable and therefore
  never appears antiquated." This is why the site is an encyclopaedia with
  permanent URLs rather than a dashboard, and why glassmorphism, gradient text
  and neon-on-black are prohibited in
  [editorial-voice](../policies/editorial-voice.md).

## 5. Deliberate non-imitation: the FastF1 gallery

A different kind of reference — one to move **away** from.

FastF1's documentation gallery ships exactly **16 canonical examples**, and
they define the visual vocabulary that the entire F1-analysis community
reproduces: TracingInsights, Armchair Strategist, and an enormous volume of
Medium and Kaggle output all render them near-identically, because they are
matplotlib defaults in team colours.

**Producing any of those sixteen in their default form is the single strongest
"seen it before" signal available to this project.** The gallery is therefore
treated as a list of chart types to deliberately redesign, not to reproduce.

Two ideas in it are genuinely worth taking: *"Draw a track map with numbered
corners"* and *"Speed visualization on track map"* — both are spatial
encodings, both are good ideas, and both are rendered in a way we should not
copy. See [analysis-tools](analysis-tools.md) for the full survey and
[minisector](minisector.md) for the nearest neighbour that got it right.

## 6. Library position

For completeness, since chart-library choice is downstream of this canon:
current versions at time of writing are three 0.186.0, d3 7.9.0 and Observable
Plot 0.6.17.

The project uses **an in-house SVG kernel** rather than a charting library.
minisector demonstrates every archetype here in plain SVG in ~225 lines of
charting code. A library's opinionated defaults — tick density, label
placement, tooltip chrome — are precisely what would be spent effort
overriding, and the aesthetic bar cannot be met by restyling. **d3 is used for
scales and shape generators only** (`d3-scale`, `d3-shape`, `d3-array`), where
its value is high and its visual footprint is zero. three.js is reserved
strictly for 3D and never used for 2D charts.
