---
type: Dataset
title: OpenF1 position coverage in practice
description: What the location feed actually holds across a season of races — placeholder openings, feeds that stop, one race with almost nothing, and the speed channel that reconstructs it to within 17 m.
resource: https://api.openf1.org/v1/location
tags: [openf1, location, car-data, coverage, gaps, reconstruction, replay]
generated:
  by: claude-code/opus-5
  at: '2026-09-16T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-16T00:00:00Z'
sources:
  - id: openf1_location
    resource: https://api.openf1.org/v1/location
    title: OpenF1 location endpoint
  - id: openf1_car_data
    resource: https://api.openf1.org/v1/car_data
    title: OpenF1 car_data endpoint (speed, throttle, brake, gear, rpm)
  - id: measured_2026
    resource: https://api.openf1.org/v1/location?session_key=11299
    title: Per-minute coverage sweep of every 2026 race session, measured 2026-09-15/16
status: stable
---

# OpenF1 position coverage in practice

[OpenF1](openf1.md)'s documentation describes the `location` endpoint without
describing how complete it is. Building fourteen race replays from it
(SPEC §6.6) measured that, and the answer is: **usually excellent, occasionally
absent, and never worth assuming.** Every figure here is measured across the
2026 season rather than quoted.

## What normal looks like

Thirteen of fourteen races have **no gap longer than one second**, at roughly
3–4 Hz per car, for the whole race. Where the feed is healthy it is very
healthy, and nothing in this document applies to it.

## The three ways it fails

**1. A placeholder opening.** Several rounds answer the first seconds — 9 s at
one, 177 s at another — with *every car on one identical coordinate*. The rows
are present and well-formed; only the positions are fictional. Detect it by
distinctness, not by spread: twenty-two cars occupying two or three distinct
points is the signature, and a field genuinely spread around a circuit passes a
spread test just as easily.

**2. A feed that stops.** One round's positions end while its lap data runs on
for another hour. The lap feed is not evidence that the position feed is still
recording.

**3. A race with almost nothing.** Monaco 2026 (`session_key=11299`) holds
**6.5 minutes of a 2h 15m race**, plus a 20-second fragment at the hour mark,
and returns HTTP **404** for every window in between — including a one-minute
window for a single driver, which rules out a size or rate limit. The data is
absent, not awkward to fetch.

A 404 from this endpoint means "nothing matched", so it is indistinguishable
from a transient failure by status alone. A per-minute sweep is the only way to
tell coverage from outage.

## Never interpolate across a hole

The natural implementation — find the samples either side, interpolate between
them — draws a straight line across a fifty-minute gap and produces a replay of
cars crawling across the map for the rest of the race. That is a picture of
nothing that happened, and it looks plausible enough to ship. Guard on the gap
between the enclosing samples, not just on each sample's distance from the
instant wanted.

## The feed backfills

Melbourne 2026 returned placeholder positions for its opening 177 seconds when
first fetched, and real data for the same window a day later. **A cache is not
a final answer.** Before concluding a round's data does not exist, delete its
cached chunks and refetch.

## car_data reconstructs what location lacks

`car_data` carries **speed** at the same rate as `location`, and was complete
for all 22 cars for the whole of Monaco 2026 — the race whose positions are
almost entirely missing. Speed and a centreline are enough to place a car:

1. Integrate speed over time within a lap to get distance travelled.
2. Close each lap against its own known duration from the `laps` endpoint, so
   error cannot accumulate from one lap to the next.
3. Anchor the first lap at its **end**, because it begins on the grid rather
   than at the line.
4. Map distance to a point on the centreline.

**Measured accuracy: a median 17 m error**, 90th percentile 31 m, maximum 52 m,
scored against real positions on a 5,843 m lap at a race that has both. That is
the same order as what the start/finish lines themselves are known to
(SPEC §6.7).

**What it cannot recover** is lateral position. Every car runs down the
centreline, so a reconstructed replay shows a race but not a duel — no
side-by-side, no line through a corner, no pit-lane geometry. A replay built
this way should say so on screen; ours does.

## A speed trace also reads the race

Incidentally, the speed channel alone recovers the shape of a race well enough
to confirm what happened: at Monaco 2026 the field's median speed drops to
safety-car pace at 78 minutes (Stroll's crash), falls to **zero for 33 minutes**
from 94 minutes (the red flag for the broken kerb at Turn 19, called on lap 68),
and returns for the standing restart. Useful as a cross-check that a
reconstruction is faithful before anyone looks at it.

## Clocks between endpoints are not always aligned

At one round the `laps` and `car_data`/`location` timestamps are about
**2.5 seconds apart**, which at 280 km/h is 194 m. It presents as a geometry
error — the lap counter appearing to roll over 194 m from the centreline's own
index 0, where every other circuit is within 28 m — and it is not one. Suspect
clock skew before suspecting the centreline.
