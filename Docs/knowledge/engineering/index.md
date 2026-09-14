# The site

* [Site architecture on Astro 7](site-architecture.md) - Why Astro 7 generates this site's ~2,400–6,000 pages, and the routing, hydration, chunking, search and base-path mechanics that follow from that choice.
* [GitHub Pages constraints](github-pages-constraints.md) - Every verified GitHub Pages quota and delivery behaviour, the requests that established them, and what each one forces on the architecture.
* [Performance budgets](performance-budgets.md) - The Core Web Vitals targets, JS and data byte budgets, GPU and canvas limits, and long-task rules that every page on this site is measured against.
* [Build and release](build-and-release.md) - The GitHub Actions deploy workflow, the human-in-the-loop ingest that CI cannot perform, the provisional-data window, and the gates that block a bad publish.

# Rendering

* [three.js track rendering](threejs-track-rendering.md) - The r186-specific facts, geometry construction and animation patterns that produce a correctly-oriented, correctly-banked 3D circuit in the browser.

# Data

* [Data pipeline](data-pipeline.md) - The five-stage Python ingest that turns F1's live-timing archive, jolpica and F1DB into validated, reproducible, incrementally-rebuilt site data.
* [Telemetry encoding](telemetry-encoding.md) - How one race of 20-car position data is quantised, delta-encoded and laid out planar to reach 623 kB at 2 Hz, with every figure marked measured or synthetic.

