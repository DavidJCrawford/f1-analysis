<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img alt="F1 Analysis — every race, circuit and team in Formula 1, one permanent page each" src="assets/banner-light.svg" width="100%">
</picture>

<br>

![Status](https://img.shields.io/badge/status-phase_0_%C2%B7_spec_complete-1f1f1f?style=flat-square)
![Docs](https://img.shields.io/badge/docs-79_documents-1f1f1f?style=flat-square)
![Astro](https://img.shields.io/badge/Astro-7-1f1f1f?style=flat-square&logo=astro&logoColor=white)
![three.js](https://img.shields.io/badge/three.js-r186-1f1f1f?style=flat-square&logo=threedotjs&logoColor=white)

</div>

<br>

A static, editorial encyclopaedia of Formula 1. Every circuit, team and race gets one
designed page, one permanent URL, and — where the data exists — a real 3D track you
can fly a lap of.

The opposite of a live-timing dashboard, deliberately.

<br>

## Tiers

Telemetry begins in 2018. That leaves ~85% of races with no lap data at all, so
coverage is a designed system rather than an apology: each tier gets its own template
and its own charts.

| Tier | Years | Adds | Pages |
|:--|:--|:--|--:|
| **Archival** | 1950–1995 | Results, grid, championship, lineage | ~570 |
| **Timing** | 1996–2017 | Lap charts, race trace, stints, pit analysis | ~420 |
| **Telemetry** | 2018–2022 | Speed traces, mini-sectors, 3D replay | ~100 |
| **Modern** | 2023–2026 | Cross-source enrichment | ~80 |

3D is tiered too — hand-authored for 8–12 hero circuits, procedural for ~40, 2D
outline for the rest. Polishing 160 layouts is not affordable and pretending
otherwise is how projects die.

<br>

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

## Ingest

There is a human in this loop, permanently. F1's archive blocks datacenter IPs, so
CI cannot fetch — it returns `200`s with empty bodies. Ingest runs locally, on a
residential connection, and its output is committed as data.

```bash
make discover YEAR=2026              # what changed upstream?
make fetch     YEAR=2026 ROUND=17    # residential IP required
make transform YEAR=2026 ROUND=17    # offline
make emit      YEAR=2026 ROUND=17    # offline
make verify                          # the gates CI will run
```

Run twice per race: once for a prompt **provisional** publish with derived metrics
suppressed, once after the amendment window closes. Stewards change results for days.

<br>

## Status

Phase 0. Spec and knowledge base complete; no application code yet. Phase 1 is the
archival site alone — it has to be good at 1962 before it is allowed to be
spectacular at 2026.

<br>

---

<div align="center">
<sub>

Unofficial and unaffiliated. Not associated with Formula 1, the FIA, or any team.<br>
F1, FORMULA ONE and related marks are trademarks of Formula One Licensing BV.

</sub>
</div>
