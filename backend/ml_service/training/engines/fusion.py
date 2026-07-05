def fuse_risks(
    medical_risk: float,
    pollution_risk: float,
    env_risk: float,
    climate_risk: float,
) -> float:
    """
    Late fusion of the 4 components into a final risk in [0,1].
    """
    final = (
        0.50 * medical_risk +
        0.25 * pollution_risk +
        0.15 * env_risk +
        0.10 * climate_risk
    )
    # clamp to [0,1]
    return max(0.0, min(1.0, final))
