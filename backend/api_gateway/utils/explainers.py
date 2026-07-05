def explain_disease_risk(
    disease: str,
    probability: float,
    nlp_features,
    pollution_risk: float,
    climate_risk: float,
):
    reasons = []

    if disease in (nlp_features.conditions or []):
        reasons.append("Condition mentioned by the user")

    if pollution_risk and pollution_risk > 0.4:
        reasons.append("High air pollution levels")

    if climate_risk and climate_risk > 0.4:
        reasons.append("Unfavorable weather conditions")

    if nlp_features.age and nlp_features.age > 60:
        reasons.append("Higher age increases vulnerability")

    if not reasons:
        reasons.append("Environmental and clinical factors combined increase risk")

    return reasons
