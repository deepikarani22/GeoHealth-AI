import numpy as np
import json
from pathlib import Path

FEATURE_LIST_PATH = Path(__file__).resolve().parents[1] / "training" / "processed" / "feature_list.json"

with open(FEATURE_LIST_PATH) as f:
    FEATURE_ORDER = json.load(f)

def build_feature_vector(env_features: dict) -> np.ndarray:
    """
    Map live environmental engine outputs to SatHealth-trained feature space
    """

    vector = []

    for feat in FEATURE_ORDER:
        if feat in env_features:
            vector.append(env_features[feat])
        else:
            # SAFE DEFAULT (mean-imputed during training)
            vector.append(0.0)

    return np.array(vector).reshape(1, -1)
