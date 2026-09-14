---
type: Reference
title: GitHub Pages constraints
description: Every verified GitHub Pages quota and delivery behaviour, the requests that established them, and what each one forces on the architecture.
resource: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
tags: [github-pages, hosting, limits, compression, caching, range-requests, cdn, bandwidth]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: pages_limits
    resource: https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
    title: GitHub Pages limits
  - id: large_files
    resource: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
    title: About large files on GitHub
  - id: releases
    resource: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
    title: About releases
  - id: lfs
    resource: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage
    title: About Git Large File Storage
  - id: actions_limits
    resource: https://docs.github.com/en/actions/reference/limits
    title: GitHub Actions limits
  - id: actions_cache
    resource: https://docs.github.com/en/actions/reference/dependency-caching-reference
    title: GitHub Actions dependency caching reference
  - id: upload_pages_artifact
    resource: https://github.com/actions/upload-pages-artifact
    title: actions/upload-pages-artifact
  - id: brotli_discussion
    resource: https://github.com/orgs/community/discussions/21655
    title: Community discussion 21655 — pre-compressed assets and brotli
  - id: custom_domain
    resource: https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site
    title: Managing a custom domain for a GitHub Pages site
status: stable
---

# GitHub Pages constraints

Two kinds of fact live here: **documented quotas**, quoted from GitHub's own docs,
and **verified runtime behaviour**, established by request on 2026-09-14 rather
than assumed from documentation. The second kind is where the surprises are.

## A. Documented quotas

### Pages

| Limit | Value | Quoted |
| --- | --- | --- |
| Published site size | **≤ 1 GB** | "Published GitHub Pages sites may be no larger than 1 GB." |
| Source repository | ≤ 1 GB recommended | "GitHub Pages source repositories have a recommended limit of 1 GB." |
| Bandwidth | **100 GB/month, soft** | "GitHub Pages sites have a *soft* bandwidth limit of 100 GB per month." |
| Builds | 10/hour, soft | "GitHub Pages sites have a *soft* limit of 10 builds per hour." |
| Deployment timeout | **10 minutes** | "GitHub Pages deployments will timeout if they take longer than 10 minutes." |
| Sites per account | one user/org site | "You can only create one user or organization site for each account on GitHub." |
| Rate limiting | HTTP 429 | — |

**The 10-builds/hour limit does not apply when publishing with a custom GitHub
Actions workflow** — which is this project's path — so the effective build cap is
the Actions cap, not 10/hour. That is the practical reason to use an Actions
workflow rather than the legacy branch publish on a site that rebuilds after every
session.

### The Pages artifact

`actions/upload-pages-artifact` documents two thresholds for the uploaded
`tar.gz`: an official recommendation of **under 1 GB** and a hard technical limit
of **10 GB** above which Pages will not attempt deployment. Larger artifacts also
risk the 10-minute deploy window. Its inputs: `name` (default `github-pages`),
`path` (required, default `_site/`), `retention-days` (default 1),
`include-hidden-files` (default false).

### Git object limits

| Limit | Value |
| --- | --- |
| Warning | > 50 MiB — "If you attempt to add or update a file that is larger than 50 MiB, you will receive a warning from Git" |
| Hard block | **100 MiB** — "GitHub blocks files larger than 100 MiB" |
| Browser upload | 25 MiB |
| Repository | "ideally under 1 GB", "strongly recommended" below 5 GB |

### Alternatives, each with a specific ceiling

| Store | Limits | Verdict for this project |
| --- | --- | --- |
| **GitHub Releases** | Each asset **< 2 GiB**; **up to 1,000 assets per release**; no limit on total release size or bandwidth | Right home for full per-lap telemetry, fetched on demand |
| **Git LFS** | Max file 2 GB (Free/Pro), 4 GB (Team), 5 GB (Enterprise Cloud); **metered storage and bandwidth** | **Never** for web-served assets — metered bandwidth is the worst possible property |
| **jsDelivr (GitHub CDN)** | 50 MB per file default, reduced to **20 MB** in many cases; can serve individual files even when the repo exceeds package limits | Possible escape hatch, not a plan |
| **Separate data repo + its own Pages site** | Own 1 GB cap, own 100 GB/month budget | Recommended split, keeps the site repo's history clean |

### Actions caps that bound the build

6 hours max per job on GitHub-hosted runners; 35 days max per workflow run;
20 concurrent jobs on Free, 40 Pro, 60 Team; 256 matrix jobs; **10 GB Actions
cache per repository** with 7-day eviction of unused entries (200 uploads/min,
1,500 downloads/min); a workflow file over 500 KB will not start. Public
repositories get GitHub-hosted runner minutes at no cost.

10 GB is ample for both `node_modules/.astro` (the incremental build cache) and a
raw-data cache — but *not* for a FastF1 `.ff1pkl` season cache, which belongs
outside it entirely. See [Data pipeline](data-pipeline.md).

## B. Verified delivery behaviour

### B1. gzip only, never brotli

