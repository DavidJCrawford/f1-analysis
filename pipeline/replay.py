"""Build race replays from timing-feed position data.

Emits, per completed race, a binary track of every car's position on a uniform
time grid plus a manifest describing it. Running order comes from lap timing
rather than from projecting coordinates onto the centreline: a car's progress is
its completed laps plus its fraction through the current one, which is both far
cheaper and closer to how the order is actually defined.

Raw API responses are cached under .cache/openf1 so re-runs cost nothing.
"""
from __future__ import annotations
import json, math, struct, sys, time, urllib.request, urllib.error
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "openf1"
OUT_BIN = ROOT / "site" / "public" / "replays"
OUT_MAN = ROOT / "site" / "data" / "replays"
STEP = 0.5                      # s between frames
CHUNK = 12 * 60                 # s per location request
ABSENT = -32768


def api(path: str, key: str) -> list:
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{key}.json"
    if f.exists():
        return json.loads(f.read_text())
    url = f"https://api.openf1.org/v1/{path}"
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "f1-analysis/0.1 (personal project)"})
            data = json.loads(urllib.request.urlopen(req, timeout=120).read())
            f.write_text(json.dumps(data))
            time.sleep(0.15)
            return data
        except Exception as e:
            if attempt == 4:
                print(f"    give up {key}: {e}")
                return []
            time.sleep(2 + attempt * 3)
    return []


def iso(t: dt.datetime) -> str:
    return t.strftime("%Y-%m-%dT%H:%M:%S")


