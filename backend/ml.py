import os
import joblib
import numpy as np
import pandas as pd

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "model.pkl"))

if not os.path.exists(MODEL_PATH):
    raise RuntimeError(
        "model.pkl not found in backend/. Place it there and restart."
    )

model_artifact = joblib.load(MODEL_PATH)
print("✅ model.pkl loaded successfully.")

if isinstance(model_artifact, dict):
    model = model_artifact.get("model")
    feature_order = model_artifact.get("features")
else:
    model = model_artifact
    feature_order = None

if model is None:
    raise RuntimeError("❌ Loaded model artifact is invalid: missing `model` key.")

FEATURE_ORDER = feature_order or [
    "distance",
    "ttc",
    "axis",
    "speed",
    "steering_angle",
    "relative_velocity",
]

STATUS_MAP = {0: "HIGH RISK", 1: "RISK", 2: "SAFE"}
STRING_STATUS_MAP = {
    "safe": "SAFE",
    "warning": "RISK",
    "danger": "HIGH RISK",
    "risk": "RISK",
    "high risk": "HIGH RISK",
}


def normalize_prediction_label(raw_prediction):
    if isinstance(raw_prediction, (np.integer, int)):
        return STATUS_MAP.get(int(raw_prediction), str(raw_prediction))
    if isinstance(raw_prediction, str):
        normalized = raw_prediction.strip().lower()
        return STRING_STATUS_MAP.get(normalized, raw_prediction.strip().upper())
    return str(raw_prediction)


def predict_status(sensor_values: dict) -> str:
    input_df = pd.DataFrame([sensor_values])[FEATURE_ORDER]
    raw_prediction = model.predict(input_df)[0]
    return normalize_prediction_label(raw_prediction)
