from typing import Dict
from shared.schemas import NLPFeatures

# Map normalized conditions → ICD blocks
CONDITION_TO_ICD = {
    "asthma": "J00-J99",
    "respiratory issue": "J00-J99",
    "diabetes": "E00-E89",
    "hypertension": "I00-I99",
    "anxiety": "F01-F99",
    "depression": "F01-F99",
    "gastric issue": "K00-K95",
}

def adjust_disease_probs(
    disease_probs: Dict[str, float],
    nlp: NLPFeatures,
) -> Dict[str, float]:
    """
    Boost disease probabilities based on clinical signals.
    """

    adjusted = disease_probs.copy()

    for cond in nlp.conditions:
        key = cond.lower()
        icd = CONDITION_TO_ICD.get(key)
        if not icd or icd not in adjusted:
            continue

        # Boost by condition presence
        adjusted[icd] = min(adjusted[icd] + 0.15, 1.0)

    # Age-based adjustment
    if nlp.age >= 60:
        for icd in ("I00-I99", "E00-E89"):
            if icd in adjusted:
                adjusted[icd] = min(adjusted[icd] + 0.1, 1.0)

    return adjusted
