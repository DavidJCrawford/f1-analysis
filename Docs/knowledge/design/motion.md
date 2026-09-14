---
type: Reference
title: Motion
description: The measured easing and duration values, the chrome/content split that lets a camera move without breaking the interface's calm, and the reduced-motion behaviour required of both.
tags:
  - design
  - motion
  - animation
  - easing
  - reduced-motion
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
  - id: mdn_prefers_reduced_motion
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
    title: MDN — prefers-reduced-motion
  - id: wcag_pause_stop_hide
    resource: https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html
    title: WCAG 2.2 Understanding SC 2.2.2 Pause, Stop, Hide
  - id: mdn_view_transitions
    resource: https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API
    title: MDN — View Transition API
  - id: mdn_view_transition_obj
    resource: https://developer.mozilla.org/en-US/docs/Web/API/ViewTransition
    title: MDN — ViewTransition
  - id: w3c_c39
    resource: https://www.w3.org/WAI/WCAG21/Techniques/css/C39
    title: W3C Technique C39 — using the reduced-motion query
  - id: w3c_scr40
    resource: https://www.w3.org/WAI/WCAG21/Techniques/client-side-script/SCR40
    title: W3C Technique SCR40 — reducing motion in script
  - id: web_dev_inp
    resource: https://web.dev/articles/optimize-inp
    title: web.dev — Optimize INP
status: stable
---

# Motion

The page is quiet until you engage it. No autoplay, no idle animation, nothing
that asks for attention it has not been given. Motion on this site exists to
confirm an action, to carry continuity between two states, and — exactly once
per page at most — to make an authored entrance. Everything else is stillness.

## 1. Tokens

Easing. Two families, and no third.

| Token | Value | Use |
| --- | --- | --- |
| `--f1-ease` | `cubic-bezier(.2, .8, .2, 1)` | The standard curve. Chrome, state changes, hovers |
| `--f1-ease-out` | `cubic-bezier(.16, 1, .3, 1)` | Exponential ease-out — a confident arrival |
| `--f1-ease-out-quint` | `cubic-bezier(.22, 1, .36, 1)` | Softer arrival for larger moves |
| `--f1-ease-in-out` | `cubic-bezier(.65, 0, .35, 1)` | Symmetric moves only |

Durations.

| Token | Value |
| --- | --- |
| `--f1-quick` | `0.12s` |
| `--f1-fast` | `0.15s` |
| `--f1-settle` | `0.18s` |
| `--f1-base` | `0.3s` |
| `--f1-slow` | `0.6s` |

**No bounce. No elastic. No spring overshoot. Anywhere.** These are named
anti-patterns, and the restraint rule is explicit: use natural deceleration for
confident arrivals; do not reach for bounce by reflex.

## 2. The duration-to-meaning table

| Duration | Meaning |
| --- | --- |
| 100–150 ms | Immediate feedback |
| 150–300 ms | Routine state change |
| 300–500 ms | Layout, overlay, or view transition |
| 500–800 ms | A deliberately authored focal entrance |

Two supporting rules travel with it:

- **Exit faster than entrance.** Long feedback feels like latency.
- **Product and reading surfaces tighten further** — 150–250 ms on most
  transitions, and **no orchestrated page-load sequences**. Almost every page
  on this site is a reading surface.

## 3. The chrome / content split

This is the policy that resolves the one genuine conflict in the system. Every
transition in the interface sits at or below **0.18 s**. A camera flying Spa
cannot obey that. So motion is split, and the split is binding.

| | **Chrome motion** | **Content motion** |
| --- | --- | --- |
| What | Buttons, panels, tooltips, page transitions, chart state changes | Camera moves, car animation, replay scrubbing |
| Ceiling | **0.18 s, absolutely** | Exempt from the ceiling |
| Initiation | User action or state change | **User-initiated or user-scrubbable — never idle-looping** |
| Under reduced motion | Duration collapses; the state change still reads | Collapses to **a meaningful static frame** |
| Easing | `--f1-ease` | Damped, short |

The exemption is narrow and conditional. Content motion may take longer than
chrome motion **only because the reader is driving it**. The moment something
in the content layer starts moving on its own, it has stopped being content
motion and become an autoplaying animation, which this site does not have.

