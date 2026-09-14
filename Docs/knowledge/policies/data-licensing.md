---
type: Policy
title: Data licensing and rights posture
description: Every source's licence, the incompatibility analysis that forces the role boundary, Formula 1's own asserted rights, and the two unresolved provenance gaps that gate launch.
resource: https://github.com/f1db/f1db
tags: [licensing, cc-by, cc-by-nc-sa, lgpl, trademark, compliance, gating]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_readme
    resource: https://raw.githubusercontent.com/f1db/f1db/main/README.md
    title: F1DB README and licence statement
  - id: jolpica_terms
    resource: https://github.com/jolpica/jolpica-f1/blob/main/TERMS.md
    title: jolpica-f1 Terms of Use
  - id: jolpica_dumps
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/database_dumps.md
    title: jolpica-f1 database dumps and access tiers
  - id: openf1_license
    resource: https://raw.githubusercontent.com/br-g/openf1/main/LICENSE
    title: OpenF1 repository LICENSE file
  - id: fastf1_pypi
    resource: https://pypi.org/pypi/fastf1/json
    title: FastF1 package metadata (licence, version, Python floor)
  - id: f1_legal_notices
    resource: https://www.formula1.com/en/information/legal-notices.7egvZU48hzrypubGBNcQKt
    title: Formula 1 Legal Notices
  - id: f1_fan_guidelines
    resource: https://www.formula1.com/en/information/guidelines.4EOKE9RRqevL4niTK9kWyt
    title: Formula 1 fan-site guidelines
  - id: bacinger
    resource: https://github.com/bacinger/f1-circuits
    title: bacinger/f1-circuits (MIT circuit outlines)
  - id: tumftm
    resource: https://github.com/TUMFTM/racetrack-database
    title: TUMFTM/racetrack-database (LGPL-3.0 centrelines and widths)
  - id: multiviewer_circuits
    resource: https://api.multiviewer.app/api/v1/circuits/63/2025
    title: MultiViewer circuits endpoint (undocumented)
  - id: chart_doctor
    resource: https://github.com/Financial-Times/chart-doctor
    title: FT chart-doctor repository licence statement
status: stable
---

# Data licensing and rights posture

This is a gating policy, not boilerplate. The licence chain is the sharpest
constraint on the project and the largest non-technical risk. Nothing here is
legal advice; it is a risk posture assembled from published terms, and several
of those terms are broadly drafted.

## 1. The decision this policy forces

**The site is and remains strictly non-commercial.** No advertising, no
sponsorship, no affiliate links, no paid tier, no commercial licensing of the
emitted data. Two of the five data sources carry a NonCommercial clause; if
that answer ever changes, this document and the entire ingest pipeline must be
re-derived from scratch.

The second decision, which follows from it: **the published artifacts of this
site must be free of NonCommercial and ShareAlike material.** Shipping a site
that is *itself* non-commercial does not discharge the ShareAlike obligation —
SA propagates to everyone who reuses the emitted JSON. The mechanism that
prevents this is [source roles](source-roles.md), and it is enforced in code.

## 2. Licence matrix

| Source | Version / state | Licence | Commercial | ShareAlike | Role |
| --- | --- | --- | --- | --- | --- |
| F1DB | v2026.14.0 (13 Sep 2026) | CC BY 4.0 | permitted | no | Canonical spine — **redistributable** |
| F1DB circuit SVGs | git repo only | CC BY 4.0 | permitted | no | 2D layouts — **redistributable** |
| bacinger/f1-circuits | 39 circuits | MIT | permitted | no | Circuit outlines — **redistributable** |
| FastF1 | 3.8.3 (29 Apr 2026) | MIT (code only) | permitted | no | Tool. The *data* it fetches is F1's — **build-time only** |
| jolpica-f1 | live API + CSV dumps | CC BY-**NC-SA** 4.0 | forbidden | yes | **Build-time gap-fill. Never redistributed.** |
| OpenF1 | 2023+ | CC BY-**NC-SA** 4.0 | forbidden | yes | **Build-time cross-check. Never redistributed.** |
| TUMFTM/racetrack-database | 24 tracks (19 used) | **LGPL-3.0 over ODbL** | permitted | copyleft + share-alike | Centreline + width — **redistributed** as derived outlines. Its README states the centrelines came from OpenStreetMap, so ODbL sits underneath: attribute OSM contributors and offer the derived geometry onward under ODbL |
| MultiViewer API | undocumented | **no terms published** | unknown | unknown | **Blocked pending contact** |
| Copernicus GLO-30 DEM | — | free, attribution required | permitted | no | Distant terrain only |
| f1tenth/f1tenth_racetracks | 23 tracks | GPL-3.0 | permitted | copyleft | **Not used.** Also 1:10 scaled with a fixed 2.20 m width |
| FT Visual Vocabulary | — | MIT **software only** | — | — | Chart-selection *reading*, never republished |

