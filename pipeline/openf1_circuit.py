"""Build circuit geometry from the timing feed via OpenF1, for circuits the
MultiViewer dataset does not yet carry.

A lap begins when the car crosses the start/finish line, so a lap's position
samples start there by definition — the same property that makes the
MultiViewer polyline authoritative, obtained directly.

Several clean laps from one driver are merged on a shared lap-fraction grid:
one lap samples at roughly 3.7 Hz (~15 m at racing speed), and stacking laps
from the same driver raises the effective resolution without smearing different
drivers' lines together.

Usage: python3 pipeline/openf1_circuit.py <circuit_id> <session_key> [n_laps]
"""
from __future__ import annotations
import json, math, sys, urllib.request, datetime as dt
from pathlib import Path

OUT = Path(__file__).resolve().parent / "vendor" / "openf1"
BINS = 1000


def get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "f1-analysis/0.1 (personal project)"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def build(circuit_id: str, session_key: int, n_laps: int = 8) -> dict:
    laps = [l for l in get(f"https://api.openf1.org/v1/laps?session_key={session_key}")
            if l.get("lap_duration") and l.get("date_start") and not l.get("is_pit_out_lap")]
    if not laps:
        raise SystemExit("no usable laps")

    # One driver, so the racing line stays consistent across merged laps.
    laps.sort(key=lambda l: l["lap_duration"])
    drv = laps[0]["driver_number"]
    mine = sorted((l for l in laps if l["driver_number"] == drv),
                  key=lambda l: l["lap_duration"])[:n_laps]
    mine.sort(key=lambda l: l["lap_number"])
    print(f"driver {drv}: merging {len(mine)} laps "
          f"({mine[0]['lap_number']}-{mine[-1]['lap_number']}), "
          f"{min(l['lap_duration'] for l in mine):.3f}-{max(l['lap_duration'] for l in mine):.3f}s")

    lo = dt.datetime.fromisoformat(min(l["date_start"] for l in mine))
    hi = (dt.datetime.fromisoformat(max(l["date_start"] for l in mine))
          + dt.timedelta(seconds=max(l["lap_duration"] for l in mine) + 1))
    loc = sorted(get(f"https://api.openf1.org/v1/location?session_key={session_key}"
                     f"&driver_number={drv}&date>={lo.isoformat()}&date<={hi.isoformat()}"),
                 key=lambda r: r["date"])
    print(f"{len(loc)} position samples over the window")

    # Bin every lap's samples onto a shared fraction-of-lap grid and average.
    acc = [[0.0, 0.0, 0] for _ in range(BINS)]
    used = 0
    for l in mine:
        s = dt.datetime.fromisoformat(l["date_start"])
        e = s + dt.timedelta(seconds=l["lap_duration"])
        pts = [r for r in loc if s <= dt.datetime.fromisoformat(r["date"]) <= e
               and r.get("x") is not None]
        if len(pts) < 50:
            continue
        used += 1
        for r in pts:
            f = (dt.datetime.fromisoformat(r["date"]) - s).total_seconds() / l["lap_duration"]
            b = min(BINS - 1, max(0, int(f * BINS)))
            acc[b][0] += r["x"] / 10.0; acc[b][1] += r["y"] / 10.0; acc[b][2] += 1

    filled = [(a[0] / a[2], a[1] / a[2]) for a in acc if a[2]]
    print(f"{used} laps merged -> {len(filled)} of {BINS} bins filled")

    # Each bin averages only a handful of ~3.7 Hz samples, so it carries a few
    # metres of positional noise. Summed over ~1000 short segments that noise
    # inflates the measured length badly — the raw merge came out 23% long
    # against a single lap's 1.1%. A short circular moving average removes the
    # jitter without touching the shape at corner scale.
    def smooth(seq, w):
        n = len(seq); h = max(1, w // 2)
        return [(sum(seq[(i + k) % n][0] for k in range(-h, h + 1)) / (2 * h + 1),
                 sum(seq[(i + k) % n][1] for k in range(-h, h + 1)) / (2 * h + 1))
                for i in range(n)]

    def clen(seq):
        return sum(math.dist(seq[i], seq[(i + 1) % len(seq)]) for i in range(len(seq)))

    print(f"  raw merge: {clen(filled):.0f} m")
    best, bw = filled, 0
    for w in (3, 5, 7, 9, 11, 15):
        s = smooth(filled, w)
        print(f"  smoothed w={w:<3} {clen(s):.0f} m")
        best, bw = s, w
        if clen(s) < clen(filled) * 0.85:      # jitter gone, stop before eroding shape
            break
    filled = best
    L = clen(filled)
    print(f"chose window {bw}: closed length {L:.0f} m, mean spacing {L/len(filled):.1f} m")

    return {"circuitId": circuit_id, "sessionKey": session_key, "driverNumber": drv,
            "laps": [l["lap_number"] for l in mine], "lapsMerged": used,
            "length": round(L, 1), "points": [[round(x, 2), round(y, 2)] for x, y in filled],
            "source": "F1 timing feed via OpenF1"}


if __name__ == "__main__":
    cid, sk = sys.argv[1], int(sys.argv[2])
    n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    OUT.mkdir(parents=True, exist_ok=True)
    data = build(cid, sk, n)
    (OUT / f"{cid}.json").write_text(json.dumps(data, separators=(",", ":"), sort_keys=True))
    print(f"-> pipeline/vendor/openf1/{cid}.json")