The longer steps in §1 — `--f1-base`, `--f1-slow` — exist for the one authored
focal entrance per page and for content motion. They are not available to
chrome.

## 4. Chart motion

| Rule | |
| --- | --- |
| On load | **No chart animates on load by default** |
| Permitted entrance | One staggered reveal, once, on first view, for a small-multiples grid or a table — where the content genuinely is a list |
| Stagger | Capped total delay. Never reinterpret every scrolled section as a staggered list |
| State transitions (filter, driver selection) | 150–200 ms ease-out on **opacity and stroke only** |
| Never animated | **Path geometry.** A line that morphs between two datasets shows a trajectory that did not happen |
| Hover promotion | Opacity and stroke-width only, at `--f1-quick` |

The prohibition on animating path geometry is a correctness rule, not a taste
rule. Interpolating between two lap charts draws intermediate positions no car
ever held.

## 5. Motion in the 3D layer

Fully specified in [3D art direction](three-d-art-direction.md); the motion
half restated here because it is where the policy is most often broken.

- `controls.autoRotate = false`, always.
- Camera transitions are damped and short. No cinematic fly-through.
- The lap "flight" is a **scrubber**. It does not play itself.
- Any non-essential loop stops when the canvas is offscreen or hidden —
  `IntersectionObserver` plus `cancelAnimationFrame`, or
  `content-visibility: auto` with `contain-intrinsic-size` and the
  `contentvisibilityautostatechange` event.
- Render on demand: `renderer.setAnimationLoop(null)` once the scene is
  settled, then re-render only on a controls `change` event.

That last point is a performance rule as much as an aesthetic one. INP
decomposes into input delay, processing duration and **presentation delay** — a
continuously running `requestAnimationFrame` loop delays the paint that closes
an interaction even when the handler itself is fast. A `render()` call
typically costs 2–8 ms against a 16.67 ms frame budget at 60 fps.

Where long synchronous work must be broken up, yield with a feature detect —
`scheduler.yield()` is **not Baseline**:

```js
function yieldToMain() {
  if (globalThis.scheduler?.yield) return scheduler.yield();
  return new Promise(r => setTimeout(r, 0));
}
```

A long task is **50 ms or longer**. Diagnose with the Long Animation Frames API
(`observe({ type: 'long-animation-frame', buffered: true })`), whose entries
expose `duration`, `blockingDuration`, `renderStart`, `styleAndLayoutStart` and
a `scripts[]` array — Chrome and Edge 123+ only, so it is a diagnostic, not a
gate.

## 6. Reduced motion

The aesthetic reference handles `prefers-reduced-motion` in **24 places** across
its stylesheets, while handling `prefers-color-scheme` in zero. The ratio is
instructive: the reduced-motion handling is the larger and more copyable part
of its motion system, not the easing curves.

```js
const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
if (reduced.matches) { /* … */ }
reduced.addEventListener('change', e => { /* react live, no reload */ });
```

A CSS media query is not sufficient on its own here: **canvas animation is
invisible to CSS**, so the 3D layer needs the JS gate. W3C techniques C39 (CSS)
and SCR40 (script) are the sufficient techniques; use both.

Baseline since January 2020. The two values are `no-preference` and `reduce`;
`@media (prefers-reduced-motion)` and
`@media (prefers-reduced-motion: reduce)` are equivalent.

### What "reduce" means here

Reduced motion means **fewer and gentler animations, not no feedback**. Erasing
all state-change feedback makes an interface harder to use, not easier.

| Element | Reduced-motion behaviour |
| --- | --- |
| Chrome transitions | Shortened; colour and opacity changes retained |
| Staggered entrances | Removed entirely; content present at rest |
| Camera tween | Cut straight to the final pose |
| Lap replay | Scrubbable timeline only, advancing solely on user input |
| Track ribbon reveal | Final frame, drawn immediately |
| Poster → canvas swap | Instant swap, no cross-fade |
| View transitions | Animation removed, DOM update kept |

The harm model is vestibular: large-field movement, parallax and camera roll
cause dizziness and nausea. Safe substitutes are opacity fades, colour
transitions and shortened durations.

## 7. Criteria that apply regardless of the OS setting

