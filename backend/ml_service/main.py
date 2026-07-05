from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import pandas as pd
from pathlib import Path
from typing import Dict, Optional

from shared.schemas import LocationInput, MLPredictionResponse
from .inference.inference_xgb import predict_env_risks
from .inference.live_features import collect_live_features

from .training.engines.pollution import compute_pollution_risk
from .training.engines.climate import compute_climate_risk
from .training.engines.environment import compute_env_risk
from .inference.clinical_adjuster import apply_clinical_adjustments


app = FastAPI(title="GeoHealthAI ML Service")

CSV_PATH = Path(r"D:\geohealthai\backend\data\env\MODIS_NDVI.csv")
_df_modis = None

def load_modis():
    global _df_modis
    if _df_modis is not None:
        return

    if not CSV_PATH.exists():
        raise RuntimeError(f"MODIS NDVI CSV not found at {CSV_PATH}")

    raw = pd.read_csv(CSV_PATH)
    raw.columns = [c.lower().strip() for c in raw.columns]

    # Normalize column names safely
    col_map = {}
    if "latitude" in raw.columns:
        col_map["latitude"] = "lat"
    if "longitude" in raw.columns:
        col_map["longitude"] = "lon"

    raw = raw.rename(columns=col_map)

    required = {"city", "lat", "lon"}
    if not required.issubset(set(raw.columns)):
        raise RuntimeError(f"MODIS CSV missing required columns: {required}")

    raw["city"] = raw["city"].astype(str).str.lower().str.strip()
    raw["lat"] = pd.to_numeric(raw["lat"], errors="coerce")
    raw["lon"] = pd.to_numeric(raw["lon"], errors="coerce")

    _df_modis = raw.dropna(subset=["city", "lat", "lon"])


def resolve_city_to_coords(city: str) -> LocationInput:
    load_modis()
    row = _df_modis[_df_modis["city"] == city.lower()].head(1)
    if row.empty:
        return None

    r = row.iloc[0]
    return LocationInput(
        city=city,
        latitude=float(r.lat),
        longitude=float(r.lon),
    )


# ------------------------------------------------------------------
# Request model
# ------------------------------------------------------------------
class MLInput(BaseModel):
    city: str
    nlp_features: Optional[Dict] = None
    ml_features: Optional[Dict] = None


# ------------------------------------------------------------------
# Prediction endpoint
# ------------------------------------------------------------------
@app.post("/ml/predict", response_model=MLPredictionResponse)
def predict(payload: MLInput):

    # 1️⃣ Resolve city → lat/lon internally
    location = resolve_city_to_coords(payload.city)

    if location is None:
        raise HTTPException(
            status_code=400,
            detail=f"City '{payload.city}' not found in MODIS dataset"
        )

    # 2️⃣ Collect live environmental features (49 features)
    env_features = collect_live_features(location)

    # 3️⃣ XGBoost inference (49-feature safe)
    #icd_risks = predict_env_risks(env_features)
    icd_risks = predict_env_risks(env_features)

    icd_risks = apply_clinical_adjustments(
        icd_risks,
        payload.nlp_features,
        payload.ml_features,
    )
    #base_risk = sum(icd_risks.values()) / len(icd_risks)
    base_risk = sum(icd_risks.values()) / len(icd_risks)


    pollution = compute_pollution_risk(location)
    climate = compute_climate_risk(location)
    env = compute_env_risk(location)

    final_risk = (
        0.4 * base_risk +
        0.2 * pollution +
        0.2 * climate +
        0.2 * env
    )

    return MLPredictionResponse(
    risk_score=round(base_risk, 4),
    disease_probs={k.replace("prev_", ""): round(v, 4) for k, v in icd_risks.items()},
    pollution_risk=round(pollution, 4),
    climate_risk=round(climate, 4),
    env_risk=round(env, 4),
    final_risk=round(final_risk, 4),
    )





