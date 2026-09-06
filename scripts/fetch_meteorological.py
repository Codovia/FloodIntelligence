import os
import json
import imdlib as imd
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

def fetch_imd_rainfall(start_yr=2020, end_yr=2023):
    print(f"Fetching IMD rainfall data from {start_yr} to {end_yr}...")
    # The imdlib will download the .grd files directly to the directory
    imd.get_data('rain', start_yr, end_yr, fn_format='yearwise', file_dir=DATA_RAW_DIR)
    
    # Generate provenance for each downloaded file
    for year in range(start_yr, end_yr + 1):
        filename = f"rain_{year}.grd"
        filepath = os.path.join(DATA_RAW_DIR, filename)
        if os.path.exists(filepath):
            create_provenance(filepath, f"IMD Gridded Rainfall API via imdlib (Year {year})")
        else:
            print(f"Warning: {filename} not found after download attempt.")
            
def main():
    print("Starting Meteorological Data Extraction...")
    fetch_imd_rainfall(2020, 2022) # Keeping range small for initial dev
    print("Meteorological extraction complete.")

if __name__ == "__main__":
    main()
