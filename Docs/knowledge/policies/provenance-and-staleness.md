---
type: Policy
title: Provenance and staleness
description: Data-as-of stamps, the provisional classification state, the staleness classes, and the rule that every derived number links to the method that produced it.
tags: [provenance, staleness, freshness, ingest, methods, ci, honesty]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: f1db_release
    resource: https://api.github.com/repos/f1db/f1db/releases/latest
    title: F1DB latest release metadata (v2026.14.0, 2026-09-13)
  - id: jolpica_dumps
    resource: https://api.jolpi.ca/data/dumps/download/
    title: jolpica-f1 database dump index (delay_days, file hashes)
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core object model (IsAccurate, FastF1Generated, ClassifiedPosition)
  - id: fastf1_cache
    resource: https://docs.fastf1.dev/api_reference/cache_and_rate_limits.html
    title: FastF1 cache configuration and rate limits
  - id: livetiming_archive
    resource: https://livetiming.formula1.com/static/
    title: F1 live-timing static archive
  - id: gh_pages_limits
    resource: https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages
    title: GitHub Pages usage limits
status: stable
---

# Provenance and staleness

Principle 6 of the project specification — *every number is traceable* — is
what separates a reference from a blog. This document is that principle made
mechanical: what each page states about its own freshness, what it does during
the window when the results are still moving, and how a derived figure is bound
to the method that produced it.

The base rate this policy exists to manage: the research underlying this
knowledge base was adversarially fact-checked and **83 of roughly 252 claims
required correction**. Confidently-presented wrong numbers are the main
correctness risk in the project, and a wrong number that carries a visible
provenance chain is a bug report; a wrong number that does not is folklore.

## 1. The operational reality

Three facts make this site a weekly publication rather than a build:

1. **GitHub-hosted runners cannot ingest.** F1's live-timing archive blocks
   datacenter IPs. Ingest runs locally, on a human's machine, after each race
   weekend.
2. **The free jolpica dump is 14 days delayed.** The dump index reports
   `delay_days: 14`, with the latest CSV bundle at 14,446,682 bytes uploaded
   2026-09-13 and the freely-available delayed bundle at 14,343,826 bytes
   uploaded 2026-08-23. jolpica is in any case a build-time-only role (see
   [source-roles.md](source-roles.md)), so this bounds nothing we publish — it
   bounds how quickly a cross-check can run.
3. **Stewards retroactively amend results for days after a race.**
   Classifications change. Penalties are applied after the flag. Appeals
   succeed.

Therefore: **pages published within roughly 72 hours of a race may be factually
wrong**, and the site says so on the page rather than hoping nobody notices.
Ingest output is committed as data, so the site is always buildable from the
repository alone and CI never needs network access to F1.

The spine refreshes on its own cadence: F1DB releases after every race, using
CalVer `YYYY.RR.MICRO` where `RR` is the round number and `RR=0` is pre-season.
The current release is `v2026.14.0`, published 2026-09-13. The pipeline
resolves the newest release programmatically rather than pinning a tag by hand,
and records the resolved tag in every artifact it emits.

## 2. The stamp

Every page carries a **data as of** stamp. It is not a tooltip and not a
footnote; it is a designed element in the page's standing furniture, set in the
mono face with `--f1-numeric` applied.

```
Data as of 13 September 2026 · F1DB v2026.14.0 · ingest 2026-09-13 22:41 UTC
```

The stamp is generated, never typed. Its fields:

| Field | Source | Example |
| --- | --- | --- |
| `dataAsOf` | The latest event covered by the ingest, as a date | `2026-09-13` |
| `spineRelease` | The resolved F1DB release tag | `v2026.14.0` |
| `ingestAt` | UTC timestamp when the local ingest completed | `2026-09-13T22:41:07Z` |
| `sources` | The source ids that actually supplied values on this page | `["f1db"]` |
| `classification` | The staleness class, §3 | `final` |
| `tier` | The coverage tier of the entity | `archival` |
| `prose` | `authored` or `reviewed` — never `generated` | `reviewed` |

`sources` is not hand-maintained. It is the union of the provenance sets on
every emitted payload the page consumes, produced by the single writer
described in [source-roles.md §4](source-roles.md). A page that consumes no
FastF1-derived value does not credit FastF1, and cannot be made to.

**Timezones.** Session times are stored as UTC with an explicit circuit
timezone and are always rendered with a visible label. A rendered time without
a timezone is a defect. Without this rule every schedule on the site is subtly
wrong, and subtly wrong is the worst kind.

## 3. Staleness classes

`classification` is a first-class field on every race record, alongside `tier`.
It selects copy, and in one case it selects a whole page state.

| Class | Meaning | When | Page treatment |
| --- | --- | --- | --- |
| `provisional` | Results are inside the amendment window | From the chequered flag until the window closes (§4) | The provisional state, §4 |
| `final` | Results are settled for this event | Window closed and the spine release for that round has landed | Normal page, stamp only |
| `amended` | A result changed after it was first published | A diff against a prior release changes a classification, a position or a points total | Normal page plus a dated amendment note, §5 |
| `historic` | Pre-1996 archival record | Any archival-tier race | Normal page; the stamp names the spine release, since the underlying record can still be corrected upstream |
| `absent` | The data does not exist for this entity and tier | Structural, by tier | Honest-absence copy, §6 |

