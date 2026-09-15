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

    # Uniform grid, linearly interpolated between samples — but only across
    # short gaps. One round's feed has seven minutes of positions and then
    # nothing for the next fifty, and drawing a straight line between the two
    # ends of that hole put the cars on a slow crawl across the map for the
    # rest of the race. A gap longer than a few seconds is not something to
    # interpolate: it is a stretch of race we do not have, and the cars belong
    # off the map until the feed picks them up again.
    MAX_GAP = 5.0
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
            if j + 1 >= len(s):
                continue
            t_a, xa, ya = s[j]; t_b, xb, yb = s[j + 1]
            if t_b - t_a > MAX_GAP or t_a > t + MAX_GAP or t_b < t - MAX_GAP:
                continue
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
    # If the feed only covers a corner of the race there is no replay to show.
    # Monaco 2026 is the case in point: the API has the first seven minutes of
    # a two-and-a-half hour race and returns nothing for the rest, so what would
    # be published under "the full race" is five laps of seventy-eight. Better
    # for the race page to carry no replay than a misleading one.
    need = max(2, len(nums) // 2)
    covered = sum(1 for f in range(frames)
                  if sum(1 for ci in range(len(nums)) if xs[f][ci] != ABSENT) >= need)
    if covered < frames * 0.5:
        print(f"    positions cover {covered / frames * 100:.0f}% of the race; no replay")
        return None

    # And the same at the other end: at least one round's position feed stops
    # long before the lap data does, which left the replay running for over an
    # hour with an empty track. End it where the cars do.
    tail = frames
    while tail > skip + 1 and sum(1 for ci in range(len(nums))
                                 if xs[tail - 1][ci] != ABSENT) < need:
        tail -= 1
    if tail < frames:
        print(f"    no positions after {tail * STEP / 60:.0f} min; ending there")
        xs, ys = xs[:tail], ys[:tail]
        frames = tail

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

        # A car cannot move far between frames, so where it was last time is a
        # strong hint about where it is now. Without that hint the nearest point
        # on the centreline is the answer, and at a circuit that runs back
        # alongside itself — Monaco above all — the nearest point flips to the
        # neighbouring stretch of track and the lap count falls apart.
        REACH = 0.5 * 120.0 * scale     # a frame at 430 km/h, with room to spare

        def _leg(j, x, y):
            ax, ay = order_track[j]
            bx, by = order_track[(j + 1) % len(order_track)]
            vx, vy = bx - ax, by - ay
            l2 = vx * vx + vy * vy
            u = 0.0 if not l2 else max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / l2))
            qx, qy = ax + vx * u, ay + vy * u
            return (x - qx) ** 2 + (y - qy) ** 2, (tcum[j] + tseg[j] * u) / TLAP

        def _sweep(x, y, lo, hi):
            """Closest approach over a run of legs, coarse then refined."""
            bi, bd = lo, float("inf")
            for i in range(lo, hi + 1, COARSE):
                j = i % len(order_track)
                dx = order_track[j][0] - x; dy = order_track[j][1] - y
                d = dx * dx + dy * dy
                if d < bd: bd, bi = d, i
            best = (float("inf"), 0.0)
            for i in range(bi - COARSE, bi + COARSE + 1):
                d2, frac = _leg(i % len(order_track), x, y)
                if d2 < best[0]:
                    best = (d2, frac)
            return best

        def arc_of(x, y, hint=None):
            """Fraction of a lap at the nearest centreline point, and how far off
            it the car is. The second number separates the pit lane from the
            track: the racing line never strays far from the centreline, so a
            large offset means the car is not racing."""
            whole = _sweep(x, y, 0, len(order_track) - 1)
            if hint is None:
                return whole[1], math.sqrt(whole[0]) / scale
            # Search only the stretch the car could plausibly have reached. Take
            # the unrestricted answer instead when it is far better, which is how
            # a car that has been off the feed for a while finds itself again.
            at = hint * TLAP
            lo = int((at - REACH) / TLAP * len(order_track))
            hi = int((at + REACH) / TLAP * len(order_track))
            near = _sweep(x, y, lo, hi)
            if whole[0] * 9.0 < near[0]:
                return whole[1], math.sqrt(whole[0]) / scale
            return near[1], math.sqrt(near[0]) / scale

    # Progress: completed laps plus the fraction through the current one.
    by_driver: dict[int, list] = {n: [] for n in nums}
    for l in laps:
        if l["driver_number"] in by_driver:
            by_driver[l["driver_number"]].append(
                ((dt.datetime.fromisoformat(l["date_start"]) - t0).total_seconds(),
                 l["lap_duration"], l["lap_number"]))
    for n in by_driver:
        by_driver[n].sort()

    grid0: list[tuple[float, int]] = []                  # (progress, car) at the lights
    order = [[0] * len(nums) for _ in range(frames)]
    downs = [[0] * len(nums) for _ in range(frames)]    # laps behind the leader
    leadlap = [0] * frames                              # the lap the race is on
    offs = [[0.0] * len(nums) for _ in range(frames)]   # metres off the centreline
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
    # Counting wraps only works while the positions are continuous. Some rounds
    # arrive with the feed full of holes — nearly two hundred jumps per car at
    # one of them — and a lap missed across a hole is a lap lost for good, by a
    # different amount for each car, which scrambles the order by the end. So
    # after any jump the count is re-anchored to the lap number from the feed,
    # which cannot drift. Only in the middle of a lap: either side of the line
    # the feed's number and the car's position disagree about which lap it is.
    prev_xy: list[tuple[float, float] | None] = [None] * len(nums)
    LEAP = 3.0 * 120.0 * STEP * scale  # well beyond any car's travel in a frame
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

            gx, gy = xs[f][ci], ys[f][ci]
            if order_track and gx != ABSENT:
                frac, off = arc_of((gx - cx) * scale, (gy - cy) * scale, prev_frac[ci])
                offs[f][ci] = off
                if f == 0:
                    in_pit[ci] = off > PIT_M
                elif in_pit[ci] and off <= PIT_M:
                    in_pit[ci] = False
                pit[ci] = in_pit[ci]

                here = ((gx - cx) * scale, (gy - cy) * scale)
                was = prev_xy[ci]
                leapt = was is None or math.hypot(here[0] - was[0], here[1] - was[1]) > LEAP
                prev_xy[ci] = here

                pv = prev_frac[ci]
                if pv is None:
                    # The grid straddles the timing line, so on the opening
                    # frame a car just short of it is a lap behind one past.
                    glap[ci] = (ln - 1) - (1 if f == 0 and frac > 0.5 else 0)
                elif leapt and ln >= 1 and 0.15 < frac < 0.85 and glap[ci] != ln - 1:
                    glap[ci] = ln - 1
                elif not leapt and pv > 0.7 and frac < 0.3:
                    glap[ci] += 1
                elif not leapt and pv < 0.3 and frac > 0.7:
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

        # Being a lap down is a matter of distance, not of lap numbers. Mid-race
        # every car that has not yet reached the line this time round reads one
        # lower on the counter than the leader, which is most of the field and
        # none of them lapped. So the gap is taken from progress round the
        # circuit, and a car is a lap down only once the leader is genuinely a
        # full lap further on.
        gp = [q[0] for q in prog]
        ahead = max(gp)
        leadlap[f] = min(255, max(0, int(math.floor(ahead)) + 1))
        for ci in range(len(nums)):
            downs[f][ci] = min(255, max(0, int(math.floor(ahead - gp[ci]))))

        ranked = sorted(range(len(nums)), key=lambda i: prog[i], reverse=True)
        for pos, ci in enumerate(ranked):
            order[f][pos] = ci

        if f == 0:                       # the grid, for the start line below
            grid0 = [(prog[i][0], i) for i in ranked if not pit[i] and xs[0][i] != ABSENT]

    # ── the start line ──────────────────────────────────────────────────────
    # Not the same line as the one laps are counted at. A Formula 1 circuit has
    # two: the finish line, placed opposite race control so a close finish can
    # be judged by eye, and the start line at the front of the grid. Index 0 of
    # the centreline is the finish line — that is the one the timing feed rolls
    # the lap counter on, and it can be most of the way round the grid from the
    # front of it, or a couple of hundred metres before the back of it.
    #
    # So the line to draw at a standing start is the start line, and the grid
    # itself is what locates it: the field lines up behind it at a fixed eight
    # metres a slot, which makes it half a slot ahead of pole. Measured from the
    # field rather than assumed, so a circuit spacing its grid differently still
    # comes out right.
    def line_at(frac: float) -> dict:
        """A point on the centreline, with the direction of travel there."""
        at = (frac % 1.0) * TLAP
        for j in range(len(order_track)):
            if at <= tseg[j] or j == len(order_track) - 1:
                u = at / tseg[j] if tseg[j] else 0.0
                ax, ay = order_track[j]
                bx, by = order_track[(j + 1) % len(order_track)]
                tx, ty = bx - ax, by - ay
                tl = math.hypot(tx, ty) or 1.0
                return {"x": round(ax + tx * u, 2), "y": round(ay + ty * u, 2),
                        "tx": round(tx / tl, 6), "ty": round(ty / tl, 6)}
            at -= tseg[j]
        return {"x": 0.0, "y": 0.0, "tx": 1.0, "ty": 0.0}

    start = None
    if order_track and len(grid0) >= 5 and frames > 2:
        ahead = [g[0] for g in grid0]                        # pole first, in laps
        gaps = sorted(ahead[k] - ahead[k + 1] for k in range(len(ahead) - 1))
        slot = gaps[len(gaps) // 2] * TLAP / scale           # median, in metres
        # Only when the field is still in grid formation. Two things say it is:
        # the cars are a grid slot apart, and the race has not yet run away from
        # the line. Some rounds open a second or two after the lights, with the
        # field intact but rolling, and those are worth keeping — the line comes
        # out a few metres long. Some open with the feed's first positions
        # minutes in, and there the field is spread and a line taken from the
        # leader would be nowhere near the start.
        rolled = sorted(math.hypot(xs[1][i] - xs[0][i], ys[1][i] - ys[0][i])
                        for _, i in grid0 if xs[1][i] != ABSENT)
        pace = rolled[len(rolled) // 2] if rolled else 1e9   # metres in a frame
        if 4.0 <= slot <= 14.0 and pace < 15.0:
            start_frac = (ahead[0] + (slot / 2) * scale / TLAP) % 1.0
            start = line_at(start_frac)
            start["frac"] = round(start_frac, 6)

    # ── what each car is doing ──────────────────────────────────────────────
    # Three things can take a car out of the race picture: it pits, it stops on
    # track, or it is gone from the feed. Left unmarked they all read as a car
    # drifting oddly, so each one is recorded as a span and drawn for what it is.
    #
    # Both come from the record rather than from the shape of the data. The
    # position feed stalls often enough — the same coordinate repeated for
    # several seconds, then a jump — that a car reads as stationary when it is
    # at full speed, so anything inferred from apparent speed is mostly noise.
    # The feed knows when a stop happened and the results know who retired; in
    # each case geometry is used only to pin down the extent.
    ON_TRACK_M = 4.0        # racing samples sit within a metre of the line
    PARKED_M = 15.0         # a car that has not moved this far has not moved
    PIT, STOPPED = 1, 2

    state = [[0] * len(nums) for _ in range(frames)]

    def mark(ci: int, a: int, b: int, kind: int) -> None:
        for f in range(max(0, a), min(frames, b + 1)):
            state[f][ci] = kind

    def grow(ci: int, f: int) -> tuple[int, int]:
        """The span around frame f for which the car is off the racing line."""
        a = b = min(max(f, 0), frames - 1)
        while a > 0 and offs[a - 1][ci] > ON_TRACK_M:
            a -= 1
        while b < frames - 1 and offs[b + 1][ci] > ON_TRACK_M:
            b += 1
        return a, b

    # Who failed to finish, from the classification rather than the telemetry.
    retired: set[int] = set()
    try:
        season = json.loads((ROOT / "site" / "data" / "seasons" / f"{year}.json").read_text())
        for r in season.get("results", {}).get(str(rnd), []):
            if r.get("reasonRetired") and str(r.get("no", "")).isdigit():
                retired.add(int(r["no"]))
    except FileNotFoundError:
        pass

    if order_track:
        idx = {n: ci for ci, n in enumerate(nums)}
        for r in api(f"pit?session_key={session_key}", f"pit_{session_key}"):
            ci = idx.get(r.get("driver_number"))
            if ci is None or not r.get("date"):
                continue
            t = (dt.datetime.fromisoformat(r["date"]) - t0).total_seconds()
            f = int(round(t / STEP)) - skip
            if not (0 <= f < frames):
                continue
            # The feed's instant can land on a sample that is briefly back near
            # the line, so search a little either way for the off-line stretch.
            for probe in (f, f - 4, f + 4, f - 10, f + 10):
                if 0 <= probe < frames and offs[probe][ci] > ON_TRACK_M:
                    mark(ci, *grow(ci, probe), PIT)
                    break

        # A car released from the pit lane after the start never appears in the
        # pit feed, because it never made a stop.
        for ci in range(len(nums)):
            if offs[0][ci] > ON_TRACK_M and xs[0][ci] != ABSENT:
                mark(ci, *grow(ci, 0), PIT)

        # Retirements. The results say who did not make the end and why; the
        # positions say where the car came to rest. Marked through to the end of
        # the race, so a car that is towed away still reads as out of it rather
        # than quietly holding its last place in the order.
        for n in retired:
            ci = idx.get(n)
            if ci is None:
                continue
            last = next((f for f in range(frames - 1, -1, -1) if xs[f][ci] != ABSENT), None)
            if last is None:
                continue
            a = last
            while a > 0 and xs[a - 1][ci] != ABSENT and \
                    math.hypot(xs[a - 1][ci] - xs[last][ci], ys[a - 1][ci] - ys[last][ci]) < PARKED_M:
                a -= 1
            mark(ci, a, frames - 1, STOPPED)

    # Spans, not a byte per car per frame: a car is racing almost all the time,
    # so the whole season's worth of this fits in a few kilobytes of manifest.
    spans: list[list[int]] = []
    for ci in range(len(nums)):
        f = 0
        while f < frames:
            k = state[f][ci]
            if not k:
                f += 1
                continue
            a = f
            while f + 1 < frames and state[f + 1][ci] == k:
                f += 1
            spans.append([ci, a, f, k])
            f += 1

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
        buf += bytes(downs[f])
    lead_off = len(buf)
    buf += bytes(leadlap)

    name = f"{year}-{rnd}"
    (OUT_BIN / f"{name}.bin").write_bytes(buf)


    dmap = {d["driver_number"]: d for d in drivers}
    man = {
        "year": year, "round": rnd, "circuitId": circuit_id, "sessionKey": session_key,
        "step": STEP, "frames": frames, "cars": len(nums),
        "scale": round(scale, 6), "cx": round(cx, 2), "cy": round(cy, 2),
        "posOffset": pos_off, "lapOffset": lap_off, "leadOffset": lead_off,
        "bytes": len(buf),
        "track": track,
        # [car, firstFrame, lastFrame, 1 = in the pits, 2 = stopped on track]
        "spans": spans,
        # Where the field lines up behind, with the track's direction there.
        # Absent when the replay does not open on a grid.
        "start": start,
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
    built, lines = {}, {}
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
            # The start line is measured from a grid, so only a race can give it.
            # Keyed by circuit, because that is where it belongs: it is a painted
            # line on a track, not a property of one afternoon.
            if m.get("start"):
                lines[r["circuitId"]] = {"frac": m["start"]["frac"], "fromRound": r["round"]}
    (OUT_MAN / "index.json").write_text(json.dumps(built, indent=1, sort_keys=True))
    (ROOT / "site" / "data" / "startlines.json").write_text(
        json.dumps(lines, indent=1, sort_keys=True) + "\n")
    print(f"start lines for {len(lines)} circuits")
    tot = sum(v["bytes"] for v in built.values())
    print(f"\n{len(built)} replays, {tot/1024/1024:.1f} MB total")


if __name__ == "__main__":
    main()