"""# geohealthai/backend/ml_service/main.py

# geohealthai/backend/ml_service/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import pandas as pd
from pathlib import Path

from shared.schemas import (
    MLFeatures,
    LocationInput,
    MLPredictionResponse,
)

# ✅ Correct import (function MUST exist)
from ml_service.inference.inference_xgb import predict_env_risks

from .engines import pollution as pollution_engine
from .engines import climate as climate_engine
from .engines import environment as env_engine
from .engines import fusion as fusion_engine

app = FastAPI(title="GeoHealthAI ML Service")

# -------------------------------------------------------------
# Load MODIS NDVI CSV for city → lat/lon lookup
# -------------------------------------------------------------
CSV_PATH = Path(r"D:\geohealthai\backend\data\env\MODIS_NDVI.csv")

df_modis = None


def load_modis():
    global df_modis
    if df_modis is not None:
        return

    if not CSV_PATH.exists():
        raise RuntimeError(f"MODIS NDVI CSV not found at: {CSV_PATH}")

    raw = pd.read_csv(CSV_PATH)
    raw.columns = [c.lower().strip() for c in raw.columns]

    clean = raw.rename(
        columns={
            next(c for c in raw.columns if "ndvi" in c): "ndvi",
            "latitude": "lat",
            "longitude": "lon",
        }
    )

    clean["city"] = clean["city"].astype(str).str.lower().str.strip()
    clean["lat"] = pd.to_numeric(clean["lat"], errors="coerce")
    clean["lon"] = pd.to_numeric(clean["lon"], errors="coerce")
    clean = clean.dropna(subset=["city", "lat", "lon"])

    df_modis = clean


def resolve_city_to_coords(city: str) -> Optional[LocationInput]:
    load_modis()
    row = df_modis[df_modis["city"] == city.lower()].head(1)
    if row.empty:
        return None

    r = row.iloc[0]
    return LocationInput(city=city, latitude=float(r.lat), longitude=float(r.lon))


# -------------------------------------------------------------
# Request model
# -------------------------------------------------------------
#class MLInput(BaseModel):
 #   ml_features: Dict
  #  city: str   # 👈 USER ENTERS ONLY CITY
class MLInput(BaseModel):
    ml_features: Dict
    nlp_features: Dict
    location: LocationInput


# -------------------------------------------------------------
# Prediction endpoint
# -------------------------------------------------------------
@app.post("/ml/predict", response_model=MLPredictionResponse)
def predict(payload: MLInput):

    #resolved_loc = resolve_city_to_coords(payload.city)
    # City comes from payload.location.city
    if not payload.location or not payload.location.city:
        raise HTTPException(400, "City is required")

    resolved_loc = resolve_city_to_coords(payload.location.city)

    #if resolved_loc is None:
       # raise HTTPException(
           # 400, f"City '{payload.city}' not found in MODIS dataset"
        #)

    # -------------------------------------------------
    # 1) XGBoost Environmental Disease Risks
    # -------------------------------------------------
    # -------------------------------------------------
# 1) Build environmental feature vector
# -------------------------------------------------
    def build_env_features(location: LocationInput) -> dict:
        "
        Build the environmental feature dictionary expected by XGBoost
        using live engines.
        "

        return {
            # Pollution proxy
            "pollution_risk": pollution_engine.compute_pollution_risk(location),

            # Climate proxy
            "climate_risk": climate_engine.compute_climate_risk(location),

            # NDVI-based environment proxy
            "env_risk": env_engine.compute_env_risk(location),
        }

    # -------------------------------------------------
    # 2) XGBoost Environmental Disease Risks
    # -------------------------------------------------
    env_features = build_env_features(resolved_loc)
    icd_risks = predict_env_risks(env_features)


    base_medical_risk = float(
        sum(icd_risks.values()) / len(icd_risks)
    )

    # -------------------------------------------------
    # 2) External Environmental Engines
    # -------------------------------------------------
    pollution_risk = pollution_engine.compute_pollution_risk(resolved_loc)
    climate_risk = climate_engine.compute_climate_risk(resolved_loc)
    env_risk = env_engine.compute_env_risk(resolved_loc)

    # -------------------------------------------------
    # 3) Fusion
    # -------------------------------------------------
    final_risk = fusion_engine.fuse_risks(
        base_medical_risk,
        pollution_risk,
        env_risk,
        climate_risk,
    )

    # -------------------------------------------------
    # 4) Response
    # -------------------------------------------------
    return MLPredictionResponse(
        risk_score=round(base_medical_risk, 4),
        icd_risks={k.replace("prev_", ""): round(v, 4) for k, v in icd_risks.items()},
        pollution_risk=round(pollution_risk, 4),
        climate_risk=round(climate_risk, 4),
        env_risk=round(env_risk, 4),
        final_risk=round(final_risk, 4),
    )"""



