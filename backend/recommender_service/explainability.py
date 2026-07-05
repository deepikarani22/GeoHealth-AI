def build_explanation(risk: dict) -> dict:
    """
    Produces a human-readable explanation for a risk.
    """

    reasons = []

    if risk["severity"] >= 0.75:
        reasons.append("Overall risk severity is high.")

    if risk["environmental_factors"]["pollution_risk"] >= 0.6:
        reasons.append("Elevated air pollution levels contributed to this risk.")

    if risk["environmental_factors"]["climate_risk"] >= 0.6:
        reasons.append("Current climate conditions increased susceptibility.")

    if risk.get("has_condition"):
        reasons.append("Existing medical history increases recurrence likelihood.")

    return {
        "summary": f"{risk['name']} risk identified due to combined environmental and personal factors.",
        "factors": reasons
    }
