from typing import Dict


def compute_base_severity(
    ml_probability: float,
    rule_matches: int,
    env_stress_score: float
) -> float:
    """
    Base severity from ML + environment rules
    Output range: 0.0 – 1.0
    """

    ml_component = ml_probability * 0.60
    rule_component = min(rule_matches / 5.0, 1.0) * 0.25
    env_component = min(env_stress_score, 1.0) * 0.15

    severity = ml_component + rule_component + env_component
    return min(round(severity, 3), 1.0)


def apply_human_modifiers(
    severity: float,
    *,
    age: int,
    lifestyle: Dict,
    has_condition: bool,
    family_history: bool
) -> float:
    """
    Applies patient-specific vulnerability modifiers.
    """

    # Age vulnerability
    if age >= 60:
        severity *= 1.15
    elif age <= 12:
        severity *= 1.10

    # Lifestyle risk
    if lifestyle.get("smoking"):
        severity *= 1.20

    if lifestyle.get("alcohol"):
        severity *= 1.05

    if lifestyle.get("exercise_level") in ("none", "low"):
        severity *= 1.05

    # Medical history
    if has_condition:
        severity *= 1.25

    if family_history:
        severity *= 1.10

    return min(round(severity, 3), 1.0)
