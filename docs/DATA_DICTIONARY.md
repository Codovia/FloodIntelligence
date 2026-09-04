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

*(Note: Rainfall amounts are spatially averaged over a bounding box approximation for Karnataka. In production, this should use exact district geometry masking.)*
