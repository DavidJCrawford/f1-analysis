---
type: Reference
title: Telemetry encoding
description: How one race of 20-car position data is quantised, delta-encoded and laid out planar to reach 623 kB at 2 Hz, with every figure marked measured or synthetic.
resource: https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
tags: [encoding, quantisation, delta-encoding, parquet, hyparquet, rdp, telemetry, payload]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: position_stream_2024_britain
    resource: https://livetiming.formula1.com/static/2024/2024-07-07_British_Grand_Prix/2024-07-07_Race/Position.z.jsonStream
    title: 2024 British GP position stream (benchmark input)
  - id: pyarrow_write_table
    resource: https://arrow.apache.org/docs/python/generated/pyarrow.parquet.write_table.html
    title: pyarrow.parquet.write_table reference
  - id: parquet_encodings
    resource: https://parquet.apache.org/docs/file-format/data-pages/encodings/
    title: Apache Parquet encodings
  - id: hyparquet
    resource: https://github.com/hyparam/hyparquet
    title: hyparquet repository and README
  - id: hyparquet_compressors
    resource: https://registry.npmjs.org/hyparquet-compressors/latest
    title: hyparquet-compressors npm metadata
  - id: decompressionstream
    resource: https://developer.mozilla.org/en-US/docs/Web/API/DecompressionStream
    title: MDN DecompressionStream
  - id: fastf1_api
    resource: https://docs.fastf1.dev/api.html
    title: FastF1 API reference (position data units and rates)
status: stable
---

# Telemetry encoding

Every figure in this document is labelled **measured** or **synthetic**.
The measured ones come from the complete 2024 British Grand Prix position stream:
677,980 real samples, 33,899 frames, 21 car numbers, a 146.5-minute window,
encoded with pyarrow 25.0.1 and stdlib zlib at level 9. The synthetic ones come
from a race-shaped generator and are called out individually — one of them does
not survive arithmetic and is flagged as such.

## 1. The four transforms

The wire format is the composition of four independent decisions, each with its
own measurable saving:

| Transform | What it does | Why it works |
| --- | --- | --- |
| **Quantisation** | float32 → int16 at a fixed metre quantum | Float mantissas are high-entropy and nearly incompressible |
| **Delta encoding** | store `x[i] − x[i−1]` per channel | Consecutive positions differ by a small, low-entropy number |
| **Planar layout** | all X deltas for car 1, then all Y, then car 2… | Puts like next to like, so the compressor sees runs |
| **Uniform time grid** | resample every car onto a shared clock | Deletes the timestamp column entirely |

The fourth is the largest single win and the least obvious, so take it first.

## 2. Why the time column has to go

**Measured.** Per-column compressed sizes inside the 1.93 MB
int16 + `DELTA_BINARY_PACKED` + zstd-9 Parquet file:

| Column | Compressed bytes | Share |
| --- | ---: | ---: |
| `driver` | 2,913 | 0.1% |
| **`t_ms`** | **772,657** | **40%** |
| `x` | 483,059 | 25% |
| `y` | 496,416 | 26% |
| `z` | 171,433 | 9% |

Each car carries its own irregular timestamps, so the time column is 40% of the
file and compresses badly by construction. Resampling all cars onto one grid
removes it outright, and the grid definition becomes three numbers in a manifest
(`t0Ms`, `stepMs`, `samplesPerCar`).

## 3. Encoding benchmark

**Measured**, all 677,980 real samples, sorted by `(driver, t_ms)` before
encoding — the sort order is load-bearing for delta encoding. KB/car divides by
20 (see §8 on the 21st car).

| Encoding | Size | B/row | KB/car |
| --- | ---: | ---: | ---: |
| naive JSON `[[x,y,z],…]` | 11.07 MB | 16.32 | 553 |
| naive JSON + gzip-9 | 2.50 MB | 3.69 | 125 |
| Parquet float32, snappy (pyarrow defaults) | 3.42 MB | 5.05 | 171 |
| Parquet float32 + zstd-9, no dictionary | 4.68 MB | 6.90 | 234 |
| Parquet float32 + zstd-9 + `BYTE_STREAM_SPLIT` | 3.29 MB | 4.86 | 165 |
| Parquet int16 (native 1/10 m) + zstd-9, dict on | 3.25 MB | 4.79 | 162 |
| **Parquet int16 + `DELTA_BINARY_PACKED` + zstd-9** | **1.93 MB** | 2.84 | 96 |
| Arrow IPC int16, zstd-9 buffers | 2.90 MB | 4.28 | 145 |
| Arrow IPC int16, lz4 buffers | 4.72 MB | 6.97 | 236 |
| raw `.bin` int16 delta planar XY | 2.71 MB | 4.00 | 136 |
| **raw `.bin` int16 delta planar XY + gzip-9** | **1.13 MB** | 1.67 | 56 |
| raw `.bin` int16 delta planar XYZ + gzip-9 | 1.31 MB | 1.94 | 66 |

