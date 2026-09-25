from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class DetectionFinding:
    rule_id: str
    rule_name: str
    title: str
    description: str
    severity: str
    confidence_score: float
    evidence: Dict[str, Any]

RULE_REGISTRY = []

def register_rule(cls):
    RULE_REGISTRY.append(cls())
    return cls

class BaseRule:
    rule_id: str
    rule_name: str
    
    def evaluate(self, log: Any, normalized_event: Dict[str, Any]) -> Optional[DetectionFinding]:
        raise NotImplementedError

@register_rule
class DET001(BaseRule):
    rule_id = "DET-001"
    rule_name = "Multiple Failed Login Attempts"
    
    def evaluate(self, log, normalized_event):
        if log.event_type == "login_failure" and normalized_event.get("attempts", 0) >= 5:
            return DetectionFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                title="Multiple Failed Login Attempts",
                description=f"User {normalized_event.get('username')} failed to login {normalized_event.get('attempts')} times",
                severity="high",
                confidence_score=0.90,
                evidence={
                    "username": log.username if getattr(log, 'username', None) else normalized_event.get("username"),
                    "ip_address": log.ip_address if getattr(log, 'ip_address', None) else normalized_event.get("ip_address"),
                    "attempts": normalized_event.get("attempts"),
                    "service": normalized_event.get("service"),
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
            )
        return None

@register_rule
class DET002(BaseRule):
    rule_id = "DET-002"
    rule_name = "Malware-Like Process Execution"
    
    def evaluate(self, log, normalized_event):
        if log.event_type == "malware_detected":
            return DetectionFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                title="Malware-Like Process Execution",
                description="Malware detected by AV or EDR.",
                severity="critical",
                confidence_score=0.98,
                evidence={
                    "process": normalized_event.get("process"),
                    "path": normalized_event.get("path"),
                    "hash": normalized_event.get("hash"),
                    "username": log.username if getattr(log, 'username', None) else normalized_event.get("username"),
                    "ip_address": log.ip_address if getattr(log, 'ip_address', None) else normalized_event.get("ip_address"),
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
            )
        return None

@register_rule
class DET003(BaseRule):
    rule_id = "DET-003"
    rule_name = "Suspicious Outbound Traffic Spike"
    
    def evaluate(self, log, normalized_event):
        if log.event_type == "network_anomaly" and normalized_event.get("bytes", 0) >= 1000000:
            return DetectionFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                title="Suspicious Outbound Traffic Spike",
                description=f"Large amount of outbound traffic detected ({normalized_event.get('bytes')} bytes).",
                severity="high",
                confidence_score=0.85,
                evidence={
                    "src_ip": normalized_event.get("src_ip") or (log.ip_address if getattr(log, 'ip_address', None) else None),
                    "dst_port": normalized_event.get("dst_port"),
                    "bytes": normalized_event.get("bytes"),
                    "action": normalized_event.get("action"),
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
            )
        return None

@register_rule
class DET004(BaseRule):
    rule_id = "DET-004"
    rule_name = "Possible Database Exfiltration"
    
    def evaluate(self, log, normalized_event):
        if log.event_type == "data_access" and normalized_event.get("query_count", 0) >= 1000:
            return DetectionFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                title="Possible Database Exfiltration",
                description=f"High query count detected ({normalized_event.get('query_count')} queries).",
                severity="high",
                confidence_score=0.92,
                evidence={
                    "database user": normalized_event.get("user") or (log.username if getattr(log, 'username', None) else None),
                    "query_count": normalized_event.get("query_count"),
                    "table": normalized_event.get("table"),
                    "duration_ms": normalized_event.get("duration_ms"),
                    "ip_address": log.ip_address if getattr(log, 'ip_address', None) else normalized_event.get("ip_address"),
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
            )
        return None

@register_rule
class DET005(BaseRule):
    rule_id = "DET-005"
    rule_name = "Unknown Critical Security Event"
    
    def evaluate(self, log, normalized_event):
        if log.severity == "critical":
            return DetectionFinding(
                rule_id=self.rule_id,
                rule_name=self.rule_name,
                title="Unknown Critical Security Event",
                description="A critical severity log was seen, and no more specific detection rule matched.",
                severity="critical",
                confidence_score=0.70,
                evidence={
                    "event_type": log.event_type,
                    "message": log.message,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None
                }
            )
        return None
