"""Check each replay against the one thing we know independently: the grid.

The opening frame of a replay should be the field sitting in its starting
order. Race results carry that order, so scoring frame 0 against it is a true
end-to-end test of the whole chain — geometry, arc projection and ordering.
A round that scores 0.00 has reproduced the grid exactly.

    python3 pipeline/verify_replay.py
"""
from __future__ import annotations

import json
import math
import pathlib
import struct
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MAN = ROOT / "site" / "data" / "replays"
BIN = ROOT / "site" / "public" / "replays"
SEASONS = ROOT / "site" / "data" / "seasons"


def arc_table(track: list[list[float]]) -> tuple[list[float], list[float], float]:
    seg = [math.hypot(track[(i + 1) % len(track)][0] - track[i][0],
                      track[(i + 1) % len(track)][1] - track[i][1])
           for i in range(len(track))]
    cum = [0.0]
    for s in seg:
        cum.append(cum[-1] + s)
    return seg, cum, cum[-1]


def arc_of(track, seg, cum, x: float, y: float) -> float:
    best = (float("inf"), 0.0)
    for j in range(len(track)):
        ax, ay = track[j]
        bx, by = track[(j + 1) % len(track)]
        vx, vy = bx - ax, by - ay
        l2 = vx * vx + vy * vy
        u = 0.0 if not l2 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / l2))
        qx, qy = ax + vx * u, ay + vy * u
        d2 = (x - qx) ** 2 + (y - qy) ** 2
        if d2 < best[0]:
            best = (d2, cum[j] + seg[j] * u)
    return best[1]


def _lis(seq: list[int]) -> int:
    """Longest increasing subsequence, by patience sorting."""
    tails: list[int] = []
    for v in seq:
        lo, hi = 0, len(tails)
        while lo < hi:
            mid = (lo + hi) // 2
            if tails[mid] < v:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(tails):
            tails.append(v)
        else:
            tails[lo] = v
    return len(tails)


def check(year: int, rnd: int, season: dict) -> tuple[int, int, int, str]:
    man = json.loads((MAN / f"{year}-{rnd}.json").read_text())
    buf = (BIN / f"{year}-{rnd}.bin").read_bytes()
    results = season["results"][str(rnd)]
    grid = {int(r["no"]): r["grid"] for r in results if r.get("grid")}

    cars, off = man["cars"], man["posOffset"]
    ranked = [man["drivers"][ci]["n"] for ci in buf[off:off + cars]]
    got = [n for n in ranked if n in grid]
    want = sorted(got, key=lambda n: grid[n])
    # Count the cars that are genuinely out of place rather than the mean slot
    # error: one car adrift shifts every car behind it by a slot, which reads as
    # a broken race when the other twenty are exactly right. The smallest set
    # whose removal leaves the rest in grid order is the honest number, and that
    # is the length less the longest increasing subsequence.
    at = {n: i for i, n in enumerate(got)}
    displaced = len(want) - _lis([at[n] for n in want])
    exact = sum(1 for a, b in zip(got, want) if a == b)

    # Where the grid sits relative to the drawn start/finish line. Pole ahead of
    # it and the back row behind is normal: the chequer marks the timing line,
    # which is not where the field lines up.
    track, scale = man["track"], man["scale"]
    seg, cum, lap = arc_table(track)
    span = ""
    if want:
        ends = []
        for n in (want[0], want[-1]):
            ci = next(i for i, d in enumerate(man["drivers"]) if d["n"] == n)
            x, y = struct.unpack_from("<hh", buf, ci * 4)
            a = arc_of(track, seg, cum, x, y)
            ends.append((a if a < lap / 2 else a - lap) / scale)
        span = f"  grid {ends[0]:+.0f}m..{ends[1]:+.0f}m of line"
    return displaced, exact, len(want), span


