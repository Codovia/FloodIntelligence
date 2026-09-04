import pandas as pd
import imdlib as imd
import os
import xarray as xr
import numpy as np
import datetime

def spatial_mean_rainfall(ds, lat_min=11.5, lat_max=18.5, lon_min=74.0, lon_max=78.5):
    """
    Since IFI events are given as district lists rather than exact coordinates, 
    and we haven't loaded complex shapefiles yet, we approximate the spatial join 
    by computing the mean rainfall over a bounding box that roughly covers Karnataka.
    For a production system, this should use exact district geometry masking.
    """
    mask_lon = (ds.lon >= lon_min) & (ds.lon <= lon_max)
    mask_lat = (ds.lat >= lat_min) & (ds.lat <= lat_max)
    return ds.where(mask_lon & mask_lat, drop=True).mean(dim=['lat', 'lon'])

def perform_join():
    events_file = "data/interim/karnataka_flood_events.csv"
    df = pd.read_csv(events_file)
    df['Start Date'] = pd.to_datetime(df['Start Date'], dayfirst=True, errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], dayfirst=True, errors='coerce')
    
    # Filter to events where we have downloaded IMD data
    downloaded_files = [f for f in os.listdir('data/raw/rainfall_imd') if f.endswith('.grd')]
    cached_years = sorted([int(f.split('_')[1].split('.')[0]) for f in downloaded_files])
    
    has_cached = df['Start Date'].dt.year.isin(cached_years)
    df_cached = df[has_cached].copy()
    
    # Initialize features
    df_cached['rain_1d'] = np.nan
    df_cached['rain_3d'] = np.nan
    df_cached['rain_7d'] = np.nan
    df_cached['rain_lag_1d'] = np.nan
    
    print(f"Joining {len(df_cached)} events with cached rainfall data...")
    
    # Load available xarray datasets
    datasets = {}
    for y in cached_years:
        data = imd.open_data('rain', y, y, 'yearwise', 'data/raw/rainfall_imd')
        ds = data.get_xarray()
        datasets[y] = spatial_mean_rainfall(ds)
    
    def get_rainfall_for_date(date):
        if pd.isna(date) or date.year not in datasets:
            return np.nan
        try:
            val = datasets[date.year].sel(time=date.strftime('%Y-%m-%d')).rain.values
            return float(val)
        except Exception:
            return np.nan

    for idx, row in df_cached.iterrows():
        start_date = row['Start Date']
        if pd.isna(start_date):
            continue
            
        try:
            r1 = get_rainfall_for_date(start_date)
            r3 = sum([get_rainfall_for_date(start_date - pd.Timedelta(days=i)) for i in range(3)])
            r7 = sum([get_rainfall_for_date(start_date - pd.Timedelta(days=i)) for i in range(7)])
            rlag1 = get_rainfall_for_date(start_date - pd.Timedelta(days=1))
            
            df_cached.at[idx, 'rain_1d'] = r1
            df_cached.at[idx, 'rain_3d'] = r3
            df_cached.at[idx, 'rain_7d'] = r7
            df_cached.at[idx, 'rain_lag_1d'] = rlag1
            
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            
    output_path = "data/interim/karnataka_rainfall_join.csv"
    df_cached.to_csv(output_path, index=False)
    print(f"Successfully joined {len(df_cached)} records and saved to {output_path}")

    # Build coverage report
    usable = df_cached['rain_1d'].notna().sum()
    report = {
        "Total Karnataka IFI events": len(df),
        "Events with usable NWDP rainfall": 0,
        "Events without usable NWDP rainfall": len(df),
        "Events with usable IMD rainfall": int(usable),
        "Events without usable IMD rainfall": int(len(df) - usable),
        "rain_1d coverage": int(df_cached['rain_1d'].notna().sum()),
        "rain_3d coverage": int(df_cached['rain_3d'].notna().sum()),
        "rain_7d coverage": int(df_cached['rain_7d'].notna().sum()),
        "rain_lag_1d coverage": int(df_cached['rain_lag_1d'].notna().sum()),
        "Primary rainfall source recommendation": "IMD 0.25 gridded (via imdlib)",
        "Secondary/cross-check source": "None (NWDP API inaccessible)",
        "Spatial join method": "Bounding box approximation (lon: 74-78.5, lat: 11.5-18.5) spatial mean. Pending exact district polygon masking.",
        "Temporal join method": "rain_1d=exact date, rain_3d=sum(t-2 to t), rain_7d=sum(t-6 to t), rain_lag_1d=t-1"
    }
    
    import json
    with open("data/interim/rainfall_coverage_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=4))

if __name__ == '__main__':
    perform_join()
