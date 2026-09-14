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
    laps = [l for l in api(f"laps?session_key={session_key}", f"lap_{session_key}")
            if l.get("date_start") and l.get("lap_duration")]
    if not drivers or not laps:
        print("    no driver or lap data"); return None

    nums = sorted({d["driver_number"] for d in drivers})
    starts = [dt.datetime.fromisoformat(l["date_start"]) for l in laps]
    t0 = min(starts)
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

    cx, cy = (min(allx) + max(allx)) / 2, (min(ally) + max(ally)) / 2
    extent = max(max(allx) - min(allx), max(ally) - min(ally)) or 1.0
    scale = 30000.0 / extent           # fit into int16 with headroom

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
    for f in range(frames):
        t = f * STEP
        prog = []
        for ci, n in enumerate(nums):
            p, ln = -1.0, 0
            for st, du, num in by_driver[n]:
                if st <= t:
                    p = num + min(1.0, (t - st) / du) if du else num
                    ln = num
                else:
                    break
            prog.append((p, -ci))
            lapno[f][ci] = min(255, ln)
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
