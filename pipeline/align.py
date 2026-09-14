"""Geo-reference the TUMFTM centrelines.

TUMFTM ships each circuit in an undocumented local metric frame — no origin, no
orientation, no stated handedness. bacinger traces the same circuits in
latitude/longitude. Both are metric once bacinger is projected, so the two are
related by a rigid transform: a rotation, a translation, and possibly a
reflection, with the traces starting at different points on the loop.

Solving it point-by-point is a registration problem with no known
correspondence. Curvature-against-arc-length sidesteps that: it is invariant
under rotation and translation, so the correspondence reduces to a cyclic shift
(plus a possible direction flip), recoverable by circular cross-correlation.
Once the traces are corresponded, Kabsch gives the rotation in closed form and
the residual says whether to believe any of it.

Output is the arc-length position of each circuit's OSM start/finish line on
its TUMFTM trace, cached so the expensive search runs only when geometry
changes.
"""
from __future__ import annotations
import json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from geo import _tumftm, _bacinger, _start_finish, scales, VENDOR, DATA  # noqa: E402

COARSE, FINE = 180, 720
MAX_RMS = 60.0          # m — beyond this the alignment is not believable


def resample(pts, n):
    seg = [math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    total = sum(seg)
    out, step = [], total / n
    acc, i, target = 0.0, 0, 0.0
    for _ in range(n):
        while i < len(seg) and acc + seg[i] < target:
            acc += seg[i]; i += 1
        if i >= len(seg):
            out.append(pts[-1]); continue
        t = (target - acc) / seg[i] if seg[i] else 0.0
        a, b = pts[i], pts[(i + 1) % len(pts)]
        out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
        target += step
    return out


def curvature(pts):
    n, out = len(pts), []
    for i in range(n):
        (x0, y0), (x1, y1), (x2, y2) = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        a = math.dist((x0, y0), (x1, y1)); b = math.dist((x1, y1), (x2, y2))
        c = math.dist((x0, y0), (x2, y2))
        cross = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
        out.append(0.0 if a * b * c == 0 else 2 * cross / (a * b * c))
    return out


def zscore(v):
    m = sum(v) / len(v)
    sd = (sum((x - m) ** 2 for x in v) / len(v)) ** 0.5 or 1.0
    return [(x - m) / sd for x in v]


def best_shift(sig_a, sig_b, window=None):
    """Circular cross-correlation. Returns (shift, flipped, score)."""
    n = len(sig_a)
    cands = range(n) if window is None else window
    best = (0, False, -1e18)
    for flip in (False, True):
        # A reversed traversal reverses arc length AND negates signed curvature.
        b = [-x for x in reversed(sig_b)] if flip else sig_b
        for s in cands:
            score = sum(sig_a[i] * b[(i + s) % n] for i in range(n))
            if score > best[2]:
                best = (s, flip, score)
    return best


def kabsch(a, b):
    """Optimal 2D rotation taking b onto a. Returns (theta, rms, centroid_a, centroid_b)."""
    ca = (sum(p[0] for p in a) / len(a), sum(p[1] for p in a) / len(a))
    cb = (sum(p[0] for p in b) / len(b), sum(p[1] for p in b) / len(b))
    A = [(p[0] - ca[0], p[1] - ca[1]) for p in a]
    B = [(p[0] - cb[0], p[1] - cb[1]) for p in b]
    num = sum(B[i][0] * A[i][1] - B[i][1] * A[i][0] for i in range(len(A)))
    den = sum(B[i][0] * A[i][0] + B[i][1] * A[i][1] for i in range(len(A)))
    th = math.atan2(num, den)
    cos, sin = math.cos(th), math.sin(th)
    rms = (sum((A[i][0] - (B[i][0] * cos - B[i][1] * sin)) ** 2
               + (A[i][1] - (B[i][0] * sin + B[i][1] * cos)) ** 2
               for i in range(len(A))) / len(A)) ** 0.5
    return th, rms, ca, cb


def arc_fraction(pts, target):
    """Where `target` falls along a closed polyline, as a fraction of its length."""
    seg = [math.dist(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]
    total, acc, best = sum(seg), 0.0, (1e18, 0.0)
    for i in range(len(pts)):
        ax, ay = pts[i]; bx, by = pts[(i + 1) % len(pts)]
        vx, vy = bx - ax, by - ay
        l2 = vx * vx + vy * vy
        t = 0.0 if not l2 else max(0.0, min(1.0, ((target[0] - ax) * vx + (target[1] - ay) * vy) / l2))
        qx, qy = ax + vx * t, ay + vy * t
        d2 = (target[0] - qx) ** 2 + (target[1] - qy) ** 2
        if d2 < best[0]:
            best = (d2, (acc + seg[i] * t) / total)
        acc += seg[i]
    return best[1], math.sqrt(best[0])


def main() -> None:
    tum, bac_raw = _tumftm(apply_alignment=False), _bacinger()
    starts = _start_finish()
    circuits = {c["id"]: c for c in json.loads((DATA / "circuits.json").read_text())}

    # bacinger keyed by circuit, choosing the candidate whose length fits best
    bac = {}
    for f in bac_raw.values():
        L = sum(math.dist(f["pts"][i], f["pts"][(i + 1) % len(f["pts"])]) for i in range(len(f["pts"])))
        for cid in f["candidates"]:
            rec = circuits.get(cid, {}).get("length")
            if not rec:
                continue
            e = abs(L - rec * 1000) / (rec * 1000)
            if e < 0.03 and (cid not in bac or e < bac[cid][1]):
                bac[cid] = (f, e)

    out, rows = {}, []
    for cid in sorted(set(tum) & set(bac)):
        if cid not in starts:
            continue
        tpts = tum[cid]["pts"]
        feat = bac[cid][0]
        bpts = feat["pts"]

        # bacinger's frame: metres east/north about the trace centroid.
        co_lat = feat.get("lat0"); co_lon = feat.get("lon0")
        if co_lat is None:
            continue

        a = resample(bpts, COARSE); b = resample(tpts, COARSE)
        sa, sb = zscore(curvature(a)), zscore(curvature(b))
        s0, flip0, _ = best_shift(sa, sb)

        af = resample(bpts, FINE); bf = resample(tpts, FINE)
        saf, sbf = zscore(curvature(af)), zscore(curvature(bf))
        centre = int(round(s0 * FINE / COARSE))
        win = [(centre + d) % FINE for d in range(-12, 13)]
        s1, flip1, _ = best_shift(saf, sbf, win)
        if flip1 != flip0:
            flip1 = flip0

        bb = list(reversed(bf)) if flip1 else bf
        corr = [bb[(i + s1) % FINE] for i in range(FINE)]
        theta, rms, ca, cb = kabsch(af, corr)

        sf = starts[cid]
        kx, ky = scales(co_lat)
        tgt = ((sf["lon"] - co_lon) * kx, (sf["lat"] - co_lat) * ky)
        b_frac, snap_err = arc_fraction(bpts, tgt)

        # af[i] corresponds to bb[(i + s1) % FINE]. Carry the fraction across in
        # that direction, then undo the reversal to land back in TUMFTM's own order.
        j = (b_frac + s1 / FINE) % 1.0
        t_frac = (1.0 - j) % 1.0 if flip1 else j

        # End-to-end check: take the point this lands on in TUMFTM, push it through
        # the solved transform, and measure how far it is from the OSM node. This
        # tests the correspondence, the rotation and the fraction mapping together —
        # the residual RMS alone would not catch a sign error in the mapping.
        tp = resample(tpts, FINE)[int(t_frac * FINE) % FINE]
        cos, sin = math.cos(theta), math.sin(theta)
        vx, vy = tp[0] - cb[0], tp[1] - cb[1]
        mapped = (ca[0] + vx * cos - vy * sin, ca[1] + vx * sin + vy * cos)
        check = math.dist(mapped, tgt)

        ok = rms <= MAX_RMS and check <= 120.0
        rows.append((cid, rms, flip1, check, ok))
        if ok:
            out[cid] = {"fraction": round(t_frac, 6), "rmsError": round(rms, 1),
                        "reversed": flip1, "checkError": round(check, 1),
                        "rotationDeg": round(math.degrees(theta) % 360, 2),
                        "osmNodeId": sf.get("osmNodeId")}

    (VENDOR / "tumftm-start-finish.json").write_text(json.dumps(out, indent=1, sort_keys=True))
    print(f"{'circuit':22} {'shape fit':>10} {'reversed':>9} {'start/finish check':>19}  verdict")
    for cid, rms, flip, check, ok in rows:
        print(f"{cid:22} {rms:9.1f}m {str(flip):>9} {check:18.1f}m  {'accepted' if ok else 'REJECTED'}")
    print(f"\n{len(out)}/{len(rows)} alignments accepted (RMS <= {MAX_RMS:.0f} m)")


if __name__ == "__main__":
    main()
