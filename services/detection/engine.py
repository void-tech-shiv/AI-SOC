from typing import List, Any, Tuple
from services.detection.normalizer import normalize_raw_event
from services.detection.rules import RULE_REGISTRY, DetectionFinding

def evaluate_log(log: Any) -> Tuple[List[DetectionFinding], int]:
    findings = []
    eval_count = 0
    
    try:
        normalized_event = normalize_raw_event(log.raw_event)
    except Exception:
        normalized_event = {}
        
    for rule in RULE_REGISTRY:
        # DET-005 is a fallback rule
        if rule.rule_id == "DET-005" and len(findings) > 0:
            continue
            
        eval_count += 1
        try:
            finding = rule.evaluate(log, normalized_event)
            if finding:
                findings.append(finding)
        except Exception as e:
            # isolate rule errors
            print(f"Error evaluating rule {rule.rule_id} for log {log.id}: {e}")
            pass
            
    return findings, eval_count

def get_detection_rules() -> List[dict]:
    return [
        {"rule_id": r.rule_id, "rule_name": r.rule_name}
        for r in RULE_REGISTRY
    ]
