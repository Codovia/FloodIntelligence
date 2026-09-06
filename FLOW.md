# Data Flow

## Ingestion
1. Raw files (IFI, IMD, KSNDMC, CWC, KGIS, SRTM) are downloaded into `data/raw`.
2. Provenance is logged per record.
3. Preprocessing scripts normalize and spatialize data, storing in `data/processed` and the PostGIS database.

## Prediction
1. Model loads preprocessed rolling rainfall and SRTM slope.
2. Inference pipeline outputs continuous risk probability.
3. Data is pushed to the `predictions` table.

## Alerting
1. Telegram Bot triggers an alert when a district's risk crosses a defined threshold.
2. Alert includes nearest active shelters.

## Shelter Management
1. Admin uses the Frontend portal to update shelter state (CANDIDATE → ACTIVE/FULL/CLOSED).
2. Updates sync to the database and reflect immediately on the Citizen map view.
