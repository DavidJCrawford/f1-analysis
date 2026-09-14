---
type: Policy
title: Motion policy
description: The chrome/content motion split, the token set and duration budget for each half, and the reduced-motion contract every animated component must satisfy.
tags: [motion, animation, easing, accessibility, reduced-motion, threejs, performance]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: impeccable_base_css
    resource: https://impeccable.style/_astro/Base.BzPGTuBF.css
    title: Reference site compiled base stylesheet (motion tokens)
  - id: impeccable_animate
    resource: https://github.com/pbakaus/impeccable/blob/main/.claude/skills/impeccable/reference/animate.md
    title: Impeccable animate reference (duration-to-meaning table)
  - id: impeccable_operate
    resource: https://github.com/pbakaus/impeccable/blob/main/.claude/skills/impeccable/reference/operate.md
    title: Impeccable operate reference (product-surface motion rules)
  - id: impeccable_slop
    resource: https://impeccable.style/slop/
    title: Impeccable slop catalogue (motion anti-patterns)
  - id: threejs
    resource: https://github.com/mrdoob/three.js
    title: three.js r186 API surface
  - id: mdn_prm
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion
    title: prefers-reduced-motion media feature
status: stable
---

# Motion policy

A camera flying Spa cannot obey a 0.18 second ceiling. A tooltip must. So
motion is split in two, the split is a policy rather than a judgement call, and
each half has its own budget, its own token set and its own reduced-motion
behaviour.

## 1. The split

| | **Chrome motion** | **Content motion** |
| --- | --- | --- |
| What | Buttons, links, panels, tooltips, disclosure, tabs, page transitions, chart hover states | Camera moves, car animation, replay scrubbing, lap-by-lap playback |
| Purpose | Feedback and continuity | Information. The movement *is* the data |
| Duration | **0.18 s ceiling, absolute** | Exempt from the ceiling |
| Trigger | User action or state change | **User-initiated or user-scrubbable, never idle-looping** |
| Easing | One curve (§2) | Physical continuity, whatever the scene needs |
| Reduced motion | Collapses to an instant state change that preserves the feedback | **Collapses to a meaningful static frame** |
| Runs offscreen | n/a | Never. Loops stop when hidden |

The test for which half something belongs to: **if you removed the motion,
would the reader lose information?** A panel that slides rather than appears
loses nothing — chrome. A replay that shows where twenty cars were at lap 34
loses everything — content. Anything that fails the test and still moves is
decoration and does not ship.

## 2. Tokens

```css
:root {
  /* Easing — four curves, no others. No bounce, no elastic, no spring. */
  --ease-standard:  cubic-bezier(.2, .8, .2, 1);   /* chrome default */
  --ease-out:       cubic-bezier(.16, 1, .3, 1);   /* confident arrival */
  --ease-out-quint: cubic-bezier(.22, 1, .36, 1);  /* long, understated */
  --ease-in-out:    cubic-bezier(.65, 0, .35, 1);  /* symmetric, rare */

  /* Chrome durations — the ceiling is --dur-settle. */
  --dur-quick:  .12s;   /* immediate feedback: hover, focus ring, underline */
  --dur-fast:   .15s;   /* routine state change */
  --dur-settle: .18s;   /* the ceiling. Panels, disclosure, page transition */

  /* Content durations — available to the scene layer only. */
  --dur-base:   .3s;
  --dur-slow:   .6s;
}
```

The duration-to-meaning table the tokens implement:

| Range | Meaning | Where it is allowed |
| --- | --- | --- |
| 100–150 ms | Immediate feedback | Chrome |
| 150–300 ms | Routine state change | Chrome, capped at 180 ms here |
| 300–500 ms | Layout, overlay or view transition | Content only |
| 500–800 ms | One deliberately authored focal entrance | Content only, once per page |

Three rules carried from the same source and adopted without modification:

- **Exit faster than entrance.** A dismissal at 0.12 s against an entrance at
  0.18 s.
- **Long feedback feels like latency.** A 400 ms button response reads as a
  slow site, not a considered one.
- **Reading and product surfaces tighten further**, to 150–250 ms, with no
  orchestrated page-load sequences at all. Almost every page on this site is a
  reading surface.

## 3. Chrome motion rules

