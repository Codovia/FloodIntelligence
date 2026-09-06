import os
import json
import requests
from datetime import datetime, timezone
import argparse

DATA_RAW_DIR = "data/raw"
os.makedirs(DATA_RAW_DIR, exist_ok=True)

# Bounding box roughly covering Karnataka: min_lon, min_lat, max_lon, max_lat
KARNATAKA_BBOX = (74.0, 11.5, 78.5, 18.5)

def create_provenance(filepath, source_url):
    provenance = {
        "classification": "REAL",
        "source": source_url,
        "retrieval_date": datetime.now(timezone.utc).isoformat()
    }
    with open(filepath + ".provenance.json", "w") as f:
        json.dump(provenance, f, indent=4)
    print(f"Created provenance for {filepath}")

def fetch_srtm(api_key):
    print("Fetching SRTM 30m DEM from OpenTopography...")
    if not api_key:
        print("ERROR: OpenTopography API key required. Provide via --ot-key.")
        return
        
    url = "https://portal.opentopography.org/API/globaldem"
    params = {
        "demtype": "SRTMGL1",
        "south": KARNATAKA_BBOX[1],
        "north": KARNATAKA_BBOX[3],
        "west": KARNATAKA_BBOX[0],
        "east": KARNATAKA_BBOX[2],
        "outputFormat": "GTiff",
        "API_Key": api_key
    }
    
    filepath = os.path.join(DATA_RAW_DIR, "karnataka_srtm30m.tif")
    response = requests.get(url, params=params, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        create_provenance(filepath, "https://portal.opentopography.org/API/globaldem")
    else:
        print(f"Failed to fetch SRTM: {response.status_code} - {response.text}")

def fetch_gee_stubs():
    print("Google Earth Engine datasets (SMAP, LULC) extraction will be placed here.")
    print("Requires `earthengine authenticate` to be run on the host system first.")

def main():
    parser = argparse.ArgumentParser(description="Fetch Spatial & Satellite Data")
    parser.add_argument("--ot-key", type=str, help="OpenTopography API Key")
    args = parser.parse_args()

    print("Starting Spatial Data Extraction...")
    fetch_srtm(args.ot_key)
    fetch_gee_stubs()
    print("Spatial extraction complete.")

if __name__ == "__main__":
    main()
