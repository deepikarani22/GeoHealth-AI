from recommender_service.rules import build_recommendations


def test_deterministic_output(base_request):
    r1 = build_recommendations(base_request)
    r2 = build_recommendations(base_request)

    assert r1 == r2
