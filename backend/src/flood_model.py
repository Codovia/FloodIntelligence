"""
flood_model.py — Random Forest classifier for flood risk prediction.
Pipeline: ColumnTransformer (numeric passthrough + OHE) -> RandomForestClassifier
Output: continuous probabilities + blended operational risk index.
"""
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score, precision_score,
    recall_score, f1_score, confusion_matrix
)

ARTIFACT_VERSION = 2
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
MODEL_PATH = os.path.join(MODEL_DIR, "flood_risk_model.pkl")

NUMERIC_FEATURES = [
    "rainfall_mm", "rainfall_3day", "rainfall_7day",
    "reservoir_level", "reservoir_storage_percent",
    "distance_to_river_km", "elevation_m", "slope",
    "past_flood_count", "drainage_score"
]

CATEGORICAL_FEATURES = ["district", "taluk"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES
TARGET_COLUMN = "risk_level"

def _build_pipeline() -> Pipeline:
    """Construct the sklearn Pipeline with ColumnTransformer."""
    preprocessor = ColumnTransformer([
        ("num", "passthrough", NUMERIC_FEATURES),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES)
    ])
    model = RandomForestClassifier(
        n_estimators=280,
        max_depth=12,
        min_samples_leaf=4,
        random_state=42,
        class_weight="balanced_subsample"
    )
    return Pipeline([("preprocessor", preprocessor), ("model", model)])

def _temporal_cutoff(df: pd.DataFrame) -> tuple:
    """Time-based train/test split at 80th percentile date."""
    unique_dates = sorted(df["date"].unique())
    cutoff_idx = min(max(1, int(len(unique_dates) * 0.8)), len(unique_dates) - 1)
    cutoff_date = unique_dates[cutoff_idx]
    
    train = df[df["date"] < cutoff_date]
    test = df[df["date"] >= cutoff_date]
    return train, test, str(cutoff_date)

def _feature_importance(pipeline: Pipeline, feature_names: list) -> list:
    """Extract Gini-based feature importances from the fitted RF."""
    rf = pipeline.named_steps["model"]
    preprocessor = pipeline.named_steps["preprocessor"]
    
    # Get all feature names after transformation
    try:
        ohe = preprocessor.named_transformers_["cat"]
        cat_names = list(ohe.get_feature_names_out(CATEGORICAL_FEATURES))
    except:
        cat_names = []
    
    all_names = NUMERIC_FEATURES + cat_names
    importances = rf.feature_importances_
    
    # Aggregate OHE features back to original categorical
    result = []
    for i, name in enumerate(NUMERIC_FEATURES):
        if i < len(importances):
            result.append({"feature": name, "importance": round(float(importances[i]), 4)})
    
    # Sum OHE importance for each categorical
    ohe_start = len(NUMERIC_FEATURES)
    if cat_names:
        cat_imp = float(np.sum(importances[ohe_start:]))
        result.append({"feature": "district+taluk (categorical)", "importance": round(cat_imp, 4)})
    
    result.sort(key=lambda x: x["importance"], reverse=True)
    return result

def _operational_risk_index(payload: dict) -> float:
    """Compute heuristic operational risk score (0-100) from physical features."""
    score = 0.0
    score += min(payload.get("rainfall_mm", 0) / 40.0, 1.0) * 16.0
    score += min(payload.get("rainfall_3day", 0) / 100.0, 1.0) * 22.0
    score += min(payload.get("rainfall_7day", 0) / 220.0, 1.0) * 26.0
    score += min(payload.get("reservoir_storage_percent", 0) / 100.0, 1.0) * 10.0
    score += min(payload.get("drainage_score", 0) / 100.0, 1.0) * 12.0
    score += min(payload.get("past_flood_count", 0) / 8.0, 1.0) * 8.0
    score += (1 - min(payload.get("distance_to_river_km", 10) / 10.0, 1.0)) * 4.0
    score += (1 - min(payload.get("elevation_m", 900) / 900.0, 1.0)) * 4.0
    return round(score, 2)

def _risk_level_from_score(probability: float, op_score: float, model_level: str) -> str:
    """Determine final risk level from blended probability and operational score."""
    if probability >= 0.76 or op_score >= 75:
        return "High"
    if probability >= 0.52 or op_score >= 52:
        return "Medium"
    if model_level == "High" and op_score >= 60:
        return "High"
    if model_level == "Medium" and op_score >= 40:
        return "Medium"
    return "Low"

