import pandas as pd
from pathlib import Path

BASE = Path("raw")
INPUT = BASE / "final_training_dataset.csv"
OUTPUT = BASE / "cbsa_training_dataset.csv"

TARGETS = [
    "prev_A00_B99",
    "prev_C00_D49",
    "prev_D50_D89",
    "prev_E00_E89",
    "prev_F01_F99",
    "prev_G00_G99",
    "prev_H00_H59",
    "prev_H60_H95",
    "prev_I00_I99",
    "prev_J00_J99",
    "prev_K00_K95",
]

print("📄 Loading ZCTA-level dataset...")
df = pd.read_csv(INPUT)

# -------------------------------------------------
# ✅ STEP 1 — Normalize YEAR (THIS FIXES YOUR ERROR)
# -------------------------------------------------
print("🔧 Normalizing year column...")

if "year" not in df.columns:
    # Prefer year_x if present
    if "year_x" in df.columns:
        df["year"] = df["year_x"]
    elif "year_y" in df.columns:
        df["year"] = df["year_y"]
    else:
        raise RuntimeError("❌ No usable year column found")

# Drop all duplicate year columns
df = df.drop(columns=[c for c in df.columns if c.startswith("year_")])

df["year"] = df["year"].astype(int)

# -------------------------------------------------
# ✅ STEP 2 — Feature selection
# -------------------------------------------------
FEATURES = [
    c for c in df.columns
    if c not in TARGETS
    and c not in ["ZCTA5", "CBSAFP"]
    and df[c].dtype != "object"
]

print(f"🧮 Using {len(FEATURES)} environmental features")

# -------------------------------------------------
# ✅ STEP 3 — Aggregate ZCTA → CBSA
# -------------------------------------------------
print("🔗 Aggregating ZCTA → CBSA (mean)...")

cbsa_env = (
    df
    .groupby(["CBSAFP", "year"], as_index=False)[FEATURES]
    .mean()
)

cbsa_targets = (
    df
    .groupby(["CBSAFP", "year"], as_index=False)[TARGETS]
    .mean()
)

# -------------------------------------------------
# ✅ STEP 4 — Merge env + disease
# -------------------------------------------------
cbsa = cbsa_env.merge(cbsa_targets, on=["CBSAFP", "year"], how="inner")

# -------------------------------------------------
# ✅ STEP 5 — Save
# -------------------------------------------------
cbsa.to_csv(OUTPUT, index=False)

print("✅ CBSA-level dataset built successfully")
print(f"📊 Rows: {cbsa.shape[0]}, Columns: {cbsa.shape[1]}")
print(f"💾 Saved to: {OUTPUT}")
