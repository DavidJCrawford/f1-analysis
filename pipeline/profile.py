"""Derive a curvature profile and corner list from circuit geometry.

The trace is projected to metres, resampled to uniform arc length, smoothed,
and differentiated to signed curvature. Corners are contiguous runs tighter
than a radius threshold.

These corners are DERIVED, not official. The official turn count from F1DB is
carried alongside so the page can state the disagreement rather than imply the
numbering is authoritative. Official corner positions exist only in the
timing-era telemetry feed (2018+) and are a later pipeline stage.
See Docs/knowledge/references/circuits/corner-and-sector-detection.md
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import load_centrelines  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GEO  = ROOT / "pipeline" / "vendor" / "f1-circuits.geojson"
DATA = ROOT / "site" / "data"

STEP          = 5.0    # m between resampled points
SMOOTH_M      = 35.0   # m — kills tracing noise without eating real corners
DISPLAY_SMOOTH= 90.0   # m — the display series needs more: the source trace has
                       # ~45 m point spacing, and what survives at 35 m is
                       # legible to a corner detector but reads as noise on a
                       # chart. Detection and display are smoothed separately.
FLAT_RADIUS   = 700.0  # m — beyond this the track is drawn as straight. Without
                       # a deadband every straight wobbles.
# Calibrated by sweeping against F1DB's official turn counts across all 39
# circuits with geometry: MAE 1.62 corners, within +/-2 for 31 of 39.
CORNER_RADIUS = 220.0  # m — tighter than this counts as cornering
MIN_ARC       = 25.0   # m — a corner must persist this far
MERGE_GAP     = 40.0   # m — runs closer than this are one corner complex
DISPLAY_MAX   = 420    # emitted profile samples per circuit



def resample(pts: list[tuple[float, float]], step: float) -> list[tuple[float, float]]:
    """Uniform arc-length resampling of a closed polyline."""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    out, target, acc, i = [], 0.0, 0.0, 0
    while target < total and i < len(seg):
        while i < len(seg) and acc + seg[i] < target:
            acc += seg[i]; i += 1
        if i >= len(seg): break
        t = (target - acc) / seg[i] if seg[i] else 0.0
        x0, y0 = pts[i]; x1, y1 = pts[i + 1]
        out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        target += step
    return out


def smooth_closed(vals: list[float], window: int) -> list[float]:
    """Circular moving average — the lap is a loop, so the ends must join."""
    n = len(vals); half = max(1, window // 2)
    return [sum(vals[(i + k) % n] for k in range(-half, half + 1)) / (2 * half + 1)
            for i in range(n)]


def curvature(pts: list[tuple[float, float]]) -> list[float]:
    """Signed curvature (1/m) from the circumscribed circle of each triple.
    Positive is a left turn."""
    n = len(pts); out = []
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        a = math.dist((x0, y0), (x1, y1))
        b = math.dist((x1, y1), (x2, y2))
        c = math.dist((x0, y0), (x2, y2))
        cross = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
        out.append(0.0 if a * b * c == 0 else 2 * cross / (a * b * c))
    return out


def find_corners(kappa: list[float], step: float) -> list[dict]:
    thresh = 1.0 / CORNER_RADIUS
    n = len(kappa)
    flags = [abs(k) > thresh for k in kappa]
    runs: list[list[int]] = []
    i = 0
    while i < n:
        if flags[i]:
            j = i
            while j + 1 < n and flags[(j + 1) % n] and j + 1 < n:
                j += 1
            runs.append([i, j]); i = j + 1
        else:
            i += 1
    # wrap a run spanning the start/finish line
    if len(runs) > 1 and runs[0][0] == 0 and runs[-1][1] == n - 1:
        runs[0][0] = runs[-1][0] - n; runs.pop()
    # merge, then drop anything too brief to be a corner
    merged: list[list[int]] = []
    for r in runs:
        if merged and (r[0] - merged[-1][1]) * step < MERGE_GAP and \
           (kappa[r[0] % n] > 0) == (kappa[merged[-1][1] % n] > 0):
            merged[-1][1] = r[1]
        else:
            merged.append(r)
    corners = []
    for s, e in merged:
        if (e - s + 1) * step < MIN_ARC: continue
        idx = range(s, e + 1)
        apex = max(idx, key=lambda i: abs(kappa[i % n]))
        kmax = kappa[apex % n]
        corners.append({
            "entry": round(s * step, 1), "apex": round(apex * step, 1),
            "exit": round(e * step, 1),
            "radius": round(1.0 / abs(kmax), 1) if kmax else None,
            "dir": "L" if kmax > 0 else "R",
            "arc": round((e - s + 1) * step, 1),
        })
    corners.sort(key=lambda c: c["apex"])
    for i, c in enumerate(corners, 1): c["n"] = i
    return corners


def corners_from_official(official, kappa, step, length):
    """Spans around published corner positions, grown while the track still curves."""
    n = len(kappa)
    SPAN_RADIUS = 450.0          # m — generous: the apex is known, only the extent is not
    lim = 1.0 / SPAN_RADIUS
    out = []
    for c in sorted(official, key=lambda c: c["distance"]):
        apex = int(round((c["distance"] % length) / step)) % n
        # Nudge to the local curvature peak; published positions sit near, not
        # exactly on, the sharpest point of a recorded lap.
        win = 6
        apex = max(range(apex - win, apex + win + 1), key=lambda i: abs(kappa[i % n])) % n
        lo = hi = apex
        while abs(kappa[(lo - 1) % n]) > lim and (hi - lo) * step < 600:
            lo -= 1
        while abs(kappa[(hi + 1) % n]) > lim and (hi - lo) * step < 600:
            hi += 1
        k = kappa[apex]
        out.append({
            "entry": round((lo * step) % length, 1), "apex": round((apex * step) % length, 1),
            "exit": round((hi * step) % length, 1),
            "radius": round(1.0 / abs(k), 1) if k else None,
            "dir": "L" if k > 0 else "R", "arc": round((hi - lo + 1) * step, 1),
            "n": c["number"], "official": True,
        })
    return out


circuits = {c["id"]: c for c in json.loads((DATA / "circuits.json").read_text())}
lines = load_centrelines()

profiles, report = {}, []
for cid, v in sorted(lines.items()):
    pts = list(v["pts"])
    pts.append(pts[0])

    rs = resample(pts, STEP)
    if len(rs) < 40: continue
    xs = smooth_closed([p[0] for p in rs], int(SMOOTH_M / STEP))
    ys = smooth_closed([p[1] for p in rs], int(SMOOTH_M / STEP))
    sm = list(zip(xs, ys))
    kappa = smooth_closed(curvature(sm), 3)

    # Display series: smoothed harder, then deadbanded so straights are flat.
    dxs = smooth_closed([p[0] for p in rs], int(DISPLAY_SMOOTH / STEP))
    dys = smooth_closed([p[1] for p in rs], int(DISPLAY_SMOOTH / STEP))
    dk = smooth_closed(curvature(list(zip(dxs, dys))), 5)
    dk = [0.0 if abs(k) < 1.0 / FLAT_RADIUS else k for k in dk]

    # A start/finish line is always on a straight. Both geometry sources begin
    # their trace at an arbitrary vertex, and at Silverstone the two disagree by
    # 135 degrees of the lap — so the trace start cannot be assumed to be the
    # real line. Where it lands on a curve it certainly is not, and the map
    # draws no chequer rather than marking a false one.
    # Where OSM records the real line, trust it — the curvature test is only a
    # proxy for "is this plausibly the start/finish", and no longer needed.
    START_STRAIGHT_RADIUS = 400.0
    start_k = max(abs(dk[i % len(dk)]) for i in range(-2, 3))
    # The feed defines the line and OSM records it; neither needs the curvature
    # proxy, which exists only to sanity-check an inferred trace start.
    start_known = (v.get("startSource") in ("feed", "osm")
                   or start_k < 1.0 / START_STRAIGHT_RADIUS)

    # Where the feed publishes official corner positions, anchor to them and
    # measure only the extent: the apex is given, so the curvature threshold is
    # used to grow a span outward from it rather than to guess that a corner is
    # there at all. Detection remains the fallback for circuits the feed does
    # not cover.
    length = len(rs) * STEP
    official_corners = v.get("officialCorners") or []
    if official_corners:
        corners = corners_from_official(official_corners, kappa, STEP, length)
    else:
        corners = find_corners(kappa, STEP)
    official = circuits[cid].get("turns")

    stride = max(1, len(kappa) // DISPLAY_MAX)
    profiles[cid] = {
        "length": round(length, 1), "step": round(STEP * stride, 2),
        # Display curvature, signed, in 1/km so the numbers stay small in JSON.
        "k": [round(k * 1000, 3) for k in dk[::stride]],
        "corners": corners, "detected": len(corners), "officialTurns": official,
        "cornersAreOfficial": bool(official_corners),
        "startKnown": start_known, "startSource": v.get("startSource", "trace"),
    }
    report.append((cid, len(corners), official, length, circuits[cid]["length"], v["spacing"]))

(DATA / "profiles.json").write_text(
    json.dumps(profiles, sort_keys=True, separators=(",", ":"), ensure_ascii=False))

exact = sum(1 for _, d, o, *_ in report if o and d == o)
close = sum(1 for _, d, o, *_ in report if o and abs(d - o) <= 2)
print(f"{'circuit':22} {'detected':>8} {'official':>8} {'spacing':>8}")
for cid, d, o, gl, rl, sp in sorted(report, key=lambda r: -(r[1] or 0))[:10]:
    flag = "" if o and abs(d - o) <= 2 else "   <-- differs by >2"
    print(f"{cid:22} {d:8} {str(o or '-'):>8} {sp:7.1f}m{flag}")
off = [c for c, v in profiles.items() if not v["startKnown"]]
print(f"\n{len(profiles)} profiles · exact match {exact}/{len(report)} · within 2 {close}/{len(report)}")
offc = [c for c, v in profiles.items() if v["cornersAreOfficial"]]
print(f"corner positions official for {len(offc)}/{len(profiles)} circuits")
osm = [c for c, v in profiles.items() if v["startSource"] == "osm"]
print(f"start/finish from OSM for {len(osm)}: {', '.join(sorted(osm))}")
print(f"start/finish unknown for {len(off)} — no chequer drawn: {', '.join(sorted(off)) or 'none'}")
print(f"{(DATA/'profiles.json').stat().st_size/1024:.0f} KB")
