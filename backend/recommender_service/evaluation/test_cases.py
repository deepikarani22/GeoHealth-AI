TEST_CASES = [
    {
        "name": "High pollution asthma patient",
        "nlp_features": {
            "age": 55,
            "conditions": ["Asthma"],
            "lifestyle": {"smoking": False, "exercise_level": "low"},
            "family_history": []
        },
        "top_risks_expected": ["Asthma"]
    },
    {
        "name": "Young healthy individual, clean air",
        "nlp_features": {
            "age": 22,
            "conditions": [],
            "lifestyle": {"smoking": False, "exercise_level": "high"},
            "family_history": []
        },
        "top_risks_expected": []
    },
    {
        "name": "Elderly smoker in polluted city",
        "nlp_features": {
            "age": 68,
            "conditions": ["COPD"],
            "lifestyle": {"smoking": True, "exercise_level": "none"},
            "family_history": ["COPD"]
        },
        "top_risks_expected": ["COPD"]
    }
]
