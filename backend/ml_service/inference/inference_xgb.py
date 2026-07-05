#from ml_service.inference.model_loader import model, scaler
import joblib
import numpy as np
from pathlib import Path
from ml_service.inference.feature_store import FeatureStore
from ml_service.model_mapping import TARGET_ORDER
from shared.schemas import LocationInput
#from ml_service.feature_store.feature_store import FeatureStore
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = BASE_DIR / "training" / "artifacts" / "xgb_model.pkl"
SCALER_PATH = BASE_DIR / "training" / "artifacts" / "scaler.pkl"

model = joblib.load(Path(r"D:\geohealthai\backend\ml_service\training\artifacts\xgb_model.pkl"))
scaler = joblib.load(Path(r"D:\geohealthai\backend\ml_service\training\artifacts\scaler.pkl"))

# ml_service/inference/inference_xgb.py

import json

with open(Path(r"D:\geohealthai\backend\ml_service\training\artifacts\feature_list.json")) as f:
    FEATURE_LIST = json.load(f)

with open(Path(r"D:\geohealthai\backend\ml_service\training\artifacts\target_list.json")) as f:
    TARGET_LIST = json.load(f)


def predict_env_risks(env_features: dict) -> dict:
    """
    env_features: dict produced by Feature Store
    """

    # 🔒 FEATURE LOCK (CRITICAL)
    X = np.array([
        env_features.get(fname, 0.0)
        for fname in FEATURE_LIST
    ]).reshape(1, -1)

    X_scaled = scaler.transform(X)
    preds = model.predict(X_scaled)[0]

    return {
        TARGET_LIST[i]: float(preds[i])
        for i in range(len(TARGET_LIST))
    }





"""import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent / "training"

MODEL_PATH = BASE_DIR / "models" / "xgb_env_health_model.pkl"
FEATURES_PATH = BASE_DIR / "processed" / "feature_list.json"
TARGETS_PATH = BASE_DIR / "processed" / "target_list.json"

# Load artifacts
model = joblib.load(MODEL_PATH)

with open(FEATURES_PATH) as f:
    FEATURE_LIST = json.load(f)

with open(TARGETS_PATH) as f:
    TARGET_LIST = json.load(f)


def predict_environmental_risk(env_features: dict) -> dict:
    "
    env_features: dict of environmental values (same keys as training features)
    returns: disease-group risk scores
    "

    # Build feature vector
    x = np.array([env_features.get(f, 0.0) for f in FEATURE_LIST]).reshape(1, -1)

    # Predict
    y_pred = model.predict(x)[0]

    return {
        TARGET_LIST[i]: float(y_pred[i])
        for i in range(len(TARGET_LIST))
    }"""
