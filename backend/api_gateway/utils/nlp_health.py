LOW_RISK_PHRASES = [
    "fit", "healthy", "energetic", "doing well", "no issues"
]

MODERATE_RISK_PHRASES = [
    "breathless", "tired", "fatigue", "stress", "anxious",
    "cough", "headache", "dizzy"
]

HIGH_RISK_PHRASES = [
    "stroke", "heart attack", "cardiac", "asthma", "copd",
    "diabetes", "hypertension", "hospitalized", "surgery"
]


def compute_text_risk_modifier(text: str) -> float:
    text = text.lower()

    if any(p in text for p in HIGH_RISK_PHRASES):
        return 0.4

    if any(p in text for p in MODERATE_RISK_PHRASES):
        return 0.2

    if any(p in text for p in LOW_RISK_PHRASES):
        return -0.3

    return 0.0
