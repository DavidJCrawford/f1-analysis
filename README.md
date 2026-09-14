<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="F1 Analysis — every race, circuit and team in Formula 1, one permanent page each" src="assets/banner-light.svg" width="100%">
</picture>

<br>

![Status](https://img.shields.io/badge/status-2026_season-1f1f1f?style=flat-square)
![Data](https://img.shields.io/badge/data-F1_timing_feed-1f1f1f?style=flat-square)
![Astro](https://img.shields.io/badge/Astro-7-1f1f1f?style=flat-square&logo=astro&logoColor=white)
![three.js](https://img.shields.io/badge/three.js-r186-1f1f1f?style=flat-square&logo=threedotjs&logoColor=white)

</div>

<br>

The 2026 Formula 1 season, circuit by circuit. Every round and every track gets one
designed page and one permanent URL, built from Formula 1's own timing feed — and
every race that has run can be replayed, car by car.

The opposite of a live-timing dashboard, deliberately.

<br>

## What's in it

| | |
|:--|--:|
| Rounds | 23 |
| Circuits | 23 |
| Teams | 11 |
| Circuits with exact start/finish from the timing feed | 23 / 23 |
| Circuits with official corner positions | 22 / 23 |

**Race replay.** Every completed round plays back from raw position data — all 22
cars at 2 Hz, as coloured dots on the real circuit, with the camera following the
leader or any car you pick from the running order. Pause, rewind, scrub, and change
speed.

**Circuit pages** carry the track drawn from feed geometry, its official corners
highlighted along their full length, an unrolled curvature profile of the lap, and
where the circuit sits against the rest of the calendar for length and turn count.

The architecture still supports the full 1950–2026 archive — 1,172 races, 78
circuits, 1,520 pages. It is narrowed to one season by a single switch in
[`scope.ts`](site/src/lib/scope.ts); see [SPEC §4.3](Docs/SPEC.md).

## Data

Every source is confined to a declared role, and the boundary is enforced in the
pipeline — not by good intentions. Non-commercial sources never reach a published
artifact.

| Source | Licence | Role |
|:--|:--|:--|
| [F1DB](https://github.com/f1db/f1db) | CC BY 4.0 | **Redistributable spine** — entities, results, 1950–2026 |
| [FastF1](https://github.com/theOehrly/Fast-F1) | MIT | Build-time — telemetry, laps, position |
| [jolpica-f1](https://github.com/jolpica/jolpica-f1) | CC BY-NC-SA | Build-time gap-fill — **never** redistributed |
| [OpenF1](https://openf1.org) | CC BY-NC-SA | Build-time cross-check — **never** redistributed |
| [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits) | MIT | Circuit outlines — including this README's banner |

<br>

## Docs

The project is grounded in a spec and a knowledge base, both written before any code.

| | |
|:--|:--|
| [**SPEC.md**](Docs/SPEC.md) | Promise, scope, architecture, design system, risks, open decisions |
| [**RUNBOOK.md**](Docs/RUNBOOK.md) | Post-race ingest, triple-headers, failure playbooks |
| [**Knowledge base**](Docs/knowledge/index.md) | 65 concept documents in [OKF](https://github.com/GoogleCloudPlatform/open-knowledge-format) v0.2 — every source, metric and decision |

Findings were researched in parallel and then adversarially fact-checked. **83 of ~252
first-pass claims required correction** before anything was written down; the corrected
values are what ship. Published methods at `/methods/` mean every derived number on the
site links to the formula that produced it.

<br>

## Build

```bash
make data      # F1DB release -> canonical JSON -> geometry -> curvature profiles
make replays   # race position data from the timing feed (slow first run, cached)
make build     # Astro build + Pagefind index
make preview
```

Telemetry ingest, when it lands, keeps a human in the loop permanently: F1's archive
blocks datacenter IPs and returns `200`s with empty bodies, so CI can never fetch.
Ingest runs locally on a residential connection and its output is committed as data —
see [RUNBOOK.md](Docs/RUNBOOK.md).

<br>

## Status

**Phase 1 — archival tier.** 1,172 races, 77 seasons, 78 circuits and
187 constructors render from the F1DB spine; 1,520 pages build in under a second.
581 of those races predate lap-by-lap timing entirely, which is the point of the
tier system: the site has to be good at 1962 before it is allowed to be spectacular
at 2026.

Next: lap charts and race traces for the timing tier, then telemetry and the first
hero circuit in 3D.

<br>

---

<div align="center">
<sub>

Unofficial and unaffiliated. Not associated with Formula 1, the FIA, or any team.<br>
F1, FORMULA ONE and related marks are trademarks of Formula One Licensing BV.

</sub>
</div>
