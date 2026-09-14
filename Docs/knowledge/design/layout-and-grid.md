---
type: Reference
title: Layout and grid
description: The 12-column grid, the spacing ladder, measures, radii, the elevation system and the paper-grain overlay that give every page the same underlying structure.
tags:
  - design
  - layout
  - grid
  - spacing
  - elevation
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
  - id: impeccable_index_css
    resource: https://impeccable.style/_astro/index.CAcT7T7Q.css
    title: impeccable.style compiled index stylesheet
  - id: impeccable_subpages_css
    resource: https://impeccable.style/_astro/sub-pages.CTJhASV9.css
    title: impeccable.style compiled sub-pages stylesheet
  - id: its_wikipedia
    resource: https://en.wikipedia.org/wiki/International_Typographic_Style
    title: International Typographic Style
  - id: grid_systems
    resource: https://designopendata.wordpress.com/portfolio/grid-systems/
    title: Josef Müller-Brockmann — Grid Systems in Graphic Design
  - id: butterick_summary
    resource: https://practicaltypography.com/summary-of-key-rules.html
    title: Butterick — Summary of key rules
  - id: mdn_content_visibility
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/content-visibility
    title: MDN — content-visibility
status: stable
---

# Layout and grid

The structural half of this aesthetic is Swiss: a mathematical modular grid,
because a grid is the most legible and harmonious means for structuring
information; asymmetric composition; flush-left ragged-right setting; and no
photography. That last one is not a stylistic preference — **there is no free,
legal F1 photo corpus**, so the system is built to work entirely without
images. Typography, data, the 3D renders and the circuit SVGs are the visual
material, and the grid is what holds them.

The canonical faces of that lineage — Akzidenz-Grotesk, Univers,
Neue Haas Grotesk / Helvetica — are historically correct and are also exactly
the category default. We take the structure and not the typeface; see
[Typography](typography.md).

## 1. The page grid

| Token | Value |
| --- | --- |
| `--f1-width-max` | `1320px` |
| `--f1-columns` | `12` |
| `--f1-gutter` | `24px` |
| `--f1-measure` | `65ch`–`75ch` |
| `--f1-section-pad` | `clamp(72px, 8vw, 120px)` |

Twelve columns at a 1320px maximum. The prose column sits inside it at 65–75
characters and is not centred in the full width — the asymmetry is deliberate
and is what leaves room for a marginal note, a provenance stamp, or a small
figure to sit beside body copy without a modal.

A modular grid means columns **and** rows: the circuit and race indexes use a
four-row module so that a track figure, a name, a set of figures and a data
stamp always occupy the same cells regardless of how long the name is. Text and
figures occupy whole modules.

Müller-Brockmann's own caveat is the right attitude to all of this: *"The grid
system is an aid, not a guarantee."*

### Breakpoints

Written in modern range syntax, matching the reference: `@media (width <= 760px)`.

The reference's own breakpoint set, recorded because it is a useful calibration
of how many are actually needed: 400, 420, 480, 520, 560, 600, 620, 640, 700,
720, 760, 768, 820, 880, 900, 920, 980, 1080, 1100, 1280, 1300px. Ours is a
subset — we do not need twenty-one.

One breakpoint is functional rather than cosmetic and belongs to the charts:
**520px**, below which direct end-of-line labelling is replaced by a legend
plus hover. See [Driver colour encoding](driver-color-encoding.md) §5.

Responsive behaviour is **structural**, not cosmetic: reorder, collapse, reflow
or reveal based on what remains important at that width. Prefer
container-aware components where the same component appears in several
contexts — a stint Gantt in a race page's main column and in a season page's
sidebar is the same component at two widths.

## 2. Spacing

The reference ladder is `8 / 16 / 24 / 32 / 48 / 80 / 120` — 8-only. Its own
authoring guidance says a **4-unit base** gives the useful middle steps an
8-only scale misses. We take the guidance rather than the artefact and add the
missing steps:

| Token | Value |
| --- | --- |
| `--space-3xs` | `4px` |
| `--space-2xs` | `8px` |
| `--space-xs` | `12px` |
| `--space-sm` | `16px` |
| `--space-s` | `20px` |
| `--space-md` | `24px` |
| `--space-lg` | `32px` |
| `--space-xl` | `48px` |
| `--space-2xl` | `80px` |
| `--space-3xl` | `120px` |

Rules that make the ladder do work rather than just exist:

