import pytest
from services.detection.engine import evaluate_log
from collections import namedtuple
from datetime import datetime

MockLog = namedtuple('MockLog', ['id', 'timestamp', 'event_type', 'severity', 'message', 'raw_event'])

def test_engine_survives_malformed_event():
    log = MockLog(1, datetime.utcnow(), "unknown", "low", "msg", "INVALID_JSON")
    # Should not crash
    findings, _ = evaluate_log(log)
    assert len(findings) == 0

def test_engine_det005_fallback():
    # If malware_detected is triggered (critical), DET-002 should match, DET-005 should be skipped
    log = MockLog(1, datetime.utcnow(), "malware_detected", "critical", "msg", "{}")
    findings, _ = evaluate_log(log)
    
    rule_ids = [f.rule_id for f in findings]
    assert "DET-002" in rule_ids
    assert "DET-005" not in rule_ids
    
    # If unknown critical, DET-005 should match
    log2 = MockLog(2, datetime.utcnow(), "unknown", "critical", "msg", "{}")
    findings2, _ = evaluate_log(log2)
    
    rule_ids2 = [f.rule_id for f in findings2]
    assert "DET-005" in rule_ids2
    assert len(rule_ids2) == 1
