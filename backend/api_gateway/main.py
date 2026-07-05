# geohealthai/backend/api_gateway/main.py

# geohealthai/backend/api_gateway/main.py


# geohealthai/backend/api_gateway/main.py

import logging
from typing import Dict, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from .utils.clinical_domain_interpreter import interpret_clinical_domains


from shared.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    NLPExtractResponse,
    MLPredictionResponse,
    RecommendationRequest,
    RecommendationResponse,
    PredictResponse,
    PredictRiskItem,
)

from shared.schemas import (
    PredictRequest,
    PredictResponse,
    DiseaseExplanation,
)
from api_gateway.utils.explainers import explain_disease_risk
from api_gateway.utils.icd_semantics import ICD_SEMANTIC_MAP
from api_gateway.utils.recommendation_fallback import enrich_recommendations
from api_gateway.utils.nlp_health import compute_text_risk_modifier


from .config import NLP_SERVICE_URL, ML_SERVICE_URL, RECOMMENDER_SERVICE_URL
from database import mysql_db
from shared.schemas import PredictRequest
from api_gateway.utils.clinical_adjuster import adjust_disease_probs

# -------------------------------------------------
# Logging
# -------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_gateway")

# -------------------------------------------------
# FastAPI App
# -------------------------------------------------
app = FastAPI(title="GeoHealthAI API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mysql_db.init_mysql()

# -------------------------------------------------
# Health Check
# -------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "api_gateway"}


# =================================================
# INTERNAL PIPELINE (PURE LOGIC — NO FASTAPI TYPES)
# =================================================
async def run_pipeline(payload: AnalyzeRequest) -> AnalyzeResponse:

    if payload.location is None or not payload.location.city:
        raise HTTPException(
            status_code=400,
            detail="Location with city is required for analysis",
        )

    nlp_request: Dict = {
        "text": payload.text,
        "location": payload.location.dict(),
    }

    timeout = httpx.Timeout(15.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:

        # ---------------------------
        # 1. NLP SERVICE
        # ---------------------------
        try:
            logger.info("Calling NLP service")
            nlp_resp = await client.post(
                f"{NLP_SERVICE_URL}/nlp/extract",
                json=nlp_request,
            )
            nlp_resp.raise_for_status()
            nlp_data = NLPExtractResponse(**nlp_resp.json())
        except Exception as e:
            logger.exception("NLP service failed")
            raise HTTPException(status_code=502, detail=str(e))

        # ---------------------------
        # 2. ML SERVICE (CITY-BASED)
        # ---------------------------
        ml_request = {
            "city": payload.location.city,
            "nlp_features": nlp_data.nlp_features.dict(),
            "ml_features": nlp_data.ml_features.dict()
        }


        try:
            logger.info("Calling ML service")
            ml_resp = await client.post(
                f"{ML_SERVICE_URL}/ml/predict",
                json=ml_request,
            )
            ml_resp.raise_for_status()
            ml_data = MLPredictionResponse(**ml_resp.json())
        except Exception as e:
            logger.exception("ML service failed")
            raise HTTPException(status_code=502, detail=str(e))


        # ---------------------------
        # 3. RECOMMENDER SERVICE
        # ---------------------------
        rec_request = RecommendationRequest(
            nlp_features=nlp_data.nlp_features,
            ml_features=nlp_data.ml_features,
            predictions=ml_data,
        )

        try:
            logger.info("Calling Recommender service")
            rec_resp = await client.post(
                f"{RECOMMENDER_SERVICE_URL}/recommend",
                json=rec_request.dict(),
            )
            rec_resp.raise_for_status()
            rec_data = RecommendationResponse(**rec_resp.json())
        except Exception as e:
            logger.exception("Recommender service failed")
            raise HTTPException(status_code=502, detail=str(e))

    return AnalyzeResponse(
        status="success",
        nlp_features=nlp_data.nlp_features,
        ml_features=nlp_data.ml_features,
        predictions=ml_data,
        recommendations=rec_data,
    )


# =================================================
# INTERNAL / DEBUG ENDPOINT (HIDDEN)
# =================================================
@app.post("/analyze", response_model=AnalyzeResponse, include_in_schema=False)
async def analyze(payload: AnalyzeRequest, request: Request):

    response = await run_pipeline(payload)

    # Best-effort MySQL logging
    try:
        mysql_db.save_request(
            user_text=payload.text,
            location_dict=payload.location.dict(),
            nlp_features=response.nlp_features.dict(),
            ml_predictions=response.predictions.dict(),
            recommendations=response.recommendations.recommendations,
            client_ip=request.client.host if request.client else None,
        )
    except Exception:
        logger.exception("MySQL logging failed (ignored)")

    return response


# =================================================
# PUBLIC / PRODUCTION ENDPOINT
# =================================================
@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest):
    """
    Public prediction endpoint.
    Input: user text + city only
    Output: ML risks + explainability + recommendations
    """

    # ----------------------------------
    # Step 1: Build AnalyzeRequest
    # ----------------------------------
    analyze_payload = AnalyzeRequest(
        text=payload.text,
        location={"city": payload.city},
    )

    # ----------------------------------
    # Step 2: Run full pipeline
    # ----------------------------------
    analyze_response = await run_pipeline(analyze_payload)

    ml = analyze_response.predictions
    nlp = analyze_response.nlp_features
    adjusted_probs = adjust_disease_probs(
        ml.disease_probs or {},
        nlp
    )
    ml.disease_probs = adjusted_probs

    # ----------------------------------
    # Step 3: Build disease-level output
    # ----------------------------------
    text_modifier = compute_text_risk_modifier(payload.text)

    """adjusted_final_risk = min(
        max((ml.final_risk or 0) + text_modifier, 0.0),
        1.0
    )"""
    clinical_signal = interpret_clinical_domains(nlp)

    adjusted_final_risk = min(
        max(
            (ml.final_risk or 0)
            + text_modifier
            + clinical_signal["severity_boost"],
            0.0,
        ),
        1.0,
    )

    top_diseases = []

    # Gate disease output strictly by adjusted risk
    if adjusted_final_risk >= 0.45:
        if ml.disease_probs:
            sorted_diseases = sorted(
                ml.disease_probs.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]

            for icd_code, prob in sorted_diseases:
                if prob < 0.25:
                    continue

                mapping = ICD_SEMANTIC_MAP.get(icd_code)
                if not mapping:
                    continue

                disease_name = mapping["primary_diseases"][0]

                top_diseases.append(
                    DiseaseExplanation(
                        name=disease_name,
                        probability=round(prob, 3),
                        why_high_risk=explain_disease_risk(
                            disease=disease_name,
                            probability=prob,
                            nlp_features=nlp,
                            pollution_risk=ml.pollution_risk or 0.0,
                            climate_risk=ml.climate_risk or 0.0,
                        ),
                    )
                )

    else:
        top_diseases = []
    # ----------------------------------
    # Step 3.5: Domain-aware prioritization
    # ----------------------------------
    if top_diseases and clinical_signal["domains"]:
        top_diseases.sort(
            key=lambda d: (
                0 if d.name.lower() in clinical_signal["domains"] else 1,
                -d.probability,
            )
        )
    top_diseases.sort(key=lambda d: d.probability, reverse=True)
    primary_condition = top_diseases[0].name if top_diseases else None

    raw_recommendations = analyze_response.recommendations.recommendations
    if nlp.conditions:
        recommendations = enrich_recommendations([], ml, nlp)

    # --------------------------------------------------
    # Apply fallback ONLY if recommender is generic
    # --------------------------------------------------

    if (
        len(raw_recommendations) == 1
        and "No significant" in raw_recommendations[0]
    ):
        recommendations = enrich_recommendations(
            raw_recommendations,
            ml,
            nlp,
        )
    else:
        recommendations = raw_recommendations

    # ----------------------------------
    # Step 4: Return enriched ML output
    # ----------------------------------
    return PredictResponse(
        risk_score=ml.risk_score,
        condition=primary_condition,
        nlp_features=nlp,
        env_risk=ml.env_risk,
        pollution_risk=ml.pollution_risk,
        climate_risk=ml.climate_risk,
        final_risk=round(adjusted_final_risk, 4),
        top_diseases=top_diseases,
        recommendations=recommendations
    )

"""top_diseases = []

    if ml.disease_probs:
        sorted_diseases = sorted(
            ml.disease_probs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        for disease, prob in sorted_diseases:
            top_diseases.append(
                DiseaseExplanation(
                    name=disease,
                    probability=round(prob, 3),
                    why_high_risk=explain_disease_risk(
                        disease=disease,
                        probability=prob,
                        nlp_features=nlp,
                        pollution_risk=ml.pollution_risk or 0.0,
                        climate_risk=ml.climate_risk or 0.0,
                    ),
                )
            )"""
"""top_diseases = []

    if ml.disease_probs:
        sorted_diseases = sorted(
            ml.disease_probs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        for icd_code, prob in sorted_diseases:
            mapping = ICD_SEMANTIC_MAP.get(icd_code)

            if not mapping:
                continue

            # pick most representative disease
            disease_name = mapping["primary_diseases"][0]
            

            top_diseases.append(
                DiseaseExplanation(
                    name=disease_name,
                    probability=round(prob, 3),
                    why_high_risk=explain_disease_risk(
                        disease=disease_name,
                        probability=prob,
                        nlp_features=nlp,
                        pollution_risk=ml.pollution_risk or 0.0,
                        climate_risk=ml.climate_risk or 0.0,
                    ),
                )
            )"""
"""ml_request = {
                "ml_features": nlp_data.ml_features.dict(),
                "nlp_features": nlp_data.nlp_features.dict(),
                "location": payload.location.dict(),
            }

            try:
                logger.info("Calling ML service")
                ml_resp = await client.post(
                    f"{ML_SERVICE_URL}/ml/predict",
                    json=ml_request,
                )
                ml_resp.raise_for_status()
                ml_data = MLPredictionResponse(**ml_resp.json())
            except Exception as e:
                logger.exception("ML service failed")
                raise HTTPException(status_code=502, detail=str(e))"""

"""import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from api_gateway.schemas.predict import PredictRequest, PredictResponse, RiskItem


from shared.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    NLPExtractResponse,
    MLPredictionResponse,
    RecommendationRequest,
    RecommendationResponse,
)

from .config import NLP_SERVICE_URL, ML_SERVICE_URL, RECOMMENDER_SERVICE_URL

# MySQL helper
from database import mysql_db

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("api_gateway")

# FastAPI app
app = FastAPI(title="GeoHealthAI API Gateway")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Init MySQL
mysql_db.init_mysql()


# ----------------------------------------------
# HEALTH CHECK
# ----------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "api_gateway"}


# ----------------------------------------------
# MAIN PIPELINE: NLP → ML → RECOMMENDER
# ----------------------------------------------
@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest, request: Request):
    ""
    Orchestrates the full pipeline:
        1. NLP extraction
        2. ML engine (medical + env + pollution + climate)
        3. Recommendations

    Also stores results into MySQL (best-effort).
    ""

    # -----------------------------
    # REQUIRE LOCATION ALWAYS
    # -----------------------------
    if payload.location is None or not payload.location.city:
        raise HTTPException(
            status_code=400,
            detail=(
                "Location (city) is required for pollution, climate and environment risk analysis. "
                "Provide: city name. System will auto-map NDVI, pollution and climate."
            ),
        )

    # -----------------------------
    # BUILD NLP REQUEST
    # -----------------------------
    nlp_request = {"text": payload.text, "location": payload.location.dict()}

    # Extra vitals (optional)
    vitals = {}
    if payload.systolic_bp is not None:
        vitals["systolic_bp"] = payload.systolic_bp
    if payload.diastolic_bp is not None:
        vitals["diastolic_bp"] = payload.diastolic_bp
    if payload.fasting_glucose is not None:
        vitals["fasting_glucose"] = payload.fasting_glucose
    if payload.bmi is not None:
        vitals["bmi"] = payload.bmi
    if vitals:
        nlp_request["vitals"] = vitals

    timeout = httpx.Timeout(15.0, connect=5.0)

    async with httpx.AsyncClient(timeout=timeout) as client:

        # ----------------------------------------------------
        # 1. NLP SERVICE
        # ----------------------------------------------------
        try:
            logger.info("Calling NLP service → %s/nlp/extract", NLP_SERVICE_URL)
            nlp_resp = await client.post(f"{NLP_SERVICE_URL}/nlp/extract", json=nlp_request)
            nlp_resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.exception("NLP service request failed")
            raise HTTPException(status_code=502, detail=f"NLP service error: {e}")

        try:
            nlp_data = NLPExtractResponse(**nlp_resp.json())
        except Exception as e:
            logger.exception("Could not parse NLP response")
            raise HTTPException(status_code=502, detail=f"Invalid NLP response: {e}")

        # ----------------------------------------------------
        # 2. ML SERVICE (UPDATED — SEND BOTH NLP + ML FEATURES)
        # ----------------------------------------------------
        ml_request = {
            "ml_features": nlp_data.ml_features.dict(),
            "nlp_features": nlp_data.nlp_features.dict(),  # <--- NEW & REQUIRED
            "location": payload.location.dict(),
        }

        try:
            logger.info("Calling ML service → %s/ml/predict", ML_SERVICE_URL)
            ml_resp = await client.post(f"{ML_SERVICE_URL}/ml/predict", json=ml_request)
            ml_resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.exception("ML service request failed")
            raise HTTPException(status_code=502, detail=f"ML service error: {e}")

        try:
            ml_data = MLPredictionResponse(**ml_resp.json())
        except Exception as e:
            logger.exception("Could not parse ML response")
            raise HTTPException(status_code=502, detail=f"Invalid ML response: {e}")

        # ----------------------------------------------------
        # 3. RECOMMENDER SERVICE
        # ----------------------------------------------------
        rec_request = RecommendationRequest(
            nlp_features=nlp_data.nlp_features,
            ml_features=nlp_data.ml_features,
            predictions=ml_data,
        )

        try:
            logger.info("Calling Recommender service → %s/recommend", RECOMMENDER_SERVICE_URL)
            rec_resp = await client.post(f"{RECOMMENDER_SERVICE_URL}/recommend", json=rec_request.dict())
            rec_resp.raise_for_status()
        except httpx.HTTPError as e:
            logger.exception("Recommender service request failed")
            raise HTTPException(status_code=502, detail=f"Recommender service error: {e}")

        try:
            rec_data = RecommendationResponse(**rec_resp.json())
        except Exception as e:
            logger.exception("Could not parse Recommender response")
            raise HTTPException(status_code=502, detail=f"Invalid recommender response: {e}")

    # -------------------------------------------
    # BUILD FINAL RESPONSE
    # -------------------------------------------
    response = AnalyzeResponse(
        status="success",
        nlp_features=nlp_data.nlp_features,
        ml_features=nlp_data.ml_features,
        predictions=ml_data,
        recommendations=rec_data,
    )


        # -------------------------------------------
        # SAVE TO MYSQL (BEST EFFORT)
        # -------------------------------------------
    try:
        client_ip = request.client.host if request.client else None
        mysql_db.save_request(
                user_text=payload.text,
                location_dict=payload.location.dict(),
                nlp_features=response.nlp_features.dict(),
                ml_predictions=response.predictions.dict(),
                recommendations=response.recommendations.recommendations,
                client_ip=client_ip,
        )
    except Exception:
            logger.exception("Failed to save request to MySQL (ignored).")

    return response
@app.post("/predict", response_model=PredictResponse)
async def predict(payload: PredictRequest):
    "
    Public prediction endpoint.
    Clean, frontend & paper-facing API.
    "

    # Reuse AnalyzeRequest internally
    analyze_payload = AnalyzeRequest(
    text=payload.user_text,
    location=payload.location
    )

    analyze_response: AnalyzeResponse = await analyze(
    analyze_payload,
    request=None  # MySQL logging not required here
    )

        # -----------------------------
        # Build clean response
        # -----------------------------
    top_risks = [
        RiskItem(condition=k, risk_score=v)
        for k, v in analyze_response.predictions.risk_scores.items()
    ]

    top_risks = sorted(
        top_risks, key=lambda x: x.risk_score, reverse=True
    )[:5]

    return PredictResponse(
        top_risks=top_risks,
        confidence=analyze_response.predictions.confidence,
        explanations=analyze_response.predictions.explanations,
        recommendations=analyze_response.recommendations.recommendations,
    )"""


