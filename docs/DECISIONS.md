# Decisions

## 1. Project Initialization
- **Decision**: Start project from clean repository state.
- **Context**: 20-day timeframe to build FloodPulse prototype in Karnataka.
- **Alternatives considered**: None.
- **Reason**: Mandated by SKILL.md.
- **Consequence**: Full architecture and data ingestion must be bootstrapped systematically.

## 2. India Flood Inventory Source Selection
- **Decision**: Use IFI-Impacts version 3.0 via Zenodo (DOI: 10.5281/zenodo.4742142) as the primary historical flood dataset.
- **Context**: We need a reliable source for historical flood events in Karnataka to generate ML labels. 
- **Alternatives considered**: None, as this is specified as P0 requirement.
- **Reason**: Recommended by the SKILL plan and provides documented, peer-reviewed flood events with spatial coordinates and district mapping from 1969 to 2023.
- **Consequence**: The spatial resolution is limited to event location (point) or district polygons. Target variable spatial granularity might be restricted to coarse grids or district levels unless intersected with high-res topographic features.
