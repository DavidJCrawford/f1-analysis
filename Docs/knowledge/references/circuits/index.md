# From coordinates to a circuit

* [Centreline Construction](centreline-construction.md) - How a usable circuit centreline is built from FastF1 position data and from the open geometry repositories — resampling, median aggregation, closure and arc-length parameterisation.
* [Circuit Coordinate Systems](coordinate-systems.md) - The exact unit, scale, orientation and datum conventions of F1 position data, and the verified transform chain from telemetry units to WGS84 and into a three.js scene.
* [OpenStreetMap Circuit Extraction](osm-extraction.md) - Working Overpass QL for raceway geometry, the tags that actually exist at an F1 venue, the multiple-layouts problem, and the ODbL position for a published static site.

# Track features

* [Corner and Sector Detection](corner-and-sector-detection.md) - How corners, marshal sectors, timing sector lines, mini-sectors and DRS zones are located on a circuit centreline, and which of them are actually available per circuit.
* [Banking and Elevation](banking-and-elevation.md) - What the telemetry Z channel actually measures, why banking cannot be derived from any open dataset and must be authored, and the frame the track ribbon is built on.

# Layout identity

* [Circuit Layout Registry](circuit-layout-registry.md) - The hand-verified build artifact that binds a race to a circuit layout and a layout to a piece of geometry across F1DB, MultiViewer, OpenF1, bacinger and TUMFTM identifiers.

