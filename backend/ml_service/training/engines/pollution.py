import logging
import os
from datetime import datetime, timezone
from typing import Optional

import requests

from shared.schemas import LocationInput
from database import db

logger = logging.getLogger(__name__)

OPENAQ_BASE_URL = "https://api.openaq.org/v3/latest"


def _compute_pollution_risk_from_pm25(pm25: float) -> float:
    """
    Simple WHO-inspired mapping from PM2.5 µg/m³ to risk in [0,1].
    You can tune this later.
    """
    if pm25 <= 10:
        return 0.1
    if pm25 <= 25:
        return 0.3
    if pm25 <= 50:
        return 0.6
    if pm25 <= 75:
        return 0.8
    return 0.95


def compute_pollution_risk(location: Optional[LocationInput]) -> float:
    """
    Uses OpenAQ + SQLite cache to compute a pollution risk score in [0,1].

    - If location is missing, returns a neutral default (0.5).
    - If OpenAQ fails or no data, uses a moderate fallback (0.6).
    """
    if location is None:
        logger.warning("compute_pollution_risk called with no location; returning 0.5")
        return 0.5

    city = (location.city or "").strip()
    state = (location.state or "").strip()
    if not city:
        logger.warning("No city in location; returning default pollution risk 0.6")
        return 0.6

    # cache key: current hour UTC
    hour_key = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00Z")

    # 1) Try cache
    cached = db.get_cached_pollution(city, state, hour_key)
    if cached is not None:
        logger.info("Using cached pollution risk for %s, %s -> %s", city, state, cached)
        return cached

    # 2) Call OpenAQ API
    params = {
        "location": city,
        "parameter": "pm25"
    }
    headers = {}
    api_key = os.getenv("OPENAQ_API_KEY")
    if api_key:
        headers["X-API-Key"] = api_key

    try:
        resp = requests.get(OPENAQ_BASE_URL, params=params, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results") or []
        if not results:
            logger.warning("No OpenAQ results for city=%s; using fallback", city)
            risk = 0.6
        else:
            measurements = results[0].get("measurements") or []
            if not measurements:
                logger.warning("No measurements in OpenAQ results; using fallback")
                risk = 0.6
            else:
                pm25 = float(measurements[0].get("value", 30.0))
                risk = _compute_pollution_risk_from_pm25(pm25)
    except Exception as e:
        logger.warning("OpenAQ request failed: %s; using fallback pollution risk", e)
        risk = 0.6

    # 3) Store in cache
    db.set_cached_pollution(city, state, hour_key, risk)
    return risk
