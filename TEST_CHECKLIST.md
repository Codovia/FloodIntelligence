# Test Checklist

## Backend
- [ ] Model inference pipeline executes without missing data silently.
- [ ] FastAPI `/health` endpoint responds 200 OK.
- [ ] Prediction endpoints return correct probability schemas.

## Database
- [ ] PostGIS extension is active.
- [ ] Provenance logs successfully capture edits.
- [ ] Shelter state transitions (e.g. CANDIDATE -> ACTIVE) store audit history.

## Frontend
- [ ] Shelter map view loads successfully.
- [ ] Admin portal updates shelter state correctly.

## Bot
- [ ] Telegram Bot triggers alert upon hitting probability threshold.
