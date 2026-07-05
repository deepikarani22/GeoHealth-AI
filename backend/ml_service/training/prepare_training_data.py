# prepare_training_data.py
# ==========================================
# Leakage-safe preprocessing for CBSA-level
# SatHealth training dataset
# ==========================================

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

# ------------------------------------------
# Paths
# ------------------------------------------
BASE_DIR = Path(__file__).parent
RAW_PATH = BASE_DIR / "raw" / "training_dataset.csv"
OUT_DIR = BASE_DIR / "processed"
OUT_DIR.mkdir(exist_ok=True)

# ------------------------------------------
# Load dataset
# ------------------------------------------
print("📄 Loading dataset...")
df = pd.read_csv(RAW_PATH)
print(f"✔ Loaded shape: {df.shape}")

# ------------------------------------------
# Target columns (ICD L1 only)
# ------------------------------------------
TARGETS = [
    "prev_A00-B99",
    "prev_C00-D49",
    "prev_D50-D89",
    "prev_E00-E89",
    "prev_F01-F99",
    "prev_G00-G99",
    "prev_H00-H59",
    "prev_H60-H95",
    "prev_I00-I99",
    "prev_J00-J99",
    "prev_K00-K95",
]

# sanity check
missing_targets = [c for c in TARGETS if c not in df.columns]
assert not missing_targets, f"❌ Missing target columns: {missing_targets}"

# ------------------------------------------
# Feature selection (STRICT leakage control)
# ------------------------------------------
EXCLUDE_COLS = (
    ["CBSAFP", "year"] +
    TARGETS +
    [c for c in df.columns if c.startswith("prev_")]
)

FEATURES = [c for c in df.columns if c not in EXCLUDE_COLS]

print(f"🧮 Features selected: {len(FEATURES)}")
print(f"🩺 Targets selected: {len(TARGETS)}")

X = df[FEATURES]
Y = df[TARGETS]

# ------------------------------------------
# Handle missing values
# ------------------------------------------
# Features → mean imputation
feature_imputer = SimpleImputer(strategy="mean")
X_imputed = feature_imputer.fit_transform(X)

# Targets → DO NOT impute (they are ground truth)
assert Y.isna().mean().max() < 1.0, "❌ All targets are NaN"

# ------------------------------------------
# Feature scaling
# ------------------------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_imputed)

# ------------------------------------------
# Final shapes
# ------------------------------------------
assert X_scaled.shape[0] > 0, "❌ Empty X matrix"
assert Y.shape[0] > 0, "❌ Empty Y matrix"

print(f"✔ Final X shape: {X_scaled.shape}")
print(f"✔ Final Y shape: {Y.shape}")

# ------------------------------------------
# Save outputs
# ------------------------------------------
np.save(OUT_DIR / "X.npy", X_scaled)
np.save(OUT_DIR / "Y.npy", Y.values)

with open(OUT_DIR / "feature_list.json", "w") as f:
    json.dump(FEATURES, f, indent=2)

with open(OUT_DIR / "target_list.json", "w") as f:
    json.dump(TARGETS, f, indent=2)

print("✅ Preprocessing complete!")
print(f"📁 Saved to: {OUT_DIR}")






