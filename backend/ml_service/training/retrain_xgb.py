# ml_service/training/retrain_xgb_49.py

import json
import joblib
import pandas as pd
import numpy as np

from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from sklearn.metrics import r2_score

# -------------------------------------------------
# PATHS
# -------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = Path(r"D:\geohealthai\backend\ml_service\training\raw\training_dataset.csv")
ARTIFACTS_DIR = BASE_DIR / "artifacts"

ARTIFACTS_DIR.mkdir(exist_ok=True)

FEATURES_PATH = ARTIFACTS_DIR / "feature_list.json"
TARGETS_PATH = ARTIFACTS_DIR / "target_list.json"

# -------------------------------------------------
# LOAD FEATURE / TARGET DEFINITIONS
# -------------------------------------------------
with open(FEATURES_PATH) as f:
    FEATURES = json.load(f)

with open(TARGETS_PATH) as f:
    TARGETS = json.load(f)

print(f"✅ Features locked: {len(FEATURES)}")
print(f"✅ Targets locked: {len(TARGETS)}")

# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------
df = pd.read_csv(DATA_PATH)

# sanity checks
missing_f = [f for f in FEATURES if f not in df.columns]
missing_t = [t for t in TARGETS if t not in df.columns]

assert not missing_f, f"❌ Missing features: {missing_f}"
assert not missing_t, f"❌ Missing targets: {missing_t}"

X = df[FEATURES].astype(float)
Y = df[TARGETS].astype(float)

print("📊 Raw shapes:", X.shape, Y.shape)

# -------------------------------------------------
# HANDLE MISSING VALUES (SAFE)
# -------------------------------------------------
X = X.fillna(X.median())
Y = Y.fillna(Y.median())

# -------------------------------------------------
# SPLIT
# -------------------------------------------------
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.2, random_state=42
)

# -------------------------------------------------
# SCALE FEATURES (ONLY FEATURES)
# -------------------------------------------------
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -------------------------------------------------
# MODEL
# -------------------------------------------------
base_model = XGBRegressor(
    n_estimators=300,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.9,
    colsample_bytree=0.9,
    objective="reg:squarederror",
    random_state=42,
)

model = MultiOutputRegressor(base_model)

print("🚀 Training XGBoost...")
model.fit(X_train_scaled, Y_train)

# -------------------------------------------------
# EVALUATION
# -------------------------------------------------
Y_pred = model.predict(X_test_scaled)

r2 = r2_score(Y_test, Y_pred, multioutput="uniform_average")
print(f"📈 Overall R²: {r2:.4f}")

# -------------------------------------------------
# SAVE ARTIFACTS
# -------------------------------------------------
joblib.dump(model, ARTIFACTS_DIR / "xgb_model.pkl")
joblib.dump(scaler, ARTIFACTS_DIR / "scaler.pkl")

print("💾 Saved:")
print(" - xgb_model.pkl")
print(" - scaler.pkl")
print(" - feature_list.json")
print(" - target_list.json")
