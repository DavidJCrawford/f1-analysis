"""Centreline sourcing.

One place decides which geometry a circuit gets, so the outline and the
curvature profile can never disagree about the shape they describe.

Preference is TUMFTM (uniform ~5 m spacing) where it covers a circuit, falling
back to bacinger (mean 44.6 m). Every candidate is validated against the
recorded circuit length before it is accepted: place names are not unique and a
wrong join produces a page that looks right and is not.
"""
from __future__ import annotations
import csv, json, math, re, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "pipeline" / "vendor"
DATA = ROOT / "site" / "data"
LENGTH_TOLERANCE = 0.03

# WGS84
_A, _F = 6378137.0, 1 / 298.257223563
_E2 = _F * (2 - _F)


def scales(lat0: float) -> tuple[float, float]:
    """Metres per degree of longitude and latitude at lat0, on the ellipsoid.

    Using the equatorial radius for both axes - the usual shortcut - is a
    systematic 0.4-2.5 m scale error at F1 latitudes, not noise.
    """
    s = math.sin(math.radians(lat0))
    n = _A / math.sqrt(1 - _E2 * s * s)
    m = _A * (1 - _E2) / (1 - _E2 * s * s) ** 1.5
    return n * math.cos(math.radians(lat0)) * math.pi / 180, m * math.pi / 180


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# bacinger Location -> F1DB circuit id, where a normalised match fails or is wrong
OVERRIDES = {
    "spa francorchamps": "spa-francorchamps", "sao paulo": "interlagos",
    "le castellet": "paul-ricard", "scarperia e san piero": "mugello",
    "nurburg": "nurburgring", "dix": "watkins-glen", "johannesburg": "kyalami",
    "sakhir": "bahrain", "lusail": "lusail", "singapore": "marina-bay",
    # Three F1DB circuits have "Barcelona" as their place. bacinger's es-1991 is
    # the 1991 Montmelo circuit; a bare place match picks pedralbes, a 1950s
    # street circuit with two races, and is silently wrong.
    "barcelona": "catalunya",
}


def _closed_length(pts: list[tuple[float, float]]) -> float:
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) + math.dist(pts[-1], pts[0])


def _tumftm() -> dict[str, dict]:
    d = VENDOR / "tumftm"
    mapping = json.loads((d / "MAPPING.json").read_text())
    out = {}
    for fname, cid in mapping.items():
        f = d / f"{fname}.csv"
        if not f.exists():
            continue
        rows = [r for r in csv.reader(f.open()) if r and not r[0].lstrip().startswith("#")]
        pts, width = [], []
        for r in rows:
            try:
                pts.append((float(r[0]), float(r[1])))
                width.append((float(r[2]), float(r[3])) if len(r) >= 4 else None)
            except ValueError:
                continue
        if len(pts) < 40:
            continue
        out[cid] = {"pts": pts, "width": width, "source": "TUMFTM/racetrack-database (LGPL-3.0)",
                    "sourceId": fname, "startSource": "trace"}
    return out


def _start_finish() -> dict[str, dict]:
    f = VENDOR / "osm-start-finish.json"
    return json.loads(f.read_text()) if f.exists() else {}


def _reorigin(pts: list[tuple[float, float]], target: tuple[float, float]) -> list[tuple[float, float]]:
    """Rotate a closed polyline so it begins at the point nearest `target`.

    Everything downstream measures distance from index 0, so this makes lap
    distances - and the profile's x axis - run from the real start/finish line
    rather than from wherever the trace happened to begin.
    """
    best_i, best_t, best_d2 = 0, 0.0, float("inf")
    n = len(pts)
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        vx, vy = bx - ax, by - ay
        l2 = vx * vx + vy * vy
        tt = 0.0 if not l2 else max(0.0, min(1.0, ((target[0] - ax) * vx + (target[1] - ay) * vy) / l2))
        qx, qy = ax + vx * tt, ay + vy * tt
        d2 = (target[0] - qx) ** 2 + (target[1] - qy) ** 2
        if d2 < best_d2:
            best_i, best_t, best_d2 = i, tt, d2
    ax, ay = pts[best_i]
    bx, by = pts[(best_i + 1) % n]
    snap = (ax + (bx - ax) * best_t, ay + (by - ay) * best_t)
    tail = pts[best_i + 1:] + pts[:best_i + 1]
    return [snap] + tail


