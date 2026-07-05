def compute_confidence(risk: dict) -> float:
    """
    Confidence is based on agreement between signals.
    """

    score = 0.0

    if risk["severity"] >= 0.7:
        score += 0.4

    if risk["environmental_factors"]["pollution_risk"] >= 0.5:
        score += 0.2

    if risk["environmental_factors"]["climate_risk"] >= 0.5:
        score += 0.2

    if risk.get("has_condition"):
        score += 0.2

    return round(min(score, 1.0), 2)
