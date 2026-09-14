---
type: Reference
title: Site architecture on Astro 7
description: Why Astro 7 generates this site's ~2,400–6,000 pages, and the routing, hydration, chunking, search and base-path mechanics that follow from that choice.
resource: https://docs.astro.build/en/reference/configuration-reference/
tags: [astro, ssg, islands, routing, pagefind, base-path, vite, rolldown]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: astro_7_release
    resource: https://astro.build/blog/astro-7/
    title: Astro 7 release announcement (2026-06-22)
  - id: astro_6_release
    resource: https://astro.build/blog/astro-6/
    title: Astro 6 release announcement (2026-03-10)
  - id: astro_config
    resource: https://docs.astro.build/en/reference/configuration-reference/
    title: Astro configuration reference
  - id: astro_incremental
    resource: https://docs.astro.build/en/reference/experimental-flags/incremental-build/
    title: Astro experimental.incrementalBuild
  - id: astro_directives
    resource: https://docs.astro.build/en/reference/directives-reference/
    title: Astro template directives reference
  - id: astro_endpoints
    resource: https://docs.astro.build/en/guides/endpoints/
    title: Astro endpoints guide
  - id: astro_fonts
    resource: https://docs.astro.build/en/guides/fonts/
    title: Astro Fonts API guide
  - id: astro_transitions
    resource: https://docs.astro.build/en/guides/view-transitions/
    title: Astro view transitions and ClientRouter
  - id: vite8_migration
    resource: https://vite.dev/guide/migration
    title: Vite 8 migration guide
  - id: rolldown_chunks
    resource: https://rolldown.rs/options/output-advanced-chunks
    title: Rolldown advanced chunk options
  - id: configure_pages
    resource: https://github.com/actions/configure-pages
    title: actions/configure-pages action.yml
  - id: pagefind
    resource: https://pagefind.app/
    title: Pagefind static search
  - id: bcd_view_transition
    resource: https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@view-transition
    title: MDN @view-transition browser compatibility
status: stable
---

# Site architecture on Astro 7

The site is a static build of roughly **2,432 pages at launch** and **5,000–6,000**
once team×season and circuit×season cross-sections exist. That number, not taste,
selects the framework and shapes every decision below.

## 1. The page-count budget

Entity totals verified against live API totals (`MRData.total` from
`https://api.jolpi.ca/ergast/f1/<entity>/?limit=1`, 2026-09-14) and cross-checked
against F1DB v2026.14.0.

| Route | Count |
| --- | ---: |
| `/races/[season]/[round]/` | 1,172 |
| `/drivers/[driverId]/` | 881 (phase 2) |
| `/teams/[constructorId]/` | 214 |
| `/circuits/[circuitId]/` | 78 |
| `/seasons/[year]/` | 77 |
| index / about / data / colophon / methods | ~10 |
| **Baseline subtotal** | **≈ 2,432** |
| `/teams/[constructorId]/[season]/` | ~1,200–1,500 real pairs |
| `/circuits/[circuitId]/[season]/` | ~1,100 |
| **Full build** | **≈ 5,000–6,000** |

Calibration: Astro's own benchmark renders **6,313 pages in 73.53 s** (down from
114.54 s pre-7.0), so pure HTML render time here is ~1–2 minutes on benchmark
hardware. HTML rendering is therefore *not* the binding constraint. The three
real constraints are image processing, the 1 GB published-site ceiling, and
memory inside `getStaticPaths()`.

## 2. Why Astro 7 wins

Version pinned: **astro 7.3.2**. Astro 7.0 shipped **2026-06-22** on Vite 8 with
Rolldown; Node 22 is the floor (inherited from Astro 6). The Rust `.astro`
compiler is not new in 7 — it shipped as an experimental flag in **Astro 6
(2026-03-10)** and became the default in 7.

