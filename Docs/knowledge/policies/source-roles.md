---
type: Policy
title: Source roles and the redistribution boundary
description: The build-time-only versus redistributable boundary, and the pipeline mechanism that keeps NonCommercial and copyleft values out of every published artifact.
tags: [licensing, pipeline, provenance, ci, enforcement, build]
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
  - id: jolpica_diffs
    resource: https://github.com/jolpica/jolpica-f1/blob/main/docs/ergast_differences.md
    title: jolpica-f1 documented differences from Ergast
  - id: openf1_docs
    resource: https://openf1.org/docs
    title: OpenF1 endpoint and field reference
  - id: fastf1_core
    resource: https://docs.fastf1.dev/core.html
    title: FastF1 core object model
  - id: f1db_release
    resource: https://api.github.com/repos/f1db/f1db/releases/latest
    title: F1DB latest release metadata
  - id: multiviewer_circuits
    resource: https://api.multiviewer.app/api/v1/circuits/63/2025
    title: MultiViewer circuits endpoint (undocumented)
status: stable
---

# Source roles and the redistribution boundary

[data-licensing.md](data-licensing.md) establishes that CC BY 4.0, MIT,
LGPL-3.0 and CC BY-NC-SA 4.0 material cannot coexist in one redistributed
bundle. This document is the mechanism that resolves it.

The rule in one sentence: **every source is confined to a declared role, and a
source whose role is build-time-only may influence whether the build succeeds
but may never supply a value that appears in a published artifact.**

The boundary is enforced in the pipeline, not by good intentions. Good
intentions fail on a Sunday night after a triple-header when one number is
missing and jolpica has it.

## 0. What the owner decided, and what it overrides

**2026-09-16.** Three sources were reassigned out of build-time-only roles, and
this document said the opposite until now while the site already shipped their
data. Recording it rather than leaving the contradiction:

> *"I will never commercialise this project so there's no need to worry about
> rights and usage."* — the project owner, on being asked.

On that basis **OpenF1, MultiViewer and TUMFTM supply published values.** The
race replays (SPEC §6.6) are 21 MB of car positions from OpenF1; the circuit
outlines, corner positions and start/finish lines are MultiViewer's; team
colours are OpenF1's. None of this is compatible with the roles they were first
assigned.

What that decision does and does not cover:

- **NonCommercial** (OpenF1, jolpica) is satisfied by the site being
  non-commercial. This is a standing constraint, not a one-off: it forbids ever
  monetising the site without removing that data first.
