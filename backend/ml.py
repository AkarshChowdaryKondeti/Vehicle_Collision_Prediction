import os
import warnings

warnings.filterwarnings(
    "ignore",
    message=r".*joblib will operate in serial mode.*",
    category=UserWarning,
)
import joblib
import numpy as np
import pandas as pd

try:
    from sklearn.exceptions import InconsistentVersionWarning
except Exception:
    InconsistentVersionWarning = None

BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "model.pkl"))

if not os.path.exists(MODEL_PATH):
    raise RuntimeError(
        "model.pkl not found in backend/. Place it there and restart."
    )

if InconsistentVersionWarning is not None:
    # Ignore sklearn version-noise from the serialized model.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
        model_artifact = joblib.load(MODEL_PATH)
else:
    model_artifact = joblib.load(MODEL_PATH)
print("✅ model.pkl loaded successfully.")

if isinstance(model_artifact, dict):
    model = model_artifact.get("model")
    feature_order = model_artifact.get("features")
    artifact_int_status_map = model_artifact.get("int_status_map")
    artifact_string_status_map = model_artifact.get("string_status_map")
else:
    model = model_artifact
    feature_order = None
    artifact_int_status_map = None
    artifact_string_status_map = None

if model is None:
    raise RuntimeError("❌ Loaded model artifact is invalid: missing `model` key.")

# Prefer artifact features, then model metadata, then project defaults.
FEATURE_ORDER = feature_order or list(getattr(model, "feature_names_in_", [])) or [
    "distance",
    "ttc",
    "axis",
    "speed",
    "steering_angle",
    "relative_velocity",
]

STATUS_MAP = artifact_int_status_map or {0: "HIGH RISK", 1: "RISK", 2: "SAFE"}
STRING_STATUS_MAP = artifact_string_status_map or {
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
