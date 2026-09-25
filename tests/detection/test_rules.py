from services.detection.normalizer import normalize_raw_event
from services.detection.rules import RULE_REGISTRY, DET001, DET002, DET003, DET004, DET005
from datetime import datetime
from collections import namedtuple

# Mock log for unit testing
MockLog = namedtuple('MockLog', ['id', 'timestamp', 'event_type', 'severity', 'message', 'raw_event'])

def test_normalizer_json():
    assert normalize_raw_event('{"foo": "bar"}') == {"foo": "bar"}
    
def test_normalizer_ast():
    assert normalize_raw_event("{'foo': 'bar'}") == {"foo": "bar"}

def test_normalizer_malformed():
    assert normalize_raw_event("malformed") == {}
    assert normalize_raw_event(123) == {}
    
def test_det001():
    rule = DET001()
    log_hit = MockLog(1, datetime.utcnow(), "login_failure", "high", "", '{"attempts": 5, "username": "admin"}')
    log_miss_1 = MockLog(2, datetime.utcnow(), "login_failure", "medium", "", '{"attempts": 4}')
    log_miss_2 = MockLog(3, datetime.utcnow(), "other", "medium", "", '{"attempts": 5}')
    
    finding = rule.evaluate(log_hit, normalize_raw_event(log_hit.raw_event))
    assert finding is not None
    assert finding.rule_id == "DET-001"
    
    assert rule.evaluate(log_miss_1, normalize_raw_event(log_miss_1.raw_event)) is None
    assert rule.evaluate(log_miss_2, normalize_raw_event(log_miss_2.raw_event)) is None

def test_det002():
    rule = DET002()
    log_hit = MockLog(1, datetime.utcnow(), "malware_detected", "critical", "", '{}')
    
    finding = rule.evaluate(log_hit, normalize_raw_event(log_hit.raw_event))
    assert finding is not None
    assert finding.rule_id == "DET-002"

def test_det003():
    rule = DET003()
    log_hit = MockLog(1, datetime.utcnow(), "network_anomaly", "high", "", '{"bytes": 1000000}')
    log_miss = MockLog(2, datetime.utcnow(), "network_anomaly", "high", "", '{"bytes": 999999}')
    
    assert rule.evaluate(log_hit, normalize_raw_event(log_hit.raw_event)) is not None
    assert rule.evaluate(log_miss, normalize_raw_event(log_miss.raw_event)) is None

def test_det004():
    rule = DET004()
    log_hit = MockLog(1, datetime.utcnow(), "data_access", "high", "", '{"query_count": 1000}')
    log_miss = MockLog(2, datetime.utcnow(), "data_access", "high", "", '{"query_count": 999}')
    
    assert rule.evaluate(log_hit, normalize_raw_event(log_hit.raw_event)) is not None
    assert rule.evaluate(log_miss, normalize_raw_event(log_miss.raw_event)) is None

def test_det005():
    rule = DET005()
    log_hit = MockLog(1, datetime.utcnow(), "random", "critical", "", '{}')
    log_miss = MockLog(2, datetime.utcnow(), "random", "high", "", '{}')
    
    assert rule.evaluate(log_hit, normalize_raw_event(log_hit.raw_event)) is not None
    assert rule.evaluate(log_miss, normalize_raw_event(log_miss.raw_event)) is None
