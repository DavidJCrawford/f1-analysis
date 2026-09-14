---
type: Dataset
title: Elevation and DEM Sources
description: Free elevation data for circuit terrain — Copernicus GLO-30 tile paths and withheld tiles, terrarium decode formulas, national LiDAR, the datum problem, and why none of it belongs on the track surface.
resource: https://copernicus-dem-30m.s3.amazonaws.com/
tags: [dem, elevation, copernicus, terrarium, lidar, datum, 3d]
generated:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
verified:
  by: claude-code/opus-5
  at: '2026-09-14T00:00:00Z'
sources:
  - id: copernicus_aws
    resource: https://registry.opendata.aws/copernicus-dem/
    title: Copernicus DEM on the AWS Registry of Open Data
  - id: copernicus_handbook
    resource: https://dataspace.copernicus.eu/sites/default/files/media/files/2024-06/geo1988-copernicusdem-spe-002_producthandbook_i5.0.pdf
    title: Copernicus DEM Product Handbook (issue 5.0)
  - id: copernicus_gee
    resource: https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_DEM_GLO30_2024_1
    title: Copernicus GLO-30 catalogue entry (attribution string)
  - id: joerd_formats
    resource: https://github.com/tilezen/joerd/blob/master/docs/formats.md
    title: Tilezen joerd — terrarium and other tile formats
  - id: joerd_attribution
    resource: https://github.com/tilezen/joerd/blob/master/docs/attribution.md
    title: Tilezen joerd — per-source attribution requirements
  - id: opentopodata
    resource: https://api.opentopodata.org/datasets
    title: OpenTopoData dataset list and public-instance limits
  - id: usgs_3dep
    resource: https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer
    title: USGS 3DEP Elevation ImageServer
  - id: ea_lidar
    resource: https://www.data.gov.uk/dataset/b1ff0a9c-74d3-4b97-a3fb-c8ab39ef6152/lidar-composite-dtm-2020-1m
    title: Environment Agency LIDAR Composite DTM 1 m
  - id: ahn4
    resource: https://developers.google.com/earth-engine/datasets/catalog/AHN_AHN4
    title: AHN4 0.5 m DSM/DTM (Netherlands)
status: stable
---

# Elevation and DEM Sources

## The principle that decides everything else

**For the road surface, use telemetry Z. For terrain around the circuit, use a DEM.**

A 30 m DEM cell is wider than a 12–18 m race track. Sampling one at the centreline
tells you about the field next to the circuit, not the tarmac. Telemetry Z resolves
0.1 m and follows the actual road.

Evidence that telemetry Z is genuine orthometric elevation, not a scaled or synthetic
value — Spa 2024, OpenF1 `session_key=9574`, car 1, a two-minute window of 465 samples:

| Measure | Value |
| --- | --- |
| Raw `z` range | 3655 → 4678 (units of 1/10 m) |
| Metres | **365.5 m → 467.8 m**, a 102.3 m span |
| Distinct `z` values | 358 of 465 samples — not quantised to a plane |
| Spa's published elevation change | ~100 m |

And a stronger cross-check: sampling EU-DEM 25 m at all 153 vertices of the Spa
centreline gives min 364.7 m, max 471.9 m, range 107.1 m. The **absolute** floor agrees
with telemetry Z to 0.8 m and the ceiling to 4.1 m. So Z is real elevation with
essentially no offset at that venue, not merely a correctly-scaled relative profile.

A caveat that survives: the vertical **datum** of the F1 Z channel is undocumented.
Where a DEM is joined to telemetry Z, solve for a constant offset by least-squares over
the whole lap rather than assuming a shared datum. Three different datums are in play
across the sources below — EGM2008, NAVD 88 and Ordnance Datum Newlyn — so any
cross-source elevation join needs explicit datum handling.

## Copernicus GLO-30 — the default global DEM

| Fact | Value |
| --- | --- |
| Resolution | 30 m |
| Type | **Digital SURFACE model** — includes buildings, grandstands and vegetation |
| Source | TanDEM-X, acquired 2011–2015 |
| Vertical datum | EGM2008 orthometric (EPSG:3855) |
| Horizontal | WGS84-G1150 (EPSG:4326) |
| Absolute vertical accuracy | **< 4 m LE90** |
| Height error mask (HEM) std dev | 0.09 – 43.4 m globally |
| Access | AWS S3, no key, not requester-pays; COG, so `Accept-Ranges: bytes` |

Tile URL pattern:

```
https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_{NS}{lat:02d}_00_{EW}{lon:03d}_00_DEM/Copernicus_DSM_COG_10_{NS}{lat:02d}_00_{EW}{lon:03d}_00_DEM.tif
```

Silverstone (52.07 N, 1.01 W → **N52 / W002**):

```
https://copernicus-dem-30m.s3.amazonaws.com/Copernicus_DSM_COG_10_N52_00_W002_00_DEM/Copernicus_DSM_COG_10_N52_00_W002_00_DEM.tif
```

