import pandas as pd

df = pd.read_csv('data/interim/karnataka_flood_events.csv')
print("Total records:", len(df))
cols_of_interest = ['Start Date', 'End Date', 'Latitude', 'Longitude', 'Districts', 'District_LGD_Codes', 'Severity', 'Location', 'Extent of damage ']

print("\nMissing values for columns of interest:")
print(df[cols_of_interest].isna().sum())

print("\nSample records:")
print(df[cols_of_interest].head(5).to_string())

# Check if Latitude/Longitude are unique or centroid-like
unique_coords = df[['Latitude', 'Longitude']].drop_duplicates()
print(f"\nUnique coordinate pairs: {len(unique_coords)} out of {len(df)} records")

# Inspect Severity
print("\nSeverity value counts:")
print(df['Severity'].value_counts(dropna=False))
