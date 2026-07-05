from typing import Dict, List

from .disease_rules import DISEASE_ENV_RULES
from .severity_scoring import (
    compute_base_severity,
    apply_human_modifiers
)
from .recommendation_engine import get_recommendations


def evaluate_environmental_rules(
    disease: str,
    environmental_data: Dict
) -> int:
    """
    Counts how many environment rules are triggered
    for a given disease.
    """

    rules = DISEASE_ENV_RULES.get(disease, {})
    matches = 0

    for rule_key, rule_value in rules.items():
        if rule_key not in environmental_data:
            continue

        env_value = environmental_data[rule_key]

        if isinstance(rule_value, bool):
            if env_value == rule_value:
                matches += 1

        elif isinstance(rule_value, (int, float)):
            if env_value >= rule_value:
                matches += 1

    return matches


def risk_engine(
    *,
    ml_predictions: Dict[str, float],
    environmental_data: Dict,
    nlp_features: Dict,
    top_k: int = 5
) -> List[Dict]:
    """
    Final risk ranking engine.

    Inputs:
    - ml_predictions: disease → probability
    - environmental_data: live env metrics
    - nlp_features: structured user health profile
    """

    results = []

    for disease, ml_prob in ml_predictions.items():
        rule_hits = evaluate_environmental_rules(disease, environmental_data)
        env_stress = environmental_data.get("env_stress_index", 0.5)

        # Step 1: base severity
        base_severity = compute_base_severity(
            ml_probability=ml_prob,
            rule_matches=rule_hits,
            env_stress_score=env_stress
        )

        # Step 2: human modifiers
        final_severity = apply_human_modifiers(
            base_severity,
            age=nlp_features.get("age", 0),
            lifestyle=nlp_features.get("lifestyle", {}),
            has_condition=disease in nlp_features.get("conditions", []),
            family_history=disease in nlp_features.get("family_history", [])
        )

        # Step 3: thresholding
        if final_severity < 0.25:
            continue

        results.append({
            "disease": disease,
            "severity": final_severity,
            "ml_probability": round(ml_prob, 3),
            "rule_matches": rule_hits,
            "recommendations": get_recommendations(disease, final_severity)
        })

    # Step 4: rank & select
    results.sort(key=lambda x: x["severity"], reverse=True)
    return results[:top_k]





# backend/ml_service/engines/risk_engine.py

"""import math
from typing import Dict, List
from shared.schemas import MLFeatures, LocationInput

# -------------------------------------------------------------------
# 1. MASTER DISEASE LIST (Expandable)
# Just add more diseases here—no other code changes required.
# -------------------------------------------------------------------
DISEASES = [
    "Asthma", "COPD", "AllergicRhinitis", "Bronchitis", "Pneumonia", "Hypoxia",
    "Hypertension", "CardiacIssue", "StrokeRisk", "Diabetes", "Obesity",
    "Dengue", "Malaria", "SkinInfection", "UrinaryInfection",
    "Gastritis", "LiverIssue", "KidneyIssue", "Anemia",
    "Migraine", "Depression", "Anxiety",
    "Thyroid", "PCOS",
    "Arthritis"
]

# -------------------------------------------------------------------
# 2. Helper: clamp values to [0,1]
# -------------------------------------------------------------------
def clamp(x: float) -> float:
    return max(0.0, min(1.0, x))

# -------------------------------------------------------------------
# 3. SYMPTOM / CONDITION BOOSTS (based on NLP)
# -------------------------------------------------------------------
CONDITION_BOOSTS = {
    "Cold": {"AllergicRhinitis": 0.25, "Bronchitis": 0.20, "Pneumonia": 0.10},
    "Fever": {"Dengue": 0.20, "Malaria": 0.15, "Pneumonia": 0.10},
    "Cough": {"Asthma": 0.20, "Bronchitis": 0.20, "Pneumonia": 0.15},
    "Headache": {"Migraine": 0.25, "Anxiety": 0.10},
    "PCOS": {"PCOS": 0.40, "Thyroid": 0.20, "Obesity": 0.25, "Migraine": 0.15},
}

# -------------------------------------------------------------------
# 4. AGE EFFECTS (Balanced Scaling)
# -------------------------------------------------------------------
def age_modifier(age: int, disease: str) -> float:
    if age <= 20:
        # teenagers → low chronic disease risk
        if disease in {"COPD", "CardiacIssue", "StrokeRisk", "Hypertension"}:
            return -0.40
        if disease in {"Arthritis"}:
            return -0.30
    if age >= 60:
        # elderly → chronic disease rises
        if disease in {"StrokeRisk", "CardiacIssue", "Arthritis", "Hypertension"}:
            return +0.25
    return 0.0

# -------------------------------------------------------------------
# 5. LIFESTYLE EFFECTS
# -------------------------------------------------------------------
def lifestyle_modifier(mf: MLFeatures, disease: str) -> float:
    score = 0
    if mf.smoking == 1:
        if disease in {"Asthma", "COPD", "Bronchitis", "Pneumonia", "CardiacIssue"}:
            score += 0.25
    if mf.alcohol == 1:
        if disease in {"LiverIssue"}:
            score += 0.30
    if mf.poor_diet == 1:
        if disease in {"Diabetes", "Obesity", "Gastritis"}:
            score += 0.25
    return score

# -------------------------------------------------------------------
# 6. ENVIRONMENTAL RISK INTEGRATION
# These values will come from engines: pollution, NDVI, climate.
# -------------------------------------------------------------------
def environmental_modifier(poll: float, env: float, climate: float, disease: str) -> float:
    score = 0
    # High pollution → respiratory diseases increase
    if disease in {"Asthma", "COPD", "AllergicRhinitis", "Bronchitis", "Pneumonia"}:
        score += 0.20 * poll

    # Low NDVI (urban heat island) → asthma + allergies
    if disease in {"Asthma", "AllergicRhinitis"}:
        score += 0.15 * env

    # High temp/humidity → skin infection + dehydration diseases
    if disease in {"SkinInfection", "Hypoxia"}:
        score += 0.20 * climate

    return score

# -------------------------------------------------------------------
# 7. FAMILY HISTORY EFFECT
# -------------------------------------------------------------------
def family_history_modifier(nlp_features, disease: str) -> float:
    fam = nlp_features.family_history
    if not fam:
        return 0
    score = 0
    if "asthma" in fam and disease == "Asthma":
        score += 0.20
    if "cardiovascular" in fam and disease in {"CardiacIssue", "Hypertension"}:
        score += 0.20
    return score

# -------------------------------------------------------------------
# 8. MAIN RISK ENGINE
# -------------------------------------------------------------------
def compute_disease_probabilities(nlp_features, ml_features: MLFeatures,
                                 pollution_risk: float,
                                 env_risk: float,
                                 climate_risk: float) -> Dict[str, float]:
    ""Return per-disease probability dict (0–1, balanced).""

    base = {d: 0.10 for d in DISEASES}  # baseline low risk

    # symptom-based boosts
    for cond in nlp_features.conditions:
        boosts = CONDITION_BOOSTS.get(cond, {})
        for disease, add in boosts.items():
            base[disease] = base.get(disease, 0.10) + add

    # apply lifestyle & age & env
    for disease in DISEASES:
        base[disease] += lifestyle_modifier(ml_features, disease)
        base[disease] += age_modifier(nlp_features.age, disease)
        base[disease] += family_history_modifier(nlp_features, disease)
        base[disease] += environmental_modifier(pollution_risk, env_risk, climate_risk, disease)

    # clamp
    final = {d: clamp(v) for d, v in base.items()}
    return final
"""