The lat/lon in the name is the **south-west corner** of a 1° × 1° tile, so a point at
longitude −1.01 needs `W002`, not `W001`. Each tile directory also holds AUXFILES: EDM
(edit data mask), FLM (filling mask), HEM (height error mask), WBM (water body mask) and
`ACM.kml`.

### Three gotchas

**1. The path is deterministic in form, not in availability.** The AWS Registry entry
states that "GLO-30 Public provides limited worldwide coverage at 30 meters because a
small subset of tiles covering specific countries are not yet released to the public."
Tested against ten F1 venues:

| Venue | Result |
| --- | --- |
| Silverstone, Spa, Monaco, Bahrain, Monza, Yas Marina, Interlagos, Jeddah, Losail | HTTP 200 |
| **Baku** (`N40_E049`) | **HTTP 404** |

Code that computes a tile name and fetches it will simply break on Azerbaijan. Always
handle the 404 and fall back.

**2. The COG carries no vertical CRS.** Range-fetching the first 200 KB of the
Silverstone tile shows the only CRS string in the GeoTIFF header is `WGS 84`.
EPSG:3855 / EGM2008 is documentation-only: GDAL and rasterio report a 2D CRS and will
not warn that the heights are geoid-referenced rather than ellipsoidal.

**3. It is a DSM, not a DTM.** The filename says `Copernicus_DSM_`. Buildings,
grandstands and trees are baked into the "terrain".

Taken together: **GLO-30 is for distant terrain only.** It is never sampled for the
track surface, and it cannot resolve banking.

Required attribution:

```
© DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018 provided under
COPERNICUS by the European Union and ESA; all rights reserved
```

## Tilezen terrarium tiles — for a browser terrain mesh

```
https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png
```

Verified HTTP 200 at z12–z15 and **404 at z16** — z15 is the maximum. Primary bucket
`elevation-tiles-prod` (us-east-1); EU replica `elevation-tiles-prod-eu`
(eu-central-1). Managed by Mapzen, a Linux Foundation project, listed on the AWS
Registry of Open Data. No key, no attribution token.

**Decode (terrarium):**

```js
elevation_m = (red * 256 + green + blue / 256) - 32768
```

**Do not confuse this with Mapbox Terrain-RGB v1**, which is a different encoding
entirely:

```js
elevation_m = -10000 + ((R * 256 * 256 + G * 256 + B) * 0.1)
```

Mapbox uses 0.1 m increments on a −10000 base; terrarium uses 1/256 m increments on a
−32768 base. Terrain-RGB also requires an access token and attribution and has been
frozen since 2021-12-01 ("elevation data updates will not be applied to the Mapbox
Terrain-RGB tileset"). It is not used here.

Other formats in the same bucket: `normal/{z}/{x}/{y}.png`,
`geotiff/{z}/{x}/{y}.tif` (512 px with internal 256 pyramiding), and
`skadi/{N|S}{lat}/{N|S}{lat}{E|W}{lon}.hgt.gz` (1° × 1° unprojected WGS84).

### Measured tile sizes and resolution

At Silverstone (52.0786 N, 1.0153 W):

| Zoom | Bytes |
| ---: | ---: |
| z12 | 100,797 |
| z13 | 85,084 |
| z14 | 54,689 |
| z15 | 27,310 |
| z16 | 404 (not served) |

Ground resolution at 256 px tiles is `r = 156543.03392 · cos(lat) / 2^z`:

| Circuit | Latitude | z14 | z15 |
| --- | ---: | ---: | ---: |
| Silverstone | 52.00 | 5.88 m/px | **2.94 m/px** |
| Spa | 50.43 | 6.09 m/px | 3.04 m/px |
| Monza | 45.62 | 6.68 m/px | 3.34 m/px |
| Bahrain | 25.99 | 8.59 m/px | 4.29 m/px |

That is **tile** resolution, not source-data resolution. The underlying pixels at
Silverstone come from EU-DEM (25 m) or UK Environment Agency data, so z15 is smoothly
interpolated rather than genuinely 3 m. Decoding `terrarium/15/16291/10812.png` with the
joerd formula gives 155.19 m at Silverstone, which checks out.

### Attribution is a mosaic, and non-trivial

terrarium is assembled from many national sources, and the credits are per-source.
Reproduce the whole list on `/data/`: "Produced using Copernicus data and information
funded by the European Union" (EU-DEM); "© Environment Agency copyright and/or database
right 2015. All rights reserved" (UK); "courtesy of the U.S. Geological Survey"
(3DEP/SRTM/GMTED2010, public domain); "© Commonwealth of Australia (Geoscience
Australia) 2017" (CC BY 4.0); "© Kartverket" (Norway, CC BY 4.0); "© offene Daten
Österreichs – Digitales Geländemodell (DGM) Österreich" (CC BY 3.0 AT); "Contains
information licensed under the Open Government Licence – Canada"; "Source: INEGI,
Continental relief, 2016" (Mexico); "Copyright 2011 Crown copyright (c) Land
Information New Zealand" (CC BY 3.0 NZ); plus the ArcticDEM NSF award text.

## Point-query APIs

