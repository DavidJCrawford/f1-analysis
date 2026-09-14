---
type: Reference
title: 3D prior art
description: Every 3D F1 project the survey located, what each actually renders with, and why the one serious FastF1-to-3D pipeline is a Blender and Unreal offline render rather than a browser renderer.
tags:
  - prior-art
  - threejs
  - 3d
  - webgl
  - elevation
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1tml
    resource: https://github.com/yashyegare/F1TrackMetricsLab
    title: yashyegare/F1TrackMetricsLab
  - id: f1_3d_viz
    resource: https://github.com/lohithburra01/F1-3D-VISUALIZATION
    title: lohithburra01/F1-3D-VISUALIZATION
  - id: blender_tutorial
    resource: https://dev.to/mlbonniec/3d-race-track-modeling-with-elevation-in-blender-14da
    title: 3D race track modeling with elevation in Blender
  - id: openf1_location
    resource: https://api.openf1.org/v1/location
    title: OpenF1 — /v1/location endpoint
  - id: openf1_home
    resource: https://openf1.org/
    title: OpenF1 — API documentation
  - id: racereplay
    resource: https://github.com/Zimal-Fatemah/F1-RACEREPLAY
    title: Zimal-Fatemah/F1-RACEREPLAY
  - id: webtrack
    resource: https://github.com/markclausing/webtrack
    title: markclausing/webtrack
  - id: printables_tracks
    resource: https://www.printables.com/model/229471-f1-tracks-with-elevation-and-without
    title: Printables — F1 tracks with elevation
  - id: gh_topic_f1telemetry
    resource: https://github.com/topics/f1-telemetry
    title: GitHub topic — f1-telemetry
status: stable
---

# 3D prior art

3D is the thinnest area of the whole field, and the single most important fact
about it is a correction to the obvious assumption.

> **The one serious FastF1 → GIS → 3D pipeline located is not a browser
> renderer.** `lohithburra01/F1-3D-VISUALIZATION` is **Blender + Unreal**,
> rendered offline. It validates the *data* half of the pipeline — telemetry to
> geometry — and says nothing whatsoever about the browser half.

Every three.js F1 project found is hobby-scale or game-shaped. That makes a
polished editorial browser renderer the unoccupied position, and it also means
there is no precedent to copy for the hard parts: the frame construction, the
banking, the LOD budget, the accessibility story.

## 1. The inventory

