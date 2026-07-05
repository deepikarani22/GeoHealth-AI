# ml_service/feature_store.py

import numpy as np
from typing import Dict
from shared.schemas import LocationInput

from ..training.engines.pollution import compute_pollution_risk
from ..training.engines.climate import compute_climate_risk
from ..training.engines.environment import compute_env_risk

from ml_service.model_mapping import FEATURE_ORDER


import json
import numpy as np
from pathlib import Path
from typing import Dict

FEATURE_LIST_PATH = Path(r"D:\geohealthai\backend\ml_service\training\artifacts\feature_list.json")


class FeatureStore:
    """
    Guarantees:
    - Correct feature names
    - Correct order
    - Correct length
    - Safe defaults
    """

    def __init__(self):
        if not FEATURE_LIST_PATH.exists():
            raise RuntimeError(f"feature_list.json not found at {FEATURE_LIST_PATH}")

        with open(FEATURE_LIST_PATH, "r") as f:
            self.feature_names = json.load(f)

        self.n_features = len(self.feature_names)

    def build_vector(self, live_features: Dict[str, float]) -> np.ndarray:
        """
        Input:
            live_features: dict from engines (pollution, climate, NDVI, etc.)

        Output:
            np.ndarray shape (1, n_features)
        """
        vector = np.zeros(self.n_features, dtype=float)

        for i, fname in enumerate(self.feature_names):
            value = live_features.get(fname, 0.0)
            vector[i] = float(value)

        return vector.reshape(1, -1)



"""import json
import numpy as np
from pathlib import Path
from shared.schemas import LocationInput
from ml_service.engines import pollution, climate, environment

BASE_DIR = Path(__file__).resolve().parents[2]
FEATURES_PATH = Path(r"D:\geohealthai\backend\ml_service\training\processed\feature_list.json")

with open(FEATURES_PATH) as f:
    FEATURE_ORDER = json.load(f)


def build_feature_vector(location: LocationInput) -> np.ndarray:
    "
    Always returns a FULL, ORDERED feature vector
    exactly matching training-time schema.
    "

    feature_map = {f: 0.0 for f in FEATURE_ORDER}

    # --- Environmental engines ---
    feature_map["pollution_risk"] = pollution.compute_pollution_risk(location)
    feature_map["climate_risk"] = climate.compute_climate_risk(location)
    feature_map["env_risk"] = environment.compute_env_risk(location)

    # --- OPTIONAL: add more mappings later ---
    # feature_map["temperature_2m"] = ...
    # feature_map["pm25"] = ...

    vector = [feature_map[f] for f in FEATURE_ORDER]
    return np.array(vector).reshape(1, -1)"""