- **ShareAlike** (OpenF1's SA, and ODbL on the OSM-derived centrelines) is a
  condition on redistribution that non-commercial use does not discharge. The
  site attributes but does not declare an onward licence. Unresolved, and the
  honest statement is that it is unresolved rather than met.
- **MultiViewer publishes no terms at all**, so there is nothing to comply with
  and nothing to rely on. `/credits/` says exactly that rather than implying a
  permission that was never given.
- **jolpica stays `GAP_FILL`.** It is not used at all, so nothing turns on it.

Attribution for all of the above lives at `/credits/`, linked from the home
page. Removing that link would break CC BY 4.0 on F1DB and ODbL on the
OSM-derived geometry — those two are licence conditions, not courtesy.

## 1. Role definitions

| Role | Meaning | Permitted in published artifacts |
| --- | --- | --- |
| `SPINE` | Redistributable under a permissive licence. Values flow straight through to emitted JSON. | **yes** |
| `TOOL` | Code we run. Its licence covers the code, not the data it retrieves. | n/a — carries no values itself |
| `DERIVED_ONLY` | Source of record for a computation whose *aggregate* may ship, but whose raw stream may not. | **aggregates only** |
| `CROSS_CHECK` | Read to validate. May raise an error. May never contribute a value. | **no** |
| `GAP_FILL` | Read to detect a missing value. May raise an error naming what is missing. May never supply it. | **no** |
| `BLOCKED` | No terms, or terms unresolved. Not fetched at all until cleared. | **no** |

## 2. Role assignment

| Source | Licence class | Role | What may leave the pipeline |
| --- | --- | --- | --- |
| F1DB v2026.14.0 | CC BY 4.0 | `SPINE` | Everything. Entities, results, standings, retirement causes, pit stops, fastest laps, 1950–2026 |
| F1DB circuit SVGs | CC BY 4.0 | `SPINE` | The SVG files, re-optimised |
| bacinger/f1-circuits | MIT | `SPINE` | Circuit outline geometry |
| FastF1 3.8.3 | MIT (code) | `TOOL` | — |
| F1 live-timing static archive | F1 rights asserted | `DERIVED_ONLY` | Derived aggregates and downsampled series. **Never** raw `.jsonStream` payloads |
| jolpica-f1 | CC BY-NC-SA 4.0 | `GAP_FILL` | Nothing |
| OpenF1 | CC BY-NC-SA 4.0 | `SPINE` **(reassigned 2026-09-16)** | Circuit geometry, car positions, speed, lap timing, team colours. The race replays are built from it |
| TUMFTM/racetrack-database | LGPL-3.0 | `SPINE` **(reassigned)** | Centreline-derived outlines, with OSM attribution and onward ODbL |
| MultiViewer | no terms published | `SPINE` **(reassigned)** | Circuit geometry, official corner positions, start/finish lines |
| Copernicus GLO-30 | free, attribution | `DERIVED_ONLY` | Distant-terrain meshes only, never the track surface |

## 3. What "cross-check only" actually permits

The distinction that matters is **value versus assertion**.

Permitted:

```python
# OpenF1 is CROSS_CHECK. This reads an OpenF1 value, compares it to the
# spine value, and writes nothing derived from OpenF1 except a pass/fail.
openf1_stops = fetch_openf1_pit(session_key)          # tainted
spine_stops  = f1db.pit_stops(race_id)                # clean

if len(openf1_stops) != len(spine_stops):
    raise CrossCheckFailure(
        f"{race_id}: F1DB has {len(spine_stops)} pit stops, "
        f"OpenF1 has {len(openf1_stops)}"
    )
emit(f"races/{race_id}/pit-stops.json", spine_stops)  # clean payload
```

The exception message names a count that came from OpenF1 — and that is fine,
because the message goes to the build log and the runbook, never to a page. If
the check fails, a human resolves it against F1DB or the live-timing archive
and the spine value changes. OpenF1 caused the correction; it did not supply
it.

Forbidden, and the exact shape the gate exists to catch:

```python
# FORBIDDEN. The NC-SA value is now in a published artifact.
if spine_stops is None:
    spine_stops = openf1_stops            # taint crosses the boundary
emit(f"races/{race_id}/pit-stops.json", spine_stops)
```

The same rule applied to `GAP_FILL`: jolpica may be queried to learn *that*
round 19 of the current season is absent from the latest F1DB release. It may
not be queried to learn *what happened* in round 19. The absence is published
as an honest-absence state (see
[provenance-and-staleness.md](provenance-and-staleness.md)); the result waits
for the next F1DB release, which lands after every race.

## 4. The taint model

Every value that enters the pipeline carries the set of source ids it descends
from. The set is unioned through every transformation. The writer refuses any
payload whose provenance set intersects the non-redistributable set.

```python
# pipeline/provenance.py
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable
import json, pathlib

class Role(str, Enum):
    SPINE        = "spine"
    TOOL         = "tool"
    DERIVED_ONLY = "derived_only"
    CROSS_CHECK  = "cross_check"
    GAP_FILL     = "gap_fill"
    BLOCKED      = "blocked"

# The single registry. Adding a source requires editing this table,
# which is what makes a new source a reviewable diff rather than an import.
ROLES: dict[str, Role] = {
    "f1db":            Role.SPINE,
    "f1db_svg":        Role.SPINE,
    "bacinger":        Role.SPINE,
    "livetiming":      Role.DERIVED_ONLY,
    "copernicus":      Role.DERIVED_ONLY,
    "jolpica":         Role.GAP_FILL,
    "openf1":          Role.CROSS_CHECK,
    "tumftm":          Role.CROSS_CHECK,
    "multiviewer":     Role.BLOCKED,
}

PUBLISHABLE = {Role.SPINE, Role.DERIVED_ONLY}

@dataclass(frozen=True)
class Tainted:
    """A value plus the set of sources it descends from."""
    value: Any
    sources: frozenset[str] = field(default_factory=frozenset)

    def map(self, fn) -> "Tainted":
        return Tainted(fn(self.value), self.sources)

    @staticmethod
    def combine(fn, *args: "Tainted") -> "Tainted":
        return Tainted(
            fn(*(a.value for a in args)),
            frozenset().union(*(a.sources for a in args)),
        )

class RedistributionError(RuntimeError):
    pass

def emit(path: str, payload: Tainted, *, out: pathlib.Path) -> None:
    """The only writer. Nothing else in the pipeline opens a file for write."""
    unknown = payload.sources - ROLES.keys()
    if unknown:
        raise RedistributionError(f"{path}: unregistered source(s) {sorted(unknown)}")

    blocked = {s for s in payload.sources if ROLES[s] not in PUBLISHABLE}
    if blocked:
        raise RedistributionError(
            f"{path}: refuses to publish values derived from "
            f"{sorted(blocked)} (roles: {sorted(ROLES[s].value for s in blocked)})"
        )

    target = out / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({
        "sources": sorted(payload.sources),
        "data": payload.value,
    }, separators=(",", ":")))
```

Four properties of this design earn their keep:

1. **There is exactly one writer.** `emit()` is the only function in the
   pipeline that opens a file for writing. A lint rule forbids `open(..., "w")`
   and `Path.write_*` anywhere under `pipeline/` except `provenance.py`.
2. **Unregistered sources fail closed.** A new source added by an ingest script
   without a `ROLES` entry raises. It cannot default to publishable.
3. **`BLOCKED` fails at fetch, not at write.** The HTTP client refuses any
   request whose source id resolves to `Role.BLOCKED`, so MultiViewer cannot be
   called at all while its terms are unresolved.
4. **The provenance set is written into the artifact.** Every emitted JSON file
   carries its own `sources` array, which is what the `/data/` attribution page
   and the per-page credit line are generated from. Attribution cannot drift
   from what the build actually used.

## 5. The `DERIVED_ONLY` rule for telemetry

`DERIVED_ONLY` is the one role that permits a value through, and it is
therefore the one that needs a written test rather than a type.

| May be published | May not be published |
| --- | --- |
| Per-lap aggregates (lap time, sector times, compound, stint number) | The `TimingData.jsonStream` or `TimingAppData.jsonStream` payload |
| A downsampled position series at 2 Hz for the replay (~623 kB per race), 5 Hz on demand | The `Position.z.jsonStream` payload (7,914,755 B for the 2024 British GP race) |
| A decimated racing line, a per-corner speed at a fixed distance grid | The `CarData.z.jsonStream` payload (7,302,595 B for the same session) |
| Fitted degradation slopes, fuel-corrected pace, clean-air pace | A full-rate speed/throttle/brake/gear/DRS table |
| A mini-sector dominance assignment | A per-sample telemetry export endpoint |

The test is the fan-site guidelines sentence in
[data-licensing.md §5](data-licensing.md): individual pieces used incidentally
within editorial material to genuinely inform, not substantial reproduction.
An aggregate that answers a question on the page passes. A serialisation that
reconstitutes the source stream does not, regardless of format.

Position data is natively ~240 ms (measured median 241.0 ms on the 2024 British
GP), so 5 Hz is close to native and 2 Hz is a genuine reduction rather than a
cosmetic one. That is why 2 Hz is the default: it is simultaneously the
performance budget and the "not substantial reproduction" argument.

## 6. Where the boundary is load-bearing

### 6.1 Retirement causes and laps-down margins

jolpica's own documentation says granular statuses collapse "from the 2025
season". The API behaves earlier than that. Observed status vocabularies:

| Season / round | Statuses returned |
| --- | --- |
| 1990 R10 | `+1 Lap`, `+2 Laps`, `+3 Laps`, `Brakes`, `Collision`, `Engine`, `Finished`, `Gearbox` |
| 2021 R5 | `Driveshaft`, `Finished`, `Wheel nut`, `+1 Lap`, `+3 Laps` |
| 2022 R10 | `Collision`, `Collision damage`, `Finished`, `Fuel pump`, `Gearbox` |
| 2023 R5 | `Finished`, `Lapped` |
| 2023 R10 | `Finished`, `Retired` |
| 2024 R10 | `Finished`, `Lapped` |
| 2025 R5, R10 | `Finished`, `Lapped`, `Retired` |

Two things collapse, not one: retirement *causes* flatten to `Retired`, and
lap-down *margins* flatten from `+N Laps` to a single `Lapped`. The `/status/`
endpoint still lists 136 distinct historical statuses, but they only populate
results through 2022.

**Rule: no retirement-cause and no laps-down figure for 2023 onward may come
from jolpica.** F1DB's `f1db-races-race-results.csv` carries `reasonRetired`,
`gapLaps` and `timeMillis` and is the source of record for all of it. This is a
correctness trap as much as a licensing one — it would silently produce wrong
reliability charts for several recent seasons, and the charts would look
plausible.

The role boundary already forbids it, which is the point: the licensing
mechanism catches a correctness bug for free.

### 6.2 Circuit geometry

MultiViewer is `BLOCKED`, so the circuit-layout registry is built from
`SPINE` sources plus telemetry-derived centrelines. The fallback chain per
layout, in order: bacinger outline → TUMFTM centreline and width
(`[x_m, y_m, w_tr_right_m, w_tr_left_m]`, so total width is
`w_tr_right_m + w_tr_left_m`) → a centreline fitted from FastF1 position
telemetry. TUMFTM is `CROSS_CHECK` pending the LGPL question, so today it
validates a telemetry-derived centreline rather than supplying one.

### 6.3 Entity resolution

Five sources, five identifier schemes. `DriverId` and `TeamId` on FastF1's
`SessionResults` are documented as the Ergast `driverId` and `constructorId`,
which is what joins FastF1 to jolpica and to F1DB. Note that `SessionResults`
has **22** always-present columns and there is no `DriverColor` column — a
common off-by-one in older write-ups.

Circuits are the hard case and no source's default handles them: F1DB has 78
circuits and ~160 *layouts*; OpenF1 uses `circuit_short_name`; bacinger uses
`<iso2>-<year>` slugs; MultiViewer uses an opaque integer `circuit_key`. The
binding artifact is `circuit-layout-registry.json`, hand-verified once per
layout and regression-tested. It is a `SPINE` artifact: it may record that a
layout exists and what its canonical id is, but it may not carry geometry
sourced from a non-publishable role.

## 7. CI gates

The boundary is only real if a test would fail without it.

| Gate | What it asserts | Fails the build |
| --- | --- | --- |
| `test_emit_refuses_tainted` | A payload tagged `openf1`, `jolpica`, `tumftm` or `multiviewer` raises `RedistributionError` | yes |
| `test_emit_refuses_unregistered` | A payload tagged with an unknown source id raises | yes |
| `test_blocked_source_not_fetched` | The HTTP client raises before issuing a request for a `BLOCKED` source | yes |
| `test_single_writer` | No file under `pipeline/` except `provenance.py` opens a file for write | yes |
| `test_emitted_sources_subset` | Every `sources` array in `dist/data/**.json` is a subset of `{f1db, f1db_svg, bacinger, livetiming, copernicus}` | yes |
| `test_no_raw_stream_artifacts` | No emitted file matches `*.jsonStream`, and no emitted position series exceeds the declared sample rate | yes |
| `test_attribution_page_matches` | The `/data/` page's source list equals the union of all emitted `sources` arrays | yes |
| `test_retirement_source` | Every `reasonRetired` value in emitted race results is tagged `f1db` | yes |

The last gate is the cheapest correctness insurance in the project: it makes
§6.1 mechanical rather than remembered.

## 8. Adding a source

A new source is a reviewable diff, deliberately:

1. Add a row to `ROLES` with a justification in the commit message.
2. Add the licence, version and verbatim terms to the matrix in
   [data-licensing.md](data-licensing.md).
3. If the role is `SPINE` or `DERIVED_ONLY`, add the attribution obligation to
   the `/data/` manifest and state what changes were made to the material.
4. If the role is anything else, add the cross-check or gap-fill call site and
   the assertion it raises — an unused `CROSS_CHECK` source is dead weight that
   still carries a rate limit and an uptime dependency.
5. Run the gate suite. A source that cannot be added without loosening a gate
   is a source that cannot be added.

Rate limits are a design input to step 4, not an afterthought: jolpica allows 4
requests per second and 500 per hour unauthenticated, and a single race's laps
endpoint alone reports `total` 921 at the maximum `limit` of 100 — about ten
paged requests for one race. It also **silently clamps** `limit` above 100
rather than erroring, so paging code must read `MRData.total` and never trust
the requested limit. None of that arithmetic argues for putting a `GAP_FILL`
source on the critical path.

## 9. What this does not solve

- It does not make the LGPL-3.0 question go away. TUMFTM stays `CROSS_CHECK`
  until either the maintainers clarify that the copyleft does not attach to the
  CSV data, or width is derived independently.
- It does not protect against a source's licence *changing*. jolpica's terms
  reserve the right to change; OpenF1 moved live data behind a paid tier in
  early 2026. The manifest records the licence as observed at ingest time, with
  its date, so a change is visible as a diff.
- It does not discharge the F1DB provenance question. If F1DB's own chain is
  unsound, every `SPINE` value inherits the problem and the boundary drawn here
  is drawn in the wrong place. That is gating item 1 in
  [data-licensing.md §10](data-licensing.md).
