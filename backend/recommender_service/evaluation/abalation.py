def ablate_component(payload, component: str):
    if component == "nlp":
        payload.nlp_features.conditions = []
        payload.nlp_features.family_history = []

    if component == "lifestyle":
        payload.nlp_features.lifestyle.smoking = False
        payload.nlp_features.lifestyle.exercise_level = "high"

    if component == "environment":
        for r in payload.predictions.top_risks:
            r.environmental_factors["pollution_risk"] = 0.1
            r.environmental_factors["climate_risk"] = 0.1

    return payload
