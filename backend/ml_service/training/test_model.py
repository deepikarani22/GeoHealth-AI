from ..inference.feature_store import FeatureStore

fs = FeatureStore()
x = fs.build_vector({"pm25": 30})
print(x.shape)  # MUST be (1, 49)




"""import json
import numpy as np
from pathlib import Path
from xgboost import Booster

import importlib.util

spec = importlib.util.spec_from_file_location(
    "model_mapping",
    str(Path(__file__).resolve().parents[1] / "model_mapping.py")
)
model_mapping = importlib.util.module_from_spec(spec)
spec.loader.exec_module(model_mapping)

build_feature_vector = model_mapping.build_feature_vector

# -------------------------------------------------------------------
# Paths
# -------------------------------------------------------------------
MODEL_DIR = Path("D:/geohealthai/backend/ml_service/model")

# -------------------------------------------------------------------
# Load model + metadata
# -------------------------------------------------------------------
model_path = MODEL_DIR / "xgb_model.json"
feature_list = json.load(open(MODEL_DIR / "feature_list.json"))
target_list = json.load(open(MODEL_DIR / "target_list.json"))

print("Loaded model with:")
print(" - Features:", len(feature_list))
print(" - Targets:", len(target_list))

# Load model
model = Booster()
model.load_model(str(model_path))

# -------------------------------------------------------------------
# Create a test input
# -------------------------------------------------------------------
test_input = {
    "age": 55,
    "smoking": 1,
    "alcohol": 0,
    "exercise_low": 1,
    "poor_diet": 1,
}

# Build vector
x = build_feature_vector(test_input, feature_list)
x = np.array(x).reshape(1, -1)

print("\nFeature vector shape:", x.shape)

# -------------------------------------------------------------------
# Run prediction
# -------------------------------------------------------------------
pred = model.infer(x)

print("\nRaw prediction output:", pred)

# -------------------------------------------------------------------
# Map outputs to disease names
# -------------------------------------------------------------------
mapped = dict(zip(target_list, pred[0].tolist()))

print("\nDisease probability map:")
for k, v in mapped.items():
    print(f"  {k}: {v:.3f}")"""
