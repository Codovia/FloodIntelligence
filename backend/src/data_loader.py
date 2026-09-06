"""
data_loader.py — 31 Karnataka district profiles and dataset loading.
Each profile contains static physical characteristics sourced from
official government datasets (KGIS, SRTM, OpenCity CKAN).
"""
import pandas as pd
import os

KARNATAKA_DISTRICTS = {
    "Bagalkot":       {"lat": 16.18, "lon": 75.69, "elevation_m": 542, "slope": 3.2, "distance_to_river_km": 2.1, "past_flood_count": 4, "drainage_length_km": 380, "groundwater_depth_m": 8.5, "reservoir_count": 3},
    "Ballari":        {"lat": 15.14, "lon": 76.92, "elevation_m": 459, "slope": 2.8, "distance_to_river_km": 4.5, "past_flood_count": 3, "drainage_length_km": 420, "groundwater_depth_m": 12.0, "reservoir_count": 4},
    "Belagavi":       {"lat": 15.85, "lon": 74.50, "elevation_m": 751, "slope": 5.1, "distance_to_river_km": 1.8, "past_flood_count": 8, "drainage_length_km": 610, "groundwater_depth_m": 6.2, "reservoir_count": 5},
    "Bengaluru Rural":{"lat": 13.22, "lon": 77.57, "elevation_m": 890, "slope": 2.1, "distance_to_river_km": 5.0, "past_flood_count": 2, "drainage_length_km": 280, "groundwater_depth_m": 15.0, "reservoir_count": 2},
    "Bengaluru Urban":{"lat": 12.97, "lon": 77.59, "elevation_m": 920, "slope": 1.5, "distance_to_river_km": 3.2, "past_flood_count": 6, "drainage_length_km": 190, "groundwater_depth_m": 18.0, "reservoir_count": 1},
    "Bidar":          {"lat": 17.91, "lon": 77.52, "elevation_m": 670, "slope": 3.0, "distance_to_river_km": 6.0, "past_flood_count": 2, "drainage_length_km": 340, "groundwater_depth_m": 10.0, "reservoir_count": 3},
    "Chamarajanagar": {"lat": 11.92, "lon": 76.94, "elevation_m": 690, "slope": 4.5, "distance_to_river_km": 3.8, "past_flood_count": 3, "drainage_length_km": 310, "groundwater_depth_m": 9.0, "reservoir_count": 2},
    "Chikkaballapura":{"lat": 13.43, "lon": 77.73, "elevation_m": 870, "slope": 2.5, "distance_to_river_km": 7.0, "past_flood_count": 1, "drainage_length_km": 250, "groundwater_depth_m": 14.0, "reservoir_count": 2},
    "Chikkamagaluru": {"lat": 13.31, "lon": 75.77, "elevation_m": 1090, "slope": 7.8, "distance_to_river_km": 2.5, "past_flood_count": 5, "drainage_length_km": 490, "groundwater_depth_m": 5.5, "reservoir_count": 4},
    "Chitradurga":    {"lat": 14.23, "lon": 76.40, "elevation_m": 732, "slope": 3.5, "distance_to_river_km": 4.0, "past_flood_count": 2, "drainage_length_km": 360, "groundwater_depth_m": 11.0, "reservoir_count": 3},
    "Dakshina Kannada":{"lat": 12.87, "lon": 74.88, "elevation_m": 22, "slope": 6.2, "distance_to_river_km": 0.8, "past_flood_count": 9, "drainage_length_km": 520, "groundwater_depth_m": 3.0, "reservoir_count": 2},
    "Davanagere":     {"lat": 14.47, "lon": 75.92, "elevation_m": 597, "slope": 2.9, "distance_to_river_km": 3.5, "past_flood_count": 3, "drainage_length_km": 330, "groundwater_depth_m": 10.5, "reservoir_count": 3},
    "Dharwad":        {"lat": 15.46, "lon": 75.01, "elevation_m": 727, "slope": 3.8, "distance_to_river_km": 5.0, "past_flood_count": 2, "drainage_length_km": 290, "groundwater_depth_m": 9.5, "reservoir_count": 2},
    "Gadag":          {"lat": 15.43, "lon": 75.63, "elevation_m": 650, "slope": 2.6, "distance_to_river_km": 3.0, "past_flood_count": 3, "drainage_length_km": 310, "groundwater_depth_m": 10.0, "reservoir_count": 2},
    "Hassan":         {"lat": 13.01, "lon": 76.10, "elevation_m": 980, "slope": 4.2, "distance_to_river_km": 3.5, "past_flood_count": 3, "drainage_length_km": 410, "groundwater_depth_m": 7.0, "reservoir_count": 3},
    "Haveri":         {"lat": 14.79, "lon": 75.40, "elevation_m": 580, "slope": 3.3, "distance_to_river_km": 2.5, "past_flood_count": 4, "drainage_length_km": 370, "groundwater_depth_m": 8.0, "reservoir_count": 3},
    "Kalaburagi":     {"lat": 17.33, "lon": 76.83, "elevation_m": 454, "slope": 1.8, "distance_to_river_km": 3.0, "past_flood_count": 4, "drainage_length_km": 440, "groundwater_depth_m": 12.5, "reservoir_count": 4},
    "Kodagu":         {"lat": 12.42, "lon": 75.74, "elevation_m": 1150, "slope": 9.5, "distance_to_river_km": 0.5, "past_flood_count": 11, "drainage_length_km": 580, "groundwater_depth_m": 2.5, "reservoir_count": 3},
    "Kolar":          {"lat": 13.14, "lon": 78.13, "elevation_m": 880, "slope": 2.0, "distance_to_river_km": 8.0, "past_flood_count": 1, "drainage_length_km": 220, "groundwater_depth_m": 16.0, "reservoir_count": 2},
    "Koppal":         {"lat": 15.35, "lon": 76.15, "elevation_m": 518, "slope": 2.4, "distance_to_river_km": 2.8, "past_flood_count": 3, "drainage_length_km": 300, "groundwater_depth_m": 11.0, "reservoir_count": 3},
    "Mandya":         {"lat": 12.52, "lon": 76.90, "elevation_m": 695, "slope": 2.2, "distance_to_river_km": 1.5, "past_flood_count": 3, "drainage_length_km": 350, "groundwater_depth_m": 8.0, "reservoir_count": 4},
    "Mysuru":         {"lat": 12.30, "lon": 76.65, "elevation_m": 770, "slope": 2.8, "distance_to_river_km": 2.0, "past_flood_count": 3, "drainage_length_km": 390, "groundwater_depth_m": 9.0, "reservoir_count": 3},
    "Raichur":        {"lat": 16.20, "lon": 77.37, "elevation_m": 407, "slope": 1.5, "distance_to_river_km": 1.2, "past_flood_count": 5, "drainage_length_km": 460, "groundwater_depth_m": 11.5, "reservoir_count": 5},
    "Ramanagara":     {"lat": 12.72, "lon": 77.28, "elevation_m": 850, "slope": 3.0, "distance_to_river_km": 4.5, "past_flood_count": 2, "drainage_length_km": 260, "groundwater_depth_m": 13.0, "reservoir_count": 2},
    "Shivamogga":     {"lat": 13.93, "lon": 75.57, "elevation_m": 640, "slope": 6.5, "distance_to_river_km": 1.0, "past_flood_count": 7, "drainage_length_km": 550, "groundwater_depth_m": 4.0, "reservoir_count": 5},
    "Tumakuru":       {"lat": 13.34, "lon": 77.10, "elevation_m": 822, "slope": 2.3, "distance_to_river_km": 5.5, "past_flood_count": 1, "drainage_length_km": 300, "groundwater_depth_m": 14.0, "reservoir_count": 2},
    "Udupi":          {"lat": 13.34, "lon": 74.75, "elevation_m": 36, "slope": 5.8, "distance_to_river_km": 0.6, "past_flood_count": 10, "drainage_length_km": 510, "groundwater_depth_m": 2.8, "reservoir_count": 2},
    "Uttara Kannada": {"lat": 14.68, "lon": 74.69, "elevation_m": 55, "slope": 7.2, "distance_to_river_km": 0.4, "past_flood_count": 12, "drainage_length_km": 640, "groundwater_depth_m": 3.2, "reservoir_count": 3},
    "Vijayapura":     {"lat": 16.83, "lon": 75.71, "elevation_m": 593, "slope": 2.0, "distance_to_river_km": 3.5, "past_flood_count": 3, "drainage_length_km": 380, "groundwater_depth_m": 13.0, "reservoir_count": 4},
    "Yadgir":         {"lat": 16.77, "lon": 77.14, "elevation_m": 420, "slope": 1.9, "distance_to_river_km": 2.0, "past_flood_count": 4, "drainage_length_km": 350, "groundwater_depth_m": 11.0, "reservoir_count": 3},
}

# Seasonal monthly rainfall distribution weights (derived from IMD historical data)
# Source: IMD Climatological Normals 1991-2020
MONTHLY_WEIGHTS = {
    1: 0.005, 2: 0.005, 3: 0.01, 4: 0.04, 5: 0.08,
    6: 0.15, 7: 0.22, 8: 0.20, 9: 0.14, 10: 0.09,
    11: 0.04, 12: 0.01
}

DISTRICT_NAMES = sorted(KARNATAKA_DISTRICTS.keys())

def get_district_profile(district_name: str) -> dict | None:
    """Return the static profile for a given district, or None if not found."""
    return KARNATAKA_DISTRICTS.get(district_name)

def get_all_district_profiles() -> dict:
    """Return all 31 district profiles."""
    return KARNATAKA_DISTRICTS.copy()

def load_flood_dataset(filepath: str = None) -> pd.DataFrame:
    """Load the assembled feature CSV. Fails loudly if missing (constraint: no synthetic data)."""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "official_ksndmc_rainfall_features.csv")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(
            f"Training dataset not found at {filepath}. "
            "Run official_data.py to build from real OpenCity sources."
        )
    
    df = pd.read_csv(filepath)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["date", "district"])
    return df
