print("\n🔥 USING UPDATED RULE_ENGINE.PY 🔥\n")


import re
import logging
from typing import List, Tuple, Optional
from pathlib import Path
from difflib import get_close_matches

import pandas as pd

from shared.schemas import NLPFeatures, LifestyleFeatures, PollutionFeatures, MLFeatures
from .scispacy_service import extract_raw_entities

logger = logging.getLogger(__name__)

# ------------------------------------------------------------
# LOAD MODIS NDVI CITY LIST FOR LOCATION NORMALIZATION
# ------------------------------------------------------------

_MODIS_CSV_PATH = Path(__file__).resolve().parents[2] / "data" / "env" / "modis_ndvi.csv"

_city_list = None

def _load_city_list():
    """Load city list from MODIS CSV only once."""
    global _city_list
    if _city_list is not None:
        return

    try:
        if _MODIS_CSV_PATH.exists():
            df = pd.read_csv(
                _MODIS_CSV_PATH,
                usecols=lambda c: c.lower() in {"city", "lat", "lon", "ndvi_mean"}
            )
            if "city" in df.columns:
                _city_list = (
                    df["city"].dropna().astype(str).str.strip().str.lower().unique().tolist()
                )
                logger.info("Loaded %d cities from MODIS CSV for normalization.", len(_city_list))
                return
    except Exception as e:
        logger.warning("Failed loading MODIS CSV for city normalization: %s", e)

    _city_list = []


def _normalize_city_name(city: str) -> str:
    """Fuzzy-correct misspelled city names using MODIS CSV city list."""
    if not city:
        return city

    _load_city_list()

    city_clean = city.strip().lower()
    if not _city_list:
        return city_clean

    match = get_close_matches(city_clean, _city_list, n=1, cutoff=0.8)
    return match[0] if match else city_clean



