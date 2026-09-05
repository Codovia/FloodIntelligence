import os
import requests

def download_rivers():
    os.makedirs('data/raw/rivers', exist_ok=True)
    out_path = 'data/raw/rivers/river_network.geojson'
    
    url = "https://nwdp.nwic.gov.in/dataset/3209962f-d0ff-45b8-910a-209bf69a0ccf/resource/6e552705-842d-40a4-92b2-8506bb66df2a/download/river_network.geojson"
    print(f"Downloading river network from {url}...")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(out_path, 'wb') as f:
            f.write(response.content)
        print(f"Successfully downloaded to {out_path} ({os.path.getsize(out_path)} bytes)")
    except Exception as e:
        print(f"Failed to download river network: {e}")

if __name__ == "__main__":
    download_rivers()