def main_factors(payload: dict) -> list:
    """Generate human-readable explanation list for the prediction."""
    factors = []
    r7 = payload.get("rainfall_7day", 0)
    r3 = payload.get("rainfall_3day", 0)
    elev = payload.get("elevation_m", 500)
    river = payload.get("distance_to_river_km", 5)
    drain = payload.get("drainage_score", 50)
    
    if r7 > 200: factors.append("High 7-day cumulative rainfall")
    elif r7 > 100: factors.append("Moderate 7-day cumulative rainfall")
    if r3 > 80: factors.append("Heavy 3-day rainfall")
    if elev < 100: factors.append("Low elevation (coastal/floodplain)")
    if river < 2: factors.append("Close proximity to river")
    if drain > 60: factors.append("Poor drainage infrastructure")
    if payload.get("reservoir_storage_percent", 0) > 80:
        factors.append("Near-full reservoir capacity")
    if payload.get("past_flood_count", 0) > 5:
        factors.append("High historical flood frequency")
    
    return factors if factors else ["No significant risk factors identified"]

def predict_flood_risk(artifact: dict, payload: dict) -> dict:
    """Run inference on a single data point.
    Returns structured prediction with probabilities and explanations."""
    pipeline = artifact["pipeline"]
    
    row = {col: payload.get(col) for col in FEATURE_COLUMNS}
    x = pd.DataFrame([row])
    
    probabilities = pipeline.predict_proba(x)[0]
    classes = list(pipeline.named_steps["model"].classes_)
    prob_by_class = dict(zip(classes, probabilities))
    ordered = sorted(prob_by_class.items(), key=lambda i: i[1], reverse=True)
    
    model_risk_level = ordered[0][0]
    model_probability = float(ordered[0][1])
    second_probability = float(ordered[1][1]) if len(ordered) > 1 else 0.0
    
    op_score = _operational_risk_index(payload)
    blended = 0.6 * model_probability + 0.4 * (op_score / 100.0)
    risk_level = _risk_level_from_score(blended, op_score, model_risk_level)
    confidence = round(0.45 + min(max(model_probability - second_probability, 0.0), 0.5), 3)
    
    from .drainage_risk import drainage_level, reservoir_status
    
    return {
        "district": payload.get("district", "Unknown"),
        "risk_level": risk_level,
        "model_risk_level": model_risk_level,
        "flood_probability": round(blended, 4),
        "confidence_score": confidence,
        "operational_risk_index": op_score,
        "main_factors": main_factors(payload),
        "drainage_risk_level": drainage_level(payload.get("drainage_score", 0)),
        "reservoir_status": reservoir_status(payload.get("reservoir_storage_percent", 0)),
    }

def load_or_train_model(df: pd.DataFrame) -> dict:
    """Load existing model or train a new one from the dataset."""
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Try loading existing model
    if os.path.exists(MODEL_PATH):
        try:
            artifact = joblib.load(MODEL_PATH)
            if (artifact.get("version") == ARTIFACT_VERSION and
                "validation_strategy" in artifact.get("metrics", {})):
                print(f"Loaded model v{ARTIFACT_VERSION} from {MODEL_PATH}")
                return artifact
        except Exception as e:
            print(f"Failed to load model: {e}. Retraining...")
    
    # Train new model
    print("Training new flood risk model...")
    required = FEATURE_COLUMNS + [TARGET_COLUMN, "date"]
    df_clean = df.dropna(subset=[c for c in required if c in df.columns]).copy()
    
    if len(df_clean) < 100:
        raise ValueError(f"Insufficient training data: {len(df_clean)} rows. Need at least 100.")
    
    X = df_clean[FEATURE_COLUMNS]
    y = df_clean[TARGET_COLUMN]
    
    # Temporal split
    train_df, test_df, cutoff = _temporal_cutoff(df_clean)
    X_train, y_train = train_df[FEATURE_COLUMNS], train_df[TARGET_COLUMN]
    X_test, y_test = test_df[FEATURE_COLUMNS], test_df[TARGET_COLUMN]
    
    print(f"Train: {len(X_train)} rows (before {cutoff}), Test: {len(X_test)} rows (after)")
    
    # Fit evaluation pipeline
    eval_pipeline = _build_pipeline()
    eval_pipeline.fit(X_train, y_train)
    y_pred = eval_pipeline.predict(X_test)
    
    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "balanced_accuracy": round(balanced_accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, average="weighted", zero_division=0), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred, labels=sorted(y.unique())).tolist(),
        "classes": sorted(y.unique().tolist()),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "validation_strategy": "Temporal holdout by date",
        "cutoff_date": cutoff,
    }
    
    print(f"Evaluation metrics: Acc={metrics['accuracy']}, F1={metrics['f1_score']}, "
          f"Balanced Acc={metrics['balanced_accuracy']}")
    
    # Fit deployment pipeline on ALL data
    deploy_pipeline = _build_pipeline()
    deploy_pipeline.fit(X, y)
    
    importance = _feature_importance(deploy_pipeline, FEATURE_COLUMNS)
    
    artifact = {
        "version": ARTIFACT_VERSION,
        "pipeline": deploy_pipeline,
        "metrics": metrics,
        "feature_importance": importance,
    }
    
    joblib.dump(artifact, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    return artifact