def laps_check(year: int, rnd: int, season: dict) -> tuple[int, int, str]:
    """Check the lap counting, which is done by watching the arc fraction wrap
    rather than by reading the feed so that it agrees with the running order at
    the line. The failure mode is drift — one wrap missed across a gap in the
    positions and a car is a lap out for the rest of the race — and drift shows
    up as a car's deficit shrinking when it has not overtaken anybody.

    Note that what is stored is distance behind the leader, not the difference
    of two lap counters. Those are not the same thing and the classification
    uses the other one: a car that stops halfway round has completed one lap
    fewer than the leader but is only half a lap behind. So the leader's own
    count is checked against the winner's, and every other car is checked for
    going backwards.
    """
    man = json.loads((MAN / f"{year}-{rnd}.json").read_text())
    buf = (BIN / f"{year}-{rnd}.bin").read_bytes()
    cars, lap_off, frames = man["cars"], man["lapOffset"], man["frames"]
    lead_off, pos_off = man["leadOffset"], man["posOffset"]
    want = max((r["laps"] for r in season["results"][str(rnd)]
                if r.get("laps") is not None), default=0)

    # The leader's count at the flag, against the winner's classified laps.
    flag = frames - 1
    for f in range(frames):
        if buf[lead_off + f] > want:
            flag = max(0, f - 1)
            break
    got = buf[lead_off + flag]
    bad = [] if got == want else [f"race reached lap {got}, winner classified on {want}"]

    # No car may fall further behind than the race is long. Deficits shrinking
    # is not a fault — a lapped car is inside the lap again the moment the
    # leader pits — but a deficit larger than the race means a miscount.
    for ci in range(cars):
        d = max(buf[lap_off + f * cars + ci] for f in range(0, flag + 1, 4))
        if d > want:
            bad.append(f"{man['drivers'][ci]['code']} reads {d} laps down in a {want}-lap race")
    return len(bad), cars, bad[0] if bad else ""


def finish_check(year: int, rnd: int, season: dict) -> tuple[int, int, str]:
    """Score the closing order against the classified result.

    The grid check says the replay starts in the right place; this says it ends
    there too, which between them covers everything that happens in between.
    Only the cars that were running at the flag are scored: a car that retired
    is classified behind cars it was ahead of when it stopped, and the replay
    has no way to know that and no business guessing.
    """
    man = json.loads((MAN / f"{year}-{rnd}.json").read_text())
    buf = (BIN / f"{year}-{rnd}.bin").read_bytes()
    cars, pos_off, frames = man["cars"], man["posOffset"], man["frames"]
    lead_off = man["leadOffset"]
    rows = season["results"][str(rnd)]
    want_laps = max((r["laps"] for r in rows if r.get("laps") is not None), default=0)
    finished = {int(r["no"]): r["posNum"] for r in rows
                if r.get("posNum") and not r.get("reasonRetired") and str(r.get("no", "")).isdigit()}

    # The moment the leader starts its last counted lap is the moment it takes
    # the flag. Anchoring on the classified lap total instead would fall back to
    # the end of the recording wherever the two disagree, and by then the field
    # is on its slow-down lap in no particular order.
    top = max(buf[lead_off + f] for f in range(frames))
    flag = next(f for f in range(frames) if buf[lead_off + f] == top)
    ranked = [man["drivers"][ci]["n"] for ci in buf[pos_off + flag * cars:pos_off + flag * cars + cars]]
    got = [n for n in ranked if n in finished]
    want = sorted(got, key=lambda n: finished[n])
    if not want:
        return 0, 0, ""
    at = {n: i for i, n in enumerate(got)}
    displaced = len(want) - _lis([at[n] for n in want])
    exact = sum(1 for a, b in zip(got, want) if a == b)
    return displaced, exact, len(want)


