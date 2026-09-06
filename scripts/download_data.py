import os
import json
import requests
from datetime import datetime, timezone

DATA_RAW_DIR = "data/raw"
os.makedirs(DATA_RAW_DIR, exist_ok=True)

def create_provenance(filepath, source_url):
    provenance = {
        "classification": "REAL",
        "source": source_url,
        "retrieval_date": datetime.now(timezone.utc).isoformat()
    }
    with open(filepath + ".provenance.json", "w") as f:
        json.dump(provenance, f, indent=4)
    print(f"Created provenance for {filepath}")

def download_file(url, dest_name):
    filepath = os.path.join(DATA_RAW_DIR, dest_name)
    print(f"Downloading {dest_name} from {url}...")
    response = requests.get(url)
    response.raise_for_status()
    with open(filepath, "wb") as f:
        f.write(response.content)
    create_provenance(filepath, url)
    return filepath

def fix_bom_encoding(filepath):
    print(f"Fixing BOM encoding for {filepath}...")
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

def download_ifi_data():
    url = "https://raw.githubusercontent.com/hydrosenselab/India-Flood-Inventory/main/v3.0/India_Flood_Inventory_v3.csv"
    dest = "India_Flood_Inventory_v3.csv"
    filepath = download_file(url, dest)
    fix_bom_encoding(filepath)

def download_kgis_data():
    district_url = "https://raw.githubusercontent.com/samashti/KGIS/main/data/output/District_Boundaries.gpkg.zip"
    download_file(district_url, "District_Boundaries.gpkg.zip")

    taluk_url = "https://raw.githubusercontent.com/samashti/KGIS/main/data/output/Taluk_Boundaries.gpkg.zip"
    download_file(taluk_url, "Taluk_Boundaries.gpkg.zip")

def download_other_stubs():
    # IMD, KSNDMC, CWC, SRTM, SMAP, LULC
    # These require specific API interactions or manual fetching
    print("Skipping IMD, KSNDMC, CWC, SRTM, SMAP, LULC - requires API keys or manual auth/bounding-box drawing.")

def main():
    print("Starting Day 2 Data Acquisition...")
    download_ifi_data()
    download_kgis_data()
    download_other_stubs()
    print("Data acquisition complete.")

if __name__ == "__main__":
    main()