`historic` is not the same as `final`. Historical F1 records are still being
corrected — F1DB ships amended rows for races run seventy years ago — so an
archival page's figures are as-of a release, not eternal. Treating a 1953 page
as immutable is how a site quietly preserves an error for a decade.

## 4. The provisional classification state

This is a real designed state, not a badge. A race page in `provisional`
renders differently, and the difference is the point.

**Window.** Opens at the chequered flag. Closes at the later of: 72 hours after
the session end, or the landing of the F1DB release for that round. Both
conditions, because a release that arrives at 36 hours can still predate a
post-race stewards' decision, and a quiet weekend can still see a release
delayed past 72 hours.

**What changes on the page:**

| Element | Provisional | Final |
| --- | --- | --- |
| Standing notice | A full-width statement at the head of the results section naming the window and what may still change | absent |
| Classification table | Rendered; every position cell marked as provisional in the accessible name as well as visually | Rendered plainly |
| Championship standings | Rendered with the same notice; a standings change is the most common consequence of a late penalty | Plain |
| Derived metrics | **Suppressed.** Fuel-corrected pace, degradation fits, overtake counts and reliability figures do not render | Rendered |
| Method links | Present on any figure that does render | Present |
| Records and superlatives | Suppressed. No "fastest ever", no "first since" | Rendered |
| Search index | Indexed, with the state included in the record | Indexed |

Derived metrics are suppressed rather than shown-with-a-caveat because a
disqualification changes the population every one of them is computed over.
A degradation fit that silently includes a car later excluded from the results
is not a caveated number; it is a wrong one.

The copy is stated once, plainly, in the site's own voice (see
[editorial-voice.md](editorial-voice.md)):

> Classification provisional. The stewards may amend results for several days
> after a race. This page will be rebuilt when the classification is final;
> derived figures are withheld until then.

No countdown timer, no live status dot, no "check back soon". The page states
the condition and the reason and stops.

## 5. Amendments

When a rebuild produces a different classification, position or points total
for a race already published, the page enters `amended` and carries a dated
note beneath the results table:

> Amended 2026-09-16. Car 44 reclassified from 4th to 5th following a
> post-race penalty. Championship standings updated accordingly.

Three rules:

1. **Amendments are additive.** The note stays permanently. Silent correction
   is how a reference loses the right to be trusted.
2. **The diff is machine-detected.** The pipeline compares the emitted payload
   for each race against the previously published payload and raises an
   amendment when a monitored field changes. Monitored fields:
   `positionNumber`, `positionText`, `points`, `reasonRetired`, `gapLaps`,
   `timeMillis`. It is not a human's job to notice.
3. **Downstream recomputation is mandatory.** An amended race invalidates the
   season standings page, the affected team-season pages, the affected driver
   records and any record page the result touches. The incremental build's
   `cacheKey` on `getStaticPaths()` includes the race payload hash precisely so
   that an amendment forces those pages to re-render.

## 6. Honest absence

An absence is a designed state, not an empty chart. The rule from the project's
third design principle: a missing dataset produces copy explaining what is
missing and why — never an empty axis, a zero, or a spinner that never
resolves.

Absence has structural causes, and the copy names the actual one:

| Cause | Boundary | Copy names |
| --- | --- | --- |
| Tier | Telemetry begins 2018; lap-by-lap timing begins 1996 | The era, not a failure |
| Session support | `F1ApiSupport` is false for the session | That the timing feed does not cover it |
| Layout unresolved | The circuit-layout registry has no verified binding for this race | That the layout is unconfirmed, and shows no geometry rather than the wrong geometry |
| 3D tier | The circuit is standard or outline tier | The tier, and links to the 2D layout |
| Source gap | A value is missing from the spine and may not be filled from a build-time-only source | That it is not yet published |

Roughly **85% of race pages have no telemetry, no position data, no 3D replay,
no speed traces and no mini-sector map.** This is the normal case, not the
exception, which is why absence gets its own page template per tier rather than
eleven empty panels on the modern one.

## 7. Every derived number links to its method

A figure is *derived* if it is not read directly from a source field. A lap
time read from `f1db-races-race-results.csv` is not derived. A fuel-corrected
pace, a degradation slope, a clean-air pace, an overtake count, a pit-loss
delta and a teammate delta all are.

**Every derived figure is rendered through a component that requires a method
slug, and the slug must resolve to a published page at `/methods/<slug>/`.**

```astro
---
// components/Derived.astro
const { value, unit, method, inputs } = Astro.props;
---
<span class="derived num" data-method={method}>
  <a href={`/methods/${method}/`}>{value}<span class="unit">{unit}</span></a>
  <span class="visually-hidden">
    Derived figure. Method: {method}. Computed from {inputs}.
  </span>
</span>
```

