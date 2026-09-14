---
type: Reference
title: Performance budgets
description: The Core Web Vitals targets, JS and data byte budgets, GPU and canvas limits, and long-task rules that every page on this site is measured against.
resource: https://web.dev/articles/vitals
tags: [performance, core-web-vitals, lcp, inp, cls, budget, threejs, canvas, webgl]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: web_vitals
    resource: https://web.dev/articles/vitals
    title: web.dev — Core Web Vitals
  - id: web_lcp
    resource: https://web.dev/articles/lcp
    title: web.dev — Largest Contentful Paint
  - id: web_inp
    resource: https://web.dev/articles/inp
    title: web.dev — Interaction to Next Paint
  - id: optimize_long_tasks
    resource: https://web.dev/articles/optimize-long-tasks
    title: web.dev — Optimize long tasks
  - id: mdn_scheduler_yield
    resource: https://developer.mozilla.org/en-US/docs/Web/API/Scheduler/yield
    title: MDN — Scheduler.yield()
  - id: mdn_content_visibility
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/content-visibility
    title: MDN — content-visibility
  - id: loaf
    resource: https://developer.chrome.com/docs/web-platform/long-animation-frames
    title: Chrome — Long Animation Frames API
  - id: webkit_canvasbase
    resource: https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/html/CanvasBase.cpp
    title: WebKit Source/WebCore/html/CanvasBase.cpp
  - id: three_webglrenderer
    resource: https://threejs.org/docs/pages/WebGLRenderer.html
    title: three.js WebGLRenderer documentation
  - id: pages_limits
    resource: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
    title: GitHub Pages limits
status: stable
---

# Performance budgets

A budget is only real if it fails a build. Everything here is either a target
Lighthouse CI gates on, or a hardware limit that decides what can be attempted.

## 1. Core Web Vitals

Standard thresholds, all assessed at the **75th percentile of field data across
mobile and desktop**, and a page passes only if all three pass:

| Metric | Good | Needs improvement | Poor |
| --- | --- | --- | --- |
| LCP | ≤ 2.5 s | 2.5–4.0 s | > 4.0 s |
| INP | ≤ 200 ms | 201–500 ms | > 500 ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |

This project's own targets are tighter than the standard on LCP, because the
pages are mostly text and there is no excuse:

| Metric | Project target |
| --- | --- |
| LCP, all pages | **< 2.0 s on 4G** |
| INP | < 200 ms |
| CLS | < 0.1 |

INP replaced FID in March 2024 and, unlike FID, "observes the latency of all
click, tap, and keyboard interactions that occur throughout the lifespan of a
user's visit to a page", reporting roughly the worst one. It decomposes into
three phases: **input delay** (before handlers run), **processing duration**
(handler execution) and **presentation delay** (until the next frame paints).

Only click, tap and keypress count. Scrolling, hovering and zooming are excluded —
which conveniently means **orbit-dragging a three.js scene does not register**,
but clicking a corner hotspot does.

## 2. Byte budgets

| Budget | Target |
| --- | --- |
| JS on a non-3D page | **< 40 kB gzip** |
| Initial data per race page | **< 250 kB** |
| 3D chunk, lazily fetched | **< 350 kB gzip** |
| Replay payload, 2 Hz, on demand | ~623 kB |
| Search, total network payload | < 300 kB |

The 40 kB figure is achievable only because Astro ships zero JS by default; an
archival-tier race page — the ~85% case — ships none at all. See
[Site architecture](site-architecture.md).

The replay payload sits deliberately *outside* the initial-data budget: it is
fetched on user intent, not on page load. The 2 Hz/5 Hz split and its measured
fidelity are in [Telemetry encoding](telemetry-encoding.md).

**The three.js chunk is the number to watch.** three.js tree-shaking is
imperfect — importing only `Vector2` from `three` has historically still produced
~295 kB uncompressed — so budget roughly **600 kB raw / ~150 kB gzipped** for the
core chunk and treat it as a deliberate, isolated, lazily-fetched cost rather than
something a bundler will fix. That figure is an **estimate, not a measurement**;
a throwaway build of a minimal r186 scene through Vite 8/Rolldown with Oxc minify
should establish the real one before the 350 kB gate is enforced.

Note also that `build.chunkSizeWarningLimit` is 500 kB and three.js will trip it.
Raise it deliberately in config rather than learning to ignore the warning.

## 3. LCP: the canvas rule

**`<canvas>` is not an LCP candidate element.** The candidate types are: `<img>`;
`<image>` inside `<svg>`; `<video>`; elements with a background image set via
`url()`; and block-level elements containing text nodes or inline-level text
children.

Two consequences that pull in opposite directions:

1. **Good:** a slow-booting 3D scene cannot itself blow LCP.
2. **Bad:** whatever text or image *is* the LCP gets delayed by everything the 3D
   pipeline does on the main thread — script parse and compile, GLTF/Draco/KTX2
   worker spin-up, shader compilation. LCP still degrades, indirectly.

The design rule, which happens to suit the editorial aesthetic anyway:

