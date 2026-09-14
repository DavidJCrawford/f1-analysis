---
type: Reference
title: Build and release
description: The GitHub Actions deploy workflow, the human-in-the-loop ingest that CI cannot perform, the provisional-data window, and the gates that block a bad publish.
resource: https://docs.astro.build/en/guides/deploy/github/
tags: [github-actions, deploy-pages, ci, release, runbook, quality-gates, provenance]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: astro_deploy_github
    resource: https://docs.astro.build/en/guides/deploy/github/
    title: Astro — Deploy to GitHub Pages
  - id: deploy_pages
    resource: https://github.com/actions/deploy-pages
    title: actions/deploy-pages
  - id: upload_pages_artifact
    resource: https://github.com/actions/upload-pages-artifact
    title: actions/upload-pages-artifact
  - id: configure_pages
    resource: https://github.com/actions/configure-pages
    title: actions/configure-pages
  - id: actions_limits
    resource: https://docs.github.com/en/actions/reference/limits
    title: GitHub Actions limits
  - id: actions_cache
    resource: https://docs.github.com/en/actions/reference/dependency-caching-reference
    title: GitHub Actions dependency caching reference
  - id: astro_incremental
    resource: https://docs.astro.build/en/reference/experimental-flags/incremental-build/
    title: Astro experimental.incrementalBuild
  - id: attestations
    resource: https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations
    title: GitHub artifact attestations
  - id: fullthrottle
    resource: https://github.com/Chiroyce1/FullThrottle
    title: Chiroyce1/FullThrottle README
  - id: custom_domain
    resource: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
    title: Managing a custom domain for a GitHub Pages site
status: stable
---

# Build and release

**This is a weekly publication, not a build.** Three facts make it one, and none
of them would be discovered until they hurt:

- **GitHub-hosted runners cannot ingest.** F1's live-timing archive blocks
  datacenter IP ranges, including Actions runners.
- **The free jolpica dump is 14 days delayed.**
- **Stewards retroactively amend results for days after a race.**

So a human runs a local ingest after each race weekend, and pages published within
roughly 72 hours of a race may be factually wrong. Everything below is shaped by
that.

## 1. The two halves

```
  HUMAN, residential IP                     CI, GitHub Actions
  ─────────────────────                     ──────────────────
  fetch    FastF1 -> .ff1pkl                build    astro build
           + data/raw/**/*.sha256           verify   gates (§5)
  transform pandera, uniform grid           deploy   actions/deploy-pages
  emit     pydantic, canonical JSON,
           .bin + manifest + sha256
  commit   ingest output as data
```

**Ingest output is committed as data**, so the site is always buildable from the
repo alone and CI never needs network access to F1. This is not a convenience: it
is what makes the deploy deterministic and re-runnable, and it is what lets CI
fail loudly on a stale manifest rather than silently publishing an empty race.

The stage graph, validation and provenance rules are in
[Data pipeline](data-pipeline.md).

## 2. Why CI cannot ingest

FullThrottle — a production site on the same FastF1 → Parquet → browser stack —
states verbatim:

> "F1's live timing servers block cloud/datacenter IP ranges (including
> GitHub-hosted Actions runners), so automated cron runs in the cloud return
> empty data."

Corroborating: FastF1 issue #615 reports a 403 from
`livetiming.formula1.com/static/2022/.../SessionInfo.jsonStream`, labelled
*external* by the maintainer. The same paths return 200 from a residential IP.

FastF1's in-library mitigation — retrying `https://livetiming-mirror.fastf1.dev`
whenever the primary returns `status >= 400` — is real code present since v3.6.0,
but the mirror is **currently dead**: 404 (a 27,150-byte HTML page) for every path
tried, including a 2024 session and the 2026-09-13 Spanish GP race path that the
primary serves with 200. There is no working in-library workaround today.

The options, recorded honestly: a human on a residential connection (the current
plan), or a **self-hosted runner on a residential connection** (the same thing,
automated, and the upgrade path if the manual step becomes a bottleneck).

## 3. The deploy workflow

Two shapes. The canonical Astro one, which is the reference:

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
  workflow_dispatch:
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout your repository using git
        uses: actions/checkout@v7
      - name: Install, build, and upload your site
        uses: withastro/action@v6
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v5
```

Requires a committed lockfile and the repository's Pages source set to
**"GitHub Actions"**.

This project needs the **custom shape**, because the incremental build cache must
be restored and a size gate must run:

```
actions/checkout@v7
  -> actions/setup-node          (Node 22+)
  -> actions/cache               (node_modules/.astro, keyed on the data digest)
  -> npm ci
  -> actions/configure-pages@v6  (capture steps.pages.outputs.base_path)
  -> npm run build
  -> verify gates                (§5)
  -> actions/upload-pages-artifact@v5   path: ./dist
  -> deploy job: actions/deploy-pages@v5
