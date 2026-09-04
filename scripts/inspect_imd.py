import imdlib as imd
import os

try:
    data = imd.open_data('rain', 2023, 2023, 'yearwise', 'data/raw/rainfall_imd')
    ds = data.get_xarray()
    print("Dataset dimensions:", ds.dims)
    print("Coordinates:", list(ds.coords.keys()))
    print("Lat min, max:", ds.lat.min().values, ds.lat.max().values)
    print("Lon min, max:", ds.lon.min().values, ds.lon.max().values)
    print("Time range:", ds.time.min().values, ds.time.max().values)
    
    # Check resolution
    print("Lat resolution:", float(ds.lat[1] - ds.lat[0]))
    print("Lon resolution:", float(ds.lon[1] - ds.lon[0]))
    
except Exception as e:
    print(e)
