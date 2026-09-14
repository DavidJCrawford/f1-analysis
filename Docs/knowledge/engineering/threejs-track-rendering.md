---
type: Reference
title: three.js track rendering
description: The r186-specific facts, geometry construction and animation patterns that produce a correctly-oriented, correctly-banked 3D circuit in the browser.
resource: https://github.com/mrdoob/three.js/tree/r186
tags: [threejs, webgl, buffergeometry, curves, instancedmesh, ktx2, r186]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: three_npm
    resource: https://registry.npmjs.org/three/latest
    title: npm registry metadata for three@0.186.0
  - id: three_curve_src
    resource: https://raw.githubusercontent.com/mrdoob/three.js/r186/src/extras/core/Curve.js
    title: three.js r186 src/extras/core/Curve.js
  - id: three_extrude_src
    resource: https://raw.githubusercontent.com/mrdoob/three.js/r186/src/geometries/ExtrudeGeometry.js
    title: three.js r186 src/geometries/ExtrudeGeometry.js
  - id: three_instancedmesh
    resource: https://threejs.org/docs/pages/InstancedMesh.html
    title: three.js InstancedMesh documentation
  - id: three_linematerial
    resource: https://threejs.org/docs/pages/LineMaterial.html
    title: three.js LineMaterial documentation
  - id: three_ktx2
    resource: https://threejs.org/docs/pages/KTX2Loader.html
    title: three.js KTX2Loader documentation
  - id: three_webgpu_manual
    resource: https://threejs.org/manual/en/webgpurenderer.html
    title: three.js WebGPURenderer manual
  - id: three_releases
    resource: https://github.com/mrdoob/three.js/releases
    title: three.js release notes
  - id: postprocessing_npm
    resource: https://registry.npmjs.org/postprocessing/latest
    title: pmndrs postprocessing npm metadata
  - id: camera_controls_npm
    resource: https://registry.npmjs.org/camera-controls/latest
    title: camera-controls npm metadata
  - id: meshline_dts
    resource: https://cdn.jsdelivr.net/npm/meshline@3.3.1/dist/MeshLineMaterial.d.ts
    title: meshline 3.3.1 type declarations
  - id: basis_universal
    resource: https://github.com/BinomialLLC/basis_universal
    title: Basis Universal README
  - id: fastf1_circuit_info
    resource: https://docs.fastf1.dev/circuit_info.html
    title: FastF1 CircuitInfo documentation
status: stable
---

# three.js track rendering

The circuit page's focal moment is a 3D track. This document records the r186
facts that make it correct, and the two construction choices — the frame and the
arc-length parameterisation — that are wrong by default and silently so.

## 1. Version, cadence and pins

**three 0.186.0 (r186), published to npm 2026-09-08.** three.js is versioned
`0.<revision>.0`, so a `^0.186.0` range will **not** pick up r187 — but `^` on
`0.x` is unsafe in general and the project pins exactly.

npm publish dates and gaps for the last four revisions:

| Release | npm publish | Gap from previous |
| --- | --- | ---: |
| 0.183.0 | 2026-02-18 | 70 days |
| 0.184.0 | 2026-04-16 | 58 days |
| 0.185.0 | 2026-06-25 | 70 days |
| 0.186.0 | 2026-09-08 | 75 days |

Cadence is therefore **8–11 weeks**, which puts r187 at roughly **November 2026** —
exactly when `postprocessing`'s `< 0.187.0` peer bound bites (§8).

The full `exports` map has seven entries, not the four usually quoted:
`.` (conditional `{ import: ./build/three.module.js, require: ./build/three.cjs }`),
`./tsl`, `./src/*`, `./addons`, `./webgpu`, `./addons/*` (→ `examples/jsm/*`),
and `./examples/jsm/*`.

Pinned companion versions:

| Package | Version | Peer range on three |
| --- | --- | --- |
| `three` | 0.186.0 | — |
| `postprocessing` (pmndrs) | 6.39.5 | `>= 0.168.0 < 0.187.0` |
| `camera-controls` | 3.1.2 | `>= 0.126.1` (no ceiling) |
| `meshline` | 3.3.1 | `>= 0.137` |

