import pandas as pd
import glob

files = glob.glob('data/raw/flood_inventory/*.csv')
for file in files:
    try:
        df = pd.read_csv(file)
        print(f"\n--- {file} ---")
        print(df.head(2))
        print(f"Total rows: {len(df)}")
        print("Columns:", df.columns.tolist())
        # check if there's a state column
        state_cols = [c for c in df.columns if 'state' in c.lower()]
        if state_cols:
            karnataka_df = df[df[state_cols[0]].str.contains('Karnataka', case=False, na=False)]
            print(f"Rows matching Karnataka: {len(karnataka_df)}")
    except Exception as e:
        print(f"Error reading {file}: {e}")
