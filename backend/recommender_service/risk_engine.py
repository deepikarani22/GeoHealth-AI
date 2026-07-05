from typing import List, Dict
from .severity_scoring import compute_base_severity, apply_human_modifiers
from .explainability import build_explanation
from .confidence import compute_confidence


def build_risk_profile(req) -> List[Dict]:
    """
    Converts ML + NLP + env signals into ranked disease risks
    """

    nlp = req.nlp_features
    pred = req.predictions

    risks: List[Dict] = []

    # If ML returned no risks, return empty safely
    if not pred.top_risks:
        return risks

    for risk in pred.top_risks:

        base_severity = compute_base_severity(
            ml_probability=risk.score,
            pollution_risk=risk.environmental_factors.get("pollution_risk", 0.0),
            climate_risk=risk.environmental_factors.get("climate_risk", 0.0),
        )

        final_severity = apply_human_modifiers(
            base_severity,
            age=nlp.age or 0,
            lifestyle=nlp.lifestyle,
            has_condition=risk.name in (nlp.conditions or []),
            family_history=risk.name in (nlp.family_history or []),
        )

        # Skip negligible risks
        if final_severity < 0.25:
            continue

        # -----------------------------
        # BUILD RISK PAYLOAD (SAFE)
        # -----------------------------
        risk_payload = {
            "name": risk.name,
            "severity": final_severity,
            "reason": risk.reason,
            "environmental_factors": risk.environmental_factors,
            "has_condition": risk.name in (nlp.conditions or []),
        }

        # Add explanation & confidence
        risk_payload["explanation"] = build_explanation(risk_payload)
        risk_payload["confidence"] = compute_confidence(risk_payload)

        risks.append(risk_payload)

    # Sort and return top 5
    risks.sort(key=lambda x: x["severity"], reverse=True)
    return risks[:5]



"""from typing import List, Dict
from .severity_scoring import compute_base_severity, apply_human_modifiers
from .explainability import build_explanation
from .confidence import compute_confidence


def build_risk_profile(req) -> List[Dict]:
    ""
    Converts ML + NLP + env signals into ranked disease risks
    ""

    nlp = req.nlp_features
    pred = req.predictions

    risks = []

    for risk in pred.top_risks or []:
        ""base_severity = compute_base_severity(
            ml_probability=risk.probability,
            pollution_risk=risk.environmental_factors["pollution_risk"],
            climate_risk=risk.environmental_factors["climate_risk"]
        )""
        base_severity = compute_base_severity(
            ml_probability=risk.score,
            pollution_risk=risk.environmental_factors.get("pollution_risk", 0.0),
            climate_risk=risk.environmental_factors.get("climate_risk", 0.0)
        )

        final_severity = apply_human_modifiers(
            base_severity,
            age=nlp.age or 0,
            lifestyle=nlp.lifestyle,
            has_condition=risk.name in (nlp.conditions or []),
            family_history=risk.name in (nlp.family_history or [])
        )

        if final_severity < 0.25:
            continue

        risk_payload = {
    "name": risk.name,
    "severity": final_severity,
    "reason": risk.reason,
    "environmental_factors": risk.environmental_factors,
    "has_condition": risk.name in (nlp.conditions or [])
    }

    risk_payload["explanation"] = build_explanation(risk_payload)
    risk_payload["confidence"] = compute_confidence(risk_payload)

    risks.append(risk_payload)


    risks.sort(key=lambda x: x["severity"], reverse=True)
    return risks[:5]"""
