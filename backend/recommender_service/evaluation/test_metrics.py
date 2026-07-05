from recommender_service.evaluation.metrics import average_severity


def test_average_severity():
    risks = [
        {"severity": 0.8},
        {"severity": 0.6}
    ]

    avg = average_severity(risks)
    assert avg == 0.7
