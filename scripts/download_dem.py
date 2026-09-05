import os
import json
import geopandas as gpd
import elevation
import rasterio

def main():
    os.makedirs('data/raw/dem', exist_ok=True)
    out_path = os.path.join(os.getcwd(), 'data/raw/dem/karnataka_srtm.tif')
    
    print("Loading Karnataka bounds...")
    gdf = gpd.read_file("data/raw/karnataka_districts.geojson")
    bounds = gdf.total_bounds # [minx, miny, maxx, maxy]
    
    # Add a small buffer just in case
    left = bounds[0] - 0.05
    bottom = bounds[1] - 0.05
    right = bounds[2] + 0.05
    top = bounds[3] + 0.05
    
    print(f"Clipping DEM for bounds: left={left}, bottom={bottom}, right={right}, top={top}")
    if not os.path.exists(out_path):
        elevation.clip(bounds=(left, bottom, right, top), output=out_path, max_download_tiles=100)
    
    print(f"DEM saved to {out_path}")
    
    # Inspect DEM
    with rasterio.open(out_path) as src:
        arr = src.read(1)
        valid_mask = arr != src.nodata
        
        valid_arr = arr[valid_mask]
        
        report = {
            "CRS": str(src.crs),
            "Resolution (degrees)": list(src.res),
            "Bounds": list(src.bounds),
            "Min Elevation (m)": float(valid_arr.min()) if valid_arr.size > 0 else None,
            "Max Elevation (m)": float(valid_arr.max()) if valid_arr.size > 0 else None,
            "NoData Value": src.nodata,
            "NoData Percentage": float((~valid_mask).sum() / arr.size * 100),
            "Tile Completeness": "Valid" if valid_arr.size > 0 else "Invalid"
        }
        
    with open("data/raw/dem/dem_inspection_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()