Useful for spot checks and for calibrating a datum offset; not for bulk work.

| Service | Endpoint | Notes |
| --- | --- | --- |
| OpenTopoData | `https://api.opentopodata.org/v1/{dataset}?locations=lat,lng\|lat,lng` | Datasets: `aster30m`, `bkg200m`, `emod2018`, `etopo1`, `eudem25m`, `gebco2020`, `mapzen`, `ned10m`, `nzdem8m`, `srtm30m`, `srtm90m`. Public instance limited to **1 call/s, 1000/day** — self-host for bulk |
| Open-Elevation | `https://api.open-elevation.com/api/v1/lookup?locations=52.0786,-1.0153` | Integer metres only; coarse |
| OpenTopography | `/API/globaldem?demtype=COP30&south=…&north=…&west=…&east=…&outputFormat=GTiff` | Returns **HTTP 401** — requires a free API key as of 2026. Do not assume it is open |

OpenTopoData response shape:
`{"results":[{"dataset":"…","elevation":155.45,"location":{…}}],"status":"OK"}`.

SRTM caveats, where it is used as a cross-check: 1 arc-second (~30 m), coverage only
60° N to 56° S (fine for every current F1 venue), a 2000-vintage surface model with
voids.

## National LiDAR — the only route to measured banking

At 0.5–1 m resolution the tarmac cross-section is actually resolved, so elevation can be
sampled at centreline ± half-width along the surface normal and a real banking angle
computed: `theta = atan2(z_left - z_right, w_left + w_right)`. At 30 m that is pure
noise.

| Country | Product | Resolution | Datum | Licence |
| --- | --- | --- | --- | --- |
| USA | USGS **3DEP** | 1 m projects; also 1/3″ and 1″ seamless | NAVD 88 | Public domain |
| England | Environment Agency **LIDAR Composite DTM** | 1 m, >95% coverage, 5 km GeoTIFF tiles on the OS National Grid | Ordnance Datum Newlyn via OSTN'15 | OGL v3 |
| Netherlands | **AHN4** DSM + DTM, 2020–2022 | 0.5 m, ~5 cm vertical accuracy | — | CC0 |

Discovering which 1 m USGS project covers a point (returns JSON immediately, no key):

```
https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer/identify
  ?geometry={"x":-97.6398,"y":30.1328,"spatialReference":{"wkid":4326}}
  &geometryType=esriGeometryPoint&returnGeometry=false&f=json
```

At COTA Turn 1 this returns `"155.089"` and names the source tile
`TX_Central_B1_2017` at
`https://prd-tnm.s3.amazonaws.com/StagedProducts/Elevation/1m/Projects/TX_Central_B1_2017/TIFF/USGS_one_meter_x63y334_TX_Central_B1_2017.tif`,
with `VerticalDatum` "North American Vertical Datum of 1988 (NAVD 88)". It also lists
the seamless products (`USGS_13_n31w098.tif`, `USGS_1_n31w098.tif`). WMS and WCS are
enabled on the same ImageServer. 3DEP content is current as published 2026-08-24, and a
new Seamless 1 m (S1M) product — 10 km × 10 km COG tiles — has been in production since
mid-2025.

England: downloads at
<https://environment.data.gov.uk/DefraDataDownload/?Mode=survey>; contributing surveys
had ±15 cm RMSE vertical accuracy; an OGC API – Features service exists.

Netherlands: AHN4 is downloadable as 6.5 × 5 km tiles or, faster, via OGC WCS for an
arbitrary area; also served through OpenTopography (`OTSDEM.012026.28992.1`) and Earth
Engine (`AHN/AHN4`). AHN5 is in progress.

### Coverage reality check

Covered: **Silverstone, Zandvoort, COTA, Miami, Las Vegas, Indianapolis.**

Not covered: **Spa, Monza, Monaco, Suzuka, Bahrain, Jeddah, Singapore, Baku, Abu Dhabi,
Qatar, Interlagos, Mexico.**

So LiDAR is a **per-circuit enhancement for a handful of hero circuits**, never a
system-wide solution. Banking for everything else is hand-authored per corner and
labelled as modelled — see [circuit geometry sources](circuit-geometry-sources.md).

## What each source is and is not usable for

| Use | Source | Verdict |
| --- | --- | --- |
| Track surface elevation profile | telemetry Z (2018+) | **Yes** — 0.1 m resolution, follows the tarmac |
| Track surface elevation, pre-2018 | — | **None available.** Archival and Timing tier circuits get no elevation, and the page says so |
| Distant terrain silhouette | GLO-30, terrarium | Yes |
| Terrain mesh in the browser | terrarium z15 | Yes, decoded client- or build-side |
| Banking / camber | 1 m LiDAR at 6 venues | Marginal; hand-authored elsewhere |
| Banking from any 30 m DEM | — | **No.** One cell is wider than the track |
| Absolute height agreement across sources | — | **No** without solving the datum offset |

The elevation exaggeration used in a scene is 1.0 by default, for honesty; 1.5–2.0 reads
better on subtle circuits but must be labelled on the page when used.
