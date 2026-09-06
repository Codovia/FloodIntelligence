"""
locality_risk.py — Locality-level disaggregation of district predictions.
Adjusts district-level ML predictions for ~169 curated Karnataka localities
using physical characteristics (elevation offset, river distance, drainage score).
"""
import json
import os
from functools import lru_cache

LOCALITIES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "localities.json")

@lru_cache(maxsize=1)
def load_localities() -> list:
    """Load curated localities from JSON file."""
    if os.path.exists(LOCALITIES_PATH):
        with open(LOCALITIES_PATH) as f:
            return json.load(f)
    return []

def _fuzzy_match_locality(name: str, district: str) -> dict | None:
    """Fuzzy match a locality name within a district."""
    localities = load_localities()
    name_lower = name.lower().strip()
    
    for loc in localities:
        if loc.get("district") == district:
            if loc.get("name", "").lower() == name_lower:
                return loc
            if name_lower in loc.get("name", "").lower():
                return loc
    return None

def locality_adjusted_prediction(district_pred: dict, locality: dict) -> dict:
    """Adjust a district-level prediction for a specific locality.
    
    Adjustment factors:
    - elevation_offset: localities below district average get higher risk
    - river_proximity: closer to river = higher risk
    - drainage_quality: poor drainage = higher risk
    - flood_history: more past events = higher risk
    """
    base_prob = district_pred.get("flood_probability", 0)
    adjustments = 0.0
    
    # Elevation offset (negative = below average = more risk)
    elev_offset = locality.get("elevation_offset_m", 0)
    if elev_offset < -50:
        adjustments += 0.08
    elif elev_offset < -20:
        adjustments += 0.04
    elif elev_offset > 100:
        adjustments -= 0.05
    
    # River proximity
    river_km = locality.get("river_distance_km", 5)
    if river_km < 0.5:
        adjustments += 0.10
    elif river_km < 1.0:
        adjustments += 0.06
    elif river_km < 2.0:
        adjustments += 0.03
    
    # Drainage quality (0-100, higher = worse drainage)
    drain = locality.get("drainage_score", 50)
    if drain > 70:
        adjustments += 0.06
    elif drain > 50:
        adjustments += 0.03
    
    # Past flood count
    past = locality.get("past_flood_count", 0)
    if past > 5:
        adjustments += 0.05
    elif past > 2:
        adjustments += 0.02
    
    adjusted_prob = min(1.0, max(0.0, base_prob + adjustments))
    
    # Reclassify
    if adjusted_prob >= 0.7:
        risk = "High"
    elif adjusted_prob >= 0.4:
        risk = "Medium"
    else:
        risk = "Low"
    
    return {
        **district_pred,
        "locality": locality.get("name", "Unknown"),
        "locality_risk_level": risk,
        "locality_probability": round(adjusted_prob, 4),
        "adjustment_applied": round(adjustments, 4),
        "adjustment_factors": {
            "elevation_offset_m": elev_offset,
            "river_distance_km": river_km,
            "drainage_score": drain,
            "past_flood_count": past,
        }
    }

def get_district_localities(district: str) -> list:
    """Return all localities for a given district."""
    return [l for l in load_localities() if l.get("district") == district]
