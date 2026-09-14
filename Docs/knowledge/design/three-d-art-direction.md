---
type: Reference
title: 3D art direction
description: What the 3D circuit renderer is for, how it is framed as an instrument panel set into a light page, and the tiering, camera, lighting and material rules that keep it honest.
tags:
  - design
  - threejs
  - 3d
  - art-direction
  - circuits
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: threejs_orbitcontrols
    resource: https://threejs.org/docs/pages/OrbitControls.html
    title: three.js — OrbitControls
  - id: threejs_renderer
    resource: https://threejs.org/docs/pages/WebGLRenderer.html
    title: three.js — WebGLRenderer
  - id: threejs_ktx2
    resource: https://threejs.org/docs/pages/KTX2Loader.html
    title: three.js — KTX2Loader
  - id: webkit_canvasbase
    resource: https://raw.githubusercontent.com/WebKit/WebKit/main/Source/WebCore/html/CanvasBase.cpp
    title: WebKit — CanvasBase.cpp (maxCanvasArea)
  - id: meshoptimizer
    resource: https://meshoptimizer.org/gltf/
    title: meshoptimizer — glTF compression
  - id: basis_universal
    resource: https://github.com/BinomialLLC/basis_universal
    title: Basis Universal
  - id: whatwg_canvas
    resource: https://html.spec.whatwg.org/multipage/canvas.html#the-canvas-element
    title: WHATWG HTML — the canvas element
  - id: web_dev_lcp
    resource: https://web.dev/articles/lcp
    title: web.dev — Largest Contentful Paint
  - id: rams_principles
    resource: https://www.vitsoe.com/us/about/good-design
    title: Dieter Rams — ten principles for good design
status: stable
---

# 3D art direction

## 1. What the 3D is for

An honest answer, because it decides placement.

**The 3D is scene-setting and spatial comprehension.** It answers *"what is
this place actually like?"* — the gradient at Eau Rouge, how tight the walls
are at Monaco, how long Monza really is — which no 2D map conveys. It is not a
substitute for analysis and it does not make anything measurable that was not
measurable before.

That answer places it precisely: **once per circuit page, as the focal moment,
and nowhere else.** The race-page replay is a different and smaller component —
a top-down or low-angle scrub of car positions, in service of an analytical
question, with no claim to being a spectacle.

The tension is worth naming rather than hiding. A 3D track is high non-data-ink
by construction; a grid of small-multiple track maps carries more information
per pixel. The 3D earns its place because spatial comprehension is genuinely
part of understanding a circuit and is genuinely absent from every 2D
alternative — not because it looks impressive. The moment a scene stops
answering that question it is decoration, and decoration is out of scope.

## 2. The instrument-panel framing

The scene is not a hero banner and it is not a full-bleed video substitute. It
is an **instrument panel set into a light editorial page**: a bounded dark
rectangle with an explicit edge, its own scoped token remap, and
`color-scheme: dark` declared locally.

```html
<figure class="f1-instrument f1-scene" role="group">
  <canvas tabindex="0" role="img" aria-label="…" aria-describedby="scene-help">
    <!-- Fallback DOM lives here: static SVG layout + corner table. -->
  </canvas>
  <figcaption>…</figcaption>
</figure>
```

This is what lets a dark WebGL canvas sit on a 97.8%-lightness page without a
theme switch, and it is the same mechanism the aesthetic reference uses for its
code blocks. The token remap is described in
[Colour system](color-system.md) §2.

Consequences that follow from the framing, not from taste:

- **The panel has a finite, stated size.** It does not expand to the viewport.
- **The chrome around it is instrument chrome** — a scrubber, a camera-target
  selector, a pause control — styled from the instrument token set, not from
  the paper set.
- **The single interface accent inside the panel is gold**, on the scrubber
  handle and the active indicator. Team colours appear only on cars.
- **`background: transparent` is not an option.** The panel's ground is
  `--f1-instrument`, and the renderer clears to it, so a failed WebGL context
  leaves a designed rectangle rather than a hole.

## 3. Tiering — the scope trap and its answer

Banking has to be hand-authored per corner. Kerbs and run-off have to be
procedurally generated. Track widths are missing for roughly twelve circuits.
Elevation is only trustworthy where telemetry exists, i.e. 2018 onward.
Multiplied across 78 circuits and about 160 layouts, **a polished 3D track is
affordable for perhaps 8–12 circuits, not for all of them.**

So 3D is tiered, and **the tier is stated on the page**. A reader should never
have to guess whether what they are looking at is surveyed or approximated.