Three readings. Parquet's compressed columnar layout beats a hand-rolled binary
only until you also drop the time column, at which point the hand-rolled binary
wins. Arrow IPC is attractive for zero-copy but is materially less compact on the
wire (2.90 MB vs 1.93 MB for identical data), and its buffer-compression support
is the weak spot. And `BYTE_STREAM_SPLIT` is the right fallback *if* float32 must
be kept — 3.29 MB vs 3.42 MB snappy and 4.68 MB plain zstd — but quantised ints
with delta encoding beat it comfortably.

### Delta safety

**Measured.** For one driver at the native ~4.55 Hz effective rate, in 1/10 m
units: `|Δx|` p99 = **285**, max = **1,503**. Against int16's ±32,767 that is a
20× margin, so int16 deltas never overflow. Assert it at build time anyway — the
assertion is cheap and the failure mode is silent corruption.

## 4. The uniform grid, and what it costs in fidelity

**Measured.** Method: for each car, `np.interp` the raw `(t, X, Y, Z)` onto
`np.arange(0, T, 1000/hz)` ms, quantise, delta-encode per channel as int16,
concatenate planar, gzip-9. Error is measured by interpolating the grid back onto
the original sample timestamps and taking Euclidean distance in metres.

| Grid | pts/car | raw bytes | gzip bytes | mean err | **p99 err** | max err |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| XY @ 10 Hz, 0.1 m | 87,906 | 7,384,104 | 1,901,979 | 0.190 m | 1.61 m | 26.9 m |
| XY @ 5 Hz, 0.1 m | 43,953 | 3,692,052 | **1,306,052** | 0.391 m | 3.22 m | 76.9 m |
| XY @ 4.55 Hz, 0.1 m | 39,998 | 3,359,832 | 1,220,284 | 0.433 m | 3.53 m | 85.9 m |
| XY @ 2 Hz, 0.1 m | 17,582 | 1,476,888 | **623,037** | 0.921 m | 7.08 m | 124.7 m |
| XY @ 1 Hz, 0.1 m | 8,791 | 738,444 | 337,666 | 1.621 m | 9.38 m | 267 m |
| XY @ 0.5 Hz, 0.1 m | 4,396 | 369,264 | 182,604 | 3.627 m | 17.5 m | 199 m |
| XYZ @ 5 Hz, 0.1 m | 43,953 | 5,538,078 | 1,494,761 | — | — | — |
| XYZ @ 2 Hz, 0.1 m | 17,582 | 2,215,332 | 744,162 | — | — | — |

