import logging
from datetime import datetime, timezone
from typing import Optional

import requests

from shared.schemas import LocationInput
from database import db

logger = logging.getLogger(__name__)

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _compute_climate_risk(temp_c: float, humidity: float) -> float:
    """
    Very simple heat-stress-based climate risk [0,1].
    You can refine this later.
    """
    # Hot and humid
    if temp_c >= 35 and humidity >= 60:
        return 0.85
    if temp_c >= 30 and humidity >= 50:
        return 0.7
    if temp_c <= 10:
        # cold stress
        return 0.6
    return 0.4  # mild climate risk


def compute_climate_risk(location: Optional[LocationInput]) -> float:
    """
    Uses Open-Meteo + SQLite cache to compute climate risk in [0,1]
    based on temperature and humidity.

    - If location is missing, returns neutral 0.5
    - If Open-Meteo fails, returns 0.5
    """
    if location is None:
        logger.warning("compute_climate_risk called with no location; returning 0.5")
        return 0.5

    if location.latitude is None or location.longitude is None:
        logger.warning("Location missing lat/lon; returning default climate risk 0.5")
        return 0.5

    lat = float(location.latitude)
    lon = float(location.longitude)

    hour_key = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00Z")

    # 1) Try cache
    cached = db.get_cached_climate(lat, lon, hour_key)
    if cached is not None:
        logger.info("Using cached climate risk for (%s, %s) -> %s", lat, lon, cached)
        return cached

    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relativehumidity_2m",
        "timezone": "auto",
    }

    try:
        resp = requests.get(OPEN_METEO_URL, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        hourly = data.get("hourly") or {}
        temps = hourly.get("temperature_2m") or []
        hums = hourly.get("relativehumidity_2m") or []
        if not temps or not hums:
            logger.warning("Open-Meteo returned no hourly data; using default climate risk")
            risk = 0.5
        else:
            temp_c = float(temps[0])
            humidity = float(hums[0])
            risk = _compute_climate_risk(temp_c, humidity)
    except Exception as e:
        logger.warning("Open-Meteo request failed: %s; using default climate risk", e)
        risk = 0.5

    db.set_cached_climate(lat, lon, hour_key, risk)
    return risk
