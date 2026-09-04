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
