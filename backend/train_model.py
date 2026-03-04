# =============================================================
# train_model.py
# Vehicle Safety Prediction - ML Training Script
# Run this script ONCE before starting the FastAPI server.
# It will:
#   1. Generate a synthetic vehicle sensor dataset
#   2. Train a Random Forest classifier
#   3. Save model.pkl and scaler.pkl to the backend folder
# =============================================================

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
import joblib
import os

# ── Reproducibility ──────────────────────────────────────────
np.random.seed(42)

# =============================================================
# STEP 1: Generate Synthetic Dataset
# =============================================================
# We simulate realistic vehicle sensor readings for 5000 samples.
# Each sample belongs to one of three safety categories:
#   safe     → plenty of distance, low speed, calm steering
#   warning  → moderate conditions
#   danger   → close distance, high speed, sharp steering

N = 5000  # total number of samples

def generate_samples(n, label, distance_range, ttc_range, speed_range,
                     steering_range, rv_range, axis_range):
    """Generate n sensor samples for a given safety label."""
    return pd.DataFrame({
        "distance":         np.random.uniform(*distance_range, n),
        "ttc":              np.random.uniform(*ttc_range,      n),
        "axis":             np.random.uniform(*axis_range,     n),
        "speed":            np.random.uniform(*speed_range,    n),
        "steering_angle":   np.random.uniform(*steering_range, n),
        "relative_velocity":np.random.uniform(*rv_range,       n),
        "status":           label
    })

# --- Generate per-class samples ---
safe_df = generate_samples(
    int(N * 0.40), "safe",
    distance_range=(30, 120), ttc_range=(5, 15),
    speed_range=(0, 60),      steering_range=(-10, 10),
    rv_range=(-5, 5),         axis_range=(-0.2, 0.2)
)

warning_df = generate_samples(
    int(N * 0.35), "warning",
    distance_range=(10, 35),  ttc_range=(2, 6),
    speed_range=(40, 100),    steering_range=(-25, 25),
    rv_range=(-15, 15),       axis_range=(-0.5, 0.5)
)

danger_df = generate_samples(
    int(N * 0.25), "danger",
    distance_range=(0, 12),   ttc_range=(0, 3),
    speed_range=(70, 160),    steering_range=(-45, 45),
    rv_range=(-30, 30),       axis_range=(-1.0, 1.0)
)

# --- Combine and shuffle ---
df = pd.concat([safe_df, warning_df, danger_df], ignore_index=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# =============================================================
# STEP 2: Add Noise for Realism
# =============================================================
# Add Gaussian noise to all numeric features (simulates sensor jitter).
feature_cols = ["distance", "ttc", "axis", "speed", "steering_angle", "relative_velocity"]
noise_scale  = 0.02  # 2% noise

for col in feature_cols:
    noise = np.random.normal(0, noise_scale * df[col].std(), len(df))
    df[col] = df[col] + noise

# --- Label flipping: flip ~2% of labels for realism ---
flip_idx = np.random.choice(df.index, size=int(0.02 * len(df)), replace=False)
label_map = {"safe": "warning", "warning": "danger", "danger": "safe"}
df.loc[flip_idx, "status"] = df.loc[flip_idx, "status"].map(label_map)

# --- Save dataset ---
os.makedirs("../data", exist_ok=True)
df.to_csv("../data/vehicle_dataset.csv", index=False)
print(f"✅ Dataset saved → ../data/vehicle_dataset.csv  ({len(df)} rows)")
print(df["status"].value_counts())

# =============================================================
# STEP 3: Prepare Features and Labels
# =============================================================
X = df[feature_cols]
y = df["status"]

# --- Scale features ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- Train / Test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X_scaled, y, test_size=0.2, random_state=42, stratify=y
)

# =============================================================
# STEP 4: Hyperparameter Tuning with GridSearchCV
# =============================================================
print("\n🔍 Running GridSearchCV for hyperparameter tuning...")

param_grid = {
    "n_estimators":     [100, 200],
    "max_depth":        [None, 10, 20],
    "min_samples_split":[2, 5],
    "min_samples_leaf": [1, 2],
}

rf = RandomForestClassifier(random_state=42, n_jobs=-1)

grid_search = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    cv=5,                 # 5-fold cross-validation inside grid search
    scoring="accuracy",
    n_jobs=-1,
    verbose=1
)
grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_
print(f"\n✅ Best Parameters: {grid_search.best_params_}")
print(f"✅ Best CV Accuracy: {grid_search.best_score_:.4f}")

# =============================================================
# STEP 5: Cross-Validation on Best Model
# =============================================================
print("\n📊 5-Fold Cross-Validation Scores:")
cv_scores = cross_val_score(best_model, X_scaled, y, cv=5, scoring="accuracy", n_jobs=-1)
for i, score in enumerate(cv_scores, 1):
    print(f"   Fold {i}: {score:.4f}")
print(f"   Mean: {cv_scores.mean():.4f}  |  Std: {cv_scores.std():.4f}")

# =============================================================
# STEP 6: Evaluate on Test Set
# =============================================================
y_pred = best_model.predict(X_test)
print(f"\n📈 Test Set Accuracy: {accuracy_score(y_test, y_pred):.4f}")
print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred))

# =============================================================
# STEP 7: Feature Importance
# =============================================================
print("\n🌲 Feature Importance (Random Forest):")
importances = best_model.feature_importances_
for col, imp in sorted(zip(feature_cols, importances), key=lambda x: -x[1]):
    bar = "█" * int(imp * 50)
    print(f"   {col:<22} {imp:.4f}  {bar}")

# =============================================================
# STEP 8: Save Model and Scaler
# =============================================================
joblib.dump(best_model, "model.pkl")
joblib.dump(scaler,     "scaler.pkl")
print("\n✅ model.pkl  saved → backend/model.pkl")
print("✅ scaler.pkl saved → backend/scaler.pkl")
print("\n🚀 Training complete! You can now run the FastAPI server.")
