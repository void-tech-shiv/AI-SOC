import pytest
from datetime import datetime, timedelta, timezone
from services.correlation.engine import correlate_alerts

class MockAlert:
    def __init__(self, id, rule_id, severity, evidence, confidence_score, created_at=None):
        self.id = id
        self.rule_id = rule_id
        self.severity = severity
        self.created_at = created_at or datetime.now(timezone.utc)
        self.evidence = evidence
        self.confidence_score = confidence_score
        
def test_corr_001_same_user_within_window():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-001", "medium", {"username": "user1"}, 0.80, base_time),
        MockAlert(2, "DET-001", "medium", {"username": "user1"}, 0.80, base_time + timedelta(minutes=5))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-001"
    assert candidates[0].alert_ids == [1, 2]
    
def test_corr_001_same_ip_within_window():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-001", "high", {"src_ip": "10.0.0.1"}, 0.90, base_time),
        MockAlert(2, "DET-001", "medium", {"ip_address": "10.0.0.1"}, 0.70, base_time + timedelta(minutes=10))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-001"
    assert candidates[0].alert_ids == [1, 2]
    
def test_corr_001_unrelated_user_ip():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-001", "medium", {"username": "user1"}, 0.80, base_time),
        MockAlert(2, "DET-002", "medium", {"src_ip": "10.0.0.2"}, 0.80, base_time + timedelta(minutes=5))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 0

def test_corr_001_outside_window():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-001", "medium", {"username": "user1"}, 0.80, base_time),
        MockAlert(2, "DET-001", "medium", {"username": "user1"}, 0.80, base_time + timedelta(minutes=20))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 0

def test_corr_002_det002_plus_same_user():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-002", "high", {"username": "user1", "src_ip": "10.0.0.1"}, 0.90, base_time),
        MockAlert(2, "DET-001", "medium", {"username": "user1"}, 0.80, base_time + timedelta(minutes=10))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-002"
    assert candidates[0].alert_ids == [1, 2]

def test_corr_002_det002_plus_same_ip():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-002", "high", {"username": "user1", "src_ip": "10.0.0.1"}, 0.90, base_time),
        MockAlert(2, "DET-004", "medium", {"ip_address": "10.0.0.1"}, 0.80, base_time + timedelta(minutes=10))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-002"
    assert candidates[0].alert_ids == [1, 2]

def test_corr_002_unrelated():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-002", "high", {"username": "user1", "src_ip": "10.0.0.1"}, 0.90, base_time),
        MockAlert(2, "DET-001", "medium", {"username": "user2"}, 0.80, base_time + timedelta(minutes=10))
    ]
    candidates = correlate_alerts(alerts)
    # the second alert won't match, and the first alert (high) will be caught by CORR-005
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-005"
    assert candidates[0].alert_ids == [1]
    
def test_corr_002_outside_window():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-002", "high", {"username": "user1", "src_ip": "10.0.0.1"}, 0.90, base_time),
        MockAlert(2, "DET-001", "medium", {"username": "user1"}, 0.80, base_time + timedelta(minutes=40))
    ]
    candidates = correlate_alerts(alerts)
    # The first alert (high) will be caught by CORR-005
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-005"
    assert candidates[0].alert_ids == [1]

def test_corr_003_correlated():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-003", "high", {"src_ip": "10.0.0.2", "username": "admin"}, 0.95, base_time),
        MockAlert(2, "DET-004", "medium", {"ip_address": "10.0.0.2", "user": "admin"}, 0.80, base_time + timedelta(minutes=5))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-003"
    assert candidates[0].alert_ids == [1, 2]
    
def test_corr_003_different_ip_user():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-003", "high", {"src_ip": "10.0.0.2", "username": "admin"}, 0.95, base_time),
        MockAlert(2, "DET-004", "medium", {"ip_address": "10.0.0.3", "user": "user2"}, 0.80, base_time + timedelta(minutes=5))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-005"
    assert candidates[0].alert_ids == [1]

