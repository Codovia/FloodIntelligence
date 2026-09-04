# Data Sources

## 1. India Flood Inventory (IFI)
- **Publisher**: HydroSense Lab, IIT Delhi / IMD
- **URL**: https://zenodo.org/doi/10.5281/zenodo.4742142
- **License**: Creative Commons Attribution 4.0 International
- **Coverage**: India (1967–2023)
- **Resolution**: Point/Event-level geometry
- **Purpose**: Historical flood events for training ML models
- **Retrieval date**: 2026-09-04
- **Processing notes**: Dataset contains 6876 historical events across India. Extracted 494 flood events explicitly impacting Karnataka to `data/interim/karnataka_flood_events.csv`. The coverage spans from 1969-07-15 to 2023-07-25.
- **Limitations**: Points or polygons may be coarse, reporting biases might exist. Spatial representation is available via Latitude/Longitude and District codes.

## 2. India Meteorological Department (IMD) 0.25 Gridded Rainfall
- **Source**: IMD Pune (via `imdlib` Python package)
- **Format**: `.grd` binary files parsed to `xarray`
- **Resolution**: 0.25° x 0.25° daily spatial grid
- **Purpose**: Broad-scale historical daily precipitation source for ML features.
- **Retrieval date**: 2026-09-04
- **Processing notes**: Downloaded years 2020-2023 for prototyping. Full dataset available 1901-2023. Spatial join approximated via Bounding Box mean for Karnataka, to be replaced by precise district polygon intersections.
- **Limitations**: Spatial resolution is 0.25 degrees, which is approx 27km.

## 3. National Water Data Portal (NWDP)
- **Source**: NWDP/NWIC API
- **Purpose**: High-resolution manual/telemetry station rainfall.
- **Retrieval date**: 2026-09-04
- **Processing notes**: API endpoints inaccessible/timing out during automated ingestion attempt.
- **Limitations**: Deemed unusable for initial POC due to access reliability. Relying entirely on IMD 0.25.
