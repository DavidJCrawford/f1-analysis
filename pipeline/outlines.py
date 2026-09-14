"""Crosswalk bacinger circuit geometry onto F1DB circuit ids.

This is the circuit-layout-registry problem in miniature: two sources with
independent identifier schemes and no shared key. Matching is on place name with
a hand-maintained override table, and every match is recorded so the join is
auditable rather than implicit.
See Docs/knowledge/references/circuits/circuit-layout-registry.md
"""
from __future__ import annotations
import json, math, unicodedata, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site" / "data"

# bacinger Location -> F1DB circuit id, where a normalised match fails
OVERRIDES = {
    "spa francorchamps": "spa-francorchamps", "sao paulo": "interlagos",
    "le castellet": "paul-ricard", "scarperia e san piero": "mugello",
    "nurburg": "nurburgring", "dix": "watkins-glen", "johannesburg": "kyalami",
    "sakhir": "bahrain", "lusail": "lusail", "singapore": "marina-bay",
    # Barcelona is genuinely ambiguous: F1DB has three circuits whose place is
    # or contains "Barcelona" (pedralbes, montjuic, catalunya). bacinger's
    # es-1991 is the 1991 Montmelo circuit. A bare place-name match picks
    # pedralbes - a 1950s street circuit with two races - and is silently wrong.
    "barcelona": "catalunya",
}

# A match is rejected if the two sources disagree about circuit length by more
# than this. Place names are not unique and a wrong join produces a page that
# looks right and is not.
LENGTH_TOLERANCE = 0.05

def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()

circuits = json.loads((OUT / "circuits.json").read_text())
by_place = {norm(c["place"]): c["id"] for c in circuits}
by_name  = {norm(c["name"]): c["id"] for c in circuits}
by_id    = {norm(c["id"]): c["id"] for c in circuits}

gj = json.loads((ROOT / "pipeline" / "vendor" / "f1-circuits.geojson").read_text())
outlines, matched, unmatched = {}, [], []

for f in gj["features"]:
    p = f["properties"]; loc = norm(p["Location"])
    cid = OVERRIDES.get(loc) or by_place.get(loc) or by_name.get(loc) or by_id.get(loc)
    if cid not in {c["id"] for c in circuits}:
        unmatched.append((p["Location"], p["id"], "no candidate")); continue

    # Validate the join against an independent quantity both sources carry.
    ref = next(c for c in circuits if c["id"] == cid)
    dl = p.get("length")                      # bacinger: metres
    rl = ref["length"] * 1000 if ref.get("length") else None   # F1DB: kilometres
    if dl and rl and abs(dl - rl) / rl > LENGTH_TOLERANCE:
        unmatched.append((p["Location"], p["id"],
                          f"length mismatch vs {cid}: {dl:.0f}m vs {rl:.0f}m "
                          f"({abs(dl-rl)/rl*100:.1f}%)")); continue

    co = f["geometry"]["coordinates"]
    lat0 = sum(c[1] for c in co) / len(co)
    k = math.cos(math.radians(lat0))
    pts = [(c[0] * k, c[1]) for c in co]
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    w, h = max(xs) - min(xs), max(ys) - min(ys)
    s = 1.0 / max(w, h)                      # fit longest axis into a unit box
    ox, oy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    # y flipped for SVG; 4dp on a unit box is ~0.6 m on a 6 km circuit
    norm_pts = [[round((x - ox) * s, 4), round(-(y - oy) * s, 4)] for x, y in pts]

    outlines[cid] = {
        "points": norm_pts, "aspect": round(w / h, 4),
        "declaredLength": p.get("length"), "openedYear": p.get("opened"),
        "sourceId": p["id"], "source": "bacinger/f1-circuits (MIT)",
    }
    matched.append((p["Location"], cid, abs((p["length"] or rl) - rl) / rl))

(OUT / "outlines.json").write_text(
    json.dumps(outlines, sort_keys=True, separators=(",", ":"), ensure_ascii=False))

print(f"matched   {len(matched)}/{len(gj['features'])}   (length agreement within {LENGTH_TOLERANCE:.0%})")
worst = sorted(matched, key=lambda m: -m[2])[:3]
for loc, cid, d in worst: print(f"    widest disagreement: {loc:22} -> {cid:20} {d*100:.2f}%")
if unmatched:
    print(f"REJECTED  {len(unmatched)}  (no outline; page falls back to honest absence)")
    for loc, sid, why in sorted(unmatched): print(f"    {loc:22} [{sid:9}] {why}")
print(f"\n{(OUT/'outlines.json').stat().st_size/1024:.0f} KB -> site/data/outlines.json")
