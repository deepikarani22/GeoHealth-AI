from typing import Dict


def compute_base_severity(
    ml_probability: float,
    pollution_risk: float,
    climate_risk: float
) -> float:
    """
    Base severity from ML + environmental risks
    """

    severity = (
        ml_probability * 0.6 +
        pollution_risk * 0.25 +
        climate_risk * 0.15
    )

    return min(round(severity, 3), 1.0)


def apply_human_modifiers(
    severity: float,
    *,
    age: int,
    lifestyle: Dict,
    has_condition: bool,
    family_history: bool
) -> float:

    if age >= 60:
        severity *= 1.15
    elif age <= 12:
        severity *= 1.10

    if lifestyle.smoking:
        severity *= 1.20

    if lifestyle.exercise_level in {"none", "low"}:
        severity *= 1.05

    if has_condition:
        severity *= 1.25

    if family_history:
        severity *= 1.10

    return min(round(severity, 3), 1.0)
