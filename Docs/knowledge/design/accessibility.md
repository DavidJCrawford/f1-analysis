---
type: Reference
title: Accessibility
description: The WCAG 2.2 AA targets this site conforms to, with the chart table fallbacks, canvas text alternatives, keyboard 3D and focus behaviour that satisfy them.
tags:
  - accessibility
  - wcag
  - charts
  - webgl
  - keyboard
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: wcag22
    resource: https://www.w3.org/TR/WCAG22/
    title: Web Content Accessibility Guidelines 2.2
  - id: wcag_non_text_contrast
    resource: https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
    title: WCAG 2.2 Understanding SC 1.4.11 Non-text Contrast
  - id: wcag_use_of_color
    resource: https://www.w3.org/WAI/WCAG22/Understanding/use-of-color.html
    title: WCAG 2.2 Understanding SC 1.4.1 Use of Color
  - id: wcag_target_size
    resource: https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
    title: WCAG 2.2 Understanding SC 2.5.8 Target Size (Minimum)
  - id: wcag_focus_appearance
    resource: https://www.w3.org/WAI/WCAG22/Understanding/focus-appearance
    title: WCAG 2.2 Understanding SC 2.4.13 Focus Appearance
  - id: w3c_complex_images
    resource: https://www.w3.org/WAI/tutorials/images/complex/
    title: W3C WAI Tutorial — Complex Images
  - id: whatwg_canvas
    resource: https://html.spec.whatwg.org/multipage/canvas.html#the-canvas-element
    title: WHATWG HTML — the canvas element
  - id: aria_graphics
    resource: https://www.w3.org/TR/graphics-aria-1.0/
    title: WAI-ARIA Graphics Module 1.0
  - id: threejs_orbitcontrols
    resource: https://threejs.org/docs/pages/OrbitControls.html
    title: three.js — OrbitControls
  - id: mdn_forced_colors
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors
    title: MDN — @media (forced-colors)
  - id: wcag3_wd
    resource: https://www.w3.org/TR/wcag-3.0/
    title: WCAG 3.0 Working Draft
status: stable
---

# Accessibility

**The target is WCAG 2.2 Level AA.** Conformance levels are stated precisely
throughout this page, because conflating an AA requirement with a AAA
aspiration is the most common way an accessibility statement becomes untrue.

A data site has an unusually high proportion of its meaning in non-text
content. That is why the charts and the 3D scene get most of the space below,
and why the table fallback is treated as a first-class output of the chart
kernel rather than an afterthought.

## 1. Criteria in scope, with levels

| SC | Name | Level | What it binds here |
| --- | --- | --- | --- |
| 1.4.1 | Use of Color | **A** | Every chart series, tyre compound, sector state |
| 1.4.3 | Contrast (Minimum) | **AA** | All text, including chart labels and figures |
| 1.4.11 | Non-text Contrast | **AA** | Every line in a graph, marker, axis, chip, control, focus ring |
| 2.2.2 | Pause, Stop, Hide | **A** | Any auto-playing replay |
| 2.3.1 | Three Flashes | **A** | Sector-state and indicator changes |
| 2.4.11 | Focus Not Obscured (Minimum) | **AA** | Sticky headers over the 3D viewport |
| 2.4.13 | Focus Appearance | **AAA** | Aspirational; not part of the conformance claim |
| 2.5.8 | Target Size (Minimum) | **AA** | Corner hotspots, scrubber handles, legend chips |
| 2.3.3 | Animation from Interactions | AAA | Aspirational |

**SC 2.4.11 and SC 2.4.13 are not one requirement.** 2.4.11 (Focus Not
Obscured, Minimum) is AA and required: *"When a user interface component
receives keyboard focus, the component is not entirely hidden due to
author-created content."* 2.4.13 (Focus Appearance) is AAA and aspirational.

## 2. Contrast

| Content | Ratio | SC |
| --- | ---: | --- |
| Normal text | 4.5:1 | 1.4.3 (AA) |
| Large text — 18pt or 14pt bold, approximately 24px / 18.5px | 3:1 | 1.4.3 (AA) |
| Graphical objects required to understand the content | 3:1 | 1.4.11 (AA) |
| User interface components | 3:1 | 1.4.11 (AA) |

