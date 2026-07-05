from pydantic import BaseModel
from typing import List, Dict, Optional


class LocationInput(BaseModel):
    city: str
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PredictRequest(BaseModel):
    user_text: str
    location: LocationInput


class RiskItem(BaseModel):
    condition: str
    risk_score: float


class PredictResponse(BaseModel):
    top_risks: List[RiskItem]
    confidence: float
    explanations: Dict[str, str]
    recommendations: List[str]
