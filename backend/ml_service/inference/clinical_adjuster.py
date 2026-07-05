# geohealthai/backend/ml_service/inference/clinical_adjuster.py

from typing import Dict, Optional


def apply_clinical_adjustments(
    icd_risks: Dict[str, float],
    nlp_features: Optional[Dict],
    ml_features: Optional[Dict],
) -> Dict[str, float]:
    """
    Adjust environment-based disease probabilities using clinical signals.
    This does NOT retrain ML — only post-processes predictions.
    """

    # Safety: no clinical info → no adjustment
    if not icd_risks or (not nlp_features and not ml_features):
        return icd_risks

    adjusted = icd_risks.copy()

    conditions = [
        c.lower()
        for c in (nlp_features.get("conditions", []) if nlp_features else [])
    ]
    age = nlp_features.get("age", 0) if nlp_features else 0

    # -----------------------------
    # RESPIRATORY
    # -----------------------------
    if any(x in conditions for x in ["asthma", "respiratory issue", "bronchitis"]):
        if "prev_Asthma" in adjusted:
            adjusted["prev_Asthma"] *= 1.25
        if "prev_COPD" in adjusted:
            adjusted["prev_COPD"] *= 1.15

    # -----------------------------
    # CARDIAC
    # -----------------------------
    if any(x in conditions for x in ["cardiac issue", "heart attack", "stroke"]):
        if "prev_Hypertension" in adjusted:
            adjusted["prev_Hypertension"] *= 1.20
        if "prev_StrokeRisk" in adjusted:
            adjusted["prev_StrokeRisk"] *= 1.25

    # -----------------------------
    # METABOLIC
    # -----------------------------
    if any(x in conditions for x in ["diabetes", "prediabetes"]):
        if "prev_Diabetes" in adjusted:
            adjusted["prev_Diabetes"] *= 1.25
        if "prev_Obesity" in adjusted:
            adjusted["prev_Obesity"] *= 1.15

    # -----------------------------
    # MENTAL HEALTH
    # -----------------------------
    if any(x in conditions for x in ["anxiety", "depression", "stress"]):
        if "prev_Anxiety" in adjusted:
            adjusted["prev_Anxiety"] *= 1.20
        if "prev_Depression" in adjusted:
            adjusted["prev_Depression"] *= 1.15

    # -----------------------------
    # DIGESTIVE
    # -----------------------------
    if any(x in conditions for x in ["gastric issue", "acid reflux", "gastritis"]):
        if "prev_Gastritis" in adjusted:
            adjusted["prev_Gastritis"] *= 1.20

    # -----------------------------
    # AGE SENSITIVITY
    # -----------------------------
    if age >= 60:
        for k in adjusted:
            adjusted[k] *= 1.10

    # -----------------------------
    # CLAMP (medical sanity)
    # -----------------------------
    for k in adjusted:
        adjusted[k] = round(min(adjusted[k], 0.95), 4)

    return adjusted
