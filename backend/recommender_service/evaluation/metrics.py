def risk_coverage(recommendations):
    return len(recommendations)

def average_severity(recommendations):
    if not recommendations:
        return 0
    return sum(r["severity"] for r in recommendations) / len(recommendations)

def confidence_alignment(recommendations):
    return all(
        r["confidence"] >= 0.6 for r in recommendations if r["severity"] >= 0.7
    )