- **Tight groups, generous separation.** Equal gaps everywhere make it
  impossible to tell what belongs together; rhythm comes from deliberate
  contrast between tight and generous intervals.
- **More space above a heading than below it.** A heading that sits closer to
  the previous block than to its own content attaches itself to the wrong
  thing. Read the computed values — do not eyeball this.
- **Group by meaning, using proximity before containers.** Reach for a border
  or a card only after spacing has failed.
- Use `gap` for sibling rhythm where it expresses the relationship more
  directly than child margins.
- One scale. No arbitrary one-off values.

## 3. Measure and density

| Surface | Measure |
| --- | --- |
| Prose | **65–75ch** |
| Outer bounds if a layout forces it | 45–90 characters |
| Short headline blocks | 11–36ch, clamped |
| Data tables and compact instrument UI | 120ch+ is fine |

Data surfaces are explicitly exempt from the prose measure — *"data and compact
UI can run denser; tables at 120ch+ are fine."* A twenty-driver results table
squeezed to 70 characters is worse, not better.

The reference's own `ch` measures, for calibration: 56, 58, 60, 62, 64, 72 and
82ch for body blocks; 11, 15, 20, 22, 24, 32 and 36ch for clamped headline
blocks.

## 4. Radii

| Token | Value | Use |
| --- | --- | --- |
| `--f1-radius-sm` | `3px` | **The default.** Inputs, chips, code, chart segment rects |
| `--f1-radius-md` | `8px` | Cards only |
| `--f1-radius-pill` | `999px` | Reserved; used sparingly |

Three values, and the small one is the default. Over-rounding is a named
anti-pattern; a 16px radius on a data panel makes an instrument look like a
toy.

The dominance strip's 27 segments use `rx: 3` — the same `--f1-radius-sm` — so
the chart layer and the interface layer share one geometry vocabulary.

## 5. Controls

| Token | Value |
| --- | --- |
| `--f1-control-sm` | `26px` |
| `--f1-control-md` | `32px` |
| `--f1-control-lg` | `44px` |

All three clear the 24×24 CSS px minimum of SC 2.5.8 (AA). The small size
exists at 26px rather than 24px so that a 1px border and a focus offset do not
eat into the target. See [Accessibility](accessibility.md) §8.

## 6. Elevation

A two-step ambient system plus a small set of physical-instrument shadows.
Recorded verbatim, because the values are the system:

| Token | Value |
| --- | --- |
| `--f1-lift-1` | `0 1px 1px oklch(13% 0 0/.05), 0 2px 3px oklch(13% 0 0/.04), 0 6px 12px oklch(13% 0 0/.05)` |
| `--f1-lift-2` | `0 1px 1px oklch(13% 0 0/.04), 0 3px 5px oklch(13% 0 0/.05), 0 12px 20px oklch(13% 0 0/.06), 0 32px 48px oklch(13% 0 0/.07)` |
| `--f1-key-lift` | `0 1px 2px oklch(0% 0 0/.4)` |
| `--f1-cap-lift` | `inset 0 1px 0 oklch(100% 0 0/.9), 0 1px 0 oklch(13% 0 0/.14), 0 2px 3px oklch(13% 0 0/.08)` |
| `--f1-cap-press` | `inset 0 1px 2px oklch(13% 0 0/.14)` |
| `--f1-track-recess` | `inset 0 1px 3px oklch(13% 0 0/.16), inset 0 -1px 0 oklch(100% 0 0/.7)` |
| `--f1-led` | `0 0 0 1px oklch(13% 0 0/.12), 0 0 4px oklch(84% .19 80/.6)` |
| `--f1-indicator-glow` | `0 0 0 1px oklch(0% 0 0/.3), 0 0 4px oklch(84% .19 80/.65)` |

**The rule: every ambient shadow carries a real y-offset and a soft blur at
4–7% alpha.** Depth is used only where it clarifies state or hierarchy — a
shadow that exists to make a panel look nice is decoration.

The two zero-offset tokens are the exception and they are deliberate. `--f1-led`
and `--f1-indicator-glow` are literal LED affordances in the physical-instrument
metaphor — an active scrubber indicator, a live-state dot on an instrument
panel. **They are never used as elevation on a card or a panel.** A zero-offset
coloured halo used as a shadow is the thing the craft floor calls decoration,
and the distinction between the two uses is the whole point.

