import pandas as pd
from pathlib import Path

BASE = Path("raw")
OUT  = Path("raw")
OUT.mkdir(exist_ok=True)

def load(name):
    p = BASE / name
    print(f"📄 Loading {p}")
    return pd.read_csv(p)

# ----------------------------------------
# Load datasets
# ----------------------------------------
air = load("airquality.csv")
climate = load("climate.csv")
greenery = load("greenery.csv")
landcover = load("landcover.csv")
icd = load("icdl1_prev_ohio.csv")

# ----------------------------------------
# Helper: yearly aggregation
# ----------------------------------------
def yearly_mean(df, group_cols):
    num_cols = df.select_dtypes(include="number").columns.tolist()
    num_cols = [c for c in num_cols if c not in group_cols]
    return (
        df
        .groupby(group_cols, as_index=False)[num_cols]
        .mean()
    )

# ----------------------------------------
# Aggregate monthly → yearly
# ----------------------------------------
print("📊 Aggregating monthly environmental data to yearly...")

air_y = yearly_mean(air, ["CBSAFP", "year"])
climate_y = yearly_mean(climate, ["CBSAFP", "year"])
greenery_y = yearly_mean(greenery, ["CBSAFP", "year"])

# ----------------------------------------
# Merge environmental datasets
# ----------------------------------------
print("🔗 Merging environmental datasets...")

env = air_y.merge(climate_y, on=["CBSAFP", "year"], how="left")
env = env.merge(greenery_y, on=["CBSAFP", "year"], how="left")
env = env.merge(landcover, on="CBSAFP", how="left")

# ----------------------------------------
# Process ICD L1 disease prevalence
# ----------------------------------------
print("🩺 Processing ICD L1 disease prevalence...")

icd_pivot = (
    icd
    .pivot_table(
        index=["CBSAFP", "year"],
        columns="code",
        values="prevalence",
        aggfunc="mean"
    )
    .reset_index()
)

# Rename targets
icd_pivot.columns = [
    f"prev_{c}" if c not in ["CBSAFP", "year"] else c
    for c in icd_pivot.columns
]

# ----------------------------------------
# Final merge
# ----------------------------------------
print("🔗 Merging environment + disease prevalence...")

final = env.merge(icd_pivot, on=["CBSAFP", "year"], how="inner")

# ----------------------------------------
# Save
# ----------------------------------------
out_path = OUT / "training_dataset.csv"
final.to_csv(out_path, index=False)

print("✅ CBSA-level dataset build complete!")
print(f"📊 Rows: {final.shape[0]}, Columns: {final.shape[1]}")
print(f"💾 Saved to: {out_path}")