Arithmetic check on the grid: the real position stream spans 8,791 s, which gives
87,905 points at 10 Hz (the table's 87,906 is a rounding difference), and
87,906 × 21 × 2 channels × 2 bytes = 7,384,104 B — exactly the raw figure.

**Use p99 as the acceptance metric, never max.** The large max values (77–267 m)
are pit-lane and garage gaps where a car stops transmitting and linear
interpolation bridges a long hole. Carry a per-sample `onTrack` bit and mask
those; do not chase them with a finer grid, which costs bytes everywhere to fix a
handful of samples.

### The free lunch

**Measured.** At 5 Hz the *temporal* error (p99 3.22 m) dominates any sane spatial
quantum, so coarsening the quantum costs nothing measurable:

| Quantum at 5 Hz XY | gzip bytes | Error vs 0.1 m |
| --- | ---: | --- |
| 0.1 m | 1,306,052 | baseline |
| 0.5 m | **848,948** | identical |
| 1.0 m | **658,463** | identical |

A 35–50% saving for nothing. **0.5 m is the project quantum.**

### The shipped decision

The spec's choice: **2 Hz for the default replay (623 kB), 5 Hz fetched on demand**
when the reader opens corner-level analysis. Native position sampling is ~240 ms
(measured median 241.0 ms; the "220 ms" in FastF1's docs is nominal, and the mean
of 259.3 ms is inflated by gaps), so 5 Hz is close to native and 2 Hz is a real
reduction rather than a token one. At 2 Hz a full race page's initial data load is
**≈ 660 kB** (`replay.bin` 623 kB + `race.json` ~20 kB + `laps.json` ~15 kB +
`replay.json` ~2 kB); at 5 Hz it is **≈ 1.4 MB**.

Bandwidth is the other half of that decision. GitHub Pages' 100 GB/month soft cap
is roughly **160,000 full replay loads at 623 kB** or **76,000 at 1.31 MB** — see
[GitHub Pages constraints](github-pages-constraints.md).

## 5. Why not float32

**Synthetic, with one caveat.** On a 518,200-row race-shaped generated dataset,
interleaved Float32 XYZ measured 6,220,000 B raw and 5,850,000 B after zlib-9 —
only about **6% saved**, because float mantissas are high-entropy. That
directional conclusion is sound and is corroborated by the real-data table above
(Parquet float32 + zstd-9 at 4.68 MB against int16 + delta at 1.93 MB).

**The array-of-structs versus struct-of-arrays figures from that same synthetic
run do not survive arithmetic and must be re-measured before they are quoted
anywhere.** 518,200 rows × 3 channels × 2 bytes is 3,109,200 B of int16 input, and
gzip cannot emit 4.62 MB or 4.00 MB from a 3.11 MB input; the run also assigns the
same "int16 absolute planar" configuration two different sizes. Treat the AoS/SoA
ratio as **unverified for binary payloads**.

There *is* a clean measurement of the same idea on real-shaped JSON, in
[Data pipeline](data-pipeline.md): a 1,040-row × 25-column laps table is
453,917 B / 31,840 B gzipped as array-of-objects and 142,265 B / **15,276 B**
gzipped columnar — 3.2× smaller raw, 2.1× gzipped. Use that as the evidence for
structure-of-arrays; do not use the synthetic binary numbers.

## 6. The wire shape

```
replay.bin      per-car planar int16 deltas, no header, no time column
replay.json     the manifest that makes the binary self-describing
```

Manifest fields: `{ quantum, originX, originY, zConst, t0Ms, stepMs,
samplesPerCar, drivers[], byteOffsets{}, sha256 }`. **Nothing about the layout is
implicit in the binary.**

Reconstruction on the client:

```js
const buf = await (await fetch(base + 'data/races/2024-britain/replay.bin')).arrayBuffer();
const d = new Int16Array(buf);
const n = manifest.samplesPerCar, cars = manifest.drivers.length;
const out = new Float32Array(cars * n * 3);
for (let c = 0; c < cars; c++) {
  let x = 0, y = 0;
  const bx = c * 2 * n, by = bx + n;
  for (let i = 0; i < n; i++) {
    x += d[bx + i]; y += d[by + i];
    const o = (c * n + i) * 3;
    out[o]     = x * manifest.quantum;   // metres
    out[o + 1] = manifest.zConst;
    out[o + 2] = y * manifest.quantum;
  }
}
```

Two build-time assertions that this snippet depends on: every `byteOffsets` value
must be **even** (an `Int16Array` view throws on a misaligned byte offset), and
`buf.byteLength` must equal `cars * channels * samples * 2`.

## 7. Transport

**Ship the raw, uncompressed `.bin`.** GitHub Pages gzips it transparently on the
wire — verified against a Pages origin with `Accept-Encoding: gzip, deflate, br,
zstd`, where `application/octet-stream`, `model/gltf-binary`, `application/wasm`,
`application/json` and `application/javascript` all came back
`content-encoding: gzip` and nothing ever came back brotli or zstd. So the
1.13 MB / 623 kB figures are what a browser actually transfers, for free, without
committing a `.gz` sibling.

Two corollaries. Pre-compressed `.br` siblings are dead weight that counts against
the 1 GB cap and are never served. And if brotli or zstd ratios are genuinely
needed, the only route is an opaque blob decompressed in JS —
`DecompressionStream` is Baseline since May 2023 but the WHATWG Compression Spec
standardises only `"gzip"`, `"deflate"` and `"deflate-raw"`, so brotli needs a
wasm decoder. Serving a `.bin.gz` as `application/octet-stream` and calling
`DecompressionStream('gzip')` on it merely double-compresses. Not worth it:
prefer a more compact wire format.

## 8. Sample-count arithmetic

**Measured.** The 2024 British GP position stream contains exactly 677,980
car-samples across 21 distinct car numbers. Nineteen cars have 33,899 samples,
car #3 has 33,896, and **car #21 has 3 samples — a spurious entry.** Divide
per-car budgets by **20**, not 21, or every KB/car figure understates by 5%.

Related unit trap: FastF1 position `X`/`Y`/`Z` are in **1/10 metre from 2020
onward**. Pre-2020 sessions are not, and the cutoff is easy to miss.

Silverstone's extents are X −2,315..7,791 and Y −4,117..13,116 in 1/10 m — a
1,011 m × 1,723 m box, comfortably inside int16's ±3,276.7 m at that quantum.
A circuit exceeding ~3.2 km on one axis would force a per-circuit origin
translation or int32; the extents of Spa, Baku, Jeddah and Las Vegas are
**unmeasured**.

## 9. Geometry is a different problem

An animated replay needs O(1) indexing by time, which a variable-rate polyline
destroys. A static ribbon or racing line needs the minimum number of points for a
given geometric error. Two problems, two tools.

**Measured**, on a 25,910-point single-car race trace (race-realistic curvature
and lateral noise); `err` is the deviation of the original points from the
simplified polyline:

| Method | Points | Max err | RMS err |
| --- | ---: | ---: | ---: |
| RDP ε = 0.25 m | 14,562 | 0.25 m | 0.136 m |
| RDP ε = 0.50 m | 10,520 | 0.50 m | 0.252 m |
| RDP ε = 1.00 m | 7,435 | 1.00 m | 0.480 m |
| RDP ε = 2.00 m | 5,283 | 2.00 m | 0.895 m |
| RDP ε = 5.00 m | 3,201 | 5.00 m | 2.201 m |
| uniform 1/2 | 12,956 | 2.77 m | 0.222 m |
| uniform 1/3 | 8,638 | 3.97 m | 0.406 m |
| uniform 1/5 | 5,183 | 8.02 m | 0.980 m |
| uniform 1/10 | 2,592 | 26.60 m | 3.632 m |
| uniform 1/20 | 1,297 | 99.32 m | 15.03 m |

**Head to head at an identical budget:** RDP tuned to 5,182 points (ε = 2.077 m)
gives max 2.08 m / RMS 0.929 m against uniform-1/5's max 8.02 m / RMS 0.980 m.
RMS is nearly identical; the entire difference is worst case — **3.9× worse** — and
worst case is always the apex of a slow corner, which is exactly where a circuit
diagram is read. RDP's error bound is a hard guarantee (`max err == ε` by
construction), which makes it specifiable in prose: "circuit centreline simplified
to ε = 0.25 m".

