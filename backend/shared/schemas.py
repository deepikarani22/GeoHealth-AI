from typing import List, Optional, Dict
from pydantic import BaseModel

# ==============================
# Location
# ==============================

class LocationInput(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# ==============================
# NLP Layer
# ==============================

class LifestyleFeatures(BaseModel):
    smoking: bool = False
    alcohol: bool = False
    diet: str = "average"
    exercise_level: str = "unknown"

class PollutionFeatures(BaseModel):
    environment: str = "unknown"
    severity: str = "unknown"

class NLPFeatures(BaseModel):
    age: int = 0
    conditions: List[str] = []
    lifestyle: LifestyleFeatures = LifestyleFeatures()
    pollution: PollutionFeatures = PollutionFeatures()
    family_history: List[str] = []
    raw_entities: List[str] = []

# ==============================
# ML Features
# ==============================

class MLFeatures(BaseModel):
    age: float = 0.0
    smoking: int = 0
    alcohol: int = 0
    exercise_none: int = 0
    exercise_low: int = 0
    exercise_moderate: int = 0
    exercise_high: int = 0
    poor_diet: int = 0
    pollution_high: int = 0
    pollution_moderate: int = 0
    family_history_asthma: int = 0
    family_history_respiratory: int = 0

# ==============================
# NLP Response
# ==============================

class NLPExtractRequest(BaseModel):
    text: str
    location: Optional[LocationInput] = None

class NLPExtractResponse(BaseModel):
    nlp_features: NLPFeatures
    ml_features: MLFeatures

# ==============================
# TOP RISK ITEM (NEW)
# ==============================

class TopRiskItem(BaseModel):
    name: str
    score: float
    reason: str
    environmental_factors: Dict[str, float]
    recommendations: List[str]

# ==============================
# ML Prediction Response (UPDATED)
# ==============================

class MLPredictionRequest(BaseModel):
    city: str

class MLPredictionResponse(BaseModel):
    risk_score: float

    # Primary predicted condition (optional summary)
    condition: Optional[str] = None

    env_risk: Optional[float] = None
    pollution_risk: Optional[float] = None
    climate_risk: Optional[float] = None
    final_risk: Optional[float] = None

    # Detailed disease probabilities
    disease_probs: Optional[Dict[str, float]] = None

    top_risks: Optional[List[TopRiskItem]] = None


# ==============================
# Recommendations
# ==============================

class RecommendationRequest(BaseModel):
    nlp_features: NLPFeatures
    ml_features: MLFeatures
    predictions: MLPredictionResponse

class RecommendationResponse(BaseModel):
    recommendations: List[str]

# ==============================
# API Gateway Final Response
# ==============================

class AnalyzeRequest(BaseModel):
    text: str
    location: Optional[LocationInput] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    fasting_glucose: Optional[float] = None
    bmi: Optional[float] = None

class AnalyzeResponse(BaseModel):
    status: str
    nlp_features: NLPFeatures
    ml_features: MLFeatures
    predictions: MLPredictionResponse
    recommendations: RecommendationResponse

# ==============================
# PUBLIC / FINAL PREDICT RESPONSE
# ==============================

class PredictRiskItem(BaseModel):
    condition: str
    risk_score: float


class PredictResponse(BaseModel):
    top_risks: List[PredictRiskItem]
    confidence: float
    explanations: Dict[str, str]
    recommendations: List[str]

# ==============================
# PUBLIC / PREDICT REQUEST
# ==============================

class PredictRequest(BaseModel):
    text: str
    city: str
    

class DiseaseExplanation(BaseModel):
    name: str
    probability: float
    why_high_risk: List[str]


class PredictResponse(BaseModel):
    risk_score: float
    condition: Optional[str]
    nlp_features: Optional[NLPFeatures] = None  # ✅ ADD THIS
    env_risk: Optional[float]
    pollution_risk: Optional[float]
    climate_risk: Optional[float]
    final_risk: Optional[float]

    top_diseases: List[DiseaseExplanation]
    recommendations: List[str]



"""from typing import List, Optional, Dict
from pydantic import BaseModel

# -------------------------------------------------
# 1. Common utility / shared models
# -------------------------------------------------

class LocationInput(BaseModel):
    "
    User location used by environmental, pollution and climate engines.
    "
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


# -------------------------------------------------
# 2. NLP feature models
# -------------------------------------------------

class LifestyleFeatures(BaseModel):
    smoking: bool = False
    alcohol: bool = False
    diet: str = "average"           # poor / average / good
    exercise_level: str = "unknown" # none / low / moderate / high / unknown


class PollutionFeatures(BaseModel):
    environment: str = "unknown"    # polluted / clean / mixed / unknown
    severity: str = "unknown"       # high / moderate / low / unknown


class NLPFeatures(BaseModel):
    "
    Structured representation of the user’s text.
    "
    age: int = 0
    conditions: List[str] = []
    lifestyle: LifestyleFeatures = LifestyleFeatures()
    pollution: PollutionFeatures = PollutionFeatures()
    family_history: List[str] = []
    raw_entities: List[str] = []


# -------------------------------------------------
# 3. ML feature vector (numeric features)
# -------------------------------------------------

class MLFeatures(BaseModel):
    "
    Flatteed ML vector built by rule_engine.to_ml_features()
    "
    age: float = 0.0

    smoking: int = 0
    alcohol: int = 0

    exercise_none: int = 0
    exercise_low: int = 0
    exercise_moderate: int = 0
    exercise_high: int = 0

    poor_diet: int = 0

    pollution_high: int = 0
    pollution_moderate: int = 0

    family_history_asthma: int = 0
    family_history_respiratory: int = 0


# -------------------------------------------------
# 4. NLP Service I/O
# -------------------------------------------------

class NLPExtractRequest(BaseModel):
    text: str
    location: Optional[LocationInput] = None


class NLPExtractResponse(BaseModel):
    nlp_features: NLPFeatures
    ml_features: MLFeatures


# -------------------------------------------------
# 5. ML Service I/O  (UPDATED)
# -------------------------------------------------

class MLPredictionRequest(BaseModel):
    "
    Updated: ML needs BOTH ml_features and nlp_features.
    "
    ml_features: MLFeatures
    nlp_features: NLPFeatures   # <-- NEW REQUIRED FIELD
    location: Optional[LocationInput] = None


class MLPredictionResponse(BaseModel):
    risk_score: float
    condition: str

    env_risk: Optional[float] = None
    pollution_risk: Optional[float] = None
    climate_risk: Optional[float] = None
    final_risk: Optional[float] = None

    disease_probs: Optional[Dict[str, float]] = None


# -------------------------------------------------
# 6. Recommendation service models
# -------------------------------------------------

class RecommendationRequest(BaseModel):
    nlp_features: NLPFeatures
    ml_features: MLFeatures
    predictions: MLPredictionResponse


class RecommendationResponse(BaseModel):
    recommendations: List[str]


# -------------------------------------------------
# 7. API Gateway models
# -------------------------------------------------

class AnalyzeRequest(BaseModel):
    text: str
    location: Optional[LocationInput] = None
    systolic_bp: Optional[float] = None
    diastolic_bp: Optional[float] = None
    fasting_glucose: Optional[float] = None
    bmi: Optional[float] = None


class AnalyzeResponse(BaseModel):
    status: str
    nlp_features: NLPFeatures
    ml_features: MLFeatures
    predictions: MLPredictionResponse
    recommendations: RecommendationResponse



"""