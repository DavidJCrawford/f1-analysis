---
type: Reference
title: Typography
description: The three-family type system, its role scale, and the numeric-figure discipline that makes lap times, gaps and axis labels line up.
tags:
  - design
  - typography
  - fonts
  - tabular-figures
  - opentype
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
  - id: google_fonts_repo
    resource: https://github.com/google/fonts
    title: google/fonts — canonical TTF sources
  - id: gf_css2_inter
    resource: https://fonts.googleapis.com/css2?family=Inter:wght@400..700&display=swap
    title: Google Fonts CSS2 served latin subset (Inter)
  - id: mdn_font_variant_numeric
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/font-variant-numeric
    title: MDN — font-variant-numeric
  - id: datawrapper_fonts
    resource: https://www.datawrapper.de/blog/fonts-for-data-visualization
    title: Datawrapper — What to look for in a font for data visualization
  - id: butterick_summary
    resource: https://practicaltypography.com/summary-of-key-rules.html
    title: Butterick — Summary of key rules
status: stable
---

# Typography

Typography carries the hierarchy on this site. Colour is spent almost entirely
on data encoding (see [Colour system](color-system.md)), which means size,
weight and space are the only tools left for telling a reader what matters.
That is a constraint chosen on purpose, and it raises the bar on the type
system rather than lowering it.

## 1. Families

| Role | Family | Fallback stack | Why |
| --- | --- | --- | --- |
| Text | **Albert Sans** | `"Avenir Next", "Helvetica Neue", Arial, system-ui, sans-serif` | The reference site's body voice; a neutral geometric grotesk with no era tell |
| Display | **Alumni Sans** | `"Albert Sans", Arial, sans-serif` | Condensed, high-contrast at large sizes, and legible at weight 200 |
| Data | **JetBrains Mono** | `ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace` | Monospaced, therefore inherently tabular; digit advance 600/1000 em |

Three families is more than the one that a strict reduction pass would allow,
and the reconciliation is that reading and instrument surfaces legitimately
carry more type roles than a brand surface does. The tighter step ratio
(1.125–1.2 between adjacent sizes) is what keeps three families from reading as
three systems.

None of the three appears on the reference project's list of training-data
default typefaces (Fraunces, Playfair Display, Cormorant, Lora, Crimson,
Newsreader, Syne, Space Grotesk, Space Mono, IBM Plex, Inter-as-display,
DM Sans, DM Serif, Outfit, Plus Jakarta Sans, Instrument Sans). That is a
deliberate reason to keep them, not a coincidence.

## 2. The figure problem, and why the data face is monospaced

**Albert Sans has neither tabular figures by default nor a working `tnum`
feature.** Its digit advances were measured from the canonical TTF at
`ofl/albertsans/` and range 306–655 per 1000 em — proportional, with no
tabular alternate to opt into. It is a perfectly good body face and an
unusable table face.

That single measurement decides the system: **every figure that will ever sit
in a column, an axis, a tooltip or a timing readout is set in JetBrains Mono,
not in Albert Sans.** Numbers inside running prose stay in Albert Sans, where
proportional figures are correct.

```css
/* Applied to every td, th, axis tick, tooltip value, gap, delta and lap time. */
.num,
td, th,
.tick text,
.readout {
  font-family: var(--f1-font-mono);
  font-variant-numeric: var(--f1-numeric);
  font-feature-settings: 'tnum' 1;
}

:root {
  --f1-numeric: tabular-nums lining-nums;
}
```

The reference stylesheet contains no `font-variant-numeric` declaration
anywhere. It does not need one; a marketing site has no leaderboard. This site
does, and the declaration above is a required addition rather than an
inherited one.

### Duplexing — the property most people miss

Tabular means *every digit in this weight has the same advance*. **Duplexed**
(Datawrapper calls it multiplexed) means *every digit has the same advance at
every weight*. Only the second property lets you bold the fastest lap in a
column without the column shifting. JetBrains Mono, being monospaced, is
duplexed by construction.

## 3. Verified figure behaviour of open-licence alternatives

Measured by downloading the canonical TTFs from `google/fonts` and reading
`hmtx` advance widths for U+0030–U+0039, with variable fonts instanced at
wght 400 / 600 / 700 and OpenType features enumerated from the GSUB/GPOS
FeatureList (fontTools 4.65.0, 2026-09-14). These are binary measurements, not
vendor claims.

### 3.1 Tabular by default **and** duplexed — safe for a bolded column

| Family | Digit advance | Notes |
| --- | --- | --- |
| IBM Plex Sans | 600/1000 em | Identical at 400/600/700 |
| Chivo | 615/1000 em | Identical at all weights |
| Asap | 535/1000 em | Identical at all weights |
| Noto Sans | 572/1000 em | Identical at all weights |
| Open Sans | 1171/2048 em | Identical at all weights |
| Radio Canada | 600/1000 em | Identical at all weights |
| Hanken Grotesk | 560/1000 em | Identical at all weights |
| Recursive (MONO=0) | 600/1000 em | The family Datawrapper names as multiplexed |
| Lato | 1160/2000 em | Measures duplexed |

