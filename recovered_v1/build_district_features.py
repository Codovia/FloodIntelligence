import pandas as pd
import numpy as np
import geopandas as gpd
import imdlib as imd
import os
import json
import warnings
warnings.filterwarnings("ignore")

def build_dataset():
    # 1. Load Geometries
    gdf = gpd.read_file("data/raw/karnataka_districts.geojson")
    districts = gdf['Dist_Name'].str.lower().str.strip().unique().tolist()
    
    # 2. Load Events
    events_df = pd.read_csv("data/interim/karnataka_flood_events.csv")
    events_df['Start Date'] = pd.to_datetime(events_df['Start Date'], dayfirst=True, errors='coerce')
    events_df['End Date'] = pd.to_datetime(events_df['End Date'], dayfirst=True, errors='coerce')
    
    # Define time period (years we have cached rainfall for)
    cached_years = [2020, 2021, 2022, 2023]
    start_date = pd.Timestamp('2020-01-01')
    end_date = pd.Timestamp('2023-12-31')
    
    # Create base grid: District x Day
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    records = []
    for d in districts:
        for dt in date_range:
            records.append({"District": d, "Date": dt})
    
    base_df = pd.DataFrame(records)
    base_df['label'] = 0
    
    # 3. Label Positives
    # If a district is in an event's 'Districts' list, and Date is between Start and End Date
    for _, row in events_df.dropna(subset=['Start Date', 'End Date', 'Districts']).iterrows():
        event_start = row['Start Date']
        event_end = row['End Date']
        # if event_end is before event_start, fix it or ignore
        if event_end < event_start:
            event_end = event_start
            
        affected = str(row['Districts']).lower()
        
        # We find which base_df districts are mentioned
        for d in districts:
            if d in affected: # Simple string match for POC
                mask = (base_df['District'] == d) & (base_df['Date'] >= event_start) & (base_df['Date'] <= event_end)
                base_df.loc[mask, 'label'] = 1
                
    # 4. Feature Engineering (Rainfall)
    # Load all xarray data
    datasets = {}
    for y in cached_years:
        data = imd.open_data('rain', y, y, 'yearwise', 'data/raw/rainfall_imd')
        ds = data.get_xarray()
        datasets[y] = ds

    def get_district_mean_rain(district_geom, year):
        # We clip/mask the dataset. For POC speed without rioxarray, we use bounding box mean.
        bounds = district_geom.bounds
        lon_min, lat_min, lon_max, lat_max = bounds
        ds = datasets[year]
        mask_lon = (ds.lon >= lon_min) & (ds.lon <= lon_max)
        mask_lat = (ds.lat >= lat_min) & (ds.lat <= lat_max)
        return ds.where(mask_lon & mask_lat, drop=True).mean(dim=['lat', 'lon'])
    
    print("Pre-calculating spatial mean rainfall for all districts...")
    district_rain_series = {}
    for _, row in gdf.iterrows():
        d_name = row['Dist_Name'].lower().strip()
        geom = row['geometry']
        series = []
        for y in cached_years:
            ds_mean = get_district_mean_rain(geom, y)
            series.append(ds_mean.rain.to_dataframe())
        
        d_df = pd.concat(series)
        # Ensure time is index
        d_df.index = pd.to_datetime(d_df.index)
        district_rain_series[d_name] = d_df['rain']

    print("Computing features...")
    # Add features
    base_df['rain_1d'] = np.nan
    base_df['rain_3d'] = np.nan
    base_df['rain_7d'] = np.nan
    base_df['rain_lag_1d'] = np.nan
    
    # We can use pandas rolling on the precalculated series
    for d in districts:
        if d not in district_rain_series:
            continue
        ts = district_rain_series[d]
        df_mask = base_df['District'] == d
        
        # Map values
        dates = base_df.loc[df_mask, 'Date']
        
        r1 = ts.reindex(dates).values
        rlag1 = ts.shift(1).reindex(dates).values
        r3 = ts.rolling(window=3, min_periods=1).sum().reindex(dates).values
        r7 = ts.rolling(window=7, min_periods=1).sum().reindex(dates).values
        
        base_df.loc[df_mask, 'rain_1d'] = r1
        base_df.loc[df_mask, 'rain_lag_1d'] = rlag1
        base_df.loc[df_mask, 'rain_3d'] = r3
        base_df.loc[df_mask, 'rain_7d'] = r7

    # Static features
    base_df['mean_elevation'] = np.nan
    base_df['mean_slope'] = np.nan
    base_df['distance_to_major_river'] = np.nan
    
    output_path = "data/interim/district_training_candidates.csv"
    base_df.to_csv(output_path, index=False)
    print(f"Saved {len(base_df)} candidates to {output_path}")

    # Generate Reports
    positives = base_df[base_df['label'] == 1]
    negatives = base_df[base_df['label'] == 0]
    
    label_def = {
        "Final spatial unit": "District polygon",
        "Final temporal unit": "Day",
        "Positive-label definition": "label = 1 if the district is identified as affected by an IFI flood event that overlaps with the given day.",
        "Negative-label definition": "label = 0 if the district is not identified as affected in the available IFI inventory for the given day. Limitation: This means 'not identified', rather than 'confirmed no flood'.",
        "Number of positive observations": len(positives),
        "Number of candidate negatives": len(negatives),
        "Class balance": f"{len(positives) / len(base_df):.4%}"
    }
    
    with open("data/interim/label_definition_report.json", "w") as f:
        json.dump(label_def, f, indent=4)
        
    feat_cov = {
        "Rainfall feature coverage (rain_1d)": int(base_df['rain_1d'].notna().sum()),
        "Rainfall feature coverage (rain_7d)": int(base_df['rain_7d'].notna().sum()),
        "Static feature coverage (mean_elevation)": int(base_df['mean_elevation'].notna().sum()),
        "Static feature coverage (mean_slope)": int(base_df['mean_slope'].notna().sum()),
        "Missing-data problems": "Static topological features (elevation, slope, river proximity) have 0 coverage because we lack a DEM dataset. Need SRTM or equivalent download.",
        "Remaining methodological risks": "Heavy class imbalance due to 'district x day' granularity. Many '0' labels might be unreported minor floods.",
        "Recommended next step": "Download SRTM DEM data to calculate topological features, and apply undersampling/SMOTE or class weights during model training."
    }
    
    with open("data/interim/feature_coverage_report.json", "w") as f:
        json.dump(feat_cov, f, indent=4)
        
    for k, v in label_def.items():
        print(f"{k}: {v}")
    for k, v in feat_cov.items():
        print(f"{k}: {v}")

if __name__ == '__main__':
    build_dataset()
