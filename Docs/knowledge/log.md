# Directory Update Log

## 2026-09-16

* **Added**: [OpenF1 position coverage in practice](datasets/openf1-position-coverage.md) — measured across the 2026 season while building the race replays. Thirteen of fourteen races have no gap over a second; the exceptions fail in three distinct ways, and Monaco holds 6.5 minutes of a 2h 15m race. Records the reconstruction from the `car_data` speed channel, measured at a median 17 m error, and the clock skew between endpoints that presents as a geometry fault.
* **Reassigned**: [source roles](policies/source-roles.md) — OpenF1, MultiViewer and TUMFTM moved out of build-time-only roles to `SPINE`, on the owner's decision that the project will never be commercialised. The document had said the opposite while the site already shipped their data. NonCommercial is satisfied; **share-alike is recorded as unresolved rather than claimed as met**.
* **Corrected**: a Formula 1 circuit has a start line and a finish line and they are usually different places — the finish line opposite race control, the start line at the front of the grid. Drawing one and calling it the start/finish line scattered the grid around it. Carried into [SPEC](../SPEC.md) §6.7 and its appendix, along with the 8 m grid slot, the 50 m resolution limit on telling the two lines apart, and Melbourne, Monaco and Montreal using a single marker.

## 2026-09-14

* **Created**: the bundle, grounding the [F1 Analysis specification](../SPEC.md) in verified research across twelve domains.
* **Added**: [datasets](datasets/index.md) — FastF1, F1DB, jolpica-f1, OpenF1, the F1 live-timing archive, MultiViewer, and the circuit-geometry and elevation sources, each with its coverage window and licence.
* **Added**: [references/domain](references/domain/index.md) — the sport as a domain model: session formats, points systems across every era, tyres, flags, the 2026 regulations, team lineage and championship edge cases.
* **Added**: [references/circuits](references/circuits/index.md) — centreline construction, coordinate systems, corner and sector detection, banking and elevation, and the circuit-layout registry.
* **Added**: [references/joins](references/joins/index.md) — the entity-resolution strategy across five sources that disagree about identifiers.
* **Added**: [metrics](metrics/index.md) — twelve derived measures including [position at corner](metrics/position-at-corner.md), the project's headline capability.
* **Added**: [design](design/index.md) — the token system read directly from the aesthetic reference, plus typography, colour, driver encoding, chart archetypes, 3D art direction and accessibility.
* **Added**: [engineering](engineering/index.md) — site architecture, three.js rendering, the data pipeline, telemetry encoding, platform constraints and performance budgets.
* **Added**: [policies](policies/index.md) — the binding rules, most importantly [source roles](policies/source-roles.md), which keeps non-commercial data out of published artifacts.
* **Added**: [prior-art](prior-art/index.md) — the competitive landscape, nearest neighbours, and the external design canon with its licence position.
* **Corrected**: 83 of roughly 252 first-pass research claims were refuted or amended during adversarial verification before any document was written. Notable corrections carried in: 2026 power units produce ~750 kW total rather than 400 kW; jolpica collapses retirement causes from 2024 rather than 2025; `MeshoptDecoder` is in `addons/libs/`, not `addons/loaders/`; the 1981-1990 points system was 9-6-4-3-2-1; and the FT Visual Vocabulary poster is not freely redistributable.