1. **0.18 s is a ceiling, not a target.** Most chrome transitions are 0.12 s.
2. **One property class.** Transition `opacity`, `transform`, `color`,
   `background-color`, `border-color`, `text-decoration-color`, `box-shadow`,
   `outline-color`. Never `width`, `height`, `top`, `left`, `margin` or
   `padding` — use a transform, or FLIP.
3. **Content is visible in its default state.** Nothing starts at `opacity: 0`
   waiting for a script. A failed script must not be able to hide the page.
4. **No entrance animation on scroll as a default.** Scroll-driven motion is
   permitted only where the scroll relationship itself carries meaning, and
   then with a static fallback.
5. **Stagger only when a list appears as a list**, with a capped total delay.
   A page is not a staggered list.
6. **`will-change` only for the duration of a known animation**, removed after.
7. **One authored moment per page.** Not a generic fade-and-rise on every
   section. On a circuit page the authored moment belongs to the 3D scene, and
   the chrome therefore gets none.

Reference implementation:

```css
.control {
  transition:
    background-color var(--dur-quick) var(--ease-standard),
    border-color     var(--dur-quick) var(--ease-standard),
    transform        var(--dur-quick) var(--ease-standard);
}
.control:active { transform: translateY(1px); }

.panel {
  transition:
    opacity    var(--dur-settle) var(--ease-out),
    transform  var(--dur-settle) var(--ease-out),
    visibility 0s linear var(--dur-settle);
}
.panel[hidden] { transition-duration: var(--dur-quick); } /* exit is faster */
```

## 4. Content motion rules

Content motion is exempt from the ceiling and bound by four conditions
instead. All four, not a choice of them.

1. **User-initiated or user-scrubbable.** A replay starts because the reader
   pressed play or dragged the scrubber. A camera moves because the reader
   moved it, or chose a named view.
2. **Never idle-looping.** No ambient rotation, no attention-seeking drift, no
   autoplay. The page is quiet until engaged.
3. **Stops when it cannot be seen.** An `IntersectionObserver` cancels the
   render loop when the canvas leaves the viewport, and `visibilitychange`
   cancels it when the tab is hidden.
4. **Collapses to a meaningful static frame under reduced motion.** §5.

```js
// Scene loop gating. `Timer` is imported from three's core — the addon path
// `three/addons/misc/Timer.js` is a 404 as of r186.
import { Timer } from 'three';

const timer = new Timer();
let frame = 0;

function start() {
  if (frame) return;
  const tick = (now) => {
    timer.update(now);
    scene.advance(timer.getDelta());
    renderer.render(scene.root, scene.camera);
    frame = requestAnimationFrame(tick);
  };
  frame = requestAnimationFrame(tick);
}

function stop() {
  cancelAnimationFrame(frame);
  frame = 0;
}

new IntersectionObserver(
  ([entry]) => (entry.isIntersecting ? start() : stop()),
  { threshold: 0 },
).observe(canvas);

document.addEventListener('visibilitychange', () => {
  document.hidden ? stop() : start();
});
```

**The canvas is never the LCP element.** The page renders complete, a static
poster frame occupies the canvas box at its final aspect ratio, and the scene
mounts via `client:visible` behind it. This is a layout-stability requirement
(CLS budget < 0.1) as much as a performance one; the 3D chunk is budgeted at
< 350 kB gzip, lazily loaded.

Canvas sizing is bounded by a **per-canvas area limit** — 8192 × 8192 on iOS,
16384 × 16384 elsewhere. Budget texture memory from an actual inventory and
device-tier testing, not from a remembered figure.

## 5. The reduced-motion contract

`prefers-reduced-motion: reduce` is honoured everywhere, and honouring it is
not the same as switching motion off. The contract has three clauses:

1. **Chrome motion becomes an instant state change that still reads as
   feedback.** The hover state still changes; it changes at 0 s. Feedback is
   never removed, because removing it removes the affordance.
2. **Content motion collapses to a meaningful static frame** — the specific
   frame that answers the question the motion was answering. Not a blank
   canvas, not a first frame, not a spinner.
3. **The control stays.** A reader who prefers reduced motion still gets the
   scrubber, still gets the lap selector, still gets the camera presets. The
   preference reduces automatic movement; it does not remove agency.

Component contract, exhaustively:

