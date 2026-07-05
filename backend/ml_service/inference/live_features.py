from typing import Dict
from shared.schemas import LocationInput

from ..training.engines.pollution import compute_pollution_risk
from ..training.engines.climate import compute_climate_risk
from ..training.engines.environment import compute_env_risk


def collect_live_features(location: LocationInput) -> Dict[str, float]:
    """
    Collects all live environmental features required by the ML model
    and returns them as a flat dictionary.
    """

    features = {}

    # Pollution
    features["pollution_risk"] = compute_pollution_risk(location)

    # Climate
    features["climate_risk"] = compute_climate_risk(location)

    # NDVI-based environment
    features["env_risk"] = compute_env_risk(location)

    return features
