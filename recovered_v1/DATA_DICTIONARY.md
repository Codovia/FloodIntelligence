# Data Dictionary

## India Flood Inventory (IFI) - Karnataka Extraction
*Path: `data/interim/karnataka_flood_events.csv`*

| Column | Data Type | Description |
|---|---|---|
| `Start Date` | DateTime | The starting date of the reported flood event. |
| `End Date` | DateTime | The end date of the reported flood event. |
| `Latitude` / `Longitude` | Float | Coordinates of the event. (Found to be mostly NaN/missing for Karnataka). |
| `Districts` | String | Comma-separated list of affected districts. |
| `District_LGD_Codes` | String | Comma-separated LGD codes for the affected districts. |
| `Severity` | String | Qualitative severity index. |

## Rainfall Join Features
*Path: `data/interim/karnataka_rainfall_join.csv`*

| Column | Data Type | Description | Mathematical Convention |
|---|---|---|---|
| `rain_1d` | Float | Daily rainfall on the `Start Date`. | $R(t)$ |
| `rain_3d` | Float | Sum of daily rainfall for the 3-day window ending on the `Start Date`. | $\sum_{i=0}^{2} R(t-i)$ |
| `rain_7d` | Float | Sum of daily rainfall for the 7-day window ending on the `Start Date`. | $\sum_{i=0}^{6} R(t-i)$ |
| `rain_lag_1d` | Float | Daily rainfall on the day immediately preceding the `Start Date`. | $R(t-1)$ |

## District-Level Training Candidates
*Path: `data/interim/district_training_candidates.csv`*

| Column | Data Type | Description |
|---|---|---|
| `District` | String | Standardized district name. |
| `Date` | DateTime | The specific day (representing the 'district x day' temporal unit). |
| `label` | Integer (0/1) | Target variable. 1 if the district was identified in an IFI flood event for this day. 0 if not identified. |
| `rain_1d` | Float | IMD rainfall on `Date` |
| `rain_3d` | Float | 3-day rolling sum of IMD rainfall |
| `rain_7d` | Float | 7-day rolling sum of IMD rainfall |
| `rain_lag_1d` | Float | IMD rainfall on `Date - 1` |
| `mean_elevation` | Float | (Pending) District mean elevation |
| `mean_slope` | Float | (Pending) District mean slope |
| `distance_to_major_river` | Float | (Pending) Distance to nearest major river |