`prefers-reduced-motion` is a preference. These are requirements, and a reader
who has not set the preference is still entitled to them.

| Criterion | Level | Requirement |
| --- | --- | --- |
| **SC 2.2.2 Pause, Stop, Hide** | **A** | Any moving content that starts automatically, lasts more than five seconds and is presented in parallel with other content needs a mechanism to pause, stop or hide it. Auto-updating information needs one with **no five-second grace period** |
| **SC 2.3.1 Three Flashes** | A | No more than three general flashes or three red flashes in any one-second period |
| SC 2.3.3 Animation from Interactions | AAA | Interaction-triggered motion animation can be disabled unless essential; `prefers-reduced-motion` is the documented way to satisfy it |

A replay that started on scroll-into-view and ran a 90-second lap beside body
copy would sit squarely inside SC 2.2.2 and would need a real,
keyboard-focusable Pause control — not a hover-only affordance. **This site
avoids the criterion structurally by having nothing auto-play at all**, which
is both cheaper and more in keeping with the aesthetic than building the pause
button. Where a control does exist, it is a native focusable button meeting the
24×24 CSS px target minimum.

## 8. View transitions

A static multi-page site opts in with a CSS at-rule on both the outgoing and
incoming page:

```css
@view-transition { navigation: auto; }
```

Elements are paired across navigations with `view-transition-name`;
`view-transition-class` and `view-transition-scope` refine it. **Duplicate
`view-transition-name` values abort the transition**, so names must be unique
per page. The pseudo-element tree is `::view-transition` >
`::view-transition-group(name)` > `::view-transition-image-pair(name)` >
`::view-transition-old(name)` / `::view-transition-new(name)`. Related events
for the cross-document case: `PageRevealEvent` and `PageSwapEvent`.

Used sparingly and only where continuity carries meaning: a circuit's track
figure morphing from its index card into the page hero; a constructor's colour
bar sliding rather than blinking. Not as a default page cross-fade.

The default UA animation is a cross-fade plus a morph, so reduced motion must
kill it explicitly:

```css
@media (prefers-reduced-motion: reduce) {
  ::view-transition-group(*),
  ::view-transition-old(*),
  ::view-transition-new(*) { animation: none !important; }
}
```

For same-document transitions there is a better hook:
`ViewTransition.skipTransition()` skips the animation *without* skipping the
`document.startViewTransition()` callback, so the DOM update still applies and
state stays correct with no motion. The object also exposes `.ready`,
`.updateCallbackDone`, `.finished`, `waitUntil(promise)`, a `transitionRoot`
and `types`. In the cross-document case no script holds a handle, so the CSS
override above remains the right tool.

## 9. Implementation rules

- **Never animate `width`, `height`, `top`, `left` or `margin`.** Use transforms
  and FLIP.
- `will-change` only during a known animation, never as a standing declaration.
- CSS transitions and keyframes for declarative, bounded sequences; the Web
  Animations API where interruption or dynamic values are needed.
- **Content is visible in its default state**, so a failed script cannot hide
  the page. An element stuck at `opacity: 0` because a reveal handler never ran
  is a named failure pattern.
- Bound expensive effects — blur, `backdrop-filter`, large shadows — to isolated
  regions, and measure on target devices rather than assuming.
- Theme the surfaces the animation sits inside: selection colour, caret,
  scrollbars, focus rings.

## 10. Named anti-patterns

Tested against on every review pass.

| Anti-pattern | |
| --- | --- |
| Pulsing status dot | Keep static status still; use motion for activity that matters |
| Blinking cursor on static copy | Decorative, and it reads as a broken input |
| Auto-scrolling marquee | — |
| Bounce or elastic easing | — |
| Animation that changes layout | Reflow, not motion |
| Images that transform on hover | — |
| Content hidden at rest awaiting a reveal handler | Fails silently and invisibly |
| One identical entrance on every section | Scattered effects, not an authored moment |
| An orchestrated page-load sequence | Explicitly banned on reading surfaces |

The test for whether a motion idea is real: name the one focal moment, the
continuity transitions, the feedback, and the budget, **before** writing any
animation. A generic fade-and-rise, a hover lift, a parallax layer or a scroll
reveal is not a thesis.