Published build-time improvements (Astro's own benchmarks, 7.0 post):

| Site | Pages | Before | After |
| --- | ---: | ---: | ---: |
| docs.astro.build | 6,313 | 114.54 s | 73.53 s |
| astro.build | 308 | 62.70 s | 24.24 s |
| biomejs.dev | 6,488 | 176.39 s | 149.90 s |
| developers.cloudflare.com | 8,431 | 386.89 s | 261.94 s |
| tauri.app | 7,117 | 86.12 s | 55.33 s |
| aspire.dev | 13,275 | 385.84 s | 326.11 s |

The decisive properties, in order of weight for this project:

1. **Zero JS by default.** An archival-tier race page — the ~85% case — ships no
   JavaScript at all. That is what makes the `< 40 kB gzip` budget in
   [Performance budgets](performance-budgets.md) achievable rather than aspirational.
2. **Per-component hydration.** `client:visible` isolates three.js into a lazy
   chunk on exactly the pages that have a 3D scene, with no framework runtime on
   the others.
3. **Build-time JSON endpoints.** Per-race data ships at a stable URL instead of
   being inlined into HTML or bundled into a JS chunk.
4. **`experimental.incrementalBuild` (7.2).** The reason a 6,000-page weekly
   rebuild is tractable.
5. **Build-time image optimisation** via `astro:assets`/sharp, with no runtime
   image service — relevant because there is no server.

Breaking changes that bite a typographically-led site specifically:

- HTML is **no longer auto-corrected**; an unclosed tag is a hard error.
- Whitespace between inline elements follows **JSX conventions** — a newline
  between `<span>`/`<a>` siblings no longer renders as a space. Any markup
  migrated from Astro ≤ 6 that relied on that needs auditing.

Rejected alternatives, briefly: **SvelteKit + adapter-static 3.0.10** is a real
second choice (and `kit.paths.relative` defaults to `true`, a genuinely better
base-path story), but `prerender.entries` defaults to `["*"]`, which only covers
routes with no required params — 1,172 race routes need explicit entries or total
link coverage — and `precompress` is dead weight here (see
[GitHub Pages constraints](github-pages-constraints.md)). **Next.js 16.3.5**
`output: 'export'` ships React to every page and disables headers, redirects,
rewrites, ISR and the default image loader; it *can* emit per-route JSON via a
Route Handler with `export const dynamic = 'force-static'`, so it is not without
a data story, but it is worse on every axis that matters here.

## 3. Incremental build

```js
// astro.config.mjs
export default defineConfig({
  experimental: {
    incrementalBuild: true,
  },
});
```

Each generated path returns a `cacheKey` — "a value that changes whenever the
page's content changes, such as a content hash, a version number, or an updated
timestamp from your data source":

```ts
export async function getStaticPaths() {
  const races = await getCollection('races');
  return races.map((r) => ({
    params: { season: r.data.season, round: r.data.round },
    props: { race: r },
    cacheKey: r.digest,          // content-collection digest
  }));
}
```

Mechanics and traps:

| Fact | Consequence |
| --- | --- |
| Astro hashes each route's **full module graph** (template, layouts, components, imported assets, package code) | Touching the race layout re-renders all 1,172 race pages, not just changed ones |
| Cache lives in `node_modules/.astro/` | **Must be restored in CI** via `actions/cache` or nothing is skipped |
| `build.concurrency > 1` disables the cache | Astro **logs a warning and re-renders every page** — it does not error. Watch CI logs for it |
| Middleware edits do not invalidate | Run `astro build --force` after editing middleware |
| Server islands need a stable `ASTRO_KEY` | Not used on this site (pure static) |

Payoff: the F1 archive is almost entirely immutable. A weekly in-season rebuild
should re-render the ~25 current-season race pages plus aggregates, not 1,172.
Known risk: `withastro/astro#17615` reports the incremental cache missing image
imports — spike this before relying on it, and keep imagery out of the per-page
Astro pipeline anyway (§7).

## 4. Routing and URL shape

Astro defaults `build.format: 'directory'` (emits `dist/races/2026/singapore/index.html`).
Set `trailingSlash: 'always'` explicitly — the default is `'ignore'`, which
silently permits slash-less internal links, and every one of those costs a 301
round trip on GitHub Pages across hundreds of index entries.

Note the redirect trigger precisely: GitHub Pages 301s a **directory URL missing
its trailing slash** (`/getting-started` → `/getting-started/`). It resolves
**extensionless paths to `.html` with a plain 200**, no redirect. So
`build.format: 'file'` is not penalised by an extra hop either; the trailing
slash on directory URLs is the only thing that matters. Details and the verifying
requests are in [GitHub Pages constraints](github-pages-constraints.md).

Slug policy (from the spec): slugs derive from F1DB canonical IDs, never display
names. Renamed lineages resolve to a lineage root, and `redirects.json` is
generated at build time and emitted as Astro redirects. A root `404.html` is
required — GitHub Pages serves it for unmatched paths.

## 5. Islands and chunking

Directives, verbatim from the reference:

| Directive | Behaviour |
| --- | --- |
| `client:load` | "Load and hydrate the component JavaScript immediately on page load." |
| `client:idle` | Hydrate after `requestIdleCallback`; optional `timeout` ms |
| `client:visible` | Hydrate once in viewport; optional `rootMargin` px |
| `client:media` | Hydrate when a CSS media query matches |
| `client:only={framework}` | Skip SSR entirely; supports `slot="fallback"` |
| `server:defer` | Server islands — not applicable to a pure static build |

Two levels of laziness for the 3D viewer. Level 1 is the directive; level 2 is a
dynamic `import()` inside the island so three.js is not even in the island's own
chunk until the reader opts in:

```astro
<TrackViewer client:visible={{ rootMargin: '400px' }} circuitId={circuit.id} />
```

```ts
// inside the island, on user intent
const { buildScene } = await import('../three/scene.ts');
```

Chunk grouping moved in Vite 8: the object form of `output.manualChunks` is
**removed** and the function form deprecated. `build.rollupOptions` still works
but is a deprecated alias of `build.rolldownOptions`. Use Rolldown's
`codeSplitting`:

```js
// astro.config.mjs
vite: {
  build: {
    rolldownOptions: {
      output: {
        codeSplitting: {
          minSize: 20000,
          groups: [
            { name: 'three-core',   test: /node_modules[\\/]three[\\/]build/,    priority: 30 },
            { name: 'three-addons', test: /node_modules[\\/]three[\\/]examples/, priority: 25 },
            { name: 'vendor',       test: /node_modules/,                        priority: 10 },
          ],
        },
      },
    },
  },
}
```

`codeSplitting` accepts `minSize`, `maxSize`, `minShareCount`, `minModuleSize`,
`maxModuleSize`, `includeDependenciesRecursively` and `groups`; each group takes
`name`, `test` (string substring, RegExp, or function on module id), `priority`
(higher wins, ties broken by lower array index) and per-group size thresholds.
Rolldown warns that manual splitting can change behaviour when side effects run
before modules load.

**Chunk count matters more than chunk size here.** GitHub Pages stamps
`max-age=600` on every file, so after ten minutes each separately-fetched chunk
costs a revalidation RTT. Prefer a few coarse, stable chunks (app shell,
`three-core`, per-page data) over dozens of micro-chunks, and use
`<link rel="modulepreload">` to hide revalidation latency.

Other Vite 8 defaults worth knowing: `build.target` is
`'baseline-widely-available'` (Chrome ≥ 111, Edge ≥ 111, Firefox ≥ 114,
Safari ≥ 16.4 — comfortably WebGL2); `build.assetsInlineLimit` 4096 bytes;
`build.chunkSizeWarningLimit` 500 kB (three.js will trip it — raise it
deliberately); Oxc replaces esbuild for transform and minification; Lightning CSS
is the default CSS minifier.

## 6. Data endpoints

The extension preceding `.ts` sets the output type: `src/pages/data.json.ts`
emits `/data.json`. Dynamic endpoints use bracket params plus `getStaticPaths()`.
Astro's docs: "In statically-generated sites, your custom endpoints are called at
build time to produce static files."

```ts
// src/pages/api/race/[season]/[round].json.ts
import type { APIRoute } from 'astro';
import { getCollection } from 'astro:content';

export async function getStaticPaths() {
  const races = await getCollection('races');
  return races.map((r) => ({
    params: { season: r.data.season, round: r.data.round },
    props: { r },
  }));
}

export const GET: APIRoute = ({ props }) =>
  new Response(JSON.stringify(toColumnar(props.r.data.laps)), {
    headers: { 'content-type': 'application/json' },
  });
```

Three rules on wire shape, all measured in
[Telemetry encoding](telemetry-encoding.md):

1. **Structure-of-arrays, not array-of-objects.** A realistic 1,040-row × 25-column
   laps table is 453,917 B as array-of-objects (31,840 B gzipped) and
   **142,265 B columnar (15,276 B gzipped)** — 3.2× smaller raw, 2.1× gzipped.
2. **Anything over ~10 kB is fetched, not imported.** Vite's `json.stringify:
   'auto'` only switches large JSON to `JSON.parse("…")` above roughly 10 kB;
   above that threshold the data belongs outside the JS module graph entirely.
3. **Always prefix with the base.** `fetch(import.meta.env.BASE_URL + 'api/race/2026/17.json')`,
   never `fetch('/api/…')`.

Register binary payload extensions so Vite emits them as hashed assets rather
than parsing them: `assetsInclude` for `.glb`, `.ktx2`, `.parquet`, `.arrow`, `.bin`.

## 7. Content collections and build memory

```ts
// src/content.config.ts
import { defineCollection, reference, z } from 'astro:content';
import { file, glob } from 'astro/loaders';

const races = defineCollection({
  loader: file('./data/races.json'),          // array; each entry needs a unique `id`
  schema: z.object({
    season: z.number(),
    round: z.number(),
    tier: z.enum(['archival', 'timing', 'telemetry', 'modern']),
    circuitId: reference('circuits'),
  }),
});

export const collections = { races };
```

`file()` parses a JSON/YAML/TOML array; `glob({ base, pattern })` handles
per-file content. Query with `getCollection` / `getEntry`, render markdown bodies
with `render(entry)`, and cross-link with `reference()`.

Build discipline at this scale:

- `build.concurrency` default is **1** and must stay 1 for incremental builds, so
  single-threaded render speed is the ceiling.
- Collect shared data **once** inside `getStaticPaths()` and pass only the
  per-page slice through `props`. Read each race's payload lazily from disk
  rather than holding 1,172 payloads in memory.
- Do **not** run one `astro:assets`/sharp operation per page across 6,000 pages.
  Generate circuit and team imagery once into `public/` through a separately
  cached pipeline. The widely-reported failure mode for large Astro builds is
  image processing, not HTML.

## 8. Fonts

The Fonts API is stable since Astro 6 (moved from `experimental.fonts` to a
top-level `fonts` key). Built-in providers on `fontProviders`: `google()`,
`fontsource()`, `adobe()`, `bunny()`, `fontshare()`, `googleIcons()`, `npm()` —
plus `local()` for self-hosted files, eight in total.

```js
import { defineConfig, fontProviders } from 'astro/config';

export default defineConfig({
  fonts: [
    {
      provider: fontProviders.google(),
      name: 'Albert Sans',
      cssVariable: '--font-albert',
      weights: [200, 300, 600],
      styles: ['normal'],
      subsets: ['latin'],
      fallbacks: ['system-ui', 'sans-serif'],
    },
  ],
});
```

```astro
---
import { Font } from 'astro:assets';
---
<head><Font cssVariable="--font-albert" preload /></head>
```

Astro handles download, caching, **automatic fallback metric generation** (which
is what removes the swap-in layout shift) and preload tag emission. Two reasons
this matters more on GitHub Pages than elsewhere: files are served from the site's
own origin, so there is no third-party connection setup; and because nothing on
Pages is `immutable`-cacheable, keeping the font count small and preloaded is the
main lever on perceived first paint.

## 9. Search

At 2,400–6,000 pages, browse-only navigation is unusable. **Pagefind** is the
answer: it advertises full-text search on a 10,000-page site with a total network
payload **under 300 kB including the library**, and it chunks its index. Chunked
index fetching suits this host specifically, because GitHub Pages supports HTTP
`Range` requests (verified `206` with `content-range`).

## 10. Navigation and view transitions

Native cross-document view transitions are **not implementable as a requirement**:
MDN browser-compat-data for `css/at-rules/view-transition` reads
`chrome: 126`, `safari: 18.2`, `edge: mirror`, `safari_ios: mirror`, and
`firefox: { version_added: false, impl_url: "https://bugzil.la/1860854" }`.

Use Astro's `<ClientRouter />`, which degrades via `fallback="animate"` (also
`"swap"`, `"none"`). Directives: `transition:name` pairs elements across pages,
`transition:animate` takes `"fade"` (default), `"slide"`, `"initial"`, `"none"`
or an object, and `transition:persist` keeps a live element — the mechanism for a
persistent WebGL canvas.

Lifecycle events on `document`, in order:
`astro:before-preparation` → `astro:after-preparation` → `astro:before-swap`
→ `astro:after-swap` → `astro:page-load`. **Dispose geometries, materials and
textures in `astro:before-swap`**, or GPU memory creeps up across navigations;
re-initialise charts in `astro:page-load`. `data-astro-reload` on a link forces a
full page load — use it on entry into heavy 3D pages where persisting a canvas is
not wanted.

**Prefetch gotcha.** `prefetch` normally defaults to `false`, but with
`<ClientRouter />` present it defaults to `{ prefetchAll: true }`. On an index
listing 1,172 races that is 1,172 speculative requests against a 600-second-TTL
origin. Set it explicitly:

```js
prefetch: { prefetchAll: false, defaultStrategy: 'hover' }
```

then opt in per link with `data-astro-prefetch="hover" | "tap" | "viewport" | "load" | "false"`.

Accessibility side-effect that happens to match the house style: the router
announces title changes via `aria-live` and disables all its animations under
`prefers-reduced-motion`.

## 11. The base-path problem

A project site serves at `https://<owner>.github.io/<repo>/` and every absolute
URL breaks. `actions/configure-pages` exposes the value needed, verbatim from its
`action.yml`:

```yaml
outputs:
  base_url:  'GitHub Pages site full base URL. Examples: "https://octocat.github.io/my-repo", …'
  origin:    'GitHub Pages site origin.'
  host:      'GitHub Pages site host.'
  base_path: 'GitHub Pages site full base path. Examples: "/my-repo" or ""'
```

Astro is **not** in that action's `static_site_generator` list (`nuxt`, `next`,
`gatsby`, `sveltekit`), so consume `steps.pages.outputs.base_path` yourself.