`camera-controls` survives the r187 bump; `postprocessing` does not. That
asymmetry is the practical shape of the upgrade risk.

## 2. Renderer decision: WebGLRenderer

**WebGLRenderer at launch. WebGPU/TSL is tracked, not shipped.** Four reasons:

1. `postprocessing@6.39.5` is WebGL-only and pins `< 0.187.0`.
2. The manual still says of WebGPURenderer: "The renderer itself is still in an
   experimental state although its maturity level has been greatly improved in
   the last years."
3. `await renderer.init()` is an async structural break in the mount path.
4. The manual is explicit that "custom materials based on ShaderMaterial,
   RawShaderMaterial and modifications of built-in materials via
   `onBeforeCompile()` are not supported in WebGPURenderer" — every custom shader
   must be ported to NodeMaterial + TSL.

A fifth reason is specific to this site's line work: `meshline@3.3.1`'s
`MeshLineMaterial` is declared `extends THREE.ShaderMaterial`, and the WebGL
`LineMaterial` addon is in the same position, so choosing WebGPU today would rule
out both. r186 does ship a WebGPU-native fat-line path at
`three/addons/lines/webgpu/Line2.js` and `.../LineSegments2.js`, which is the
correct answer *if* that migration ever happens.

The escape hatch, recorded so it is not rediscovered:

```js
import * as THREE from 'three/webgpu';
import { pass } from 'three/tsl';
import { bloom } from 'three/addons/tsl/display/BloomNode.js';

const renderer = new THREE.WebGPURenderer({ antialias: true /*, forceWebGL: true */ });
await renderer.init();

const renderPipeline = new THREE.RenderPipeline(renderer);
const scenePass = pass(scene, camera);
const scenePassColor = scenePass.getTextureNode('output');
renderPipeline.outputNode = scenePassColor.add(bloom(scenePassColor));
```

