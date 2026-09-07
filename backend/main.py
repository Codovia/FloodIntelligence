"""
main.py — FloodPulse FastAPI Backend
22+ API endpoints covering predictions, alerts, subscriptions, shelters, and data management.
"""
import os
import time
import threading
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware

from . import database
from .src.data_loader import KARNATAKA_DISTRICTS, DISTRICT_NAMES, get_district_profile, load_flood_dataset
from .src.flood_model import predict_flood_risk, load_or_train_model, FEATURE_COLUMNS
from .src.rainfall_forecast import fetch_weather_forecast, fetch_all_districts_forecast, fetch_locality_weather
from .src.locality_risk import load_localities, get_district_localities, locality_adjusted_prediction
from .src.map_data import risk_geojson, DISTRICT_POLYGONS
from .src.drainage_risk import drainage_level, reservoir_status
from .src.alert_system import run_alert_check
from .src.notifier import format_telegram_alert, send_telegram
from .src.telegram_bot import FloodPulseBot
from .src import data_loader

# ── Module-level globals ────────────────────────────
MODEL_ARTIFACT = None
DATAFRAME = None
BOT = None

# ── TTL Cache ───────────────────────────────────────
LIVE_SUMMARY_CACHE_TTL = 180  # 3 minutes
MAP_HOTSPOT_CACHE_TTL = 180
_RUNTIME_CACHE: dict[str, tuple[float, any]] = {}

def _cache_get(key):
    if key in _RUNTIME_CACHE:
        ts, val = _RUNTIME_CACHE[key]
        if time.time() - ts < LIVE_SUMMARY_CACHE_TTL:
            return val
    return None

def _cache_set(key, val):
    _RUNTIME_CACHE[key] = (time.time(), val)


# ── Lifespan ────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global MODEL_ARTIFACT, DATAFRAME, BOT
    
    # Initialize DB
    database.initialize_database()
    
    # Load or build dataset + train model
    try:
        DATAFRAME = load_flood_dataset()
        MODEL_ARTIFACT = load_or_train_model(DATAFRAME)
        # Log model run
        if MODEL_ARTIFACT and "metrics" in MODEL_ARTIFACT:
            database.model_run_create(MODEL_ARTIFACT["metrics"])
    except FileNotFoundError:
        print("WARNING: Training dataset not found. Run `python -m backend.src.official_data` first.")
        print("API will start but prediction endpoints will return errors.")
    except Exception as e:
        print(f"WARNING: Model loading failed: {e}")
    
    # Start Telegram bot
    BOT = FloodPulseBot(db_module=database, predict_fn=predict_flood_risk, data_loader=data_loader)
    BOT.start()
    
    # Seed default shelters if empty
    _seed_shelters()
    
    yield
    
    # Shutdown
    if BOT:
        BOT.stop()

def _seed_shelters():
    """Seed real Karnataka shelter data if the table is empty."""
    existing = database.shelter_list()
    if existing:
        return
    
    shelters = [
        {"name": "Kanteerava Indoor Stadium", "district": "Bengaluru Urban", "locality": "Mahadevapura", "lat": 12.978, "lon": 77.600, "capacity": 500, "status": "ACTIVE", "changed_by": "KSNDMC"},
        {"name": "Mysuru Town Hall", "district": "Mysuru", "locality": "Mysuru City", "lat": 12.308, "lon": 76.655, "capacity": 200, "status": "ACTIVE", "changed_by": "DDMA Mysuru"},
        {"name": "Udupi District Community Hall", "district": "Udupi", "locality": "Udupi Town", "lat": 13.340, "lon": 74.751, "capacity": 300, "status": "ACTIVE", "changed_by": "DDMA Udupi"},
        {"name": "Kodagu Relief Camp - Madikeri", "district": "Kodagu", "locality": "Madikeri", "lat": 12.420, "lon": 75.740, "capacity": 250, "status": "ACTIVE", "changed_by": "DDMA Kodagu"},
        {"name": "Karwar Indoor Stadium", "district": "Uttara Kannada", "locality": "Karwar", "lat": 14.810, "lon": 74.130, "capacity": 400, "status": "ACTIVE", "changed_by": "DDMA UK"},
        {"name": "Belagavi Sports Complex", "district": "Belagavi", "locality": "Belagavi City", "lat": 15.850, "lon": 74.500, "capacity": 350, "status": "CANDIDATE", "changed_by": "system"},
        {"name": "Shivamogga Govt School Shelter", "district": "Shivamogga", "locality": "Shivamogga Town", "lat": 13.930, "lon": 75.570, "capacity": 150, "status": "CANDIDATE", "changed_by": "system"},
        {"name": "Mangaluru Convention Centre", "district": "Dakshina Kannada", "locality": "Mangaluru City", "lat": 12.870, "lon": 74.880, "capacity": 450, "status": "ACTIVE", "changed_by": "DDMA DK"},
    ]
    for s in shelters:
        database.shelter_create(s)
    print(f"Seeded {len(shelters)} default shelters.")