| Tier | Count | Treatment |
| --- | ---: | --- |
| **Hero** | 8–12 | Hand-authored banking, real elevation, kerbs, run-off, custom camera choreography |
| **Standard** | ~40 | Procedural from centreline + width; flat or DEM-approximated; generic kerbs |
| **Outline** | remainder | 2D SVG layout only, from F1DB assets. **No 3D at all.** |

Hero order: Monza, Spa, Monaco, Suzuka, Silverstone, Interlagos, Zandvoort,
Singapore. One of them — Monza — is built end to end before any of the others
start, to prove the pipeline rather than to repeat a mistake eight times.

A circuit is an entity with a version history. Silverstone, Bahrain,
Yas Marina, Zandvoort, Albert Park, Spa, Suzuka and Hockenheim have all been
relaid, and picking one layout per circuit silently misattributes geometry.
Tier is assigned per **layout**, not per circuit.

## 4. Honesty in geometry

Rams' sixth principle — *good design is honest; it does not make a product more
innovative, powerful or valuable than it really is* — is the operative
constraint on the whole renderer.

| Do not | Because |
| --- | --- |
| Draw a smooth racing line from 5 Hz GPS | The source does not contain that curve |
| Render kerb detail on a Standard-tier circuit | The width data is procedural; the detail would be invented |
| Use DEM elevation for the track surface | Copernicus GLO-30 is a **surface** model at < 4 m LE90 — distant terrain only |
| Let banking emerge from the curve frame | Banking is authored data, not a side effect of geometry |
| Show a Standard tier with Hero-tier lighting | Fidelity of rendering implies fidelity of data |

### The track ribbon

Build the ribbon as a custom `BufferGeometry` on a **fixed world-up frame**,
not on `computeFrenetFrames`. The reasons matter, because the function's name
invites the wrong assumption:

1. three.js's `computeFrenetFrames` is misnamed — it is *already* a
   parallel-transport frame, not a true Frenet frame.
2. Its initial normal is chosen arbitrarily, so the starting roll is
   unpredictable.
3. Parallel transport conserves **twist**, not gravity. A track built on it
   self-banks through elevation change — the ribbon rolls where the real
   circuit is flat.
4. On a closed curve, the residual-twist correction is smeared along the whole
   loop, so an error at the join is distributed everywhere.

A real circuit is near-flat in roll except where it is deliberately banked.
Banking is therefore authored data applied to a gravity-aligned frame.

### Coordinates

FastF1 position `X`/`Y`/`Z` are in **1/10 metre from 2020 onward** — the unit
has a date cutoff that is easy to miss and produces a silently ten-times-wrong
scene.

For local ENU ↔ WGS84, do not use the naive equirectangular constant. Using the
equatorial radius `a = 6378137` on both axes gives **0.4–2.5 m of systematic
scale error** at F1 latitudes. Use the ellipsoidal radii:

```
k_east  = N(φ₀) · cos(φ₀)
k_north = M(φ₀)
```

which brings residual error below 0.1 m over a few kilometres.

Copernicus GLO-30 tile paths are deterministic in *form* but not in
*availability*: some tiles are withheld and at least one F1 venue (Baku)
returns 404. **Always handle the 404** — a missing DEM degrades to flat distant
terrain, not to a crash.

## 5. Camera language

The scene is calm. There is no idle animation, no autoplay, and nothing moves
that the reader did not move.

| Rule | Value |
| --- | --- |
| `controls.autoRotate` | **`false`**, always |
| Camera transitions | Damped and short. No cinematic fly-through |
| Default state | A composed static pose, already correct before any input |
| Lap "flight" | User-scrubbed on a timeline; it never plays itself |
| Motion under `prefers-reduced-motion` | Cut straight to the final pose; no tween |
| Field of view | Narrow enough that a corner reads as a corner, not as a fisheye |

`OrbitControls` defaults worth knowing when tuning: `keys`
`{LEFT:'ArrowLeft', UP:'ArrowUp', RIGHT:'ArrowRight', BOTTOM:'ArrowDown'}`,
`keyPanSpeed 7`, `keyRotateSpeed 1`, `autoRotate false`, `autoRotateSpeed 2.0`,
`enableDamping false`, `dampingFactor 0.05`, `minPolarAngle 0`,
`maxPolarAngle Math.PI`, `minDistance 0`, `maxDistance Infinity`. Enable
damping; clamp `maxPolarAngle` below the horizon so the camera cannot go
underground; clamp `minDistance`/`maxDistance` to the circuit's bounding box.

Three named camera positions per hero circuit, no more — the working-memory
limit applies to controls too:

1. **Plan** — the whole layout, aligned to the same rotation as the 2D map so
   the two read as the same object.
2. **Signature** — the one corner the circuit is known for, framed at eye
   height.
3. **Free** — orbit, with the clamps above.

