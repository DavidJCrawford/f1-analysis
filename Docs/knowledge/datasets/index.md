# Timing and results

* [FastF1 3.8.3](fastf1.md) - The Python library that parses Formula 1's timing archive into laps, telemetry and results — its object model, exact column names, cache configuration and the 2018 coverage floor.
* [F1DB v2026.14.0](f1db.md) - The CC BY 4.0 bulk dataset covering 1950–2026 that forms this site's redistributable spine — release artifacts, table inventory, the in-repo-only circuit SVGs, and the provenance gap that makes its licence an assumption.
* [jolpica-f1](jolpica-f1.md) - The Ergast successor API covering 1950–2026 — its endpoints, hard limits, CSV dumps, NonCommercial licence, and the status collapse that makes it unsafe for retirement-cause analysis in recent seasons.
* [OpenF1](openf1.md) - The 2023-onward REST API whose 18 endpoints add overtakes, team radio and pit-lane splits that FastF1 lacks — with its free/sponsor tier split, deprecated fields and NonCommercial licence.
* [OpenF1 position coverage in practice](openf1-position-coverage.md) - What the location feed actually holds across a season — placeholder openings, feeds that stop, one race with almost nothing, and the speed channel that reconstructs it to within 17 m.
* [F1 Live-Timing Archive](f1-livetiming-archive.md) - Formula 1's post-session static stream archive — the raw source under FastF1, its exact filenames and measured sizes, its unauthenticated but datacentre-hostile access, and the rights position that caps what may be published.

# Geometry and terrain

* [MultiViewer Circuit API](multiviewer-api.md) - The undocumented endpoint behind FastF1's get_circuit_info() — the best available F1 track centreline, corner distances and pit-loss times, blocked from use on this site until terms are agreed.
* [Circuit Geometry Sources](circuit-geometry-sources.md) - Every usable source of F1 track outlines, centrelines, widths and SVG silhouettes — counts, licences, measured accuracy and provenance, with the gaps each one leaves.
* [Elevation and DEM Sources](elevation-dem.md) - Free elevation data for circuit terrain — Copernicus GLO-30 tile paths and withheld tiles, terrarium decode formulas, national LiDAR, the datum problem, and why none of it belongs on the track surface.