`PostProcessing` was renamed **`RenderPipeline` in r183** (#32789) — the migration
guide lists it under "182 → 183". A separate, unrelated internal rename landed in
the same revision (`RenderPipeline` → `RenderObjectPipeline`, #32785); the two are
easy to conflate. There is no such entry in the 184 → 185 migration section.

## 3. r186 API facts that are wrong in most tutorials

| Thing | The fact | Source of the error |
| --- | --- | --- |
| Timer | `import { Timer } from 'three'` — it lives in core at `src/core/Timer.js`, re-exported from the main bundle | `three/addons/misc/Timer.js` **404s** at r180, r182 and r186. It only worked up to r178 |
| `Clock` | Deprecated in favour of `Timer` since r183 | Repeated `Clock.getDelta()` calls in one tick return near-zero after the first; `Timer` separates `update()` from `getDelta()` |
| `PCFSoftShadowMap` | **Deprecated with a warning** in r186, not removed. `src/constants.js` still exports `PCFSoftShadowMap = 2` with the JSDoc "deprecated since r186. Use PCFShadowMap instead." The *implementation* was removed and `PCFShadowMap` is now the soft filter | Existing code still runs; it just warns |
| `MeshoptDecoder` | `import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js'` | `three/addons/loaders/MeshoptDecoder.js` **404s**. Only `DRACOLoader` and `KTX2Loader` live under `loaders/` |
| `SunLight` | **New** in r186 at `examples/jsm/lights/SunLight.js` (with `SunLightNode.js`, `SunLightShadow.js`, `SunShadowNode.js`), cascaded shadow maps, cascade count reduced to 2, works on both renderers | It did not "move" as a breaking change. `src/lights/` contains no `SunLight` |

`SunLight` is directly useful here: a 6 km circuit is precisely the large-extent
scene where one directional shadow map either has no resolution near the camera
or no coverage far away.

Also noted: r185 deprecated `Matrix3.scale()/.rotate()/.translate()` and removed
the `TiledLighting` addon; r183 renamed `shadowMap.color` → `shadowMap.colored`
→ `shadowMap.transmitted`.

Animation loop shape:

```js
import { Timer } from 'three';
const timer = new Timer();
function animate(timestamp) {
  timer.update(timestamp);           // once per frame
  const dt = timer.getDelta();       // stable for every subsystem reading it
  const t  = timer.getElapsed();
}
```

That stability matters because a replay has several subsystems reading delta in
the same frame — car positions, camera damping, trail decay, the UI clock.

## 4. The frame problem

`Curve.computeFrenetFrames(segments, closed = false)` is **misnamed**. It is not a
Frenet frame (there is no second derivative anywhere in it); it is a
rotation-minimising **parallel-transport** frame. From `src/extras/core/Curve.js`
at r186:

```js
for ( let i = 1; i <= segments; i ++ ) {
  normals[ i ] = normals[ i - 1 ].clone();
  binormals[ i ] = binormals[ i - 1 ].clone();
  vec.crossVectors( tangents[ i - 1 ], tangents[ i ] );
  if ( vec.length() > Number.EPSILON ) {
    vec.normalize();
    const theta = Math.acos( clamp( tangents[ i - 1 ].dot( tangents[ i ] ), - 1, 1 ) );
    normals[ i ].applyMatrix4( mat.makeRotationAxis( vec, theta ) );
  }
  binormals[ i ].crossVectors( tangents[ i ], normals[ i ] );
}
```

Three distinct defects for a road surface:

1. **The initial normal is arbitrary.** It picks the world axis aligned with the
   minimum-magnitude component of `tangents[0]`, so the starting roll is
   unpredictable and changes if the centreline's start point moves.
2. **Parallel transport conserves twist, not gravity.** Through elevation change
   the frame's "up" drifts away from world-up, so the track self-banks with no
   physical basis.
3. **The closed branch smears the loop's residual twist over every segment:**

```js
if ( closed === true ) {
  let theta = Math.acos( clamp( normals[ 0 ].dot( normals[ segments ] ), - 1, 1 ) );
  theta /= segments;
  if ( tangents[ 0 ].dot( vec.crossVectors( normals[ 0 ], normals[ segments ] ) ) > 0 ) theta = - theta;
  for ( let i = 1; i <= segments; i ++ ) {
    normals[ i ].applyMatrix4( mat.makeRotationAxis( tangents[ i ], theta * i ) );
    binormals[ i ].crossVectors( tangents[ i ], normals[ i ] );
  }
}
```

That is correct for a tube — it makes the seam continuous — and wrong for a road.
A closed Spa or Silverstone ribbon built from these normals rolls gradually left
then right around its own centreline, and "up" is never world-up anywhere. This
is the mechanism behind the familiar "ExtrudeGeometry twists along my path"
complaints.

**A real circuit is near-flat in roll except where it is deliberately banked.
Banking is therefore authored data, not a side effect of the frame.**

`ExtrudeGeometry` and `TubeGeometry` both delegate to it and are both the wrong
tool for the road surface. `ExtrudeGeometry` additionally hard-codes bevel
suppression when a path is supplied — from `src/geometries/ExtrudeGeometry.js` at
r186: `extrudeByPath = true; bevelEnabled = false; // bevels not supported for
path extrusion`, then `splineTube = extrudePath.computeFrenetFrames( steps,
isClosed )`. Its `steps` default is **1**, so an un-tuned extrusion along a 6 km
spline produces a single segment.

Where they *are* right: `TubeGeometry` for tyre-barrier tubes, catch-fence posts
and pit-lane guardrail; `ExtrudeGeometry` without `extrudePath` (plain `depth`)
for grandstand footprints and building masses.

## 5. The track ribbon

Build the road as a hand-authored indexed `BufferGeometry` on a **fixed world-up
frame** plus an explicit banking rotation about the tangent. Because a racing
circuit is never vertical, `tangent × worldUp` is always well-conditioned and no
degenerate-case handling is needed in practice.

```js
function buildTrackRibbon(curve, { segments = 4000, halfWidth = 6, bankAt = () => 0, metresPerRepeat = 8 }) {
  const positions = [], normals = [], uvs = [], indices = [];
  const worldUp = new THREE.Vector3(0, 1, 0);
  const P = new THREE.Vector3(), T = new THREE.Vector3();
  const L = new THREE.Vector3(), N = new THREE.Vector3();
  const q = new THREE.Quaternion();
  const total = curve.getLength();

  for (let i = 0; i <= segments; i++) {
    const u = i / segments;
    curve.getPointAt(u, P);                    // arc-length parameterised
    curve.getTangentAt(u, T).normalize();
    L.crossVectors(T, worldUp).normalize();    // lateral: track right
    N.crossVectors(L, T).normalize();          // surface normal

    const bank = bankAt(u);                    // radians, signed superelevation
    if (bank !== 0) { q.setFromAxisAngle(T, bank); L.applyQuaternion(q); N.applyQuaternion(q); }

    const v = (u * total) / metresPerRepeat;   // arc-length proportional V -> no stretch
    for (const s of [-1, 1]) {                 // left vertex then right vertex
      positions.push(P.x + L.x * halfWidth * s, P.y + L.y * halfWidth * s, P.z + L.z * halfWidth * s);
      normals.push(N.x, N.y, N.z);
      uvs.push((s + 1) * 0.5, v);              // U = 0 left kerb .. 1 right kerb
    }
  }

  for (let i = 0; i < segments; i++) {
    const a = i * 2, b = a + 1, c = a + 2, d = a + 3;  // a=left_i b=right_i c=left_i+1 d=right_i+1
    indices.push(a, b, c,  b, d, c);                    // CCW viewed from +N
  }

  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  g.setAttribute('normal',   new THREE.Float32BufferAttribute(normals, 3));
  g.setAttribute('uv',       new THREE.Float32BufferAttribute(uvs, 2));
  g.setIndex(indices);
  g.computeBoundingSphere();
  return g;
}
```

**Winding proof.** With `T = (0,0,-1)` and `worldUp = (0,1,0)`:
`L = T × up = (1,0,0)` (track right) and `N = L × T = (0,1,0)`. For the triangle
`(a,b,c)`, `(b−a) × (c−a) = (2·hw,0,0) × (0,0,−d) = (0, +2·hw·d, 0) = +Y` — front
face up. Keep `material.side = THREE.DoubleSide` while developing to confirm.

**Never call `computeVertexNormals()` afterwards.** It discards the analytic
banked normal and reintroduces faceting on a long thin strip.

Per-vertex attributes worth baking while generating (all `Float32BufferAttribute`,
`itemSize` 1). One shader then drives every analytic overlay without rebuilding
geometry:

| Attribute | Meaning | Unlocks |
| --- | --- | --- |
| `aArcLength` | metres from start/finish | kerb stripes, DRS zones, distance labels, sector boundaries |
| `aSector` | 1 / 2 / 3 | sector colouring |
| `aCurvature` | signed 1/radius | corner-severity shading |
| `aGradient` | dy/ds | gradient overlay |

Kerbs, pit lane, run-off and the static ideal racing line are **sibling ribbons
from the same helper** with an offset centre and a narrower width. The red/white
kerb alternation is procedural rather than textured — `step(0.5, fract(aArcLength
/ kerbPitch))` with `kerbPitch ≈ 1.0 m` — which stays crisp at any zoom and
avoids a photographic texture that would read as off.

## 6. Curve setup and arc length

`CatmullRomCurve3(points, closed = false, curveType = 'centripetal', tension = 0.5)`.
Allowed `curveType` values are exactly `'centripetal'`, `'chordal'`,
`'catmullrom'`; `tension` applies only to `'catmullrom'`. Use `'centripetal'` —
it is provably cusp- and self-intersection-free on the irregularly-spaced samples
that GPS traces and telemetry produce (dense in slow corners, sparse on
straights). Use `closed: true` so the curve wraps start/finish with C1 continuity.

**The arc-length trap.** The constructor sets `this.arcLengthDivisions = 200`.
`getLengths(divisions = this.arcLengthDivisions)` builds a cached cumulative-distance
table from `divisions + 1` uniform-`t` samples and reuses it unless
`this.needsUpdate`. On a 5.8 km circuit, 200 divisions means **29 m chords** — every
corner is cut, the total length is under-reported, and equal-`u` spacing is
visibly non-uniform through slow corners.

```js
const curve = new THREE.CatmullRomCurve3(points, true, 'centripetal', 0.5);
curve.arcLengthDivisions = 20000;   // ~0.3 m resolution on a 6 km lap
curve.updateArcLengths();           // the ONLY supported cache invalidation
const lapLength = curve.getLength();
```

A worse trap sits next to it: `getPoints(divisions = 5)` and
`getSpacedPoints(divisions = 5)` default to **five** divisions — a bare
`getSpacedPoints()` on a circuit returns a pentagon.

`getUtoTmapping(u, distance = null)` binary-searches `arcLengths` for
`targetArcLength = distance ?? u * arcLengths[il − 1]`, then interpolates within
the bracketing segment:
`segmentFraction = (target − lengthBefore) / (lengthAfter − lengthBefore)`,
returning `t = (i + segmentFraction) / (il − 1)`. The `distance` argument takes
**metres directly**, which is the useful form for racing.

Rule: `getPointAt` / `getTangentAt` / `getSpacedPoints` for anything metric;
`getPoint` / `getPoints` never.

## 7. Animating cars

Uniform `t` is not uniform distance — a car driven by `getPoint(t)` accelerates
through corners and crawls on straights.

**Pattern A — direct**, exact, ~O(log n) per query:

```js
const lapLength = curve.getLength();
let s = 0;                                       // metres along lap
function update(dt, speedMs) {
  s = (s + speedMs * dt) % lapLength;
  const u = s / lapLength;
  curve.getPointAt(u, carPos);
  curve.getTangentAt(u, carDir).normalize();
  carQuat.setFromUnitVectors(FORWARD, carDir);   // FORWARD = model's local forward axis
}
```

**Pattern B — precomputed LUT**, the right choice for a 20-car replay at 60 fps:

```js
const N = 4096;
const lut = curve.getSpacedPoints(N);            // N+1 equidistant Vector3
const tangents = lut.map((_, i) => curve.getTangentAt(i / N, new THREE.Vector3()));
// per car per frame: i = (s / lapLength) * N; lerp between lut[floor(i)] and lut[floor(i)+1]
```

One lerp per car per frame beats a binary search plus spline evaluation twenty
times a frame. Build the LUT once per circuit at load.

For a real replay the drive variable is not speed-integrated at all: it is the
per-sample distance-along-lap from the pipeline's uniform time grid. Interpolate
**in the distance domain**, never by lerping raw X/Y, or cars visibly cut corners —
effective position sampling is around **260 ms**, so a car at 300 km/h covers
roughly 20 m between native samples.

Lateral placement (racing line vs centreline) uses the same post-bank
`L = T × worldUp` vector that built the ribbon, so cars sit correctly on banked
sections.

FastF1's `Session.get_circuit_info()` returns a `CircuitInfo.corners` DataFrame
with `X`, `Y`, `Number`, `Letter`, `Angle`, `Distance` — `Distance` is metres
along the lap and plugs straight into both patterns for corner labelling and
sector boundaries.

**Units.** FastF1 position `X`/`Y`/`Z` are in **1/10 metre from 2020 onward** —
the unit has a date cutoff that is easy to miss, and pre-2020 sessions are not in
1/10 m.

## 8. Instancing and scene composition

Twenty cars do **not** need instancing — twenty draw calls is negligible against a
~100-call mobile budget, and separate meshes are far easier to pick, outline and
animate individually. Instancing's payoff on a circuit page is the thousands of
kerb blocks, tyre-barrier stacks, marshal posts, fence panels, trees and
grandstand crowd.

`InstancedMesh(geometry, material, count)`. Properties: `count`, `instanceMatrix`
(`InstancedBufferAttribute`), `instanceColor` (default `null`), `morphTexture`
(default `null`), `boundingBox`, `boundingSphere`. Methods: `setMatrixAt` /
`getMatrixAt`, `setColorAt` / `getColorAt`, `setMorphAt` / `getMorphAt`,
`computeBoundingBox`, `computeBoundingSphere`, `raycast`, `copy`, `dispose`.

```js
const cars = new THREE.InstancedMesh(carGeo, carMat, 20);
cars.instanceMatrix.setUsage(THREE.DynamicDrawUsage);   // set once at construction
for (let i = 0; i < 20; i++) cars.setColorAt(i, new THREE.Color(teamInk[driver[i].team]));
cars.instanceColor.needsUpdate = true;
cars.frustumCulled = false;

// per frame
const m = new THREE.Matrix4(), q = new THREE.Quaternion(), s = new THREE.Vector3(1, 1, 1);
for (let i = 0; i < 20; i++) { q.setFromRotationMatrix(orient[i]); m.compose(pos[i], q, s); cars.setMatrixAt(i, m); }
cars.instanceMatrix.needsUpdate = true;
```

Three `needsUpdate` rules, stated as rules because they are the usual bug:
`instanceMatrix.needsUpdate` after a `setMatrixAt` batch; `instanceColor.needsUpdate`
after `setColorAt`; `morphTexture.needsUpdate` after `setMorphAt`.
`computeBoundingBox()` is **not** automatic and must be recomputed after matrices
change, or frustum culling misbehaves — for a scene-spanning instanced set,
`frustumCulled = false` is the pragmatic answer.

Per-instance data beyond matrix and colour, and what each route costs:

| Route | Cost |
| --- | --- |
| Own `InstancedBufferAttribute` + `onBeforeCompile` string patch | A `mat4` attribute consumes 4 of ~16 vertex attribute slots; standard materials will not read a custom attribute unpatched |
| Troika `InstancedUniformsMesh` | Auto-converts `float`/`vec2`/`vec3`/`vec4` uniforms into instanced attributes |
| WebGPU/TSL: read `instanceIndex`, index a storage buffer | Cleanest — but `onBeforeCompile` does not exist there |

`BatchedMesh` (multi-draw) covers many *different* geometries sharing one
material — the right tool for varied barrier and building meshes. r184 added
per-instance opacity; r186 fixed draw-offset bugs.

## 9. Lines

WebGL's `gl.LINES` ignores `linewidth` on virtually every platform, so
`THREE.Line` + `LineBasicMaterial.linewidth` is a no-op. Three options:

**Line2** — `three/addons/lines/{Line2,LineGeometry,LineMaterial}.js`
(`LineSegments2` is the disjoint-segment base; `Line2` the continuous polyline).
`LineMaterial` defaults: `linewidth` 1 (CSS px when `worldUnits === false`, world
units when true), `worldUnits` false, `resolution` (Vector2, **must be updated on
every resize** or widths are wrong), `dashed` false, `dashScale` 1, `dashSize` 1,
`gapSize` 0, `alphaToCoverage`, `color` (1,1,1), `opacity` 1.

```js
const geo = new LineGeometry();
geo.setPositions(flatXYZArray);       // [x1,y1,z1, x2,y2,z2, …]
const mat = new LineMaterial({ color: 0x111111, linewidth: 2, alphaToCoverage: true });
mat.resolution.set(canvas.clientWidth, canvas.clientHeight);
const line = new Line2(geo, mat);
line.computeLineDistances();          // REQUIRED if dashed
// on resize: mat.resolution.set(w, h);
```

A 1–2 px hairline outline at `worldUnits: false` stays 1–2 px at any zoom and
reads as *drawn* rather than rendered — the correct register for the editorial
page. `worldUnits: true` is for the painted white track-edge line, which should
thin with distance.

**meshline 3.3.1** for trails: `MeshLineGeometry.setPoints(points, (p) => 1 - p)`
gives a variable-width callback — a comet taper for free, the feature `Line2`
lacks. `MeshLineMaterial` props: `lineWidth`, `color`, `opacity`,
`sizeAttenuation`, `map`/`useMap`, `alphaMap`/`useAlphaMap`, `repeat`,
`dashArray`, `dashOffset`, `dashRatio`, `resolution` (required), `alphaTest`; set
`mesh.raycast = raycast` for picking.

**Offset ribbon** for the *static* ideal racing line — reuse `buildTrackRibbon`
with a per-`u` lateral offset and a narrow width. It sits flush on the road,
respects banking, needs no billboarding, and costs one draw call.

## 10. Post-processing and camera

Default to three's own addon composer for editorial views: `EffectComposer`,
`RenderPass`, `OutputPass` from `three/addons/postprocessing/*`, plus `SMAAPass`
where needed. **`OutputPass` must be last** — it applies tone mapping and the sRGB
output conversion that `renderer.render()` would otherwise do; omit it and the
scene renders washed out. `GTAOPass(scene, camera, width, height)` supersedes
`SSAOPass`; gate it off on mobile. `TAARenderPass` accumulates jittered samples
over `sampleLevel` frames — excellent for the **static** circuit hero shot,
ghosting and unusable for a moving replay camera. TAA for stills, SMAA for motion.

pmndrs `postprocessing@6.39.5` is reached for only when a merged multi-effect
chain is genuinely needed: its `EffectPass` merges N effects into **one** fullscreen
shader (rather than N ping-pong passes) and uses a single oversized triangle.
Recommended renderer config alongside it:
`{ powerPreference: 'high-performance', antialias: false, stencil: false, depth: false }`,
with AA from `SMAAEffect` inside the composer, and
`new EffectComposer(renderer, { frameBufferType: HalfFloatType })` for an HDR
workflow with a `ToneMappingEffect` last.

Permitted effects: SMAA (or MSAA), a very restrained bloom at high
`luminanceThreshold`, low-intensity vignette, tone mapping. Prohibited as AI
tells: heavy depth of field, chromatic aberration, glitch, god rays, scanlines,
lens flares, ambient auto-rotation.

**Camera damping must be frame-rate independent.** A fixed `lerp(0.1)` converges
twice as fast at 120 fps as at 60:

```js
const alpha = 1 - Math.exp(-lambda * dt);
camera.position.lerp(desiredPos, alpha);
camera.quaternion.slerp(desiredQuat, alpha);
```

Chase-cam construction: derive both the eye point (curve at `s − 12 m`, lifted
along the banked normal) and the look target (curve at `s + 25 m`) **from the
curve**, not from the car's noisy instantaneous orientation. Use a softer lambda
for position (~2–3) than for the look target (~6–8); that asymmetry is what makes
the shot read as filmed rather than glued. Never lerp Euler angles.

Interactive views: `camera-controls@3.1.2` for smooth `setLookAt` / `dollyTo` /
`fitToBox` transitions with an `enableTransition` flag — the mechanism for "click
a corner, the camera glides there". Or `OrbitControls` with `enableDamping = true`,
`dampingFactor = 0.05` and a mandatory `controls.update()` each frame. Clamp
`maxPolarAngle` well above the horizon, `enablePan = false`, `autoRotate` off.
Keyboard operation and the `listenToKeyEvents` deviation are covered in the
accessibility material; the rendering-side requirement is only that every camera
move is user-initiated.

## 11. Textures and materials

Anisotropic filtering is the single biggest visual win on a road surface, because
the track is viewed at extreme grazing angles; without it the asphalt goes to
mush about 50 m ahead of the camera.

```js
asphalt.wrapS = THREE.ClampToEdgeWrapping;                       // U spans the strip exactly once
asphalt.wrapT = THREE.RepeatWrapping;                            // V tiles along the lap
asphalt.anisotropy = renderer.capabilities.getMaxAnisotropy();   // usually 16
asphalt.colorSpace = THREE.SRGBColorSpace;                       // COLOUR MAPS ONLY
// normal / roughness / AO maps stay linear (THREE.NoColorSpace)
```

**KTX2/Basis is the only texture format that reduces GPU memory.** JPEG, PNG,
WebP and AVIF shrink the download only — they decode to full RGBA8 in VRAM. Basis
Universal has two modes: **ETC1S**, described by its README as "a roughly
.3-3bpp low to medium quality supercompressed mode", which transcodes to 4 bpp
GPU formats (BC1 / ETC1 / ETC2-RGB); and **UASTC LDR 4×4**, "a custom ASTC 4x4-like
format designed for very fast transcoding to other LDR texture formats with high
quality", at 8 bpp on the GPU. ETC1S for bulk; UASTC for normal maps and hero art.

```js
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

const base = import.meta.env.BASE_URL;
const ktx2 = new KTX2Loader().setTranscoderPath(base + 'basis/').detectSupport(renderer);
const draco = new DRACOLoader().setDecoderPath(base + 'draco/');
const gltf = new GLTFLoader()
  .setKTX2Loader(ktx2)
  .setMeshoptDecoder(MeshoptDecoder)
  .setDRACOLoader(draco);
```

`detectSupport(renderer)` **must** precede any load — without it the loader cannot
choose a transcode target and throws. It is the most common KTX2 bug.

Geometry compression: **meshopt is the default**, and it is `gltf-transform
optimize`'s own default `--compress` method. Its decoder "can directly target
write-combined memory; you can expect it to run at 3-6 GB/s on modern desktop
CPUs", and it preserves GPU-friendly vertex order. meshoptimizer's stated critique
of the alternative is the reason to prefer it for long thin strips like racing
lines and kerbs: competing libraries "typically are designed to maximize the
compression ratio at the cost of disturbing the vertex/index order (which makes
the meshes inefficient to render on GPU) or decompression performance." Reserve
Draco for geometry-dominant models where ratio beats decode cost.

For 78 circuits, prefer **generating track geometry procedurally from a compact
coordinate array in the page's JSON** over shipping a GLB per circuit. A circuit
spine simplified with RDP at ε = 0.25 m is 322 points / 1,288 B as int16 XY — see
[Telemetry encoding](telemetry-encoding.md). Every decoder file is an extra
600-second-TTL request that also counts against the 1 GB site cap.

## 12. Resource discipline

- `renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))`.
- Dispose geometries, materials and textures — and call `renderer.dispose()` — on
  island unmount and on `astro:before-swap`, or GPU memory creeps up across
  view-transition navigations.
- `canvas.addEventListener('webglcontextlost', e => e.preventDefault())` and
  rebuild all GPU resources on `webglcontextrestored`. Hold every GPU resource
  behind a class that can rebuild from JS-side state, so recovery is "rebuild
  scene from source of truth".
- Instrument in dev with `renderer.info.render.calls` / `.triangles` and
  `renderer.info.memory.geometries` / `.textures`, on a rolling-average frame
  timer driven by `Timer`.

A 4,000-segment ribbon is ~8,002 vertices and ~16,000 triangles in **one draw
call** — trivially inside budget, so smooth Eau Rouge is affordable. The scene
risk is grandstands, trees and post-processing, not the track. Full numbers in
[Performance budgets](performance-budgets.md).

## 13. Prior art, accurately

The one serious FastF1 → GIS → parametric-curve track pipeline found,
[lohithburra01/F1-3D-VISUALIZATION](https://github.com/lohithburra01/F1-3D-VISUALIZATION),
is **not** three.js prior art: its README names Python (FastF1), QGIS, Blender and
Unreal Engine 5, and renders offline. ("Array modifiers" is a Blender concept.)
It validates the *data* half of the pipeline — 4 Hz X/Y telemetry, GeoJSON,
satellite imagery plus DEM for terrain — and says nothing about the browser. No
polished editorial 3D circuit renderer exists on the web; the existing three.js
F1 work is hobby-scale or game-shaped.

## Open items

- The `SunLight` addon's exact constructor signature and API surface (cascade
  count, shadow bounds, bias) is **unverified** and must be read from source
  before it is specified in code.
- Whether iOS Safari's WebGL2 can sustain ribbon + instanced furniture + SMAA at
  60 fps on a 3–4 year old iPhone is **unmeasured**; the budget numbers are
  documented best practice, not device testing.
- Per-circuit superelevation values are **not available from any API found**.
  Indianapolis, Zandvoort (Turn 3 and Turn 14 at ~18°) and COTA are publicly
  documented; most circuits are not. `bankAt(u)` will need hand-authored
  keyframes per hero circuit, or derivation from lateral-acceleration telemetry.
- Whether DEM elevation at 30 m posting is adequate for the Y axis of a 6 km
  ribbon, or whether hand-authored elevation profiles are needed, is **open**.
- The gzipped size of a minimal r186 scene (WebGLRenderer + OrbitControls +
  BufferGeometry lines) built through Vite 8/Rolldown with Oxc minify is
  **estimated, not measured**.
