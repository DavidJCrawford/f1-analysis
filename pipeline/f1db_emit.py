"""Emit stage — F1DB CSV -> canonical JSON for the site.

Phase 1 (archival tier) subset: entities, races and results. No telemetry.
Reads an unpacked f1db-csv release; writes site/data/.

Canonical serialisation (sorted keys, tight separators, no ASCII escaping) so an
unchanged rebuild is byte-identical and git shows no diff. See
Docs/knowledge/engineering/build-and-release.md.
"""
from __future__ import annotations
import csv, json, sys, hashlib
from pathlib import Path
from collections import defaultdict

SRC = Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/f1db")
OUT = Path(__file__).resolve().parent.parent / "site" / "data"


def read(name: str) -> list[dict]:
    with (SRC / f"f1db-{name}.csv").open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def num(v, cast=int):
    if v in (None, "", "NULL"):
        return None
    try:
        return cast(v)
    except ValueError:
        return None


def write(rel: str, obj) -> int:
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    p.write_text(text, encoding="utf-8")
    return len(text.encode())


def tier(year: int) -> str:
    if year <= 1995: return "archival"
    if year <= 2017: return "timing"
    if year <= 2022: return "telemetry"
    return "modern"


countries = {c["id"]: c["name"] for c in read("countries")}
gp = {g["id"]: g for g in read("grands-prix")}

# ── circuits ────────────────────────────────────────────────────────────────
circuits = [{
    "id": c["id"], "name": c["name"], "fullName": c["fullName"],
    "place": c["placeName"], "country": countries.get(c["countryId"], c["countryId"]),
    "countryId": c["countryId"], "type": c["type"], "direction": c["direction"],
    "lat": num(c["latitude"], float), "lon": num(c["longitude"], float),
    "length": num(c["length"], float), "turns": num(c["turns"]),
    "racesHeld": num(c["totalRacesHeld"]),
} for c in read("circuits")]

# ── constructors ────────────────────────────────────────────────────────────
constructors = [{
    "id": c["id"], "name": c["name"], "fullName": c["fullName"],
    "country": countries.get(c["countryId"], c["countryId"]),
    "entries": num(c["totalRaceEntries"]), "starts": num(c["totalRaceStarts"]),
    "wins": num(c["totalRaceWins"]), "podiums": num(c["totalPodiums"]),
    "poles": num(c["totalPolePositions"]), "titles": num(c["totalChampionshipWins"]),
    "points": num(c["totalChampionshipPoints"], float),
    "bestChampionshipPosition": num(c["bestChampionshipPosition"]),
} for c in read("constructors")]

# ── drivers (slim) ──────────────────────────────────────────────────────────
drivers = [{
    "id": d["id"], "name": d["name"], "abbr": d["abbreviation"] or None,
    "nationality": countries.get(d["nationalityCountryId"], d["nationalityCountryId"]),
} for d in read("drivers")]
dname = {d["id"]: d["name"] for d in drivers}
cname = {c["id"]: c["name"] for c in constructors}

# ── races ───────────────────────────────────────────────────────────────────
races_raw = read("races")
races = [{
    "id": num(r["id"]), "year": num(r["year"]), "round": num(r["round"]),
    "date": r["date"], "grandPrixId": r["grandPrixId"],
    "name": gp.get(r["grandPrixId"], {}).get("fullName") or r["officialName"],
    "shortName": gp.get(r["grandPrixId"], {}).get("name") or r["grandPrixId"],
    "officialName": r["officialName"],
    "circuitId": r["circuitId"], "circuitLayoutId": r["circuitLayoutId"],
    "courseLength": num(r["courseLength"], float), "turns": num(r["turns"]),
    "laps": num(r["laps"]), "distance": num(r["distance"], float),
    "tier": tier(num(r["year"])),
} for r in races_raw]
by_year_races = defaultdict(list)
for r in races:
    by_year_races[r["year"]].append(r)