Three consequences:

1. **A derived figure without a method slug does not compile.** The prop is
   required and the build fails on a missing one.
2. **A slug that does not resolve fails the link check**, which runs across all
   pages. Dense cross-linking at this scale rots silently; the link checker is
   the only reason it does not.
3. **The method page is the definition of record.** It carries the formula, the
   inputs, the exclusions, the worked example and the hand-verified fixture the
   golden-file test runs against. The `/methods/` section of the site is the
   published knowledge base — this is the structural form of "every number is
   traceable".

A worked example of what a method page must state, using the degradation fit:

```
inputs      laps where IsAccurate is true, within one stint, on one compound
exclusions  in-laps, out-laps, laps under SC/VSC/red (TrackStatus != "1"),
            residuals beyond ±1200 ms, stints with fewer than 4 remaining laps
pre-step    fuel correction applied unconditionally before fitting
fit         robust linear regression of corrected lap time on tyre age
output      seconds per lap per lap of tyre age, with the fit's interval
```

The pre-step is not optional and is the reason the method page exists: **fuel
load does not cancel out of a degradation slope.** It is collinear with tyre
age within a stint and biases the slope toward zero. A site that publishes
degradation without saying whether fuel was corrected has published a number
nobody can check.

## 8. Lap-level provenance

Two FastF1 flags are provenance, not data quality, and they reach the page:

- **`IsAccurate`** is true only when a lap is not an in- or out-lap, was set
  under green or yellow, is not the first lap after a safety-car period, has a
  lap time and all three sector times, and the sector times sum to the lap
  time. Every metric that consumes laps states whether it filters on it. Most
  do.
- **`FastF1Generated`** marks a lap the library synthesised — for example a
  partial final lap for a retirement. A synthesised lap is never presented as a
  recorded one. Where it appears in a chart it is marked, and where it would
  change a total it is excluded and the exclusion is stated.

The documented alignment caveat is carried onto any page that overlays two
laps: expect an error of around ±10 m when overlapping telemetry from different
laps, because the lap-time reference is synchronised on the sector time
triggered with the lowest latency. A 3D render must not imply a precision the
source lacks.

## 9. Reproducibility

The site must rebuild identically from the repository alone, with no network
access to F1.

- Ingest output is committed as data. CI reads the repository, not the feeds.
- The FastF1 cache is restored from CI cache keyed by season and round, and
  reproducible rebuilds run with the cache in offline mode so no request is
  issued. Cached requests do not count toward rate limits, which is also why
  offline rebuilds are free.
- The cache-configuration call is written to survive the next FastF1 minor:
  `enable_cache()` is current in 3.8.3 but is deprecated on the 3.9 line in
  favour of the keyword-only `Cache.configure(*, cache_dir=None,
  force_renew=False, ignore_version=False, use_requests_cache=True)`. Pin the
  version or write for both.
- Every emitted artifact records the resolved spine release, the ingest
  timestamp and its provenance set, so a build is auditable after the fact
  without re-running it.

**Caching at the edge is not under our control.** GitHub Pages sets
`max-age=600` on *every* file, including content-hashed assets, so long-lived
immutable caching is impossible; freshness on the live site depends on Fastly
edge caching and ETag 304s. It also serves gzip only — never brotli — so
emitting `.br` siblings is dead weight against the 1 GB cap. Range requests are
supported (`206` with `content-range`), which is what makes chunked search
indexes and byte-ranged Parquet reads viable.

## 10. CI gates

| Gate | Asserts | Fails build |
| --- | --- | --- |
| Golden-file metrics | Every derived metric reproduces a hand-verified fixture — a known lap chart, a known pit-stop table | yes |
| Method resolution | Every `data-method` slug resolves to a page under `/methods/` | yes |
| Link check | All internal links across all pages resolve | yes |
| Stamp presence | Every page emits a complete `dataAsOf` / `spineRelease` / `ingestAt` triple | yes |
| Provisional suppression | No derived figure renders on a page whose `classification` is `provisional` | yes |
| Amendment detection | A monitored field changing against the previous publish produces an `amended` note | yes |
| Schema validation | All emitted JSON validates against its schema | yes |
| Timezone labelling | No rendered session time lacks a visible timezone | yes |
| Prose state | No page carries `prose: generated` | yes |
| axe / Lighthouse CI | Accessibility checks and performance budgets | yes |
| Visual regression | One representative page per coverage tier | yes |

## 11. The runbook

The post-race ingest is a human procedure and is documented as one at
`Docs/RUNBOOK.md`, covering the normal weekend, triple-headers, and what
happens when the maintainer is away. The site's honesty about staleness is what
makes an absent maintainer survivable: a page that is three weeks old and says
so is a working page, and the amendment mechanism catches up when the ingest
next runs.

Related: [source-roles.md](source-roles.md) for what may supply a value at all,
[data-licensing.md](data-licensing.md) for why the spine is the only thing that
can, and [editorial-voice.md](editorial-voice.md) for how absence and
provisionality are written.