`--f1-cap-lift` uses a 90%-white inset top highlight: the classic keycap bevel.
`--f1-track-recess` is its inverse and belongs on a slider track. These belong
to the instrument chrome around the 3D canvas and the replay scrubber; they do
not appear in the editorial body of a page.

## 7. The grain overlay

A single paper texture, defined as an inline SVG `feTurbulence` fractal noise
and used as a background token:

| Parameter | Value |
| --- | --- |
| Type | `fractalNoise` |
| `baseFrequency` | `0.9` |
| `numOctaves` | `2` |
| Desaturation | via `feColorMatrix` |
| Tile | 160 × 160 |

It goes on the paper ground at very low opacity and nowhere else. It is not on
cards, not on instrument panels, not behind charts and not behind the 3D
canvas. A grain over a data mark changes the mark's measured contrast, which
makes the palette assertions in CI meaningless.

Grain is the site's one texture. A decorative grid-line background is a named
anti-pattern — with the explicit carve-out that grids are legitimate *"for
canvases, maps, or tasks that need measurement"*, which covers a track map, a
telemetry plot and the 3D scene's ground plane. A grid behind body copy is not
covered.

## 8. Containers, and what not to reach for

| Rule | |
| --- | --- |
| Cards are **not** the default layout | Use spacing and alignment first. Same-size cards of icon + heading + text as the page structure is a named category default |
| **Never nest cards** | Flatten: spacing, typography and dividers instead of nested containers |
| No coloured `border-left`/`border-right` above 1px | On cards, list items, callouts or alerts |
| No modal | For a task that needs neither interruption nor protected focus. Overlays that must escape their container use `<dialog>`, the popover API, `position: fixed`, or a portal |
| No section numbers (01 / 02 / 03) | Unless the sequence itself carries information the reader needs |
| Alignment | Pick left and keep it. Centred body copy is prohibited |
| Reduce variants | Three variants that cover 90% of cases beat twelve |

The one thing that must **not** be simplified away: *"do not oversimplify
complex domains"* and *"do not remove information users need to make
decisions."* A dense twenty-driver timing table is the correct amount of
complexity for the task. Restraint applies to chrome, not to data.

## 9. Composition checks

**The squint test.** With detail blurred, can you still identify the primary
element, the secondary element, and the major groups, in order? If everything
has the same visual weight, nothing stands out — the visual-noise-floor
failure. One primary element, two or three secondary, everything else muted.

**One focal moment per page.** Each page has exactly one thing it is for. On a
circuit page that is the 3D track; on a race page it is the race trace.
Everything else is subordinate, and subordinate means visually subordinate, not
merely further down.

**The working-memory rule.** Humans hold about four items at once. Five to
seven pushes the boundary; eight or more is overload. Applied: one primary
action and one or two secondary, with the rest in a menu; five or fewer
top-level navigation items; four or fewer sibling choices visible per sidebar
level; one reading path through a long article, with related links gathered
into a single block at the end rather than scattered mid-flow.

## 10. Layout stability and long pages

At 2,400–6,000 pages, most of which are long, two mechanisms matter:

- **Reserve every box that loads late.** The 3D canvas, every chart SVG and
  every track figure carry an `aspect-ratio` so nothing reflows. CLS target is
  **< 0.1**, and structurally it should be 0 — layout shift on this site would
  come from a missing reservation, not from anything unavoidable.
- **`content-visibility: auto` with `contain-intrinsic-size`** on long index
  pages and on off-screen chart sections, paired with the
  `contentvisibilityautostatechange` event so that any render loop inside them
  stops when they are not visible.

Both are in service of the budgets: LCP < 2.0 s on 4G, INP < 200 ms, and
under 40 kB of JavaScript on a page with no 3D.

## 11. Browser surfaces

The parts nobody draws still carry the design: text selection, the caret,
custom scrollbars, focus rings, underline offset, and the numerals in tabular
data. All of them ship with browser defaults that belong to no design system.
Theme every one of them from the palette.

| Surface | Treatment |
| --- | --- |
| Selection | Patina at low alpha, ink text |
| Caret | `--f1-ink` |
| Scrollbars | Thin, themed, on instrument panels and code blocks |
| Focus ring | `2px solid var(--f1-patina-deep)`, offset 3px (1–4px contextually) |
| Underline offset | Set explicitly; the default sits too close at 16px |
| Tabular numerals | [Typography](typography.md) §2 |

This is the cheapest signal that a page was built rather than assembled, and it
is the one most reliably skipped.
