---
type: Reference
title: Colour system
description: The OKLCH token system — paper, ink and instrument families, two interface accents, and the per-theme re-toning rule that keeps brand colours legible.
tags:
  - design
  - colour
  - oklch
  - tokens
  - contrast
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
  - id: wcag_non_text_contrast
    resource: https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html
    title: WCAG 2.2 Understanding SC 1.4.11 Non-text Contrast
  - id: wcag_contrast_minimum
    resource: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
    title: WCAG 2.2 Understanding SC 1.4.3 Contrast (Minimum)
  - id: w3c_relative_luminance
    resource: https://www.w3.org/WAI/GL/wiki/Relative_luminance
    title: W3C — Relative luminance
  - id: mdn_light_dark
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/color_value/light-dark
    title: MDN — light-dark()
  - id: mdn_forced_colors
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors
    title: MDN — @media (forced-colors)
status: stable
---

# Colour system

Colour on this site does two jobs and no third one. It encodes data, and it
carries a very small amount of interface meaning. It does **not** carry
hierarchy — that is typography's job — and it does not decorate.

Everything is authored in `oklch()`. This is not a preference. Perceptually
even lightness is the property that makes a categorical palette tractable at
all, and it is the only way to re-tone a brand hue for a different ground
without the hue drifting. sRGB interpolation toward white visibly shifts
saturated reds, which is exactly the family F1 liveries are densest in.

## 1. Neutrals at chroma 0

Every neutral has chroma exactly `0`. A tinted grey is a decision that has to
be earned, and on a page whose accents are already spent on data, it is not
earned.

### Paper — the light ground

| Token | Value | Role |
| --- | --- | --- |
| `--f1-paper` | `oklch(97.8% 0 0)` | Page ground |
| `--f1-paper-raised` | `oklch(99.5% 0 0)` | Raised surface |
| `--f1-paper-deep` | `oklch(95% 0 0)` | Recessed / alternate row |
| `--f1-gray` | `oklch(92% 0 0)` | Fills |
| `--f1-gray-2` | `oklch(88% 0 0)` | Stronger fills |

### Ink — text

| Token | Value | Role |
| --- | --- | --- |
| `--f1-ink` | `oklch(13% 0 0)` | Maximum-contrast ink; headings |
| `--f1-text` | `oklch(22% 0 0)` | Body text |
| `--f1-text-muted` | `oklch(46% 0 0)` | Secondary |
| `--f1-text-faint` | `oklch(51% 0 0)` | Captions, provenance stamps |
| `--f1-text-mute-deep` | `oklch(66% 0 0)` | Disabled; **never** body text |

### Lines

| Token | Value | Role |
| --- | --- | --- |
| `--f1-rule` | `oklch(13% 0 0 / .08)` | Hairline rules, chart gridlines |
| `--f1-edge` | `oklch(13% 0 0 / .45)` | Definite edges |

`--f1-rule` at 8% alpha is the value chart gridlines use. An axis drawn at a
mid grey competes with the data; an axis drawn at 8% ink recedes into the paper
and still reads.

## 2. Instrument surfaces — dark panels on a light page

The aesthetic reference has **no dark theme**. `prefers-color-scheme` appears
zero times across all five of its stylesheets. What it has instead is
*instrument panels*: scoped blocks that redefine a handful of tokens and
declare `color-scheme: dark` locally. Four non-`:root` blocks in its
stylesheets remap tokens this way, and `color-scheme: dark` appears twice, both
times on a panel rather than on the document.

We adopt exactly this pattern, and it is what lets a dark WebGL canvas sit on a
light page without a theme switch. See
[3D art direction](three-d-art-direction.md).

| Token | Value | Role |
| --- | --- | --- |
| `--f1-instrument` | `oklch(24% 0 0)` | Panel ground |
| `--f1-instrument-deep` | `oklch(17% 0 0)` | Recessed panel |
| `--f1-instrument-raised` | `oklch(31% 0 0)` | Raised element inside a panel |
| `--f1-instrument-text` | `oklch(93% 0 0)` | Text on a panel |
| `--f1-instrument-muted` | `oklch(68% 0 0)` | Secondary text on a panel |
| `--f1-instrument-rule` | `oklch(100% 0 0 / .12)` | Rule on a panel |
| `--f1-instrument-edge` | `oklch(100% 0 0 / .3)` | Edge on a panel |

```css
/* An instrument panel is a scope, not a theme. */
.f1-instrument {
  color-scheme: dark;
  --f1-paper: var(--f1-instrument);
  --f1-paper-raised: var(--f1-instrument-raised);
  --f1-paper-deep: var(--f1-instrument-deep);
  --f1-text: var(--f1-instrument-text);
  --f1-text-muted: var(--f1-instrument-muted);
  --f1-rule: var(--f1-instrument-rule);
  --f1-edge: var(--f1-instrument-edge);
}
```