```
$ curl -sI -H "Accept-Encoding: br, gzip, deflate" https://pages.github.com/
server: GitHub.com
content-encoding: gzip
vary: Accept-Encoding
content-length: 3844
via: 1.1 varnish
x-fastly-request-id: 1606c0c2da3d0529a7c2dea329f40450eeb8c560
accept-ranges: bytes

$ curl -sI -H "Accept-Encoding: br" https://pages.github.com/
   -> NO content-encoding header at all
   -> content-length: 14446
```

Brotli-only request returns the file **completely uncompressed**: 14,446 bytes
identity against 3,844 gzipped (73% saving from gzip; brotli would typically add
a further 15–20% and is simply unavailable). Reproduced independently against a
second Pages origin with `Accept-Encoding: gzip, deflate, br, zstd`:
`application/javascript` (133,842 B transferred), `application/json`,
`model/gltf-binary` (1,373,536 B), `application/wasm` and
`application/octet-stream` all returned `content-encoding: gzip` with
`vary: Accept-Encoding`; `image/jpeg` and `.exr` returned no `content-encoding`
at all (already-compressed types are skipped). Neither br nor zstd was ever
selected.

This matches community discussion #21655 ("Support for pre-compressed assets and
brotli compression"), open since 2019.

**What it forces:**

1. Never ship `.br` or `.gz` siblings. `precompress: true` in
   `@sveltejs/adapter-static` is dead weight that doubles artifact size and counts
   against the 1 GB cap. Pages ignores pre-compressed siblings.
2. There is no way to set a `Content-Encoding` header, because **GitHub Pages
   exposes zero response-header configuration.**
3. Application-level brotli is the only route to brotli ratios: ship an opaque
   `.br` blob and decode with a wasm decoder. Native `DecompressionStream` with
   format `"brotli"` is Chromium-only — the WHATWG Compression Spec standardises
   only `"deflate"`, `"deflate-raw"` and `"gzip"` — so it needs a polyfill on
   Firefox and Safari. Usually not worth it; prefer a more compact wire format.
4. gzip-on-the-fly means text minification still pays, JSON key shortening still
   pays, and **columnar JSON compresses notably better than array-of-objects**.
5. Binary payloads get gzipped transparently, so a raw `.bin` of int16 deltas
   transfers at its gzipped size for free. See
   [Telemetry encoding](telemetry-encoding.md).

### B2. `max-age=600` on everything, including hashed assets

```
$ curl -sI -H "Accept-Encoding: gzip" https://pages.github.com/css/pages.css
HTTP/2 200
server: GitHub.com
etag: W/"689c7eee-2fc2"
expires: Sun, 13 Sep 2026 20:46:01 GMT
cache-control: max-age=600
content-encoding: gzip
vary: Accept-Encoding
x-cache: HIT
```

Same on a large project site's HTML: `etag: W/"6a945588-141c7"`,
`cache-control: max-age=600`, `content-encoding: gzip`.

- **600 seconds for HTML *and* for content-hashed JS/CSS.** No `immutable`, no
  `public`, no per-path control.
- Requests are served through Fastly (`via: 1.1 varnish`, `x-fastly-request-id`,
  `x-served-by: cache-…`, `x-cache: HIT/MISS`), and GitHub purges the Fastly
  cache on deploy, so new deploys propagate quickly.
- After the TTL the browser revalidates; the **weak ETag** lets Fastly answer
  `304 Not Modified`, so a repeat visit pays an RTT but not the payload.

**What it forces:**

1. **Do not design around "hash the filename and cache forever".** It is not
   available.
2. **Minimise the *number* of separately-fetched chunks on cold paths**, not just
   their size. Every chunk costs a revalidation RTT after ten minutes. Prefer a
   few coarse, stable chunks (app shell, `three-core`, per-page data) over dozens
   of micro-chunks.
3. Use `<link rel="modulepreload">` and Astro's prefetch to hide revalidation
   latency.
4. A cache-first service worker on hashed URLs is the **only** mechanism for
   long-lived caching on this host — and it adds update-flow complexity plus a
   stale-content risk on a site whose race data changes weekly in season. Treat it
   as an open decision, not a default.
5. If year-long immutable caching genuinely becomes necessary, the route is
   Cloudflare in front of Pages on the custom domain with Cache Rules set there —
   which is one of the spec's open decisions, because it also decides how much
   telemetry can ship.

### B3. Range requests work

```
$ curl -s -D- -o /dev/null -H "Range: bytes=0-99" https://pages.github.com/css/pages.css
HTTP/2 206
accept-ranges: bytes
content-range: bytes 0-99/12226
content-length: 100
```

Identical with `Accept-Encoding: identity`. And:

```
$ curl -sI https://pages.github.com/css/pages.css | grep -i access-control
access-control-allow-origin: *
```

`access-control-allow-origin: *` is sent on **HTML documents too**, not only CSS
assets. Together these unlock browser-side byte-range Parquet reads — the reader
fetches the footer metadata, then only the byte ranges for the columns and row
groups it needs, cross-origin, with no COOP/COEP headers (which cannot be set
here anyway).

