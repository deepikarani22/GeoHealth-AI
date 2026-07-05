import logging
import importlib
from typing import List
import re

logger = logging.getLogger(__name__)

# Try loading SciSpaCy model
try:
    en_core_sci_sm = importlib.import_module("en_core_sci_sm")
    _NLP = en_core_sci_sm.load()
    logger.info("Loaded en_core_sci_sm SciSpaCy model.")
except Exception as e:
    logger.warning("Unable to load en_core_sci_sm model: %s", e)
    _NLP = None


# -----------------------------
# FALLBACK KEYWORD LIST
# -----------------------------
FALLBACK_MEDICAL_KEYWORDS = [
    # Core diseases & conditions
    "asthma", "asthmatic", "sinus", "sinusitis", "bronchitis",
    "copd", "allergy", "allergic", "infection", "viral", "fever",
    "diabetes", "sugar", "hypertension", "bp", "blood pressure",
    "thyroid", "hypothyroid", "hyperthyroid", "pcos", "pcod",
    "cholesterol", "lipids", "obesity", "overweight", "arthritis",
    "osteoarthritis", "migraine", "headache", "stroke", "heart",
    "cardiac", "attack", "cancer", "tumor", "ulcer", "gastritis",
    "asthama", "dengue", "malaria", "pneumonia", "covid",

    # Respiratory symptoms
    "cough", "cold", "congestion", "wheezing", "breath", "breathing",
    "breathless", "chest", "tightness", "phlegm", "sputum",
    "runny", "blocked", "sneeze", "snoring", "wheeze", "dust",

    # Pain symptoms
    "pain", "ache", "shoulder", "neck", "knee",
    "joint", "bodyache", "cramp", "muscle", "spasm",
    "tingling", "numbness", "leg", "foot", "hand",
    "arm", "lower", "upper",

    # Digestive symptoms
    "vomit", "vomiting", "nausea", "gas", "acidity",
    "heartburn", "indigestion", "diarrhea", "loose",
    "constipation", "stomach", "abdominal", "bloating", "cramps",

    # Mental health
    "stress", "anxiety", "panic", "fear", "overthinking",
    "insomnia", "sad", "depressed", "lowmood", "mood",
    "psych", "mental",

    # Lifestyle habits
    "smoke", "smoker", "smoking", "tobacco", "cigarette",
    "drink", "alcohol", "wine", "beer", "junk", "fastfood",
    "unhealthy", "healthy", "gym", "exercise", "sedentary",

    # Environmental factors
    "pollution", "polluted", "dusty", "factory",
    "industrial", "traffic", "rural", "urban", "city", "dirty",

    # Family history
    "mother", "father", "parent", "family", "hereditary",
    "genetic", "history",

    # Hinglish common
    "bukhar", "khansi", "sardi", "gala", "dard", "saans",
    "pet", "kamar", "pair", "haath",

    # Chronic diseases
    "kidney", "liver", "fatty", "anemia",

    # Misc short expressions
    "itch", "rashes", "eczema", "swelling", "burning",
    "rash", "vision", "blur", "infection",

    # Low-literacy expressions
    "weak", "tired", "fatigue", "sleepy",

    # Severe emergencies
    "faint", "collapse", "unconscious", "bleeding",
    "severe", "acute", "chronic",
]


def extract_raw_entities(text: str) -> List[str]:
    """Extract entities using spaCy when available, otherwise fallback to keyword-based detection."""
    text_lower = text.lower()
    ents: List[str] = []

    # Use SciSpaCy if loaded
    if _NLP is not None:
        doc = _NLP(text)
        ents = sorted({ent.text.lower().strip() for ent in doc.ents if ent.text.strip()})

    # Fallback: keyword exact-word matching using boundaries
    for kw in FALLBACK_MEDICAL_KEYWORDS:
        # full-word matching only
        pattern = r"\b" + re.escape(kw) + r"\b"
        if re.search(pattern, text_lower):
            ents.append(kw)

    # Remove duplicates, sort
    return sorted(set(ents))
