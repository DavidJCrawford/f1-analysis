# Vendored geometry

`f1-circuits.geojson` — from [bacinger/f1-circuits](https://github.com/bacinger/f1-circuits),
MIT licence, Copyright (c) 2019-2025 Tomislav Bacinger. 40 circuits as closed
LineStrings in WGS84.

Provenance note: traced from a Google My Maps layer plus Wikipedia and official
F1 sites — **not** OpenStreetMap-derived, so ODbL does not attach. Measured
length error against declared length: Silverstone -0.113%, Monza -0.002%,
Monaco -0.27%, Spa -0.255%.

Vendored rather than fetched so the build is reproducible offline.

## tumftm/

Centrelines from [TUMFTM/racetrack-database](https://github.com/TUMFTM/racetrack-database),
**LGPL-3.0**, Technical University of Munich, Institute of Automotive Technology.

Columns are `x_m, y_m, w_tr_right_m, w_tr_left_m` — a closed centreline in local
metric coordinates at uniform ~5 m spacing, plus track width either side.
Roughly nine times the resolution of the bacinger traces (5.0 m against 44.6 m
mean spacing), which is why it is preferred wherever it covers a circuit.

`MAPPING.json` records the TUMFTM filename to F1DB circuit id crosswalk. Every
match is still validated against the recorded circuit length before use.

**Provenance, and why it matters.** The TUMFTM README states the centrelines
were "fetched as GPS points from the OpenStreetMap project" and then smoothed,
so they "do not lie perfectly in the middle of the track anymore". The licence
chain is therefore LGPL-3.0 over **ODbL** data, not LGPL alone, and ODbL carries
share-alike on derived databases.

Posture, following `Docs/knowledge/policies/data-licensing.md`: attribute
OpenStreetMap contributors prominently, and offer the derived geometry
(`site/data/outlines.json`) under ODbL rather than relying on it counting as a
Produced Work. The accuracy caveat is theirs too — quality "varies greatly
depending on the location", which is what the length-validation gate in
`geo.py` exists to catch.
