# FloodPulse

FloodPulse is a Karnataka-focused flood decision-support and emergency-response
platform. The first milestone is a reproducible district-day ML baseline,
followed by the PostGIS/FastAPI shelter service, citizen locator, and Telegram
integration.

## Current status

This repository contains the project foundation, strict data readiness checks,
and the first label-construction component. No observations, shelters, model
metrics, or predictions are included. Real datasets must be acquired and their
provenance recorded before training.

The working research target is:

> district × day → likelihood that the available IFI inventory identifies a
> flood-affected district.

This is not an official warning and a label of `0` is not proof that no flood
occurred.

## Planned architecture

```text
React → FastAPI → PostgreSQL + PostGIS
                    ├── data/ML pipeline
                    ├── shelter administration and audit trail
                    └── Telegram Bot API integration
```

## Development setup

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e .
floodpulse-check-data --data-root data
floodpulse-build-labels \
  --events data/raw/ifi/events.csv \
  --candidates data/interim/candidate_district_days.csv \
  --output data/processed/district_day_labels.csv
floodpulse-build-rainfall-features \
  --input data/interim/district_daily_rainfall.csv \
  --output data/processed/rainfall_features.csv
```

The check fails until the required real inputs exist:

```text
data/raw/ifi/events.csv
data/raw/rainfall_imd/daily_gridded.csv
data/raw/boundaries/karnataka_districts.geojson
data/raw/dem/srtm.tif
```

The label command expects `candidate_district_days.csv` to be derived from
observed rainfall coverage and containing `district_id,event_date`. It refuses
duplicates, malformed dates, empty event inventories, and missing columns.

The rainfall command expects real, already spatially aggregated observations
with columns `district_id,observation_date,rainfall_mm`. It refuses duplicate
days, negative values, malformed dates, and incomplete seven-day histories.

Raw and generated data are intentionally ignored by Git. See
[`docs/DATA_SOURCES.md`](docs/DATA_SOURCES.md) before adding any source.

## Non-negotiable limitations

- The initial spatial unit is the district, not a household or exact flood
  boundary.
- Historical evaluation must use a time-based split; random splitting is not
  acceptable for the primary result.
- Model output must remain separate from official government warnings.
- Only verified and admin-activated shelters can be citizen-facing.