# ── FastAPI App ─────────────────────────────────────
app = FastAPI(
    title="FloodPulse API",
    description="AI-Based Flood Risk Mapping & Early Warning System for Karnataka",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Helper Functions ────────────────────────────────

def _live_district_summary() -> list:
    """Compute live risk summary for all 31 districts using weather + ML."""
    cached = _cache_get("live_summary")
    if cached:
        return cached
    
    if not MODEL_ARTIFACT:
        return []
    
    forecasts = fetch_all_districts_forecast()
    results = []
    
    for fc in forecasts:
        district = fc.get("district", "")
        profile = KARNATAKA_DISTRICTS.get(district, {})
        if not profile:
            continue
        
        today_rain = fc["forecast"][0]["rainfall_mm"] if fc.get("forecast") else 0
        total_7day = fc.get("total_7day_mm", 0)
        
        payload = {
            "district": district,
            "taluk": f"{district}_Central",
            "rainfall_mm": today_rain,
            "rainfall_3day": today_rain * 2.5,
            "rainfall_7day": total_7day,
            "reservoir_level": 55,
            "reservoir_storage_percent": 50,
            "distance_to_river_km": profile["distance_to_river_km"],
            "elevation_m": profile["elevation_m"],
            "slope": profile["slope"],
            "past_flood_count": profile["past_flood_count"],
            "drainage_score": 50,
        }
        
        prediction = predict_flood_risk(MODEL_ARTIFACT, payload)
        prediction["weather_context"] = {
            "today_rainfall_mm": today_rain,
            "total_7day_mm": total_7day,
            "forecast": fc.get("forecast", [])
        }
        
        # Apply live signal adjustments
        if total_7day >= 180:
            prediction["flood_probability"] = min(1.0, prediction["flood_probability"] + 0.12)
            prediction["confidence_score"] = min(1.0, prediction["confidence_score"] + 0.05)
        elif total_7day >= 120:
            prediction["flood_probability"] = min(1.0, prediction["flood_probability"] + 0.08)
        
        # Reclassify after adjustment
        prob = prediction["flood_probability"]
        if prob >= 0.7:
            prediction["risk_level"] = "High"
        elif prob >= 0.4:
            prediction["risk_level"] = "Medium"
        
        results.append(prediction)
    
    results.sort(key=lambda x: x.get("flood_probability", 0), reverse=True)
    _cache_set("live_summary", results)
    return results


# ══════════════════════════════════════════════════════
# API ENDPOINTS (22+)
# ══════════════════════════════════════════════════════

# ── Health ──────────────────────────────────────────
@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_loaded": MODEL_ARTIFACT is not None,
        "dataset_loaded": DATAFRAME is not None,
        "districts": len(KARNATAKA_DISTRICTS),
    }

# ── Districts ───────────────────────────────────────
@app.get("/api/districts")
def list_districts():
    return [
        {"name": d, **KARNATAKA_DISTRICTS[d]}
        for d in DISTRICT_NAMES
    ]

# ── Summary ─────────────────────────────────────────
@app.get("/api/summary")
def district_summary():
    results = _live_district_summary()
    high = sum(1 for r in results if r.get("risk_level") == "High")
    medium = sum(1 for r in results if r.get("risk_level") == "Medium")
    low = sum(1 for r in results if r.get("risk_level") == "Low")
    return {
        "total_districts": len(results),
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "districts": results,
    }

# ── Live Risk Console ───────────────────────────────
@app.get("/api/live-risk")
def live_risk(district: str = None):
    results = _live_district_summary()
    if district:
        results = [r for r in results if r.get("district") == district]
        if not results:
            raise HTTPException(404, f"District '{district}' not found")
    
    geojson = risk_geojson({r["district"]: r for r in results})
    alerts = [r for r in results if r.get("risk_level") == "High"]
    
    return {
        "districts": results,
        "geojson": geojson,
        "alerts": alerts,
        "total_districts": len(KARNATAKA_DISTRICTS),
        "high_risk_count": len(alerts),
    }

# ── Rainfall Forecast ───────────────────────────────
@app.get("/api/rainfall/forecast")
def rainfall_forecast(district: str = None):
    if district:
        profile = get_district_profile(district)
        if not profile:
            raise HTTPException(404, f"District '{district}' not found")
        return fetch_weather_forecast(profile["lat"], profile["lon"], district)
    return fetch_all_districts_forecast()