def test_corr_003_missing_context():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-003", "high", {}, 0.95, base_time),
        MockAlert(2, "DET-004", "medium", {}, 0.80, base_time + timedelta(minutes=5))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-005"
    assert candidates[0].alert_ids == [1]

def test_corr_003_outside_window():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-003", "high", {"src_ip": "10.0.0.2", "username": "admin"}, 0.95, base_time),
        MockAlert(2, "DET-004", "medium", {"ip_address": "10.0.0.2", "user": "admin"}, 0.80, base_time + timedelta(minutes=40))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-005"
    assert candidates[0].alert_ids == [1]

def test_corr_004_det005_critical():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-005", "critical", {"username": "admin"}, 0.99, base_time),
        MockAlert(2, "DET-001", "critical", {"username": "admin"}, 0.90, base_time + timedelta(minutes=10))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-004"
    assert candidates[0].alert_ids == [1, 2]
    
def test_corr_004_unrelated():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-001", "critical", {"username": "admin"}, 0.99, base_time),
        MockAlert(2, "DET-002", "critical", {"username": "user2"}, 0.90, base_time + timedelta(minutes=10))
    ]
    candidates = correlate_alerts(alerts)
    # Will be caught by CORR-005 separately
    assert len(candidates) == 2
    assert candidates[0].correlation_rule == "CORR-005"
    assert candidates[1].correlation_rule == "CORR-005"
    
def test_corr_004_outside_window():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-005", "critical", {"username": "admin"}, 0.99, base_time),
        MockAlert(2, "DET-001", "critical", {"username": "admin"}, 0.90, base_time + timedelta(minutes=30))
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 2
    assert candidates[0].correlation_rule == "CORR-005"
    assert candidates[1].correlation_rule == "CORR-005"
    
def test_corr_005_standalone():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-001", "high", {"username": "admin"}, 0.90, base_time),
        MockAlert(2, "DET-001", "critical", {"username": "user2"}, 0.95, base_time),
        MockAlert(3, "DET-001", "medium", {"username": "user3"}, 0.70, base_time),
        MockAlert(4, "DET-001", "low", {"username": "user4"}, 0.50, base_time)
    ]
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 2
    for c in candidates:
        assert c.correlation_rule == "CORR-005"
        assert c.severity in ["high", "critical"]
        
def test_engine_invariants():
    base_time = datetime.now(timezone.utc)
    alerts = [
        MockAlert(1, "DET-001", "high", {"username": "admin"}, 0.90, base_time),
        MockAlert(2, "DET-001", "high", {"username": "admin"}, 0.95, base_time + timedelta(minutes=5))
    ]
    
    candidates1 = correlate_alerts(alerts)
    candidates2 = correlate_alerts(alerts)
    
    # same input produces same incident_key
    assert candidates1[0].incident_key == candidates2[0].incident_key
    
    # original objects unchanged
    assert alerts[0].id == 1
    assert alerts[1].id == 2
    
    # priority score stays between 0 and 100
    assert 0 <= candidates1[0].priority_score <= 100
    
    # confidence score stays between 0.0 and 100.0
    assert 0.0 <= candidates1[0].confidence_score <= 1.0
    
    # one alert cannot appear in multiple candidates
    alerts = [
        MockAlert(1, "DET-002", "high", {"username": "admin", "src_ip": "10.0.0.1"}, 0.90, base_time),
        MockAlert(2, "DET-001", "medium", {"username": "admin"}, 0.95, base_time + timedelta(minutes=5))
    ]
    # DET-002 + same user triggers CORR-002.
    # The same user also triggers CORR-001. But CORR-002 has higher priority, so they should be combined by CORR-002
    candidates = correlate_alerts(alerts)
    assert len(candidates) == 1
    assert candidates[0].correlation_rule == "CORR-002"
    assert sorted(candidates[0].alert_ids) == [1, 2]