Two rows carry corrections a reasonable person would get wrong:

- **bacinger/f1-circuits is not OpenStreetMap-derived.** Its README names
  Google My Maps tracing plus Wikipedia and official circuit sites. The ODbL
  share-alike concern therefore does not apply — but neither does the
  "OSM-derived" provenance story, and a Google Maps Terms of Service question
  takes its place. The repo holds 39 circuits in its README table (~40
  `.geojson` files under `/circuits`, named `<iso2>-<year>.geojson`), not 43.
- **The FT Visual Vocabulary poster is not Creative Commons.** The
  `Financial-Times/chart-doctor` repository is MIT, and its README states that
  the MIT licence "includes only the software, and does not cover any FT
  content made available using the software", which is copyright The Financial
  Times Limited, all rights reserved. The poster is FT content. It may be read
  as a chart-selection reference; it may not be republished, re-drawn as a
  facsimile, or embedded.

## 3. The verbatim terms

**F1DB** — "F1DB is licensed under a Creative Commons Attribution 4.0
International License."[^f1db] Attribution only; commercial use permitted; no
share-alike. This is the only comprehensive source under a permissive licence,
which is the entire argument for making it the spine.

**jolpica-f1** — "The API is freely available for **non-commercial use**. The
data is licensed under Creative Commons Attribution-NonCommercial-ShareAlike
4.0 International (CC BY-NC-SA 4.0) … For commercial usage, please contact us
via admin@jolpi.ca". The same file adds that the project is "volunteer-run,
donation-supported" and that "we **do not guarantee uptime, availability, or
correctness**", and reserves the right to change the terms.[^jolpica] The
supporter tier (API key) grants latest dumps *and* a commercial-use licence —
which is the escape hatch if the non-commercial decision in §1 is ever
revisited, and the only one.

**OpenF1** — the repository `LICENSE` file is verbatim the text of
"Attribution-NonCommercial-ShareAlike 4.0 International"; the site footer reads
"Licensed under CC BY-NC-SA 4.0".[^openf1]

**FastF1** — MIT, "Copyright (c) 2026 Philipp Schäfer".[^fastf1] This licences
the *code*. It does not licence the live-timing archive the code reads, which
belongs to Formula One World Championship Limited. Treating FastF1's MIT
licence as cover for redistributing telemetry is the single most common
licensing error in this space.

## 4. Incompatibility analysis

The question is not whether each licence permits our use individually. It is
whether the emitted bundle — the JSON committed to the repo and served from
GitHub Pages — can carry a single coherent licence statement.

| Combination in one published artifact | Resolves? | Consequence |
| --- | --- | --- |
| CC BY 4.0 + MIT | yes | Attribution notices for both; no further obligation |
| CC BY 4.0 + CC BY-NC-SA 4.0 | **no** | The adapted material must be offered under NC-SA. The whole emitted data directory becomes NC-SA, every downstream reuser inherits the NC term, and the permissive-spine claim in the colophon becomes false |
| MIT + CC BY-NC-SA 4.0 | **no** | Same direction: the MIT geometry is absorbed into an NC-SA adapted work |
| CC BY 4.0 + LGPL-3.0 | **unresolved** | LGPL is a software licence applied to CSV data. Whether the copyleft attaches to derived geometry is genuinely murky. Unresolved obligations are not shipped |
| Anything + undocumented terms | **no** | Absence of terms is not permission |

The resolution is not a clever combined licence. It is a boundary: **NC-SA and
copyleft sources are build-time inputs whose values are never written to a
published artifact.** They may cause a build to fail. They may never supply a
number to a page. That mechanism, and how CI proves it, is
[source-roles.md](source-roles.md).

Concrete consequence that bites immediately: jolpica's CSV dump is a single
14.4 MB bundle refreshed within a day of the last race, and it is by far the
most convenient way to fill in a current-season gap. Convenience is exactly
why the boundary has to be mechanical rather than remembered.

## 5. Formula 1's own position

Quoted from the Legal Notices:[^f1legal]

> "all materials on this Site, including, but not limited to live timing data,
> historical race data, photographs, other images…are protected by copyrights,
> database rights, trademarks"

> "All results, timing data and certain other content are copyright Formula One
> World Championship Limited. All rights reserved."

