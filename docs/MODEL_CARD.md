# Model card — initial baseline

No model has been trained yet, so no performance metrics are reported.

## Intended use

The planned model provides a district-level decision-support likelihood from
historical rainfall and static terrain features. It is not an official warning,
hydraulic forecast, or household-level prediction.

## Planned model

Class-weighted Random Forest using `rain_1d`, `rain_3d`, `rain_7d`,
`rain_lag_1d`, `mean_elevation`, and `mean_slope`.

## Evaluation requirements

The primary split will be chronological, with later observations held out from
training. Reports must include precision, recall, F1, confusion matrix,
per-class metrics, valid ROC-AUC, class counts, and the exact split dates.

