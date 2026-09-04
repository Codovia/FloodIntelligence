import pandas as pd

input_file = 'data/raw/flood_inventory/India_Flood_Inventory_v3.csv'
output_file = 'data/interim/karnataka_flood_events.csv'

df = pd.read_csv(input_file)
# Filter for Karnataka
karnataka_df = df[df['State'].str.contains('Karnataka', case=False, na=False)].copy()

# Sort by Start Date
karnataka_df['Start Date'] = pd.to_datetime(karnataka_df['Start Date'], errors='coerce')
karnataka_df = karnataka_df.sort_values(by='Start Date')

karnataka_df.to_csv(output_file, index=False)
print(f"Extracted {len(karnataka_df)} events for Karnataka.")
print(f"Date coverage: {karnataka_df['Start Date'].min()} to {karnataka_df['Start Date'].max()}")