Any camera move is user-initiated. An automatic transition longer than five
seconds running alongside body copy would require a pause control under
SC 2.2.2 regardless of any OS preference — the simplest way to satisfy that
criterion is to have nothing auto-play at all, which is also the aesthetic the
site wants. See [Accessibility](accessibility.md) and [Motion](motion.md).

## 6. Lighting and materials

The two AI-default aesthetic clusters for motorsport are **near-black with one
neon accent and glowing edges**, and **broadsheet hairlines with tracked mono
labels**. The first is what an unexamined 3D F1 scene becomes. Every rule here
exists to avoid landing in it by reflex.

| Direction | Rule |
| --- | --- |
| Key light | One directional key, high and slightly off-axis. Soft, not dramatic |
| Fill | Low-intensity ambient or a neutral hemisphere. No coloured rim light |
| Emissive | **None** on track, kerbs, barriers or terrain. No glowing edges |
| Track surface | Matte, low-specular, near-neutral. Reads as asphalt, not as wet vinyl |
| Kerbs | Flat colour, correct proportions, no bloom |
| Barriers and run-off | Neutral value separation; they are context, not subject |
| Sky / environment | Neutral, unobtrusive. No sunset gradient |
| Shadows | `PCFShadowMap`. `PCFSoftShadowMap` is deprecated-with-warning in r186 |
| Post-processing | Minimal. `RenderPipeline` (renamed from `PostProcessing` in **r183**, not r185) |
| Bloom | Off. If a scene needs bloom to look good, the lighting is wrong |
| Cars | `InstancedMesh` with per-instance colour, fed from the resolved team ink token |

Read colours into materials from the resolved CSS tokens —
`getComputedStyle(document.documentElement).getPropertyValue(...)` — so the
scene follows whichever token scope it is mounted in rather than carrying its
own duplicate palette.

The reference's one sanctioned zero-offset glow is the **LED/indicator**
affordance, `0 0 0 1px oklch(13% 0 0 / .12), 0 0 4px oklch(84% .19 80 / .6)`.
If the panel chrome wants an active-state indicator, that is the treatment —
and it is CSS on the chrome, never an emissive material in the scene.

## 7. Technical baseline

Verified against r186.

| Item | Value |
| --- | --- |
| three.js | **0.186.0** (r186, published 2026-09-08). Pin exactly — `^` ranges are unsafe on `0.x` |
| Release cadence | 8–11 weeks, so r187 lands ~Nov 2026 |
| Renderer | `WebGLRenderer` at launch. WebGPU/TSL tracked, not shipped |
| Timer | `import { Timer } from 'three'` — it moved to core at ~r179/r180. `three/addons/misc/Timer.js` is **404** |
| Meshopt decoder | `three/addons/libs/meshopt_decoder.module.js` — **not** under `loaders/`, which 404s. Only `DRACOLoader` and `KTX2Loader` live there |
| Post-processing | `RenderPipeline`, renamed in **r183** |
| Shadows | `PCFShadowMap` |
| Not on cdnjs | `three` is absent from cdnjs; it comes from jsDelivr or is bundled |

### Geometry and textures

**Geometry ships meshopt by default.** Its decoder runs at 3–6 GB/s on modern
desktop CPUs and preserves GPU-friendly vertex order; the competing approach
"maximise the compression ratio at the cost of disturbing the vertex/index
order (which makes the meshes inefficient to render on GPU) or decompression
performance". Racing lines and kerb strips are long thin geometry where that
ordering matters most. Draco is reserved for geometry-dominant models where
ratio beats decode cost.

**Textures ship as KTX2/Basis, always.** JPEG, PNG, WebP and AVIF shrink the
download only — they decode to full RGBA8 in VRAM. KTX2 stays compressed on the
GPU.

| Format | Wire | GPU |
| --- | --- | --- |
| RGBA8 uncompressed | — | 8 bpp per channel set |
| ETC1S | ~0.3–3 bpp | 4 bpp (BC1 / ETC1 / ETC2-RGB) |
| UASTC LDR 4×4 | larger | 8 bpp (ASTC 4×4 / BC7) |

Texture memory, MiB, base / with a full mip chain (×4/3):

| Size | RGBA8 | ETC1S-class 4 bpp | UASTC-class 8 bpp |
| --- | --- | --- | --- |
| 512² | 1.00 / 1.33 | — | — |
| 1024² | 4.00 / 5.33 | — | — |
| 2048² | 16.00 / 21.33 | 2.00 / 2.67 | 4.00 / 5.33 |
| 4096² | 64.00 / 85.33 | 8.00 / 10.67 | 16.00 / 21.33 |

