---
type: Reference
title: Reference Design Tokens (impeccable.style)
description: The verbatim design token system extracted from the project's aesthetic reference, impeccable.style, and the rules derived from it.
resource: https://impeccable.style/_astro/Base.BzPGTuBF.css
tags:
  - design
  - tokens
  - typography
  - color
  - motion
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: impeccable_base_css
    resource: https://impeccable.style/_astro/Base.BzPGTuBF.css
    title: impeccable.style compiled base stylesheet
  - id: impeccable_home
    resource: https://impeccable.style
    title: impeccable.style homepage
status: stable
---

# Reference Design Tokens

These values were read directly from the compiled stylesheet of
[impeccable.style](https://impeccable.style), the project's stated aesthetic
reference. They are recorded verbatim so that our own token set can be derived
deliberately rather than approximated by eye.

The reference site is built with **Astro**, which is corroborating evidence for
the site architecture decision recorded in
[/engineering/site-architecture.md](../engineering/site-architecture.md).

## Colour — OKLCH throughout

Every colour is authored in `oklch()`. No hex, no `rgb()`. This matters: OKLCH
gives perceptually-even lightness, which is what makes a 20-driver categorical
palette tractable (see
[/design/driver-color-encoding.md](driver-color-encoding.md)).

### Paper (the light ground)

| Token | Value |
| --- | --- |
| `--ks-paper` | `oklch(97.8% 0 0)` |
| `--ks-paper-raised` | `oklch(99.5% 0 0)` |
| `--ks-paper-deep` | `oklch(95% 0 0)` |
| `--ks-gray` | `oklch(92% 0 0)` |
| `--ks-gray-2` | `oklch(88% 0 0)` |

### Ink (text)

| Token | Value | Role |
| --- | --- | --- |
| `--ks-ink` | `oklch(13% 0 0)` | maximum-contrast ink |
| `--ks-text` | `oklch(22% 0 0)` | body text |
| `--ks-text-muted` | `oklch(46% 0 0)` | secondary |
| `--ks-text-faint` | `oklch(51% 0 0)` | tertiary |
| `--ks-text-mute-deep` | `oklch(66% 0 0)` | quaternary / disabled |
| `--ks-rule` | `oklch(13% 0 0/.08)` | hairline rules |
| `--ks-edge` | `oklch(13% 0 0/.45)` | hard edges |

Note the chroma is `0` for every neutral. The greys are *truly* neutral — no
warm or cool cast. Any tint we introduce is therefore a deliberate departure.

### Accents — only two, plus one alarm

| Token | Value | Notes |
| --- | --- | --- |
| `--ks-kinpaku` | `oklch(84% .19 80.46)` | *kinpaku* = gold leaf. Primary accent. |
| `--ks-kinpaku-vivid` | `oklch(87% .2 85)` | |
| `--ks-kinpaku-rich` | `oklch(77% .13 82)` | |
| `--ks-kinpaku-deep` | `oklch(61% .085 78)` | |
| `--ks-kinpaku-pale` | `oklch(86% .07 84)` | |
| `--ks-patina` | `oklch(70% .12 188)` | verdigris. Secondary / state. |
| `--ks-patina-deep` | `oklch(45% .1 190)` | also the focus ring |
| `--ks-patina-ink` | `oklch(41% .11 190)` | |
| `--ks-patina-pale` | `oklch(82% .07 188)` | |
| `--ks-vermilion` | `oklch(52% .16 35)` | reserved; alarm/negative only |

The palette is Japanese-influenced in naming and restraint: gold leaf and
verdigris against neutral paper. **Two accents carry the entire site.**

### Instrument — dark surfaces on a light page

| Token | Value |
| --- | --- |
| `--ks-instrument` | `oklch(24% 0 0)` |
| `--ks-instrument-deep` | `oklch(17% 0 0)` |
| `--ks-instrument-raised` | `oklch(31% 0 0)` |
| `--ks-instrument-text` | `oklch(93% 0 0)` |
| `--ks-instrument-muted` | `oklch(68% 0 0)` |
| `--ks-instrument-rule` | `oklch(100% 0 0/.12)` |
| `--ks-instrument-edge` | `oklch(100% 0 0/.3)` |

**This is the single most important finding for our project.** The reference
site has *no dark theme* — there is no `prefers-color-scheme: dark` block
anywhere in the stylesheet. Instead it has a dark **instrument surface family**
used for panels embedded in a light page, like a gauge cluster set into a
dashboard.

That is exactly the affordance a 3D circuit viewport needs: a dark WebGL canvas
does not have to fight a light page if it is framed as an *instrument*. See
[/design/three-d-art-direction.md](three-d-art-direction.md).

## Typography

Three families, loaded from Google Fonts:

```
Albert Sans:wght@400;500;600;700
Alumni Sans:wght@200..800        (variable)
JetBrains Mono:wght@400;500
```

| Token | Value |
| --- | --- |
| `--ks-font` | `"Albert Sans", "Avenir Next", "Helvetica Neue", Arial, system-ui, sans-serif` |
| `--ks-font-wordmark` | `"Alumni Sans", "Albert Sans", Arial, sans-serif` |
| `--ks-mono` | `"JetBrains Mono", ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace` |

### Scale

| Token | Size | Weight | Line | Tracking |
| --- | --- | --- | --- | --- |
| display | `clamp(3.2rem, 6.2vw, 5.6rem)` | `200` | `1` | `0` |
| headline | `clamp(2.4rem, 3.6vw, 3.4rem)` | `300` | `1.04` | `0` |
| title-lg | `1.5rem` | — | `1.35` | — |
| subhead | `1.25rem` | — | — | — |
| wordmark | `1.25rem` | — | — | `.18em` |
| lead | `1.125rem` | — | — | — |
| body | `1rem` | — | `1.65` | — |
| ui-lead | `.9375rem` | — | — | — |
| small | `.875rem` | — | — | — |
| ui | `.8125rem` | — | — | — |
| label | `.75rem` | — | — | — |
| eyebrow | `.6875rem` | — | — | `.14em` |
| micro | `.6875rem` | — | — | — |
| mono | `.6875rem` | — | — | `.12em` |

The signature move: **display and headline are ultra-light (200/300), while
small titles are semibold (600)**. Large type whispers, small type asserts.
Tracking is zero at display sizes and opens up dramatically at small sizes
(`.12em`–`.18em` for mono, eyebrow, wordmark).

### Gap we must close

The reference stylesheet contains **no `font-variant-numeric` declaration**.
It does not need one — it is a marketing site. We are a data site, and every
lap time, gap and position must align in a column. Our token set therefore
*adds*:

```css
--f1-numeric: tabular-nums lining-nums;
```

applied to every table cell, axis label, timing readout and telemetry value.
Albert Sans and JetBrains Mono both ship tabular figures.

## Space, radius, shadow

| Token | Value |
| --- | --- |
| `--ks-radius-sm` | `3px` |
| `--ks-radius-md` | `8px` |
| `--ks-radius-pill` | `999px` |
| `--ks-code-radius` / `--ks-code-block-radius` | `3px` |
| `--ks-section-pad` | `clamp(72px, 8vw, 120px)` |
| `--ks-control-sm` / `md` / `lg` | `26px` / `32px` / `44px` |

Radii are tiny. `3px` is the default; `8px` is for cards only. Nothing is
soft-cornered by default — this is a large part of why the site does not read
as generic.

Elevation is layered and extremely subtle:

```css
--ks-lift-1: 0 1px 1px oklch(13% 0 0/.05), 0 2px 3px oklch(13% 0 0/.04), 0 6px 12px oklch(13% 0 0/.05);
--ks-lift-2: 0 1px 1px oklch(13% 0 0/.04), 0 3px 5px oklch(13% 0 0/.05), 0 12px 20px oklch(13% 0 0/.06), 0 32px 48px oklch(13% 0 0/.07);
```

Physical-control shadows exist for buttons and tracks, reinforcing the
instrument metaphor:

```css
--ks-cap-lift:     inset 0 1px 0 oklch(100% 0 0/.9), 0 1px 0 oklch(13% 0 0/.14), 0 2px 3px oklch(13% 0 0/.08);
--ks-cap-press:    inset 0 1px 2px oklch(13% 0 0/.14);
--ks-track-recess: inset 0 1px 3px oklch(13% 0 0/.16), inset 0 -1px 0 oklch(100% 0 0/.7);
--ks-led:          0 0 0 1px oklch(13% 0 0/.12), 0 0 4px oklch(84% .19 80/.6);
```

There is also a grain overlay — an inline SVG `feTurbulence` at
`baseFrequency="0.9"`, `numOctaves="2"`, desaturated via `feColorMatrix` — in
`--ks-grain`. It is what keeps flat paper from looking sterile.

## Motion

| Token | Value |
| --- | --- |
| `--ks-quick` | `.12s` |
| `--ks-settle` | `.2s` |
| `--ks-ease` | `cubic-bezier(.2, .8, .2, 1)` |

Every transition found in the compiled CSS falls between **`.12s` and `.18s`**,
and all of them use the single shared easing curve. There is no transition
longer than `.2s` anywhere on the site. Documented interaction specs are
`hover · lift 1px · 150ms` and `press · 160ms · scale .96`.

`prefers-reduced-motion: reduce` is honoured, but narrowly — it disables
specific component transitions rather than globally killing animation.

**Tension to resolve.** A 0.18s motion ceiling is a UI rule, not a
cinematography rule. A camera flying a lap of Spa cannot obey it. Our
resolution, recorded in [/policies/motion-policy.md](../policies/motion-policy.md):
the ceiling binds all *chrome* (buttons, panels, tooltips, page transitions)
absolutely; *content* motion inside an instrument frame — camera moves, car
animation, scrubbing — is exempt but must be user-initiated or user-scrubbable,
never idle-looping, and must collapse to a static frame under
`prefers-reduced-motion`.

## Layout

- Container max width **`1320px`**, on a **12-column** grid
  (`repeat(12, minmax(0, 1fr))`).
- Prose measures are capped at **`60ch`** and **`82ch`**.
- Narrow content blocks cluster at `280px`, `360px`, `420px`, `440px`, `460px`,
  `720px`.

## Stated principles

From the site's own copy:

> Calm by default. One action per screen. Never hide the seat count.

It names a category of anti-pattern it calls **"AI tells"** — the defaults that
mark a page as machine-generated. Those it calls out include italic serif
pull-quotes, beige palettes, and ubiquitous status chips. Our own prohibition
list is derived from this in
[/policies/editorial-voice.md](../policies/editorial-voice.md).

## How we diverge, deliberately

1. **We add tabular figures.** Non-negotiable for timing data.
2. **We add a categorical data palette.** Two accents cannot encode 20 drivers.
   The accents stay reserved for interface meaning; driver identity uses a
   separate, explicitly-scoped scale.
3. **We use the instrument family far more heavily,** because 3D viewports and
   telemetry readouts live there.
4. **We keep the motion ceiling for chrome and break it only inside
   instruments,** under the policy above.