SC 1.4.11's Understanding document defines graphical objects as *"stand-alone
icons such as a print icon (with no text), and the important parts of a more
complex diagram such as **each line in a graph**."* That sentence puts every
telemetry trace, lap-delta line, bar, sector swatch, compound chip, racing line
and driver marker in scope. A 1px hairline in a pale team colour on a warm
off-white page is a direct failure — which is exactly what five of the eleven
2026 liveries are. See [Driver colour encoding](driver-color-encoding.md).

Exceptions worth knowing precisely, because one of them is genuinely useful
here: inactive or disabled components; graphics where *"a particular
presentation of graphics is essential to the information being conveyed"*
(logos, flags, photographs, **heat maps**); graphics with an equivalent text
alternative already provided; purely decorative graphics; and components whose
appearance is determined by the user agent. The heat-map carve-out legitimises
a continuous circuit-speed gradient. **It does not legitimise a categorical
series palette.**

Text that is part of a logo or brand name has no contrast requirement — so a
constructor wordmark is exempt, and a team-coloured statistic is not.

The arithmetic, the formula and the WCAG 3 / APCA status are in
[Colour system](color-system.md) §5. Two additions from the 10 September 2026
Working Draft worth recording: the WCAG 3 text-appearance requirement
*"assumes the algorithm will include a size/weight factor"*, and *"a separate
requirement may be needed if red/green color vision deficiency (CVD) is not
accounted for within the contrast algorithm."* The second sentence is the W3C
conceding the exact gap this site measures empirically — Ferrari, Audi and
McLaren all pass contrast and all collapse to the same olive under
deuteranopia.

## 3. Colour is never the only encoding

SC 1.4.1, Level A, verbatim: *"Color is not used as the only visual means of
conveying information, indicating an action, prompting a response, or
distinguishing a visual element."* The W3C's own failure example is a chart
whose series are distinguished only by colour.

Applied concretely:

| Element | Redundant channel |
| --- | --- |
| Lap-time trace | Three-letter driver code at the line end, plus dash for the team-mate |
| Scatter series | Marker shape |
| Constructor standings bar | Team name printed in or beside the bar |
| Tyre stint block | Compound letter — S / M / H / I / W — printed on the block |
| Sector timing cell | Cell state as text, and luminance separation, not hue alone |
| Track dominance segment | The dominance table below, listing segments won |

## 4. Charts: the table fallback

Every chart on this site has a real `<table>` fallback. This is not optional
and it is not generated on demand.

The W3C Complex Images tutorial sanctions **three** approaches — not four:

1. A text link to the long description adjacent to the image.
2. Describing the location of the long description in the `alt` attribute.
3. Structurally associating the image and its adjacent long description.

Approach 3 is our default. A fourth technique people reach for —
`aria-describedby` pointing elsewhere on the page — *"only works for long
descriptions that are text-only, without needing structural information"*, so
it is the wrong choice for tabular race data.

The tutorial's shape, which we follow:

```html
<figure role="group">
  <svg role="img" aria-label="Race trace, 2024 British Grand Prix — described in detail below.">…</svg>
  <figcaption>
    <h3>Overview</h3>
    <p>Reference pace is the winner's clean-lap median of 1:29.412. Flat is that
       pace; a vertical drop is a pit stop or a neutralisation.</p>
    <details>
      <summary>View as table</summary>
      <table>
        <caption>Delta to reference pace, seconds, by lap and driver</caption>
        …
      </table>
    </details>
  </figcaption>
</figure>
```

The two-part text alternative is the requirement: *"the first part is the short
description to identify the image and, where appropriate, indicate the location
of the long description."*

Rules that follow:

- **Keep the table in the DOM**, inside `<details>` or visually hidden — never
  built on demand — so find-in-page and copy-paste work.
