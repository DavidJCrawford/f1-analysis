# Entity resolution

* [Entity Resolution Across Five Sources](entity-resolution.md) - The five-source identifier problem — which joins are free, which are hand-built, and how the pipeline enforces that every foreign record resolves to an F1DB id before it can be published.
* [Driver and Team Identifier Joins](drivers-and-teams.md) - How DriverId and TeamId bind FastF1, jolpica and F1DB together, where the punctuation and lineage break the join, and why abbreviations, car numbers and team membership are all season- or session-scoped rather than identities.
* [Circuit Identifier Crosswalk](circuits-crosswalk.md) - How circuit identifiers map across F1DB, FastF1, OpenF1, MultiViewer and the open geometry repositories — and why the layout, not the circuit, is the key that actually has to resolve.
* [Race and Session Identity Joins](sessions-and-races.md) - Binding a race to its sessions across F1DB, jolpica, FastF1 and OpenF1 — why season plus round is not a stable key, how meeting_key and session_key are mapped positionally, and where the 2026 calendar breaks naive schedule alignment.