"""import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.preprocessing import StandardScaler

# --------------------------------------------------
# CONFIG
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "raw"
OUT_DIR = BASE_DIR / "processed"
OUT_DIR.mkdir(exist_ok=True)

DATASET_PATH = RAW_DIR / "final_training_dataset.csv"

# ✔ FINAL agreed ICD-L1 targets (ONLY THESE)
TARGET_COLS = [
    "prev_A00_B99",  # Infectious
    "prev_C00_D49",  # Cancer
    "prev_D50_D89",  # Blood
    "prev_E00_E89",  # Metabolic
    "prev_F01_F99",  # Mental
    "prev_G00_G99",  # Neuro
    "prev_H00_H59",  # Eye
    "prev_H60_H95",  # Ear
    "prev_I00_I99",  # Cardiac
    "prev_J00_J99",  # Respiratory
    "prev_K00_K95",  # Digestive
]

# Columns NEVER used for ML
DROP_COLS_CONTAINS = [
    "year", "month", "lat", "lon",
    "CBSAFP", "ZCTA5"
]

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

print(f"📄 Loading dataset: {DATASET_PATH}")
df = pd.read_csv(DATASET_PATH)

print(f"✔ Loaded shape: {df.shape}")

# --------------------------------------------------
# CLEAN DUPLICATE / BAD COLUMNS
# --------------------------------------------------

# Drop duplicated columns if any
df = df.loc[:, ~df.columns.duplicated()]

# Drop obvious junk ICD columns (L2/L3 style)
bad_icd_cols = [
    c for c in df.columns
    if c.startswith(("L00-", "M00-", "N00-", "O00-", "P00-", "Q00-", "R00-", "S00-", "U00-", "V00-", "Z00-"))
]

if bad_icd_cols:
    print(f"🧹 Dropping invalid ICD columns: {bad_icd_cols}")
    df = df.drop(columns=bad_icd_cols)

# --------------------------------------------------
# TARGET HANDLING (IMPORTANT)
# --------------------------------------------------

print("🩺 Processing target columns...")

# Ensure all targets exist
missing_targets = [c for c in TARGET_COLS if c not in df.columns]
if missing_targets:
    raise ValueError(f"❌ Missing target columns: {missing_targets}")

# Fill NaN targets with COLUMN MEAN (regional average)
for col in TARGET_COLS:
    mean_val = df[col].mean()
    df[col] = df[col].fillna(mean_val)

# ----------------------------------------
# Handle missing ICD targets (CRITICAL FIX)
# ----------------------------------------

print("🩺 Processing target columns with imputation...")

target_cols = [
    "prev_A00_B99", "prev_C00_D49", "prev_D50_D89", "prev_E00_E89",
    "prev_F01_F99", "prev_G00_G99", "prev_H00_H59", "prev_H60_H95",
    "prev_I00_I99", "prev_J00_J99", "prev_K00_K95"
]

# Ensure numeric
df[target_cols] = df[target_cols].apply(pd.to_numeric, errors="coerce")

# Step 1: CBSA-wise mean imputation
for col in target_cols:
    df[col] = df.groupby("CBSAFP")[col].transform(
        lambda x: x.fillna(x.mean())
    )

# Step 2: Global mean fallback
for col in target_cols:
    df[col] = df[col].fillna(df[col].mean())

# Step 3: Absolute fallback
df[target_cols] = df[target_cols].fillna(0.0)

print("✔ ICD targets imputed successfully")


# --------------------------------------------------
# FEATURE SELECTION
# --------------------------------------------------

# Drop target columns from features
feature_cols = [c for c in df.columns if c not in TARGET_COLS]

# Drop non-feature columns by name pattern
feature_cols = [
    c for c in feature_cols
    if not any(key in c for key in DROP_COLS_CONTAINS)
]

# Keep only numeric features
feature_cols = [
    c for c in feature_cols
    if pd.api.types.is_numeric_dtype(df[c])
]

print(f"🧮 Final feature count: {len(feature_cols)}")

# --------------------------------------------------
# BUILD MATRICES
# --------------------------------------------------

X = df[feature_cols].values
Y = df[TARGET_COLS].values

print(f"✔ X shape: {X.shape}")
print(f"✔ Y shape: {Y.shape}")

if X.shape[0] == 0 or Y.shape[0] == 0:
    raise RuntimeError("❌ Empty training matrix — check preprocessing")

# --------------------------------------------------
# SCALE FEATURES
# --------------------------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --------------------------------------------------
# SAVE OUTPUTS
# --------------------------------------------------

np.save(OUT_DIR / "train_features.npy", X_scaled)
np.save(OUT_DIR / "train_labels.npy", Y)

joblib.dump(scaler, OUT_DIR / "scaler.pkl")

with open(OUT_DIR / "feature_list.json", "w") as f:
    json.dump(feature_cols, f, indent=2)

with open(OUT_DIR / "target_list.json", "w") as f:
    json.dump(TARGET_COLS, f, indent=2)

print("✅ Preprocessing complete!")
print(f"📁 Saved to: {OUT_DIR}")"""