TEXT_NORMALIZATION = {

    # ------------------------
    # BASIC SPELL CORRECTIONS
    # ------------------------
    "backpain": "back pain",
    "bpain": "back pain",
    "back-pain": "back pain",
    "stomachache": "stomach ache",
    "tummyache": "stomach ache",
    "headachee": "headache",
    "hedache": "headache",
    "migrain": "migraine",
    "feaver": "fever",
    "faver": "fever",
    "feavar": "fever",
    "diebities": "diabetes",
    "diabities": "diabetes",
    "diabates": "diabetes",
    "daibetes": "diabetes",
    "sugarproblem": "sugar problem",
    "throad": "throat",
    "soar throat": "sore throat",
    "soarthroat": "sore throat",
    "breating": "breathing",
    "brethless": "breathless",
    "breathles": "breathless",
    "breathlessness": "shortness of breath",
    "shalow breath": "shallow breath",
    "bp": "blood pressure",
    "b.p": "blood pressure",
    "coldcough": "cold cough",

    # ------------------------
    # COMBINED WORD SPLITTING
    # ------------------------
    "noseblock": "nose block",
    "noseblockage": "nose blockage",
    "jointpain": "joint pain",
    "kneepain": "knee pain",
    "legpain": "leg pain",
    "handpain": "hand pain",
    "shoulderpain": "shoulder pain",
    "chestpain": "chest pain",
    "bodypain": "body pain",
    "bodyache": "body ache",
    "musclepain": "muscle pain",
    "lowerbackpain": "lower back pain",
    "upperbackpain": "upper back pain",
    "highbp": "high blood pressure",
    "lowbp": "low blood pressure",
    "bloodsugar": "blood sugar",
    "highsugar": "high sugar",
    "lowsugar": "low sugar",

    # ------------------------
    # SPEECH NORMALIZATION (LOW-LITERACY USERS)
    # ------------------------
    "i have": "i have ",
    "i m ": "i am ",
    "im ": "i am ",
    "iam ": "i am ",
    "i've ": "i have ",
    "got ": "have ",
    "gotta ": "have to ",
    "cant": "can't",
    "dont": "don't",
    "hav": "have",
    "hv ": "have ",
    "plz": "please",
    "pls": "please",
    "smthing": "something",

    # ------------------------
    # HINGLISH / INDIAN PATTERNS
    # ------------------------
    "bukhar": "fever",
    "khansi": "cough",
    "sardi": "cold",
    "gala dard": "throat pain",
    "sir dard": "headache",
    "peeth dard": "back pain",
    "kamar dard": "back pain",
    "sandhi dard": "joint pain",
    "haath dard": "hand pain",
    "pair dard": "leg pain",
    "ungli dard": "finger pain",
    "saans nahi aa rahi": "breathing difficulty",
    "saans phoolna": "breathlessness",
    "saans rukna": "breath stopping",
    "dil dhadak raha": "heart racing",
    "dil tez chal raha": "heart racing",
    "dil bahut tez": "heart racing",
    "gas ho rahi": "gas problem",
    "pet dard": "stomach pain",
    "pet me jalan": "acidity",

    # ------------------------
    # LIFESTYLE NORMALIZATION
    # ------------------------
    "junkfood": "junk food",
    "fastfood": "fast food",
    "badfood": "bad food",
    "noexercise": "no exercise",
    "laziness": "low activity",
    "inactive": "sedentary",
    "nonsmoker": "non smoker",
    "smokeing": "smoking",
    "smokin": "smoking",
    "drinikng": "drinking",
    "alchohol": "alcohol",
    "alcool": "alcohol",
    "drinkng": "drinking",

    # ------------------------
    # ENVIRONMENTAL
    # ------------------------
    "poluted": "polluted",
    "pollutionarea": "pollution area",
    "highpollution": "high pollution",
    "dustyarea": "dusty area",
    "dirtyair": "dirty air",
    "badair": "bad air",
    "trafficpollution": "traffic pollution",
    "industrialarea": "industrial area",

    # ------------------------
    # SPELL CORRECTIONS FOR MEDICAL TERMS
    # ------------------------
    "sinusits": "sinusitis",
    "sinusitise": "sinusitis",
    "sinuss": "sinus",
    "bronchtis": "bronchitis",
    "bronchits": "bronchitis",
    "allergi": "allergy",
    "allergicreaction": "allergic reaction",
    "arthiritis": "arthritis",
    "artheritis": "arthritis",
    "arthiritis": "arthritis",
    "osteoartheritis": "osteoarthritis",
    "nephropathy": "kidney disease",
    "neuropathy": "nerve damage",

    # ------------------------
    # EMOTIONAL STATE NORMALIZATION
    # ------------------------
    "tension": "stress",
    "tanav": "stress",
    "pareeshani": "stress",
    "panicattack": "panic attack",
    "fear": "anxiety",
    "ghabrahat": "anxiety",
    "ghabra raha": "anxiety",
    "sad": "depressed",
    "feeling low": "depressed",
    "low mood": "depressed",

    # ------------------------
    # SUGAR / DIABETES
    # ------------------------
    "high sugar": "high blood sugar",
    "sugar is high": "high blood sugar",
    "sugar is low": "low blood sugar",
    "sugar gone up": "high blood sugar",
    "sugar gone down": "low blood sugar",

    # ------------------------
    # MISC GENERAL
    # ------------------------
    "painfull": "painful",
    "severe pain": "severe pain",
    "mild pain": "mild pain",
    "heavy pain": "severe pain",
    "light pain": "mild pain",
    "lots of pain": "severe pain",

}

def normalize_text(text: str) -> str:
    for wrong, correct in TEXT_NORMALIZATION.items():
        text = text.replace(wrong, correct)
    return text.lower()


# ------------------------------------------------------------
# AGE EXTRACTION (IMPROVED)
# ------------------------------------------------------------

def _extract_age(text: str) -> int:
    """Extract age from text and clamp unrealistic values."""
    t = text.lower()

    m = re.search(r"(\d{1,4})\s*years?\s*old", t)
    if not m:
        m = re.search(r"age\s*[:=]?\s*(\d{1,4})", t)

    if m:
        try:
            age = int(m.group(1))
            if 0 < age <= 120:
                return age
            if age > 120:
                logger.warning("Unrealistic age %s detected; clamping to 120.", age)
                return 120
        except ValueError:
            pass

    return 0


# ------------------------------------------------------------
# ENTITY FILTERING (FIX FOR NOISE LIKE "ear")
# ------------------------------------------------------------

def _filter_raw_entities(raw_entities: List[str], fallback_keywords: List[str]) -> List[str]:
    """Remove noisy entities."""
    clean = []
    for ent in raw_entities:
        if not isinstance(ent, str):
            continue

        e = ent.strip().lower()
        if not e:
            continue

        # Keep fallback keywords always
        if e in fallback_keywords:
            clean.append(e)
            continue

        # Remove too short tokens unless medical keyword
        if len(e) < 3:
            continue

        # Remove non-alphabetic garbage
        if not re.search(r"[a-zA-Z]", e):
            continue

        clean.append(e)

    return sorted(set(clean))