# ── results, grouped by season ──────────────────────────────────────────────
res_by_year = defaultdict(lambda: defaultdict(list))
for x in read("races-race-results"):
    y, rd = num(x["year"]), num(x["round"])
    res_by_year[y][rd].append({
        "pos": x["positionText"], "posNum": num(x["positionNumber"]),
        "no": x["driverNumber"], "driverId": x["driverId"], "driver": dname.get(x["driverId"], x["driverId"]),
        "constructorId": x["constructorId"], "constructor": cname.get(x["constructorId"], x["constructorId"]),
        "laps": num(x["laps"]), "time": x["time"] or None, "gap": x["gap"] or None,
        "reasonRetired": x["reasonRetired"] or None,
        "grid": num(x["gridPositionNumber"]), "points": num(x["points"], float),
        "sharedCar": x["sharedCar"] == "true",
    })

# ── standings ───────────────────────────────────────────────────────────────
ds, cs = defaultdict(list), defaultdict(list)
for s in read("seasons-driver-standings"):
    ds[num(s["year"])].append({"pos": s["positionText"], "driverId": s["driverId"],
                               "driver": dname.get(s["driverId"], s["driverId"]),
                               "points": num(s["points"], float), "champion": s["championshipWon"] == "true"})
for s in read("seasons-constructor-standings"):
    cs[num(s["year"])].append({"pos": s["positionText"], "constructorId": s["constructorId"],
                               "constructor": cname.get(s["constructorId"], s["constructorId"]),
                               "points": num(s["points"], float), "champion": s["championshipWon"] == "true"})

# ── seasons index ───────────────────────────────────────────────────────────
seasons = []
for row in read("seasons"):
    y = num(row["year"])
    dc = next((d for d in ds[y] if d["champion"]), None)
    cc = next((c for c in cs[y] if c["champion"]), None)
    seasons.append({"year": y, "races": len(by_year_races[y]), "tier": tier(y),
                    "championDriver": dc["driver"] if dc else None,
                    "championDriverId": dc["driverId"] if dc else None,
                    "championConstructor": cc["constructor"] if cc else None,
                    "championConstructorId": cc["constructorId"] if cc else None})

# ── write ───────────────────────────────────────────────────────────────────
release = (SRC / ".release").read_text().strip() if (SRC / ".release").exists() else "unknown"
total = 0
total += write("circuits.json", sorted(circuits, key=lambda c: c["name"]))
total += write("constructors.json", sorted(constructors, key=lambda c: -(c["entries"] or 0)))
total += write("drivers.json", drivers)
total += write("seasons.json", seasons)
total += write("races.json", races)
for y in sorted(by_year_races):
    total += write(f"seasons/{y}.json", {
        "year": y, "tier": tier(y),
        "races": sorted(by_year_races[y], key=lambda r: r["round"]),
        "driverStandings": ds[y], "constructorStandings": cs[y],
        "results": {str(k): v for k, v in res_by_year[y].items()},
    })

meta = {
    "spineRelease": release, "source": "F1DB (CC BY 4.0)",
    "counts": {"seasons": len(seasons), "races": len(races), "circuits": len(circuits),
               "constructors": len(constructors), "drivers": len(drivers),
               "results": sum(len(v) for y in res_by_year.values() for v in y.values())},
    "tiers": {t: sum(1 for r in races if r["tier"] == t) for t in ("archival", "timing", "telemetry", "modern")},
    # Latest event actually covered - not the last scheduled race. A future
    # fixture on the calendar is not data.
    "dataAsOf": max((r["date"] for r in races
                     if r["date"] and res_by_year[r["year"]].get(r["round"])), default=None),
    "scheduledThrough": max(r["date"] for r in races if r["date"]),
}
total += write("meta.json", meta)
print(json.dumps(meta, indent=2))
print(f"\n{total/1024/1024:.2f} MB across {sum(1 for _ in OUT.rglob('*.json'))} files -> {OUT}")
