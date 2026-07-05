def enrich_recommendations(recommendations, ml, nlp):
    if not recommendations:
        recommendations = []

    # Detect generic fallback
    if len(recommendations) == 1 and "No significant" in recommendations[0]:
        enriched = []

        if ml.pollution_risk and ml.pollution_risk > 0.4:
            enriched.append("Avoid outdoor activity during high pollution hours")
            enriched.append("Use a certified mask (N95) outdoors")

        if ml.climate_risk and ml.climate_risk > 0.4:
            enriched.append("Take precautions during extreme weather conditions")

        if nlp.conditions:
            enriched.append("Continue prescribed medication and monitor symptoms")

        return enriched or recommendations

    return recommendations