# ------------------------------------------------------------
# LIFESTYLE, POLLUTION, FAMILY HISTORY (UNCHANGED)
# ------------------------------------------------------------

def _infer_lifestyle(text: str) -> LifestyleFeatures:
    t = text.lower()
    ls = LifestyleFeatures()
    if any(x in t for x in ["smoke", "smoker", "smoking", "cigarette"]):
        ls.smoking = True
    if any(x in t for x in ["drink", "alcohol", "wine", "beer"]):
        ls.alcohol = True
    if "poor diet" in t or "junk food" in t or "unhealthy" in t:
        ls.diet = "poor"
    elif "balanced diet" in t or "healthy diet" in t:
        ls.diet = "good"
    else:
        ls.diet = "average"
    if "never exercise" in t or "no exercise" in t or "sedentary" in t:
        ls.exercise_level = "none"
    elif "walk" in t or "light exercise" in t:
        ls.exercise_level = "low"
    elif ("exercise" in t or "gym" in t or "run" in t):
        ls.exercise_level = "moderate"
    else:
        ls.exercise_level = "unknown"
    return ls


def _infer_pollution(text: str) -> PollutionFeatures:
    t = text.lower()
    p = PollutionFeatures()
    if "polluted" in t or "high pollution" in t:
        p.environment = "polluted"
        p.severity = "high"
    elif "clean air" in t or "rural area" in t:
        p.environment = "clean"
        p.severity = "low"
    elif "urban" in t or "city" in t:
        p.environment = "mixed"
        p.severity = "moderate"
    else:
        p.environment = "unknown"
        p.severity = "unknown"
    return p


def _extract_family_history(text: str) -> List[str]:
    t = text.lower()
    fam = []
    if "mother" in t and "asthma" in t:
        fam.append("asthma")
    if "father" in t and ("heart attack" in t or "cardiac" in t):
        fam.append("cardiovascular")
    if "family history" in t and "asthma" in t and "asthma" not in fam:
        fam.append("asthma")
    return fam

