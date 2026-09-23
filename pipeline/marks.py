"""The constructors' marks, and the championship's own.

None of the data sources publish these. F1DB ships circuit diagrams and no team
imagery; OpenF1 gives a team colour and nothing else. So unlike the sibling NFL
project — where the data itself carried the addresses — these are sourced here,
and where they come from is written down rather than implied.

**The constructors' marks** come from Formula 1's own media library, which
publishes each one at 96x96 in three treatments: `logo` in the team's colours,
`logoblack` for a light ground and `logowhite` for a dark one. The black one is
taken: every surface that names a team on this site is paper.

They arrive padded into a square, and the padding is not even: the ink fills the
full width of every one of them but its **height ranges from 0.23 to 0.83 of the
canvas, a 3.6x spread** — the same fault the sibling NFL project found in its
club marks. Drawn into a fixed box, Aston Martin's wings would read as a sliver
beside Ferrari's shield. So each is asked for trimmed to its ink and scaled to a
common height, which the media library will do on request: `e_trim` cuts the
padding and `c_fit,h_96` sets the height. The width is then whatever the mark's
own proportions make it, which is how a mark sits beside a word in print.

The trim happens where the original is held, so nothing is upscaled locally. The
ceiling is still the 96px the library stores: the flattest mark carries only 22
pixels of ink, so marks are drawn small — around the height of the text they sit
beside — and none of them is asked to be a picture.

**The championship's mark** is the F1 wordmark, from the same ESPN CDN the
sibling project takes the NFL shield from. Trimmed to its ink, because it
arrives as a wide mark adrift in a 500x500 transparent square.

All of these are trademarks — of the constructors, and of Formula One Licensing
BV. No licence covers them and none is claimed. They are reproduced to say which
team is which, and whose sport this is about, on a site that states on its face
that it is unofficial and unaffiliated. See /credits/.

Pillow is needed only to trim the wordmark, which is why this is a one-off step
rather than part of `make data` — the rest of the pipeline stays dependency-free.

    python3 pipeline/marks.py
"""
from __future__ import annotations

import io
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache" / "marks"
OUT = ROOT / "site" / "public" / "marks"

UA = {"User-Agent": "f1-analysis/0.1 (personal project; github.com/DavidJCrawford)"}

# Our constructor id -> the slug Formula 1's media library files it under.
TEAMS = {
    "alpine": "alpine",
    "aston-martin": "astonmartin",
    "audi": "audi",
    "cadillac": "cadillac",
    "ferrari": "ferrari",
    "haas": "haasf1team",
    "mclaren": "mclaren",
    "mercedes": "mercedes",
    "racing-bulls": "racingbulls",
    "red-bull": "redbullracing",
    "williams": "williams",
}
F1_MEDIA_BASE = "https://media.formula1.com/image/upload"
F1_MEDIA_PATH = "v1740000001/common/f1/2026"
WORDMARK = "https://a.espncdn.com/i/teamlogos/leagues/500/f1.png"


def fetch(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()


# Trim the padding, then set a common height. Width follows the mark's own
# proportions — see the note above on why a fixed square will not do.
TRIM = "e_trim/c_fit,h_96"


def teams() -> int:
    """Both monochrome treatments, trimmed to ink and normalised for height."""
    got = 0
    # Only the treatment that is used. `logowhite` is published alongside and
    # would be the one for a dark ground — the replay's instrument panel is the
    # only dark surface here and it distinguishes cars by the team's own colour
    # already, so a mark there would crowd a chip to repeat what it says. Add
    # "white" below if a dark surface ever wants one.
    for tone, folder in (("black", OUT),):
        folder.mkdir(parents=True, exist_ok=True)
        for cid, slug in TEAMS.items():
            dest = folder / f"{cid}.webp"
            if dest.exists() and dest.stat().st_size:
                got += 1
                continue
            try:
                dest.write_bytes(fetch(
                    f"{F1_MEDIA_BASE}/{TRIM}/q_auto/{F1_MEDIA_PATH}/{slug}/2026{slug}logo{tone}.webp"))
                got += 1
            except Exception as e:
                print(f"  {cid} ({tone}): {e}")
    # Each mark's shape, so a page can reserve the right box before the image
    # lands. Only the current grid is published; widen the scope and the rest
    # have no mark, and a page has to know that rather than link at nothing.
    import json
    have = {}
    for cid in TEAMS:
        f = OUT / f"{cid}.webp"
        if not f.exists():
            continue
        try:
            from PIL import Image
            with Image.open(f) as im:
                have[cid] = list(im.size)
        except Exception:
            have[cid] = [96, 96]
    (ROOT / "site" / "data" / "marks.json").write_text(
        json.dumps(have, indent=1, sort_keys=True) + "\n")
    total = sum(p.stat().st_size for p in OUT.rglob("*.webp"))
    print(f"  {got} constructor marks for {len(have)} teams, {total / 1024:.0f} KB in all")
    return got


def wordmark() -> int:
    """The F1 wordmark, trimmed to its ink and set on the site's own ground.

    It arrives 500x500 with the mark 454x114 in the middle of it, so nine tenths
    of the file is empty and any box it is put in is mostly padding.
    """
    dest = OUT / "f1.webp"
    if dest.exists() and dest.stat().st_size:
        print("  wordmark already cut")
        return 1
    try:
        from PIL import Image
    except ImportError:
        print("  wordmark needs Pillow: pip install pillow")
        return 0
    CACHE.mkdir(parents=True, exist_ok=True)
    raw = CACHE / "f1.png"
    if not raw.exists():
        raw.write_bytes(fetch(WORDMARK))
    im = Image.open(io.BytesIO(raw.read_bytes())).convert("RGBA")
    box = im.split()[3].getbbox()
    if not box:
        print("  wordmark is empty")
        return 0
    im = im.crop(box)
    h = 56
    im = im.resize((round(im.width * h / im.height), h), Image.LANCZOS)
    OUT.mkdir(parents=True, exist_ok=True)
    im.save(dest, "WEBP", quality=92, method=6)
    print(f"  wordmark {im.width}x{im.height}, {dest.stat().st_size / 1024:.1f} KB")
    return 1


def main() -> int:
    print("marks")
    n = teams()
    wordmark()
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