**Measured.** RDP applied to a 4,001-point centreline of a 5,874 m lap:

| ε | Points | Retained | int16 XY bytes |
| --- | ---: | ---: | ---: |
| 0.05 m | 712 | 17.8% | 2,848 |
| 0.25 m | 322 | 8.0% | **1,288** |
| 0.50 m | 222 | 5.5% | 888 |
| 1.00 m | 160 | 4.0% | 640 |
| 5.00 m | 69 | 1.7% | 276 |

A per-circuit 3D ribbon spine therefore costs **1–3 kB**, and all 78 circuits fit
in well under 1 MB. That is the argument for generating track geometry
procedurally from a coordinate array in the page's JSON rather than shipping a GLB
per circuit — see [three.js track rendering](threejs-track-rendering.md).

**Recorded decision:** ε = 0.25 m for circuit centrelines and racing lines;
uniform 2 Hz / 0.5 m for the default race replay, 5 Hz on demand; and
`RelativeDistance` (0.0–1.0) rather than `Distance` as the cross-driver,
cross-season comparison key.

## 10. Reading Parquet in the browser

GitHub Pages supports HTTP `Range` requests — verified: `Range: bytes=0-99`
returns `HTTP/2 206` with `content-range: bytes 0-99/12226` and
`accept-ranges: bytes`, identically with `Accept-Encoding: identity`, and every
asset carries `access-control-allow-origin: *`. So a browser can read the Parquet
footer and then fetch only the byte ranges for the columns and row groups it
needs. That is what makes on-demand per-driver telemetry viable without shipping
the whole file.

