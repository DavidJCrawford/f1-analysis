"""Normalised circuit outlines for the site, from the best geometry available.
import sys as _sys; _sys.setrecursionlimit(20000)

Source selection, projection and length validation all live in geo.py so the
outline and the curvature profile can never describe different shapes.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import load_centrelines, DATA  # noqa: E402

def rdp(pts: list[list[float]], eps: float) -> list[list[float]]:
    """Ramer-Douglas-Peucker. 5 m spacing is ~0.35 px at render scale, so the
    display outline is simplified adaptively: straights collapse to a couple of
    points while corners keep every vertex that matters."""
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    den = (dx * dx + dy * dy) ** 0.5
    worst, idx = -1.0, 0
    for i in range(1, len(pts) - 1):
        x, y = pts[i]
        d = (abs(dy * x - dx * y + x2 * y1 - y2 * x1) / den) if den else ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
        if d > worst:
            worst, idx = d, i
    if worst <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:idx + 1], eps)[:-1] + rdp(pts[idx:], eps)


# ~0.35 px at a 440 px render: below the width of the stroke drawn over it.
DISPLAY_EPS = 0.0008

lines = load_centrelines(verbose=True)
outlines = {}
for cid, v in lines.items():
    pts = v["pts"]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    s = 1.0 / max(w, h)                      # fit the longest axis into a unit box
    ox, oy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    # y flipped for SVG; 4dp on a unit box is ~0.6 m on a 6 km circuit
    norm = [[round((x - ox) * s, 5), round(-(y - oy) * s, 5)] for x, y in pts]
    simple = rdp(norm, DISPLAY_EPS)
    if simple[0] != simple[-1]:
        simple.append(simple[0])
    outlines[cid] = {
        "points": [[round(x, 4), round(y, 4)] for x, y in simple],
        "aspect": round(w / h, 4) if h else 1.0,
        "length": round(v["length"], 1),
        "spacing": round(v["spacing"], 2),
        "lengthError": round(v["lengthError"], 5),
        "source": v["source"], "sourceId": v["sourceId"],
        "startSource": v.get("startSource", "trace"),
    }

(DATA / "outlines.json").write_text(
    json.dumps(outlines, sort_keys=True, separators=(",", ":"), ensure_ascii=False))
raw = sum(len(v["pts"]) for v in lines.values())
kept = sum(len(o["points"]) for o in outlines.values())
print(f"\nsimplified {raw} -> {kept} points ({kept/raw*100:.0f}%), "
      f"{(DATA/'outlines.json').stat().st_size/1024:.0f} KB -> site/data/outlines.json")
