"""
rainfall_forecast.py — Open-Meteo API integration for live 7-day weather forecasts.
Free API, no key required. Fetches daily rainfall at exact GPS coordinates.
"""
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from .data_loader import KARNATAKA_DISTRICTS

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# In-memory TTL cache
_WEATHER_CACHE: dict[str, tuple[float, dict]] = {}
CACHE_TTL = 180  # 3 minutes

def _cache_get(key: str) -> dict | None:
    if key in _WEATHER_CACHE:
        ts, data = _WEATHER_CACHE[key]
        if time.time() - ts < CACHE_TTL:
            return data
        del _WEATHER_CACHE[key]
    return None

def _cache_set(key: str, data: dict):
    _WEATHER_CACHE[key] = (time.time(), data)

def fetch_weather_forecast(lat: float, lon: float, district: str = "") -> dict:
    """Fetch 7-day daily rainfall forecast from Open-Meteo for given coordinates."""
    cache_key = f"{lat:.2f}_{lon:.2f}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,rain_sum,weathercode",
        "timezone": "Asia/Kolkata",
        "forecast_days": 7
    }
    
    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        precip = daily.get("precipitation_sum", [])
        rain = daily.get("rain_sum", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        codes = daily.get("weathercode", [])
        
        forecast_days = []
        total_7day = 0
        for i in range(len(dates)):
            daily_rain = (rain[i] if rain[i] is not None else 0) or (precip[i] if precip[i] is not None else 0)
            total_7day += daily_rain
            forecast_days.append({
                "date": dates[i],
                "rainfall_mm": round(daily_rain, 1),
                "temp_max": temp_max[i] if i < len(temp_max) else None,
                "temp_min": temp_min[i] if i < len(temp_min) else None,
                "weather_code": codes[i] if i < len(codes) else None,
            })
        
        result = {
            "district": district,
            "lat": lat,
            "lon": lon,
            "forecast": forecast_days,
            "total_7day_mm": round(total_7day, 1),
            "source": "Open-Meteo",
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        }
        _cache_set(cache_key, result)
        return result
        
    except Exception as e:
        return {
            "district": district,
            "lat": lat, "lon": lon,
            "forecast": [],
            "total_7day_mm": 0,
            "error": str(e),
            "source": "Open-Meteo (failed)"
        }

def fetch_all_districts_forecast() -> list:
    """Fetch 7-day forecasts for all 31 districts in parallel using ThreadPoolExecutor."""
    results = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {}
        for district, profile in KARNATAKA_DISTRICTS.items():
            future = executor.submit(
                fetch_weather_forecast,
                profile["lat"], profile["lon"], district
            )
            futures[future] = district
        
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                results.append({
                    "district": futures[future],
                    "error": str(e),
                    "forecast": [],
                    "total_7day_mm": 0
                })
    
    results.sort(key=lambda x: x.get("district", ""))
    return results

def fetch_locality_weather(lat: float, lon: float, locality_name: str = "") -> dict:
    """Fetch weather for a specific locality coordinate."""
    return fetch_weather_forecast(lat, lon, locality_name)
