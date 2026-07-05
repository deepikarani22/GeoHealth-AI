import numpy as np

# ============================================================
# Target order (MUST match training order exactly)
# ============================================================

TARGET_ORDER = [
    "prev_A00-B99",  # Infectious
    "prev_C00-D49",  # Cancer
    "prev_D50-D89",  # Blood
    "prev_E00-E89",  # Metabolic
    "prev_F01-F99",  # Mental
    "prev_G00-G99",  # Neuro
    "prev_H00-H59",  # Eye
    "prev_H60-H95",  # Ear
    "prev_I00-I99",  # Cardiac
    "prev_J00-J99",  # Respiratory
    "prev_K00-K95",  # Digestive
]

# ============================================================
# Feature order (49 features — MUST match training)
# ============================================================

FEATURE_ORDER = [
    # --- Air Quality (OpenAQ mapped) ---
    "total_aerosol_optical_depth_at_550nm_surface",
    "particulate_matter_d_less_than_25_um_surface",
    "NO2_column_number_density",
    "ozone",

    # --- Climate (OpenMeteo mapped) ---
    "temperature_2m",
    "dewpoint_temperature_2m",
    "surface_pressure",
    "total_precipitation_sum",
    "u_component_of_wind_10m",
    "v_component_of_wind_10m",

    # --- Hydrology / Heat ---
    "surface_latent_heat_flux_sum",
    "surface_net_solar_radiation_sum",
    "surface_thermal_radiation_downwards_sum",
    "total_evaporation_sum",

    # --- Vegetation ---
    "NDVI",
    "leaf_area_index_high_vegetation",
    "leaf_area_index_low_vegetation",

    # --- Landcover ---
    "urban-coverfraction",
    "tree-coverfraction",
    "grass-coverfraction",
    "crops-coverfraction",

    # --- Snow / Water ---
    "snow_cover",
    "snow_depth",
    "water-permanent-coverfraction",

    # --- Soil ---
    "volumetric_soil_water_layer_1",
    "volumetric_soil_water_layer_3",

    # --- Remaining stable env features ---
    "soil_temperature_level_1",
    "soil_temperature_level_3",
    "lake_bottom_temperature",
    "lake_mix_layer_temperature",
    "lake_total_layer_temperature",

    # --- Wind & runoff ---
    "surface_runoff_sum",

    # --- Month encoding ---
    "month_sin",
    "month_cos",
]

# ============================================================
# Feature vector builder
# ============================================================

def build_feature_vector(env: dict) -> np.ndarray:
    """
    env: dictionary produced by environmental engines
    returns: np.array shape (1, 49)
    """

    vec = []

    for f in FEATURE_ORDER:
        val = env.get(f, 0.0)

        # Safety: convert None / nan
        if val is None or (isinstance(val, float) and np.isnan(val)):
            val = 0.0

        vec.append(float(val))

    return np.array(vec).reshape(1, -1)


"""# backend/ml_service/model_mapping.py

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------
# Load feature & target order from training artifacts
# ---------------------------------------------------

FEATURE_LIST = json.load(
    open(BASE_DIR / "training" / "processed" / "feature_list.json")
)

TARGET_LIST = json.load(
    open(BASE_DIR / "training" / "processed" / "target_list.json")
)

# ---------------------------------------------------
# Public mappings used by inference & API
# ---------------------------------------------------

TARGET_TO_RISK_NAME = {
    "prev_A00-B99": "InfectiousRisk",
    "prev_C00-D49": "CancerRisk",
    "prev_D50-D89": "BloodRisk",
    "prev_E00-E89": "MetabolicRisk",
    "prev_F01-F99": "MentalRisk",
    "prev_G00-G99": "NeuroRisk",
    "prev_H00-H59": "EyeRisk",
    "prev_H60-H95": "EarRisk",
    "prev_I00-I99": "CardiacRisk",
    "prev_J00-J99": "RespiratoryRisk",
    "prev_K00-K95": "DigestiveRisk",
}

# ---------------------------------------------------
# Feature vector builder (STRICT ordering)
# ---------------------------------------------------

def build_feature_vector(env_features: dict) -> list:
    "
    Converts dictionary of live environmental features
    into ordered feature vector expected by XGBoost model.
    "

    vector = []

    for feature in FEATURE_LIST:
        value = env_features.get(feature)

        # Safe fallback (never NaN at inference)
        if value is None:
            value = 0.0

        vector.append(float(value))

    return vector"""
