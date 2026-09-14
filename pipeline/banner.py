"""Generate the README banner from real circuit geometry and the real palette.

Light and dark variants, referenced from the README via <picture>. Counts are
read from the emitted data rather than typed, so the banner cannot drift from
what the site actually contains.
"""
from __future__ import annotations
import json, math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEO  = ROOT / "pipeline" / "vendor" / "f1-circuits.geojson"
DATA = ROOT / "site" / "data"
OUT  = ROOT / "assets"


def oklch_hex(L: float, C: float, H: float) -> str:
    """OKLCH -> sRGB hex. SVG attributes cannot rely on oklch() support."""
    h = math.radians(H); a = C * math.cos(h); b = C * math.sin(h)
    l, m, s = (L + 0.3963377774*a + 0.2158037573*b)**3, \
              (L - 0.1055613458*a - 0.0638541728*b)**3, \
              (L - 0.0894841775*a - 1.2914855480*b)**3
    r  = +4.0767416621*l - 3.3077115913*m + 0.2309699292*s
    g  = -1.2684380046*l + 2.6097574011*m - 0.3413193965*s
    bl = -0.0041960863*l - 0.7034186147*m + 1.7076147010*s
    def enc(u: float) -> int:
        u = max(0.0, min(1.0, u))
        return round((1.055 * u**(1/2.4) - 0.055 if u > 0.0031308 else 12.92*u) * 255)
    return "#%02x%02x%02x" % (enc(r), enc(g), enc(bl))

T = {"ink": oklch_hex(.13,0,0), "text": oklch_hex(.22,0,0), "muted": oklch_hex(.46,0,0),
     "paper": oklch_hex(.978,0,0), "kinpaku": oklch_hex(.84,.19,80.46),
     "instrument": oklch_hex(.24,0,0), "insttext": oklch_hex(.93,0,0),
     "instmuted": oklch_hex(.68,0,0)}

PICK = [("it-1922","Monza"),("be-1925","Spa"),("mc-1929","Monaco"),("gb-1948","Silverstone"),
        ("jp-1962","Suzuka"),("br-1940","Interlagos"),("nl-1948","Zandvoort"),("us-2012","Austin")]
W, H, PAD = 1200, 344, 52
CELL = (W - 2*PAD) / len(PICK)
SHAPE_TOP, SHAPE_H = 48, 102
LABEL_Y, RULE_Y, MAST_Y = SHAPE_TOP + SHAPE_H + 20, 220, 276
F = "'Helvetica Neue',Helvetica,Arial,sans-serif"

feats = {f["properties"]["id"]: f for f in json.loads(GEO.read_text())["features"]}
counts = json.loads((DATA / "meta.json").read_text())["counts"]
STATS = [("SEASONS", f"{counts['seasons']:,}"), ("RACES", f"{counts['races']:,}"),
         ("CIRCUITS", f"{counts['circuits']:,}"), ("CONSTRUCTORS", f"{counts['constructors']:,}")]


def path_for(fid, cx, cy, maxw, maxh):
    co = feats[fid]["geometry"]["coordinates"]
    k = math.cos(math.radians(sum(c[1] for c in co) / len(co)))
    pts = [(c[0]*k, c[1]) for c in co]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    s = min(maxw/(max(xs)-min(xs)), maxh/(max(ys)-min(ys)))
    ox, oy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
    d = "".join(f"{'M' if i==0 else 'L'}{cx+(x-ox)*s:.1f} {cy-(y-oy)*s:.1f}"
                for i, (x, y) in enumerate(pts))
    return d + ("" if co[0] == co[-1] else "Z"), cx+(pts[0][0]-ox)*s, cy-(pts[0][1]-oy)*s


def build(dark: bool) -> str:
    bg   = T["instrument"] if dark else T["paper"]
    line = T["insttext"]   if dark else T["text"]
    mute = T["instmuted"]  if dark else T["muted"]
    word = T["insttext"]   if dark else T["ink"]
    rule, ruleop = ("#ffffff", "0.12") if dark else (T["ink"], "0.10")
    names = ", ".join(n for _, n in PICK)
    s = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'role="img" aria-label="F1 Analysis. Every race, circuit and team in Formula 1, one '
         f'permanent page each. Outlines of eight circuits: {names}. '
         + ", ".join(f"{v} {l.lower()}" for l, v in STATS) + '.">',
         f'<rect width="{W}" height="{H}" rx="10" fill="{bg}"/>',
         f'<text x="{PAD}" y="31" font-family="{F}" font-size="10" letter-spacing="2.2" '
         f'fill="{mute}">EIGHT CIRCUITS · NORTH UP · GOLD MARKS START–FINISH</text>']
    for i, (fid, label) in enumerate(PICK):
        cx, cy = PAD + CELL*i + CELL/2, SHAPE_TOP + SHAPE_H/2
        d, sx, sy = path_for(fid, cx, cy, CELL-30, SHAPE_H-10)
        s += [f'<path d="{d}" fill="none" stroke="{line}" stroke-width="1.5" '
              f'stroke-linejoin="round" stroke-linecap="round" opacity="0.92"/>',
              f'<circle cx="{sx:.1f}" cy="{sy:.1f}" r="2.7" fill="{T["kinpaku"]}"/>',
              f'<text x="{cx:.1f}" y="{LABEL_Y}" text-anchor="middle" font-family="{F}" '
              f'font-size="9.5" letter-spacing="1.5" fill="{mute}">{label.upper()}</text>']
    s.append(f'<line x1="{PAD}" y1="{RULE_Y}" x2="{W-PAD}" y2="{RULE_Y}" stroke="{rule}" '
             f'stroke-opacity="{ruleop}" stroke-width="1"/>')
    s += [f'<text x="{PAD}" y="{MAST_Y}" font-family="{F}" font-size="44" font-weight="200" '
          f'letter-spacing="6" fill="{word}">F1 ANALYSIS</text>',
          f'<text x="{PAD}" y="{MAST_Y+28}" font-family="{F}" font-size="13" fill="{mute}">'
          f'Every race, circuit and team in Formula 1 — one permanent page each.</text>']
    for j, (lbl, val) in enumerate(STATS):
        x = W - PAD - (len(STATS)-1-j)*124
        s += [f'<text x="{x}" y="{MAST_Y-14}" text-anchor="end" font-family="{F}" font-size="9" '
              f'letter-spacing="1.6" fill="{mute}">{lbl}</text>',
              f'<text x="{x}" y="{MAST_Y+9}" text-anchor="end" font-family="{F}" font-size="19" '
              f'font-weight="300" fill="{word}">{val}</text>']
    return "\n".join(s + ["</svg>"])


OUT.mkdir(exist_ok=True)
for dark, name in ((False, "banner-light.svg"), (True, "banner-dark.svg")):
    (OUT / name).write_text(build(dark))
    print(f"  assets/{name}")
print("  stats:", ", ".join(f"{l.lower()} {v}" for l, v in STATS))
