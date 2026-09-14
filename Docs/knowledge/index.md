---
okf_version: "0.2"
---

# F1 Analysis knowledge base

The knowledge base for the **F1 Analysis** project — a static, editorial
encyclopaedia of Formula 1 in which every circuit, team and race is a designed
page with real data and a real 3D track.

This bundle is the project's reference material and its evidence base. It is
written in the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format)
v0.2, and it is intended to be *published* as a section of the site rather than
kept internal — every derived number on the site links back to the method
recorded here.

The specification it grounds is [SPEC.md](../SPEC.md).

Findings here were produced by parallel research and then adversarially
fact-checked; where a first-pass claim and a verification disagreed, the
verified value is what appears. See [log.md](log.md) for the change history.

# Subdirectories

* [datasets](datasets/) - Every external data source the project draws on, with its schema, coverage, limits and licence.
* [design](design/) - The visual system: tokens, typography, colour, motion, chart encodings and the 3D art direction.
* [engineering](engineering/) - How the site is built, rendered, measured and shipped.
* [metrics](metrics/) - Every derived measure the site publishes, with its formula, caveats and failure modes.
* [policies](policies/) - Binding rules — what may be redistributed, how things are worded, how motion behaves, how provenance is shown.
* [prior-art](prior-art/) - The existing field, the nearest neighbours, and the external design canon.
* [references](references/) - Domain knowledge: the sport itself, circuit geometry, and the joins between sources.