- The **circuit name, race headline, or a pre-rendered static SVG/AVIF track map
  is the LCP element.** Never the canvas.
- Preload the display font (`<link rel="preload" as="font" crossorigin>`), which
  Astro's Fonts API emits.
- `fetchpriority="high"` on the hero image, in the image case.
- Boot three.js **only after** LCP: mount inside an `IntersectionObserver` or a
  `requestIdleCallback` after `load`, with a dynamic `import()` so the bundle is
  never in the critical path.
- Keep the static track map in place as the canvas's fallback content, so there
  is never a blank rectangle, and cross-fade it out when the first WebGL frame
  lands — subject to `prefers-reduced-motion`.
- **Reserve the canvas box with `aspect-ratio`** to keep CLS at 0.

## 4. INP and the render loop

| Threshold | Value |
| --- | --- |
| Long task | **50 ms or longer** |
| Blocking time | task duration − 50 ms |
| Frame budget at 60 fps | 16.67 ms |
| Frame budget at 120 fps | 8.33 ms |
| Realistic app-JS budget per frame | ~5 ms |
| `renderer.render()` alone | typically 2–8 ms |

Because INP's third phase is presentation delay, **a continuously running
`requestAnimationFrame` loop inflates INP even when the interaction handler itself
is fast** — the paint that closes the interaction queues behind the render.

Four mitigations, in order of how much they buy:

1. **Render on demand.** `renderer.setAnimationLoop(null)` once the scene is
   settled; re-render only on control `change` events. This also saves battery
   and satisfies the site's motion policy, which forbids idle animation anyway.
2. **Gate by visibility.** `content-visibility: auto; contain-intrinsic-size: auto
   500px;` (Baseline September 2024) plus the `contentvisibilityautostatechange`
   event to start and stop the loop as the canvas enters and leaves the viewport.
3. **OffscreenCanvas in a worker** for heavy scenes — genuinely effective, but it
   adds the complexity of passing theme tokens and interaction events across the
   worker boundary, and it is **unmeasured** here.
4. **Yield inside long synchronous work.**

```js
function yieldToMain() {
  if (globalThis.scheduler?.yield) return scheduler.yield();
  return new Promise(r => setTimeout(r, 0));
}
```

**`scheduler.yield()` is not Baseline.** MDN states plainly: "This feature is not
Baseline because it does not work in some of the most widely-used browsers" — it
is flagged Limited availability. Shipping it without the guard above means the
mitigation simply does not run for a large share of visitors.
`scheduler.postTask` priorities, where available, are `user-blocking`,
`user-visible`, `background`.

**Diagnosis: the Long Animation Frames API.**

```js
new PerformanceObserver(list => { /* … */ })
  .observe({ type: 'long-animation-frame', buffered: true });
```

Entries expose `duration`, `blockingDuration`, `renderStart`,
`styleAndLayoutStart`, `firstUIEventTimestamp`, and a `scripts[]` array with
`sourceURL`, `sourceFunctionName`, `invoker`, `invokerType`,
`forcedStyleAndLayoutDuration` and `pauseDuration`. **Chrome/Edge 123+ only** —
not Firefox, not Safari. It is a diagnostic, not a metric source.

The one decode job on the critical-ish path is the int16-delta reconstruction:
at 5 Hz that is roughly 880,000 delta accumulations plus a `Float32Array` fill.
If it exceeds 50 ms on a mid-range phone it must move to a worker. **Unmeasured.**

## 5. Canvas and GPU limits

### The real canvas limit is area, not total memory

The widely-cited "224 MB total canvas memory cap on iOS" is wrong and should not
be designed against. In the WebKit source that implemented it,
`maxActivePixelMemory()` returned `ramSize() / 4` on iOS — 224 MB is simply what
that evaluates to on a ~1 GB device. It counted 2D-canvas `ImageBuffer`
backing-store pixels, not WebGL texture VRAM, and the mechanism no longer exists
in current WebKit.

**What current WebKit enforces is a per-canvas *area* limit.**
`CanvasBase::maxCanvasArea()` returns:

| Platform | Max area | Megapixels |
| --- | --- | ---: |
| iOS family | **8192 × 8192** | 67.1 |
| Everywhere else | **16384 × 16384** | 268.4 |

Exceeding it makes the canvas fail to allocate, with the console message
"Canvas area exceeds the maximum limit (width * height > N)." The source comment
explains the design: "Firefox limits width/height to 32767 pixels, but slows down
dramatically before it reaches that limit. We limit by area instead, giving us
larger maximum dimensions, in exchange for a smaller maximum canvas size."

**The limit is measured in device pixels**, so on a 3× DPR iPhone a CSS-sized
canvas backed by `devicePixelRatio` hits the ceiling nine times faster than its
CSS dimensions suggest. Hence the standing rule:

```js
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
```

Capping at 2 also avoids rendering 2.25× the pixels of a 2× cap for no
perceptible gain.

### Texture memory

Budget from an actual texture inventory plus device-tier testing, not from a
constant. The arithmetic (MiB, base / with a full mip chain, ×4/3):