### B4. Routing

```
$ curl -s -D- -o /dev/null https://squidfunk.github.io/mkdocs-material/getting-started
HTTP/2 301
location: https://squidfunk.github.io/mkdocs-material/getting-started/

$ curl -s -D- -o /dev/null https://squidfunk.github.io/mkdocs-material/getting-started/
HTTP/2 200

$ curl -s -o /dev/null -w "%{http_code}\n" https://squidfunk.github.io/mkdocs-material/404
200
```

Two distinct behaviours, often conflated:

- **A directory URL missing its trailing slash 301-redirects** to add it. This is
  the only 301 trigger of the two.
- **Extensionless paths resolve to `.html` with a plain 200**, no redirect —
  `/404` serves `404.html` directly.

A third, observed: a repo with a custom domain configured 301-redirects its
`*.github.io` URL to the custom domain.

**What it forces:** set `trailingSlash: 'always'` so every internal `<a href>`
already carries the slash and never triggers the 301 — across hundreds of index
entries, that is hundreds of avoidable round trips. `build.format` is *not* the
differentiator, because extensionless resolution costs nothing. Add a root
`404.html`; Pages serves it for unmatched paths.

## C. Custom domain and HTTPS

Apex domain — A records to all four:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

IPv6 AAAA records (the docs recommend keeping the A records **in addition to**
AAAA):

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

An ALIAS/ANAME record pointing at `<owner>.github.io` is also acceptable for the
apex. A subdomain (`f1.example.com`) takes a single CNAME to `<owner>.github.io`
**without the repository name**.

**The mechanism that breaks silently:** saving a custom domain in repository
settings creates a commit adding a `CNAME` file to the source branch **only when
publishing from a branch**. With a custom GitHub Actions workflow, GitHub creates
no CNAME file — you must author it in the build output yourself, as
`public/CNAME` containing the bare domain. Otherwise the custom domain reverts on
every deploy.

"Enforce HTTPS" becomes available once the Let's Encrypt certificate is issued —
"up to 24 hours", as is DNS propagation. Verify the domain (Settings → Pages →
Verified domains) to block subdomain takeover by other GitHub users. Wildcard DNS
records such as `*.example.com` "create immediate domain takeover risks" and must
not be used.

With a custom domain, set `site` to it and **delete `base`** entirely — which
also eliminates the whole base-path bug class described in
[Site architecture](site-architecture.md).

## D. The binding constraint

The 1 GB size cap and the 100 GB/month bandwidth cap together decide how much
telemetry ships. Projection across ~190 race sessions (2018–2026) using measured
per-race figures:

| Payload | Per race | × 190 |
| --- | ---: | ---: |
| results + laps JSON (columnar, gzipped) | ~15–32 kB | **3–6 MB** |
| circuit centreline + racing line (RDP ε = 0.25 m) | 1–3 kB | < 1 MB (78 circuits) |
| position replay, uniform 2 Hz XY int16 delta | 623 kB | **118 MB** |
| position replay, 5 Hz + 0.5 m quantum | ~849 kB | **161 MB** |
| position replay, uniform 5 Hz XY int16 delta | 1.31 MB | **249 MB** |
| full telemetry Parquet (quantised + delta + zstd) | ~2–3 MB | **380–570 MB** |

HTML alone is material: ~6,000 pages × ~25 kB ≈ **150 MB** before any data or
assets.

**Bandwidth arithmetic, which must stay visible:** 100 GB/month is roughly
**160,000 full replay loads at 623 kB** or **76,000 at 1.31 MB**. Default fidelity
is a bandwidth decision as much as a quality one, and **one viral link is an
outage.**

Placement decision:

- **Site repo:** results, laps, geometry, per-page JSON (≤ 10 MB). Small,
  diffable, versioned, never a moving part.
- **Site repo or a separate `f1-data` Pages site:** the 2 Hz position replay
  (118 MB). Separate if clone weight matters — and it gets its own 1 GB and
  100 GB/month budgets.
- **GitHub Releases:** full per-lap telemetry, one asset per race, fetched on
  demand. Under 2 GiB each, unlimited total, unmetered bandwidth.
- **Never Git LFS** for anything web-served.

A CDN fallback path is designed **before** launch, not after the cap is hit.

## E. Rules derived

1. Track `du -sh dist` in CI and **fail the build above ~700 MB**, well short of
   the 1 GB ceiling.
2. Never emit `.br` or `.gz` siblings.
3. Budget chunk *count*, not only chunk size.
4. `trailingSlash: 'always'`; ship a root `404.html`.
5. Ship raw `.bin` and `.json`; let Pages gzip them.
6. Byte-range Parquet is a legitimate option here, unlike on most static hosts.
7. Telemetry volume is capped by bandwidth before it is capped by size.
8. Commit `public/CNAME` yourself under an Actions workflow.
