import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
import joblib

DATA_PROCESSED_DIR = "data/processed"
MODEL_DIR = "backend/ml_model"
os.makedirs(MODEL_DIR, exist_ok=True)

def train_model():
    print("Starting Machine Learning Pipeline...")
    features_path = os.path.join(DATA_PROCESSED_DIR, "features.csv")
    
    if not os.path.exists(features_path):
        print(f"ERROR: {features_path} not found. Run feature_engineering.py first.")
        return
        
    df = pd.read_csv(features_path)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date') # Crucial for Time-based split
    
    # Define features and target
    # Target 'flood_event' would be derived from India Flood Inventory
    feature_cols = ['rain_3d_sum', 'rain_7d_sum', 'rain_1d_lag', 'daily_rainfall_mm']
    
    # Drop NaNs created by rolling windows
    df = df.dropna(subset=feature_cols + ['flood_event'])
    
    X = df[feature_cols]
    y = df['flood_event']
    
    # Strict Time-Based Split (Constraint: No Random k-fold on temporal data)
    print("Configuring TimeSeriesSplit...")
    tscv = TimeSeriesSplit(n_splits=3)
    
    # Model: Class-weighted Random Forest (Addressing class imbalance of rare floods)
    rf = RandomForestClassifier(class_weight='balanced', random_state=42)
    
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [5, 10, None]
    }
    
    print("Starting Grid Search CV...")
    grid_search = GridSearchCV(estimator=rf, param_grid=param_grid, cv=tscv, scoring='roc_auc', n_jobs=-1)
    grid_search.fit(X, y)
    
    best_model = grid_search.best_estimator_
    print(f"Best parameters found: {grid_search.best_params_}")
    
    # Save Model
    model_out = os.path.join(MODEL_DIR, "rf_model.pkl")
    joblib.dump(best_model, model_out)
    print(f"Model trained and saved to {model_out}")
    print("NOTE: Model outputs continuous probabilities via `predict_proba()`.")

if __name__ == "__main__":
    train_model()