CONDITION_NORMALIZATION = {

    # ----------------------------
    # RESPIRATORY (BREATHING ISSUES)
    # ----------------------------
    "asthma": "Asthma",
    "asma": "Asthma",
    "azma": "Asthma",
    "my asthma": "Asthma",
    "breathing problem": "Respiratory Issue",
    "breathing problems": "Respiratory Issue",
    "breathing issue": "Respiratory Issue",
    "breathing issues": "Respiratory Issue",
    "breathlessness": "Respiratory Issue",
    "breath less": "Respiratory Issue",
    "short breath": "Respiratory Issue",
    "shortness of breath": "Respiratory Issue",
    "difficulty breathing": "Respiratory Issue",
    "cant breathe": "Respiratory Issue",
    "cannot breathe": "Respiratory Issue",
    "hard to breathe": "Respiratory Issue",
    "wheezing": "Asthma",
    "wheez": "Asthma",
    "chest congestion": "Respiratory Congestion",
    "nose block": "Blocked Nose",
    "blocked nose": "Blocked Nose",
    "nose is blocked": "Blocked Nose",
    "sneeze": "Allergy",
    "sneezing": "Allergy",
    "running nose": "Allergic Rhinitis",
    "runny nose": "Allergic Rhinitis",
    "cold allergy": "Allergy",
    "dust allergy": "Allergy",
    "allergy": "Allergy",
    "allergies": "Allergy",

    # ----------------------------
    # SINUS / HEAD CONGESTION
    # ----------------------------
    "sinus": "Sinusitis",
    "sinusitis": "Sinusitis",
    "sinus infection": "Sinusitis",
    "sinus issue": "Sinusitis",
    "sinus problem": "Sinusitis",
    "sinus pain": "Sinusitis",
    "nose pain": "Sinusitis",
    "forehead pressure": "Sinusitis",
    "head pressure": "Sinusitis",

    # ----------------------------
    # BRONCHITIS / COUGHING
    # ----------------------------
    "bronchitis": "Bronchitis",
    "dry cough": "Cough",
    "wet cough": "Cough",
    "coughing": "Cough",
    "bad cough": "Cough",
    "severe cough": "Cough",
    "persistent cough": "Cough",

    # ----------------------------
    # HEART / CARDIAC CONDITIONS
    # ----------------------------
    "heart issue": "Cardiac Issue",
    "heart issues": "Cardiac Issue",
    "heart problem": "Cardiac Issue",
    "heart problems": "Cardiac Issue",
    "heart pain": "Cardiac Issue",
    "chest pain": "Chest Pain",
    "chest tightness": "Cardiac Issue",
    "tight chest": "Cardiac Issue",
    "pressure in chest": "Cardiac Issue",
    "heart racing": "Arrhythmia",
    "heart beat fast": "Arrhythmia",
    "fast heartbeat": "Arrhythmia",
    "irregular heartbeat": "Arrhythmia",
    "palpitations": "Arrhythmia",
    "palpitation": "Arrhythmia",

    "high bp": "Hypertension",
    "bp high": "Hypertension",
    "bp is high": "Hypertension",
    "blood pressure high": "Hypertension",
    "high blood pressure": "Hypertension",

    "low bp": "Hypotension",
    "bp low": "Hypotension",
    "blood pressure low": "Hypotension",
    "low blood pressure": "Hypotension",

    "heart attack": "Cardiac Event",
    "attack in heart": "Cardiac Event",

    # ----------------------------
    # DIABETES / METABOLIC
    # ----------------------------
    "diabetes": "Diabetes",
    "diabetic": "Diabetes",
    "high sugar": "Diabetes",
    "sugar high": "Diabetes",
    "sugar problem": "Diabetes",
    "sugar disease": "Diabetes",
    "type 1 diabetes": "Diabetes Type 1",
    "type 2 diabetes": "Diabetes Type 2",
    "prediabetes": "Prediabetes",

    "low sugar": "Hypoglycemia",
    "sugar low": "Hypoglycemia",
    "sugar drop": "Hypoglycemia",

    "thyroid": "Thyroid Disorder",
    "hypothyroid": "Hypothyroidism",
    "hyperthyroid": "Hyperthyroidism",
    "pcos": "PCOS",
    "pcod": "PCOS",

    # ----------------------------
    # PAIN CONDITIONS
    # ----------------------------
    "back pain": "Back Pain",
    "lower back pain": "Back Pain",
    "upper back pain": "Back Pain",
    "backpain": "Back Pain",
    "bpain": "Back Pain",
    "spine pain": "Back Pain",

    "neck pain": "Neck Pain",
    "shoulder pain": "Shoulder Pain",
    "arm pain": "Arm Pain",
    "hand pain": "Hand Pain",
    "leg pain": "Leg Pain",
    "knee pain": "Knee Pain",
    "ankle pain": "Ankle Pain",
    "foot pain": "Foot Pain",

    "joint pain": "Joint Pain",
    "body pain": "Body Pain",
    "body ache": "Body Pain",
    "full body pain": "Body Pain",
    "muscle pain": "Muscle Pain",
    "muscle ache": "Muscle Pain",
    "cramp": "Muscle Cramp",
    "cramps": "Muscle Cramp",

    "headache": "Headache",
    "head ache": "Headache",
    "head hurting": "Headache",
    "migraine": "Migraine",

    # ----------------------------
    # STOMACH / DIGESTIVE
    # ----------------------------
    "acidity": "Acid Reflux",
    "acid reflux": "Acid Reflux",
    "heartburn": "Acid Reflux",
    "gas": "Gastric Issue",
    "gas problem": "Gastric Issue",
    "gastric": "Gastric Issue",

    "stomach pain": "Stomach Pain",
    "stomachache": "Stomach Pain",
    "tummy pain": "Stomach Pain",
    "abdomen pain": "Abdominal Pain",
    "abdominal pain": "Abdominal Pain",

    "vomiting": "Vomiting",
    "nausea": "Nausea",
    "loose motion": "Diarrhea",
    "diarrhea": "Diarrhea",
    "constipation": "Constipation",
    "indigestion": "Indigestion",

    # ----------------------------
    # FEVER / INFECTIONS
    # ----------------------------
    "fever": "Fever",
    "high fever": "Fever",
    "viral fever": "Viral Infection",
    "cold": "Cold",
    "flu": "Flu",
    "sore throat": "Throat Infection",
    "throat pain": "Throat Infection",
    "infection": "Infection",
    "viral infection": "Viral Infection",
    "bacterial infection": "Bacterial Infection",

    # ----------------------------
    # MENTAL HEALTH
    # ----------------------------
    "stress": "Stress",
    "severe stress": "Stress",
    "mental stress": "Stress",
    "overthinking": "Anxiety",
    "thinking too much": "Anxiety",
    "anxiety": "Anxiety",
    "panic attack": "Panic Attack",
    "panic": "Panic Attack",
    "depression": "Depression",
    "depressed": "Depression",
    "lonely": "Depression",
    "insomnia": "Insomnia",
    "sleep problem": "Insomnia",
    "cant sleep": "Insomnia",

    # ----------------------------
    # SKIN CONDITIONS
    # ----------------------------
    "rashes": "Skin Allergy",
    "rash": "Skin Allergy",
    "itching": "Skin Irritation",
    "itchy": "Skin Irritation",
    "eczema": "Eczema",
    "psoriasis": "Psoriasis",
    "dry skin": "Skin Dryness",
    "skin allergy": "Skin Allergy",

    # ----------------------------
    # EYE / EAR
    # ----------------------------
    "eye pain": "Eye Issue",
    "red eye": "Eye Irritation",
    "itchy eye": "Eye Irritation",
    "watering eye": "Eye Irritation",
    "watery eye": "Eye Irritation",

    "ear pain": "Ear Infection",
    "ear infection": "Ear Infection",
    "hearing loss": "Hearing Issue",

    # ----------------------------
    # LIFESTYLE & HABITS
    # ----------------------------
    "smoking": "Smoking",
    "smokes": "Smoking",
    "smoker": "Smoking",
    "cigarette": "Smoking",
    "cigarettes": "Smoking",

    "alcohol": "Alcohol Use",
    "drinking": "Alcohol Use",
    "drink alcohol": "Alcohol Use",
    "regular drinker": "Alcohol Use",

    "junk food": "Poor Diet",
    "unhealthy food": "Poor Diet",
    "bad diet": "Poor Diet",
    "poor diet": "Poor Diet",

    "no exercise": "Sedentary Lifestyle",
    "never exercise": "Sedentary Lifestyle",
    "sedentary": "Sedentary Lifestyle",
    "inactive": "Sedentary Lifestyle",

    "light exercise": "Low Exercise",
    "walk daily": "Low Exercise",
    "walking": "Low Exercise",

    "gym": "Moderate Exercise",
    "exercise": "Moderate Exercise",
    "running": "Moderate Exercise",
    "workout": "Moderate Exercise",

    # ----------------------------
    # ENVIRONMENTAL EXPOSURE
    # ----------------------------
    "pollution": "Pollution Exposure",
    "polluted": "Pollution Exposure",
    "dirty air": "Pollution Exposure",
    "dusty air": "Pollution Exposure",
    "smoke exposure": "Pollution Exposure",
    "traffic pollution": "Pollution Exposure",
    "industrial area": "Pollution Exposure",

    # ----------------------------
    # FAMILY HISTORY
    # ----------------------------
    "mother asthma": "Asthma",
    "father asthma": "Asthma",
    "mother diabetes": "Diabetes",
    "father diabetes": "Diabetes",
    "family history asthma": "Asthma",
    "family history diabetes": "Diabetes",
    "parent heart attack": "Cardiac Issue",
    "father heart attack": "Cardiac Issue",
    "mother heart attack": "Cardiac Issue",

}


