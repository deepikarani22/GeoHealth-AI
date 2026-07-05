# backend/ml_service/inference_xgb.py

import joblib
import numpy as np
from pathlib import Path

from ml_service.model_mapping import (
    build_feature_vector,
    TARGET_LIST,
    TARGET_TO_RISK_NAME
)

# ---------------------------------------------------
# Load trained model & scaler
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "training" / "models" / "xgb_env_health_model.pkl"
SCALER_PATH = BASE_DIR / "training" / "processed" / "scaler.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# ---------------------------------------------------
# Public inference function
# ---------------------------------------------------

def predict_environmental_risk(env_features: dict) -> dict:
    """
    env_features:
        Output of OpenAQ + OpenMeteo + NDVI + static landcover

    Returns:
        Dict of disease-group → risk score (0–1 normalized)
    """

    # 1️⃣ Build ordered feature vector
    x = build_feature_vector(env_features)
    x = np.array(x).reshape(1, -1)

    # 2️⃣ Scale using TRAINING scaler
    x_scaled = scaler.transform(x)

    # 3️⃣ Predict multi-output prevalence
    y_pred = model.predict(x_scaled)[0]

    # 4️⃣ Map outputs to disease groups
    results = {}

    for idx, target in enumerate(TARGET_LIST):
        risk_name = TARGET_TO_RISK_NAME[target]

        # Clamp for safety
        score = float(np.clip(y_pred[idx], 0.0, 1.0))

        results[risk_name] = score

    return results