def _bacinger() -> dict[str, dict]:
    gj = json.loads((VENDOR / "f1-circuits.geojson").read_text())
    starts = _start_finish()
    # A place name can name several circuits — Las Vegas, Madrid and Barcelona
    # each cover two or three. Collect every candidate and let the caller pick
    # the one whose recorded length matches the geometry.
    by_place: dict[str, list[str]] = {}
    by_name: dict[str, list[str]] = {}
    for c in json.loads((DATA / "circuits.json").read_text()):
        by_place.setdefault(_norm(c["place"]), []).append(c["id"])
        by_name.setdefault(_norm(c["name"]), []).append(c["id"])
    out = {}
    for f in gj["features"]:
        p = f["properties"]
        loc = _norm(p["Location"])
        cands = ([OVERRIDES[loc]] if loc in OVERRIDES
                 else by_place.get(loc) or by_name.get(loc) or [])
        if not cands:
            continue
        co = f["geometry"]["coordinates"]
        lat0 = sum(c[1] for c in co) / len(co)
        lon0 = sum(c[0] for c in co) / len(co)
        kx, ky = scales(lat0)
        pts = [((c[0] - lon0) * kx, (c[1] - lat0) * ky) for c in co]
        if math.dist(pts[0], pts[-1]) < 1.0:
            pts = pts[:-1]

        # Where OSM records the start/finish line, begin the lap there. This
        # trace is geo-referenced, so the node projects into the same frame.
        start_src = "trace"
        for cand in cands:
            sf = starts.get(cand)
            if sf:
                pts = _reorigin(pts, ((sf["lon"] - lon0) * kx, (sf["lat"] - lat0) * ky))
                start_src = "osm"
                break
        out[p["id"]] = {"pts": pts, "width": None, "source": "bacinger/f1-circuits (MIT)",
                        "sourceId": p["id"], "candidates": cands, "startSource": start_src,
                        "declaredLength": p.get("length")}
    return out


def load_centrelines(verbose: bool = False) -> dict[str, dict]:
    """Best available metric centreline per circuit id, length-validated."""
    circuits = {c["id"]: c for c in json.loads((DATA / "circuits.json").read_text())}
    tum, bac = _tumftm(), _bacinger()
    result, report = {}, []

    def err(length: float, cid: str) -> float | None:
        rec = circuits[cid].get("length")
        return abs(length - rec * 1000) / (rec * 1000) if rec else None

    # bacinger features are keyed by their own id and may name several
    # candidates; resolve each to its best-matching circuit first.
    bac_by_cid: dict[str, dict] = {}
    for feat in bac.values():
        length = _closed_length(feat["pts"])
        scored = [(err(length, c), c) for c in feat["candidates"]]
        scored = [(e, c) for e, c in scored if e is not None]
        if not scored:
            continue
        e, cid = min(scored)
        if e > LENGTH_TOLERANCE:
            report.append((cid, "bacinger", "REJECTED", length, circuits[cid]["length"] * 1000, e))
            continue
        prev = bac_by_cid.get(cid)
        if prev is None or e < prev["lengthError"]:
            bac_by_cid[cid] = {**feat, "length": length, "lengthError": e}

    for cid in sorted(set(tum) | set(bac_by_cid)):
        for cand in (tum.get(cid), bac_by_cid.get(cid)):
            if not cand:
                continue
            length = cand.get("length") or _closed_length(cand["pts"])
            e = err(length, cid)
            if e is not None and e > LENGTH_TOLERANCE:
                report.append((cid, cand["source"].split("/")[0], "REJECTED",
                               length, circuits[cid]["length"] * 1000, e))
                continue
            result[cid] = {**cand, "length": length, "spacing": length / len(cand["pts"]),
                           "lengthError": e or 0.0}
            report.append((cid, cand["source"].split("/")[0], "used", length,
                           (circuits[cid].get("length") or 0) * 1000, e or 0.0))
            break

    if verbose:
        used = [r for r in report if r[2] == "used"]
        rej = [r for r in report if r[2] == "REJECTED"]
        tumn = sum(1 for cid, v in result.items() if v["source"].startswith("TUMFTM"))
        osmn = sum(1 for v in result.values() if v.get("startSource") == "osm")
        print(f"{len(result)} centrelines: {tumn} TUMFTM, {len(result)-tumn} bacinger"
              f" · {osmn} re-origined to an OSM start/finish line")
        mean_sp = sum(v["spacing"] for v in result.values()) / len(result)
        print(f"mean point spacing {mean_sp:.1f} m  "
              f"(TUMFTM circuits ~{sum(v['spacing'] for v in result.values() if v['source'].startswith('TUMFTM'))/max(tumn,1):.1f} m)")
        worst = sorted(used, key=lambda r: -r[5])[:3]
        for cid, src, _, L, R, e in worst:
            print(f"  widest length disagreement: {cid:20} {src:10} {L:6.0f}m vs {R:6.0f}m  {e*100:.2f}%")
        for cid, src, _, L, R, e in rej:
            print(f"  rejected: {cid:22} {src:10} {L:6.0f}m vs {R:6.0f}m  {e*100:.1f}%")
    return result


if __name__ == "__main__":
    load_centrelines(verbose=True)
