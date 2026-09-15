"""Emit each constructor's own colour for the current season.

F1DB carries no livery colour, but the timing feed does, against a team name of
its own spelling — "Red Bull Racing" where F1DB says "red-bull". Rather than
keep a table of those spellings in step with two sources, the join goes through
the car number, which both sides agree on: the feed gives number -> colour, the
season's results give number -> constructor.

Writes site/data/colours.json, a map of constructor id to hex.

    python3 pipeline/colours.py [year]
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / "openf1" if (ROOT / "openf1").exists() else ROOT / ".cache" / "openf1"
DATA = ROOT / "site" / "data"


def main() -> int:
    year = int(sys.argv[1]) if len(sys.argv) > 1 else None
    seasons = json.loads((DATA / "seasons.json").read_text())
    year = year or max(s["year"] for s in seasons)
    season = json.loads((DATA / "seasons" / f"{year}.json").read_text())

    # number -> constructor, from the results. A driver who changes team
    # mid-season carries their number with them, so count rather than assume.
    by_number: dict[int, collections.Counter] = collections.defaultdict(collections.Counter)
    for rows in season.get("results", {}).values():
        for r in rows:
            if str(r.get("no", "")).isdigit() and r.get("constructorId"):
                by_number[int(r["no"])][r["constructorId"]] += 1

    # number -> colour, from the timing feed's own driver list for each session.
    votes: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    sessions = 0
    for f in sorted(CACHE.glob("drv_*.json")):
        try:
            rows = json.loads(f.read_text())
        except (OSError, ValueError):
            continue
        sessions += 1
        for r in rows:
            n, hexcode = r.get("driver_number"), r.get("team_colour")
            if not n or not hexcode or n not in by_number:
                continue
            cid = by_number[n].most_common(1)[0][0]
            votes[cid]["#" + str(hexcode).lstrip("#").upper()] += 1

    colours = {cid: c.most_common(1)[0][0] for cid, c in sorted(votes.items())}
    if not colours:
        print("no colours found; is the timing-feed cache present?")
        return 1

    out = DATA / "colours.json"
    out.write_text(json.dumps(colours, sort_keys=True, separators=(",", ":")) + "\n")
    print(f"{len(colours)} constructors from {sessions} sessions -> {out.relative_to(ROOT)}")
    for cid, hexcode in colours.items():
        print(f"  {cid:<22} {hexcode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
