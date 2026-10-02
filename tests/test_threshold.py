TRUST_THRESHOLD=70.0

def requires_fallback(score: float) -> bool:
    return score < TRUST_THRESHOLD

def test_low_score_requires_pin():
    assert requires_fallback(45.0)

def test_high_score_does_not_require_pin():
    assert not requires_fallback(88.0)
