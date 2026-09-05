import pandas as pd
import numpy as np
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
import os
import json

def calculate_slope_array(elevation_arr, cellsize_x, cellsize_y):
    """
    Calculate slope from elevation array.
    cellsize_x and cellsize_y should be in meters.
    Returns slope in degrees.
    """
    dz_dx, dz_dy = np.gradient(elevation_arr, cellsize_x, cellsize_y)
    slope = np.arctan(np.sqrt(dz_dx**2 + dz_dy**2)) * (180 / np.pi)
    return slope

def main():
    # 1. Load Geometries
    print("Loading district polygons...")
    districts_gdf = gpd.read_file("data/raw/karnataka_districts.geojson")
    districts_metric = districts_gdf.to_crs(epsg=32643)
    
    # 2. Process Rivers
    print("Loading river network...")
    rivers_gdf = gpd.read_file("data/raw/rivers/river_network.geojson")
    
    print("Clipping rivers to Karnataka...")
    karnataka_bounds = districts_gdf.total_bounds
    rivers_subset = rivers_gdf.cx[karnataka_bounds[0]:karnataka_bounds[2], karnataka_bounds[1]:karnataka_bounds[3]]
    rivers_metric = rivers_subset.to_crs(epsg=32643)
    
    print("Calculating river density per district...")
    district_river_density = {}
    for idx, row in districts_metric.iterrows():
        d_name = row['Dist_Name'].lower().strip()
        geom = row['geometry']
        d_area_km2 = geom.area / 1e6
        
        intersected = gpd.clip(rivers_metric, geom)
        total_river_length_m = intersected.geometry.length.sum() if not intersected.empty else 0
        total_river_length_km = total_river_length_m / 1000.0
        
        density = total_river_length_km / d_area_km2 if d_area_km2 > 0 else 0
        district_river_density[d_name] = density

    # 3. Process DEM
    dem_path = "data/raw/dem/karnataka_srtm.tif"
    print(f"Loading DEM from {dem_path}...")
    
    district_mean_elev = {}
    district_mean_slope = {}
    
    if os.path.exists(dem_path):
        with rasterio.open(dem_path) as src:
            arr = src.read(1)
            affine = src.transform
            nodata = src.nodata
            
            arr_masked = np.where(arr == nodata, np.nan, arr)
            res_x, res_y = src.res
            
            # Approx conversion to meters at Karnataka's center latitude
            lat_center = 15.0
            cellsize_x_m = res_x * 111320.0 * np.cos(np.radians(lat_center))
            cellsize_y_m = res_y * 111320.0
            
            print("Calculating slope...")
            slope_arr = calculate_slope_array(arr_masked, cellsize_x_m, cellsize_y_m)
            slope_arr = np.nan_to_num(slope_arr, nan=-9999.0)
            
            print("Computing zonal stats for elevation...")
            elev_stats = zonal_stats(districts_gdf, dem_path, stats="mean", nodata=nodata)
            
            print("Computing zonal stats for slope...")
            slope_stats = zonal_stats(districts_gdf, slope_arr, affine=affine, stats="mean", nodata=-9999.0)
            
            for idx, row in districts_gdf.iterrows():
                d_name = row['Dist_Name'].lower().strip()
                district_mean_elev[d_name] = elev_stats[idx]['mean']
                district_mean_slope[d_name] = slope_stats[idx]['mean']
    else:
        print("DEM file not found!")

    # 4. Join to Candidates
    print("Loading candidate dataset...")
    df = pd.read_csv("data/interim/district_training_candidates.csv")
    
    df['mean_elevation'] = df['District'].map(district_mean_elev)
    df['mean_slope'] = df['District'].map(district_mean_slope)
    df['river_density_km_per_sqkm'] = df['District'].map(district_river_density)
    
    if 'distance_to_major_river' in df.columns:
        df = df.drop(columns=['distance_to_major_river'])
        
    out_csv = "data/interim/district_features.csv"
    df.to_csv(out_csv, index=False)
    print(f"Saved featured dataset to {out_csv}")
    
    # 5. Coverage and Leakage checks
    total_rows = len(df)
    elev_rows = df['mean_elevation'].notna().sum()
    slope_rows = df['mean_slope'].notna().sum()
    river_rows = df['river_density_km_per_sqkm'].notna().sum()
    
    dupes = df.duplicated(subset=['District', 'Date']).sum()
    
    report = {
        "Total district x day rows": int(total_rows),
        "Rows with elevation": int(elev_rows),
        "Rows with slope": int(slope_rows),
        "Rows with river feature": int(river_rows),
        "Rows with land-cover feature": 0,
        "Coverage % (Elevation)": float(elev_rows / total_rows * 100),
        "Coverage % (Slope)": float(slope_rows / total_rows * 100),
        "Coverage % (River Density)": float(river_rows / total_rows * 100),
        "Missing % (Elevation)": float(100 - (elev_rows / total_rows * 100)),
        "Missing % (Slope)": float(100 - (slope_rows / total_rows * 100)),
        "Missing % (River Density)": float(100 - (river_rows / total_rows * 100)),
        "Number of districts": int(df['District'].nunique()),
        "Date range": f"{df['Date'].min()} to {df['Date'].max()}",
        "Duplicate rows": int(dupes),
        "Positive events by year": df[df['label']==1]['Date'].astype(str).str[:4].value_counts().to_dict(),
        "Positive events by district (top 5)": df[df['label']==1]['District'].value_counts().head(5).to_dict(),
        "Unique flood events": "Determined chronologically by connected positive components",
        "Average positive days per district": float(df[df['label']==1].groupby('District').size().mean()) if len(df[df['label']==1]) > 0 else 0
    }
    
    with open("data/interim/static_feature_coverage_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))

if __name__ == "__main__":
    main()