| Component | Full motion | Reduced motion |
| --- | --- | --- |
| Circuit 3D hero | Authored camera move on load; orbit and zoom on drag | Static render from the authored final camera position, with the track fully in frame. Orbit still available on explicit drag; no automatic move |
| Race replay | Cars animate along the 2 Hz position series | Renders the frame at the currently selected lap. The scrubber still moves the frame; nothing plays |
| Lap chart / race trace | Lines draw in on first view | Lines present at full opacity immediately |
| Mini-sector dominance | Segments colour in sequence | All segments coloured on render |
| Championship swing | Series animates across the season | Final state, with the season slider still operable |
| Page transition | Cross-fade at 0.18 s | Instant |
| Tooltip / panel | Fade and 4 px rise | Instant appearance, same final position |
| Focus ring | 0.12 s colour transition | Instant |
| Stint Gantt | Bars grow from the stint start | Bars at full length |

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
}
```

The blanket rule handles CSS. It does not handle the scene layer, which must
check the preference itself and react to changes at runtime:

```js
const reduce = window.matchMedia('(prefers-reduced-motion: reduce)');

function applyMotionPreference(mq) {
  scene.autoplay = !mq.matches;
  if (mq.matches) {
    scene.seekToAuthoredFrame();  // the meaningful static frame
    scene.renderOnce();
    stop();
  } else {
    start();
  }
}

applyMotionPreference(reduce);
reduce.addEventListener('change', applyMotionPreference);
```

Two details that are routinely missed and are defects here:

- **The preference can change mid-session.** Listen for `change`; do not read
  the media query once at mount.
- **The reduced-motion path is the one that ships broken.** It is tested on
  every animated component, in CI, by forcing the emulated preference and
  asserting the static frame is non-empty and carries the same information as
  the animated end state.

## 6. Banned motion patterns

Each of these is a named detector rule; a hit fails the build.

| Pattern | Note |
| --- | --- |
| Pulsing status dot | Keep static status still; use motion for activity that matters |
| Blinking cursor on static copy | Decoration imitating a terminal |
| Auto-scrolling marquee | |
| Bounce or elastic easing | Not in the four-curve set, at any duration |
| Animation that changes layout | Never animate width/height/top/left/margin |
| Images that transform on hover | |
| Content hidden at rest | `opacity: 0` awaiting a reveal handler |
| Orchestrated page-load sequences | Reading surfaces get none |
| Scroll-reveal applied to every section | One authored moment, not a pattern |
| Idle camera drift on the 3D canvas | Violates §4.2 directly |
| Zero-offset coloured glow used as elevation | Glow is reserved for a literal indicator affordance, never for depth |

## 7. Performance budget

| Constraint | Value |
| --- | --- |
| INP | < 200 ms |
| CLS | < 0.1 |
| Long task | **50 ms or longer** |
| 3D chunk, lazy | < 350 kB gzip |
| Replay payload, 2 Hz | ~623 kB, on demand |
| JS on a non-3D page | < 40 kB gzip |

Work that risks a long task is yielded. `scheduler.yield()` is **not Baseline**
— feature-detect and fall back:

```js
const yieldToMain = globalThis.scheduler?.yield
  ? () => globalThis.scheduler.yield()
  : () => new Promise((r) => setTimeout(r, 0));

for (const chunk of chunks) {
  decode(chunk);
  await yieldToMain();
}
```

Renderer settings that interact with motion cost, verified against r186:

| Setting | Choice |
| --- | --- |
| Renderer | `WebGLRenderer`. WebGPU/TSL is tracked, not shipped |
| Shadows | `PCFShadowMap`. `PCFSoftShadowMap` is deprecated-with-warning in r186 |
| Post-processing | `RenderPipeline` (renamed from `PostProcessing` in **r183**) |
| Cars | `InstancedMesh` with per-instance colour |
| Version pin | `three@0.186.0`, exact. `^` ranges are unsafe on `0.x` semver, and `postprocessing`'s `< 0.187.0` peer bound bites when r187 lands |

## 8. Review checklist

- [ ] Every chrome transition is ≤ 0.18 s on one of the four curves.
- [ ] No transition on a layout property.
- [ ] Nothing animates without a user action or a state change.
- [ ] No loop runs while its canvas is offscreen or the tab is hidden.
- [ ] Every animated component has a row in §5 and it is implemented.
- [ ] The reduced-motion static frame carries the same information as the
      animated end state.
- [ ] The media query is listened to, not sampled once.
- [ ] The canvas is not the LCP element; a poster frame holds its box.
- [ ] No pattern from §6 present.
- [ ] INP and CLS within budget on the tested device tiers.
