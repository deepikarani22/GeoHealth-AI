from recommender_service.rules import build_recommendations


def test_ablation_removes_conditions(base_request):
    # baseline
    baseline = build_recommendations(base_request)

    # ablated
    base_request.nlp_features.conditions = []
    ablated = build_recommendations(base_request)

    assert baseline != ablated