Because the remap is on the *semantic* layer, every component inside the panel
— charts included — inherits the dark ground without knowing it is in one.
That is the property that makes this cheaper than a theme.

Light-on-dark type needs compensating on all three perceptual axes: slightly
more line height, a touch more tracking, and one step more weight where the
face needs it. Apply this inside `.f1-instrument`, do not rely on the same
values as on paper.

## 3. The two-accent rule

**There are exactly two interface accents, plus one alarm colour.**

| Token | Value | Role |
| --- | --- | --- |
| `--f1-gold` | `oklch(84% .19 80.46)` | Primary accent: link underline on hover, active indicator, scrubber handle |
| `--f1-gold-rich` | `oklch(77% .13 82)` | Gold where 84% is too light against paper |
| `--f1-gold-deep` | `oklch(61% .085 78)` | Gold carrying text |
| `--f1-on-gold` | `oklch(14% .018 95)` | Text on a gold fill |
| `--f1-patina` | `oklch(70% .12 188)` | Secondary accent: selection, secondary state |
| `--f1-patina-deep` | `oklch(45% .1 190)` | **Focus ring** |
| `--f1-patina-ink` | `oklch(41% .11 190)` | Patina carrying text |
| `--f1-vermilion` | `oklch(52% .16 35)` | Alarm only — errors, red-flag states, stale-data warnings |

Gold and patina lineage: the values above are the reference site's own
`kinpaku` and `patina` families, kept because they are two hues that are
neither of the two obvious motorsport defaults (near-black-plus-neon, and
cream-plus-signal-red).

**The binding rule: interface accents are never used to encode data.** Gold
means "this is the thing you are interacting with". If gold also meant "this is
McLaren", both meanings would be destroyed. Conversely, a team colour never
indicates interactive state.

Vermilion is reserved for alarm and is not a chart colour, despite a red F1
livery existing. A red line on a chart is Ferrari; a red panel border is a
failure.

### Links

| Token | Value |
| --- | --- |
| `--f1-link-on-paper` | `var(--f1-ink)` |
| `--f1-link-on-paper-line` | `oklch(13% 0 0 / .28)` |
| `--f1-link-on-paper-line-hover` | `var(--f1-gold)` |

Links are ink-coloured with an animated underline, never a coloured link. This
matters at this site's link density: a page whose every derived number links to
its method page would be unreadable in blue.

### Focus

```css
:focus-visible {
  outline: 2px solid var(--f1-patina-deep);
  outline-offset: 3px;
}
```

Offsets of 1–4px are used contextually where 3px collides with an adjacent
element. The ring must clear 3:1 against both the component and its
surroundings — see [Accessibility](accessibility.md).

## 4. Per-theme re-toning

A brand hex is a fact about a livery. It is not a fact about legibility on a
97.8%-lightness ground, and five of the eleven 2026 team colours fail the
non-text contrast threshold there. The mechanism is the **three-token model**,
applied to every externally-sourced colour — team liveries and tyre compounds
alike:

| Token shape | Where it may be used |
| --- | --- |
| `--team-<id>-brand` | Large fills, chips, swatches — areas big enough that the colour is unambiguous. **Never a lone hairline.** |
| `--team-<id>-ink-light` | Strokes, markers and text on paper. Clears 3:1 (4.5:1 where it carries text). |
| `--team-<id>-ink-dark` | Strokes, markers and text on an instrument panel. |

The measured failures, the computed replacements and the colour-vision analysis
are in [Driver colour encoding](driver-color-encoding.md). This page records
only the derivation rule.

**Derive by adjusting OKLCH lightness only**, holding chroma and hue, then
reduce chroma as you approach white or black rather than keeping high chroma at
extreme lightness to make the arithmetic uniform. The published prior-art
implementation does its remap by linear-sRGB channel mixing:

```js
// WCAG relative luminance
function lum(h) {
  const [r, g, b] = hexRgb(h).map(v => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function teamCol(hex) {
  let h = hex;
  if (isDark()) { let n = 0; while (lum(h) < 0.10 && n++ < 6) h = mix(h, '#ffffff', 0.22); }
  else          { let n = 0; while (lum(h) > 0.62 && n++ < 6) h = mix(h, '#0a0d12', 0.18); }
  return h;
}
```

Thresholds: luminance floor 0.10 on a dark ground, ceiling 0.62 on a light one;
mix steps of 22% toward white and 18% toward `#0a0d12`; hard cap of six
iterations so a pathological input terminates instead of washing out. **Our
variant performs the same search in OKLCH on the L channel alone**, which
avoids the hue drift sRGB mixing introduces on saturated reds — the family this
palette is densest in. Colours are resolved **at build time** and emitted as
tokens; nothing iterates in the browser.

