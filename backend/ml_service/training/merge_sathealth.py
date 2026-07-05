import pandas as pd
from pathlib import Path

# -----------------------------------------------------------
# CONFIG — main SatHealth folder
# -----------------------------------------------------------
BASE = Path(r"D:\geohealthai\backend\ml_service\training\raw")

DATA_DIR = BASE

# Environmental tables
AIR = DATA_DIR / "airquality.csv"
CLIMATE = DATA_DIR / "climate.csv"
GREENERY = DATA_DIR / "greenery.csv"
LANDCOVER = DATA_DIR / "landcover.csv"
SDI = DATA_DIR / "sdi.csv"

# Disease table (correct location)
DISEASE = BASE / "icdl1_prev_ohio.csv"

# Output
OUTPUT = BASE / "final_training_dataset.csv"


def load_csv(path):
    if not path.exists():
        print(f"❌ ERROR: File not found: {path}")
        return None
    print(f"📄 Loading: {path.name}")
    return pd.read_csv(path)


# -----------------------------------------------------------
# Load datasets
# -----------------------------------------------------------
air = load_csv(AIR)
climate = load_csv(CLIMATE)
green = load_csv(GREENERY)
land = load_csv(LANDCOVER)
sdi = load_csv(SDI)
disease = load_csv(DISEASE)

# -----------------------------------------------------------
# Fix missing ZCTA5 column in SDI table
# -----------------------------------------------------------
if "ZCTA5_FIPS" in sdi.columns:
    print("🔧 Renaming ZCTA5_FIPS → ZCTA5 in SDI table")
    sdi = sdi.rename(columns={"ZCTA5_FIPS": "ZCTA5"})

# -----------------------------------------------------------
# Verify all tables now have ZCTA5
# -----------------------------------------------------------
for name, table in {
    "airquality": air,
    "climate": climate,
    "greenery": green,
    "landcover": land,
    "sdi": sdi,
}.items():
    if "ZCTA5" not in table.columns:
        raise ValueError(
            f"❌ ERROR: {name} table does NOT contain ZCTA5 column.\n"
            f"Columns are: {table.columns}"
        )

# -----------------------------------------------------------
# Preprocess disease table
# -----------------------------------------------------------
print("🩺 Processing disease table (icd_l1)...")
disease = disease.copy()

pivot = disease.pivot_table(
    index="code",
    values="prevalence",
    aggfunc="mean"
).reset_index()

pivot["disease_name"] = (
    pivot["code"]
    .str.replace("-", "_")
    .str.replace(".", "_")
)

# -----------------------------------------------------------
# Start merging environmental data
# -----------------------------------------------------------
print("🔗 Merging environmental datasets...")

merged = air.copy()

# Average monthly data if month exists
if "month" in merged.columns:
    merged = merged.groupby("ZCTA5").mean().reset_index()

def merge_on_zcta(base, other, label):
    print(f"   ➤ merging {label} …")
    return base.merge(other.groupby("ZCTA5").mean().reset_index(), on="ZCTA5", how="left")

merged = merge_on_zcta(merged, climate, "climate")
merged = merge_on_zcta(merged, green, "greenery")
merged = merge_on_zcta(merged, land, "landcover")
merged = merge_on_zcta(merged, sdi, "sdi")

# -----------------------------------------------------------
# Add disease prevalence columns
# -----------------------------------------------------------
print("🏷 Adding disease prevalence features...")

for _, row in pivot.iterrows():
    col = f"prev_{row['disease_name']}"
    merged[col] = row["prevalence"]

# -----------------------------------------------------------
# Cleanup
# -----------------------------------------------------------
print("🧹 Final cleanup...")

merged = merged.dropna(subset=["ZCTA5"])
merged = merged.apply(pd.to_numeric, errors="ignore")
merged = merged.fillna(merged.mean(numeric_only=True))

merged.to_csv(OUTPUT, index=False)

print("✅ Merge complete!")
print(f"📁 Saved dataset → {OUTPUT}")
print(f"📊 Rows: {len(merged)}, Columns: {len(merged.columns)}")
