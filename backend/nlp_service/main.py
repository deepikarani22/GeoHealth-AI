from fastapi import FastAPI
from shared.schemas import NLPExtractRequest, NLPExtractResponse
from .rule_engine import build_nlp_and_ml_features

app = FastAPI(title="GeoHealthAI NLP Service")


@app.post("/nlp/extract", response_model=NLPExtractResponse)
def extract(payload: NLPExtractRequest):
    nlp_features, ml_features = build_nlp_and_ml_features(payload.text)
    return NLPExtractResponse(nlp_features=nlp_features, ml_features=ml_features)