## 5. Contrast arithmetic

Implement this exactly in the build so tokens can be unit-tested. Do not trust
a design-tool eyedropper.

```
contrast = (L1 + 0.05) / (L2 + 0.05)          // L1 is the lighter luminance

L = 0.2126·R + 0.7152·G + 0.0722·B
where, per channel c = c8bit / 255:
  c ≤ 0.03928  →  c / 12.92
  c > 0.03928  →  ((c + 0.055) / 1.055) ^ 2.4
```

The specification's `0.03928` threshold is a known erratum for the IEC
61966-2-1 value of `0.04045`; the difference is negligible at 8-bit depth.

Targets, with their conformance levels stated correctly:

| Content | Ratio | Criterion |
| --- | ---: | --- |
| Body text | 4.5:1 | SC 1.4.3 (AA) |
| Large text (18pt / 14pt bold ≈ 24px / 18.5px) | 3:1 | SC 1.4.3 (AA) |
| Graphical objects — **every line in a graph**, marker, axis, chip | 3:1 | SC 1.4.11 (AA) |
| Controls, icons, focus indicators | 3:1 | SC 1.4.11 (AA) |

**Do not ship an APCA-only palette.** As of the 10 September 2026 Working
Draft, WCAG 3 still states that its contrast algorithm "is yet to be
determined"; APCA was removed from the July 2023 draft. CI gates on the WCAG 2
ratio. APCA Lc values may be computed as an advisory aid — they predict thin
light-on-dark readability better, which is relevant inside instrument panels —
but they are never the gate.

## 6. Dark theme (phase 2)

Instrument panels are the launch mechanism; a full dark theme is a phase-2
decision. When it arrives, the layering is:

1. Define the **complete** light palette on bare `:root`.
2. Redefine **only the changed tokens** under
   `@media (prefers-color-scheme: dark)`, guarded as
   `:root:not([data-theme='light'])`.
3. Redefine them again under `:root[data-theme='dark']` so a manual toggle wins
   in both directions.

Never let a colour's only definition live inside a media block.
`light-dark(light, dark)` (Baseline May 2024) works only where `color-scheme`
resolves to `light dark`, and is the right tool for per-token pairs once
`:root { color-scheme: light dark; }` is set. Do not invert the light theme
mechanically — surface elevation and contrast are designed separately for a
dark ground, not derived.

Resolved token values are passed into three.js materials with
`getComputedStyle(document.documentElement).getPropertyValue(...)` so the scene
follows whichever scope it is mounted in.

## 7. Forced colours

Under `@media (forced-colors: active)` the user agent forces `color`,
`background-color`, `border-color`, `outline-color`, SVG `fill`/`stroke` and
several others to system values; forces `box-shadow` and `text-shadow` to
`none`; and forces non-`url()` `background-image` to `none`. It does **not**
repaint `<canvas>` pixels — a WebGL track render keeps its own colours against
a forced black or white page, which usually reads as broken.

Required handling:

- Hide the WebGL canvas and reveal the SVG/static fallback.
- Re-style chart strokes to `CanvasText`.
- Restore any border that was being carried by `box-shadow`, e.g.
  `border: 2px ButtonText solid`.
- Use the system keywords — `Canvas`, `CanvasText`, `LinkText`, `ButtonText`,
  `ButtonBorder`, `Highlight`, `HighlightText`, `GrayText`, `AccentColor`.

Note the user agent picks system colours from native element semantics, not
from ARIA roles: `role="button"` on a `div` does not get `ButtonText`.

Also handle `prefers-contrast` (`no-preference` / `more` / `less` / `custom`)
and `prefers-reduced-transparency` for any overlay sitting on the 3D scene.

## 8. Prohibited colour moves

- **Purple-and-blue gradients, and bright cyan on dark.** Named as a familiar
  machine-generated default.
- **Cream and beige as a palette.** A default substitute for a considered one.
- **Dark mode with glowing accents.** Glowing borders turn a dark interface
  into neon.
- **Gradient text.** One solid colour; emphasis from size or weight.
- **Grey text on a coloured surface.** Tint secondary text from that surface's
  hue or its foreground instead.
- **Coloured `border-left`/`border-right` above 1px** on cards, list items,
  callouts or alerts.
- **A zero-offset coloured halo as elevation.** The one sanctioned zero-offset
  glow is the LED/indicator affordance described in
  [Layout and grid](layout-and-grid.md), and it is a literal instrument
  metaphor, not a shadow.
- **Chains of translucent overlays** where alpha makes contrast
  context-dependent. Prefer explicit colours.
