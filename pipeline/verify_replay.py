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


def main() -> int:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2026
    season = json.loads((SEASONS / f"{year}.json").read_text())
    rounds = sorted(int(p.stem.split("-")[1]) for p in MAN.glob(f"{year}-*.json")
                    if p.stem.split("-")[1].isdigit())
    clean = 0
    for rnd in rounds:
        displaced, exact, n, span = check(year, rnd, season)
        clean += displaced == 0
        mark = "ok  " if displaced == 0 else "    "
        note = "grid exact" if displaced == 0 else f"{displaced} of {n} out of place"
        print(f"{mark}r{rnd:<2} {exact:>2}/{n} in slot  {note}{span}")
    print(f"\n{clean}/{len(rounds)} rounds reproduce the starting grid exactly")
    return 0 if clean == len(rounds) else 1


if __name__ == "__main__":
    raise SystemExit(main())