- The table contains **the exact rows that drew the chart**, not a summary.
- The prose in the `figcaption` states what the chart shows and what its
  assumptions were: reference lap, excluded laps, fuel coefficient,
  mini-sector count.
- The SVG carries `role="img"` and a descriptive `label`.

### Telemetry is the open case

Car telemetry samples at a few hundred hertz. A raw table of that is not a text
alternative, it is a denial of service. The summarisation rule is **not yet
defined** and is recorded here as an open item: some form of per-corner
aggregate — entry, apex and exit speed, minimum speed, gear, brake point — is
the likely shape, but the exact schema is unverified. Whether sonification is
worth building for lap-time deltas is likewise undecided.

## 5. Canvas and WebGL

Canvas pixels are not in the DOM and carry no semantics. Assistive technology
sees nothing. The HTML specification is explicit about the obligation: authors
*"must also provide content that, when presented to the user, conveys
essentially the same function or purpose as the canvas's bitmap. This content
may be placed as content of the canvas element."* It further advises *"a
one-to-one mapping of interactive regions to focusable areas in the fallback
content."*

Four layers, all of them required.

**Layer 1 — Naming.** `role="img"` plus a substantive `aria-label` on the
canvas. Not "3D scene". Something like *"3D model of Suzuka Circuit, 5.807 km,
18 corners, viewed from above Turn 1."*

**Layer 2 — Fallback DOM inside the `<canvas>` tags.** A static SVG track map,
a heading, and a real data table of corners with their numbers, entry speeds
and gears. This same subtree is the no-JavaScript fallback, the no-WebGL
fallback, the forced-colours fallback and the poster frame. It is the permanent
representation, not a loading state.

**Layer 3 — Semantics, via WAI-ARIA Graphics Module 1.0.**

| Role | Superclass | Accessible name |
| --- | --- | --- |
| `graphics-document` | `document` | **Required** — on the figure root |
| `graphics-object` | `group` | Not required — per sector or sub-component |
| `graphics-symbol` | `img` | **Required**, children presentational — per atomic marker |

**Layer 4 — Interaction.** A sibling list of native `<button>` elements, one
per corner or sector, whose handlers drive the same camera code the pointer
uses. An `aria-live="polite"` region announces the camera's current subject as
it changes.

## 6. Keyboard control of the 3D scene

The canvas gets `tabindex="0"` and a visible focus ring. Control instructions
live in an adjacent element referenced by `aria-describedby`.

`OrbitControls` has arrow-key support, but it is **off by default** and must be
wired explicitly with `listenToKeyEvents(domElement)`. Defaults:

| Property | Default |
| --- | --- |
| `keys` | `{ LEFT: 'ArrowLeft', UP: 'ArrowUp', RIGHT: 'ArrowRight', BOTTOM: 'ArrowDown' }` |
| `keyPanSpeed` | `7.0` |
| `keyRotateSpeed` | `1.0` |
| `autoRotate` | `false` |
| `autoRotateSpeed` | `2.0` |
| `enableDamping` | `false` |
| `dampingFactor` | `0.05` |
| `minPolarAngle` / `maxPolarAngle` | `0` / `Math.PI` |
| `minDistance` / `maxDistance` | `0` / `Infinity` |

`stopListenToKeyEvents()`, `update()` and `dispose()` exist and are used on
teardown.

### A documented deviation

**three.js recommends `window` as the argument to `listenToKeyEvents`.** We
attach to the focusable canvas instead, so that arrow keys are only captured
while the scene has focus and are not swallowed from the rest of the page.

This is recorded as a **deliberate deviation from the library's documented
recommendation**, taken for a stated accessibility reason, and it is written
down here precisely so that nobody later "fixes" it back. The trade-off is
real: `window` is simpler and is what the library suggests; canvas-scoped
listening requires the canvas to be focusable and the focus state to be
visible, both of which we do anyway.

## 7. Focus

```css
:focus-visible {
  outline: 2px solid var(--f1-patina-deep);
  outline-offset: 3px;
}
```

- The ring must clear **3:1** against both the component and the adjacent
  surface (SC 1.4.11, AA).