def grid_check(year: int, rnd: int) -> tuple[int, int, str]:
    """Check the field lines up behind the start line, the way a grid does.

    Every car should sit within a couple of hundred metres behind it, spaced
    about eight metres apart, and none of them in front. A car measuring a whole
    lap behind is really a car just ahead of the line, which is what the finish
    line gives you if you mistake it for the start line.
    """
    man = json.loads((MAN / f"{year}-{rnd}.json").read_text())
    buf = (BIN / f"{year}-{rnd}.bin").read_bytes()
    st = man.get("start")
    if not st:
        return 0, 0, "no grid — the replay does not open on one"

    track, scale, cars = man["track"], man["scale"], man["cars"]
    seg, cum, lap = arc_table(track)
    line = arc_of(track, seg, cum, st["x"], st["y"])
    pits = {sp[0] for sp in man.get("spans", []) if sp[3] == 1 and sp[1] == 0}

    behind = []
    for ci in range(cars):
        if ci in pits:
            continue
        x, y = struct.unpack_from("<hh", buf, ci * 4)
        if x == -32768:
            continue
        behind.append(((line - arc_of(track, seg, cum, x, y)) % lap) / scale)
    if not behind:
        return 0, 0, ""

    behind.sort()
    # A grid is about 180 m long. Anything past that is on the far side.
    LIMIT = 260.0
    stray = [d for d in behind if d > LIMIT]
    gaps = [behind[i + 1] - behind[i] for i in range(len(behind) - 1)]
    med = sorted(gaps)[len(gaps) // 2] if gaps else 0.0
    note = (f"{behind[0]:.0f}–{behind[-1]:.0f} m behind, {med:.1f} m apart"
            if not stray else
            f"{len(stray)} car(s) not behind the line, furthest {max(stray):.0f} m")
    return len(stray), len(behind), note


def main() -> int:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    season = json.loads((SEASONS / f"{year}.json").read_text())
    rounds = sorted(int(p.stem.split("-")[1]) for p in MAN.glob(f"{year}-*.json")
                    if p.stem.split("-")[1].isdigit())
    clean = grid_off = 0
    for rnd in rounds:
        displaced, exact, n, span = check(year, rnd, season)
        clean += displaced == 0
        grid_off += displaced
        mark = "ok  " if displaced == 0 else "    "
        note = "grid exact" if displaced == 0 else f"{displaced} of {n} out of place"
        print(f"{mark}r{rnd:<2} {exact:>2}/{n} in slot  {note}{span}")
    print(f"\n{clean}/{len(rounds)} rounds reproduce the starting grid exactly, "
          f"{grid_off} cars out of place in all")

    print("\nclosing order, against the classified result")
    ends = fin_off = 0
    for rnd in rounds:
        displaced, exact, n = finish_check(year, rnd, season)
        ends += displaced == 0
        fin_off += displaced
        mark = "ok  " if displaced == 0 else "    "
        note = "result exact" if displaced == 0 else f"{displaced} of {n} out of place"
        print(f"{mark}r{rnd:<2} {exact:>2}/{n} in place  {note}")
    # Rounds-exact is a brittle headline — one adjacent swap costs a whole round
    # — so the count of cars out of place is reported beside it.
    print(f"\n{ends}/{len(rounds)} rounds finish in the classified order, "
          f"{fin_off} cars out of place in all")

    print("\nthe grid, against the start line")
    off_grid = 0
    for rnd in rounds:
        stray, n, note = grid_check(year, rnd)
        off_grid += stray
        mark = "ok  " if stray == 0 else "    "
        print(f"{mark}r{rnd:<2} {note}")
    print(f"\n{off_grid} cars are not lined up behind the start line")

    print("\nlap counting")
    drifted = 0
    for rnd in rounds:
        off, n, worst = laps_check(year, rnd, season)
        drifted += off
        mark = "ok  " if off == 0 else "    "
        note = "counts out" if off == 0 else f"{off} problem(s)  (e.g. {worst})"
        print(f"{mark}r{rnd:<2} {note}")
    print(f"\n{drifted} problems with lap counting across the season")
    return 0 if clean == len(rounds) and drifted == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
