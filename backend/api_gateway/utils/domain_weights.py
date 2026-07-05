# How much each domain should influence GeoHealth risk

DOMAIN_RISK_WEIGHTS = {
    "respiratory": 0.40,      # pollution & climate sensitive
    "cardiac": 0.45,          # pollution & heat sensitive
    "metabolic": 0.25,
    "mental": 0.20,
    "infectious": 0.15,

    # Below domains should NOT increase environmental risk
    "digestive": 0.0,
    "musculoskeletal": 0.0,
    "skin": 0.0,
    "sensory": 0.0,
}