- Project site: `site: 'https://<user>.github.io'`, `base: '/<repo>'`.
- User site or custom domain: `site: 'https://example.com'`, **no `base`**.
- At runtime read `import.meta.env.BASE_URL`, which "respects your `trailingSlash`
  configuration regardless of how you define `base`".
- Astro's docs warn: "all of your static asset imports and URLs should add the
  base as a prefix."

**The single most common deploy-breaking bug is a bare `fetch('/api/...')` inside
an island.** It works in `astro dev` at `/` and 404s in production under
`/<repo>/`. Decoder paths have the same problem: `public/basis/` and
`public/draco/` must be referenced as `import.meta.env.BASE_URL + 'basis/'`.

The strongest mitigation is structural: use a user/organisation site
(`<owner>.github.io`) or a custom domain, where `base` is `''` and the entire bug
class disappears. See [Build and release](build-and-release.md) for the DNS and
`public/CNAME` mechanics.

## 12. Sitemap

`@astrojs/sitemap` requires the `site` config and splits at `entryLimit`, default
**45,000** entries per file. At ~6,000 pages that is a single `sitemap-0.xml`
under `sitemap-index.xml`; no splitting configuration is needed.

## Open items

- Whether the `node_modules/.astro` incremental cache restores reliably through
  `actions/cache` at 6,000-page scale, and how large it grows, is **unverified**.
  `withastro/astro#17615` (incremental build missing the cache for image imports)
  should be reproduced before the weekly rebuild depends on it.
- Real wall-clock for a ~6,000-page build on a 2-core `ubuntu-latest` runner —
  rather than Astro's benchmark hardware — is **unmeasured**.
- Whether `withastro/action@v6` permits injecting an `actions/cache` step for the
  incremental cache, or whether the hand-rolled workflow is required, is
  **unresolved**; the hand-rolled shape is assumed in
  [Build and release](build-and-release.md).
