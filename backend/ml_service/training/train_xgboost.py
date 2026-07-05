# train_xgboost.py

import json
import joblib
import numpy as np
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import mean_squared_error, r2_score

from xgboost import XGBRegressor

# -------------------------------------------------
# Paths
# -------------------------------------------------
BASE = Path(__file__).resolve().parent
PROCESSED = BASE / "processed"
MODELS = BASE / "models"
MODELS.mkdir(exist_ok=True)

# -------------------------------------------------
# Load data
# -------------------------------------------------
print("📄 Loading processed data...")

X = np.load(PROCESSED / "X.npy")
Y = np.load(PROCESSED / "Y.npy")

with open(PROCESSED / "feature_list.json") as f:
    FEATURE_NAMES = json.load(f)

with open(PROCESSED / "target_list.json") as f:
    TARGET_NAMES = json.load(f)

print(f"✔ X: {X.shape}")
print(f"✔ Y: {Y.shape}")
print(f"✔ Features: {len(FEATURE_NAMES)}")
print(f"✔ Targets: {len(TARGET_NAMES)}")

# -------------------------------------------------
# Train / Test split (NO GROUPS NEEDED)
# -------------------------------------------------
X_train, X_test, Y_train, Y_test = train_test_split(
    X,
    Y,
    test_size=0.2,
    random_state=42
)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")

# -------------------------------------------------
# Model
# -------------------------------------------------
print("🚀 Training multi-output XGBoost model...")

base_model = XGBRegressor(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    random_state=42,
    n_jobs=-1
)

model = MultiOutputRegressor(base_model)
model.fit(X_train, Y_train)

print("✔ Training complete!")

# -------------------------------------------------
# Evaluation
# -------------------------------------------------
Y_pred = model.predict(X_test)

rmse = mean_squared_error(Y_test, Y_pred) ** 0.5
r2 = r2_score(Y_test, Y_pred)

print(f"\n📊 Evaluation")
print(f"🔍 RMSE (overall): {rmse:.6f}")
print(f"🔍 R²  (overall): {r2:.4f}")

print("\n📈 Per-target R²:")
for i, name in enumerate(TARGET_NAMES):
    score = r2_score(Y_test[:, i], Y_pred[:, i])
    print(f"  {name}: {score:.4f}")

# -------------------------------------------------
# Save model
# -------------------------------------------------
model_path = MODELS / "xgb_env_health_model.pkl"
joblib.dump(model, model_path)

print(f"\n💾 Model saved → {model_path}")
print("🎉 Training pipeline finished successfully.")









"""import json
import joblib
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputRegressor
from sklearn.metrics import r2_score, mean_squared_error
from xgboost import XGBRegressor

# -----------------------------
# Paths
# -----------------------------
BASE = Path(__file__).parent
PROC = BASE / "processed"
MODEL_DIR = BASE / "models"
MODEL_DIR.mkdir(exist_ok=True)

# -----------------------------
# Load processed data
# -----------------------------
print("📄 Loading training matrices...")

X = np.load(PROC / "train_features.npy")
Y = np.load(PROC / "train_labels.npy")

with open(PROC / "feature_list.json") as f:
    FEATURES = json.load(f)

with open(PROC / "target_list.json") as f:
    TARGETS = json.load(f)

print(f"✔ X: {X.shape}")
print(f"✔ Y: {Y.shape}")
print(f"✔ Features: {len(FEATURES)}")
print(f"✔ Targets: {len(TARGETS)}")

# -----------------------------
# Train / Test split
# -----------------------------
X_train, X_test, Y_train, Y_test = train_test_split(
    X, Y, test_size=0.15, random_state=42
)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")

# -----------------------------
# XGBoost base model
# -----------------------------
xgb = XGBRegressor(
    n_estimators=400,
    max_depth=6,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    n_jobs=-1,
    random_state=42
)

model = MultiOutputRegressor(xgb)

# -----------------------------
# Training
# -----------------------------
print("🚀 Training multi-output XGBoost model...")
model.fit(X_train, Y_train)
print("✔ Training complete!")

# -----------------------------
# Evaluation
# -----------------------------
print("📊 Evaluating model...")
Y_pred = model.predict(X_test)

from sklearn.metrics import mean_squared_error
import numpy as np

rmse = np.sqrt(mean_squared_error(Y_test, Y_pred))

r2 = r2_score(Y_test, Y_pred, multioutput="uniform_average")

print(f"🔍 RMSE (overall): {rmse:.6f}")
print(f"🔍 R²  (overall): {r2:.4f}")

print("\n📈 Per-target R²:")
for i, name in enumerate(TARGETS):
    score = r2_score(Y_test[:, i], Y_pred[:, i])
    print(f"  {name}: {score:.4f}")

# -----------------------------
# Save model + metadata
# -----------------------------
joblib.dump(
    {
        "model": model,
        "features": FEATURES,
        "targets": TARGETS
    },
    MODEL_DIR / "xgb_env_health_model.pkl"
)

print(f"\n💾 Model saved → {MODEL_DIR / 'xgb_env_health_model.pkl'}")
print("🎉 Training pipeline finished successfully.")"""
