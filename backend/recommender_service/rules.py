from shared.schemas import RecommendationRequest, RecommendationResponse
from .risk_engine import build_risk_profile


def build_recommendations(req: RecommendationRequest) -> RecommendationResponse:
    risks = build_risk_profile(req)

    recommendations: list[str] = []

    for r in risks:
        if r["severity"] >= 0.8:
            level = "HIGH"
            advice = "Immediate preventive measures or clinical consultation is advised."
        elif r["severity"] >= 0.5:
            level = "MODERATE"
            advice = "Lifestyle and environmental precautions are recommended."
        else:
            level = "LOW"
            advice = "Continue monitoring and maintain healthy habits."

        recommendations.append(
            f"[{level}] {r['name']} risk detected. {r['reason']}. {advice}"
        )

    if not recommendations:
        recommendations.append(
            "No significant short-term environmental health risks detected at this time."
        )

    return RecommendationResponse(recommendations=recommendations)



"""from shared.schemas import RecommendationRequest, RecommendationResponse
from .risk_engine import build_risk_profile


def build_recommendations(req: RecommendationRequest) -> RecommendationResponse:
    risks = build_risk_profile(req)

    outputs = []

    for r in risks:
        if r["severity"] >= 0.8:
            advice = "Immediate preventive measures or clinical consultation is advised."
        elif r["severity"] >= 0.5:
            advice = "Lifestyle and environmental precautions are recommended."
        else:
            advice = "Continue monitoring and maintain healthy habits."

        outputs.append({
            "name": r["name"],
            "severity": r["severity"],
            "confidence": r["confidence"],
            "explanation": r["explanation"],
            "recommendation": advice
        })

    return RecommendationResponse(recommendations=outputs)"""





"""from shared.schemas import RecommendationRequest, RecommendationResponse


def build_recommendations(req: RecommendationRequest) -> RecommendationResponse:
    nlp = req.nlp_features
    ml = req.ml_features
    pred = req.predictions
    recs = []
    r = pred.risk_score
    if r >= 0.8:
        recs.append("Your respiratory risk appears high. Please consult a clinician for a detailed assessment.")
    elif r >= 0.5:
        recs.append("Your respiratory risk is moderate. Early lifestyle changes can still make a big impact.")
    else:
        recs.append("Your current respiratory risk is relatively low based on the provided information.")
    if nlp.lifestyle.smoking:
        recs.append("Consider starting a smoking cessation program; quitting smoking significantly reduces respiratory risk.")
    if nlp.lifestyle.diet == "poor":
        recs.append("Improve diet quality by increasing fruits, vegetables, and whole grains while reducing processed foods.")
    if nlp.lifestyle.exercise_level in {"none", "low"}:
        recs.append("Gradually increase physical activity, aiming for at least 3 sessions of light-to-moderate exercise per week.")
    if nlp.pollution.environment == "polluted" or ml.pollution_high:
        recs.append("Limit time outdoors on high-pollution days and consider using air-quality apps to plan activities.")
    if ml.family_history_asthma:
        recs.append("Because of a family history of asthma, monitor for wheezing or shortness of breath and seek evaluation if needed.")
    if nlp.age and nlp.age < 30 and r >= 0.5:
        recs.append("Making these changes now while you are young can help prevent early onset of chronic respiratory disease.")
    if not recs:
        recs.append("No specific concerns detected, but maintaining healthy lifestyle habits is always recommended.")
    return RecommendationResponse(recommendations=recs)"""
