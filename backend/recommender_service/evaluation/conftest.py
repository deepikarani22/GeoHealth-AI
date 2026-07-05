import pytest
from shared.schemas import (
    RecommendationRequest,
    NLPFeatures,
    LifestyleFeatures,
    PollutionFeatures,
    MLFeatures,
    MLPredictionResponse,
    TopRiskItem
)


@pytest.fixture
def base_request():
    """
    Minimal VALID RecommendationRequest for pytest evaluation.
    Matches shared/schemas.py EXACTLY.
    """

    # ---------- NLP FEATURES ----------
    nlp_features = NLPFeatures(
        age=55,
        conditions=["Asthma"],
        lifestyle=LifestyleFeatures(
            smoking=False,
            alcohol=False,
            diet="average",
            exercise_level="low"
        ),
        pollution=PollutionFeatures(
            environment="polluted",
            severity="high"
        ),
        family_history=[],
        raw_entities=["asthma", "pollution"]
    )

    # ---------- ML FEATURES ----------
    ml_features = MLFeatures(
        age=55,
        smoking=0,
        alcohol=0,
        exercise_none=0,
        exercise_low=1,
        exercise_moderate=0,
        exercise_high=0,
        poor_diet=0,
        pollution_high=1,
        pollution_moderate=0,
        family_history_asthma=0,
        family_history_respiratory=0
    )

    # ---------- TOP RISK ITEM ----------
    top_risk = TopRiskItem(
        name="Asthma",
        score=0.78,
        reason="High PM2.5 exposure",
        environmental_factors={
            "pollution_risk": 0.8,
            "climate_risk": 0.6
        },
        recommendations=[
            "Avoid outdoor activity during high pollution",
            "Use prescribed inhaler if needed"
        ]
    )

    # ---------- ML PREDICTION RESPONSE ----------
    predictions = MLPredictionResponse(
        risk_score=0.75,
        condition="Asthma",
        pollution_risk=0.8,
        climate_risk=0.6,
        final_risk=0.78,
        disease_probs={"Asthma": 0.78},
        top_risks=[top_risk]
    )

    # ---------- FINAL REQUEST ----------
    return RecommendationRequest(
        nlp_features=nlp_features,
        ml_features=ml_features,
        predictions=predictions
    )
