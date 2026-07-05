from recommender_service.rules import build_recommendations

SCENARIOS = [
    {
        "name": "Asthma patient, polluted environment",
        "expected_risk": "Asthma"
    }
]


def test_scenario_outputs(base_request):
    response = build_recommendations(base_request)

    joined_text = " ".join(response.recommendations)

    assert "Asthma" in joined_text

