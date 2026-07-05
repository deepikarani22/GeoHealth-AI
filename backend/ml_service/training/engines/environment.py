# environment.py (MODIS NDVI loader + query)
import logging
from pathlib import Path
from typing import Optional, Tuple
import pandas as pd
import numpy as np
from shared.schemas import LocationInput
from database import db

logger = logging.getLogger(__name__)

# Path to the MODIS NDVI CSV you exported from GEE
CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "env" / "modis_ndvi.csv"

_df = None
_min_ndvi = None
_max_ndvi = None

def _load_modis_csv():
    global _df, _min_ndvi, _max_ndvi
    if _df is not None:
        return
    if not CSV_PATH.exists():
        logger.error("MODIS NDVI CSV not found at %s", CSV_PATH)
        # create empty df fallback
        _df = pd.DataFrame(columns=["city", "lat", "lon", "NDVI_mean"])
        _min_ndvi, _max_ndvi = 0.0, 1.0
        return

    # read CSV - accomodate different column names
    raw = pd.read_csv(CSV_PATH)
    # normalize column names
    raw_cols = [c.strip() for c in raw.columns]
    raw.columns = raw_cols

    # attempt to find columns
    # allowed variations: NDVI_mean or ndvi_mean etc.
    ndvi_col = None
    for candidate in ["NDVI_mean", "ndvi_mean", "ndvi", "NDVI"]:
        if candidate in raw.columns:
            ndvi_col = candidate
            break
    lat_col = None
    lon_col = None
    for candidate in ["lat", "latitude", "LAT", "LATITUDE"]:
        if candidate in raw.columns:
            lat_col = candidate
            break
    for candidate in ["lon", "longitude", "LON", "LONGITUDE"]:
        if candidate in raw.columns:
            lon_col = candidate
            break
    city_col = None
    for candidate in ["city", "City", "CITY"]:
        if candidate in raw.columns:
            city_col = candidate
            break

    if ndvi_col is None or lat_col is None or lon_col is None:
        logger.error("MODIS CSV missing required columns. Found columns: %s", list(raw.columns))
        _df = pd.DataFrame(columns=["city", "lat", "lon", "NDVI_mean"])
        _min_ndvi, _max_ndvi = 0.0, 1.0
        return

    df = raw.rename(columns={ndvi_col: "NDVI_mean", lat_col: "lat", lon_col: "lon"})
    if city_col:
        df = df.rename(columns={city_col: "city"})
    # ensure proper types
    df["NDVI_mean"] = pd.to_numeric(df["NDVI_mean"], errors="coerce")
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["NDVI_mean", "lat", "lon"])
    # clean city strings
    if "city" in df.columns:
        df["city"] = df["city"].astype(str).str.strip().str.lower()
    else:
        df["city"] = ""

    # compute min/max NDVI for normalization
    _min_ndvi = float(df["NDVI_mean"].min())
    _max_ndvi = float(df["NDVI_mean"].max())
    if _min_ndvi == _max_ndvi:
        # avoid division by zero
        _min_ndvi, _max_ndvi = 0.0, 1.0

    _df = df.reset_index(drop=True)
    logger.info("Loaded MODIS NDVI CSV (%d rows). NDVI range: %s - %s", len(_df), _min_ndvi, _max_ndvi)

def _normalize_ndvi(v: float) -> float:
    # maps NDVI -> [0,1]
    if _min_ndvi is None or _max_ndvi is None or _max_ndvi == _min_ndvi:
        return float(np.clip(v, 0.0, 1.0))
    return float((v - _min_ndvi) / (_max_ndvi - _min_ndvi))

def compute_env_risk(location: Optional[LocationInput]) -> float:
    """
    Use the MODIS NDVI CSV to compute env_risk in [0,1].
    - Prefer exact city match (case-insensitive)
    - Fallback to nearest lat/lon using Euclidean distance
    - Final env_risk = 1 - normalized_ndvi (higher NDVI => lower risk)
    - Store result in SQLite cache for quick reuse
    """
    _load_modis_csv()
    if location is None:
        logger.warning("compute_env_risk called with no location; returning default 0.6")
        return 0.6

    city = (location.city or "").strip().lower()
    state = (location.state or "").strip().lower()
    lat = location.latitude
    lon = location.longitude

    if city:
        cached = db.get_cached_env(city, state)
        if cached is not None:
            logger.info("Using env cache for %s,%s -> %s", city, state, cached)
            return cached

    # try city match first
    if city and _df is not None and not _df.empty:
        # exact match
        matches = _df[_df["city"] == city]
        if not matches.empty:
            ndvi = float(matches["NDVI_mean"].mean())
            norm = _normalize_ndvi(ndvi)
            env_risk = float(1.0 - norm)
            db.set_cached_env(city, state, env_risk)
            logger.info("Env risk (city match) %s,%s -> ndvi=%s env_risk=%s", city, state, ndvi, env_risk)
            return env_risk

    # fallback: nearest lat/lon
    if lat is None or lon is None or _df is None or _df.empty:
        # default
        logger.warning("No lat/lon or empty NDVI table; default env risk 0.6")
        return 0.6

    # compute nearest
    coords = _df[["lat", "lon"]].to_numpy()
    target = np.array([float(lat), float(lon)])
    dists = np.sum((coords - target) ** 2, axis=1)  # squared euclid
    idx = int(np.argmin(dists))
    ndvi = float(_df.iloc[idx]["NDVI_mean"])
    norm = _normalize_ndvi(ndvi)
    env_risk = float(1.0 - norm)
    # store in cache optionally under city if present else use lat/lon keyed cache is climate/pollution only
    if city:
        db.set_cached_env(city, state, env_risk)
    logger.info("Env risk (nearest) for (%s,%s) -> ndvi=%s env_risk=%s", lat, lon, ndvi, env_risk)
    return env_risk