**hyparquet 1.30.1** is the reader. Measured size: **18,826 B (18.4 KiB)
minified+gzipped**, 62,180 B minified, dependency count **0**. (Lower figures
circulate; the package has since absorbed geoparquet, variant, bloom-filter, wkb
and xxhash modules.)

```js
import { parquetReadObjects, parquetMetadataAsync, asyncBufferFromUrl } from 'hyparquet'
import { compressors } from 'hyparquet-compressors'

const file = await asyncBufferFromUrl({ url: base + 'data/races/2024-britain/telemetry/VER.parquet' })
const meta = await parquetMetadataAsync(file)          // schema + row counts, no full download
const rows = await parquetReadObjects({
  file, compressors,
  columns: ['t_ms', 'Speed', 'nGear'],
  rowStart: 0, rowEnd: 100000,
})
```

`asyncBufferFromUrl({ url, byteLength, requestInit, fetch })`. The lower-level
`parquetRead` exposes `onComplete` / `onChunk` / `onPage` callbacks and avoids the
row-transposition cost entirely — use it to get columnar typed arrays straight
into a `BufferAttribute` or a worker. Other options: `utf8`, `geoparquet`,
`includeRowIndex`, `rowFormat: 'object'`.

Encoding support is complete for this pipeline: `PLAIN`, `PLAIN_DICTIONARY`,
`RLE_DICTIONARY`, `RLE`, `BIT_PACKED`, **`DELTA_BINARY_PACKED`**,
`DELTA_BYTE_ARRAY`, `DELTA_LENGTH_BYTE_ARRAY`, **`BYTE_STREAM_SPLIT`**.

**The zero-dependency property has a condition.** hyparquet's *built-in*
compression support is uncompressed and snappy only. The zstd-9 Parquet this
pipeline writes requires `hyparquet-compressors@1.1.1`, which itself declares
dependencies `fzstd@0.1.1` and `hysnappy@1.0.0`. If minimal bundle size is
load-bearing, either write **snappy** Parquet (native to hyparquet, with GitHub
Pages' transparent gzip as the outer layer) or accept the extra package and its
two transitive dependencies.

Alternatives, with their real costs:

| Reader | Size | Verdict |
| --- | --- | --- |
| hyparquet 1.30.1 | 18.4 KiB min+gzip, 0 deps | **Default** |
| apache-arrow JS 21.2.0 | much larger; zero-copy `vector.toArray()` typed arrays | Attractive for three.js, but IPC is less compact on the wire |
| parquet-wasm 0.7.2 | ~1.2 MB brotli-compressed wasm | Faster, far heavier |
| `@duckdb/duckdb-wasm` | **35–41 MB** wasm binaries (mvp 40,621,595 B; eh 35,659,694 B; coi 35,272,630 B) | Disqualified. The commonly-quoted 6–18 MB is wrong |

The single-threaded duckdb bundle does work without COOP/COEP headers — which
matters because those headers cannot be set on Pages — but 35–41 MB is not a
page dependency on a site whose whole JS budget is 40 kB.

**Rule of thumb:** precomputed columnar JSON for the 95% case; raw `.bin` plus
manifest for the replay hot path; hyparquet range reads only for on-demand
per-driver telemetry columns; never duckdb-wasm.

## Open items

- The JS decode cost of the int16-delta reconstruction is **unmeasured**. At 5 Hz
  that is ~880k delta accumulations plus a `Float32Array` fill on the main
  thread; if it exceeds ~50 ms on a mid-range phone it must move to a worker,
  which changes the 3D page's loading choreography. See
  [Performance budgets](performance-budgets.md) on the 50 ms long-task threshold.
- Whether GitHub Pages' Fastly edge honours `Range` against *large* files (tens
  of MB) as reliably as against the 12 kB file tested is **unverified**, as is
  whether range reads bill against the bandwidth cap by requested bytes or full
  object bytes.
- Whether `DecompressionStream('brotli')` has shipped outside Chromium is
  **unresolved**; MDN does not list per-format support and sources conflict. It
  affects only the fallback plan for very large text payloads.
- The AoS-versus-SoA ratio for **binary** payloads needs re-measuring on real
  data before it is cited (§5).