The first six of these are the shortlist named in the project specification as
the replacement candidates if Albert Sans proves inadequate for figures. The
measurement above is what "verified" means in that sentence.

Monospaced and therefore inherently tabular: JetBrains Mono 600/1000,
IBM Plex Mono 600/1000, Roboto Mono 1229/2048, Space Mono 612/1000,
Sometype Mono 580/1000, Martian Mono 750/1000, Geist Mono 600/1000.

### 3.2 Tabular by default but **not** duplexed — the column shifts on bold

| Family | 400 → 600 → 700 |
| --- | --- |
| Source Sans 3 | 497 → 513 → 528 /1000 |
| Roboto | 1151 → 1170 → 1175 /2048 |
| Source Serif 4 | 500 → 520 → 542 /1000 |
| Newsreader | 1100 → 1185 → 1230 /1000 |
| PT Serif | 533/1000 (Regular) |

Usable only if you never change weight inside a numeric column. Of the five
families Datawrapper recommends (Roboto, Lato, Open Sans, Source Sans 3,
Noto Sans), **Roboto and Source Sans 3 fail the duplex test** — a detail that
matters precisely because those two are the most commonly reached for.

### 3.3 Proportional by default, with a working `tnum` opt-in

| Family | Digit advance under `tnum` |
| --- | --- |
| Inter | 1328 → 1325 → 1324 /2048 (0.3% drift — effectively duplexed) |
| Instrument Sans | 600/1000 at 400/600/700 (exactly duplexed under `tnum`) |
| Archivo | 579/1000 |
| Public Sans | 1400/2000 |
| Literata | 582/1000 |
| Work Sans | 604/1000 |
| Space Grotesk | 620/1000 |

**Inter and Public Sans are not tabular by default** — their default digits
measure 1292/1351/1381 per 2048 em and 1224/1259/1289 per 2000 em respectively
at wght 400/600/700. A leaderboard set in either needs the explicit opt-in.
Other families carrying a working `tnum`: Atkinson Hyperlegible, Figtree,
Manrope, Lora, Bricolage Grotesque, Geist, Outfit, Plus Jakarta Sans, Onest,
Gabarito, Karla, Schibsted Grotesk, Montserrat, Rubik, Syne, Alumni Sans,
Cormorant Garamond.

Note that **Alumni Sans carries `tnum`** — so a display-sized figure in the
display face can be made tabular if a layout ever needs one.

### 3.4 Never use for numeric tables — no tabular default, no `tnum`

Albert Sans, DM Sans, Libre Franklin, Commissioner, Fraunces, Instrument Serif.

## 4. Self-hosting, and what the CDN removes

The Google Fonts CSS2 endpoint **strips most OpenType features from the served
latin subsets**. Verified by requesting `css2?family=<X>&display=swap` with a
desktop Chrome UA, taking the final (latin) `@font-face` `src`, and
enumerating the served woff2's FeatureList:

| Survives the subset | Stripped from the subset |
| --- | --- |
| `tnum`, `pnum`, `frac`, `numr`, `dnom`, `calt`, `kern`, `liga`, `locl`, `ccmp`, `mark`, `mkmk` | `zero`, `case`, `onum`, `lnum`, `ss01`–`ss05`, `salt`, `sups`, `subs`, `ordn`, `cv01` |

Served Inter v20 (48,432 B) exposes exactly eleven features: `calt, ccmp, dnom,
frac, kern, locl, mark, mkmk, numr, pnum, tnum`. Upstream Inter
(`Inter[opsz,wght].ttf`, 876,576 B) exposes `cv01`–`cv14` and `ss01`–`ss08`
plus `aalt`, `cpsp`, `dlig`, `sinf` — so the gap is larger than a short list
suggests. **Served JetBrains Mono has no `zero`**, so its slashed-zero
alternate is unreachable from the CDN.

Two consequences, and they point the same way:

1. `font-variant-numeric: slashed-zero` — genuinely useful on lap times and
   sector deltas — **requires self-hosting**.
2. Self-hosting also removes the third-party request, removes the FOUT, and
   lets us subset to `U+0020-007E` plus the punctuation the site actually uses.

Fonts are therefore self-hosted and subset through **Astro's Fonts API**, which
also gives us metric-compatible fallbacks and a non-blocking load. *The exact
configuration key and option names for the Astro 7 Fonts API are not
established by the research recorded in this knowledge base and must be read
from the Astro documentation before implementation — do not copy a guessed
config from this page.*

### `font-variant-numeric` → OpenType tag

| CSS keyword | Tag |
| --- | --- |
| `lining-nums` | `lnum` |
| `oldstyle-nums` | `onum` |
| `tabular-nums` | `tnum` |
| `proportional-nums` | `pnum` |
| `diagonal-fractions` | `frac` |
| `stacked-fractions` | `afrc` |
| `ordinal` | `ordn` |
| `slashed-zero` | `zero` |