# ------------------------------------------------------------
# MAIN FUNCTION — UPDATED & CLEAN
# ------------------------------------------------------------

def build_nlp_and_ml_features(text: str) -> Tuple[NLPFeatures, MLFeatures]:
    from .scispacy_service import FALLBACK_MEDICAL_KEYWORDS  # avoid circular import

    text = normalize_text(text)

    raw_entities = extract_raw_entities(text)
    filtered_entities = _filter_raw_entities(raw_entities, FALLBACK_MEDICAL_KEYWORDS)

    age = _extract_age(text)
    life = _infer_lifestyle(text)
    poll = _infer_pollution(text)
    fam = _extract_family_history(text)

    conds = []
    for ent in filtered_entities:
        norm = CONDITION_NORMALIZATION.get(ent.lower())
        if norm and norm not in conds:
            conds.append(norm)

    if "asthma" in fam and "Asthma" not in conds:
        conds.append("Asthma")

    nlp = NLPFeatures(
        age=age,
        conditions=conds,
        lifestyle=life,
        pollution=poll,
        family_history=fam,
        raw_entities=filtered_entities,
    )

    ml = to_ml_features(nlp)
    return nlp, ml


# ------------------------------------------------------------
# CONVERT TO ML FEATURES (UNCHANGED)
# ------------------------------------------------------------