@app.get("/api/rainfall/history")
def rainfall_history(district: str = None):
    if DATAFRAME is None:
        raise HTTPException(503, "Dataset not loaded")
    df = DATAFRAME.copy()
    if district:
        df = df[df["district"] == district]
    # Return last 30 days
    df = df.sort_values("date").tail(30 * len(KARNATAKA_DISTRICTS) if not district else 30)
    return df[["date", "district", "rainfall_mm", "rainfall_3day", "rainfall_7day"]].to_dict(orient="records")

# ── Prediction ──────────────────────────────────────
@app.post("/api/predict/flood")
def predict_manual(payload: dict):
    if not MODEL_ARTIFACT:
        raise HTTPException(503, "Model not loaded")
    
    district = payload.get("district")
    if district and district not in KARNATAKA_DISTRICTS:
        raise HTTPException(404, f"District '{district}' not found")
    
    # Merge with district profile
    profile = KARNATAKA_DISTRICTS.get(district, {})
    for key in ["distance_to_river_km", "elevation_m", "slope", "past_flood_count"]:
        if key not in payload:
            payload[key] = profile.get(key, 0)
    if "taluk" not in payload:
        payload["taluk"] = f"{district}_Central"
    
    prediction = predict_flood_risk(MODEL_ARTIFACT, payload)
    prediction["mode"] = "manual"
    prediction["input_snapshot"] = payload
    return prediction

@app.get("/api/predict/flood/auto")
def predict_auto(district: str):
    if not MODEL_ARTIFACT:
        raise HTTPException(503, "Model not loaded")
    profile = get_district_profile(district)
    if not profile:
        raise HTTPException(404, f"District '{district}' not found")
    
    weather = fetch_weather_forecast(profile["lat"], profile["lon"], district)
    today_rain = weather["forecast"][0]["rainfall_mm"] if weather.get("forecast") else 0
    
    payload = {
        "district": district,
        "taluk": f"{district}_Central",
        "rainfall_mm": today_rain,
        "rainfall_3day": today_rain * 2.5,
        "rainfall_7day": weather.get("total_7day_mm", 0),
        "reservoir_level": 55,
        "reservoir_storage_percent": 50,
        **{k: profile[k] for k in ["distance_to_river_km", "elevation_m", "slope", "past_flood_count"]},
        "drainage_score": 50,
    }
    
    prediction = predict_flood_risk(MODEL_ARTIFACT, payload)
    prediction["mode"] = "automatic"
    prediction["weather_context"] = weather
    return prediction

@app.get("/api/predict/flood/locality")
def predict_locality(district: str, locality: str = None):
    if not MODEL_ARTIFACT:
        raise HTTPException(503, "Model not loaded")
    
    # Get district prediction first
    profile = get_district_profile(district)
    if not profile:
        raise HTTPException(404, f"District '{district}' not found")
    
    weather = fetch_weather_forecast(profile["lat"], profile["lon"], district)
    today_rain = weather["forecast"][0]["rainfall_mm"] if weather.get("forecast") else 0
    
    payload = {
        "district": district, "taluk": f"{district}_Central",
        "rainfall_mm": today_rain, "rainfall_3day": today_rain * 2.5,
        "rainfall_7day": weather.get("total_7day_mm", 0),
        "reservoir_level": 55, "reservoir_storage_percent": 50,
        **{k: profile[k] for k in ["distance_to_river_km", "elevation_m", "slope", "past_flood_count"]},
        "drainage_score": 50,
    }
    district_pred = predict_flood_risk(MODEL_ARTIFACT, payload)
    
    localities = get_district_localities(district)
    if locality:
        localities = [l for l in localities if l.get("name", "").lower() == locality.lower()]
        if not localities:
            raise HTTPException(404, f"Locality '{locality}' not found in {district}")
    
    results = [locality_adjusted_prediction(district_pred, loc) for loc in localities]
    return {"district": district, "localities": results}

# ── Map Data ────────────────────────────────────────
@app.get("/api/map/risk")
def map_risk():
    results = _live_district_summary()
    return risk_geojson({r["district"]: r for r in results})