ETC1S for bulk; UASTC for normal maps and hero art. `KTX2Loader` requires
`setTranscoderPath(...)` **and** `detectSupport(renderer)` before any load, and
the transcoder files must be copied into the static output.

```js
const loader = new KTX2Loader();
loader.setTranscoderPath('examples/jsm/libs/basis/');
loader.detectSupport(renderer);
const texture = await loader.loadAsync('surface.ktx2');
```

### Canvas limits

The widely-repeated "224 MB iOS canvas cap" is wrong. That number was
`ramSize() / 4` evaluated on a roughly 1 GB device, it counted 2D-canvas
backing store rather than WebGL texture memory, and the mechanism has been
removed from current WebKit.

What current WebKit enforces is a **per-canvas area** limit:
`maxCanvasArea()` returns `8192 × 8192` on iOS and `16384 × 16384` elsewhere,
with the failure surfacing as *"Canvas area exceeds the maximum limit (width *
height > N)."* That limit is measured in **device** pixels, so a 3× DPR phone
reaches it nine times faster than the CSS dimensions suggest.

```js
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
```

Budget texture memory from an actual inventory plus device-tier testing, not
from a constant. Instrument in development with `renderer.info.render.calls`,
`.triangles`, `.frame` and `renderer.info.memory.geometries`, `.textures`.

### Resilience

```js
canvas.addEventListener('webglcontextlost', e => e.preventDefault());
canvas.addEventListener('webglcontextrestored', () => rebuildFromSourceOfTruth());
```

Every GPU resource sits behind something that can rebuild it from JS-side
state, so recovery means "rebuild the scene from the source of truth" rather
than "reload the page". Dispose geometries, materials, textures and the
renderer on route change.

## 8. The canvas is never the LCP element

`<canvas>` is **not** an LCP candidate element. The candidates are `<img>`,
`<image>` inside `<svg>`, `<video>`, elements with a `url()` background image,
and block-level elements containing text.

This cuts both ways. A slow-booting scene does not directly blow LCP — but
whatever *is* the LCP gets delayed by everything the 3D pipeline does on the
main thread: script parse and compile, decoder worker spin-up, shader
compilation.

The rule, which suits the editorial aesthetic anyway:

1. **The LCP is typographic** — the circuit name and its opening paragraph — or
   a pre-rendered static track map.
2. The page renders complete. Then the scene mounts via `client:visible`,
   behind a **static poster frame** (the F1DB SVG layout, or a pre-rendered
   still of the composed pose).
3. The canvas box is reserved with `aspect-ratio` so CLS stays at 0.
4. The poster cross-fades out when the first WebGL frame lands — subject to
   `prefers-reduced-motion`, under which it simply swaps.
5. The 3D chunk stays under **350 kB gzip**, lazy.

The poster frame is not a loading state. It is the **permanent representation**
for every reader without WebGL, with forced colours active, with JavaScript
disabled, or using a screen reader — which is also why it is a real static SVG
with a real corner table inside the `<canvas>` element, per the WHATWG
requirement that authors supply content conveying "essentially the same
function or purpose as the canvas's bitmap". See
[Accessibility](accessibility.md) for the full four-layer pattern.

## 9. Race replay — the smaller component

Distinct from the circuit hero, and deliberately less.

| Property | Value |
| --- | --- |
| Camera | Top-down or low fixed angle. No orbiting during playback |
| Cars | `InstancedMesh`, per-instance team ink colour, driver code on hover |
| Control | A scrubber. It does not auto-play |
| Default payload | **2 Hz, ~623 kB** for one race of 20-car position data |
| On demand | 5 Hz (~1.31 MB) when the reader opens corner-level analysis |
| Encoding | int16 delta-encoded, planar, gzipped. float32 naive gzips only ~6% and is unusable |

Native position sampling is ~240 ms (measured median 241.0 ms on the 2024
British GP), so 5 Hz is close to native and 2 Hz is a real reduction rather
than a cosmetic one.

The replay is subordinate to the analytical charts on the race page, not the
other way round. The race page's focal moment is the race trace.

## 10. Open questions

- Whether the 3D track and the 2D mini-sector dominance map can share one
  segment array. They should, for coherence; it depends on whether elevation
  comes from telemetry `Z` or from an external source.
- Whether telemetry `Z` is usable at all for hero-tier elevation. It is
  GPS-derived and noisy, and the honesty rule in §4 bites hard here.
- MultiViewer's geometry — a ~730-point centreline plus corners and marshal
  sectors — is the best available, and **blocked**: no terms of use are
  published. Fallback is bacinger + TUMFTM + telemetry-derived centrelines.
- The exact byte size of the Basis transcoder WASM is unmeasured and sits in
  the critical path for first 3D paint.