| Project | Renders with | Runs | Scale |
| --- | --- | --- | --- |
| [lohithburra01/F1-3D-VISUALIZATION](https://github.com/lohithburra01/F1-3D-VISUALIZATION) | **Blender + Unreal**, offline | Not a website | The serious data pipeline; no browser story |
| [yashyegare/F1TrackMetricsLab](https://github.com/yashyegare/F1TrackMetricsLab) | React Three Fiber + Drei (three.js) | Vite SPA on Vercel / Google Cloud Run | MIT, **0 stars / 0 forks / 0 watchers**, 103 commits, 40 circuits |
| Zimal-Fatemah/F1-RACEREPLAY (and the Astrageguyonthemoon fork) | React + three.js | SPA | 2025 replay viewer on 3D track maps, variable playback |
| markclausing/webtrack | **Software-rendered 320×224 polygons — no WebGL** | Browser | Eight OSM-measured circuits; a game, not a reference |
| craigderington/f1-sculptures | three.js + vanilla ES6 (reported) | Web + FastAPI/Celery/Redis backend | **Unverified** — see §5 |
| Printables "F1 tracks with elevation" | Not a renderer — STL models | 3D print | Useful editorial precedent, see §4 |

Nothing in that list is a polished, editorial, browser-native 3D circuit
renderer. That is the gap.

## 2. F1TrackMetricsLab — the closest architectural precedent

It is a 0-star repository, and treating it as negligible on that basis would be
a mistake: it has 103 commits, 40 circuits, and it draws **real qualifying
telemetry from the OpenF1 API for 2023+ circuits**. It is the working proof that
the telemetry → 3D geometry route runs end to end in a browser.

**Stack, as stated by the repository:** React 18 + Vite, Zustand, React Three
Fiber + Drei (3D), Leaflet (2D map), Recharts (telemetry charts), idb-keyval
(IndexedDB caching), Playwright (e2e).

**3D method:** a road-ribbon mesh built from the centreline with corner markers,
elevation banking and orbit controls, using **Catmull-Rom smoothing** for cubic
interpolation between telemetry points.

**Feature surface:** three comparison modes (side-by-side 3D, overlay 3D, flat
2D); a speed-coloured ribbon on a blue→red heatmap with a variable-speed car
animation; a four-lane telemetry scrubber (speed / time delta / throttle-brake /
gear-DRS); a ⌘K command palette with deep links; filters by continent, decade,
track length and corner count; lap records and DRS zones; screenshot export;
shareable URLs; a `circuits.json` covering 40 circuits. Geometry from
`bacinger/f1-circuits` (MIT); telemetry from OpenF1, 2023+ only.

**What it establishes, and what it leaves open.** The ribbon-from-centreline
recipe works. The packaging is a dark dashboard on dynamic hosting, which is why
the static-and-permanent axis in
[the scorecard](landscape.md#3-the-four-axis-scorecard) remains genuinely
unoccupied — but the *3D-plus-per-circuit* combination is more thoroughly
executed than the star count suggests, and it should be treated as the
functional bar, not as a curiosity.

## 3. The elevation recipe, and where its evidence stops

The published route to elevation is OpenF1's `/v1/location` endpoint, whose `z`
field is real and integer-valued. A live call returns exactly:

```json
{"date":"2023-09-16T13:03:35.292000+00:00","session_key":9161,
 "z":187,"x":567,"meeting_key":1219,"driver_number":81,"y":3195}
```

The Blender tutorial that popularised the route states, verbatim:

> The coordinates are relative to the track's origin point, not global GPS
> coordinates like latitude/longitude or even distance in meters

and scales all three axes by a single constant:

```python
TRACK_SCALE: int = 150
points = [(v["x"] / TRACK_SCALE, v["y"] / TRACK_SCALE, v["z"] / TRACK_SCALE)
          for v in locations]
```

justified only because "F1 tracks are typically 3-6 km long, which would be huge
in Blender's default scale". **The unit of the raw `z` value is not established
by any source found.** Treat 150 as one author's convenience factor, not as a
conversion.

Its accuracy warning is the operative one: irregularities in the mesh come from
"abrupt changes in direction or elevation in the source data" — so a smoothing
pass is mandatory before meshing, not optional.

Two sampling facts bound what an un-interpolated ribbon can look like. OpenF1
documents **18 endpoints and a 3.7 Hz car-telemetry sampling rate**. FastF1
position data is natively around 240 ms (measured median 241.0 ms on the 2024
British GP), which is the higher-resolution source and also the one that reaches
back to 2018 where OpenF1 starts at 2023.

### Where this project diverges from the prior art

| Prior art does | We do | Why |
| --- | --- | --- |
| Catmull-Rom through raw telemetry, naive frame | **Fixed world-up frame**, not `computeFrenetFrames` | three.js's `computeFrenetFrames` is already a parallel-transport frame; its initial normal is arbitrary, it conserves twist rather than gravity so a track self-banks through elevation change, and closed curves get residual twist smeared around the loop |
| Banking as a side effect of the frame | **Banking is authored data**, per corner | A real circuit is near-flat in roll except where deliberately banked |
| A single `TRACK_SCALE` divisor | Documented unit handling: FastF1 position `X`/`Y`/`Z` are **1/10 metre from 2020 onward** | The unit has a date cutoff that is easy to miss |
| GPS-derived `z` as the surface | Telemetry Z for the track surface only where telemetry exists (2018+); Copernicus GLO-30 for **distant terrain only** | GLO-30 is a surface model at <4 m LE90, and at least one venue (Baku) returns 404 |

The full technical baseline is in
[three.js track rendering](../engineering/threejs-track-rendering.md); the
elevation and banking treatment is in
[Banking and elevation](../references/circuits/banking-and-elevation.md); the
coordinate handling is in
[Coordinate systems](../references/circuits/coordinate-systems.md).

## 4. Two editorial ideas worth taking from outside the web

**Constant cross-circuit scale.** The Printables model set renders every circuit
mutually to scale. A Monaco drawn the same size as Spa is a lie of omission; at
true relative scale the comparison itself becomes an argument. The circuits index
is designed around this.

**A declared vertical exaggeration.** Real F1 elevation change is small relative
to track length and reads as flat unless exaggerated — the same model set offers
original, 3× and 5× variants. The legibility trick is worth stealing; hiding it
is not. **Both the scale and the exaggeration factor are stated in the interface**,
never applied silently.

A third, from `f1-sculptures` conceptually rather than as evidence: a lap as a
sculpture — track layout in XY, extruded along Z by a channel such as combined
G-force. It is a genuinely original idea. It is not a circuit renderer, and it is
not what the circuit page is for.

## 5. What is unverified, and stays unverified

Accuracy matters more than inventory completeness here, so three items are
recorded as *not established*:

1. **`craigderington/f1-sculptures`** — the repository could not be located during
   verification (the URL in the source claim was truncated mid-owner). Its
   licence, stack and star count are unconfirmed. Cite the *idea*, not the repo.
2. **Nicolas Penco's Formula 1 Data Art Series** — the host returns HTTP 403 to
   automated fetches. The palette and typography details attributed to it rest on
   a search snippet and are not usable as a design citation.
3. **The negative claim itself.** "No credible, polished three.js F1 circuit
   project exists in the wild" is **not provable from the evidence gathered**.
   GitHub's `f1-telemetry` topic is effectively unused, so absence there is not
   evidence of absence, and the survey's search budget ran out before a broad
   sweep. What is established is the narrower statement at the top of this
   document: every 3D F1 project *actually located* is hobby-scale, game-shaped,
   or rendered offline.

## 6. What none of the prior art attempts

| Unattempted | Our position |
| --- | --- |
| 3D as a *focal moment* on an editorial page | One scene per circuit page, behind a static poster frame, mounted `client:visible`; `<canvas>` is never the LCP element |
| Tiered ambition across 78 circuits and ~160 layouts | Hero (8–12, hand-authored banking and real elevation), Standard (~40, procedural), Outline (remainder, 2D SVG only) |
| Keyboard operability and a text alternative for the scene | Required, per [SPEC §11.1](../../SPEC.md) |
| `prefers-reduced-motion` collapse to a meaningful static frame | Required; content motion must be user-initiated or scrubbable, never idle-looping |
| A stated provenance for the geometry of each circuit | Every 3D page names its centreline source, its elevation source and its exaggeration |

The prior art is a set of demos. The unsolved part is not the ribbon mesh — that
is proven — it is making a ribbon mesh behave like a page in an encyclopaedia.

## Related

- [three.js track rendering](../engineering/threejs-track-rendering.md)
- [Centreline construction](../references/circuits/centreline-construction.md)
- [Banking and elevation](../references/circuits/banking-and-elevation.md)
- [Coordinate systems](../references/circuits/coordinate-systems.md)
- [OpenF1](../datasets/openf1.md) · [FastF1](../datasets/fastf1.md)
- [Landscape](landscape.md)