@app.get("/api/map/hotspots")
def map_hotspots():
    """Return high-risk locality hotspot markers."""
    if not MODEL_ARTIFACT:
        return {"hotspots": []}
    
    hotspots = []
    results = _live_district_summary()
    high_districts = [r for r in results if r.get("risk_level") in ["High", "Medium"]]
    
    for pred in high_districts:
        district = pred["district"]
        locs = get_district_localities(district)
        for loc in locs:
            adjusted = locality_adjusted_prediction(pred, loc)
            if adjusted.get("locality_risk_level") in ["High", "Medium"]:
                hotspots.append({
                    "name": loc["name"],
                    "district": district,
                    "lat": loc["lat"],
                    "lon": loc["lon"],
                    "risk_level": adjusted["locality_risk_level"],
                    "probability": adjusted["locality_probability"],
                })
    
    return {"hotspots": hotspots}

# ── Alerts ──────────────────────────────────────────
@app.get("/api/alerts")
def list_alerts(district: str = None):
    results = _live_district_summary()
    alerts = [r for r in results if r.get("risk_level") == "High"]
    if district:
        alerts = [a for a in alerts if a.get("district") == district]
    return alerts

@app.get("/api/alert-events")
def list_alert_events(district: str = None, limit: int = 50):
    return database.alert_event_list(district=district, limit=limit)

@app.post("/api/alerts/run-check")
def trigger_alert_check(background_tasks: BackgroundTasks):
    if not MODEL_ARTIFACT:
        raise HTTPException(503, "Model not loaded")
    localities = load_localities()
    background_tasks.add_task(run_alert_check, MODEL_ARTIFACT, DATAFRAME, localities, database)
    return {"status": "alert_sweep_started", "localities": len(localities)}

# ── Localities ──────────────────────────────────────
@app.get("/api/localities")
def list_localities(district: str = None):
    locs = load_localities()
    if district:
        locs = [l for l in locs if l.get("district") == district]
    return locs

# ── Subscriptions ───────────────────────────────────
@app.post("/api/subscribe", status_code=201)
def create_subscriber(payload: dict):
    try:
        return database.subscriber_create(
            payload["contact_method"], payload["contact_value"],
            payload["district"], payload.get("locality", "district_wide")
        )
    except Exception as e:
        if "UNIQUE" in str(e) or "unique" in str(e).lower():
            raise HTTPException(409, "Subscriber already exists for this district/locality")
        raise HTTPException(400, str(e))

@app.delete("/api/subscribe/{sub_id}")
def delete_subscriber(sub_id: int):
    if database.subscriber_delete(sub_id):
        return {"status": "deleted"}
    raise HTTPException(404, "Subscriber not found")

@app.get("/api/subscribe")
def list_subscribers(district: str = None):
    return database.subscriber_list(district=district)

# ── Model Performance ───────────────────────────────
@app.get("/api/model/performance")
def model_performance():
    if not MODEL_ARTIFACT:
        raise HTTPException(503, "Model not loaded")
    return {
        "version": MODEL_ARTIFACT.get("version"),
        "metrics": MODEL_ARTIFACT.get("metrics", {}),
        "feature_importance": MODEL_ARTIFACT.get("feature_importance", []),
    }

@app.post("/api/model/retrain")
def retrain_model(background_tasks: BackgroundTasks):
    if DATAFRAME is None:
        raise HTTPException(503, "Dataset not loaded")
    
    def _retrain():
        global MODEL_ARTIFACT
        MODEL_ARTIFACT = load_or_train_model(DATAFRAME)
        if MODEL_ARTIFACT and "metrics" in MODEL_ARTIFACT:
            database.model_run_create(MODEL_ARTIFACT["metrics"])
    
    background_tasks.add_task(_retrain)
    return {"status": "retraining_started"}

# ── Data Sources ────────────────────────────────────
@app.get("/api/data/sources")
def data_sources():
    import json
    manifest_path = os.path.join(os.path.dirname(__file__), "data", "processed", "official_data_sources.json")
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            return json.load(f)
    return {"status": "manifest_not_found", "hint": "Run official_data.py first"}

@app.post("/api/data/download-official")
def download_official(background_tasks: BackgroundTasks):
    from .src.official_data import build_official_feature_dataset
    background_tasks.add_task(build_official_feature_dataset)
    return {"status": "download_started"}

# ── Shelters ────────────────────────────────────────
@app.get("/api/shelters")
def list_shelters(district: str = None, status: str = None):
    return database.shelter_list(district=district, status=status)

@app.post("/api/shelters", status_code=201)
def create_shelter(payload: dict):
    return database.shelter_create(payload)

@app.patch("/api/shelters/{shelter_id}/status")
def update_shelter_status(shelter_id: int, payload: dict):
    result = database.shelter_update_status(
        shelter_id,
        payload.get("status", "ACTIVE"),
        payload.get("changed_by", "admin"),
        payload.get("reason", "Status update")
    )
    if not result:
        raise HTTPException(404, "Shelter not found")
    return result
