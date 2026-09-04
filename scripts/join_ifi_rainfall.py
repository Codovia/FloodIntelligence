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
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    df['End Date'] = pd.to_datetime(df['End Date'], errors='coerce')
    
    # Filter to events where we have downloaded IMD data
    downloaded_files = [f for f in os.listdir('data/raw/rainfall_imd') if f.endswith('.grd')]
    cached_years = sorted([int(f.split('_')[1].split('.')[0]) for f in downloaded_files])
    
    df = df[df['Start Date'].dt.year.isin(cached_years)].copy()
    
    # Initialize features
    df['rain_1d'] = np.nan
    df['rain_3d'] = np.nan
    df['rain_7d'] = np.nan
    df['rain_lag_1d'] = np.nan
    
    print(f"Joining {len(df)} events with cached rainfall data...")
    
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
            # imdlib xarray indexing
            val = datasets[date.year].sel(time=date.strftime('%Y-%m-%d')).rain.values
            return float(val)
        except Exception:
            return np.nan

    for idx, row in df.iterrows():
        start_date = row['Start Date']
        if pd.isna(start_date):
            continue
            
        # Mathematical convention:
        # rain_1d: rainfall on the exact Start Date
        # rain_3d: sum of rainfall from Start Date - 2 days to Start Date
        # rain_7d: sum of rainfall from Start Date - 6 days to Start Date
        # rain_lag_1d: rainfall on the day immediately preceding the Start Date
        
        try:
            r1 = get_rainfall_for_date(start_date)
            
            r3 = sum([get_rainfall_for_date(start_date - pd.Timedelta(days=i)) for i in range(3)])
            r7 = sum([get_rainfall_for_date(start_date - pd.Timedelta(days=i)) for i in range(7)])
            rlag1 = get_rainfall_for_date(start_date - pd.Timedelta(days=1))
            
            df.at[idx, 'rain_1d'] = r1
            df.at[idx, 'rain_3d'] = r3
            df.at[idx, 'rain_7d'] = r7
            df.at[idx, 'rain_lag_1d'] = rlag1
            
        except Exception as e:
            print(f"Error processing row {idx}: {e}")
            
    output_path = "data/interim/karnataka_rainfall_join.csv"
    df.to_csv(output_path, index=False)
    print(f"Successfully joined {len(df)} records and saved to {output_path}")

if __name__ == '__main__':
    perform_join()
