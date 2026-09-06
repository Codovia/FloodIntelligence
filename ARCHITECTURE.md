# Architecture

## Overview
FloodPulse is a full-loop flood risk system encompassing prediction, alerting, and shelter management.

### Components
1. **Database:** PostgreSQL + PostGIS for spatial data and predictions.
2. **Backend:** FastAPI for ML inference, CRUD operations for shelters, and alert management.
3. **Frontend:** React application for public shelter locator and admin dashboard.
4. **Alerts:** Telegram Bot API for pushing warnings.
