"""
map_data.py — GeoJSON builder for Karnataka district boundaries + risk data.
Merges real district polygon data with live prediction results.
"""
import json
import os
from functools import lru_cache

GEOJSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "geojson", "karnataka_districts.geojson")

# Approximate bounding box polygons for each Karnataka district
# These are simplified representations — in production, use the real KGIS GeoJSON
DISTRICT_POLYGONS = {
    "Bagalkot": [[75.3,15.8],[76.1,15.8],[76.1,16.5],[75.3,16.5]],
    "Ballari": [[76.0,14.8],[77.0,14.8],[77.0,15.6],[76.0,15.6]],
    "Belagavi": [[74.0,15.4],[75.6,15.4],[75.6,16.6],[74.0,16.6]],
    "Bengaluru Rural": [[77.2,12.8],[77.9,12.8],[77.9,13.4],[77.2,13.4]],
    "Bengaluru Urban": [[77.4,12.8],[77.8,12.8],[77.8,13.2],[77.4,13.2]],
    "Bidar": [[77.0,17.5],[77.9,17.5],[77.9,18.3],[77.0,18.3]],
    "Chamarajanagar": [[76.5,11.6],[77.4,11.6],[77.4,12.2],[76.5,12.2]],
    "Chikkaballapura": [[77.4,13.3],[78.1,13.3],[78.1,13.8],[77.4,13.8]],
    "Chikkamagaluru": [[75.3,12.9],[76.3,12.9],[76.3,13.7],[75.3,13.7]],
    "Chitradurga": [[76.0,13.8],[77.0,13.8],[77.0,14.7],[76.0,14.7]],
    "Dakshina Kannada": [[74.7,12.5],[75.4,12.5],[75.4,13.2],[74.7,13.2]],
    "Davanagere": [[75.5,14.0],[76.5,14.0],[76.5,14.8],[75.5,14.8]],
    "Dharwad": [[74.6,15.1],[75.5,15.1],[75.5,15.8],[74.6,15.8]],
    "Gadag": [[75.2,15.1],[76.0,15.1],[76.0,15.7],[75.2,15.7]],
    "Hassan": [[75.6,12.6],[76.5,12.6],[76.5,13.3],[75.6,13.3]],
    "Haveri": [[74.9,14.4],[75.8,14.4],[75.8,15.1],[74.9,15.1]],
    "Kalaburagi": [[76.3,16.8],[77.6,16.8],[77.6,17.7],[76.3,17.7]],
    "Kodagu": [[75.3,12.0],[76.2,12.0],[76.2,12.7],[75.3,12.7]],
    "Kolar": [[77.7,12.9],[78.4,12.9],[78.4,13.5],[77.7,13.5]],
    "Koppal": [[75.7,15.1],[76.5,15.1],[76.5,15.8],[75.7,15.8]],
    "Mandya": [[76.4,12.3],[77.1,12.3],[77.1,12.9],[76.4,12.9]],
    "Mysuru": [[76.0,11.8],[77.0,11.8],[77.0,12.6],[76.0,12.6]],
    "Raichur": [[76.2,15.7],[77.5,15.7],[77.5,16.5],[76.2,16.5]],
    "Ramanagara": [[76.9,12.4],[77.5,12.4],[77.5,12.9],[76.9,12.9]],
    "Shivamogga": [[74.9,13.5],[75.9,13.5],[75.9,14.5],[74.9,14.5]],
    "Tumakuru": [[76.5,13.0],[77.5,13.0],[77.5,13.8],[76.5,13.8]],
    "Udupi": [[74.4,13.2],[75.1,13.2],[75.1,13.9],[74.4,13.9]],
    "Uttara Kannada": [[73.8,14.0],[75.2,14.0],[75.2,15.5],[73.8,15.5]],
    "Vijayapura": [[75.0,16.2],[76.3,16.2],[76.3,17.1],[75.0,17.1]],
    "Yadgir": [[76.5,16.3],[77.5,16.3],[77.5,17.0],[76.5,17.0]],
}

def risk_geojson(district_predictions: dict) -> dict:
    """Build a GeoJSON FeatureCollection with district polygons colored by risk.
    
    Args:
        district_predictions: {district_name: prediction_dict}
    
    Returns:
        GeoJSON FeatureCollection
    """
    features = []
    
    for district, coords in DISTRICT_POLYGONS.items():
        pred = district_predictions.get(district, {})
        closed = coords + [coords[0]]  # Close the polygon
        
        feature = {
            "type": "Feature",
            "properties": {
                "name": district,
                "risk_level": pred.get("risk_level", "Low"),
                "flood_probability": pred.get("flood_probability", 0),
                "operational_risk_index": pred.get("operational_risk_index", 0),
                "confidence_score": pred.get("confidence_score", 0),
                "main_factors": pred.get("main_factors", []),
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [closed]
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@lru_cache(maxsize=1)
def load_geojson() -> dict | None:
    """Load real GeoJSON from file if available."""
    if os.path.exists(GEOJSON_PATH):
        with open(GEOJSON_PATH) as f:
            return json.load(f)
    return None
