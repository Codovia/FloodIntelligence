# Initial data dictionary

## District-day modelling table

| Field | Type | Meaning |
| --- | --- | --- |
| `district_id` | string | Stable source identifier for a Karnataka district |
| `event_date` | date | UTC/local source date, documented explicitly |
| `label` | integer | `1` if IFI identifies the district as affected on that date; otherwise `0` under the inventory interpretation |
| `rain_1d` | float | Daily rainfall aggregate |
| `rain_3d` | float | Three-day rainfall aggregate |
| `rain_7d` | float | Seven-day rainfall aggregate |
| `rain_lag_1d` | float | Prior-day rainfall aggregate |
| `mean_elevation` | float | District polygon mean elevation from SRTM |
| `mean_slope` | float | District polygon mean slope from a metric terrain workflow |

Missing values must remain explicit and be handled by a documented pipeline
decision. They must never be silently filled.

The rainfall transformer requires one real aggregated observation per
`district_id` and `observation_date`. It emits only dates with a complete
seven-day history; missing history is an error, not an imputation opportunity.

## Label construction

The pipeline takes candidate district-days from observed rainfall coverage and
marks `label = 1` when the same `district_id` and `event_date` occur in the
verified IFI event extract. It does not generate a calendar of negatives.
Duplicate candidates, missing identifiers, invalid dates, and empty event files
fail the pipeline.
