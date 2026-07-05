import numpy as np
from typing import Dict, List
from shared.schemas import MLFeatures, LocationInput, MLPredictionResponse, TopRiskItem

from .engines.pollution import compute_pollution_risk
from .engines.environment import compute_env_risk
from .engines.climate import compute_climate_risk
from .engines.fusion import fuse_risks

from .infxgb import predict_multilabel
from .engines.fusion import fuse_risks
from .engines.pollution import compute_pollution_risk
from .engines.climate import compute_climate_risk
from .engines.environment import compute_env_risk

# -----------------------------
# 25 diseases (fixed list)
# -----------------------------
DISEASES = [
    "Asthma", "COPD", "AllergicRhinitis", "Bronchitis", "Migraine",
    "Hypertension", "Diabetes", "Gastritis", "Pneumonia", "Sinusitis",
    "CardiacIssue", "Depression", "Anxiety", "Obesity", "Dengue",
    "Malaria", "SkinInfection", "UrinaryInfection", "Thyroid", "StrokeRisk",
    "KidneyIssue", "LiverIssue", "Anemia", "Arthritis", "Hypoxia"
]

# -----------------------------
# Fake baseline probabilities
# -----------------------------
def _baseline_fake_model(features: MLFeatures) -> Dict[str, float]:
    np.random.seed(3)
    probs = np.random.uniform(0.35, 0.75, size=len(DISEASES))
    return {DISEASES[i]: float(probs[i]) for i in range(len(DISEASES))}

# -----------------------------
# Build Top 5 risks
# -----------------------------
def compute_top_risks(
    disease_probs: Dict[str, float],
    pollution_risk: float,
    env_risk: float,
    climate_risk: float
) -> List[TopRiskItem]:

    top_items = []

    for name, base in disease_probs.items():
        # final adjusted score
        score = float(
            0.45 * base +
            0.20 * pollution_risk +
            0.20 * env_risk +
            0.15 * climate_risk
        )

        top_items.append(
            TopRiskItem(
                name=name,
                score=score,
                reason=f"Environmental conditions may worsen {name.lower()} risk.",
                environmental_factors={
                    "pollution_risk": pollution_risk,
                    "env_risk": env_risk,
                    "climate_risk": climate_risk,
                },
                recommendations=[
                    "Stay hydrated",
                    "Avoid heavy outdoor activity during peak pollution",
                ],
            )
        )

    # sort & return top 5
    top_items = sorted(top_items, key=lambda x: x.score, reverse=True)
    return top_items[:5]

# -----------------------------
# Main predict() function
# -----------------------------
def predict_risk(ml_features, location):
    top5, disease_probs = predict_multilabel(ml_features.dict())

    pollution_r = compute_pollution_risk(location)
    climate_r = compute_climate_risk(location)
    env_r = compute_env_risk(location)

    for item in top5:
        item["environmental_factors"] = {
            "pollution_risk": pollution_r,
            "climate_risk": climate_r,
            "env_risk": env_r
        }

    return {
        "risk_score": float(top5[0]["score"]),
        "condition": top5[0]["name"],
        "disease_probs": disease_probs,
        "env_risk": env_r,
        "pollution_risk": pollution_r,
        "climate_risk": climate_r,
        "final_risk": fuse_risks(
            top5[0]["score"],
            pollution_r,
            env_r,
            climate_r
        ),
        "top_risks": top5
    }


"""# model.py (multi-disease)

# backend/ml_service/model.py

from typing import Optional
from shared.schemas import MLFeatures, LocationInput, MLPredictionResponse

from .engines.pollution import compute_pollution_risk
from .engines.environment import compute_env_risk
from .engines.climate import compute_climate_risk
from .engines.risk_engine import compute_disease_probabilities, DISEASES

def predict_risk(ml_features: MLFeatures, location: Optional[LocationInput]):
    # environment engines
    pollution = compute_pollution_risk(location)
    env = compute_env_risk(location)
    climate = compute_climate_risk(location)

    # expert ML engine
    disease_probs = compute_disease_probabilities(
        ml_features.nlp_features,   # IMPORTANT (use NLP features inside ML)
        ml_features,
        pollution,
        env,
        climate
    )

    # final aggregated risk = simple mean of all diseases (balanced)
    final_risk = sum(disease_probs.values()) / len(disease_probs)

    # highest risk label
    condition = max(disease_probs, key=disease_probs.get)

    return MLPredictionResponse(
        risk_score=final_risk,
        condition=condition,
        env_risk=env,
        pollution_risk=pollution,
        climate_risk=climate,
        final_risk=final_risk,
        disease_probs=disease_probs
    )"""


