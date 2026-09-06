"""
alert_system.py — Alert building and dispatch logic.
alert_scheduler.py — APScheduler 6-hour interval sweep across localities.
Combined into a single file for simplicity.
"""
import time
from datetime import datetime, timezone
from .flood_model import predict_flood_risk
from .rainfall_forecast import fetch_locality_weather
from .notifier import dispatch_alert

def build_alert(prediction: dict, locality: str, forecast_date: str) -> dict:
    """Build a structured alert dict from a prediction result."""
    return {
        "district": prediction.get("district", "Unknown"),
        "locality": locality,
        "predicted_date": forecast_date,
        "risk_level": prediction.get("risk_level", "Low"),
        "flood_probability": prediction.get("flood_probability", 0),
        "main_factors": prediction.get("main_factors", []),
        "operational_risk_index": prediction.get("operational_risk_index", 0),
        "triggered_at": datetime.now(timezone.utc).isoformat(),
    }

def run_alert_check(model_artifact: dict, df, localities: list, db_module=None) -> dict:
    """Sweep all localities, predict risk for next 7 days, trigger alerts on High risk.
    
    Args:
        model_artifact: The trained ML model artifact
        df: The training dataframe (for feature reference)
        localities: List of locality dicts with lat, lon, district, name
        db_module: Database module for subscriber lookup and alert event storage
    
    Returns:
        Summary dict with counts
    """
    from .data_loader import KARNATAKA_DISTRICTS
    
    total_checked = 0
    alerts_triggered = 0
    notifications_sent = 0
    errors = 0
    
    print(f"[Alert Sweep] Starting check for {len(localities)} localities...")
    start = time.time()
    
    for loc in localities:
        district = loc.get("district", "")
        locality_name = loc.get("name", "district_wide")
        lat = loc.get("lat", 0)
        lon = loc.get("lon", 0)
        
        profile = KARNATAKA_DISTRICTS.get(district)
        if not profile:
            continue
        
        try:
            weather = fetch_locality_weather(lat, lon, locality_name)
            forecast = weather.get("forecast", [])
            
            for day in forecast:
                total_checked += 1
                rain_mm = day.get("rainfall_mm", 0)
                
                payload = {
                    "district": district,
                    "taluk": f"{district}_Central",
                    "rainfall_mm": rain_mm,
                    "rainfall_3day": rain_mm * 2.5,
                    "rainfall_7day": weather.get("total_7day_mm", 0),
                    "reservoir_level": 60,
                    "reservoir_storage_percent": 55,
                    "distance_to_river_km": profile["distance_to_river_km"],
                    "elevation_m": profile["elevation_m"],
                    "slope": profile["slope"],
                    "past_flood_count": profile["past_flood_count"],
                    "drainage_score": 50,
                }
                
                prediction = predict_flood_risk(model_artifact, payload)
                
                if prediction["risk_level"] == "High":
                    alert = build_alert(prediction, locality_name, day.get("date", ""))
                    alerts_triggered += 1
                    
                    # Store alert event
                    if db_module:
                        db_module.alert_event_upsert(
                            district, locality_name,
                            day.get("date", ""), "High"
                        )
                        
                        # Get subscribers and dispatch
                        subscribers = db_module.subscriber_list(district=district)
                        sent = dispatch_alert(alert, subscribers)
                        notifications_sent += sent
        
        except Exception as e:
            errors += 1
            print(f"  Error checking {locality_name}: {e}")
    
    elapsed = round(time.time() - start, 1)
    summary = {
        "total_checked": total_checked,
        "alerts_triggered": alerts_triggered,
        "notifications_sent": notifications_sent,
        "errors": errors,
        "elapsed_seconds": elapsed,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    print(f"[Alert Sweep] Done in {elapsed}s: {alerts_triggered} alerts, {notifications_sent} notifications, {errors} errors")
    return summary