- The focused component must not be **entirely hidden** by author content
  (SC 2.4.11, AA). The practical case is a sticky header over the 3D viewport
  or over a long results table — scroll padding is set so a focused row is
  never behind it.
- SC 2.4.13 (AAA) would additionally require an indicator area at least that of
  a 2 CSS px thick perimeter of the component — a 90×30px button needs ≥480px²
  — and 3:1 contrast measured as *"the change of contrast between the same
  pixels in focused and unfocused states"*. Our 2px ring at 3px offset satisfies
  the area part comfortably; we do not claim the criterion.
- Focus order follows reading order. Focus never moves without a user action.

## 8. Target size

SC 2.5.8, Level AA: *"The size of the target for pointer inputs is at least 24
by 24 CSS pixels."* Exceptions: spacing, equivalent functions elsewhere on the
page, inline targets, user-agent-controlled appearance, and essential
presentation.

The **spacing exception** is the one that applies to a track map: an undersized
target passes if a 24px-diameter circle centred on its bounding box does not
intersect the circle of any other target. Corner hotspots on a tight sequence —
Suzuka's esses, the Monaco swimming-pool complex — will not satisfy that, so
they are given real 24px targets and the marker is offset with a leader line
rather than sitting on the apex.

Our control sizes are 26 / 32 / 44px, all clearing the minimum.

Legend chips, scrubber handles and chart hover targets are all held to the same
number.

## 9. Forced colours and other preference queries

Under `@media (forced-colors: active)` the user agent forces colour, background
colour, border, outline and SVG fill/stroke to system values; forces
`box-shadow` and `text-shadow` to `none`; and forces non-`url()`
`background-image` to `none`. **It does not repaint `<canvas>` pixels.**

Required behaviour:

- Hide the WebGL canvas; reveal the Layer 2 fallback.
- Re-style chart strokes to `CanvasText`.
- Restore any border previously carried by `box-shadow`, e.g.
  `border: 2px ButtonText solid`.
- Use system keywords: `Canvas`, `CanvasText`, `LinkText`, `ButtonText`,
  `ButtonBorder`, `Highlight`, `HighlightText`, `GrayText`, `AccentColor`.
- `forced-color-adjust` takes `auto`, `none`, `preserve-parent-color` — use
  `none` only where a colour genuinely is the information.

Note the user agent derives system colours from **native element semantics, not
ARIA roles**: `role="button"` on a `div` will not receive `ButtonText`. Use real
elements.

Also honoured: `prefers-contrast` (`no-preference` / `more` / `less` /
`custom`) and `prefers-reduced-transparency` for any overlay above the 3D
scene. Motion preferences are in [Motion](motion.md) §6.

## 10. Structure and navigation

- One `<h1>` per page; no skipped heading levels.
- Landmarks on every page; a skip link to `<main>`.
- Top-level navigation held to **five items or fewer**, and sibling choices in
  any sidebar level to four or fewer — the working-memory limit is ≤4 items
  held at once.
- Flush-left ragged-right text; justified body text is prohibited, partly
  because the rivers it creates are a legibility problem for dyslexic readers.
- Every table has a `<caption>` and real `<th scope>` attributes. A results
  table is a table, not a grid of divs.
- Session times are rendered with a visible timezone label. A time without a
  zone is an accessibility failure as much as a correctness one.

## 11. What CI enforces

Accessibility is a gate, not a review item. CI blocks on:

- **axe** checks across a representative page per coverage tier.
- **Lighthouse CI** budgets.
- **Palette assertions** — every categorical swatch at 3:1 on both grounds,
  4.5:1 where it carries text, and CIEDE2000 separation under three
  colour-vision simulations. Full specification in
  [Driver colour encoding](driver-color-encoding.md) §8.
- **Link checking** across all pages. At 2,400–6,000 densely cross-linked
  pages, rot is silent and a broken "described in detail below" link removes a
  text alternative.

Manual passes that CI cannot replace: keyboard-only traversal of a race page
and a circuit page; a screen-reader pass over one chart of each archetype; and
a forced-colours pass on the circuit hero.