def to_ml_features(nlp: NLPFeatures) -> MLFeatures:
    mf = MLFeatures()
    mf.age = nlp.age
    mf.smoking = 1 if nlp.lifestyle.smoking else 0
    mf.alcohol = 1 if nlp.lifestyle.alcohol else 0

    if nlp.lifestyle.exercise_level == "none":
        mf.exercise_none = 1
    elif nlp.lifestyle.exercise_level == "low":
        mf.exercise_low = 1
    elif nlp.lifestyle.exercise_level == "moderate":
        mf.exercise_moderate = 1
    elif nlp.lifestyle.exercise_level == "high":
        mf.exercise_high = 1

    if nlp.lifestyle.diet == "poor":
        mf.poor_diet = 1

    if nlp.pollution.severity == "high":
        mf.pollution_high = 1
    elif nlp.pollution.severity == "moderate":
        mf.pollution_moderate = 1

    if any("asthma" in fh for fh in nlp.family_history):
        mf.family_history_asthma = 1
        mf.family_history_respiratory = 1

    return mf

"""def _extract_age(text: str) -> int:
    
    Extracts age from text; clamps unrealistic values to [0,120].
    If extracted age > 120, clamp to 120 and log a warning.

    t = text.lower()
    m = re.search(r"(\d{1,4})\s*years?\s*old", t)
    if not m:
        m = re.search(r"age\s*[:=]?\s*(\d{1,4})", t)
    if m:
        try:
            age = int(m.group(1))
            if 0 < age <= 120:
                return age
            # clamp unrealistic but keep value to avoid silent zeros
            if age > 120:
                logger.warning("Extracted unrealistic age=%s; clamping to 120.", age)
                return 120
        except ValueError:
            pass
    return 0

def _infer_lifestyle(text: str) -> LifestyleFeatures:
    t = text.lower()
    ls = LifestyleFeatures()
    if any(x in t for x in ["smoke", "smoker", "smoking", "cigarette"]):
        ls.smoking = True
    if any(x in t for x in ["drink", "alcohol", "wine", "beer"]):
        ls.alcohol = True
    if "poor diet" in t or "junk food" in t or "unhealthy" in t:
        ls.diet = "poor"
    elif "balanced diet" in t or "healthy diet" in t:
        ls.diet = "good"
    else:
        ls.diet = "average"
    if "never exercise" in t or "no exercise" in t or "sedentary" in t:
        ls.exercise_level = "none"
    elif "walk" in t or "light exercise" in t:
        ls.exercise_level = "low"
    elif "exercise" in t or "gym" in t or "run" in t:
        ls.exercise_level = "moderate"
    else:
        ls.exercise_level = "unknown"
    return ls


def _infer_pollution(text: str) -> PollutionFeatures:
    t = text.lower()
    p = PollutionFeatures()
    if "polluted" in t or "high pollution" in t:
        p.environment = "polluted"
        p.severity = "high"
    elif "clean air" in t or "rural area" in t:
        p.environment = "clean"
        p.severity = "low"
    elif "urban" in t or "city" in t:
        p.environment = "mixed"
        p.severity = "moderate"
    else:
        p.environment = "unknown"
        p.severity = "unknown"
    return p


def _extract_family_history(text: str) -> List[str]:
    t = text.lower()
    fam: List[str] = []
    if "mother" in t and "asthma" in t:
        fam.append("asthma")
    if "father" in t and ("heart attack" in t or "cardiac" in t):
        fam.append("cardiovascular")
    if "family history" in t and "asthma" in t and "asthma" not in fam:
        fam.append("asthma")
    return fam


def to_ml_features(nlp: NLPFeatures) -> MLFeatures:
    mf = MLFeatures()
    mf.age = nlp.age
    mf.smoking = 1 if nlp.lifestyle.smoking else 0
    mf.alcohol = 1 if nlp.lifestyle.alcohol else 0
    if nlp.lifestyle.exercise_level == "none":
        mf.exercise_none = 1
    elif nlp.lifestyle.exercise_level == "low":
        mf.exercise_low = 1
    elif nlp.lifestyle.exercise_level == "moderate":
        mf.exercise_moderate = 1
    elif nlp.lifestyle.exercise_level == "high":
        mf.exercise_high = 1
    if nlp.lifestyle.diet == "poor":
        mf.poor_diet = 1
    if nlp.pollution.severity == "high":
        mf.pollution_high = 1
    elif nlp.pollution.severity == "moderate":
        mf.pollution_moderate = 1
    if any("asthma" in fh for fh in nlp.family_history):
        mf.family_history_asthma = 1
        mf.family_history_respiratory = 1
    return mf"""