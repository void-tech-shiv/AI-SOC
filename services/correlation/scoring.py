def calculate_priority_score(severity: str, num_alerts: int, confidence: float, rule_id: str) -> int:
    score = 0
    if severity == 'critical':
        score += 50
    elif severity == 'high':
        score += 35
    elif severity == 'medium':
        score += 20
    else:
        score += 10
        
    score += min((num_alerts - 1) * 5, 25)
    score += int(confidence * 10)
    
    return max(0, min(100, score))