def build(year: int, rnd: int, session_key: int, circuit_id: str) -> dict | None:
    drivers = api(f"drivers?session_key={session_key}", f"drv_{session_key}")
    raw_laps = api(f"laps?session_key={session_key}", f"lap_{session_key}")
    laps = [l for l in raw_laps if l.get("date_start") and l.get("lap_duration")]
    if not drivers or not laps:
        print("    no driver or lap data"); return None

    nums = sorted({d["driver_number"] for d in drivers})
    # Zero the replay on the race start, not on the first sample of any kind.
    # Taking the earliest lap start of any driver lets a stray outlap drag the
    # opening frame back into the formation lap, so the field is strung round
    # the circuit instead of sitting on the grid. The field leaves the grid
    # together, so the median of the lap-1 starts is the start; fall back to the
    # earliest lap of any sort if the feed has no lap 1.
    # Read the opening lap from the unfiltered feed: at some rounds the lap-1
    # rows carry a start but no duration, and taking them from the filtered list
    # loses the start of the race entirely.
    firsts = sorted(dt.datetime.fromisoformat(l["date_start"])
                    for l in raw_laps
                    if l.get("lap_number") == 1 and l.get("date_start"))
    if firsts:
        t0 = firsts[len(firsts) // 2]
    else:
        t0 = min(dt.datetime.fromisoformat(l["date_start"]) for l in laps)
    t1 = max(dt.datetime.fromisoformat(l["date_start"])
             + dt.timedelta(seconds=l["lap_duration"]) for l in laps)
    frames = int((t1 - t0).total_seconds() / STEP) + 1
    print(f"    {len(nums)} cars, {frames} frames, {(t1-t0).total_seconds()/60:.0f} min")

    # Position samples, chunked so no single request is enormous.
    samples: dict[int, list[tuple[float, float, float]]] = {n: [] for n in nums}
    span = (t1 - t0).total_seconds()
    for c in range(int(span // CHUNK) + 1):
        a = t0 + dt.timedelta(seconds=c * CHUNK)
        b = min(t1, a + dt.timedelta(seconds=CHUNK))
        rows = api(f"location?session_key={session_key}&date>={iso(a)}&date<={iso(b)}",
                   f"loc_{session_key}_{c}")
        for r in rows:
            if r.get("x") is None:
                continue
            n = r["driver_number"]
            if n in samples:
                samples[n].append(((dt.datetime.fromisoformat(r["date"]) - t0).total_seconds(),
                                   r["x"] / 10.0, r["y"] / 10.0))
    for n in samples:
        samples[n].sort()

    # The feed emits occasional rows far outside the circuit — a garage or pit
    # coordinate, or plain noise. Left in they stretch the bounding box, which
    # both squashes the real track within the int16 grid and parks a car in the
    # corner of the map on the opening frame. Trim to a robust box: every part
    # of a circuit is driven by every car on every lap, so a genuine corner is
    # nowhere near the half-percentile.
    flat = [(pt[1], pt[2]) for n in nums for pt in samples[n]]
    if len(flat) > 400:
        def band(vals: list[float]) -> tuple[float, float]:
            vals.sort()
            k = len(vals) // 200
            lo, hi = vals[k], vals[-k - 1]
            pad = (hi - lo) * 0.25 + 1.0
            return lo - pad, hi + pad
        x0, x1 = band([p[0] for p in flat])
        y0, y1 = band([p[1] for p in flat])
        dropped = 0
        for n in nums:
            keep = [pt for pt in samples[n] if x0 <= pt[1] <= x1 and y0 <= pt[2] <= y1]
            dropped += len(samples[n]) - len(keep)
            samples[n] = keep
        if dropped:
            print(f"    dropped {dropped} stray samples outside the circuit")

    got = sum(1 for n in nums if len(samples[n]) > 100)
    print(f"    position samples for {got}/{len(nums)} cars")
    if got < 2:
        return None

    # Uniform grid, linearly interpolated between samples.
    xs = [[ABSENT] * len(nums) for _ in range(frames)]
    ys = [[ABSENT] * len(nums) for _ in range(frames)]
    allx, ally = [], []
    for ci, n in enumerate(nums):
        s = samples[n]
        if len(s) < 2:
            continue
        j = 0
        for f in range(frames):
            t = f * STEP
            while j + 1 < len(s) and s[j + 1][0] < t:
                j += 1
            if j + 1 >= len(s) or s[j][0] > t + 5 or s[j + 1][0] < t - 5:
                continue
            t_a, xa, ya = s[j]; t_b, xb, yb = s[j + 1]
            u = 0.0 if t_b == t_a else (t - t_a) / (t_b - t_a)
            u = max(0.0, min(1.0, u))
            xs[f][ci] = xa + (xb - xa) * u
            ys[f][ci] = ya + (yb - ya) * u
            allx.append(xs[f][ci]); ally.append(ys[f][ci])
    if not allx:
        return None

    # A few rounds carry no real positions at the moment the race starts: the
    # feed puts every car on one placeholder point for a few seconds. That is
    # not a grid, and drawing it stacks the whole field on a single dot, so open
    # the replay at the first frame where the cars are actually apart.
    # The giveaway is not how far apart the field looks but how few places it
    # occupies: a placeholder frame puts twenty-two cars on two or three points.
    skip = 0
    for f in range(min(frames, int(240 / STEP))):
        here = [(round(xs[f][ci]), round(ys[f][ci]))
                for ci in range(len(nums)) if xs[f][ci] != ABSENT]
        if len(here) >= 8 and len(set(here)) >= max(8, int(len(here) * 0.8)):
            skip = f
            break
    if skip:
        xs, ys = xs[skip:], ys[skip:]
        frames -= skip
        allx = [v for row in xs for v in row if v != ABSENT]
        ally = [v for row in ys for v in row if v != ABSENT]
        if not allx:
            return None
        print(f"    no positions for the first {skip * STEP:.0f}s; opening after them")

    cx, cy = (min(allx) + max(allx)) / 2, (min(ally) + max(ally)) / 2
    extent = max(max(allx) - min(allx), max(ally) - min(ally)) or 1.0
    scale = 30000.0 / extent           # fit into int16 with headroom

    # The track, in the same frame as the cars. Circuits sourced from the timing
    # feed share its coordinate system, so the centreline transforms with the
    # identical offset and scale. Where it does not, no track is drawn and the
    # cars carry the shape on their own.
    track = []
    try:
        from geo import load_centrelines
        cl = load_centrelines().get(circuit_id)
        if cl and cl["source"].startswith("F1 timing"):
            track = [[int(round((x - cx) * scale)), int(round((y - cy) * scale))]
                     for x, y in cl["pts"]]
    except Exception as e:
        print(f"    track unavailable: {e}")

    # Running order comes from where a car actually is on the track, not from
    # how far through its lap time it is. Time-fraction ordering makes a car on
    # a quicker lap appear further along than one physically ahead of it, so the
    # order churned every few frames — and the camera, which follows the leader,
    # jumped with it.
    order_track = track or []
    if order_track:
        tseg = [math.hypot(order_track[(i + 1) % len(order_track)][0] - order_track[i][0],
                           order_track[(i + 1) % len(order_track)][1] - order_track[i][1])
                for i in range(len(order_track))]
        tcum = [0.0]
        for s in tseg:
            tcum.append(tcum[-1] + s)
        TLAP = tcum[-1] or 1.0
        COARSE = max(1, len(order_track) // 120)

        def arc_of(x, y):
            """Fraction of a lap at the nearest centreline point, and how far off
            it the car is. The second number separates the pit lane from the
            track: the racing line never strays far from the centreline, so a
            large offset means the car is not racing."""
            bi, bd = 0, float("inf")
            for i in range(0, len(order_track), COARSE):
                dx = order_track[i][0] - x; dy = order_track[i][1] - y
                d = dx * dx + dy * dy
                if d < bd: bd, bi = d, i
            best = (float("inf"), 0.0)
            for i in range(bi - COARSE, bi + COARSE + 1):
                j = i % len(order_track)
                ax, ay = order_track[j]
                bx, by = order_track[(j + 1) % len(order_track)]
                vx, vy = bx - ax, by - ay
                l2 = vx * vx + vy * vy
                u = 0.0 if not l2 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / l2))
                qx, qy = ax + vx * u, ay + vy * u
                d2 = (x - qx) ** 2 + (y - qy) ** 2
                if d2 < best[0]:
                    best = (d2, (tcum[j] + tseg[j] * u) / TLAP)
            return best[1], math.sqrt(best[0]) / scale

    # Progress: completed laps plus the fraction through the current one.
    by_driver: dict[int, list] = {n: [] for n in nums}
    for l in laps:
        if l["driver_number"] in by_driver:
            by_driver[l["driver_number"]].append(
                ((dt.datetime.fromisoformat(l["date_start"]) - t0).total_seconds(),
                 l["lap_duration"], l["lap_number"]))
    for n in by_driver:
        by_driver[n].sort()

    order = [[0] * len(nums) for _ in range(frames)]
    lapno = [[0] * len(nums) for _ in range(frames)]
    # Laps are counted from the geometry itself, not read off the feed: the two
    # disagree for a frame or two either side of the line, and a disagreement
    # there is a whole-lap error in the running order. Seeded from the feed once,
    # then advanced only when a car's arc fraction wraps.
    prev_frac: list[float | None] = [None] * len(nums)
    glap = [0] * len(nums)
    # A car starting from the pit lane sits beside the track, and projected onto
    # the centreline that reads as a place well up the order — at Silverstone
    # nearly four hundred metres ahead of pole. The distance test is only safe on
    # the opening frame, where the field is stationary on the grid and every car
    # that is racing sits within a few centimetres of the line; once the race is
    # running, cars stray far enough that no fixed distance tells the two apart.
    # So the flag is only ever raised on that first frame, and only ever lowered
    # afterwards — the moment the car reaches the track it is racing, and from
    # then on it is ordered like everyone else.
    PIT_M = 6.0
    in_pit = [False] * len(nums)
    for f in range(frames):
        tsec = (f + skip) * STEP       # laps are timed from t0, not from frame 0
        prog = []
        pit = [False] * len(nums)
        for ci, n in enumerate(nums):
            ln = 0
            for st, du, num in by_driver[n]:
                if st <= tsec:
                    ln = num
                else:
                    break
            lapno[f][ci] = min(255, ln)

            gx, gy = xs[f][ci], ys[f][ci]
            if order_track and gx != ABSENT:
                frac, off = arc_of((gx - cx) * scale, (gy - cy) * scale)
                if f == 0:
                    in_pit[ci] = off > PIT_M
                elif in_pit[ci] and off <= PIT_M:
                    in_pit[ci] = False
                pit[ci] = in_pit[ci]
                pv = prev_frac[ci]
                if pv is None:
                    # The grid straddles the timing line, so on the opening
                    # frame a car just short of it is a lap behind one past.
                    glap[ci] = (ln - 1) - (1 if f == 0 and frac > 0.5 else 0)
                elif pv > 0.7 and frac < 0.3:
                    glap[ci] += 1
                elif pv < 0.3 and frac > 0.7:
                    glap[ci] -= 1
                prev_frac[ci] = frac
                p = glap[ci] + frac
            else:
                # Off the feed for a moment: hold the last known position.
                p = (glap[ci] + prev_frac[ci]) if prev_frac[ci] is not None else float(ln - 1)
            prog.append((p, -ci))

        # A car still waiting in the pit lane has not started the race: put it
        # behind the field rather than wherever the centreline says it is.
        if any(pit):
            racing = [prog[i][0] for i in range(len(nums)) if not pit[i]]
            back = (min(racing) if racing else 0.0) - 0.01
            for i in range(len(nums)):
                if pit[i]:
                    prog[i] = (back - 0.01 * i, prog[i][1])

        ranked = sorted(range(len(nums)), key=lambda i: prog[i], reverse=True)
        for pos, ci in enumerate(ranked):
            order[f][pos] = ci

    OUT_BIN.mkdir(parents=True, exist_ok=True)
    OUT_MAN.mkdir(parents=True, exist_ok=True)
    buf = bytearray()
    for f in range(frames):
        for ci in range(len(nums)):
            for arr, c0 in ((xs, cx), (ys, cy)):
                v = arr[f][ci]
                buf += struct.pack("<h", ABSENT if v == ABSENT
                                   else max(-32767, min(32767, int(round((v - c0) * scale)))))
    pos_off = len(buf)
    for f in range(frames):
        buf += bytes(order[f])
    lap_off = len(buf)
    for f in range(frames):
        buf += bytes(lapno[f])

    name = f"{year}-{rnd}"
    (OUT_BIN / f"{name}.bin").write_bytes(buf)


    dmap = {d["driver_number"]: d for d in drivers}
    man = {
        "year": year, "round": rnd, "circuitId": circuit_id, "sessionKey": session_key,
        "step": STEP, "frames": frames, "cars": len(nums),
        "scale": round(scale, 6), "cx": round(cx, 2), "cy": round(cy, 2),
        "posOffset": pos_off, "lapOffset": lap_off, "bytes": len(buf),
        "track": track,
        "drivers": [{
            "n": n,
            "code": (dmap.get(n, {}).get("name_acronym") or str(n)),
            "name": (dmap.get(n, {}).get("full_name") or str(n)).title(),
            "team": dmap.get(n, {}).get("team_name") or "",
            "colour": "#" + (dmap.get(n, {}).get("team_colour") or "999999"),
        } for n in nums],
    }
    (OUT_MAN / f"{name}.json").write_text(json.dumps(man, separators=(",", ":"), sort_keys=True))
    print(f"    -> {len(buf)/1024:.0f} KB binary")
    return man


def main() -> None:
    races = json.loads((ROOT / "site" / "data" / "races.json").read_text())
    meta = json.loads((ROOT / "site" / "data" / "meta.json").read_text())
    year = max(r["year"] for r in races)
    done = [r for r in races if r["year"] == year and r["date"] <= meta["dataAsOf"]]
    print(f"{len(done)} completed rounds in {year}")

    meetings = api(f"meetings?year={year}", f"meet_{year}")
    built = {}
    for r in sorted(done, key=lambda r: r["round"]):
        print(f"  R{r['round']:>2} {r['shortName']}")
        cand = [m for m in meetings if abs(
            (dt.datetime.fromisoformat(m["date_start"]).date()
             - dt.date.fromisoformat(r["date"])).days) <= 3]
        if not cand:
            print("    no matching meeting"); continue
        sess = api(f"sessions?meeting_key={cand[0]['meeting_key']}", f"sess_{cand[0]['meeting_key']}")
        race = [s for s in sess if s.get("session_name") == "Race"]
        if not race:
            print("    no race session"); continue
        m = build(year, r["round"], race[0]["session_key"], r["circuitId"])
        if m:
            built[f"{year}-{r['round']}"] = {"frames": m["frames"], "cars": m["cars"],
                                             "bytes": m["bytes"]}
    (OUT_MAN / "index.json").write_text(json.dumps(built, indent=1, sort_keys=True))
    tot = sum(v["bytes"] for v in built.values())
    print(f"\n{len(built)} replays, {tot/1024/1024:.1f} MB total")


if __name__ == "__main__":
    main()