| Format | 512 | 1024 | 2048 | 4096 |
| --- | --- | --- | --- | --- |
| RGBA8 uncompressed | 1.00 / 1.33 | 4.00 / 5.33 | **16.00 / 21.33** | 64.00 / 85.33 |
| ETC1S / BC1 / ETC2-RGB (4 bpp GPU) | — | — | **2.00 / 2.67** | 8.00 / 10.67 |
| UASTC → ASTC 4×4 or BC7 (8 bpp GPU) | — | — | **4.00 / 5.33** | 16.00 / 21.33 |

Against a conservative 64 MB texture allowance that is roughly **12 2K UASTC
textures with mips or 24 2K ETC1S**; against 128 MB, ~24 / ~48.

The shock worth internalising: a 200 kB PNG at 2048×2048 becomes ~21 MiB of VRAM
once decoded and mipmapped. **JPEG, PNG, WebP and AVIF shrink the download only.**
KTX2/Basis is the only format that reduces GPU memory, because it stays
compressed in VRAM.

### Scene budget

| Quantity | Mobile | Desktop |
| --- | --- | --- |
| Draw calls | < 100 (~0.1 ms CPU each) | several hundred to low thousands |
| Vertices | < 100,000 | — |
| Triangles, total scene | < 500,000 for broad compatibility | — |
| Triangles, hero object | 50k–100k | — |
| Triangles, environment prop | 500–5,000 each | — |
| Texture size | ≤ 2048 px unless hero | ≤ 2048 px unless hero |
| Shadow map | 512–1024 | 1024–2048 (4096 only when critical) |
| Dynamic lights | ≤ 3 | ≤ 3 |

Never use a `PointLight` shadow — it is six render passes, one per cube face.

**The reassuring calculation:** a 2,000-segment track ribbon is ~4,002 vertices
and ~8,000 triangles in **one draw call**; 4,000–8,000 segments is affordable and
gives smooth Eau Rouge. The scene risk is grandstands, trees and post-processing,
not the track. On mobile, limit post-processing to SMAA + `OutputPass`, gate bloom
behind a desktop check, and consider rendering effects at half resolution — which
roughly doubles frame rate when fill-rate bound.

Renderer config when post-processing supplies AA:
`{ powerPreference: 'high-performance', antialias: false, stencil: false, depth: false }`.

### Instrumentation and resilience

In dev, log `renderer.info.render.calls`, `.triangles`, `.frame`, `.points`,
`.lines`, plus `renderer.info.memory.geometries`, `.memory.textures` and
`renderer.info.programs`, on a rolling-average frame timer driven by `Timer` (not
the deprecated `Clock`).

Handle exhaustion gracefully:
`canvas.addEventListener('webglcontextlost', e => e.preventDefault())`, then
rebuild every GPU resource on `webglcontextrestored`. Hold GPU resources behind a
class that can rebuild from JS-side state, so recovery is "rebuild scene from
source of truth". Dispose geometries, materials and textures and call
`renderer.dispose()` on route change.

## 6. Delivery-side constraints on the budget

Two host behaviours change what a byte budget even means here:

- **Every asset carries `cache-control: max-age=600`, including content-hashed
  bundles.** So chunk *count* is a first-class budget: after ten minutes each
  separately-fetched chunk costs a revalidation RTT, answered `304` off the weak
  ETag. Prefer a few coarse, stable chunks.
- **gzip only, never brotli.** Compression must live in the asset format
  (KTX2/Basis, meshopt, int16 quantisation), not in the transport, and a
  Brotli-11 build step buys nothing.

Both are established in [GitHub Pages constraints](github-pages-constraints.md).

## 7. Measurement

| Layer | Tool |
| --- | --- |
| Field | `web-vitals` 6.2.1 in the page; CrUX via the PageSpeed Insights API (there is no server to receive beacons) |
| Lab, gated in CI | Lighthouse CI budgets |
| Frame-level diagnosis | Long Animation Frames API (Chrome/Edge 123+) |
| GPU | `renderer.info` in a dev overlay |
| Size | `du -sh dist` in CI, failing above ~700 MB |

Lighthouse CI is one of the blocking quality gates; the full gate list is in
[Build and release](build-and-release.md).

## Open items

- The gzipped size of a minimal three.js r186 scene through Vite 8/Rolldown is
  **estimated at ~150 kB, not measured.** The 350 kB 3D-chunk gate should be
  calibrated against a real build.
- The int16-delta decode cost on a mid-range phone is **unmeasured** (§4).
- Whether iOS Safari sustains the full scene at 60 fps on a 3–4 year old iPhone is
  **unmeasured**; the scene budget above is documented best practice rather than
  device testing, and the texture arithmetic is arithmetic.
- Whether OffscreenCanvas + worker is warranted is **undecided** pending a
  measurement on a mid-range Android device.
- Whether a cache-first service worker is acceptable — the only route to
  long-lived caching on this host — is **an open decision**, weighed against
  stale-content risk during a race weekend.
