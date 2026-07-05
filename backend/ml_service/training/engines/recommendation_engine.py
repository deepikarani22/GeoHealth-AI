RECOMMENDATIONS = {
    "Asthma": [
        "Avoid outdoor activity during high pollution hours",
        "Use prescribed inhaler regularly",
        "Wear N95 mask outdoors"
    ],
    "COPD": [
        "Limit exposure to smoke and dust",
        "Use air purifier indoors"
    ],
    "HeatStress": [
        "Stay hydrated",
        "Avoid outdoor activity during peak heat",
        "Wear light cotton clothing"
    ],
    "Dengue": [
        "Prevent mosquito breeding near residence",
        "Use mosquito repellents",
        "Seek medical care if fever persists"
    ]
}

def get_recommendations(disease: str, severity: float):
    base = RECOMMENDATIONS.get(disease, [])
    if severity > 0.75:
        return base + ["Seek immediate medical advice"]
    return base
