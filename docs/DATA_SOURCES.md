# Data sources and provenance

This file is the source register. Every acquired dataset must record its exact
version, URL or distribution method, retrieval date, coverage, license, schema,
and any transformations in this document before entering the pipeline.

## Required core sources

| Source | Role | Status |
| --- | --- | --- |
| IFI-Impacts | Historical flood events and labels | Not acquired |
| IMD gridded rainfall | Historical rainfall features | Not acquired |
| Karnataka district polygons / KGIS | Spatial aggregation unit | Not acquired |
| SRTM | Elevation and slope | Not acquired |

## Optional sources

NWDP/CWC/Karnataka water-data sources, a documented river dataset, land cover,
and NDEM/Bhuvan layers may enrich the system. None is a critical dependency.

## Acquisition rules

Do not commit raw or generated datasets. Do not proceed with a missing required
source by inserting zeros, invented averages, random values, or placeholders.
Record failed acquisition attempts and use a real alternative only when its
coverage and semantics are verified.

