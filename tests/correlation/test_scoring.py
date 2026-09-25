import pytest
from services.correlation.scoring import calculate_priority_score

def test_confidence_adds_points_correctly():
    # baseline for low severity, 1 alert is 10 points
    score_0 = calculate_priority_score('low', 1, 0.0, 'rule1')
    assert score_0 == 10  # 10 + 0

    score_half = calculate_priority_score('low', 1, 0.5, 'rule1')
    assert score_half == 15  # 10 + 5

    score_full = calculate_priority_score('low', 1, 1.0, 'rule1')
    assert score_full == 20  # 10 + 10

def test_priority_score_bounds():
    # Max possible inputs: critical (50) + 100 alerts (25 max) + conf 1.0 (10) = 85. 
    # Let's force a scenario if any formula changed in future to ensure bounds.
    assert calculate_priority_score('critical', 1000, 1.0, 'rule1') <= 100
    assert calculate_priority_score('low', 1, 0.0, 'rule1') >= 0

def test_no_huge_confidence_allowance():
    # Even if someone accidentally passed 90.0, it should be clamped to 100 overall
    score_huge = calculate_priority_score('critical', 10, 90.0, 'rule1')
    assert score_huge == 100