> "The material and content provided on the Site is for your personal,
> non-commercial use only…you agree not…to distribute copy extract or
> commercially exploit such material or content."

The fan-site guidelines are narrower and more useful, because they describe
what a fan site may actually do:[^f1guidelines]

> "Individual pieces of the data can be used incidentally within editorial
> material to genuinely inform but substantial pieces of the data may not be
> reproduced or used commercially through scraping or any other means."

**This is the sentence the whole project is shaped around.** An editorial site
that publishes derived analysis sits on the permitted side of that line; a bulk
data mirror does not. Hence §6.5 of the spec: derived aggregates and
visualisations ship, raw timing streams never do. The raw material is large
anyway — one 2024 race session's live-timing streams total ~21 MB across 12
files (`Position.z` 7,914,755 B, `CarData.z` 7,302,595 B, `TimingData`
5,589,783 B), roughly 1.5–2 GB per season — so the legal position and the
1 GB GitHub Pages cap point the same way.

Mitigations, all of them cheap:

1. Publish derived aggregates and visualisations only. No downloadable raw
   telemetry, no bulk dumps, no "export the session" feature.
2. Keep volumes modest. The 2 Hz default replay payload (~623 kB) is a
   licensing decision as much as a performance one.
3. Carry the non-affiliation disclaimer in the footer of every page (§7).
4. Be prepared to take material down. There is documented history of aggressive
   enforcement in this space, including DMCA notices used against trademark
   rather than copyright concerns.

## 6. The two provenance gaps — both gating

### 6.1 F1DB's licence chain is an assumption, not a fact

F1DB's CC BY 4.0 is **a claim by a compiler about data he did not create.** Its
README documents no upstream provenance at all — no sources, no third-party
attribution, and no trademark disclaimer despite the project using "Formula 1®"
in its own description.

If any material part of F1DB descends from Ergast (which was CC BY-**NC-SA**
3.0), the permissive relicensing is not effective downstream, and the clean
spine on which this entire architecture rests does not exist. Nothing observed
proves it does descend from Ergast; nothing observed proves it does not. That
is precisely the problem.

**Action: ask the F1DB maintainer directly, in writing, before F1DB becomes
load-bearing.** The question is narrow: what are the upstream sources for the
1950–2003 results tables, and was any of it derived from Ergast?

### 6.2 MultiViewer publishes no terms of use

The MultiViewer circuits endpoint is genuinely the best geometry available. A
single response for circuit key 63 (Sakhir) is 14,684 bytes and carries a
730-point centreline as parallel `x`/`y` integer arrays, `rotation`, 15
`corners`, 18 `marshalSectors`, 18 `marshalLights`, `miniSectorsIndexes`,
`pitLoss` (`normal` / `sc` / `vsc`, in seconds) and the `candidateLap` the
geometry was captured from.

It is also undocumented, unofficial, unstable, and carries **no published terms
of use, no rate limits and no API documentation.** Absence of terms is not
permission. Shipping it without asking is not acceptable.

**Action: contact the maintainers. Blocked until resolved.**

Two facts that reduce the cost of the block. First, `miniSectorsIndexes` is
absent on roughly half of circuits — including Silverstone, Monaco, Suzuka,
Singapore, Miami, Imola, Montreal, Spielberg, Catalunya and Interlagos — so it
was never going to be the general recipe for sector boundaries. Second, the
endpoint ignores the year in its path: requesting `/circuits/63/2025` returns a
payload stamped `"year": 2022` whose `candidateLap` is a 2022 FP1 lap. It does
not give year-specific geometry, so the fallback (bacinger + TUMFTM +
telemetry-derived centrelines) loses less than it appears to.

## 7. Trademark and naming

The fan-site guidelines set out four obligations that apply directly:

| # | Rule | Consequence here |
| --- | --- | --- |
| 1 | A disclaimer in the footer of the landing/home page | Rendered in the footer of **every** page, not just the home page |
| 2 | "You may not use, for any purpose or in any medium, any of our Logos unless you have an express written licence from the Formula 1 companies." | No F1 logotype, no official team logos, no livery artwork. Team identity is expressed through a self-authored colour token, typography and abstract marks |
| 3 | Incidental editorial use of data only (§5) | Editorial framing, derived charts, no bulk mirror |
| 4 | Word marks may appear as a path (`example.com/formula1`) but not as a sub-domain prefix (`formula1.example.com`) | A GitHub Pages project site at `user.github.io/<repo>` is the compliant shape. Do not put an F1 word mark in a sub-domain |