```

Verified current major tags (from `git ls-remote --tags`):
`withastro/action` v0–v6, `actions/deploy-pages` v1–v5, `actions/checkout` v1–v7,
`actions/configure-pages` v0–v6, `actions/upload-pages-artifact` v0–v5.

Action inputs worth knowing:

| Action | Inputs | Defaults |
| --- | --- | --- |
| `actions/deploy-pages` | `token`, `artifact_name`, `timeout`, `error_count`, `reporting_interval`, `preview` | `${{ github.token }}`, `"github-pages"`, `"600000"` ms (= 10 min), `"10"`, `"5000"`, `"false"`. Output: `page_url` |
| `actions/upload-pages-artifact` | `name`, `path`, `retention-days`, `include-hidden-files` | `github-pages`, `_site/` (required), `1`, `false`. Packages the directory as a gzip tar |
| `actions/configure-pages` | `static_site_generator`, `generator_config_file`, `token`, `enablement` | Outputs `base_url`, `origin`, `host`, `base_path`. **Astro is not in the `static_site_generator` list** (`nuxt`, `next`, `gatsby`, `sveltekit`) — consume `base_path` yourself |

**`actions/configure-pages` does not create the CNAME file.** With a custom
Actions workflow, GitHub creates no `CNAME` at all — commit `public/CNAME`
containing the bare domain, or the custom domain reverts on every deploy. DNS
records and the certificate timeline are in
[GitHub Pages constraints](github-pages-constraints.md).

### Caps that bound the run

6 hours max per job; 35 days max per workflow run; 20 concurrent jobs on Free,
40 Pro, 60 Team; 256 matrix jobs; **10 GB Actions cache per repository** with
7-day eviction; a workflow file over 500 KB will not start. Public repositories
get GitHub-hosted runner minutes at no cost.

Separately, **Pages deployments time out at 10 minutes**. That is the constraint
`experimental.incrementalBuild` exists to satisfy at 6,000-page scale.

### The cache that must actually restore

`experimental.incrementalBuild` keeps its cache in `node_modules/.astro/`.
**In CI that directory must be restored between runs or nothing is skipped** —
key the `actions/cache` entry on the emitted data digest so a data change
invalidates cleanly.

Two failure modes to watch for in logs rather than in exit codes:

- `build.concurrency > 1` disables the cache. Astro "logs a warning and re-renders
  every page" — the build still *succeeds*, it just silently loses all
  incrementality. Grep CI logs for that warning.
- Middleware edits do not invalidate the cache. Run `astro build --force` after
  editing middleware.

## 4. The provisional-data window

This is a design requirement, not an ops note.

- **Every page carries a "data as of" stamp.**
- **Races inside the amendment window render a "provisional classification"
  state** — a real designed state, with its own copy, not a tooltip and not a
  grey badge.
- **A runbook lives at [`Docs/RUNBOOK.md`](../../RUNBOOK.md)**, covering the post-race ingest,
  triple-headers, and what to do when the maintainer is away.

The mechanism that makes amendment detectable is provenance hashing: every
emitted file records the **sha256 of the raw upstream bytes** it derived from, and
a changed `source_sha256` is the only reliable signal that a past race needs
rebuilding. Stewards amend results after the fact — penalties, deleted laps,
reinstated classifications — and nothing else in the chain announces it.

Two related correctness rules that belong in the release checklist because they
produce *confidently wrong* pages rather than obviously broken ones:

- **Retirement causes and laps-down margins for 2024–2026 must come from F1DB,
  not jolpica.** jolpica collapses retirement causes from **2024** onward — not
  2025 as its docs state — returning only `Finished / Lapped / Retired / Did not
  start / Disqualified`, and flattening `+N Laps` to a single `Lapped` over the
  same range.
- **Session times are stored as UTC with an explicit circuit timezone and always
  rendered with a visible label.** Otherwise every schedule on the site is subtly
  wrong.

## 5. Quality gates

Adversarial verification corrected 83 of roughly 252 initial research claims. The
main correctness risk on this project is therefore **shipping confidently-presented
wrong numbers**, not shipping a broken build. CI blocks on:

| Gate | What it catches |
| --- | --- |
| **Golden-file tests** for every derived metric against hand-verified reference races (a known lap chart, a known pit-stop table) | A metric that silently changes meaning |
| **Schema validation** of all emitted JSON (`check-jsonschema` against the pydantic-generated schemas shipped in `site/data/schema/`) | Shape drift between pipeline and front end |
| **Binary assertions** — int16 deltas never saturate, `len(bin) == cars × channels × samples × 2`, every manifest byte offset even, recorded sha256 re-verified | Corrupt replays that decode to garbage rather than failing |
| **Link checking** across all pages | Dense cross-linking at 6,000-page scale rots silently |
| **axe** accessibility checks | Contrast and semantics regressions |
| **Lighthouse CI** budgets | The targets in [Performance budgets](performance-budgets.md) |
| **Visual regression** on a representative page per coverage tier | A template change that quietly breaks the archival tier |
| **Size gate** — `du -sh dist`, fail above ~700 MB | The 1 GB published-site ceiling |
| **Stale-manifest check** | CI publishing a race the human never ingested |

The tier-per-page visual regression matters specifically because the four coverage
tiers (archival, timing, telemetry, modern) select different templates, and a
change made while looking at a 2026 page can break a 1962 page without anyone
noticing.

## 6. Reproducibility of the release

- **Toolchain pinned.** `uv.lock` committed; CI runs `uv sync --frozen`. Exact
  pins for `fastf1`, `pyarrow`, `pydantic`, `pandera`. Node 22+, `npm ci` against
  a committed lockfile. three.js pinned **exactly** (`0.186.0`) — `^` ranges are
  unsafe on `0.x` semver, and `postprocessing@6.39.5` peers `three >= 0.168.0 <
  0.187.0`, so the r187 release due around November 2026 will break the build the
  moment three.js is bumped.
- **Build is a pure function.** Transform and emit run under
  `fastf1.Cache.offline_mode(True)`; JSON is serialised canonically
  (`sort_keys=True, separators=(',', ':'), ensure_ascii=False`) with fixed float
  rounding, so rebuilding an unchanged race produces a byte-identical file and
  git shows no diff. `SOURCE_DATE_EPOCH` is honoured for embedded timestamps.
- **Optional signing.** Release assets can carry GitHub artifact attestations —
  `actions/attest@v4` with `subject-path` and
  `permissions: { id-token: write, contents: read, attestations: write }`,
  verified with `gh attestation verify PATH -R owner/repo`.

## 7. Upgrade checklist

Because three.js breaks something every revision and the peer lattice is tight:

1. Bump `three` to the exact new revision.
2. **Verify `postprocessing`'s peer range** covers it. If not, stop — either wait
   for a matching `postprocessing` release or drop back.
3. Re-run visual regression on the track ribbon specifically. The ribbon depends
   on `Curve` internals and on the frame construction described in
   [three.js track rendering](threejs-track-rendering.md).
4. Check the migration guide for renames (the `PostProcessing` → `RenderPipeline`
   and `Clock` → `Timer` moves are the pattern to expect).
5. Re-measure the 3D chunk against its budget.

`camera-controls@3.1.2` has no upper three.js bound and does not gate the upgrade;
`postprocessing` is the single blocking pin.

## 8. Release cadence

| Trigger | Action |
| --- | --- |
| After each race weekend | Human runs `fetch` → `transform` → `emit` locally; commits the ingest output; opens a PR |
| On merge to `main` | Full CI build, gates, deploy |
| Within ~72 h of a race | Affected race pages render the provisional-classification state |
| When `source_sha256` changes for a past race | That race alone is rebuilt |
| Weekly in season | Incremental rebuild re-renders ~25 current-season pages, not 1,172 |

A normal race weekend rebuilds **one race directory out of ~190**.

## Open items

- Whether `withastro/action@v6` permits injecting an `actions/cache` step for the
  incremental cache, or whether the hand-rolled workflow shape in §3 is mandatory,
  is **unverified**. The hand-rolled shape is assumed.
- Real wall-clock for a ~6,000-page build on a 2-core `ubuntu-latest` runner is
  **unmeasured**, and with it whether the build plus the 10-minute deploy window
  is comfortable or tight.
- Whether the FastF1 mirror ever serves from a GitHub-hosted runner is
  **untested from CI**. If it does, the local-ingest constraint disappears and
  the pipeline becomes CI-native — worth a throwaway workflow before the
  architecture is fixed.
- How often F1 retroactively amends archive files is **uncharacterised**; if files
  are rewritten on every stewards' decision the `source_sha256` rule churns.
- Whether the site and data live in one repository or two is one of the spec's
  open decisions. The recommendation is **split, from the start**, because of the
  1 GB cap.
