# File-system path utilities and environment variable access.
import os
# Warning controls for cross-version pickle loading noise.
import warnings
# Suppress Joblib's optional parallelism warning in restricted environments.
warnings.filterwarnings(
    "ignore",
    message=r".*joblib will operate in serial mode.*",
    category=UserWarning,
)
# Load serialized scikit-learn model artifacts.
import joblib
# Numpy type checks for model output normalization.
import numpy as np
# DataFrame wrapper to preserve model feature ordering.
import pandas as pd
try:
    # Raised by sklearn when model file version differs from runtime version.
    from sklearn.exceptions import InconsistentVersionWarning
except Exception:
    InconsistentVersionWarning = None

# Absolute directory path for backend files.
BASE_DIR = os.path.dirname(__file__)
# Path to model artifact, overrideable via MODEL_PATH env variable.
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "model.pkl"))

if not os.path.exists(MODEL_PATH):
    # Fail fast if model artifact is missing at startup.
    raise RuntimeError(
        "model.pkl not found in backend/. Place it there and restart."
    )

# Load model artifact (either model directly or dict containing metadata).
if InconsistentVersionWarning is not None:
    # Keep startup logs clean when model was serialized on a different sklearn version.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
        model_artifact = joblib.load(MODEL_PATH)
else:
    model_artifact = joblib.load(MODEL_PATH)
print("✅ model.pkl loaded successfully.")

if isinstance(model_artifact, dict):
    # Support artifact format: {"model": ..., "features": [...]}.
    model = model_artifact.get("model")
    feature_order = model_artifact.get("features")
    # Optional custom integer/string status mapping stored in artifact.
    artifact_int_status_map = model_artifact.get("int_status_map")
    artifact_string_status_map = model_artifact.get("string_status_map")
else:
    # Support artifact format: raw estimator object.
    model = model_artifact
    feature_order = None
    artifact_int_status_map = None
    artifact_string_status_map = None

if model is None:
    # Guard against malformed artifact dictionary.
    raise RuntimeError("❌ Loaded model artifact is invalid: missing `model` key.")

# Final feature order used to build model input dataframe.
# Priority:
# 1) features list provided in artifact dict
# 2) scikit-learn feature_names_in_ from loaded model
# 3) default project feature order
FEATURE_ORDER = feature_order or list(getattr(model, "feature_names_in_", [])) or [
    "distance",
    "ttc",
    "axis",
    "speed",
    "steering_angle",
    "relative_velocity",
]

# Integer class output mapping expected by older numeric-label models.
STATUS_MAP = artifact_int_status_map or {0: "HIGH RISK", 1: "RISK", 2: "SAFE"}
# String class output mapping expected by current text-label models.
STRING_STATUS_MAP = artifact_string_status_map or {
    "safe": "SAFE",
    "warning": "RISK",
    "danger": "HIGH RISK",
    "risk": "RISK",
    "high risk": "HIGH RISK",
}


def normalize_prediction_label(raw_prediction):
    # Convert integer/numpy integer prediction labels to API status strings.
    if isinstance(raw_prediction, (np.integer, int)):
        return STATUS_MAP.get(int(raw_prediction), str(raw_prediction))
    # Normalize free-form string labels to canonical API statuses.
    if isinstance(raw_prediction, str):
        normalized = raw_prediction.strip().lower()
        return STRING_STATUS_MAP.get(normalized, raw_prediction.strip().upper())
    # Fallback for unexpected model output types.
    return str(raw_prediction)


def predict_status(sensor_values: dict) -> str:
    # Build single-row dataframe in exact feature order expected by model.
    input_df = pd.DataFrame([sensor_values])[FEATURE_ORDER]
    # Run model inference and extract first prediction.
    raw_prediction = model.predict(input_df)[0]
    # Convert raw prediction to API-friendly status label.
    return normalize_prediction_label(raw_prediction)