Licensing contact of record: `brandprotection@f1.com`.

**Disclaimer wording.** The string recorded in research is:

> This website is unofficial and is not associated in any way with the
> Formula 1 companies. F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD
> CHAMPIONSHIP, GRAND PRIX and related marks are trade marks of Formula One
> Licensing B.V.

**The exact current wording is unverified** — the candidate guidelines URLs did
not resolve on re-check — and it must be confirmed against a live F1 page
before launch. A comparable fan site (pitwall.app) renders the full string
including the trademark sentence, which is a useful precedent for the shape but
not a substitute for confirming the source. Until confirmed, treat the string
above as provisional and mark it as such in the source, per
[provenance-and-staleness.md](provenance-and-staleness.md).

Two further trademark-adjacent rules:

- **Never hotlink or rehost F1-hosted imagery.** FastF1's `HeadshotUrl`,
  OpenF1's `headshot_url` and `meetings.circuit_image` all point at F1's own
  CDN. Hotlinking them embeds F1-copyright images in our pages.
- **Never link ergast.com.** Ergast shut down after the 2024 season and the
  domain is now a squatted gambling-spam site — `ergast.com/api` returns 404
  and the homepage serves casino SEO content. Attribution names "the Ergast
  Motor Racing Developer API (2010–2024, discontinued)" in plain text, with no
  hyperlink, and links jolpica-f1 instead.

## 8. There is no free, legal F1 photo corpus

Getty, LAT and Motorsport Images are uniformly rights-managed. There is no
permissively-licensed archive of F1 photography of usable breadth.

This is stated here rather than in the design documents because it is a
licensing fact with a compositional consequence: **the design system is built
to work entirely without photography.** Typography, data, the 3D renders and
the F1DB circuit SVGs are the visual material. That is a constraint accepted at
the start, not a limitation to be worked around later — see
[design-tokens.md](../design/design-tokens.md).

## 9. Attribution

An attribution page lives at `/data/` and names every source, its licence, its
version or release, and its declared role. It is generated from the same
manifest the pipeline enforces, so it cannot drift from what the build actually
used.

Per-page attribution is narrower: a page names only the sources that actually
supplied a value on that page. A 1962 race page credits F1DB; it does not
credit FastF1, because no FastF1 value reaches it.

Obligations by licence:

- **CC BY 4.0** (F1DB, F1DB SVGs) — name the source, state the licence, link
  it, indicate whether changes were made. Derived aggregates are changes.
- **MIT** (bacinger, FastF1) — retain the copyright notice and licence text.
  `Copyright (c) 2019-2025 Tomislav Bacinger` for the circuit outlines.
- **LGPL-3.0** (TUMFTM) — ship the licence text and mark the derived files, if
  and only if the derived geometry is published at all. Currently build-time.
- **Copernicus GLO-30** — attribution required. Note that tile availability is
  not guaranteed: at least one F1 venue (Baku) returns 404, so the 404 path is
  always handled.

## 10. Gating checklist

Nothing in Phase 1 ships until these are closed.

| # | Item | State | Owner |
| --- | --- | --- | --- |
| 1 | F1DB upstream provenance confirmed with the maintainer | **open** | maintainer |
| 2 | MultiViewer terms obtained, or the source dropped | **open** | maintainer |
| 3 | Exact fan-site disclaimer wording confirmed against a live F1 page | **open** | maintainer |
| 4 | Repository and any custom domain checked against the sub-domain rule | open | maintainer |
| 5 | `/data/` attribution page generated from the source manifest | open | build |
| 6 | CI gate proving no NC-SA value reaches a published artifact | open | build |

Items 1–3 are the §13 gating items named in the spec. Item 6 is the mechanism
described in [source-roles.md](source-roles.md); without it, items 1 and 2
matter less than they should, because a single convenience call to jolpica
during a busy race weekend would undo the entire posture.

[^f1db]: F1DB README, `f1db/f1db` on GitHub. Release v2026.14.0 published
2026-09-13; `LICENSE` is "Attribution 4.0 International".
[^jolpica]: jolpica-f1 `TERMS.md`, last updated 27 August 2025.
[^openf1]: `br-g/openf1` repository `LICENSE` file and the openf1.org footer.
[^fastf1]: FastF1 3.8.3 package metadata on PyPI (uploaded 2026-04-29,
`requires_python` `>=3.10`).
[^f1legal]: Formula 1 Legal Notices.
[^f1guidelines]: Formula 1 fan-site guidelines. See §7 on the unverified
status of the disclaimer string.