Values combine: `font-variant-numeric: tabular-nums lining-nums slashed-zero;`

## 5. The role scale

The reference values, read verbatim from the compiled stylesheet, are recorded
in [Reference design tokens](design-tokens.md). Our scale below adopts its
structure and its signature weight inversion, and adds the numeric roles it has
no need for.

| Role | Size | Weight | Line | Tracking | Face |
| --- | --- | ---: | ---: | --- | --- |
| `display` | `clamp(3.2rem, 6.2vw, 5.6rem)` | 200 | 1.0 | 0 | Alumni Sans |
| `headline` | `clamp(2.4rem, 3.6vw, 3.4rem)` | 300 | 1.04 | 0 | Alumni Sans |
| `title-lg` | `1.5rem` | 600 | 1.25 | 0 | Albert Sans |
| `subhead` | `1.25rem` | 600 | 1.3 | 0 | Albert Sans |
| `lead` | `1.125rem` | 400 | 1.55 | 0 | Albert Sans |
| `title` | `1.0625rem` | 600 | 1.35 | 0 | Albert Sans |
| `body` | `1rem` | 400 | 1.65 | 0 | Albert Sans |
| `small` | `0.875rem` | 400 | 1.5 | 0 | Albert Sans |
| `ui` | `0.8125rem` | 500 | 1.4 | 0 | Albert Sans |
| `label` | `0.75rem` | 500 | 1.3 | `0.08em` | Albert Sans |
| `tick` | `0.8125rem` | 400 | 1 | 0 | **JetBrains Mono** |
| `readout` | `0.875rem` | 500 | 1.2 | 0 | **JetBrains Mono** |
| `datum-lg` | `1.5rem` | 500 | 1.1 | 0 | **JetBrains Mono** |

**The signature move is the weight inversion**: display sits at 200–300 while a
small title sits at 600. Large type whispers; small type asserts. Copying the
sizes without the inversion produces a different, louder site.

## 6. Measures, sizes and rhythm

| Rule | Value | Source of the number |
| --- | --- | --- |
| Prose measure | **65–75ch** | The figure the reference project's own detector enforces |
| Outer bounds, if a layout forces it | 45–90 characters | Butterick |
| Data tables | 120ch+ is fine | Dense instrument surfaces are exempt from the prose measure |
| Body size floor | 1rem / 16px | "Start around 16px, then check the actual typeface on a phone and desktop" |
| Body line-height | ~1.65 at 16px, tuned **inversely** with measure | Wider lines need more leading |
| Display line-height | ~1.0–1.3 | Tighter as size grows |
| Tracking floor | **−0.04em** | Anything tighter reads as a compression artefact |
| All-caps / small-caps | +5–12% tracking | Butterick; the reference's own label token is `0.14em` |
| Display cap | 6rem | Our `display` clamp tops out at 5.6rem, inside it |
| Minimum chart text | 12px | Below 12px "will likely be too small" for a chart label |
| Paragraph rhythm | Space **or** first-line indent, never both | Combining them double-marks the boundary |
| Alignment | Flush left, ragged right, everywhere | Justified body text is prohibited |

A note on the 12px floor: the nearest prior art sets direct end-of-line driver
labels at 10px bold. We set ours at **0.8125rem / 13px JetBrains Mono 500**
instead, accepting a slightly wider label gutter in exchange for staying above
the floor. That is our decision, not a measured convention.

## 7. Browser surfaces

The parts of a page nobody draws still carry the design: text selection, the
caret, custom scrollbars, focus rings, underline offset, and **the numerals in
tabular data**. All of them ship with browser defaults belonging to no design
system. Theme every one of them from the palette. The numerals item is the
whole of §2 above, and it is the one most often skipped.

Links are ink-coloured with an animated underline rather than a coloured link —
`text-decoration-color` transitions from `oklch(13% 0 0 / .28)` to the gold
accent over 0.12s. See [Motion](motion.md) for the timing and
[Colour system](color-system.md) for the tokens.

## 8. Prohibitions

These are binding here because they are typographic; the full catalogue lives
in [`/policies/editorial-voice.md`](../policies/editorial-voice.md).

- **A kicker or eyebrow above a heading.** This is the one outright ban rather
  than a default to argue against. The heading carries its own weight.
- **Gradient text.** Emphasis comes from weight or size.
- **Italic serif display headlines.** A familiar shortcut to an editorial look.
- **Justified body text**, and hyphenation-free justification especially.
- **Monospace as a costume for "technical".** JetBrains Mono appears on this
  site for code, data and measurement only — lap times, gaps, deltas, axis
  values. It is never the voice of a paragraph.
- **A system display face** (Impact, Arial Black, the platform sans) as the
  display voice.
- **Flat type hierarchy** — headings and body that differ by less than an
  obvious step in both size and weight.
- **Extreme negative tracking**, past the −0.04em floor.