"""from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import pandas as pd
from pathlib import Path

from shared.schemas import (
    MLFeatures,
    LocationInput,
    MLPredictionResponse,
)

from ml_service.inference.inference_xgb import predict_env_risks
from ml_service.model_mapping import TARGET_ORDER
from .engines import pollution as pollution_engine
from .engines import climate as climate_engine
from .engines import environment as env_engine
from .engines import fusion as fusion_engine


app = FastAPI(title="GeoHealthAI ML Service (City → Lat/Lon + Full Engines)")


# -------------------------------------------------------------
# Load MODIS NDVI CSV for city → lat/lon lookup
# -------------------------------------------------------------
#CSV_PATH = Path(__file__).resolve().parents[2] /"backend"/ "data" / "MODIS_NDVI.csv"
CSV_PATH = Path(r"D:\geohealthai\backend\data\MODIS_NDVI.csv")

df_modis = None

def load_modis():
    global df_modis
    if df_modis is not None:
        return
    if not CSV_PATH.exists():
        raise RuntimeError(f"MODIS NDVI CSV not found at: {CSV_PATH}")

    raw = pd.read_csv(CSV_PATH)

    # Normalize columns
    clean = raw.copy()
    clean.columns = [c.lower().strip() for c in clean.columns]

    # Detect proper name columns
    ndvi_col = next((c for c in clean.columns if "ndvi" in c), None)
    lat_col = next((c for c in clean.columns if c in ["lat", "latitude"]), None)
    lon_col = next((c for c in clean.columns if c in ["lon", "longitude"]), None)
    city_col = next((c for c in clean.columns if c == "city"), None)

    if not (ndvi_col and lat_col and lon_col and city_col):
        raise RuntimeError("MODIS CSV missing city/lat/lon/NDVI columns.")

    clean = clean.rename(
        columns={
            ndvi_col: "ndvi",
            lat_col: "lat",
            lon_col: "lon",
            city_col: "city",
        }
    )

    clean["city"] = clean["city"].astype(str).str.strip().str.lower()
    clean["lat"] = pd.to_numeric(clean["lat"], errors="coerce")
    clean["lon"] = pd.to_numeric(clean["lon"], errors="coerce")
    clean = clean.dropna(subset=["city", "lat", "lon"])

    df_modis = clean


def resolve_city_to_coords(city: str) -> Optional[LocationInput]:
    "
    Takes a city name string → returns a LocationInput(lat, lon)
    "
    load_modis()

    city_clean = city.strip().lower()
    matches = df_modis[df_modis["city"] == city_clean]

    if matches.empty:
        return None

    row = matches.iloc[0]
    return LocationInput(
        city=city,
        latitude=float(row["lat"]),
        longitude=float(row["lon"]),
    )


# -------------------------------------------------------------
# ML Input Model (location is mandatory now)
# -------------------------------------------------------------
class MLInput(BaseModel):
    ml_features: dict
    location: LocationInput  # Mandatory now


# -------------------------------------------------------------
# Prediction endpoint
# -------------------------------------------------------------
@app.post("/ml/predict", response_model=MLPredictionResponse)
def predict(payload: MLInput):

    # Convert dict → MLFeatures Pydantic model
    ml_feats = MLFeatures(**payload.ml_features)

    # -------------------------------------------------
    # LOCATION MUST BE PROVIDED BY USER
    # -------------------------------------------------
    if payload.location.city is None:
        raise HTTPException(400, "City is required.")

    # -------------------------------------------------
    # CITY → LATITUDE/LONGITUDE AUTO-RESOLUTION
    # -------------------------------------------------
    resolved_loc = resolve_city_to_coords(payload.location.city)

    if resolved_loc is None:
        raise HTTPException(
            400, 
            f"City '{payload.location.city}' not found in MODIS NDVI dataset. "
            "Please enter another city."
        )

    # -------------------------------------------------
    # 1) Medical ML model output
    # -------------------------------------------------
    env_predictions = predict_env_risks(
    location=resolved_loc
    )
    medical_risk = float(sum(env_predictions.values()) / len(env_predictions))

    # -------------------------------------------------
    # 2) Environmental ML Engines
    # -------------------------------------------------
    pollution_risk = float(pollution_engine.compute_pollution_risk(resolved_loc))
    climate_risk = float(climate_engine.compute_climate_risk(resolved_loc))
    env_risk = float(env_engine.compute_env_risk(resolved_loc))

    # -------------------------------------------------
    # 3) Fuse All Risks
    # -------------------------------------------------
    final_risk = float(
        fusion_engine.fuse_risks(
            medical_risk,
            pollution_risk,
            env_risk,
            climate_risk,
        )
    )

    medical_pred = MLPredictionResponse(
        risk_score=round(medical_risk, 4),
        icd_risks={
            k.replace("prev_", ""): round(v, 4)
            for k, v in env_predictions.items()
        },
        env_risk=round(env_risk, 4),
        pollution_risk=round(pollution_risk, 4),
        climate_risk=round(climate_risk, 4),
        final_risk=round(final_risk, 4),
    )

    return medical_pred


medical_pred.icd_risks = {
    k.replace("prev_", ""): round(v, 4)
    for k, v in env_predictions.items()
}

    # Attach to output
    medical_pred.env_risk = env_risk
    medical_pred.pollution_risk = pollution_risk
    medical_pred.climate_risk = climate_risk
    medical_pred.final_risk = round(final_risk, 3)

    return medical_pred"""


