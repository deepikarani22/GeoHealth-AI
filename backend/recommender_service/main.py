from fastapi import FastAPI
from shared.schemas import RecommendationRequest, RecommendationResponse
from .rules import build_recommendations

app = FastAPI(title="GeoHealthAI Recommender Service")


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest):
    return build_recommendations(payload)



"""from fastapi import FastAPI
from shared.schemas import RecommendationRequest, RecommendationResponse

app = FastAPI(title="GeoHealthAI Recommender Service")

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest):

    items = []

    for risk in payload.predictions.top_risks or []:
        items.append(
            f"For {risk.name}: {risk.reason}. "
            f"Pollution={risk.environmental_factors['pollution_risk']:.2f}, "
            f"Climate={risk.environmental_factors['climate_risk']:.2f}."
        )

    return RecommendationResponse(recommendations=items)"""



"""from fastapi import FastAPI
from shared.schemas import RecommendationRequest, RecommendationResponse
from .rules import build_recommendations

app = FastAPI(title="GeoHealthAI Recommendation Service")


@app.post("/recommend", response_model=RecommendationResponse)
def recommend(payload: RecommendationRequest):
    return build_recommendations(payload)"""
